import paho.mqtt.client as mqtt

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

mqttc = mqtt.Client("bigus-mac")
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
mqttc.on_message = on_message
mqttc.on_log = on_log

mqttc.connect('192.168.3.42', 1883, 60)
mqttc.subscribe('test', 0)

mqttc.loop_forever()