#MQTT Publish Script
from math import *
from random import randint
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import time
from datetime import datetime



def DCVoltage(): #Voltage coming from the PLC
    Vc = GPIO.input(11)
    if Vc == 1:
        status = "On"
        V0 = 5
    else:
        status = "Off"
        V0 = 0
    return [status, V0]


def current(freq, res): #input the frequency from frequency function
    resConst = 5
    d = datetime.now()
    uSec = d.microsecond
    secs = d.second
    mSec = uSec / 1000.0
    global Irms
    I1 = ((V0/(resConst*res))*sin(2*pi*freq*mSec))
    Irms = I1/(sqrt(2))
    return Irms


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
    #Defining Global Constants and Variables
    res = 1
    V0 = 100 #Amplified Voltage for visual purposes
    I0 = 20 #
    freq = 0
    Irms = 0

    #Get ip address
    hostip = "10.0.0.12"
    
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation
    try:
        print("Running...")
        motorEncoder()
        status, DCVolts = DCVoltage()
        while True: #Publish single and multiple messages to these topics
            publish.single("Motor/dcvoltage", DCVolts, hostname=hostip)
            publish.single("Motor/status", status, hostname=hostip)
            publish.single("Motor/temperature", temperature(Irms), hostname=hostip)
            publish.single("Motor/vibration", vibration(res), hostname=hostip)
            publish.single("Motor/rmsCurrent", current(freq, res), hostname=hostip)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print ("Ctrl C - Ending Program")

    finally:
        global p12
        p12.stop
        GPIO.cleanup()
