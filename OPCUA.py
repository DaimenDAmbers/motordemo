from opcua import Server
from random import randint
from math import *
import RPi.GPIO as GPIO
import time
from datetime import datetime

server = Server()
freq = 4

url = "opc.tcp://10.0.0.12:4840"
server.set_endpoint(url)

name = "MOTOR_SIMULATION"
addspace = server.register_namespace(name)

node = server.get_objects_node()

Param = node.add_object(addspace, "Parameters")

Temp = Param.add_variable(addspace, "Temperature", 0)
Vibr = Param.add_variable(addspace, "Vibration", 0)
Curr = Param.add_variable(addspace, "Current", 0)
Volt = Param.add_variable(addspace, "Voltage", 0)

Temp.set_writable()
Vibr.set_writable()
Curr.set_writable()
Volt.set_writable()

server.start()
print("Server started at {}".format(url))

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
    seconds = d.second
    Vrms = V0/(sqrt(2))
    fs = 100
    V1 = V0*sin(2*pi*freq*seconds/fs)
    V2 = V0*sin(2*pi*freq*seconds/fs + pi*2/3)
    V3 = V0*sin(2*pi*freq*seconds/fs + pi*4/3)
    return [V1, V2, V3]

def current(freq): #input the frequency from frequency function
    I0 = 20 #amps
    d = datetime.now()
    seconds = d.second
    fs = 100
    Irms = I0/(sqrt(2))
    I1 = I0*sin(2*pi*freq*seconds/fs)
    I2 = I0*sin(2*pi*freq*seconds/fs + pi*2/3)
    I3 = I0*sin(2*pi*freq*seconds/fs + pi*4/3)
    return [I1, I2, I3]


def temperature(): #constant temperature
    rand = randint(1,50)
    temp = 50 + rand
    return temp

def vibration(): #constant vibration
    rand = randint(1,10)
    vibr = 2 + rand 
    return vibr

def motorSimulator(): 
    p12 = GPIO.PWM(12, 40) #Blink LED on GPIO 18, pin 12 with f=40Hz
    p12.start(50) #50% duty cycle
    return p12

if __name__ == "__main__":
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.IN) #GPIO17 Receiving the 5 Vc from the PLC
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation
    try:
        while True:
            Temperature = temperature()
            Vibration = vibration()
            Current = current(freq)
            Voltage = voltage(freq)

            print(Temperature, Vibration, Current, Voltage)

            Temp.set_value(Temperature)
            Vibr.set_value(Vibration)
            Curr.set_value(Current)
            Volt.set_value(Voltage)

            time.sleep(2)
    except KeyboardInterrupt:
        print("Ctrl C: Exiting Program")
    finally:
        GPIO.cleanup()
