import os
import joblib
import pandas as pd


class MultimodalRiskAI:

    RISK_LEVELS = {
        0: "LOW",
        1: "MODERATE",
        2: "HIGH",
        3: "CRITICAL"
    }

    FEATURE_NAMES = [
        "heart_rate",
        "spo2",
        "systolic_bp",
        "diastolic_bp",
        "temperature",
        "inactivity_duration",
        "possible_fall",
        "confirmed_fall",
        "pre_fall_risk",
        "acceleration_magnitude",
        "gyroscope_magnitude",
        "acceleration_change",
        "gyroscope_change"
    ]

    def __init__(self, model_path=None):

        if model_path is None:
            model_path = os.path.join(
                "models",
                "multimodal_risk_model.pkl"
            )

        self.model_path = model_path

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"Multimodal model not found: "
                f"{self.model_path}"
            )

        self.model = joblib.load(self.model_path)

        model_features = list(
            self.model.feature_names_in_
        )

        if model_features != self.FEATURE_NAMES:
            raise ValueError(
                "Multimodal model feature mismatch.\n"
                f"Expected: {self.FEATURE_NAMES}\n"
                f"Found: {model_features}"
            )

    def predict(
        self,
        heart_rate,
        spo2,
        systolic_bp,
        diastolic_bp,
        temperature,
        inactivity_duration=0.0,
        possible_fall=False,
        confirmed_fall=False,
        pre_fall_risk=False,
        acceleration_magnitude=0.0,
        gyroscope_magnitude=0.0,
        acceleration_change=0.0,
        gyroscope_change=0.0
    ):

        features = {
            "heart_rate": float(heart_rate),
            "spo2": float(spo2),
            "systolic_bp": float(systolic_bp),
            "diastolic_bp": float(diastolic_bp),
            "temperature": float(temperature),
            "inactivity_duration": float(
                inactivity_duration
            ),
            "possible_fall": int(possible_fall),
            "confirmed_fall": int(confirmed_fall),
            "pre_fall_risk": int(pre_fall_risk),
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
            )
        }

        input_data = pd.DataFrame(
            [features],
            columns=self.FEATURE_NAMES
        )

        prediction = int(
            self.model.predict(input_data)[0]
        )

        risk_level = self.RISK_LEVELS.get(
            prediction,
            "UNKNOWN"
        )

        probabilities = self.model.predict_proba(
            input_data
        )[0]

        confidence = float(
            max(probabilities)
        ) * 100

        return {
            "risk_class": prediction,
            "risk_level": risk_level,
            "confidence": confidence,
            "probabilities": {
                self.RISK_LEVELS[index]: float(
                    probabilities[position]
                )
                for position, index in enumerate(
                    self.model.classes_
                )
            }
        }


def create_multimodal_risk_ai():
    return MultimodalRiskAI()