from pushbullet.pushbullet import PushBullet

sendPushBulletNotification(str apiKey, str message) {
    p = PushBullet(apiKey)
    p.pushNote(devices[0]["iden"], 'EMERGENCY', message)
}

sendPushBulletEmail(str apiKey, str message, str email) {
    p = PushBullet(apiKey)
    p.pushNote(email, 'EMERGENCY', message, recipient_type='email')
}

displayPushBulletDevices(str apiKey) {
    p = PushBullet(apiKey)
    devices = p.getDevices()
    print(devices)
}
