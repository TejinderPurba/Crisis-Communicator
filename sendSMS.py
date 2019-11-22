from twilio.rest import Client

def sendSMS(account_sid, auth_token, sender, recipient, msgToSend):

    client = Client(account_sid, auth_token)

    message = client.messages \
                .create(
                     body=msgToSend,
                     from_=sender,
                     to=recipient
                 )
    print(message.sid)

