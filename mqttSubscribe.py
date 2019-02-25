#MQTT Client
import paho.mqtt.client as mqtt
import mqttPublish
import RPi.GPIO as GPIO

vCtrl = 2
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #Subscribing in on_connect() - if we lose the connection and reconnect then subscription will be renewed
    client.subscribe("Motor/#") #Subscribes to the Voltage, Current, Temp, Resistance and Vibration Messages
    client.subscribe("PLC/ctrlvoltage")
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
    if msg.topic == "Motor/dcvoltage":
        client.publish("Motor/status", status)
        print(DCVolts)
        
    if msg.topic == "PLC/ctrlvoltage":
        global vCtrl
        vCtrl = int(msg.payload)
#        mqttPublish.motorEncoder(vCtrl)
#        client.publish("Motor/rmsCurrent", mqttPublish.current(freq, res, vCtrl))
#        client.publish("Motorl/vibration", mqttPublish.vibration(res, vCtrl))
#        print(vCtrl)
    
    if msg.topic == "Motor/resistance": #When the resistnace value changes, the new resistance is published to the functions
        res = int(msg.payload)
        client.publish("Motor/rmsCurrent", mqttPublish.current(freq, res, vCtrl))
        client.publish("Motor/vibration", mqttPublish.vibration(res, vCtrl))
        client.publish("Motor/temperature", mqttPublish.temperature(Irms))
        
#    if msg.topic == "Motor/rmsCurrent":
#        client.publish("Motor/temperature", mqttPublish.temperature(Irms))
        
def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code "+str(rc))
    client.loop_stop()
            
    

if __name__ == "__main__":
    hostip = "192.168.137.34"
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation

    #freq = mqttPublish.motorEncoder(vCtrl)
    
    
    
    #Create an MQTT client and attach our routines to it
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(hostip, 1883, 60)
    try:
        while True:
            client.publish("Motor/ctrlvoltage", vCtrl)
            client.loop()
            mqttPublish.time.sleep(1)
#        while True:
#            #res = mqttPublish.resistance()
#            Irms = mqttPublish.current(freq, res, vCtrl)
#            status = mqttPublish.inputVoltage()
#            vibration = mqttPublish.vibration(res, vCtrl)
#            temperature = mqttPublish.temperature(Irms)
#            
#            client.publish("Motor/dcvoltage", DCVolts)
#            client.publish("Motor/vibration", vibration)
#            client.publish("Motor/temperature", temperature)
#            client.publish("Motor/rmsCurrent", Irms)
#            
#            print("The test resistance is",res)
#            client.loop()
#            mqttPublish.time.sleep(1)

    except KeyboardInterrupt:
        client.disconnect()
        print("Ctrl+C Exiting program")
    finally:
        GPIO.cleanup()
    
