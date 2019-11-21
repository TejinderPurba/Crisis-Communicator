import serial, time, datetime, sys
import yaml

from sendSMS import sendSMS
from sendPushBullet import sendPushBulletNotification, sendPushBulletEmail, displayPushBulletDevices
from pulseSensor import PulseSensor

msgSent = False
p = PulseSensor()
p.startAsyncBPM()

with open(r'Configuration.yaml') as file:
	conf_list = yaml.full_load(file)

try:
    while True:
        bpm = p.BPM
        voltage = p.voltage
        if bpm > 0:
            print("BPM: %d" % bpm)
        else:
            print("No Heartbeat found")
        if not msgSent and voltage > 0:
        	print("SENDING EMERGENCY NOTIFICATIONS")
        	sendSMS(conf_list['sms_account_sid'], conf_list['sms_auth_token'], conf_list['sms_sender_number'], conf_list['sms_sender_recipient'], conf_list['sms_message'])
			if (conf_list['send_pushbullet_option']):
				sendPushBulletNotification(conf_list['pushbullet_api_key'], conf_list['pushbullet_message'])
			if (conf_list['send_email_option']):
				sendPushBulletEmail(conf_list['pushbullet_api_key'], conf_list['pushbullet_message'], conf_list['pushbullet_email'])
			msgSent = True
			msgSentTime = time.time()
        time.sleep(1)
except:
    p.stopAsyncBPM()

ser.close()
