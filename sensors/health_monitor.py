class HealthMonitor:

    def __init__(self):

        # ----------------------------------------------------
        # DEMONSTRATION THRESHOLDS
        # ----------------------------------------------------
        # These are software-demo thresholds only.
        # They are NOT medical diagnostic limits.
        # ----------------------------------------------------

        self.heart_rate_min = 50.0
        self.heart_rate_max = 120.0

        self.spo2_min = 92.0

        self.temperature_min = 35.0
        self.temperature_max = 39.0


    # ========================================================
    # CHECK HEART RATE
    # ========================================================

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


    # ========================================================
    # CHECK SPO2
    # ========================================================

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


    # ========================================================
    # CHECK TEMPERATURE
    # ========================================================

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


    # ========================================================
    # CHECK ALL SENSORS
    # ========================================================

    def check_all(
        self,
        heart_rate=None,
        spo2=None,
        temperature=None
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

        alerts = []

        if heart_rate_result["alert"]:

            alerts.append(
                heart_rate_result
            )

        if spo2_result["alert"]:

            alerts.append(
                spo2_result
            )

        if temperature_result["alert"]:

            alerts.append(
                temperature_result
            )

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
            "alerts": alerts
        }


def create_health_monitor():

    return HealthMonitor()