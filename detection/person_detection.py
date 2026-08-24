import cv2
from ultralytics import YOLO
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "yolo11n.pt"

CONFIDENCE_THRESHOLD = 0.65

# Number of consecutive frames required before
# accepting a detection as stable.
STABLE_FRAMES_REQUIRED = 5


# ============================================================
# PERSON DETECTION
# ============================================================

def run_person_detection():

    # --------------------------------------------------------
    # Load YOLO model
    # --------------------------------------------------------

    model = YOLO(MODEL_PATH)


    # --------------------------------------------------------
    # Open webcam
    # --------------------------------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open the camera.")

        return False


    # --------------------------------------------------------
    # START MESSAGE
    # --------------------------------------------------------

    print("=" * 60)
    print("SMART HEALTH MONITORING SYSTEM")
    print("AI PERSON DETECTION STARTED")
    print("=" * 60)
    print("Press Q to close the camera.\n")


    # --------------------------------------------------------
    # Detection state
    # --------------------------------------------------------

    previous_count = -1

    stable_count = 0

    last_detected_count = 0


    # ========================================================
    # MAIN LOOP
    # ========================================================

    while True:

        # ----------------------------------------------------
        # Read camera
        # ----------------------------------------------------

        ret, frame = camera.read()

        if not ret:

            print("ERROR: Could not read camera frame.")

            break


        # ----------------------------------------------------
        # YOLO DETECTION
        # ----------------------------------------------------
        #
        # classes=[0] means:
        # Only detect the PERSON class.
        #
        # conf=0.65 means:
        # Ignore detections below 65% confidence.
        # ----------------------------------------------------

        results = model(
            frame,
            classes=[0],
            conf=CONFIDENCE_THRESHOLD,
            verbose=False
        )


        # ----------------------------------------------------
        # Count detected people
        # ----------------------------------------------------

        detected_person_count = 0


        for result in results:

            for box in result.boxes:

                class_id = int(box.cls[0])

                confidence = float(box.conf[0])


                # ------------------------------------------------
                # Extra safety check
                # ------------------------------------------------

                if class_id == 0 and confidence >= 0.60:
                
                    detected_person_count += 1


        # ----------------------------------------------------
        # STABLE DETECTION
        # ----------------------------------------------------
        #
        # If the same count appears repeatedly,
        # consider it a stable detection.
        # ----------------------------------------------------

        if detected_person_count == last_detected_count:

            stable_count += 1

        else:

            stable_count = 1

            last_detected_count = detected_person_count


        # ----------------------------------------------------
        # Accept detection only after several frames
        # ----------------------------------------------------

        if stable_count >= STABLE_FRAMES_REQUIRED:

            person_count = detected_person_count

        else:

            # Keep previous stable count while waiting
            # for confirmation.
            if previous_count == -1:

                person_count = 0

            else:

                person_count = previous_count


        # ----------------------------------------------------
        # PRINT WHEN STABLE COUNT CHANGES
        # ----------------------------------------------------

        if person_count != previous_count:

            current_time = datetime.now().strftime(
                "%H:%M:%S"
            )


            if person_count == 0:

                message = (
                    "No person detected - 0"
                )

            elif person_count == 1:

                message = (
                    "Person detected - 1"
                )

            else:

                message = (
                    f"Multiple people detected - "
                    f"{person_count}"
                )


            print(
                f"[{current_time}] {message}"
            )


            previous_count = person_count


        # ----------------------------------------------------
        # DRAW YOLO BOXES
        # ----------------------------------------------------

        annotated_frame = results[0].plot()


        # ----------------------------------------------------
        # DISPLAY PERSON COUNT
        # ----------------------------------------------------

        cv2.putText(
            annotated_frame,
            f"People: {person_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        # ----------------------------------------------------
        # DISPLAY CAMERA
        # ----------------------------------------------------

        cv2.imshow(
            "Smart Health Monitoring - Person Detection",
            annotated_frame
        )


        # ----------------------------------------------------
        # QUIT
        # ----------------------------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


    # ========================================================
    # CLEANUP
    # ========================================================

    camera.release()

    cv2.destroyAllWindows()


    print("\nCamera stopped.")
    print("Person detection system closed.")


    return True


# ============================================================
# DIRECT EXECUTION
# ============================================================

if __name__ == "__main__":

    run_person_detection()

# ============================================================
# REAL-TIME FRAME PERSON DETECTION
# ============================================================

def process_person_frame(
    frame,
    model,
    previous_count=0,
    stable_count=0,
    last_detected_count=0
):

    results = model(
        frame,
        classes=[0],
        conf=CONFIDENCE_THRESHOLD,
        verbose=False
    )

    detected_person_count = 0

    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if class_id == 0 and confidence >= 0.60:

                detected_person_count += 1

    # --------------------------------------------------------
    # STABLE DETECTION
    # --------------------------------------------------------

    if detected_person_count == last_detected_count:

        stable_count += 1

    else:

        stable_count = 1
        last_detected_count = detected_person_count

    if stable_count >= STABLE_FRAMES_REQUIRED:

        person_count = detected_person_count

    else:

        person_count = previous_count

    # --------------------------------------------------------
    # ANNOTATED FRAME
    # --------------------------------------------------------

    annotated_frame = results[0].plot(
        labels=False,
        conf=False
    )


    cv2.putText(
        annotated_frame,
        f"People: {person_count}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    return (
        annotated_frame,
        person_count,
        stable_count,
        last_detected_count
    )