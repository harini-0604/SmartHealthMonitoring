class HealthMonitor:

    def __init__(self):

        # DEMONSTRATION / PROTOTYPE THRESHOLDS
        # These are NOT medical diagnostic limits.

        self.heart_rate_min = 50.0
        self.heart_rate_max = 120.0

        self.spo2_min = 92.0

        self.temperature_min = 35.0
        self.temperature_max = 39.0

        # Prototype BP thresholds
        self.systolic_bp_min = 90
        self.systolic_bp_max = 140

        self.diastolic_bp_min = 60
        self.diastolic_bp_max = 90

    def check_heart_rate(self, value):

        if value is None:
            return {
                "status": "NO DATA",
                "alert": False
            }

        if (
            value < self.heart_rate_min
            or value > self.heart_rate_max
        ):
            return {
                "status": "ABNORMAL",
                "alert": True,
                "value": value,
                "reason": "Heart rate outside configured range"
            }

        return {
            "status": "NORMAL",
            "alert": False,
            "value": value
        }

    def check_spo2(self, value):

        if value is None:
            return {
                "status": "NO DATA",
                "alert": False
            }

        if value < self.spo2_min:
            return {
                "status": "ABNORMAL",
                "alert": True,
                "value": value,
                "reason": "SpO2 below configured threshold"
            }

        return {
            "status": "NORMAL",
            "alert": False,
            "value": value
        }

    def check_temperature(self, value):

        if value is None:
            return {
                "status": "NO DATA",
                "alert": False
            }

        if (
            value < self.temperature_min
            or value > self.temperature_max
        ):
            return {
                "status": "ABNORMAL",
                "alert": True,
                "value": value,
                "reason": "Temperature outside configured range"
            }

        return {
            "status": "NORMAL",
            "alert": False,
            "value": value
        }

    def check_blood_pressure(self, systolic, diastolic):

        if systolic is None or diastolic is None:
            return {
                "status": "NO DATA",
                "alert": False
            }

        if (
            systolic < self.systolic_bp_min
            or systolic > self.systolic_bp_max
            or diastolic < self.diastolic_bp_min
            or diastolic > self.diastolic_bp_max
        ):
            return {
                "status": "ABNORMAL",
                "alert": True,
                "systolic": systolic,
                "diastolic": diastolic,
                "reason": "Blood pressure outside configured prototype range"
            }

        return {
            "status": "NORMAL",
            "alert": False,
            "systolic": systolic,
            "diastolic": diastolic
        }

    def check_emergency_button(self, pressed):

        if pressed:
            return {
                "status": "EMERGENCY",
                "alert": True,
                "reason": "Emergency button manually activated"
            }

        return {
            "status": "NORMAL",
            "alert": False
        }

    def check_all(
        self,
        heart_rate=None,
        spo2=None,
        temperature=None,
        systolic_bp=None,
        diastolic_bp=None,
        emergency_button=False
    ):

        heart_rate_result = self.check_heart_rate(
            heart_rate
        )

        spo2_result = self.check_spo2(
            spo2
        )

        temperature_result = self.check_temperature(
            temperature
        )

        blood_pressure_result = self.check_blood_pressure(
            systolic_bp,
            diastolic_bp
        )

        emergency_button_result = self.check_emergency_button(
            emergency_button
        )

        alerts = []

        if heart_rate_result["alert"]:
            alerts.append(heart_rate_result)

        if spo2_result["alert"]:
            alerts.append(spo2_result)

        if temperature_result["alert"]:
            alerts.append(temperature_result)

        if blood_pressure_result["alert"]:
            alerts.append(blood_pressure_result)

        if emergency_button_result["alert"]:
            alerts.append(emergency_button_result)

        return {
            "status": (
                "ABNORMAL"
                if alerts
                else "NORMAL"
            ),

            "alert": bool(alerts),

            "heart_rate": heart_rate_result,

            "spo2": spo2_result,

            "temperature": temperature_result,

            "blood_pressure": blood_pressure_result,

            "emergency_button": emergency_button_result,

            "alerts": alerts
        }


def create_health_monitor():

    return HealthMonitor()