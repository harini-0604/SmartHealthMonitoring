from sensors.hardware_simulator import create_hardware_simulator
from ai.risk_ai import create_ai_risk_scorer


print()
print("=" * 75)
print("SMART HEALTH MONITORING SYSTEM")
print("AI RISK + HARDWARE INTEGRATION TEST")
print("=" * 75)


hardware = create_hardware_simulator()
ai_risk = create_ai_risk_scorer()

hardware.start()


# ============================================================
# TEST 1 — NORMAL
# ============================================================

print()
print("=" * 75)
print("TEST 1 : NORMAL HEALTH CONDITION")
print("=" * 75)

data = hardware.generate_normal_data()

result = ai_risk.predict(
    heart_rate=data["heart_rate"],
    spo2=data["spo2"],
    systolic_bp=data["systolic_bp"],
    diastolic_bp=data["diastolic_bp"],
    temperature=data["temperature"],
    inactivity_duration=10,
    possible_fall=False,
    confirmed_fall=False,
    emergency_button=data["emergency_button"]
)

print(f"HR         : {data['heart_rate']}")
print(f"SpO2       : {data['spo2']}")
print(f"BP         : {data['systolic_bp']}/{data['diastolic_bp']}")
print(f"Temperature: {data['temperature']}")
print(f"Risk Score : {result['risk_score']}/100")
print(f"Risk Level : {result['risk_level']}")
print(f"Confidence : {result['confidence']}%")


# ============================================================
# TEST 2 — ABNORMAL
# ============================================================

print()
print("=" * 75)
print("TEST 2 : ABNORMAL HEALTH CONDITION")
print("=" * 75)

data = hardware.generate_abnormal_data()

result = ai_risk.predict(
    heart_rate=data["heart_rate"],
    spo2=data["spo2"],
    systolic_bp=data["systolic_bp"],
    diastolic_bp=data["diastolic_bp"],
    temperature=data["temperature"],
    inactivity_duration=100,
    possible_fall=True,
    confirmed_fall=False,
    emergency_button=data["emergency_button"]
)

print(f"HR         : {data['heart_rate']}")
print(f"SpO2       : {data['spo2']}")
print(f"BP         : {data['systolic_bp']}/{data['diastolic_bp']}")
print(f"Temperature: {data['temperature']}")
print(f"Risk Score : {result['risk_score']}/100")
print(f"Risk Level : {result['risk_level']}")
print(f"Confidence : {result['confidence']}%")


# ============================================================
# TEST 3 — EMERGENCY BUTTON
# ============================================================

print()
print("=" * 75)
print("TEST 3 : MANUAL EMERGENCY BUTTON")
print("=" * 75)

data = hardware.press_emergency_button()

result = ai_risk.predict(
    heart_rate=data["heart_rate"],
    spo2=data["spo2"],
    systolic_bp=data["systolic_bp"],
    diastolic_bp=data["diastolic_bp"],
    temperature=data["temperature"],
    inactivity_duration=0,
    possible_fall=False,
    confirmed_fall=False,
    emergency_button=data["emergency_button"]
)

print(f"Emergency Button : {data['emergency_button']}")
print(f"Risk Score       : {result['risk_score']}/100")
print(f"Risk Level       : {result['risk_level']}")
print(f"Confidence       : {result['confidence']}%")


hardware.stop()


print()
print("=" * 75)
print("AI + HARDWARE INTEGRATION TEST COMPLETED")
print("=" * 75)