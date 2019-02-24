#MQTT Client
import paho.mqtt.client as mqtt
import mqttPublish
import RPi.GPIO as GPIO


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    #Subscribing in on_connect() - if we lose the connection and reconnect then subscription will be renewed
    client.subscribe("Motor/#") #Subscribes to the Voltage, Current, Temp, Resistance and Vibration Messages
    global res
    res = 1
    
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    
    if msg.topic == "Motor/dcvoltage":
        client.publish("Motor/status", status)
        print(DCVolts)
    
    if msg.topic == "Motor/resistance":
        global res
        res = int(msg.payload)
        client.publish("Motor/rmsCurrent", mqttPublish.current(freq, res))
        client.publish("Motor/vibration", mqttPublish.vibration(res))
        client.publish("Motor/temperature", mqttPublish.temperature(res))
        
#    if msg.topic == "Motor/rmsCurrent":
#        client.publish("Motor/temperature", mqttPublish.temperature(Irms))
        
def on_disconnect(client, userdata, flags, rc=0):
    print("Disconnected result code "+str(rc))
            
    

if __name__ == "__main__":
    hostip = "10.0.0.8"
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation
    
    res = 1
    freq = mqttPublish.motorEncoder()
    
    
    
    #Create an MQTT client and attach our routines to it
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    client.connect(hostip, 1883, 60)
    try:
        while True:
            Irms = mqttPublish.current(freq, res)
            status, DCVolts = mqttPublish.DCVoltage()
            vibration = mqttPublish.vibration(res)
            temperature = mqttPublish.temperature(Irms)
            
            client.publish("Motor/dcvoltage", DCVolts)
            client.publish("Motor/vibration", vibration)
            client.publish("Motor/temperature", temperature)
            client.publish("Motor/rmsCurrent", Irms)
            
            print("The test resistance is",res)
            client.loop(.1)

    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop()
        print("Ctrl+C Exiting program")
    finally:
        GPIO.cleanup()
    
