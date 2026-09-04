import time

from sensors.hardware_simulator import create_hardware_simulator
from sensors.health_monitor import create_health_monitor
from sensors.risk_scoring import create_risk_scoring

from emergency.emergency_manager import handle_verified_emergency


# ============================================================
# HARDWARE → EMERGENCY INTEGRATION TEST
# ============================================================


def main():

    hardware = create_hardware_simulator()
    monitor = create_health_monitor()
    risk_engine = create_risk_scoring()

    hardware.start()

    print()
    print("=" * 75)
    print("SMART HEALTH MONITORING SYSTEM")
    print("HARDWARE → EMERGENCY INTEGRATION TEST")
    print("=" * 75)

    print()
    print("Demonstration sequence:")
    print("Cycles 1-3 : Normal")
    print("Cycle 4    : Abnormal health condition")
    print("Cycles 5-6 : Monitoring")
    print()

    try:

        for cycle in range(1, 7):

            print()
            print("=" * 75)
            print(f"CYCLE {cycle}")
            print("=" * 75)

            # ------------------------------------------------
            # HARDWARE DATA
            # ------------------------------------------------

            if cycle == 4:

                data = hardware.generate_abnormal_data()

                print()
                print("SIMULATED ABNORMAL HARDWARE EVENT")

            else:

                data = hardware.generate_normal_data()


            # ------------------------------------------------
            # HEALTH MONITOR
            # ------------------------------------------------

            health = monitor.check_all(
                heart_rate=data["heart_rate"],
                spo2=data["spo2"],
                temperature=data["temperature"],
                systolic_bp=data["systolic_bp"],
                diastolic_bp=data["diastolic_bp"],
                emergency_button=data["emergency_button"]
            )


            # ------------------------------------------------
            # RISK SCORING
            # ------------------------------------------------

            risk = risk_engine.calculate_score(

                heart_rate_alert=
                health["heart_rate"]["alert"],

                spo2_alert=
                health["spo2"]["alert"],

                temperature_alert=
                health["temperature"]["alert"],

                blood_pressure_alert=
                health["blood_pressure"]["alert"],

                emergency_button=
                health["emergency_button"]["alert"]
            )


            # ------------------------------------------------
            # DISPLAY SENSOR STATUS
            # ------------------------------------------------

            print()
            print(
                f"HR          : "
                f"{data['heart_rate']} BPM"
            )

            print(
                f"SpO2        : "
                f"{data['spo2']}%"
            )

            print(
                f"Temperature : "
                f"{data['temperature']} C"
            )

            print(
                f"Blood Press : "
                f"{data['systolic_bp']}/"
                f"{data['diastolic_bp']} mmHg"
            )

            print(
                f"Health      : "
                f"{health['status']}"
            )

            print(
                f"Risk        : "
                f"{risk['risk_level']} "
                f"({risk['score']})"
            )


            # ------------------------------------------------
            # EMERGENCY TRIGGER
            # ------------------------------------------------

            if risk["risk_level"] == "CRITICAL":

                print()
                print("=" * 75)
                print("CRITICAL RISK DETECTED")
                print("=" * 75)

                reason = "; ".join(
                    risk["reasons"]
                )

                print()
                print(f"Emergency Reason: {reason}")

                print()
                print(
                    "Starting 30-second "
                    "emergency verification..."
                )

                result = handle_verified_emergency(

                    reason=reason,

                    source="HARDWARE MONITOR",

                    verification_duration=30
                )

                print()
                print("=" * 75)
                print("EMERGENCY WORKFLOW RESULT")
                print("=" * 75)

                print(result)

                # Stop automatic sequence after emergency
                break


            time.sleep(2)


    except KeyboardInterrupt:

        print()
        print("Monitoring interrupted by user.")


    finally:

        hardware.stop()

        print()
        print("=" * 75)
        print("HARDWARE → EMERGENCY TEST COMPLETED")
        print("=" * 75)


if __name__ == "__main__":

    main()