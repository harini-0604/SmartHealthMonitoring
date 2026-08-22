from datetime import datetime
from pathlib import Path

from emergency.voice_assistant import run_voice_check
from detection.person_detection import run_person_detection
from detection.pose_detection import run_pose_detection
from detection.fall_detection import run_fall_detection


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

LOG_FOLDER = PROJECT_ROOT / "logs"

EMERGENCY_LOG = LOG_FOLDER / "emergency_log.txt"
SESSION_LOG = LOG_FOLDER / "session_log.txt"


# ============================================================
# STARTUP
# ============================================================

def show_startup():

    print("=" * 65)
    print("SMART HEALTH MONITORING SYSTEM")
    print("=" * 65)

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print(f"Start time : {current_time}")
    print()

    print("Available modules:")
    print("  [1] Voice Assistant")
    print("  [2] Person Detection")
    print("  [3] Pose Estimation")
    print("  [4] Fall Detection")
    print("  [5] Emergency Manager")

    print("=" * 65)


# ============================================================
# EMERGENCY LOG
# ============================================================

def show_emergency_log():

    print()
    print("=" * 65)
    print("EMERGENCY EVENT LOG")
    print("=" * 65)

    if not EMERGENCY_LOG.exists():

        print("No emergency events recorded.")

        return


    with open(
        EMERGENCY_LOG,
        "r",
        encoding="utf-8"
    ) as file:

        events = [
            line.strip()
            for line in file
            if line.strip()
        ]


    if not events:

        print("No emergency events recorded.")

        return


    print(
        f"Total recorded events: {len(events)}"
    )

    print()

    for event in events:

        print(event)


# ============================================================
# SESSION LOGGER
# ============================================================

def save_session_log(
    voice_result=None,
    person_result=None,
    pose_result=None,
    fall_result=None
):

    LOG_FOLDER.mkdir(
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        SESSION_LOG,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n"
            + "=" * 60
            + "\n"
        )

        file.write(
            f"SESSION TIME: {timestamp}\n"
        )

        file.write(
            f"VOICE: {voice_result}\n"
        )

        file.write(
            f"PERSON DETECTION: {person_result}\n"
        )

        file.write(
            f"POSE ESTIMATION: {pose_result}\n"
        )

        file.write(
            f"FALL DETECTION: {fall_result}\n"
        )


# ============================================================
# COMPLETE MONITORING
# ============================================================

def run_complete_monitoring():

    print()
    print("=" * 65)
    print("STARTING COMPLETE HEALTH MONITORING")
    print("=" * 65)


    # --------------------------------------------------------
    # VOICE
    # --------------------------------------------------------

    print()
    print("Starting Voice Assistant...")

    voice_result = run_voice_check()

    print(
        f"Voice result: {voice_result}"
    )


    # --------------------------------------------------------
    # PERSON
    # --------------------------------------------------------

    print()
    print("Starting Person Detection...")

    person_result = run_person_detection()

    print(
        f"Person result: {person_result}"
    )


    # --------------------------------------------------------
    # POSE
    # --------------------------------------------------------

    print()
    print("Starting Pose Estimation...")

    pose_result = run_pose_detection()

    print(
        f"Pose result: {pose_result}"
    )


    # --------------------------------------------------------
    # FALL
    # --------------------------------------------------------

    print()
    print("Starting Fall Detection...")

    fall_result = run_fall_detection()

    print(
        f"Fall result: {fall_result}"
    )


    # --------------------------------------------------------
    # SAVE SESSION
    # --------------------------------------------------------

    save_session_log(
        voice_result,
        person_result,
        pose_result,
        fall_result
    )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print()
    print("=" * 65)
    print("MONITORING SESSION SUMMARY")
    print("=" * 65)

    print(
        f"Voice Assistant : {voice_result}"
    )

    print(
        f"Person Detection: {person_result}"
    )

    print(
        f"Pose Estimation : {pose_result}"
    )

    print(
        f"Fall Detection  : {fall_result}"
    )

    print("=" * 65)

    print(
        f"Session log saved to: {SESSION_LOG}"
    )


# ============================================================
# MAIN MENU
# ============================================================

def main():

    show_startup()

    while True:

        print()
        print("=" * 65)
        print("MAIN MENU")
        print("=" * 65)

        print("[1] Run Complete Monitoring")
        print("[2] Voice Emergency Check")
        print("[3] Fall Detection")
        print("[4] View Emergency Log")
        print("[5] Exit")

        print("=" * 65)

        choice = input(
            "Enter your choice: "
        ).strip()


        # ====================================================
        # COMPLETE MONITORING
        # ====================================================

        if choice == "1":

            run_complete_monitoring()


        # ====================================================
        # VOICE
        # ====================================================

        elif choice == "2":

            print()
            print("=" * 65)
            print("VOICE EMERGENCY CHECK")
            print("=" * 65)

            result = run_voice_check()

            print()
            print(
                f"Voice Assistant result: {result}"
            )


        # ====================================================
        # FALL
        # ====================================================

        elif choice == "3":

            print()
            print("=" * 65)
            print("FALL DETECTION")
            print("=" * 65)

            result = run_fall_detection()

            print()
            print(
                f"Fall Detection result: {result}"
            )


        # ====================================================
        # EMERGENCY LOG
        # ====================================================

        elif choice == "4":

            show_emergency_log()


        # ====================================================
        # EXIT
        # ====================================================

        elif choice == "5":

            print()
            print(
                "Exiting Smart Health Monitoring System."
            )

            break


        else:

            print()
            print(
                "Invalid choice. Please select 1-5."
            )


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()