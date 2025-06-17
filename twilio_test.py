from twilio.rest import Client
import os
from dotenv import load_dotenv

# NOT WORKING YET

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  body='Hello, this is a test message',
  to='whatsapp:+447874943523'
)

print(message)
print(message.sid)
print(message.body)
print(message.status)

message = client.messages.create(
  from_='whatsapp:+14155238886',
  body='testlocal',
  to='whatsapp:+447874943523'
)

print(message)
print(message.sid)
print(message.body)
print(message.status)
