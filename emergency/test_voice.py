import pyttsx3

engine = pyttsx3.init()

engine.setProperty("rate", 160)
engine.setProperty("volume", 1.0)

engine.say("This is the first sentence.")

engine.say("This is the second sentence.")

engine.say("Can you hear all three sentences?")

engine.runAndWait()

print("Voice test completed.")