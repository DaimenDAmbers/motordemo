@@ -1,103 +0,0 @@
from opcua import Server
import RPi.GPIO as GPIO
import time

#Import created functions
import Functions

def createOPCUA():
    server = Server()

    url = "opc.tcp://192.168.137.34:4840"
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
    Rms.set_writable()

    server.start()
    print("Server started at {}".format(url))
    return [Temp, Vibr, Curr, Rms]

def publishOPCUA(load, vCtrl, freq, Irms, Temp, Vibr, Curr, Rms):
    Current = Functions.current(freq, vCtrl, load)
    Temperature = Functions.temperature(Irms)
    Vibration = Functions.vibration(vCtrl, load)
    Frequency, RootMeanSquare = Functions.motorEncoder(vCtrl, load)

    print(Temperature, Vibration, Current, Rms)

    Curr.set_value(Current)
    Temp.set_value(Temperature)
    Vibr.set_value(Vibration)
    Rms.set_value(RootMeanSquare)

def disconnectOPCUA():
    server.stop()
    print("OPC UA has stopped running")

if __name__ == "__main__":
    #Board/Port Setup
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT) #GPIO18 Pulse Width Modulation
    try:
        while True:
            publishOPCUA(load, vCtrl, freq, Irms, Temp, Vibr, Curr)

            time.sleep(2)
    except KeyboardInterrupt:
        print("Ctrl C: Exiting Program")
    finally:
        GPIO.cleanup()
