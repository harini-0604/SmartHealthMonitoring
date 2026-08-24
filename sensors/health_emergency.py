from emergency.verification import EmergencyVerification


class HealthEmergencyHandler:

    def __init__(self, verification_duration=60):

        self.verification = EmergencyVerification(
            duration=verification_duration
        )


    # ========================================================
    # HANDLE HEALTH ALERT
    # ========================================================

    def handle_health_alert(
        self,
        health_result
    ):

        if not health_result.get("alert"):

            return {
                "status": "NORMAL",
                "verification": None
            }


        # ----------------------------------------------------
        # BUILD ALERT REASON
        # ----------------------------------------------------

        reasons = []

        for alert in health_result.get(
            "alerts",
            []
        ):

            reason = alert.get(
                "reason",
                "Abnormal health reading"
            )

            value = alert.get(
                "value",
                "UNKNOWN"
            )

            reasons.append(
                f"{reason} (Value: {value})"
            )


        alert_reason = "; ".join(
            reasons
        )


        # ----------------------------------------------------
        # START VOICE VERIFICATION
        # ----------------------------------------------------

        self.verification.start(
            reason=alert_reason,
            source="HEALTH SENSOR"
        )


        verification_result = (
            self.verification.run_voice_verification()
        )


        return {
            "status": verification_result.get(
                "status",
                "UNKNOWN"
            ),
            "verification": verification_result
        }


def create_health_emergency_handler(
    verification_duration=60
):

    return HealthEmergencyHandler(
        verification_duration=verification_duration
    )