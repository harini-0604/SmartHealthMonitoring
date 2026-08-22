import speech_recognition as sr

recognizer = sr.Recognizer()

print("=" * 60)
print("SMART HEALTH MONITORING")
print("MICROPHONE TEST")
print("=" * 60)

with sr.Microphone() as source:
    print("Adjusting for background noise...")
    recognizer.adjust_for_ambient_noise(source, duration=1)

    print("🎤 Listening... Please say something.")
    audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)

print("Processing your voice...")

try:
    text = recognizer.recognize_google(audio)
    print(f"YOU SAID: {text}")

except sr.UnknownValueError:
    print("Sorry, I could not understand your voice.")

except sr.RequestError as e:
    print(f"Speech recognition service error: {e}")

except Exception as e:
    print(f"Error: {e}")

print("=" * 60)
print("MICROPHONE TEST COMPLETE")
print("=" * 60)