import serial, time, datetime, sys
from xbee import XBee, ZigBee

SP = "/dev/serial0"
BR = 9600

ser = serial.Serial(SP, BR)

xbee = ZigBee(ser, escaped=True)

print ('Starting up ADC Reader')

#xbee.remote_at(
#    dest_addr=b'\x1d\x14',
#    command='D1',
#    parameter=b'\x04')

#xbee.remote_at(
#    dest_addr=b'\x1d\x14',
#    command='WR')

while True:
	try:
		response = xbee.wait_read_frame()
		print (response)
		#time.sleep(0.2)
	except KeyboardInterrupt:
		break
		
ser.close()
