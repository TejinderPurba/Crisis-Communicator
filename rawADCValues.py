import serial, time, datetime, sys
from xbee import XBee, ZigBee

SP = "/dev/serial0"
BR = 9600

ser = serial.Serial(SP, BR)

xbee = ZigBee(ser, escaped=True)

print ('Starting up ADC Reader')

while True:
	try:
		response = xbee.wait_read_frame()
		print (response)
		#time.sleep(0.2)
	except KeyboardInterrupt:
		break
		
ser.close()
