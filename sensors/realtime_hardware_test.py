import time

from sensors.hardware_simulator import create_hardware_simulator
from sensors.health_monitor import create_health_monitor
from sensors.risk_scoring import create_risk_scoring


def print_status(data, health, risk):

    print()
    print("-" * 75)

    print(
        f"HR: {data['heart_rate']:>5.1f} BPM   "
        f"SpO2: {data['spo2']:>4.1f}%   "
        f"Temp: {data['temperature']:>4.1f} °C   "
        f"BP: {data['systolic_bp']}/{data['diastolic_bp']} mmHg"
    )

    print(
        f"Button: {data['emergency_button']}   "
        f"Health: {health['status']}   "
        f"Risk: {risk['risk_level']} ({risk['score']})"
    )

    if risk["manual_emergency"]:

        print(
            "🚨 MANUAL EMERGENCY BUTTON ACTIVATED"
        )

    elif risk["risk_level"] == "CRITICAL":

        print(
            "🚨 CRITICAL HEALTH CONDITION DETECTED"
        )

    elif risk["risk_level"] == "HIGH":

        print(
            "⚠️ HIGH RISK CONDITION DETECTED"
        )

    elif risk["risk_level"] == "MODERATE":

        print(
            "⚠️ MODERATE RISK CONDITION"
        )

    else:

        print(
            "✅ SYSTEM STATUS: NORMAL"
        )


def main():

    hardware = create_hardware_simulator()
    monitor = create_health_monitor()
    risk_engine = create_risk_scoring()

    hardware.start()

    print()
    print("=" * 75)
    print("REAL-TIME HARDWARE MONITORING")
    print("=" * 75)

    print()
    print("Automatic demonstration sequence:")
    print("Cycles 1-5  : Normal")
    print("Cycles 6-8  : Abnormal")
    print("Cycles 9-12 : Recovery / Normal")
    print()
    print("Press Ctrl+C to stop.")
    print()

    cycle = 0

    try:

        while cycle < 12:

            cycle += 1


            # --------------------------------------------------
            # SELECT HARDWARE CONDITION
            # --------------------------------------------------

            if 6 <= cycle <= 8:

                data = hardware.generate_abnormal_data()

            else:

                data = hardware.generate_normal_data()


            # --------------------------------------------------
            # HEALTH MONITORING
            # --------------------------------------------------

            health = monitor.check_all(
                heart_rate=data["heart_rate"],
                spo2=data["spo2"],
                temperature=data["temperature"],
                systolic_bp=data["systolic_bp"],
                diastolic_bp=data["diastolic_bp"],
                emergency_button=data["emergency_button"]
            )


            # --------------------------------------------------
            # RISK SCORING
            # --------------------------------------------------

            risk = risk_engine.calculate_score(
                heart_rate_alert=health["heart_rate"]["alert"],
                spo2_alert=health["spo2"]["alert"],
                temperature_alert=health["temperature"]["alert"],
                blood_pressure_alert=health["blood_pressure"]["alert"],
                emergency_button=health["emergency_button"]["alert"]
            )


            # --------------------------------------------------
            # DISPLAY
            # --------------------------------------------------

            print()
            print(f"CYCLE {cycle}")

            if 6 <= cycle <= 8:

                print(
                    "⚠️ SIMULATED ABNORMAL HARDWARE EVENT"
                )

            elif cycle >= 9:

                print(
                    "🔄 HARDWARE CONDITION RECOVERED"
                )


            print_status(
                data,
                health,
                risk
            )


            time.sleep(2)


    except KeyboardInterrupt:

        print()
        print()
        print("=" * 75)
        print("REAL-TIME MONITORING INTERRUPTED")
        print("=" * 75)


    finally:

        hardware.stop()


if __name__ == "__main__":

    main()