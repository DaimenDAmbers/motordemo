#MQTT Client
from math import *
from random import randint
import time
import paho.mqtt.client as mqtt

hostip = "192.168.137.185"
    

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #Subscribing in on_connect() - if we lose the connection and reconnect then subscription will be renewed
    client.subscribe("Motor/#") #Subscribes to the Voltage, Current, Temp, Resistance and Vibration Messages
    #client.subscribe("Motor/resistance")
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


    if msg.payload == "1" and msg.topic == "Motor/resistance": 
        res = 1
        print("The resistance is 1")
    elif msg.payload == "2" and msg.topic == "Motor/resistance":
        res = 2
        print("The resistance is 2")
    elif msg.payload == "3" and msg.topic == "Motor/resistance":
        res = 3
        print("The resistance is 3")
    elif msg.payload == "4" and msg.topic == "Motor/resistance":
        res = 4
        print("The resistance is 4")
    elif msg.payload == "5" and msg.topic == "Motor/resistance":
        res = 5
        print("The resistance is 5")
    elif msg.payload == "0" and msg.topic == "Motor/resistance":
        res = 0
        print("The resistance is 0")
            
    
#Create an MQTT client and attach our routines to it
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(hostip, 1883, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Ctrl+C Exiting program")
    
