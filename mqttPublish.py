#MQTT Publish Script
from math import *
from random import randint
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
from datetime import datetime
#import socket

client = mqtt.Client()

#Defining Constants
rand = 0
res = 1
V0 = 12
I0 = 20
freq = 0
Irms = 0

#Get ip address
hostname = socket.gethostname()
ipAddr = socket.gethostbyname(hostname)

def DCVoltage(): #Voltage coming from the PLC
    Vc = GPIO.input(11)
    if Vc == 1:
        status = "On"
    else:
        status = "Off"
    return status

def voltage(freq, res): #3 phase voltage from
    resConst = 5
    d = datetime.now()
    uSec = d.microsecond
    mSec = uSec / 1000.0
    Vrms = (I0*(resConst*res))/(sqrt(2))
    V1 = (I0*(resConst*res))*sin(2*pi*freq*mSec)
    V2 = (I0*(resConst*res))*sin(2*pi*freq*mSec + pi*2/3)
    V3 = (I0*(resConst*res))*sin(2*pi*freq*mSec + pi*4/3)
    msgs=[{ #Message that will publish the three voltage values on the same graph
    "topic":"Motor/voltage1"
    ,"payload": V1}
    ,("Motor/voltage2", V2)
    ,("Motor/voltage3", V3)]
    return msgs

def current(freq, res): #input the frequency from frequency function
    resConst = 5
    d = datetime.now()
    uSec = d.microsecond
    secs = d.second
    mSec = uSec / 1000.0
    global Irms
    Irms = (V0/(resConst*res))/(sqrt(2))
    I1 = (V0/(resConst*res))*sin(2*pi*freq*mSec)
    I2 = (V0/(resConst*res))*sin(2*pi*freq*mSec + pi*2/3)
    I3 = (V0/(resConst*res))*sin(2*pi*freq*mSec + pi*4/3)
    msgs=[{ #Message that will publish the three voltage values on the same graph
        "topic":"Motor/current1"
        ,"payload": I1}
        ,("Motor/current2", I2)
        ,("Motor/current3", I3)]
    return msgs


def temperature(Irms): #constant temperature
    temp = 50 + Irms
    return temp

def vibration(res): #constant vibration
    resConst = 5
    vibr = randint(1,resConst*res)
    return vibr

def motorEncoder():
    global p12
    global freq
    pulses = 40
    p12 = GPIO.PWM(12, pulses) #Blink LED on GPIO 18, pin 12 with f=40Hz
    p12.start(50) #50% duty cycle
    freq = pulses/10
    return freq

if __name__ == "__main__":
    hostip = "192.168.137.185"
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation
    try:
        print("Running...")
        motorEncoder()
        while True: #Publish single and multiple messages to these topics
            publish.single("Motor/dcvoltage", DCVoltage(), hostname=hostip)
            publish.multiple(voltage(freq, res), hostname=hostip)
            publish.single("Motor/temperature", temperature(Irms), hostname=hostip)
            publish.single("Motor/vibration", vibration(res), hostname=hostip)
            publish.multiple(current(freq, res), hostname=hostip)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print ("Ctrl C - Ending Program")

    finally:
        global p12
        p12.stop
        GPIO.cleanup()
