
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
    print("STATUS    : NOTIFICATION QUEUED")
    print("=" * 60)

    return {
        "status": "NOTIFICATION QUEUED",
        "recipient": recipient,
        "message": message
    }
