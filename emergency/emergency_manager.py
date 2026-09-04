from datetime import datetime

from database.database import save_incident
from database.models import Incident

from emergency.verification import EmergencyVerification
from emergency.notification import send_notification
from emergency.hospital_api import send_hospital_alert


# ============================================================
# EMERGENCY MANAGER
# ============================================================

def handle_emergency(
    reason,
    source="UNKNOWN"
):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print()
    print("=" * 75)
    print("🚨 EMERGENCY MANAGER")
    print("=" * 75)

    print(f"Source    : {source}")
    print(f"Reason    : {reason}")
    print(f"Timestamp : {timestamp}")

    # ========================================================
    # 1. SAVE INCIDENT TO DATABASE
    # ========================================================

    incident = Incident(
        timestamp=timestamp,
        source=source,
        reason=reason,
        status="EMERGENCY_CONFIRMED"
    )

    save_incident(incident)

    print()
    print("DATABASE : INCIDENT SAVED")

    # ========================================================
    # 2. FAMILY SMS ALERT
    # ========================================================

    message = (
        "🚨 EMERGENCY ALERT\n"
        f"Source: {source}\n"
        f"Reason: {reason}\n"
        f"Time: {timestamp}\n"
        "Immediate attention required."
    )

    notification_result = send_notification(
        message=message,
        recipient="FAMILY"
    )

    # ========================================================
    # 3. HOSPITAL ALERT
    # ========================================================

    hospital_result = send_hospital_alert(
        patient_data={
            "source": source
        },
        emergency_data={
            "reason": reason,
            "timestamp": timestamp,
            "status": "EMERGENCY_CONFIRMED"
        }
    )

    # ========================================================
    # 4. EMERGENCY SERVICE INTERFACE
    # ========================================================

    print()
    print("=" * 60)
    print("EMERGENCY SERVICE INTERFACE")
    print("=" * 60)
    print("STATUS : EMERGENCY SERVICE ALERT PREPARED")
    print(f"REASON : {reason}")
    print(f"TIME   : {timestamp}")
    print("=" * 60)

    emergency_service_result = {
        "status": "EMERGENCY SERVICE ALERT PREPARED",
        "reason": reason,
        "timestamp": timestamp
    }

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print()
    print("=" * 75)
    print("EMERGENCY WORKFLOW COMPLETED")
    print("=" * 75)

    return {
        "status": "EMERGENCY_HANDLED",
        "reason": reason,
        "source": source,
        "timestamp": timestamp,
        "notification": notification_result,
        "hospital": hospital_result,
        "emergency_service": emergency_service_result
    }


# ============================================================
# VERIFIED EMERGENCY
# ============================================================

def handle_verified_emergency(
    reason,
    source="UNKNOWN",
    verification_duration=30
):

    print()
    print("=" * 75)
    print("VERIFIED EMERGENCY WORKFLOW")
    print("=" * 75)

    verification = EmergencyVerification(
        duration=verification_duration
    )

    verification.start(
        reason=reason,
        source=source
    )

    verification_result = (
        verification.run_voice_verification()
    )

    # ========================================================
    # USER CANCELLED EMERGENCY
    # ========================================================

    if verification_result.get("status") == "CANCELLED":

        print()
        print("=" * 75)
        print("EMERGENCY CANCELLED")
        print("=" * 75)

        return {
            "status": "CANCELLED",
            "verification": verification_result
        }

    # ========================================================
    # EMERGENCY CONFIRMED / NO RESPONSE
    # ========================================================

    if verification_result.get("status") in [
        "CONFIRMED",
        "NO_RESPONSE"
    ]:

        emergency_result = handle_emergency(
            reason=reason,
            source=source
        )

        return {
            "status": emergency_result["status"],
            "verification": verification_result,
            "emergency": emergency_result
        }

    # ========================================================
    # UNKNOWN STATE
    # ========================================================

    return {
        "status": "UNKNOWN",
        "verification": verification_result
    }


# ============================================================
# EMERGENCY TEST
# ============================================================

def emergency_test():

    result = handle_emergency(
        reason="Test emergency condition",
        source="EMERGENCY TEST"
    )

    print()
    print("=" * 75)
    print("TEST RESULT")
    print("=" * 75)

    print(result)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    emergency_test()