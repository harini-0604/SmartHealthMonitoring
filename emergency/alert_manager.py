from emergency.emergency_manager import handle_emergency


def trigger_alert(
    reason="Possible emergency detected",
    source="UNKNOWN"
):
    return handle_emergency(
        reason=reason,
        source=source
    )
