import smbus
import time as time


class ADS1115:
	def __init__(self,adr):
        	self.adr = adr
        	self.i2cBus = smbus.SMBus(1)

    	def config(self,ch=0,gain=2/3):
        	if(ch==0):
            		self.ch=0x04
        	elif(ch==1):
            		self.ch=0x05
       		elif(ch==2):
           		self.ch=0x06
        	elif(ch==3):
            		self.ch=0x07

        	if(gain==2/3):
            		self.gain = 0x00
            		self.vMax = 6.144
        	elif(gain==1):
            		self.gain = 0x01
            		self.vMax = 4.096
        	elif(gain==2):
            		self.gain = 0x02
            		self.vMax = 2.048
        	elif(gain==4):
            		self.gain = 0x03
            		self.vMax = 1.024
        	elif(gain==8):
            		self.gain = 0x04
            		self.vMax = 0.512
        	elif(gain==16):
           		self.gain=0x05
            		self.vMax = 0.256

        	msg_config = 0x8300+(self.ch<<4)+(self.gain<<1)
        	self.i2cBus.write_word_data(self.adr,1,msg_config)

    	def read(self):
        	reading = self.i2cBus.read_word_data(self.adr,0x00)
        	reading = ((reading&0xFF00)>>8)+((reading&0x00FF)<<8)
        	val = (reading&(0x8000-1))-(reading&0x8000) #sign extension
        	val = val>>4
        	return val

    	def conv2Volt(self,val):
        	return(val*self.vMax)/2047


if __name__ == "__main__":
	adc = ADS1115(0x48)
	adc.config(0,2/3)
	while True:
        	print adc.conv2Volt(adc.read())
		time.sleep(1)


