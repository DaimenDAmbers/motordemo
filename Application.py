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
    print(msg.topic+" "+str(msg.payload)+" "+str(msg.retain))


    if msg.topic == "PLC/ctrlvoltage":
        global vCtrl
        vCtrl = int(msg.payload)
        client.publish("Motor/ctrlvoltage", vCtrl)
        global freq
        freq = Functions.motorEncoder(vCtrl, load)

    if msg.topic == "PLC/load": #When the resistnace value changes, the new resistance is published to the functions
        global load
        load = int(msg.payload)
        client.publish("Motor/load", load)
        global freq
        freq = Functions.motorEncoder(vCtrl, load)
        
    if msg.topic == "PLC/status":
        client.pulish("Motor/status", status)
        

def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code "+str(rc))
    client.loop_stop()


if __name__ == "__main__": #Script for frunning the main application
    hostip = "192.168.137.34"
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation / Motor Encoder

    #Initalize a constants
    vCtrl = 0 #Still need to be globalized but vCtrl is retained from the dashboard
    load = 0
    freq = Functions.motorEncoder(vCtrl, load) #Takes the input of vCtrl and load
    status = Functions.inputVoltage()
    counter = 0 #Counter for checking if the PLC is connected to the Pi

    #Create an MQTT client and attach our routines to it
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(hostip, 1883, 60)
    try:
        while True:
#            while status == "Off": #Determines if the PLC is on or not
#                counter += 1
#                if counter == 1:
#                    print("Please connect PLC")
#                    client.publish("Motor/status", status)
#                if status == "On":
#                    client.publish("Motor/status", status)
#                    break
                
            while freq == 0: #Determines if the freq is equal to 0
                client.loop()
                if freq != 0:
                    break
                
            #Making the functions output to varialbes
            Irms = Functions.current(freq, load, vCtrl)
            Vibration = Functions.vibration(load, vCtrl)
            Temperature = Functions.temperature(Irms)

            #Pulish the varialbes in half second intervals
            client.publish("Motor/rmsCurrent", Irms)
            client.publish("Motor/vibration", Vibration)
            client.publish("Motor/temperature", Temperature)
            print(vCtrl, load)

            client.loop(5)
            Functions.time.sleep(1)
            
#            if status == "Off": #If the PLC is disconnected, turn off the program
#                print("PLC disconnected, turning off program...")
#                break

    except KeyboardInterrupt:
        print("Ctrl+C Exiting program")
    finally:
        client.disconnect()
        GPIO.cleanup()
