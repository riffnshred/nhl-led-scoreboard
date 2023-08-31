import paho.mqtt.client as sbmqtt
import debug
import json
import uuid
from sbio.screensaver import screenSaver


AVAIL_BOARDS = ["team_summary","standings","scoreticker","seriesticker","clock","weather","wxalert","pbdisplay","wxforecast","screensaver","stanley_cup_champions","christmas"]
class sbMQTT(object):
    def on_connect(self,client,userdata,flags,rc):
        if rc == 0:
            debug.info("MQTT: Connected to broker: {0}:{1}".format(self.data.config.mqtt_broker,self.data.config.mqtt_port))
            client.publish("{0}/status".format(self.data.config.mqtt_main_topic),payload="Online", qos=0, retain=True) 
        else:
            debug.info("MQTT: Connection error code {0} to {1}:{2}".format(str(rc),self.data.config.mqtt_broker,self.data.config.mqtt_port))

    def on_disconnect(self, client, userdata,rc=0):
        debug.info("DisConnected result code {}".format(rc))
        client.loop_stop()   

    #Used to push out events to scoreboard topic
    def on_publish(self, client, userdata, mid):
        debug.info("MQTT: published message id: "+str(mid))

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
        debug.info("MQTT:  Topic: {0} Payload: {1}".format(msg.topic,msg.payload))
        

        # The test topic is used to test the queue directly without getting to a live game mode
        if msg.topic == "{0}/control/test".format(self.data.config.mqtt_main_topic):
            if msg.payload == "queue":
                qPayload = {"preferred_team": True,"score": 5}
                qItem = ["{0}/live/goal/home".format(self.data.config.mqtt_main_topic),qPayload]
                self.sbQueue.put_nowait(qItem)
            
            if msg.payload == "goal":
                qPayload = {"preferred_team": True,"score": 5}
                qItem = ["{0}/live/goal/home".format(self.data.config.mqtt_main_topic),qPayload]
                self.sbQueue.put_nowait(qItem)
            
            if msg.payload == "penalty":
                qPayload = {"preferred_team": True,"score": 5}
                qItem = ["{0}/live/penalty/home".format(self.data.config.mqtt_main_topic),qPayload]
                self.sbQueue.put_nowait(qItem)
        
        if msg.topic == "{0}/control/screensaver".format(self.data.config.mqtt_main_topic):
            if msg.payload == "on":
                if self.screensaver != None:
                    self.screensaver.runSaver()
                else:
                    debug.error("MQTT: Screen saver not enabled")
            else:
                if self.screensaver != None:
                    self.screensaver.stopSaver()
                else:
                    debug.error("MQTT: Screen saver not enabled")

        # brightness is a number between 1-100
        # Brightness will get set on the next refresh of the board being displayed
        # Also, if you have automatic dimmer enabled, it will go back to the brightness values it uses
        if msg.topic == "{0}/control/brightness".format(self.data.config.mqtt_main_topic):
            if not self.data.config.dimmer_enabled:
                screen_brightness = int(msg.payload)
                
                if screen_brightness not in range(1,101):
                    #set the brightness to original
                    screen_brightness = self.original_brightness
                    debug.info("MQTT: Brightness set to {0}".format(str(screen_brightness)))

                self.matrix.set_brightness(screen_brightness)
            else:
                debug.error("MQTT: brightness can not be set with dimmer enabled")

        # Update the brightness for the dimmer if enabled.  Set either sunset or sunrise or both
        # payload needs to be a json
        # { 
        #   "sunrise": 10,
        #   "sunset": 40 
        # }

        if msg.topic == "{0}/control/dimmer".format(self.data.config.mqtt_main_topic):
            dimmer_payload=json.loads(msg.payload)
            sunrise=dimmer_payload["sunrise"]
            sunset=dimmer_payload["sunset"]
            if self.data.config.dimmer_enabled:
                self.data.config.dimmer_sunrise_brightness = sunrise
                self.data.config.dimmer_sunset_brightness = sunset

                debug.info("MQTT: Changing dimmer brightness sunrise:{0} sunset:{1}".format(sunrise,sunset))


        # Trigger the display to show a board

        if msg.topic == "{0}/control/showboard".format(self.data.config.mqtt_main_topic):
            showboard= msg.payload
            if showboard != "":
                if showboard not in AVAIL_BOARDS:
                    debug.error("MQTT: showboard is not one of the available boards.  Defaulting to clock.  Payload must be one of " + str(AVAIL_BOARDS))
                    showboard = "clock"

                self.data.mqtt_showboard = showboard
                debug.info("MQTT: payload fired...." + showboard + " will be shown on next loop. Currently displayed board " + self.data.curr_board)
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

        clientID = "nhl-led-scoreboard-{0}".format(uuid.uuid1())

        self.client = sbmqtt.Client(clientID,clean_session=True)
        self.client.on_publish = self.on_publish
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.will_set("{0}/status".format(self.data.config.mqtt_main_topic), payload="Offline", qos=0, retain=True)
        # User name and password set here
        if hasattr(self.data.config, 'mqtt_username') and hasattr(self.data.config, 'mqtt_password'):
            self.client.username_pw_set(self.data.config.mqtt_username, self.data.config.mqtt_password)
        
        self.client.connect(self.data.config.mqtt_broker, port=self.data.config.mqtt_port)
        self.client.subscribe("{0}/control/#".format(self.data.config.mqtt_main_topic))
        self.client.loop_start()


    # Run in an endless loop consuming what's on the the queue and publishing to the MQTT broker
    # Possible topics:
    # scoreboard/live/goal
    # payload will be {"away": True, "team": away_name, "preferred_team": pref_team_only,"score": self.away_score}
    #              or {"home": True, "team": home_name, "preferred_team": pref_team_only,"score": self.home_score}
    # scoreboard/live/penalty
    # payload will be  {"home": True, "team": home_name}
    #              or  {"away": True, "team": away_name}
    # scoreboard/live/status
    # status will have a payload {"period": period, "clock": clock,"score": score}
    # scoreboard/state
    # States will have payload of a string: off_day, game_day, pregame,postgame, intermission
    def run(self):
        while True:
            #Get the topic and the payload from the queue
            qData = self.sbQueue.get()
            qTopic = qData[0]
            qPayload = json.dumps(qData[1])
            debug.info("MQTT: Sending: {0} {1}".format(qTopic,qPayload))
            self.client.publish(qTopic,qPayload)
            self.sbQueue.task_done()