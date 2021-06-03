import paho.mqtt.client as sbmqtt
import debug
import json

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
    # scoreboard/control/screen/brightness/<level, 1-100>
    # scoreboard/control/screen/off
    # scoreboard/control/screen/on
    # scoreboard/control/screensaver/on
    # scoreboard/control/screensaver/off
    # scoreboard/control/test/goal
    # scoreboard/control/test/penalty
    # scoreboard/control/test/queue
    def on_message(self, client, userdata, msg):
        msg.payload = msg.payload.decode("utf-8")
        debug.info("MQTT Message: Topic: {0} Payload: {1}".format(msg.topic,msg.payload))
        

        if msg.topic == "scoreboard/control/test/queue":
            qPayload = {"preferred_team": True,"score": 5}
            qItem = ["scoreboard/live/goal/home",qPayload]
            self.sbQueue.put_nowait(qItem)
        

    def __init__(self, data, matrix,sleepEvent,sbQueue):

        self.data = data
        self.matrix = matrix
        self.brightness = self.matrix.brightness
        self.original_brightness = self.brightness
        self.sleepEvent = sleepEvent
        self.sbQueue = sbQueue

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
        
    