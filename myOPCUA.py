from opcua import Server
import RPi.GPIO as GPIO
import time

#Import created functions
import Functions

def createOPCUA():
    global server
    server = Server()

    url = "opc.tcp://10.148.6.70:4840"
    server.set_endpoint(url)

    name = "MOTOR_SIMULATION"
    addspace = server.register_namespace(name)

    node = server.get_objects_node()

    Param = node.add_object(addspace, "Parameters")

    Temp = Param.add_variable(addspace, "Temperature", 0)
    Vibr = Param.add_variable(addspace, "Vibration", 0)
    Curr = Param.add_variable(addspace, "Current", 0)
    Rpm = Param.add_variable(addspace, "Rate Per Minute", 0)

    Temp.set_writable()
    Vibr.set_writable()
    Curr.set_writable()
    Rpm.set_writable()

    server.start()
    print("Server started at {}".format(url))
    return [Temp, Vibr, Curr, Rpm]

def publishOPCUA(Irms, Vibration, Temperature, RatePerMin, Temp, Vibr, Curr, Rpm):
#    Current = Irms #Functions.current(freq, vCtrl, load)
#    Temperature = Temperature#Functions.temperature(Irms)
#    Vibration = Functions.vibration(vCtrl, load)
#    Frequency, RootMeanSquare = Functions.motorEncoder(vCtrl, load)

    print(Temperature, Vibration, Irms, RatePerMin)

    Curr.set_value(Irms)
    Temp.set_value(Temperature)
    Vibr.set_value(Vibration)
    Rpm.set_value(RatePerMin)

def disconnectOPCUA():
    server.stop()
    print("OPC UA has stopped running")

if __name__ == "__main__":
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation
    try:
        createOPCUA()
        while True:
            print('Running')
            #publishOPCUA(load, vCtrl, freq, Irms, Temp, Vibr, Curr)

            time.sleep(2)
    except KeyboardInterrupt:
        print("Ctrl C: Exiting Program")
    finally:
        disconnectOPCUA()
        GPIO.cleanup()
