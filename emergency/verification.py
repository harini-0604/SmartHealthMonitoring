import time

from emergency.voice_assistant import speak, listen


class EmergencyVerification:

    def __init__(self, duration=30):

        self.duration = duration
        self.active = False
        self.reason = None
        self.source = None

    def start(self, reason="Possible emergency detected", source="UNKNOWN"):

        self.reason = reason
        self.source = source
        self.active = True

        print()
        print("=" * 70)
        print("EMERGENCY VERIFICATION")
        print("=" * 70)

        print(f"Source : {self.source}")
        print(f"Reason : {self.reason}")
        print("Verification Time : 30 seconds")
        print("=" * 70)

    def run_voice_verification(self):

        if not self.active:

            return {
                "status": "NOT_STARTED"
            }

        print()
        print("🚨 POSSIBLE EMERGENCY DETECTED")
        print("Voice verification started.")
        print("You have 30 seconds to respond.")
        print()

        speak("Emergency detected.")
        speak("Are you okay?")

        start_time = time.time()

        while time.time() - start_time < self.duration:

            remaining = int(
                self.duration - (time.time() - start_time)
            )

            print(
                f"Waiting for response... {remaining} seconds remaining"
            )

            response = listen()

            if response:

                response = response.lower().strip()

                print(
                    f"YOU: {response}"
                )

                # ------------------------------------------
                # SAFE RESPONSE
                # ------------------------------------------

                if any(
                    word in response
                    for word in [
                        "yes",
                        "okay",
                        "ok",
                        "fine",
                        "good"
                    ]
                ):

                    speak("Okay. Emergency cancelled.")

                    self.active = False

                    return {
                        "status": "CANCELLED",
                        "response": response,
                        "reason": self.reason,
                        "source": self.source
                    }


                # ------------------------------------------
                # HELP RESPONSE
                # ------------------------------------------

                if any(
                    word in response
                    for word in [
                        "help",
                        "emergency",
                        "no",
                        "not okay",
                        "need help"
                    ]
                ):

                    speak(
                        "Emergency confirmed. Sending alerts."
                    )

                    self.active = False

                    return {
                        "status": "CONFIRMED",
                        "response": response,
                        "reason": self.reason,
                        "source": self.source
                    }

            time.sleep(1)


        # --------------------------------------------------
        # NO RESPONSE
        # --------------------------------------------------

        speak(
            "No response received. Emergency confirmed."
        )

        self.active = False

        return {
            "status": "NO_RESPONSE",
            "reason": self.reason,
            "source": self.source
        }


def create_emergency_verification(duration=30):

    return EmergencyVerification(
        duration=duration
    )


if __name__ == "__main__":

    verification = EmergencyVerification(
        duration=30
    )

    verification.start(
        reason="Test emergency condition",
        source="HARDWARE TEST"
    )

    result = verification.run_voice_verification()

    print()
    print("=" * 70)
    print("VERIFICATION RESULT")
    print("=" * 70)
    print(result)
    print("=" * 70)