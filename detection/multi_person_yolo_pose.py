import cv2
import mediapipe as mp
from ultralytics import YOLO


# ============================================================
# INITIALIZATION
# ============================================================

model = YOLO("yolo11n.pt")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# ============================================================
# SETTINGS
# ============================================================

CONFIDENCE_THRESHOLD = 0.50
LANDMARK_VISIBILITY_THRESHOLD = 0.60


# ============================================================
# MULTI-PERSON POSE
# ============================================================

def run_multi_person_pose():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open camera.")

        return False


    print()
    print("=" * 70)
    print("SMART HEALTH MONITORING SYSTEM")
    print("MULTI-PERSON MEDIAPIPE POSE")
    print("=" * 70)
    print("YOLO detects people.")
    print("MediaPipe estimates pose separately for each person.")
    print("Press Q to close.")
    print()


    try:

        while True:

            ret, frame = camera.read()

            if not ret:

                print("ERROR: Could not read camera frame.")

                break


            # ------------------------------------------------
            # YOLO PERSON DETECTION
            # ------------------------------------------------

            results = model(
                frame,
                classes=[0],
                conf=CONFIDENCE_THRESHOLD,
                verbose=False
            )


            person_count = 0


            # ------------------------------------------------
            # PROCESS EACH DETECTED PERSON
            # ------------------------------------------------

            for result in results:

                if result.boxes is None:

                    continue


                for box in result.boxes:

                    class_id = int(
                        box.cls[0]
                    )

                    confidence = float(
                        box.conf[0]
                    )


                    if (
                        class_id != 0
                        or confidence < CONFIDENCE_THRESHOLD
                    ):

                        continue


                    person_count += 1


                    # ------------------------------------------------
                    # GET BOUNDING BOX
                    # ------------------------------------------------

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0]
                    )


                    frame_height, frame_width = (
                        frame.shape[:2]
                    )


                    # Keep box inside frame

                    x1 = max(0, x1)
                    y1 = max(0, y1)

                    x2 = min(frame_width, x2)
                    y2 = min(frame_height, y2)


                    if x2 <= x1 or y2 <= y1:

                        continue


                    # ------------------------------------------------
                    # DRAW PERSON BOX
                    # ------------------------------------------------

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )


                    cv2.putText(
                        frame,
                        f"Person {person_count}",
                        (
                            x1,
                            max(25, y1 - 10)
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        (0, 255, 0),
                        2
                    )


                    # ------------------------------------------------
                    # CREATE PERSON CROP
                    # ------------------------------------------------

                    person_crop = frame[
                        y1:y2,
                        x1:x2
                    ].copy()


                    if person_crop.size == 0:

                        continue


                    # ------------------------------------------------
                    # SEPARATE MEDIAPIPE INSTANCE
                    # ------------------------------------------------

                    person_pose = mp_pose.Pose(
                        static_image_mode=True,
                        model_complexity=1,
                        enable_segmentation=False,
                        min_detection_confidence=0.5,
                        min_tracking_confidence=0.5
                    )


                    # ------------------------------------------------
                    # RGB CONVERSION
                    # ------------------------------------------------

                    rgb_person = cv2.cvtColor(
                        person_crop,
                        cv2.COLOR_BGR2RGB
                    )


                    # ------------------------------------------------
                    # POSE ESTIMATION
                    # ------------------------------------------------

                    pose_results = person_pose.process(
                        rgb_person
                    )


                    # ------------------------------------------------
                    # DRAW POSE
                    # ------------------------------------------------

                    if pose_results.pose_landmarks:

                        landmarks = (
                            pose_results.pose_landmarks
                        )


                        # ------------------------------------------------
                        # FILTER LOW-VISIBILITY LANDMARKS
                        # ------------------------------------------------

                        for landmark in landmarks.landmark:

                            if (
                                landmark.visibility
                                < LANDMARK_VISIBILITY_THRESHOLD
                            ):

                                landmark.x = -1

                                landmark.y = -1


                        # ------------------------------------------------
                        # DRAW MEDIA PIPE SKELETON
                        # ------------------------------------------------

                        mp_drawing.draw_landmarks(
                            person_crop,
                            landmarks,
                            mp_pose.POSE_CONNECTIONS,
                            mp_drawing.DrawingSpec(
                                color=(0, 255, 0),
                                thickness=2,
                                circle_radius=3
                            ),
                            mp_drawing.DrawingSpec(
                                color=(255, 255, 0),
                                thickness=2,
                                circle_radius=2
                            )
                        )


                    # ------------------------------------------------
                    # CLOSE PERSON POSE INSTANCE
                    # ------------------------------------------------

                    person_pose.close()


                    # ------------------------------------------------
                    # PUT POSE CROP BACK
                    # ------------------------------------------------

                    frame[
                        y1:y2,
                        x1:x2
                    ] = person_crop


            # ------------------------------------------------
            # PEOPLE COUNT
            # ------------------------------------------------

            cv2.putText(
                frame,
                f"People Detected: {person_count}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 255, 255),
                2
            )


            # ------------------------------------------------
            # DISPLAY
            # ------------------------------------------------

            cv2.imshow(
                "Smart Health Monitoring - Multi-Person Pose",
                frame
            )


            key = cv2.waitKey(1) & 0xFF


            if key == ord("q"):

                break


    finally:

        camera.release()

        cv2.destroyAllWindows()


    print()
    print("=" * 70)
    print("MULTI-PERSON POSE STOPPED")
    print("=" * 70)

    return True


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_multi_person_pose()