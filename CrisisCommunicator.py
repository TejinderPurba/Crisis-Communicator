import serial, time, datetime, sys
import yaml
from xbee import XBee

from sendSMS import sendSMS
from sendPushBullet import sendPushBulletNotification, sendPushBulletEmail, displayPushBulletDevices

serialPort = "/dev/ttyAMA0"    
baudRate = 9600      

with open(r'Configuration.yaml') as file:
    conf_list = yaml.full_load(file)

ser = serial.Serial(SERIALPORT, BAUDRATE)

xbee = XBee(ser)

while True:
    try:
        response = xbee.wait_read_frame()
        userPulse = getPulse(response)
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
    readings=[]
    for item in data:
        readings.append(item.get('adc-0'))

    voltage_average = sum(readings)/float(len(readings))

    'pulse = NEED A VOLTAGE TO PULSE FORMULA'

    return pulse
