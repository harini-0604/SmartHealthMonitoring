
def send_hospital_alert(
    patient_data=None,
    emergency_data=None
):

    if patient_data is None:
        patient_data = {}

    if emergency_data is None:
        emergency_data = {}

    print()
    print("=" * 60)
    print("HOSPITAL ALERT INTERFACE")
    print("=" * 60)
    print("STATUS : HOSPITAL ALERT PREPARED")
    print(f"PATIENT DATA   : {patient_data}")
    print(f"EMERGENCY DATA : {emergency_data}")
    print("=" * 60)

    return {
        "status": "HOSPITAL ALERT PREPARED",
        "patient_data": patient_data,
        "emergency_data": emergency_data
    }
