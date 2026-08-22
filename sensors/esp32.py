
class ESP32Connection:

    def __init__(self):
        self.connected = False

    def connect(self):
        print()
        print("=" * 60)
        print("ESP32 COMMUNICATION")
        print("=" * 60)
        print("STATUS : ESP32 CONNECTION INTERFACE READY")
        print("=" * 60)

        self.connected = True
        return self.connected

    def disconnect(self):
        self.connected = False
        return self.connected

    def read_data(self):
        if not self.connected:
            return {}

        return {
            "heart_rate": None,
            "spo2": None,
            "temperature": None
        }


def get_esp32_connection():
    return ESP32Connection()