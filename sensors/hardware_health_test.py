from sensors.hardware_simulator import create_hardware_simulator
from sensors.health_monitor import create_health_monitor


def display_result(title, data, result):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    print()
    print("HARDWARE DATA")
    print("-" * 70)

    print(f"Heart Rate      : {data.get('heart_rate')} BPM")
    print(f"SpO2            : {data.get('spo2')} %")
    print(f"Temperature     : {data.get('temperature')} °C")
    print(
        f"Blood Pressure  : "
        f"{data.get('systolic_bp')}/"
        f"{data.get('diastolic_bp')} mmHg"
    )
    print(f"Emergency Button: {data.get('emergency_button')}")
    print(f"Source          : {data.get('source')}")

    print()
    print("HEALTH MONITOR")
    print("-" * 70)

    print(f"Overall Status  : {result.get('status')}")
    print(f"Alert           : {result.get('alert')}")

    if result.get("alerts"):

        print()
        print("ACTIVE HEALTH ALERTS")

        for alert in result["alerts"]:

            print(
                f"- {alert['reason']} "
                f"(Value: {alert['value']})"
            )

    else:

        print()
        print("No abnormal health readings detected.")


def run_hardware_health_test():

    hardware = create_hardware_simulator()
    monitor = create_health_monitor()

    hardware.start()

    # ========================================================
    # NORMAL HARDWARE DATA
    # ========================================================

    normal_data = hardware.generate_normal_data()

    normal_result = monitor.check_all(
        heart_rate=normal_data.get("heart_rate"),
        spo2=normal_data.get("spo2"),
        temperature=normal_data.get("temperature")
    )

    display_result(
        "TEST 1 - NORMAL HARDWARE CONDITION",
        normal_data,
        normal_result
    )

    # ========================================================
    # ABNORMAL HARDWARE DATA
    # ========================================================

    abnormal_data = hardware.generate_abnormal_data()

    abnormal_result = monitor.check_all(
        heart_rate=abnormal_data.get("heart_rate"),
        spo2=abnormal_data.get("spo2"),
        temperature=abnormal_data.get("temperature")
    )

    display_result(
        "TEST 2 - ABNORMAL HARDWARE CONDITION",
        abnormal_data,
        abnormal_result
    )

    # ========================================================
    # MANUAL EMERGENCY BUTTON
    # ========================================================

    emergency_data = hardware.press_emergency_button()

    print()
    print("=" * 70)
    print("TEST 3 - MANUAL EMERGENCY BUTTON")
    print("=" * 70)

    print()
    print(
        f"Emergency Button: "
        f"{emergency_data.get('emergency_button')}"
    )

    if emergency_data.get("emergency_button"):

        print("STATUS          : MANUAL EMERGENCY TRIGGERED")

    hardware.stop()


if __name__ == "__main__":

    run_hardware_health_test()