from twilio.rest import Client

sendSMS (str account_sid, str auth_token, str sender, str recipient, str msgToSend) {

    client = Client(account_sid, auth_token)

    message = client.messages \
                .create(
                     body=msgToSend,
                     from_=sender,
                     to=recipient
                 )
    print(message.sid)
}
