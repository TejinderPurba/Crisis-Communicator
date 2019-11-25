import serial, time, datetime, sys
import yaml

from sendSMS import sendSMS
from sendPushBullet import sendPushBulletNotification, sendPushBulletEmail, displayPushBulletDevices
from dataProcessing import DataProcessing

msgSent = False
msgSentTime = 0
data = DataProcessing()
data.startAsyncXBee()
data.startAsyncBPM()
data.startAsyncTemp()

conf_list = None
with open(r'Configuration.yaml') as file:
	conf_list = yaml.full_load(file)

def sendNotifications(sms_msg, pb_msg):
	try:
		for item in conf_list['sms_recipient_number']:
			sendSMS(conf_list['sms_account_sid'], conf_list['sms_auth_token'], conf_list['sms_sender_number'], item, sms_msg)
		if (conf_list['send_pushbullet_option']):
			sendPushBulletNotification(conf_list['pushbullet_api_key'], pb_msg)
		return True
	except:
		return False

try:
	while True:
		time.sleep(1)
		bpm = data.BPM
		voltage = data.pulseVoltage
		temp = data.temp
		motion = data.motion
		bpmQueueSize = data.bpmQueue.qsize()
		tempQueueSize = data.tempQueue.qsize()
		msgRxTime = data.msgRxTime

		if msgRxTime > 0:
			if bpm > 0:
				print("BPM: %d\n" % bpm)
			else:
				print("NO HEARTBEAT DETECTED\n")
				
			if temp > -100:
				print("TEMPERATURE: %d\n" % temp)
			else:
				print("NO TEMPERATURE DETECTED\n")

			if motion:
				print("DEVICE MOTION DETECTED\n\n")
			else:
				print("NO DEVICE MOTION DETECTED\n\n")
				
		else:
			print("DEVICE IS OFF\n\n")

		if not msgSent and (voltage > 0 or motion == True):
			print("++++++++++++++++++++++++++++++++++++++++++++++\nSENDING EMERGENCY NOTIFICATIONS\n++++++++++++++++++++++++++++++++++++++++++++++\n")
			if (sendNotifications(conf_list['sms_message'], conf_list['pushbullet_message'])):
				print("++++++++++++++++++++++++++++++++++++++++++++++\nEMERGENCY NOTIFICATIONS SENT\n++++++++++++++++++++++++++++++++++++++++++++++\n\n")
			else:
				print("++++++++++++++++++++++++++++++++++++++++++++++\nEMERGENCY NOTIFICATIONS FAILED TO SEND\n++++++++++++++++++++++++++++++++++++++++++++++\n\n")
			msgSent = True
			msgSentTime = time.time()

		timeVal = int(time.time()) - int(msgSentTime)
		if msgSentTime > 0 and (timeVal % conf_list['vitals_interval'] == 0) and timeVal > 0:          
			notif_msg = "VITALS WERE CAPTURED\n\n"
			if bpm > 0:
				notif_msg = notif_msg + "BPM: %d\n" % bpm
			else:
				notif_msg = notif_msg + "BPM WAS NOT DETECTED\n"
			if temp > -100:
				notif_msg = notif_msg + "TEMPERATURE: %d\n" % temp
			else:
				notif_msg = notif_msg + "TEMPERATURE WAS NOT DETECTED\n"
			if motion:
				notif_msg = notif_msg + "DEVICE MOTION WAS DETECTED\n"
			else:
				notif_msg = notif_msg + "DEVICE MOTION WAS NOT DETECTED\n"
			
			print("++++++++++++++++++++++++++++++++++++++++++++++\nSENDING VITALS NOTIFICATIONS\n++++++++++++++++++++++++++++++++++++++++++++++\n")
			if (sendNotifications(notif_msg, notif_msg)):
				print("++++++++++++++++++++++++++++++++++++++++++++++\nVITALS NOTIFICATIONS SENT\n++++++++++++++++++++++++++++++++++++++++++++++\n\n")
			else:
				print("++++++++++++++++++++++++++++++++++++++++++++++\nVITALS NOTIFICATIONS FAILED TO SEND\n++++++++++++++++++++++++++++++++++++++++++++++\n\n")
		
		msgRxTime = data.msgRxTime
		if (time.time() - msgRxTime > 20) and msgRxTime > 0:            # Approximation when XBee is sent to sleep mode
			msgSent = False
			msgSentTime = 0
			data.clearValues()
			time.sleep(1)
		
except:
	data.stopAsyncXBee()
	data.stopAsyncBPM()
	data.stopAsyncTemp()
	data.closeSerial()
