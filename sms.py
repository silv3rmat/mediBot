from twilio.rest import Client
from creds import *


def send_sms(text):
    client = Client(twilio_id, twilio_token)
    client.messages.create(to=twilio_recip, from_=twilio_from, body=text)
