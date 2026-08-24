import sys
import threading
from pathlib import Path
import cv2
import mediapipe as mp
from ultralytics import YOLO
from datetime import datetime
import math
import time


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# EMERGENCY MANAGER
# ============================================================


from emergency.verification import EmergencyVerification

# ============================================================
# EMERGENCY VERIFICATION WORKER
# ============================================================

def run_emergency_verification(
    verification,
    reason,
    source="FALL DETECTION"
):

    try:

        verification.start(
            reason=reason,
            source=source
        )

        result = verification.run_voice_verification()

        print(
            f"Verification result: {result}"
        )

    except Exception as error:

        print(
            f"Emergency verification error: {error}"
        )

# ============================================================
# INITIALIZATION
# ============================================================

model = YOLO("yolo11n.pt")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# ============================================================
# PARAMETERS
# ============================================================

CONFIDENCE_THRESHOLD = 0.50

DOWNWARD_DISTANCE_THRESHOLD = 0.15

HORIZONTAL_ANGLE_THRESHOLD = 45

MOVEMENT_WINDOW = 8

FALL_CONFIRMATION_TIME = 2.0

RECOVERY_CONFIRMATION_TIME = 1.0


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_landmark(landmarks, landmark_name):

    landmark_id = getattr(
        mp_pose.PoseLandmark,
        landmark_name
    )

    point = landmarks.landmark[landmark_id]

    return (
        point.x,
        point.y,
        point.z,
        point.visibility
    )


# ============================================================
# EVENT LOGGER
# ============================================================

def log_event(message):

    current_time = datetime.now().strftime(
        "%H:%M:%S"
    )

    print(
        f"[{current_time}] {message}"
    )

# ============================================================
# FALL FRAME PROCESSOR
# ============================================================


def process_fall_frame(
    frame,
    model,
    pose,
    body_y_history,
    previous_body_y,
    previous_time,
    fall_candidate,
    fall_confirmed,
    fall_candidate_start,
    emergency_alert_sent
):

    current_time_seconds = time.time()

    # --------------------------------------------------------
    # YOLO PERSON DETECTION
    # --------------------------------------------------------

    results = model(
        frame,
        classes=[0],
        verbose=False
    )

    annotated_frame = frame.copy()

    largest_person = None
    largest_area = 0
    person_count = 0

    # --------------------------------------------------------
    # DETECT ONLY PERSON CLASS
    # YOLO CLASS 0 = PERSON
    # --------------------------------------------------------

    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if (
                class_id == 0
                and confidence >= CONFIDENCE_THRESHOLD
            ):

                person_count += 1

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                # Draw ONLY human bounding boxes
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    annotated_frame,
                    f"Person {confidence:.2f}",
                    (
                        x1,
                        max(20, y1 - 10)
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

                area = (
                    x2 - x1
                ) * (
                    y2 - y1
                )

                # Select largest person for pose analysis
                if area > largest_area:

                    largest_area = area

                    largest_person = (
                        x1,
                        y1,
                        x2,
                        y2
                    )

    # --------------------------------------------------------
    # DEFAULT VALUES
    # --------------------------------------------------------

    current_body_y = None
    current_angle = None
    vertical_speed = 0.0

    status = "NO PERSON"

    # --------------------------------------------------------
    # PROCESS LARGEST PERSON
    # --------------------------------------------------------

    if largest_person is not None:

        x1, y1, x2, y2 = largest_person

        frame_height, frame_width = frame.shape[:2]

        x1 = max(0, x1)
        y1 = max(0, y1)

        x2 = min(frame_width, x2)
        y2 = min(frame_height, y2)

        person_crop = frame[
            y1:y2,
            x1:x2
        ]

        if person_crop.size > 0:

            rgb_person = cv2.cvtColor(
                person_crop,
                cv2.COLOR_BGR2RGB
            )

            pose_results = pose.process(
                rgb_person
            )

            if pose_results.pose_landmarks:

                landmarks = (
                    pose_results.pose_landmarks
                )

                # ------------------------------------------------
                # GET LANDMARKS
                # ------------------------------------------------

                left_shoulder = get_landmark(
                    landmarks,
                    "LEFT_SHOULDER"
                )

                right_shoulder = get_landmark(
                    landmarks,
                    "RIGHT_SHOULDER"
                )

                left_hip = get_landmark(
                    landmarks,
                    "LEFT_HIP"
                )

                right_hip = get_landmark(
                    landmarks,
                    "RIGHT_HIP"
                )

                # ------------------------------------------------
                # SHOULDER CENTER
                # ------------------------------------------------

                shoulder_x = (
                    left_shoulder[0]
                    + right_shoulder[0]
                ) / 2

                shoulder_y = (
                    left_shoulder[1]
                    + right_shoulder[1]
                ) / 2

                # ------------------------------------------------
                # HIP CENTER
                # ------------------------------------------------

                hip_x = (
                    left_hip[0]
                    + right_hip[0]
                ) / 2

                hip_y = (
                    left_hip[1]
                    + right_hip[1]
                ) / 2

                # ------------------------------------------------
                # BODY CENTER
                # ------------------------------------------------

                print(
                    f"DEBUG LANDMARKS | LSY={left_shoulder[1]:.3f} "
                    f"RSY={right_shoulder[1]:.3f} "
                    f"LHY={left_hip[1]:.3f} "
                    f"RHY={right_hip[1]:.3f}"
                )

                current_body_y = (
                    shoulder_y
                    + hip_y
                ) / 2

                # ------------------------------------------------
                # BODY ANGLE
                # ------------------------------------------------

                dx = hip_x - shoulder_x
                dy = hip_y - shoulder_y

                raw_angle = abs(
                    math.degrees(
                        math.atan2(
                            dy,
                            dx
                        )
                    )
                )

                # Normalize the angle so both horizontal directions
                # are treated as approximately 0 degrees.
                if raw_angle > 90:
                    current_angle = 180 - raw_angle
                else:
                    current_angle = raw_angle

                # ------------------------------------------------
                # ------------------------------------------------

                left_shoulder = get_landmark(
                    landmarks,
                    "LEFT_SHOULDER"
                )

                right_shoulder = get_landmark(
                    landmarks,
                    "RIGHT_SHOULDER"
                )

                left_hip = get_landmark(
                    landmarks,
                    "LEFT_HIP"
                )

                right_hip = get_landmark(
                    landmarks,
                    "RIGHT_HIP"
                )

                # ------------------------------------------------
                # SHOULDER CENTER
                # ------------------------------------------------

                shoulder_x = (
                    left_shoulder[0]
                    + right_shoulder[0]
                ) / 2

                shoulder_y = (
                    left_shoulder[1]
                    + right_shoulder[1]
                ) / 2

                # ------------------------------------------------
                # HIP CENTER
                # ------------------------------------------------

                hip_x = (
                    left_hip[0]
                    + right_hip[0]
                ) / 2

                hip_y = (
                    left_hip[1]
                    + right_hip[1]
                ) / 2

                # ------------------------------------------------
                # BODY CENTER
                # ------------------------------------------------

                print(
                    f"DEBUG LANDMARKS | LSY={left_shoulder[1]:.3f} "
                    f"RSY={right_shoulder[1]:.3f} "
                    f"LHY={left_hip[1]:.3f} "
                    f"RHY={right_hip[1]:.3f}"
                )

                current_body_y = (
                    shoulder_y
                    + hip_y
                ) / 2

                # ------------------------------------------------
                # BODY ANGLE
                # ------------------------------------------------

                dx = hip_x - shoulder_x
                dy = hip_y - shoulder_y

                current_angle = abs(
                    math.degrees(
                        math.atan2(
                            dy,
                            dx
                        )
                    )
                )

                # ------------------------------------------------
                # VERTICAL SPEED
                # ------------------------------------------------

                if (
                    previous_body_y is not None
                    and previous_time is not None
                ):

                    delta_y = (
                        current_body_y
                        - previous_body_y
                    )

                    delta_time = (
                        current_time_seconds
                        - previous_time
                    )

                    if delta_time > 0:

                        vertical_speed = (
                            delta_y
                            / delta_time
                        )

                # ------------------------------------------------
                # SAVE BODY POSITION
                # ------------------------------------------------

                body_y_history.append(
                    current_body_y
                )

                if (
                    len(body_y_history)
                    > MOVEMENT_WINDOW
                ):

                    body_y_history.pop(0)

                # ------------------------------------------------
                # DRAW POSE
                # ------------------------------------------------

                mp_drawing.draw_landmarks(
                    person_crop,
                    landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

                annotated_frame[
                    y1:y2,
                    x1:x2
                ] = person_crop

                # ------------------------------------------------
                # FALL ANALYSIS
                # ------------------------------------------------

                downward_distance = 0

                if len(body_y_history) >= 2:

                    oldest_y = (
                        body_y_history[0]
                    )

                    newest_y = (
                        body_y_history[-1]
                    )

                    downward_distance = (
                        newest_y
                        - oldest_y
                    )

                significant_downward_motion = (
                    downward_distance
                    > DOWNWARD_DISTANCE_THRESHOLD
                )


                body_is_horizontal = (
                    current_angle
                    < HORIZONTAL_ANGLE_THRESHOLD
                )

                body_is_normal = (
                    current_angle
                    >= HORIZONTAL_ANGLE_THRESHOLD
                )

                # ------------------------------------------------
                # POSSIBLE FALL
                # ------------------------------------------------

                if (
                    significant_downward_motion
                    and body_is_horizontal
                    and not fall_confirmed
                ):

                    if not fall_candidate:

                        fall_candidate = True

                        fall_candidate_start = (
                            time.time()
                        )

                        log_event(
                            "Possible fall detected"
                        )


                        # ------------------------------------------------
                        # EMERGENCY VERIFICATION
                        # ------------------------------------------------

                        if not emergency_alert_sent:

                            emergency_alert_sent = True

                            verification = EmergencyVerification(
                                duration=60
                            )

                            verification_thread = threading.Thread(
                                target=run_emergency_verification,
                                args=(
                                    verification,
                                    "Fall detected by fall detection system"
                                ),
                                daemon=True
                            )

                            verification_thread.start()
                # ------------------------------------------------
                # FALL CONFIRMATION
                # ------------------------------------------------

                if (
                    fall_candidate
                    and not fall_confirmed
                    and fall_candidate_start is not None
                ):

                    elapsed = (
                        time.time()
                        - fall_candidate_start
                    )

                    if (
                        elapsed
                        >= FALL_CONFIRMATION_TIME
                    ):

                        fall_confirmed = True

                        fall_candidate = False

                        fall_candidate_start = None

                        log_event(
                            "Fall candidate confirmed"
                        )


                        # ------------------------------------------------
                        # EMERGENCY VERIFICATION
                        # ------------------------------------------------

                        if not emergency_alert_sent:

                            emergency_alert_sent = True

                            verification = EmergencyVerification(
                                duration=60
                            )

                            verification_thread = threading.Thread(
                                target=run_emergency_verification,
                                args=(
                                    verification,
                                    "Fall detected by fall detection system"
                                ),
                                daemon=True
                            )

                            verification_thread.start()
                # ------------------------------------------------
                # RECOVERY
                # ------------------------------------------------

                if fall_confirmed:

                    if body_is_normal:

                        fall_confirmed = False

                        fall_candidate = False

                        fall_candidate_start = None
                        emergency_alert_sent = False

                        body_y_history.clear()

                        log_event(
                            "Person recovered - "
                            "returning to normal state"
                        )

                # ------------------------------------------------
                # STATUS
                # ------------------------------------------------

                if fall_confirmed:

                    status = "FALL CONFIRMED"

                elif fall_candidate:

                    status = "POSSIBLE FALL"

                else:

                    status = "NORMAL"

            else:

                status = "PERSON DETECTED"

        else:

            status = "PERSON DETECTED"

    # --------------------------------------------------------
    # NO PERSON
    # --------------------------------------------------------

    else:

        previous_body_y = None
        previous_time = None

        body_y_history.clear()

        fall_candidate = False
        fall_candidate_start = None

    # --------------------------------------------------------
    # UPDATE PREVIOUS VALUES
    # --------------------------------------------------------

    if current_body_y is not None:

        previous_body_y = current_body_y

        previous_time = current_time_seconds

    # --------------------------------------------------------
    # RETURN VALUES TO DASHBOARD
    # --------------------------------------------------------

    return (
        annotated_frame,
        person_count,
        current_angle,
        current_body_y,
        vertical_speed,
        status,
        body_y_history,
        previous_body_y,
        previous_time,
        fall_candidate,
        fall_confirmed,
        fall_candidate_start,
        emergency_alert_sent
    )


# ============================================================
# STANDALONE FALL DETECTION RUNNER
# ============================================================

def run_fall_detection():

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

    body_y_history = []

    previous_body_y = None
    previous_time = None

    fall_candidate = False
    fall_confirmed = False
    fall_candidate_start = None
    emergency_alert_sent = False

    print()
    print("=" * 70)
    print("SMART HEALTH MONITORING SYSTEM")
    print("FALL DETECTION ENGINE")
    print("=" * 70)
    print("Press Q to close.")
    print()

    log_event("Fall detection system started")

    try:

        while True:

            ret, frame = camera.read()

            if not ret:

                print("ERROR: Could not read camera frame.")

                break

            (
                annotated_frame,
                person_count,
                body_angle,
                body_y,
                vertical_speed,
                status,
                body_y_history,
                previous_body_y,
                previous_time,
                fall_candidate,
                fall_confirmed,
                fall_candidate_start,
                emergency_alert_sent
            ) = process_fall_frame(

                frame,
                model,
                pose,
                body_y_history,
                previous_body_y,
                previous_time,
                fall_candidate,
                fall_confirmed,
                fall_candidate_start,
                emergency_alert_sent
            )

            cv2.putText(
                annotated_frame,
                f"People: {person_count}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

            cv2.putText(
                annotated_frame,
                f"Status: {status}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

            cv2.imshow(
                "Smart Health Monitoring - Fall Detection",
                annotated_frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

        pose.close()

        log_event("Fall detection system stopped")

    return True


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_fall_detection()

