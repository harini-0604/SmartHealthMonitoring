from emergency.emergency_manager import handle_verified_emergency


def main():

    print()
    print("=" * 75)
    print("SMART HEALTH MONITORING SYSTEM")
    print("END-TO-END EMERGENCY WORKFLOW TEST")
    print("=" * 75)

    result = handle_verified_emergency(
        reason="Simulated abnormal health condition",
        source="HARDWARE SIMULATOR",
        verification_duration=30
    )

    print()
    print("=" * 75)
    print("FINAL WORKFLOW RESULT")
    print("=" * 75)

    print(result)

    print("=" * 75)


if __name__ == "__main__":

    main()