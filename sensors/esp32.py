class ESP32Connection:

    def __init__(self):

        self.connected = False


    # ========================================================
    # CONNECT
    # ========================================================

    def connect(self):

        print()
        print("=" * 60)
        print("ESP32 COMMUNICATION")
        print("=" * 60)
        print("STATUS : ESP32 CONNECTION INTERFACE READY")
        print("=" * 60)

        self.connected = True

        return self.connected


    # ========================================================
    # DISCONNECT
    # ========================================================

    def disconnect(self):

        self.connected = False

        return self.connected


    # ========================================================
    # READ SENSOR DATA
    # ========================================================

    def read_data(self):

        if not self.connected:

            return {}


        # ----------------------------------------------------
        # SIMULATED ESP32 DATA
        # ----------------------------------------------------
        # These values represent the structure expected from
        # a future physical ESP32 + sensor setup.
        #
        # They are NOT real sensor measurements.
        # ----------------------------------------------------

        return {
            "heart_rate": 75.0,
            "spo2": 98.0,
            "temperature": 36.7,
            "source": "SIMULATED ESP32"
        }


# ============================================================
# FACTORY
# ============================================================

def get_esp32_connection():

    return ESP32Connection()