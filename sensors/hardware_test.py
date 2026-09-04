from sensors.hardware_simulator import create_hardware_simulator


def print_data(title, data):

    print()
    print("=" * 65)
    print(title)
    print("=" * 65)

    print(f"Heart Rate     : {data.get('heart_rate')} BPM")
    print(f"SpO2           : {data.get('spo2')} %")
    print(f"Temperature    : {data.get('temperature')} °C")
    print(
        f"Blood Pressure : "
        f"{data.get('systolic_bp')}/"
        f"{data.get('diastolic_bp')} mmHg"
    )
    print(
        f"Emergency Button: "
        f"{data.get('emergency_button')}"
    )
    print(f"Source         : {data.get('source')}")


def run_hardware_test():

    hardware = create_hardware_simulator()

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    hardware.start()

    # --------------------------------------------------------
    # NORMAL CONDITION
    # --------------------------------------------------------

    normal_data = hardware.generate_normal_data()

    print_data(
        "NORMAL HEALTH CONDITION",
        normal_data
    )

    # --------------------------------------------------------
    # ABNORMAL CONDITION
    # --------------------------------------------------------

    abnormal_data = hardware.generate_abnormal_data()

    print_data(
        "ABNORMAL HEALTH CONDITION",
        abnormal_data
    )

    # --------------------------------------------------------
    # MANUAL EMERGENCY BUTTON
    # --------------------------------------------------------

    emergency_data = hardware.press_emergency_button()

    print_data(
        "MANUAL EMERGENCY BUTTON",
        emergency_data
    )

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    hardware.stop()


if __name__ == "__main__":

    run_hardware_test()