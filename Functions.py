#Functions for the python application
from math import *
from random import randint
import RPi.GPIO as GPIO
import time
from datetime import datetime
import numpy
import paho.mqtt.publish as publish



def inputVoltage(vCtrl): #This determines if the Rpi is receiving an input from the PLC
#    Vin = GPIO.input(11)
    if vCtrl != 0:
        status = "On"
    else:
        status = "Off"
    return status


def current(freq, load, vCtrl): #input the frequency, load and vCtrl from outside sources
    loadweight = 3
    d = datetime.now()
    uSec = d.microsecond
    mSec = uSec / 1000.0
    I0 = (vCtrl*4) + (loadweight*load)
    global Irms
#    I1 = ((vCtrl/(loadConst*load))*sin(2*pi*freq*mSec))
#    I2 = ((vCtrl/(loadConst*load))*sin(2*pi*freq*mSec) + pi*(2/3))
#    I3 = ((vCtrl/(loadConst*load))*sin(2*pi*freq*mSec) + pi*(4/3))
    Irms = I0/(sqrt(2))
    return Irms


def temperature(Irms): #constant temperature
    temp = 20 + ((Irms**3)*0.002)
    return temp

def vibration(load, vCtrl): #constant vibration
    vibr = numpy.random.uniform(1.0,2.0) * int(0.1*(load + vCtrl)+1)
    return vibr

def motorEncoder(vCtrl, load):
    global p12
    global freq
    if (load == 0 and vCtrl == 0):
        freq = 0
    else:
        freq = (8 * vCtrl)-(1.5*load)
        p12 = GPIO.PWM(12, freq) #Blink LED on GPIO 18, pin 12 with f=40Hz
        p12.start(50) #50% duty cycle
    return freq


if __name__ == "__main__":

    #Get ip address
    hostip = "192.168.137.34"

    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation

    #    #Defining Global Constants and Variables
    load = 10
    vCtrl = 5 #Amplified Voltage for visual purposes
    freq = motorEncoder(vCtrl, load)
    try:
        print("Running...")
        print(freq)
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
        GPIO.cleanup()
