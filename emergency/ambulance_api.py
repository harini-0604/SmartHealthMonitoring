
def request_emergency_service(
    location=None,
    emergency_data=None
):
    

    if location is None:
        location = "UNKNOWN"

    if emergency_data is None:
        emergency_data = {}

    print()
    print("=" * 60)
    print("EMERGENCY SERVICE INTERFACE")
    print("=" * 60)
    print(f"LOCATION : {location}")
    print(f"STATUS   : EMERGENCY REQUEST PREPARED")
    print(f"DETAILS  : {emergency_data}")
    print("=" * 60)

    return {
        "status": "EMERGENCY REQUEST PREPARED",
        "location": location,
        "emergency_data": emergency_data
    }
