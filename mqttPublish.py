#MQTT Publish Script
from math import *
from random import randint
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import time
from datetime import datetime

#Defining Constants
rand = 0
freq = 4

def DCVoltage(): #Voltage coming from the PLC
    Vc = GPIO.input(11)
    if Vc == 1:
        status = "On"
    else:
        status = "Off"
    return status

def voltage(freq): #3 phase voltage from
    V0 = 5 #volts
    d = datetime.now()
    uSec = d.microsecond
    mSec = uSec / 1000.0
    Vrms = V0/(sqrt(2))
    fs = 1
    V1 = V0*sin(2*pi*freq*mSec/fs)
    V2 = V0*sin(2*pi*freq*mSec/fs + pi*2/3)
    V3 = V0*sin(2*pi*freq*mSec/fs + pi*4/3)
    msgs=[{ #Message that will publish the three voltage values on the same graph
    "topic":"Motor/voltage1"
    ,"payload": V1}
    ,("Motor/voltage2", V2)
    ,("Motor/voltage3", V3)]
    return msgs

def current(freq): #input the frequency from frequency function
    I0 = 20 #amps
    d = datetime.now()
    uSec = d.microsecond
    secs = d.second
    mSec = uSec / 1000.0
    fs = 1
    Irms = I0/(sqrt(2))
    I1 = I0*sin(2*pi*freq*mSec/fs)
    I2 = I0*sin(2*pi*freq*mSec/fs + pi*2/3)
    I3 = I0*sin(2*pi*freq*mSec/fs + pi*4/3)
    msgs=[{ #Message that will publish the three voltage values on the same graph
        "topic":"Motor/current1"
        ,"payload": I1}
        ,("Motor/current2", I2)
        ,("Motor/current3", I3)]
    return msgs


def temperature(): #constant temperature
    rand = randint(1,50)
    temp = 50 + rand
    return temp

def vibration(): #constant vibration
    rand = randint(1,10)
    vibr = 2 + rand 
    return vibr

def motorEncoder(): 
    p12 = GPIO.PWM(12, 40) #Blink LED on GPIO 18, pin 12 with f=40Hz
    p12.start(50) #50% duty cycle
    return p12
if __name__ == "__main__":
    hostip = "10.0.0.12"

    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation
    try:
        print("Running...")
        while True: #Publish single and multiple messages to these topics
            publish.single("Motor/dcvoltage", DCVoltage(), hostname=hostip)
            publish.multiple(voltage(freq), hostname=hostip)
            publish.single("Motor/temperature", temperature(), hostname=hostip)
            publish.single("Motor/vibration", vibration(), hostname=hostip)
            publish.multiple(current(freq), hostname=hostip)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print ("Ctrl C - Ending Program")
        
    finally:
        GPIO.cleanup()
