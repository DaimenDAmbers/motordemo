#Script that sends and receives messages from the dashboard
import paho.mqtt.client as mqtt
import Functions
import RPi.GPIO as GPIO

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #Subscribing in on_connect() - if we lose the connection and reconnect then subscription will be renewed
    client.subscribe("Motor/#") #Subscribes to the Voltage, Current, Temp, Resistance and Vibration Messages
    client.subscribe("PLC/#")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


    if msg.topic == "PLC/ctrlvoltage":
        global vCtrl
        vCtrl = int(msg.payload)
        client.publish("Motor/ctrlvoltage", vCtrl)
        Functions.motorEncoder(vCtrl)
        client.publish("Motor/rmsCurrent", Functions.current(freq, load, vCtrl))
        client.publish("Motorl/vibration", Functions.vibration(load, vCtrl))

    if msg.topic == "PLC/load": #When the resistnace value changes, the new resistance is published to the functions
        global load
        load = int(msg.payload)
        client.publish("Motor/load", load)
        client.publish("Motor/rmsCurrent", Functions.current(freq, load, vCtrl))
        client.publish("Motor/vibration", Functions.vibration(load, vCtrl))
        client.publish("Motor/temperature", Functions.temperature(Irms))

#    if msg.topic == "Motor/rmsCurrent":
#        client.publish("Motor/temperature", Functions.temperature(Irms))

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code "+str(rc))
    client.loop_stop()



if __name__ == "__main__":
    hostip = "192.168.137.34"
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation

    #Initalize a constants
    vCtrl = 0
    load = 0
    freq = Functions.motorEncoder(vCtrl, load)

    #Create an MQTT client and attach our routines to it
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(hostip, 1883, 60)
    try:
        while True:
            #Making the functions output to varialbes
            Irms = Functions.current(freq, load, vCtrl)
            Vibration = Functions.vibration(load, vCtrl)
            Temperature = Functions.temperature(Irms)

            #Pulish the varialbes in half second intervals
            client.publish("Motor/rmsCurrent", Irms)
            client.publish("Motor/vibration", Vibration)
            client.publish("Motor/temperature", Temperature)

            client.loop()
            Functions.time.sleep(0.5)

    except KeyboardInterrupt:
        client.disconnect()
        print("Ctrl+C Exiting program")
    finally:
        GPIO.cleanup()
