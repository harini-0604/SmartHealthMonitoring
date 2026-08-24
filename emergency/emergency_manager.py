from datetime import datetime
from pathlib import Path

from database.database import save_incident
from database.models import Incident

from emergency.notification import send_notification
from emergency.hospital_api import send_hospital_alert
from emergency.ambulance_api import request_emergency_service

def handle_emergency(
    reason="Possible emergency detected",
    source="UNKNOWN"
):
    """
    Handle and record a possible emergency.

    Current implementation:
    1. Creates the emergency incident.
    2. Saves it to the database.
    3. Queues family notification.
    4. Prepares hospital alert.
    5. Prepares emergency-service request.

    External services are currently simulation/interface calls.
    """

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # ========================================================
    # EMERGENCY ALERT
    # ========================================================

    print()
    print("=" * 60)
    print("🚨 EMERGENCY ALERT")
    print("=" * 60)

    print(f"TIME   : {timestamp}")
    print(f"SOURCE : {source}")
    print(f"REASON : {reason}")
    print("STATUS : POSSIBLE EMERGENCY DETECTED")

    print("=" * 60)

    # ========================================================
    # EMERGENCY DATA
    # ========================================================

    emergency_data = {
        "timestamp": timestamp,
        "source": source,
        "reason": reason,
        "status": "POSSIBLE EMERGENCY"
    }

    # ========================================================
    # DATABASE
    # ========================================================

    database_result = None

    try:

        incident = Incident(
            timestamp=timestamp,
            source=source,
            reason=reason,
            status="POSSIBLE EMERGENCY"
        )

        database_result = save_incident(incident)

    except Exception as error:

        print(
            f"WARNING: Could not save incident: {error}"
        )

    # ========================================================
    # FAMILY NOTIFICATION
    # ========================================================

    notification_result = send_notification(
        message=(
            f"Possible emergency detected. "
            f"Source: {source}. "
            f"Reason: {reason}. "
            f"Time: {timestamp}."
        ),
        recipient="FAMILY"
    )

    # ========================================================
    # HOSPITAL ALERT
    # ========================================================

    hospital_result = send_hospital_alert(
        patient_data={
            "patient_id": "UNKNOWN"
        },
        emergency_data=emergency_data
    )

    # ========================================================
    # EMERGENCY SERVICE / AMBULANCE
    # ========================================================

    ambulance_result = request_emergency_service(
        location="UNKNOWN",
        emergency_data=emergency_data
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "status": "POSSIBLE EMERGENCY",
        "source": source,
        "reason": reason,
        "timestamp": timestamp,
        "database": database_result,
        "notification": notification_result,
        "hospital": hospital_result,
        "ambulance": ambulance_result
    }

# ============================================================
# EMERGENCY MANAGER TEST
# ============================================================

def emergency_test():

    result = handle_emergency(
        reason="Emergency manager test",
        source="TEST"
    )

    print(
        "Emergency manager test completed."
    )

    return result


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    emergency_test()