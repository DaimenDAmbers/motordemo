#MQTT Client
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #Subscribing in on_connect() - if we lose the connection and reconnect then subscription will be renewed
    #client.subscribe("Motor/#") #Subscribes to the Voltage, Current, Temp, Resistance and Vibration Messages
    client.subscribe("Motor/resistance")
    #client.subscribe("Motor/changeRes")
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
    if msg.topic == "Motor/resistance":
        res = msg.payload
        client.publish("Motor/changeRes", res)
        
def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code "+str(rc))
            
    

if __name__ == "__main__":
    hostip = "192.168.137.247"
    #Create an MQTT client and attach our routines to it
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(hostip, 1883, 60)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop()
        print("Ctrl+C Exiting program")
    
