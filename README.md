# Motor Demo
## Using mqtt to subscribe and publish simulated motor data using a PLC as the control.

## Program Details
The purpose of this program is to simulate data from a PLC that alters the functionality of the motor (i.e. the temperature, vibration etc.) A few sliders on the node-red dashboard will publish a specific Control Voltage and Load Resistance to the simulated motor. Inputs from these sliders will adjust the motor's performance. The OPCUA will allow the data that is being pushed to be retrieved by a connectivity platform that uses OPCUA. This is beneficial for connecting, managing and monitoring each aspect of the motor.

## Program Structure
#### Application.py
This file imports the mqtt client and also imports the Functions file and the myOPCUA file. After initializing the connections to subscribe to the motor and the PLC, the messages that we are waiting for come from the PLC which is the load and the control voltage. A forever loop will push the necessary data to the subscriber every half a second. This same data is also pushed to an OPCUA server.

#### Functions.py
##### - Current
Takes in the frequency, load and the control voltage and calculates a sine value. This returns an Irms value.

#####	- Temperature
Takes in the Irms value and performs a constant calculation. Returns temperature.

##### - Vibration
Takes in the load and control voltage and outputs a vibration that depends on how much load and control voltage is being input.

##### - Motor Encoder
Creates the frequency by taking in the load and the control voltage. This will output the frequency and the rpms.

#### myOPCUA.py
The OPCUA file will create an OPCUA server that creates the variables for temperature, vibration, current, and the rpms and set them to be writable to take in any change that occur. Once changes occur, their values are set and sent off in the Application.py file.

#### Node-Red
This data is then published on a node-red dashboard for a visual representation of a motor simulation.
