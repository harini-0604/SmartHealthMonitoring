from sensors.esp32 import get_esp32_connection
from sensors.health_monitor import create_health_monitor
from sensors.health_emergency import create_health_emergency_handler

def run_sensor_test():

    print("=" * 65)
    print("SMART HEALTH MONITORING SYSTEM")
    print("HEALTH SENSOR TEST")
    print("=" * 65)

    # --------------------------------------------------------
    # ESP32 CONNECTION
    # --------------------------------------------------------

    esp32 = get_esp32_connection()

    connected = esp32.connect()

    if not connected:
        print("ERROR: ESP32 connection failed.")
        return

    # --------------------------------------------------------
    # READ SIMULATED SENSOR DATA
    # --------------------------------------------------------

    sensor_data = esp32.read_data()

    # TEST ONLY: simulate an abnormal heart rate
    
    sensor_data["heart_rate"] = 150.0

    print()
    print("SENSOR DATA")
    print("-" * 65)

    print(f"Heart Rate : {sensor_data.get('heart_rate')}")
    print(f"SpO2       : {sensor_data.get('spo2')}")
    print(f"Temperature: {sensor_data.get('temperature')}")
    print(f"Source     : {sensor_data.get('source')}")

    # --------------------------------------------------------
    # HEALTH MONITOR
    # --------------------------------------------------------

    monitor = create_health_monitor()

    result = monitor.check_all(
        heart_rate=sensor_data.get("heart_rate"),
        spo2=sensor_data.get("spo2"),
        temperature=sensor_data.get("temperature")
    )

    print()
    print("HEALTH MONITOR RESULT")
    print("-" * 65)

    print(f"Status : {result['status']}")
    print(f"Alert  : {result['alert']}")

    # --------------------------------------------------------
    # ALERT DETAILS
    # --------------------------------------------------------

    if result["alerts"]:

        print()
        print("ALERTS")

        for alert in result["alerts"]:

            print(
                f"- {alert['reason']} "
                f"(Value: {alert['value']})"
            )

    else:

        print()
        print("No abnormal health readings detected.")


    # --------------------------------------------------------
    # HEALTH EMERGENCY HANDLER
    # --------------------------------------------------------

    if result["alert"]:

        print()
        print("=" * 65)
        print("HEALTH EMERGENCY HANDLER")
        print("=" * 65)

        emergency_handler = create_health_emergency_handler(
            verification_duration=10
        )

        emergency_result = (
            emergency_handler.handle_health_alert(
                result
            )
        )

        print()
        print(
            f"Emergency status: "
            f"{emergency_result['status']}"
        )

    else:

        print()
        print("No emergency verification required.")

    # --------------------------------------------------------
    # DISCONNECT
    # --------------------------------------------------------

    esp32.disconnect()

    print()
    print("=" * 65)
    print("HEALTH SENSOR TEST COMPLETED")
    print("=" * 65)


if __name__ == "__main__":

    run_sensor_test()