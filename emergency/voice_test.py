from voice_assistant import speak, listen_for_response

print("=" * 60)
print("SMART HEALTH MONITORING")
print("VOICE ASSISTANT TEST")
print("=" * 60)

print("\nTEST 1: Speaker")

speak("Hello. This is the Smart Health Monitoring system.")

print("TEST 1 COMPLETE")

print("\nTEST 2: Second voice message")

speak("Are you okay? Please say yes or no.")

print("TEST 2 COMPLETE")

print("\nTEST 3: Microphone")

response = listen_for_response(timeout=10)

print("\nResponse received:", response)

if response is None:

    speak("I did not receive a response.")

elif "yes" in response:

    speak("Okay. Emergency alert cancelled.")

elif "no" in response:

    speak("I understand. Emergency assistance may be required.")

else:

    speak("I could not understand your response.")

print("\nVOICE TEST COMPLETE")