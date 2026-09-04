import os
import joblib
import pandas as pd

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "models",
    "risk_model.pkl"
)


class AIRiskScorer:

    def __init__(self, model_path=MODEL_PATH):

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"AI risk model not found: {model_path}"
            )

        self.model = joblib.load(model_path)

        self.feature_names = [
            "heart_rate",
            "spo2",
            "systolic_bp",
            "diastolic_bp",
            "temperature",
            "inactivity_duration",
            "possible_fall",
            "confirmed_fall",
            "emergency_button"
        ]

    def predict(
        self,
        heart_rate,
        spo2,
        systolic_bp,
        diastolic_bp,
        temperature,
        inactivity_duration=0,
        possible_fall=False,
        confirmed_fall=False,
        emergency_button=False
    ):

        values = pd.DataFrame([[
            heart_rate,
            spo2,
            systolic_bp,
            diastolic_bp,
            temperature,
            inactivity_duration,
            int(possible_fall),
            int(confirmed_fall),
            int(emergency_button)
        ]], columns=self.feature_names)

        prediction = self.model.predict(values)[0]

        probabilities = self.model.predict_proba(values)[0]

        confidence = float(max(probabilities)) * 100

        risk_levels = {
            0: "LOW",
            1: "MODERATE",
            2: "HIGH",
            3: "CRITICAL"
        }

        risk_level = risk_levels.get(
            int(prediction),
            "UNKNOWN"
        )

        # Convert model class to a project-friendly risk score.
        score_mapping = {
            "LOW": 15,
            "MODERATE": 40,
            "HIGH": 70,
            "CRITICAL": 90
        }

        risk_score = score_mapping.get(
            risk_level,
            0
        )

        risk_score = score_mapping.get(
            risk_level,
            0
        )

        if emergency_button:
            risk_score = 100
            risk_level = "CRITICAL"

        reasons = []

        if spo2 < 92:
            reasons.append("Low SpO2")

        if heart_rate < 50 or heart_rate > 120:
            reasons.append("Abnormal heart rate")

        if temperature < 35 or temperature > 39:
            reasons.append("Abnormal temperature")

        if systolic_bp < 90 or systolic_bp > 140:
            reasons.append("Abnormal systolic blood pressure")

        if diastolic_bp < 60 or diastolic_bp > 90:
            reasons.append("Abnormal diastolic blood pressure")

        if inactivity_duration >= 60:
            reasons.append("Prolonged inactivity")

        if possible_fall:
            reasons.append("Possible fall detected")

        if confirmed_fall:
            reasons.append("Confirmed fall detected")

        if emergency_button:
            reasons.append("Emergency button activated")

        if not reasons:
            reasons.append("No major abnormal conditions detected")

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence": round(confidence, 2),
            "reasons": reasons
        }


def create_ai_risk_scorer():

    return AIRiskScorer()


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    scorer = create_ai_risk_scorer()

    print()
    print("=" * 70)
    print("AI RISK SCORING ENGINE TEST")
    print("=" * 70)

    result = scorer.predict(
        heart_rate=165,
        spo2=85,
        systolic_bp=190,
        diastolic_bp=120,
        temperature=40.0,
        inactivity_duration=180,
        possible_fall=True,
        confirmed_fall=True,
        emergency_button=True
    )

    print(f"Risk Score : {result['risk_score']}/100")
    print(f"Risk Level : {result['risk_level']}")
    print(f"Confidence : {result['confidence']}%")

    print()
    print("Reasons:")

    for reason in result["reasons"]:
        print(f" - {reason}")

    print()
    print("=" * 70)
    print("AI RISK ENGINE TEST COMPLETED")
    print("=" * 70)