#MQTT Client
import paho.mqtt.client as mqtt
import mqttPublish
import RPi.GPIO as GPIO


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #Subscribing in on_connect() - if we lose the connection and reconnect then subscription will be renewed
    client.subscribe("Motor/#") #Subscribes to the Voltage, Current, Temp, Resistance and Vibration Messages
    client.publish("Motor/status", status)
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
    if msg.topic == "Motor/dcvoltage":
        client.publish("Motor/status", status)
    
    if msg.topic == "Motor/resistance":
        global res
        res = int(msg.payload)
        client.publish("Motor/changeRes", res)
        client.publish("Motor/rmsCurrent", mqttPublish.current(freq, res))
        #Will need vibration function in this if statement as well.
        
    if msg.topic == "Motor/rmsCurrent":
        client.publish("Motor/temperature", mqttPublish.temperature(Irms))
def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code "+str(rc))
            
    

if __name__ == "__main__":
    hostip = "10.0.0.12"
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation
    
    res = 1
    V0 = 100 #Amplified for visual purposes
    freq = mqttPublish.motorEncoder()
    Irms = mqttPublish.current(freq, res)
    status, DCVolts = mqttPublish.DCVoltage()
    
    #Create an MQTT client and attach our routines to it
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(hostip, 1883, 60)
    try:
#            client.loop()
        client.loop_forever()
#            client.publish("Motor/current1", str(mqttPublish.current(freq,res)))
    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop()
        print("Ctrl+C Exiting program")
    
