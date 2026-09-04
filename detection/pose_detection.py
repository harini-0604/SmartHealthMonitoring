import cv2
import mediapipe as mp
from ultralytics import YOLO


# ============================================================
# MULTI-PERSON POSE ESTIMATION
# ============================================================

CONFIDENCE_THRESHOLD = 0.50

model = YOLO("yolo11n.pt")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# ============================================================
# DRAW PERSON LABEL
# ============================================================

def draw_person_label(
    frame,
    x1,
    y1,
    person_id
):

    label = f"Person {person_id}"

    cv2.rectangle(
        frame,
        (x1, max(0, y1 - 32)),
        (x1 + 120, y1),
        (255, 0, 0),
        -1
    )

    cv2.putText(
        frame,
        label,
        (x1 + 6, y1 - 9),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


# ============================================================
# MULTI-PERSON POSE DETECTION
# ============================================================

def run_pose_detection():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print("ERROR: Could not open camera.")

        return False

    print("=" * 70)
    print("SMART HEALTH MONITORING SYSTEM")
    print("MULTI-PERSON POSE ESTIMATION")
    print("=" * 70)
    print("Press Q to close.\n")

    try:

        while True:

            ret, frame = camera.read()

            if not ret:

                print(
                    "ERROR: Could not read camera frame."
                )

                break

            frame_height, frame_width = frame.shape[:2]

            # ------------------------------------------------
            # YOLO PERSON DETECTION
            # ------------------------------------------------

            results = model(
                frame,
                classes=[0],
                conf=CONFIDENCE_THRESHOLD,
                verbose=False
            )

            persons = []

            for result in results:

                for box in result.boxes:

                    confidence = float(
                        box.conf[0]
                    )

                    if confidence < CONFIDENCE_THRESHOLD:
                        continue

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0]
                    )

                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(frame_width, x2)
                    y2 = min(frame_height, y2)

                    if x2 <= x1 or y2 <= y1:
                        continue

                    persons.append(
                        (x1, y1, x2, y2)
                    )

            # ------------------------------------------------
            # SORT PERSONS LEFT → RIGHT
            # ------------------------------------------------

            persons.sort(
                key=lambda box: box[0]
            )

            # ------------------------------------------------
            # PROCESS EACH PERSON SEPARATELY
            # ------------------------------------------------

            for person_id, (
                x1,
                y1,
                x2,
                y2
            ) in enumerate(persons, start=1):

                person_crop = frame[
                    y1:y2,
                    x1:x2
                ]

                if person_crop.size == 0:
                    continue

                rgb_crop = cv2.cvtColor(
                    person_crop,
                    cv2.COLOR_BGR2RGB
                )

                # Separate pose estimator for this person
                with mp_pose.Pose(
                    static_image_mode=True,
                    model_complexity=1,
                    enable_segmentation=False,
                    min_detection_confidence=0.5
                ) as pose:

                    pose_results = pose.process(
                        rgb_crop
                    )

                # ------------------------------------------------
                # PERSON BOX
                # ------------------------------------------------

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 0, 0),
                    3
                )

                # ------------------------------------------------
                # PERSON LABEL
                # ------------------------------------------------

                draw_person_label(
                    frame,
                    x1,
                    y1,
                    person_id
                )

                # ------------------------------------------------
                # DRAW POSE INSIDE PERSON BOX
                # ------------------------------------------------

                if pose_results.pose_landmarks:

                    mp_drawing.draw_landmarks(
                        person_crop,
                        pose_results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(
                            color=(0, 0, 255),
                            thickness=3,
                            circle_radius=4
                        ),
                        mp_drawing.DrawingSpec(
                            color=(255, 0, 0),
                            thickness=3,
                            circle_radius=3
                        )
                    )

                    frame[
                        y1:y2,
                        x1:x2
                    ] = person_crop

            # ------------------------------------------------
            # TOTAL PEOPLE
            # ------------------------------------------------

            cv2.putText(
                frame,
                f"People Detected: {len(persons)}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                3
            )

            # ------------------------------------------------
            # DISPLAY
            # ------------------------------------------------

            cv2.imshow(
                "Smart Health Monitoring - Multi Person Pose",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

    print("\nMulti-person pose estimation stopped.")

    return True


# ============================================================
# DASHBOARD FRAME FUNCTION
# ============================================================

def process_pose_frame(frame, pose=None):

    results = model(
        frame,
        classes=[0],
        conf=CONFIDENCE_THRESHOLD,
        verbose=False
    )

    persons = []

    for result in results:

        for box in result.boxes:

            confidence = float(
                box.conf[0]
            )

            if confidence < CONFIDENCE_THRESHOLD:
                continue

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            persons.append(
                (x1, y1, x2, y2)
            )

    persons.sort(
        key=lambda box: box[0]
    )

    pose_detected = len(persons) > 0

    body_angle = None

    for person_id, (
        x1,
        y1,
        x2,
        y2
    ) in enumerate(persons, start=1):

        crop = frame[
            y1:y2,
            x1:x2
        ]

        if crop.size == 0:
            continue

        rgb_crop = cv2.cvtColor(
            crop,
            cv2.COLOR_BGR2RGB
        )

        with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5
        ) as person_pose:

            results_pose = person_pose.process(
                rgb_crop
            )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            3
        )

        draw_person_label(
            frame,
            x1,
            y1,
            person_id
        )

        if results_pose.pose_landmarks:

            mp_drawing.draw_landmarks(
                crop,
                results_pose.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(
                    color=(0, 0, 255),
                    thickness=3,
                    circle_radius=4
                ),
                mp_drawing.DrawingSpec(
                    color=(255, 0, 0),
                    thickness=3,
                    circle_radius=3
                )
            )

            frame[
                y1:y2,
                x1:x2
            ] = crop

    return (
        frame,
        pose_detected,
        body_angle
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_pose_detection()