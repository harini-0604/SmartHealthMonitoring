import cv2
import mediapipe as mp
import math
from ultralytics import YOLO


# ============================================================
# MULTI-PERSON ACTIVITY DETECTION
# ============================================================

CONFIDENCE_THRESHOLD = 0.50

model = YOLO("yolo11n.pt")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# ============================================================
# ANGLE CALCULATION
# ============================================================

def calculate_angle(a, b, c):

    ba = (
        a.x - b.x,
        a.y - b.y
    )

    bc = (
        c.x - b.x,
        c.y - b.y
    )

    dot_product = (
        ba[0] * bc[0]
        + ba[1] * bc[1]
    )

    magnitude_ba = math.sqrt(
        ba[0] ** 2
        + ba[1] ** 2
    )

    magnitude_bc = math.sqrt(
        bc[0] ** 2
        + bc[1] ** 2
    )

    if (
        magnitude_ba == 0
        or magnitude_bc == 0
    ):
        return 0

    cosine_angle = (
        dot_product
        / (
            magnitude_ba
            * magnitude_bc
        )
    )

    cosine_angle = max(
        -1,
        min(1, cosine_angle)
    )

    return math.degrees(
        math.acos(cosine_angle)
    )


# ============================================================
# DRAW ACTIVITY LABEL
# ============================================================

def draw_activity_label(
    frame,
    x1,
    y1,
    activity,
    person_id
):

    label = (
        f"Person {person_id}: "
        f"{activity}"
    )

    text_size = cv2.getTextSize(
        label,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        2
    )[0]

    text_width = text_size[0]
    text_height = text_size[1]

    label_y = max(
        5,
        y1 - 38
    )

    cv2.rectangle(
        frame,
        (
            x1,
            label_y
        ),
        (
            x1 + text_width + 12,
            label_y + text_height + 12
        ),
        (255, 0, 0),
        -1
    )

    cv2.putText(
        frame,
        label,
        (
            x1 + 6,
            label_y + text_height + 5
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


# ============================================================
# ACTIVITY CLASSIFICATION
# ============================================================

def classify_activity(landmarks):

    left_shoulder = landmarks[
        mp_pose.PoseLandmark.LEFT_SHOULDER
    ]

    right_shoulder = landmarks[
        mp_pose.PoseLandmark.RIGHT_SHOULDER
    ]

    left_hip = landmarks[
        mp_pose.PoseLandmark.LEFT_HIP
    ]

    right_hip = landmarks[
        mp_pose.PoseLandmark.RIGHT_HIP
    ]

    left_knee = landmarks[
        mp_pose.PoseLandmark.LEFT_KNEE
    ]

    right_knee = landmarks[
        mp_pose.PoseLandmark.RIGHT_KNEE
    ]

    left_ankle = landmarks[
        mp_pose.PoseLandmark.LEFT_ANKLE
    ]

    right_ankle = landmarks[
        mp_pose.PoseLandmark.RIGHT_ANKLE
    ]

    # --------------------------------------------------------
    # KNEE ANGLES
    # --------------------------------------------------------

    left_angle = calculate_angle(
        left_hip,
        left_knee,
        left_ankle
    )

    right_angle = calculate_angle(
        right_hip,
        right_knee,
        right_ankle
    )

    average_knee_angle = (
        left_angle
        + right_angle
    ) / 2

    # --------------------------------------------------------
    # BODY GEOMETRY
    # --------------------------------------------------------

    shoulder_y = (
        left_shoulder.y
        + right_shoulder.y
    ) / 2

    hip_y = (
        left_hip.y
        + right_hip.y
    ) / 2

    knee_y = (
        left_knee.y
        + right_knee.y
    ) / 2

    torso_length = abs(
        hip_y - shoulder_y
    )

    leg_position = (
        knee_y - hip_y
    )

    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    if average_knee_angle < 125:

        return "Sitting"

    elif (
        average_knee_angle >= 150
        and leg_position > 0.15
        and torso_length > 0.15
    ):

        return "Standing"

    else:

        return "Moving"


# ============================================================
# MAIN ACTIVITY DETECTION
# ============================================================

def run_activity_detection():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print(
            "ERROR: Could not open camera."
        )

        return

    print("=" * 70)
    print("SMART HEALTH MONITORING SYSTEM")
    print("MULTI-PERSON ACTIVITY DETECTION")
    print("=" * 70)
    print("Press Q to close.\n")

    try:

        while True:

            success, frame = camera.read()

            if not success:

                print(
                    "ERROR: Could not read camera frame."
                )

                break

            frame_height, frame_width = (
                frame.shape[:2]
            )

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
            # LEFT → RIGHT PERSON ORDER
            # ------------------------------------------------

            persons.sort(
                key=lambda box: box[0]
            )

            # ------------------------------------------------
            # PROCESS EACH PERSON
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

                # ------------------------------------------------
                # INDIVIDUAL POSE ESTIMATOR
                # ------------------------------------------------

                with mp_pose.Pose(
                    static_image_mode=True,
                    model_complexity=1,
                    enable_segmentation=False,
                    min_detection_confidence=0.5
                ) as pose:

                    pose_results = pose.process(
                        rgb_crop
                    )

                activity = "Unknown"

                if pose_results.pose_landmarks:

                    landmarks = (
                        pose_results.pose_landmarks
                        .landmark
                    )

                    activity = classify_activity(
                        landmarks
                    )

                    # ------------------------------------------------
                    # DRAW SKELETON
                    # ------------------------------------------------

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

                # ------------------------------------------------
                # BLUE PERSON BOX
                # ------------------------------------------------

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 0, 0),
                    3
                )

                # ------------------------------------------------
                # ACTIVITY LABEL
                # ------------------------------------------------

                draw_activity_label(
                    frame,
                    x1,
                    y1,
                    activity,
                    person_id
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
                "Smart Health Monitoring - Multi Person Activity",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

    print("\nMulti-person activity detection stopped.")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_activity_detection()