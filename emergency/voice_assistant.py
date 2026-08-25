import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


import pyttsx3
import speech_recognition as sr

from emergency.emergency_manager import handle_emergency


# ============================================================
# TEXT TO SPEECH
# ============================================================

def speak(message):

    print(f"ASSISTANT: {message}")

    engine = pyttsx3.init()

    engine.setProperty(
        "rate",
        160
    )

    engine.setProperty(
        "volume",
        1.0
    )

    engine.say(message)

    engine.runAndWait()

    engine.stop()


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def listen():

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print("Listening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=5
            )

        print("Processing...")

        response = recognizer.recognize_google(
            audio
        )

        print(f"YOU: {response}")

        return response


    except sr.WaitTimeoutError:

        print("No speech detected.")

        return ""


    except sr.UnknownValueError:

        print("Could not understand the audio.")

        return ""


    except sr.RequestError as e:

        print(
            f"Speech recognition service error: {e}"
        )

        return ""


    except Exception as e:

        print(f"Error: {e}")

        return ""


# ============================================================
# EMERGENCY VOICE CHECK
# ============================================================

def run_voice_check():

    print("=" * 60)
    print("SMART HEALTH MONITORING")
    print("EMERGENCY VOICE CHECK")
    print("=" * 60)


    speak(
        "Hello. This is the Smart Health Monitoring system."
    )

    speak(
        "Are you okay? Please say yes or no."
    )


    response = listen()


    # ========================================================
    # NO RESPONSE
    # ========================================================

    if not response:

        speak(
            "I could not hear your response. Please try again."
        )

        print("STATUS: NO RESPONSE")

        return {
            "status": "NO RESPONSE"
        }


    # Convert response to lowercase

    response = response.lower().strip()

    # Normalize punctuation so voice responses can be
    # compared reliably.

    import re

    normalized_response = re.sub(
        r"[^a-zA-Z0-9']+",
        " ",
        response
    ).strip()

    response_words = set(
        normalized_response.split()
    )


    # ========================================================
    # RESPONSE KEYWORDS
    # ========================================================

    positive_words = {
        "yes",
        "yeah",
        "yep",
        "okay",
        "ok",
        "fine",
        "good"
    }

    negative_words = {
        "no",
        "help",
        "emergency",
        "pain",
        "hurt"
    }


    # ========================================================
    # POSSIBLE EMERGENCY
    # ========================================================

    if response_words.intersection(negative_words):

        speak(
            "I understand that you may need help."
        )


        result = handle_emergency(

            reason=f"User said: {response}",

            source="VOICE"

        )


        print(
            f"STATUS: {result['status']}"
        )


        return result


    # ========================================================
    # USER IS OKAY
    # ========================================================

    elif response_words.intersection(positive_words):

        speak(
            "Okay. I am glad you are okay."
        )


        print(
            "STATUS: USER OKAY"
        )


        return {

            "status": "USER OKAY",

            "response": response

        }


    # ========================================================
    # UNKNOWN RESPONSE
    # ========================================================

    else:

        speak(
            "I am not sure I understood your response."
        )


        print(
            "STATUS: UNKNOWN RESPONSE"
        )


        return {

            "status": "UNKNOWN RESPONSE",

            "response": response

        }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    result = run_voice_check()


    print("=" * 60)
    print("EMERGENCY VOICE CHECK COMPLETE")
    print("=" * 60)