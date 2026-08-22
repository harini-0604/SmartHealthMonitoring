
class HeartRateSensor:

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


def create_heart_rate_sensor():
    return HeartRateSensor()
