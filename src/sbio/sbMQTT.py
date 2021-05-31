import paho.mqtt.client as sbmqtt
import debug

class sbMQTT(object):

    def on_connect(client, userdata, flags, rc):
        debug.info(“CONNACK received with code %d.” % (rc))

    def on_disconnect(client, userdata,rc=0):
        debug.info("DisConnected result code "+str(rc))
        client.loop_stop()   

    #Used to push out events to scoreboard topic
    #
    def on_publish(client, userdata, mid):
        debug.info("mid: "+str(mid))

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        debug.info(str(msg.payload))
    
    def __init__(self, data, matrix,sleepEvent,sbQueue):

        self.data = data
        self.matrix = matrix
        self.brightness = self.matrix.brightness
        self.original_brightness = self.brightness
        self.sleepEvent = sleepEvent
        self.sbQueue = sbQueue

        self.client = sbmqtt.Client("nhl-led-scoreboard",clean_session=True)
        self.client.on_publish = on_publish
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.connect(“192.168.100.3”, 1883)
        self.client.subscribe("scoreboard/control")
        self.client.loop_start()


    # Run in an endless loop consuming what's on the the queue and publishing to the MQTT broker
    def run(self):
        while True:
            self.sbQueue.get()
            self.sbQueue.task_done()
        
    