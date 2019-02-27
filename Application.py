#Script that sends and receives messages from the dashboard
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time

#Files that I have created that allow for functions and OPC UA functionaility
import Functions
import myOPCUA

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    #Subscribing in on_connect() - if we lose the connection and reconnect then subscription will be renewed
    client.subscribe("Motor/#") #Subscribes to the Voltage, Current, Temp, Resistance and Vibration Messages
    client.subscribe("PLC/#") #Subscribes to the slider controls from the dashboard


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload)+" "+str(msg.retain))

    if msg.topic == "PLC/ctrlvoltage": #When the control voltage value changes, the new voltage is published to the functions
        global vCtrl
        global freq         #Make these global because they are used elsewhere in the code
        global RatePerMin
        vCtrl = int(msg.payload)
        freq, RatePerMin = Functions.motorEncoder(vCtrl, load) #Not sure if this is necessary here if it is down in the while loop

    if msg.topic == "PLC/load": #When the load value changes, the new load is updated globally
        global load
        global freq
        global RatePerMin
        load = int(msg.payload)
        freq, RatePerMin = Functions.motorEncoder(vCtrl, load)

    if msg.topic == "PLC/status":
        client.pulish("Motor/status", status)


def on_disconnect(client, userdata, flags, rc=0): #Runs this when Ctrl+C is enterred to disconnet cleanly
    print("Disconnected result code "+str(rc))
    client.loop_stop()
    myOPCUA.disconnectOPCUA()
    GPIO.cleanup()
    print("Shutdown successful")


if __name__ == "__main__": #Script for frunning the main application
    hostip = "10.148.6.70"
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation / Motor Encoder

    #Initalize a constants
    vCtrl = 0 #Still need to be globalized but vCtrl and load is retained from the dashboard
    load = 0
    freq, RatePerMin = Functions.motorEncoder(vCtrl, load) #Takes the input of vCtrl and load

    #Create an OPCUA server
    Temp, Vibr, Curr, Rpm = myOPCUA.createOPCUA()

    #Create an MQTT client and attach our routines to it
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    #Connects and starts the connection to the mqtt server
    client.connect(hostip, 1883, 60)
    client.loop_start()

    try:
        while True:
            #Making the functions output to varialbes
#            freq, rpm = Functions.motorEncoder(vCtrl, load)
            Irms = Functions.current(freq, load, vCtrl)
            Vibration = Functions.vibration(load, vCtrl)
            Temperature = Functions.temperature(Irms)

            #Pulish the varialbes in half second intervals
            client.publish("Motor/rmsCurrent", Irms)
            client.publish("Motor/vibration", Vibration)
            client.publish("Motor/temperature", Temperature)
            client.publish("Motor/rpms", RatePerMin)

            #OPCUA publish
            myOPCUA.publishOPCUA(Irms, Vibration, Temperature, RatePerMin, Temp, Vibr, Curr, Rpm)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Ctrl+C Exiting program")
    finally:
        client.disconnect()
