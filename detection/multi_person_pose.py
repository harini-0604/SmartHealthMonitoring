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


# ============================================================
# MULTI-PERSON POSE + TRACKING
# ============================================================

def run_multi_person_pose():

    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open camera.")

        pose.close()

        return False

    print()
    print("=" * 70)
    print("SMART HEALTH MONITORING SYSTEM")
    print("MULTI-PERSON POSE + TRACKING")
    print("=" * 70)
    print("Detecting, tracking and estimating pose for multiple people.")
    print("Press Q to close.")
    print()

    try:

        while True:

            ret, frame = camera.read()

            if not ret:

                print("ERROR: Could not read camera frame.")

                break


            # ------------------------------------------------
            # YOLO TRACKING
            # ------------------------------------------------

            results = model.track(
                frame,
                classes=[0],
                persist=True,
                verbose=False
            )


            person_count = 0


            # ------------------------------------------------
            # PROCESS DETECTED PEOPLE
            # ------------------------------------------------

            for result in results:

                if result.boxes is None:

                    continue


                boxes = result.boxes


                for index in range(len(boxes)):

                    class_id = int(
                        boxes.cls[index]
                    )

                    confidence = float(
                        boxes.conf[index]
                    )


                    if (
                        class_id != 0
                        or confidence < CONFIDENCE_THRESHOLD
                    ):

                        continue


                    person_count += 1


                    # ------------------------------------------------
                    # TRACK ID
                    # ------------------------------------------------

                    track_id = None

                    if boxes.id is not None:

                        track_id = int(
                            boxes.id[index]
                        )


                    if track_id is None:

                        track_id = person_count


                    # ------------------------------------------------
                    # BOUNDING BOX
                    # ------------------------------------------------

                    x1, y1, x2, y2 = map(
                        int,
                        boxes.xyxy[index]
                    )


                    frame_height, frame_width = frame.shape[:2]


                    x1 = max(0, x1)
                    y1 = max(0, y1)

                    x2 = min(frame_width, x2)
                    y2 = min(frame_height, y2)


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
                        f"ID {track_id} "
                        f"({confidence:.2f})",
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
                    # PERSON CROP
                    # ------------------------------------------------

                    person_crop = frame[
                        y1:y2,
                        x1:x2
                    ]


                    if person_crop.size == 0:

                        continue


                    # ------------------------------------------------
                    # MEDIAPIPE POSE
                    # ------------------------------------------------

                    rgb_person = cv2.cvtColor(
                        person_crop,
                        cv2.COLOR_BGR2RGB
                    )


                    pose_results = pose.process(
                        rgb_person
                    )


                    # ------------------------------------------------
                    # DRAW POSE
                    # ------------------------------------------------

                    if pose_results.pose_landmarks:

                        mp_drawing.draw_landmarks(
                            person_crop,
                            pose_results.pose_landmarks,
                            mp_pose.POSE_CONNECTIONS
                        )


                        cv2.putText(
                            frame,
                            f"POSE ID {track_id}",
                            (
                                x1,
                                min(
                                    frame_height - 10,
                                    y2 + 20
                                )
                            ),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.55,
                            (255, 255, 0),
                            2
                        )


                    # ------------------------------------------------
                    # PUT PERSON BACK
                    # ------------------------------------------------

                    frame[
                        y1:y2,
                        x1:x2
                    ] = person_crop


            # ------------------------------------------------
            # PERSON COUNT
            # ------------------------------------------------

            cv2.putText(
                frame,
                f"People Tracked: {person_count}",
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
                "Smart Health Monitoring - Multi-Person Tracking",
                frame
            )


            key = cv2.waitKey(1) & 0xFF


            if key == ord("q"):

                break


    finally:

        camera.release()

        cv2.destroyAllWindows()

        pose.close()


    print()
    print("=" * 70)
    print("MULTI-PERSON POSE + TRACKING STOPPED")
    print("=" * 70)

    return True


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_multi_person_pose()