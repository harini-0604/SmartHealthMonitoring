from sensors.hardware_simulator import create_hardware_simulator
from sensors.health_monitor import create_health_monitor
from sensors.risk_scoring import create_risk_scoring


def print_section(title):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def main():

    hardware = create_hardware_simulator()
    monitor = create_health_monitor()
    risk_engine = create_risk_scoring()

    hardware.start()


    # ==========================================================
    # TEST 1 - NORMAL HARDWARE
    # ==========================================================

    print_section(
        "TEST 1 - NORMAL HARDWARE + RISK ANALYSIS"
    )

    data = hardware.generate_normal_data()

    health = monitor.check_all(
        heart_rate=data["heart_rate"],
        spo2=data["spo2"],
        temperature=data["temperature"],
        systolic_bp=data["systolic_bp"],
        diastolic_bp=data["diastolic_bp"],
        emergency_button=data["emergency_button"]
    )

    risk = risk_engine.calculate_score(
        heart_rate_alert=health["heart_rate"]["alert"],
        spo2_alert=health["spo2"]["alert"],
        temperature_alert=health["temperature"]["alert"],
        blood_pressure_alert=health["blood_pressure"]["alert"],
        emergency_button=health["emergency_button"]["alert"]
    )

    print()
    print("HARDWARE DATA")
    print("-" * 70)

    print(f"Heart Rate      : {data['heart_rate']} BPM")
    print(f"SpO2            : {data['spo2']} %")
    print(f"Temperature     : {data['temperature']} °C")
    print(
        f"Blood Pressure  : "
        f"{data['systolic_bp']}/{data['diastolic_bp']} mmHg"
    )
    print(
        f"Emergency Button: "
        f"{data['emergency_button']}"
    )

    print()
    print("HEALTH STATUS")
    print("-" * 70)

    print(f"Status          : {health['status']}")
    print(f"Alert           : {health['alert']}")

    print()
    print("RISK ANALYSIS")
    print("-" * 70)

    print(f"Risk Score      : {risk['score']}")
    print(f"Risk Level      : {risk['risk_level']}")
    print(f"Reasons         : {risk['reasons']}")


    # ==========================================================
    # TEST 2 - ABNORMAL HARDWARE
    # ==========================================================

    print_section(
        "TEST 2 - ABNORMAL HARDWARE + RISK ANALYSIS"
    )

    data = hardware.generate_abnormal_data()

    health = monitor.check_all(
        heart_rate=data["heart_rate"],
        spo2=data["spo2"],
        temperature=data["temperature"],
        systolic_bp=data["systolic_bp"],
        diastolic_bp=data["diastolic_bp"],
        emergency_button=data["emergency_button"]
    )

    risk = risk_engine.calculate_score(
        heart_rate_alert=health["heart_rate"]["alert"],
        spo2_alert=health["spo2"]["alert"],
        temperature_alert=health["temperature"]["alert"],
        blood_pressure_alert=health["blood_pressure"]["alert"],
        emergency_button=health["emergency_button"]["alert"]
    )

    print()
    print("HARDWARE DATA")
    print("-" * 70)

    print(f"Heart Rate      : {data['heart_rate']} BPM")
    print(f"SpO2            : {data['spo2']} %")
    print(f"Temperature     : {data['temperature']} °C")
    print(
        f"Blood Pressure  : "
        f"{data['systolic_bp']}/{data['diastolic_bp']} mmHg"
    )
    print(
        f"Emergency Button: "
        f"{data['emergency_button']}"
    )

    print()
    print("HEALTH STATUS")
    print("-" * 70)

    print(f"Status          : {health['status']}")
    print(f"Alert           : {health['alert']}")

    print()
    print("RISK ANALYSIS")
    print("-" * 70)

    print(f"Risk Score      : {risk['score']}")
    print(f"Risk Level      : {risk['risk_level']}")

    print()
    print("Risk Reasons:")

    for reason in risk["reasons"]:
        print(f"- {reason}")


    # ==========================================================
    # TEST 3 - MANUAL EMERGENCY BUTTON
    # ==========================================================

    print_section(
        "TEST 3 - MANUAL EMERGENCY BUTTON"
    )

    data = hardware.press_emergency_button()

    health = monitor.check_all(
        heart_rate=data["heart_rate"],
        spo2=data["spo2"],
        temperature=data["temperature"],
        systolic_bp=data["systolic_bp"],
        diastolic_bp=data["diastolic_bp"],
        emergency_button=data["emergency_button"]
    )

    risk = risk_engine.calculate_score(
        heart_rate_alert=health["heart_rate"]["alert"],
        spo2_alert=health["spo2"]["alert"],
        temperature_alert=health["temperature"]["alert"],
        blood_pressure_alert=health["blood_pressure"]["alert"],
        emergency_button=health["emergency_button"]["alert"]
    )

    print()
    print("EMERGENCY BUTTON")
    print("-" * 70)

    print(
        f"Button Status   : "
        f"{data['emergency_button']}"
    )

    print(
        f"Manual Emergency: "
        f"{risk['manual_emergency']}"
    )

    print()
    print("RISK ANALYSIS")
    print("-" * 70)

    print(f"Risk Score      : {risk['score']}")
    print(f"Risk Level      : {risk['risk_level']}")

    print()
    print("Reasons:")

    for reason in risk["reasons"]:
        print(f"- {reason}")


    hardware.stop()


if __name__ == "__main__":
    main()