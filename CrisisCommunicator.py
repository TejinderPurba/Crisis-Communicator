import serial, time, datetime, sys
import yaml
from xbee import XBee

from sendSMS import sendSMS
from sendPushBullet import sendPushBulletNotification, sendPushBulletEmail, displayPushBulletDevices

serialPort = "/dev/ttyAMA0"    
baudRate = 9600 
msgSent = False

with open(r'Configuration.yaml') as file:
	conf_list = yaml.full_load(file)

ser = serial.Serial(serialPort, baudRate)

xbee = XBee(ser, escaped=True)

while True:
	try:
		userPulse = getPulse()
		if userPulse > 0:
			sendSMS(conf_list['sms_account_sid'], conf_list['sms_auth_token'], conf_list['sms_sender_number'], conf_list['sms_sender_recipient'], conf_list['sms_message'])
			if (conf_list['send_pushbullet_option']):
				sendPushBulletNotification(conf_list['pushbullet_api_key'], conf_list['pushbullet_message'])
			if (conf_list['send_email_option']):
				sendPushBulletEmail(conf_list['pushbullet_api_key'], conf_list['pushbullet_message'], conf_list['pushbullet_email'])
	except KeyboardInterrupt:
		break

ser.close()

def getPulse(data):
	'Program XBee to send 1 sample every 2ms'

	curState = 0
	thresh = 525  # mid point in the waveform
	P = 512
	T = 512
	stateChanged = 0
	sampleCounter = 0
	lastBeatTime = 0
	firstBeat = True
	secondBeat = False
	Pulse = False
	IBI = 600
	rate = [0]*10
	amp = 100

	lastTime = int(time.time()*1000)

	while True:
		response = xbee.wait_read_frame()
		signal = response.get('samples')[0].get('adc-0')
		curTime = int(time.time()*1000)

		if signal == 0:
			time.sleep(2)
			return 0

		sampleCounter += curTime - lastTime;           # keep track of the time in mS with this variable
		lastTime = curTime
		N = sampleCounter - lastBeatTime;     		   # monitor the time since the last beat to avoid noise
		#print N, signal, curTime, sampleCounter, lastBeatTime

		##  find the peak and trough of the pulse wave
		if signal < thresh and N > (IBI/5.0)*3.0 :  #       # avoid dichrotic noise by waiting 3/5 of last IBI
			if signal < T :                        # T is the trough
			  T = signal;                         # keep track of lowest point in pulse wave 

		if signal > thresh and  signal > P:           # thresh condition helps avoid noise
			P = signal;                             # P is the peak
												# keep track of highest point in pulse wave

		  #  NOW IT'S TIME TO LOOK FOR THE HEART BEAT
		  # signal surges up in value every time there is a pulse
		if N > 250 :                                   # avoid high frequency noise
			if  (signal > thresh) and  (Pulse == False) and  (N > (IBI/5.0)*3.0)  :       
			  Pulse = True;                               # set the Pulse flag when we think there is a pulse
			  IBI = sampleCounter - lastBeatTime;         # measure time between beats in mS
			  lastBeatTime = sampleCounter;               # keep track of time for next pulse

			  if secondBeat :                        # if this is the second beat, if secondBeat == TRUE
				secondBeat = False;                  # clear secondBeat flag
				for i in range(0,10):             # seed the running total to get a realisitic BPM at startup
				  rate[i] = IBI;                      

			  if firstBeat :                        # if it's the first time we found a beat, if firstBeat == TRUE
				firstBeat = False;                   # clear firstBeat flag
				secondBeat = True;                   # set the second beat flag
				continue                              # IBI value is unreliable so discard it


			  # keep a running total of the last 10 IBI values
			  runningTotal = 0;                  # clear the runningTotal variable    

			  for i in range(0,9):                # shift data in the rate array
				rate[i] = rate[i+1];                  # and drop the oldest IBI value 
				runningTotal += rate[i];              # add up the 9 oldest IBI values

			  rate[9] = IBI;                          # add the latest IBI to the rate array
			  runningTotal += rate[9];                # add the latest IBI to runningTotal
			  runningTotal /= 10;                     # average the last 10 IBI values 
			  BPM = 60000/runningTotal;               # how many beats can fit into a minute? that's BPM!
			  print 'BPM: {}'.format(BPM)

		if signal < thresh and Pulse == True :   # when the values are going down, the beat is over
			Pulse = False;                         # reset the Pulse flag so we can do it again
			amp = P - T;                           # get amplitude of the pulse wave
			thresh = amp/2 + T;                    # set thresh at 50% of the amplitude
			P = thresh;                            # reset these for next time
			T = thresh;

		if N > 2500 :                          # if 2.5 seconds go by without a beat
			thresh = 512;                          # set thresh default
			P = 512;                               # set P default
			T = 512;                               # set T default
			lastBeatTime = sampleCounter;          # bring the lastBeatTime up to date        
			firstBeat = True;                      # set these to avoid noise
			secondBeat = False;                    # when we get the heartbeat back

		time.sleep(0.005)

		if not msgSent:
			return 1
		else:
			return 0
