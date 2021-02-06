import threading
import paho.mqtt.client as mqtt
import time
from re import match

DOMAINEXPRESSION = "^([a-z0-9])(([a-z0-9-]{1,61})?[a-z0-9]{1})?(\.[a-z0-9](([a-z0-9-]{1,61})?[a-z0-9]{1})?)?(\.[a-zA-Z]{2,4})+$"
IPEXPRESSIOM = "[0-9]+(?:\.[0-9]+){3}(:[0-9]+)?"


class MQTT:
    sendingKey = []
    sendTopic = None
    client = mqtt.Client()
    isMain = False
    recData = ""

    def __init__(self, login, password, server, port):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.server = server
        self.login = login
        self.password = password
        self.port = port

    def connect(self):
        if bool(match(DOMAINEXPRESSION, self.server)) \
                or bool(match(IPEXPRESSIOM, self.server)):
            self.client.username_pw_set(self.login, password=self.password)
            self.client.connect(self.server, self.port, 60)
        mqttThread = threading.Thread(target=self.mqtt_connect, args=(), daemon=True)
        mqttThread.start()
        if self.isMain:
            sendThread = threading.Thread(target=self.send, args=(), daemon=True)
            sendThread.start()

    def reconnect(self, password, login, address, port):
        try:
            self.client.disconnect()
        except Exception as e:
            print(e)
        self.client.username_pw_set(login, password=password)
        self.client.connect(address, port, 60)

    def on_message(self, client, userdata, msg):
        rec = str(msg.payload)
        print(rec)

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def publish(self, topic, msg):
        self.client.publish(topic, msg)

    def on_connect(self, client, userdata, flags, rc):
        print('in MQTT connected')
        self.client.subscribe(self.sendTopic + '/status')

    def updateTopic(self, topic, old_topic):
        try:
            self.sendTopic = topic
            self.client.unsubscribe(old_topic)
            self.client.subscribe(topic + '/status')
            return True
        except:
            return False

    def mqtt_connect(self):
        self.client.loop_forever()

    def setKey(self, sending_key):
        self.sendingKey = sending_key

    def setSendTopic(self, topic=None):
        self.sendTopic = topic

    def send(self):
        while True:
            time.sleep(0.08)
            if len(self.sendingKey) > 0:
                for key in self.sendingKey:
                    print(key)
                    self.client.publish(self.sendTopic, key)

    def disconnect(self):
        self.client.disconnect()

    def updateServer(self, server, port, login, password):
        self.client.disconnect()
        self.client.username_pw_set(login, password=password)
        self.client.connect(server, port, 60)
