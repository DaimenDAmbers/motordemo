#MQTT Publish Script
from math import *
from random import randint
import paho.mqtt.publish as publish
import RPi.GPIO as GPIO
import time
from datetime import datetime



def inputVoltage(): #This determines if the Rpi is receiving an input from the PLC
    Vc = GPIO.input(11)
    if Vc == 1:
        status = "On"
    else:
        status = "Off"
    return status        


def current(freq, load, vCtrl): #input the frequency, load and vCtrl from outside sources
    loadConst = 5
    d = datetime.now()
    uSec = d.microsecond
    mSec = uSec / 1000.0
    global Irms
    I1 = ((vCtrl/(loadConst*load))*sin(2*pi*freq*mSec))
    I2 = ((vCtrl/(loadConst*load))*sin(2*pi*freq*mSec) + pi*(2/3))
    I3 = ((vCtrl/(loadConst*load))*sin(2*pi*freq*mSec) + pi*(4/3))
    Irms = (vCtrl/(loadConst*load))/(sqrt(2))
    return Irms


def temperature(Irms): #constant temperature
    temp = 20 + ((Irms**3)*0.002)
    return temp

def vibration(load, vCtrl): #constant vibration
    vibr = randint(1,int(0.1*(load + vCtrl)+1))
    return vibr

def motorEncoder(vCtrl):
    global p12
    global freq
    pulses = 8 * vCtrl
    p12 = GPIO.PWM(12, pulses) #Blink LED on GPIO 18, pin 12 with f=40Hz
    p12.start(50) #50% duty cycle
    freq = pulses/10
    return freq


if __name__ == "__main__":
#    #Defining Global Constants and Variables
#    load = 1
#    vCtrl = 1 #Amplified Voltage for visual purposes
#    res = 1
#    freq = 0


    #Get ip addloads
    hostip = "192.168.137.34"
    
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation
    try:
        print("Running...")
        motorEncoder(vCtrl)
        while True: #Publish single and multiple messages to these topics
            status = inputVoltage()
            publish.single("Motor/status", status, hostname=hostip)            
            publish.single("Motor/vibration", vibration(load, vCtrl), hostname=hostip)
            publish.single("Motor/rmsCurrent", current(freq, load, vCtrl), hostname=hostip)
            publish.single("Motor/temperature", temperature(Irms), hostname=hostip)
            time.sleep(1)
    except KeyboardInterrupt:
        print ("Ctrl C - Ending Program")

    finally:
        global p12
        p12.stop()
        GPIO.cleanup()
