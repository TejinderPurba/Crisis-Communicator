from pushbullet.pushbullet import PushBullet

def sendPushBulletNotification(apiKey, message):
    p = PushBullet(apiKey)
    devices = p.getDevices()
    p.pushNote(devices[0]["iden"], 'EMERGENCY', message)


def sendPushBulletEmail(apiKey, message, email):
    p = PushBullet(apiKey)
    p.pushNote(email, 'EMERGENCY', message, recipient_type='email')


def displayPushBulletDevices(apiKey):
    p = PushBullet(apiKey)
    devices = p.getDevices()
    print(devices)

