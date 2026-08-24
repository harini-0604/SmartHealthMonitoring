from emergency.verification import EmergencyVerification

print()
print("=" * 70)
print("END-TO-END EMERGENCY FLOW TEST")
print("=" * 70)

verification = EmergencyVerification(
    duration=30
)

verification.start(
    reason="Simulated fall detected",
    source="FALL DETECTION TEST"
)

print()
print("Starting voice verification...")
print()

result = verification.run_voice_verification()

print()
print("=" * 70)
print("END-TO-END TEST RESULT")
print("=" * 70)
print(result)
print("=" * 70)
