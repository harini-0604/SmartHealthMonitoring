
class SpO2Sensor:

    def __init__(self):
        self.value = None

    def update(self, value):
        if value is None:
            self.value = None
            return self.value

        self.value = float(value)
        return self.value

    def read(self):
        return self.value


def create_spo2_sensor():
    return SpO2Sensor()
