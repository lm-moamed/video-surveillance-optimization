from twilio.rest import Client
# from .models import Record

def send_whatsapp_message(record):
    # Your Twilio Account SID and Auth Token
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'

    client = Client(account_sid, auth_token)

    user_phone_number = record.userid.userinfo.phone_number  # Get the user's phone number
    record_url = record.path.url  # Assuming the record path is a URL

    message = client.messages.create(
        from_='whatsapp:+1234567890',  # Your Twilio WhatsApp number
        body=f'New record added: {record_url}',
        to=f'whatsapp:{user_phone_number}'
    )

    return message.sid