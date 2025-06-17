import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_whatsapp_summary(events, to_number):
    """
    events: list of dicts with keys 'title', 'date', 'location'
    to_number: WhatsApp number in format '+1234567890' (no 'whatsapp:' prefix)
    """
    print("[WhatsApp] Loading Twilio credentials from environment...")
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")  # e.g. '+14155238886'

    if not from_number or not to_number:
        print("[WhatsApp] ERROR: WhatsApp numbers not configured in environment variables.")
        return

    print(f"[WhatsApp] Initializing Twilio client for whatsapp:{from_number} -> whatsapp:{to_number}")
    client = Client(account_sid, auth_token)

    # Build summary message
    print(f"[WhatsApp] Building summary message for {len(events)} events...")
    lines = ["Upcoming Hackathons:"]
    for event in events:
        lines.append(f"{event['date']}: {event['title']} @ {event['location']}")
    message_body = "\n".join(lines)
    print(f"[WhatsApp] Message body preview:\n{message_body}")

    print("[WhatsApp] Sending message via Twilio API...")
    message = client.messages.create(
        from_=f'whatsapp:{os.getenv("TWILIO_WHATSAPP_NUMBER")}',
        body=message_body,
        to=f'whatsapp:+447874943523'
    )
    print("[WhatsApp] WhatsApp message sent! SID:", message.sid)
