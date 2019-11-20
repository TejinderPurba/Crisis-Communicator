from twilio.rest import Client

sendSMS (str account_sid, str auth_token, str sender, str recipient) {

    client = Client(account_sid, auth_token)

    message = client.messages \
                .create(
                     body="A person's life may be at risk! Please send emergency services to their house.",
                     from_='+12262711202',
                     to='+15192774981'
                 )
    print(message.sid)
}
