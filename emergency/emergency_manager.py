from datetime import datetime
from pathlib import Path

from database.database import save_incident
from database.models import Incident


# ============================================================
# LOG FILE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOG_FOLDER = PROJECT_ROOT / "logs"
LOG_FILE = LOG_FOLDER / "emergency_log.txt"

LOG_FOLDER.mkdir(exist_ok=True)


# ============================================================
# EMERGENCY HANDLER
# ============================================================

def handle_emergency(
    reason="Possible emergency detected",
    source="UNKNOWN"
):
    """
    Handle and record a possible emergency.
    """

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

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
    # SAVE EVENT TO LOG FILE
    # ========================================================

    try:

        incident = Incident(
            timestamp=timestamp,
            source=source,
            reason=reason,
            status="POSSIBLE EMERGENCY"
        )

    except Exception as error:

        print(
            f"WARNING: Could not write emergency log: {error}"
        )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {
        "status": "POSSIBLE EMERGENCY",
        "source": source,
        "reason": reason,
        "timestamp": timestamp
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