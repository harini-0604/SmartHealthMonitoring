import os

from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()


# ============================================================
# SMS CONFIGURATION
# ============================================================

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
EMERGENCY_PHONE_NUMBER = os.getenv("EMERGENCY_PHONE_NUMBER")


# ============================================================
# SMS NOTIFICATION
# ============================================================

def send_sms(message):

    if not all([
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_PHONE_NUMBER,
        EMERGENCY_PHONE_NUMBER
    ]):

        print()
        print("=" * 60)
        print("SMS NOTIFICATION")
        print("=" * 60)
        print("STATUS : SMS NOT CONFIGURED")
        print("MESSAGE:", message)
        print("=" * 60)

        return {
            "status": "SMS NOT CONFIGURED",
            "message": message
        }

    try:

        client = Client(
            TWILIO_ACCOUNT_SID,
            TWILIO_AUTH_TOKEN
        )

        sms = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=EMERGENCY_PHONE_NUMBER
        )

        print()
        print("=" * 60)
        print("SMS NOTIFICATION")
        print("=" * 60)
        print("STATUS : SMS SENT")
        print(f"MESSAGE SID : {sms.sid}")
        print("=" * 60)

        return {
            "status": "SMS SENT",
            "message_sid": sms.sid,
            "message": message
        }

    except Exception as error:

        print()
        print("=" * 60)
        print("SMS NOTIFICATION")
        print("=" * 60)
        print("STATUS : SMS FAILED")
        print(f"ERROR  : {error}")
        print("=" * 60)

        return {
            "status": "SMS FAILED",
            "error": str(error),
            "message": message
        }


# ============================================================
# GENERAL NOTIFICATION
# ============================================================

def send_notification(
    message,
    recipient="FAMILY"
):

    print()
    print("=" * 60)
    print("EMERGENCY NOTIFICATION")
    print("=" * 60)
    print(f"RECIPIENT : {recipient}")
    print(f"MESSAGE   : {message}")
    print("=" * 60)

    sms_result = send_sms(message)

    return {
        "status": sms_result["status"],
        "recipient": recipient,
        "message": message,
        "sms": sms_result
    }