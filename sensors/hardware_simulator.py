import random
import time


class HardwareSimulator:

    def __init__(self):
        self.running = False

        self.heart_rate = 75.0
        self.spo2 = 98.0
        self.temperature = 36.7

        self.systolic_bp = 118
        self.diastolic_bp = 76

        self.emergency_button = False

    # ========================================================
    # START SIMULATOR
    # ========================================================

    def start(self):

        self.running = True

        print()
        print("=" * 65)
        print("SMART HEALTH MONITORING SYSTEM")
        print("HARDWARE SIMULATOR")
        print("=" * 65)
        print("STATUS : SIMULATED HARDWARE STARTED")
        print("=" * 65)

    # ========================================================
    # STOP SIMULATOR
    # ========================================================

    def stop(self):

        self.running = False

        print()
        print("SIMULATED HARDWARE STOPPED")

    # ========================================================
    # GENERATE NORMAL SENSOR DATA
    # ========================================================

    def generate_normal_data(self):

        if not self.running:
            return {}

        self.heart_rate = round(
            random.uniform(70, 85), 1
        )

        self.spo2 = round(
            random.uniform(96, 99), 1
        )

        self.temperature = round(
            random.uniform(36.4, 37.2), 1
        )

        self.systolic_bp = random.randint(
            110, 125
        )

        self.diastolic_bp = random.randint(
            70, 80
        )

        self.emergency_button = False

        return self.read_data()

    # ========================================================
    # GENERATE ABNORMAL HEALTH CONDITION
    # ========================================================

    def generate_abnormal_data(self):

        if not self.running:
            return {}

        self.heart_rate = 135.0
        self.spo2 = 89.0
        self.temperature = 39.5

        self.systolic_bp = 165
        self.diastolic_bp = 105

        self.emergency_button = False

        return self.read_data()

    # ========================================================
    # SIMULATE EMERGENCY BUTTON
    # ========================================================

    def press_emergency_button(self):

        if not self.running:
            return {}

        self.emergency_button = True

        return self.read_data()

    # ========================================================
    # RESET EMERGENCY BUTTON
    # ========================================================

    def reset_emergency_button(self):

        self.emergency_button = False

    # ========================================================
    # READ ALL DATA
    # ========================================================

    def read_data(self):

        if not self.running:
            return {}

        return {
            "heart_rate": self.heart_rate,
            "spo2": self.spo2,
            "temperature": self.temperature,
            "systolic_bp": self.systolic_bp,
            "diastolic_bp": self.diastolic_bp,
            "emergency_button": self.emergency_button,
            "source": "SIMULATED HARDWARE"
        }


# ============================================================
# FACTORY
# ============================================================

def create_hardware_simulator():

    return HardwareSimulator()