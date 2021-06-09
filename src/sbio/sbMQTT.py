import paho.mqtt.client as sbmqtt
import debug
import json
from sbio.screensaver import screenSaver


AVAIL_BOARDS = ["team_summary","standings","scoreticker","seriesticker","clock","weather","wxalert","pbdisplay","wxforecast","screensaver","stanley_cup_champions","christmas"]
class sbMQTT(object):
    def on_connect(self,client,userdata,flags,rc):
        debug.info("Connected result code {}".format(rc))

    def on_disconnect(self, client, userdata,rc=0):
        debug.info("DisConnected result code {}".format(rc))
        client.loop_stop()   

    #Used to push out events to scoreboard topic
    def on_publish(self, client, userdata, mid):
        debug.info("mid: "+str(mid))

    # The callback for when a PUBLISH message is received from the server.
    # Possible messages that will arrive
    # scoreboard/control/showboard/<boardname>
    # showboard payload will be a string that is the boardname
    # scoreboard/control/brightness/<level, 1-100>
    # scoreboard/control/screensaver/on
    # scoreboard/control/screensaver/off
    # screensaver payload will either be on/off string
    # scoreboard/control/test/goal
    # scoreboard/control/test/penalty
    # scoreboard/control/test/queue
    # test payload will be strings goal, penalty or queue
    def on_message(self, client, userdata, msg):
        msg.payload = msg.payload.decode("utf-8")
        debug.info("MQTT Message: Topic: {0} Payload: {1}".format(msg.topic,msg.payload))
        

        if msg.topic == "scoreboard/control/test":
            if msg.payload == "queue":
                qPayload = {"preferred_team": True,"score": 5}
                qItem = ["scoreboard/live/goal/home",qPayload]
                self.sbQueue.put_nowait(qItem)
            
            if msg.payload == "goal":
                qPayload = {"preferred_team": True,"score": 5}
                qItem = ["scoreboard/live/goal/home",qPayload]
                self.sbQueue.put_nowait(qItem)
            
            if msg.payload == "penalty":
                qPayload = {"preferred_team": True,"score": 5}
                qItem = ["scoreboard/live/pemalty/home",qPayload]
                self.sbQueue.put_nowait(qItem)
        
        if msg.topic == "scoreboard/control/screensaver":
            if msg.payload == "on":
                if self.screensaver != None:
                    self.screensaver.runSaver()
                else:
                    debug.error("Screen saver not enabled")
            else:
                if self.screensaver != None:
                    self.screensaver.stopSaver()
                else:
                    debug.error("Screen saver not enabled")

        # brightness is a number between 1-100
        # Brightness will get set on the next refresh of the board being displayed
        # Also, if you have automatic dimmer enabled, it will go back to the brightness values it uses
        if msg.topic == "scoreboard/control/brightness":
            if not self.data.config.dimmer_enabled:
                screen_brightness = int(msg.payload)
                
                debug.info("Brightness set to {0} from MQTT".format(str(screen_brightness)))

                if screen_brightness not in range(1,101):
                    #set the brightness to original
                    screen_brightness = self.original_brightness
                    debug.info("Brightness set to {0} from MQTT".format(str(screen_brightness)))

                self.matrix.set_brightness(screen_brightness)
            else:
                debug.error("MQTT - brightness can not be set with dimmer enabled")

        # Update the brightness for the dimmer if enabled.  Set either sunset or sunrise or both
        # payload needs to be a json
        # { 
        #   "sunrise": 10,
        #   "sunset": 40 
        # }

        if msg.topic == "scoreboard/control/dimmer":
            dimmer_payload=json.loads(msg.payload)
            sunrise=dimmer_payload["sunrise"]
            sunset=dimmer_payload["sunset"]
            if self.data.config.dimmer_enabled:
                self.data.config.dimmer_sunrise_brightness = sunrise
                self.data.config.dimmer_sunset_brightness = sunset

                debug.info("Changing dimmer brightness sunrise:{0} sunset:{1}".format(sunrise,sunset))


        # Trigger the display to show a board

        if msg.topic == "scoreboard/control/showboard":
            showboard= msg.payload
            if showboard != "":
                if showboard not in AVAIL_BOARDS:
                    debug.error("MQTT showboard is not one of the available boards.  Defaulting to clock.  Payload must be one of " + str(AVAIL_BOARDS))
                    showboard = "clock"

                self.data.mqtt_showboard = showboard
                debug.info("MQTT payload fired...." + showboard + " will be shown on next loop. Currently displayed board " + self.data.curr_board)
                self.data.mqtt_trigger = True
                self.sleepEvent.set()
            

    def __init__(self, data, matrix,sleepEvent,sbQueue,screenSaver):

        self.data = data
        self.matrix = matrix
        self.brightness = self.matrix.brightness
        self.original_brightness = self.brightness
        self.sleepEvent = sleepEvent
        self.sbQueue = sbQueue
        self.screensaver = screenSaver

        self.sleepEvent.clear()


        self.client = sbmqtt.Client("nhl-led-scoreboard",clean_session=True)
        self.client.on_publish = self.on_publish
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("192.168.100.3", port=1883)
        self.client.subscribe("scoreboard/control/#")
        self.client.loop_start()


    # Run in an endless loop consuming what's on the the queue and publishing to the MQTT broker
    # Possible topics:
    # scoreboard/live/start
    # scoreboard/live/current_period
    # scoreboard/live/goal/home
    # scoreboard/live/goal/away
    # scoreboard/live/penalty/home
    # scoreboard/live/penalty/away
    # scoreboard/live/intermission
    # scoreboard/live/end
    def run(self):
        while True:
            #Get the topic and the payload from the queue
            qData = self.sbQueue.get()
            qTopic = qData[0]
            qPayload = json.dumps(qData[1])
            debug.info("Sending: {0} {1}".format(qTopic,qPayload))
            self.client.publish(qTopic,qPayload)
            self.sbQueue.task_done()
        
    