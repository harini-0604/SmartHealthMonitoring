import os
import random

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


# ============================================================
# AI RISK MODEL TRAINING
# ============================================================

random.seed(42)

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "risk_model.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)


# Features:
# heart_rate
# spo2
# systolic_bp
# diastolic_bp
# temperature
# inactivity_duration
# possible_fall
# confirmed_fall
# emergency_button


def generate_sample():
    """
    Generate one synthetic project-training sample.

    Labels:
    0 = LOW
    1 = MODERATE
    2 = HIGH
    3 = CRITICAL
    """

    category = random.choice([
        "low",
        "moderate",
        "high",
        "critical"
    ])

    if category == "low":
        heart_rate = random.uniform(65, 90)
        spo2 = random.uniform(96, 100)
        systolic = random.uniform(105, 130)
        diastolic = random.uniform(65, 85)
        temperature = random.uniform(36.2, 37.4)
        inactivity = random.uniform(0, 30)
        possible_fall = 0
        confirmed_fall = 0
        emergency_button = 0
        label = 0

    elif category == "moderate":
        heart_rate = random.choice([
            random.uniform(45, 59),
            random.uniform(101, 120)
        ])
        spo2 = random.uniform(92, 95)
        systolic = random.choice([
            random.uniform(85, 99),
            random.uniform(131, 150)
        ])
        diastolic = random.choice([
            random.uniform(50, 59),
            random.uniform(91, 100)
        ])
        temperature = random.uniform(37.5, 38.5)
        inactivity = random.uniform(30, 90)
        possible_fall = random.choice([0, 1])
        confirmed_fall = 0
        emergency_button = 0
        label = 1

    elif category == "high":
        heart_rate = random.choice([
            random.uniform(40, 50),
            random.uniform(121, 145)
        ])
        spo2 = random.uniform(88, 93)
        systolic = random.choice([
            random.uniform(75, 90),
            random.uniform(145, 175)
        ])
        diastolic = random.choice([
            random.uniform(45, 60),
            random.uniform(95, 110)
        ])
        temperature = random.uniform(38.5, 40)
        inactivity = random.uniform(60, 180)
        possible_fall = 1
        confirmed_fall = random.choice([0, 1])
        emergency_button = 0
        label = 2

    else:
        heart_rate = random.choice([
            random.uniform(35, 45),
            random.uniform(140, 180)
        ])
        spo2 = random.uniform(80, 90)
        systolic = random.choice([
            random.uniform(60, 80),
            random.uniform(175, 210)
        ])
        diastolic = random.choice([
            random.uniform(35, 50),
            random.uniform(110, 130)
        ])
        temperature = random.uniform(39, 41)
        inactivity = random.uniform(120, 300)
        possible_fall = 1
        confirmed_fall = 1
        emergency_button = random.choice([0, 1])
        label = 3

    return [
        heart_rate,
        spo2,
        systolic,
        diastolic,
        temperature,
        inactivity,
        possible_fall,
        confirmed_fall,
        emergency_button,
        label
    ]


# ============================================================
# CREATE DATASET
# ============================================================

columns = [
    "heart_rate",
    "spo2",
    "systolic_bp",
    "diastolic_bp",
    "temperature",
    "inactivity_duration",
    "possible_fall",
    "confirmed_fall",
    "emergency_button",
    "risk_level"
]

data = [generate_sample() for _ in range(2000)]

df = pd.DataFrame(data, columns=columns)

print()
print("=" * 70)
print("AI RISK SCORING MODEL TRAINING")
print("=" * 70)

print(f"Dataset samples : {len(df)}")
print("Features        : 9")
print("Classes         : LOW / MODERATE / HIGH / CRITICAL")


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X = df.drop("risk_level", axis=1)
y = df["risk_level"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# ============================================================
# RANDOM FOREST
# ============================================================

model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    max_depth=10,
    class_weight="balanced"
)

model.fit(X_train, y_train)


# ============================================================
# EVALUATION
# ============================================================

predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print()
print(f"Model Accuracy : {accuracy * 100:.2f}%")

print()
print("Classification Report")
print("-" * 70)

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "LOW",
            "MODERATE",
            "HIGH",
            "CRITICAL"
        ]
    )
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print("Feature Importance")
print("-" * 70)

for feature, importance in zip(
    X.columns,
    model.feature_importances_
):
    print(f"{feature:25s}: {importance:.4f}")


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(model, MODEL_PATH)

print()
print("=" * 70)
print("AI MODEL SAVED")
print("=" * 70)
print(f"Model path : {MODEL_PATH}")
print("=" * 70)