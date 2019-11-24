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

try:
	while True:
		bpm = data.BPM
		voltage = data.pulseVoltage
        temp = data.temp
        motion = data.motion
        bpmQueueSize = data.bpmQueue.qsize()
        tempQueueSize = data.tempQueue.qsize()

		if bpm > 0:
			print("BPM: %d\n" % bpm)
		else:
			print("NO HEARTBEAT DETECTED\n")

        if temp > -100:
            print("TEMPERATURE: %d\n" % temp)
        else:
            print("NO TEMPERATURE DETECTED\n")

        if motion:
            print("DEVICE MOTION WAS DETECTED\n\n")
        else:
            print("DEVICE MOTION WAS NOT DETECTED\n\n")

		if not msgSent and voltage > 0:
			print("SENDING EMERGENCY NOTIFICATIONS\n")
            sendNotifications(conf_list['sms_message'], conf_list['pushbullet_message'])
            print("EMERGENCY NOTIFICATIONS SENT\n")
			msgSent = True
			msgSentTime = time.time()

        if msgSent and time.time() - msgSentTime >= 5:          # change to 30 seconds when done testing
            vitalsCheck = False
            sms_msg = "VITALS WERE CAPTURED\n\nBPM: %d\nTEMPERATURE: %d\nDEVICE IS IN MOTION" % (bpm, temp)
            pb_msg = "VITALS WERE CAPTURED\n\nBPM: %d\nTEMPERATURE: %d\nDEVICE IS IN MOTION" % (bpm, temp)
            if bpm > 0:
                sms_msg.join("BPM: %d\n" % bpm)
                pb_msg.join("BPM: %d\n" % bpm)
                vitalsCheck = True
            else:
                sms_msg.join("BPM NOT DETECTED")
                pb_msg.join("BPM NOT DETECTED")
            if temp > -100:
                sms_msg.join("TEMPERATURE: %d\n" % temp)
                pb_msg.join("TEMPERATURE: %d\n" % temp)
                vitalsCheck = True
            else:
                sms_msg.join("TEMPERATURE WAS NOT DETECTED")
                pb_msg.join("TEMPERATURE WAS NOT DETECTED")
            if motion:
                sms_msg.join("DEVICE MOTION WAS DETECTED")
                pb_msg.join("DEVICE MOTION WAS DETECTED")
                vitalsCheck = True
            else:
                sms_msg.join("DEVICE MOTION WAS NOT DETECTED")
                pb_msg.join("DEVICE MOTION WAS NOT DETECTED")
            if vitalsCheck:
                sendNotifications(sms_msg, pb_msg)
            vitalsCheck = False 
            msgSentTime = 0

        if msgSent and bpmQueueSize == 0 and tempQueueSize == 0:            # Approximation when XBee is sent to sleep mode
            msgSent = False

		time.sleep(1)
except:
    data.stopAsyncXBee()
    data.stopAsyncBPM()
    data.stopAsyncTemp()

def sendNotifications(sms_msg, pb_msg):
    sendSMS(conf_list['sms_account_sid'], conf_list['sms_auth_token'], conf_list['sms_sender_number'], conf_list['sms_sender_recipient'], sms_msg)
    if (conf_list['send_pushbullet_option']):
        sendPushBulletNotification(conf_list['pushbullet_api_key'], pb_msg)
    if (conf_list['send_email_option']):
        sendPushBulletEmail(conf_list['pushbullet_api_key'], pb_msg, conf_list['pushbullet_email'])