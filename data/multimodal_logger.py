import csv
import os
from datetime import datetime
from data.sample_id import create_sample_id_generator


DATASET_PATH = os.path.join(
    "data",
    "multimodal_dataset.csv"
)


FIELDNAMES = [
    "sample_id",
    "timestamp",
    "heart_rate",
    "spo2",
    "systolic_bp",
    "diastolic_bp",
    "temperature",
    "inactivity_duration",
    "possible_fall",
    "pre_fall_risk",
    "confirmed_fall",
    "acceleration_magnitude",
    "gyroscope_magnitude",
    "acceleration_change",
    "gyroscope_change",
    "risk_class",
    "risk_level",
    "risk_confidence"
]


class MultimodalDataLogger:

    def __init__(self, dataset_path=DATASET_PATH):

        self.dataset_path = dataset_path
        self.sample_id_generator = create_sample_id_generator()

        directory = os.path.dirname(
            self.dataset_path
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        self._initialize_dataset()

    def _initialize_dataset(self):

        if (
            not os.path.exists(self.dataset_path)
            or os.path.getsize(self.dataset_path) == 0
        ):

            with open(
                self.dataset_path,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=FIELDNAMES
                )

                writer.writeheader()

    def log_sample(
        self,
        heart_rate,
        spo2,
        systolic_bp,
        diastolic_bp,
        temperature,
        inactivity_duration=0.0,
        possible_fall=False,
        pre_fall_risk=False,
        confirmed_fall=False,
        acceleration_magnitude=0.0,
        gyroscope_magnitude=0.0,
        acceleration_change=0.0,
        gyroscope_change=0.0,
        risk_class=None,
        risk_level="UNKNOWN",
        risk_confidence=0.0
    ):

        sample = {
            "sample_id": self.sample_id_generator.next_id(),
            
            "timestamp": datetime.now().isoformat(
                timespec="milliseconds"
            ),

            "heart_rate": float(
                heart_rate
            ),

            "spo2": float(
                spo2
            ),

            "systolic_bp": float(
                systolic_bp
            ),

            "diastolic_bp": float(
                diastolic_bp
            ),

            "temperature": float(
                temperature
            ),

            "inactivity_duration": float(
                inactivity_duration
            ),

            "possible_fall": int(
                bool(possible_fall)
            ),

            "pre_fall_risk": int(
                bool(pre_fall_risk)
            ),

            "confirmed_fall": int(
                bool(confirmed_fall)
            ),

            "acceleration_magnitude": float(
                acceleration_magnitude
            ),

            "gyroscope_magnitude": float(
                gyroscope_magnitude
            ),

            "acceleration_change": float(
                acceleration_change
            ),

            "gyroscope_change": float(
                gyroscope_change
            ),

            "risk_class": (
                int(risk_class)
                if risk_class is not None
                else ""
            ),

            "risk_level": str(
                risk_level
            ),

            "risk_confidence": float(
                risk_confidence
            )
        }

        with open(
            self.dataset_path,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=FIELDNAMES
            )

            writer.writerow(sample)

        return sample


def create_multimodal_logger():
    return MultimodalDataLogger()