from twilio.rest import Client
from medi_creds import *


def send_sms(text):
    try:
        client = Client(twilio_id, twilio_token)
        client.messages.create(to=twilio_recip, from_=twilio_from, body=text)
    except:
        print("Cannot send sms")
