import paho.mqtt.client as sbmqtt


class sbMQTT(object):

    def on_connect(client, userdata, flags, rc):
        print(“CONNACK received with code %d.” % (rc))

    def on_disconnect(client, userdata,rc=0):
        print("DisConnected result code "+str(rc))
        client.loop_stop()   

    #Used to push out events (currently goals and penalties) to scoreboard topic
    #
    def on_publish(client, userdata, mid):
        print("mid: "+str(mid))

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        print(str(msg.payload))
    
    def __init__(self, data, matrix,sleepEvent):

        self.data = data
        self.matrix = matrix
        self.brightness = self.matrix.brightness
        self.original_brightness = self.brightness
        self.sleepEvent = sleepEvent


    def run(self):
        
        client = sbmqtt.Client("nhl-led-scoreboard")
        client.on_publish = on_publish
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(“broker.mqttdashboard.com”, 1883)
        client.subscribe("streamlit")
        client.loop_forever()
    