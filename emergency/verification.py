import time

from emergency.voice_assistant import run_voice_check


class EmergencyVerification:

    def __init__(self, duration=60):

        self.duration = duration
        self.active = False
        self.start_time = None
        self.reason = None
        self.source = None

    # ========================================================
    # START VERIFICATION
    # ========================================================

    def start(
        self,
        reason,
        source="FALL DETECTION"
    ):

        self.active = True
        self.start_time = time.time()
        self.reason = reason
        self.source = source

        print()
        print("=" * 70)
        print("EMERGENCY VERIFICATION STARTED")
        print("=" * 70)

        print(f"SOURCE : {self.source}")
        print(f"REASON : {self.reason}")
        print(f"TIME   : {self.duration} seconds")

        print()
        print("Please confirm that you are okay.")

        print("=" * 70)

    # ========================================================
    # VOICE VERIFICATION
    # ========================================================

    def run_voice_verification(self):

        if not self.active:

            return {
                "status": "NOT ACTIVE"
            }

        print()
        print("=" * 70)
        print("VOICE VERIFICATION")
        print("=" * 70)

        while self.active:

            remaining = self.get_remaining_time()

            print(
                f"Verification time remaining: "
                f"{remaining} seconds"
            )

            # ------------------------------------------------
            # CHECK TIMEOUT BEFORE LISTENING
            # ------------------------------------------------

            if self.is_expired():

                return self.escalate()

            # ------------------------------------------------
            # VOICE CHECK
            # ------------------------------------------------

            result = run_voice_check()

            status = result.get("status")

            # ------------------------------------------------
            # USER CONFIRMED RECOVERY
            # ------------------------------------------------

            if status == "USER OKAY":

                return self.cancel(
                    reason="User confirmed they are okay"
                )

            # ------------------------------------------------
            # USER REQUESTED HELP
            # ------------------------------------------------

            if status == "POSSIBLE EMERGENCY":

                self.active = False

                return result

            # ------------------------------------------------
            # NO RESPONSE
            # ------------------------------------------------

            if status == "NO RESPONSE":

                print()
                print(
                    "No valid response received."
                )

                # Check whether the 60-second period
                # has now expired.

                if self.is_expired():

                    return self.escalate()

                print(
                    "Continuing emergency verification..."
                )

                continue

            # ------------------------------------------------
            # UNKNOWN RESPONSE
            # ------------------------------------------------

            if status == "UNKNOWN RESPONSE":

                print()
                print(
                    "Response was not understood."
                )

                if self.is_expired():

                    return self.escalate()

                print(
                    "Please respond again."
                )

                continue

            # ------------------------------------------------
            # UNEXPECTED STATUS
            # ------------------------------------------------

            print(
                f"Unexpected verification status: "
                f"{status}"
            )

            if self.is_expired():

                return self.escalate()

        return {
            "status": "VERIFICATION ENDED"
        }

    # ========================================================
    # REMAINING TIME
    # ========================================================

    def get_remaining_time(self):

        if not self.active:

            return 0

        elapsed = (
            time.time()
            - self.start_time
        )

        remaining = (
            self.duration
            - elapsed
        )

        return max(
            0,
            int(remaining)
        )

    # ========================================================
    # CHECK EXPIRATION
    # ========================================================

    def is_expired(self):

        if not self.active:

            return False

        return (
            time.time()
            - self.start_time
            >= self.duration
        )

    # ========================================================
    # CANCEL VERIFICATION
    # ========================================================

    def cancel(
        self,
        reason="User recovered"
    ):

        self.active = False

        print()
        print("=" * 70)
        print("EMERGENCY VERIFICATION CANCELLED")
        print("=" * 70)

        print(f"REASON : {reason}")

        print("=" * 70)

        return {
            "status": "CANCELLED",
            "reason": reason
        }

    # ========================================================
    # ESCALATE EMERGENCY
    # ========================================================

    def escalate(self):

        from emergency.emergency_manager import handle_emergency

        if not self.active:

            return {
                "status": "NOT ACTIVE"
            }

        self.active = False

        print()
        print("=" * 70)
        print("EMERGENCY VERIFICATION FAILED")
        print("=" * 70)

        print("No valid confirmation received.")
        print("Emergency escalation required.")

        print("=" * 70)

        return handle_emergency(
            reason=(
                f"Verification timeout: "
                f"{self.reason}"
            ),
            source=self.source
        )

    # ========================================================
    # CURRENT STATUS
    # ========================================================

    def get_status(self):

        if not self.active:

            return {
                "status": "INACTIVE",
                "remaining": 0
            }

        remaining = self.get_remaining_time()

        if remaining <= 0:

            return {
                "status": "EXPIRED",
                "remaining": 0
            }

        return {
            "status": "VERIFYING",
            "remaining": remaining,
            "reason": self.reason,
            "source": self.source
        }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    verification = EmergencyVerification(
        duration=5
    )

    verification.start(
        reason="Test fall",
        source="TEST"
    )

    print(
        "Current status:",
        verification.get_status()
    )

    time.sleep(1)

    print(
        "Remaining:",
        verification.get_remaining_time()
    )

    verification.cancel(
        reason="Test completed"
    )

    print()
    print("Verification module test completed.")