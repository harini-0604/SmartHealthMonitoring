import sys
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

from emergency.emergency_manager import handle_emergency


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
# FALL DETECTION FUNCTION
# ============================================================

def run_fall_detection():

    # --------------------------------------------------------
    # INITIALIZE MEDIAPIPE
    # --------------------------------------------------------

    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )


    # --------------------------------------------------------
    # OPEN CAMERA
    # --------------------------------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print(
            "ERROR: Could not open camera."
        )

        pose.close()

        return False


    # ========================================================
    # STATE VARIABLES
    # ========================================================

    body_y_history = []

    previous_body_y = None
    previous_time = None

    fall_candidate = False
    fall_confirmed = False

    fall_candidate_start = None
    recovery_start = None

    emergency_alert_sent = False


    # ========================================================
    # START
    # ========================================================

    print()
    print("=" * 70)
    print("SMART HEALTH MONITORING SYSTEM")
    print("FALL DETECTION ENGINE - VERSION 2")
    print("=" * 70)
    print("Press Q to close.\n")

    log_event(
        "Fall detection system started"
    )


    # ========================================================
    # MAIN LOOP
    # ========================================================

    while True:

        # ----------------------------------------------------
        # READ CAMERA
        # ----------------------------------------------------

        ret, frame = camera.read()

        if not ret:

            print(
                "ERROR: Could not read camera frame."
            )

            break


        current_time_seconds = time.time()


        # ====================================================
        # YOLO
        # ====================================================

        results = model(
            frame,
            verbose=False
        )


        largest_person = None
        largest_area = 0
        person_count = 0


        for result in results:

            for box in result.boxes:

                class_id = int(
                    box.cls[0]
                )

                confidence = float(
                    box.conf[0]
                )


                if (
                    class_id == 0
                    and confidence >= CONFIDENCE_THRESHOLD
                ):

                    person_count += 1


                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0]
                    )


                    area = (
                        x2 - x1
                    ) * (
                        y2 - y1
                    )


                    if area > largest_area:

                        largest_area = area

                        largest_person = (
                            x1,
                            y1,
                            x2,
                            y2
                        )


        # ====================================================
        # DRAW YOLO
        # ====================================================

        annotated_frame = results[0].plot()


        # ====================================================
        # CURRENT VALUES
        # ====================================================

        current_body_y = None
        current_angle = None
        vertical_speed = 0.0


        # ====================================================
        # PROCESS PERSON
        # ====================================================

        if largest_person is not None:

            x1, y1, x2, y2 = largest_person


            frame_height, frame_width = (
                frame.shape[:2]
            )


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


                    # ----------------------------------------
                    # SHOULDERS
                    # ----------------------------------------

                    left_shoulder = get_landmark(
                        landmarks,
                        "LEFT_SHOULDER"
                    )

                    right_shoulder = get_landmark(
                        landmarks,
                        "RIGHT_SHOULDER"
                    )


                    # ----------------------------------------
                    # HIPS
                    # ----------------------------------------

                    left_hip = get_landmark(
                        landmarks,
                        "LEFT_HIP"
                    )

                    right_hip = get_landmark(
                        landmarks,
                        "RIGHT_HIP"
                    )


                    # ----------------------------------------
                    # SHOULDER CENTER
                    # ----------------------------------------

                    shoulder_x = (
                        left_shoulder[0]
                        + right_shoulder[0]
                    ) / 2


                    shoulder_y = (
                        left_shoulder[1]
                        + right_shoulder[1]
                    ) / 2


                    # ----------------------------------------
                    # HIP CENTER
                    # ----------------------------------------

                    hip_x = (
                        left_hip[0]
                        + right_hip[0]
                    ) / 2


                    hip_y = (
                        left_hip[1]
                        + right_hip[1]
                    ) / 2


                    # ----------------------------------------
                    # BODY CENTER
                    # ----------------------------------------

                    current_body_y = (
                        shoulder_y
                        + hip_y
                    ) / 2


                    # ----------------------------------------
                    # BODY ANGLE
                    # ----------------------------------------

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


                    # ----------------------------------------
                    # VERTICAL SPEED
                    # ----------------------------------------

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


                    # ----------------------------------------
                    # SAVE BODY POSITION
                    # ----------------------------------------

                    body_y_history.append(
                        current_body_y
                    )


                    if (
                        len(body_y_history)
                        > MOVEMENT_WINDOW
                    ):

                        body_y_history.pop(0)


                    # ----------------------------------------
                    # DRAW POSE
                    # ----------------------------------------

                    mp_drawing.draw_landmarks(
                        person_crop,
                        landmarks,
                        mp_pose.POSE_CONNECTIONS
                    )


                    annotated_frame[
                        y1:y2,
                        x1:x2
                    ] = person_crop


        # ====================================================
        # FALL ANALYSIS
        # ====================================================

        if current_body_y is not None:

            # ------------------------------------------------
            # DOWNWARD MOVEMENT
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


            # ------------------------------------------------
            # CONDITIONS
            # ------------------------------------------------

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


            # =================================================
            # POSSIBLE FALL
            # =================================================

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

                    recovery_start = None

                    log_event(
                        "Possible fall detected"
                    )


            # =================================================
            # FALL CONFIRMATION
            # =================================================

            if (
                fall_candidate
                and not fall_confirmed
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

                    recovery_start = None


                    log_event(
                        "Fall candidate confirmed"
                    )


                    # -----------------------------------------
                    # EMERGENCY MANAGER
                    # -----------------------------------------

                    if not emergency_alert_sent:

                        emergency_alert_sent = True


                        log_event(
                            "Sending fall event "
                            "to emergency manager"
                        )


                        emergency_result = (
                            handle_emergency(
                                reason=(
                                    "Fall detected by "
                                    "fall detection system"
                                ),
                                source="FALL DETECTION"
                            )
                        )


                        log_event(
                            "Emergency manager status: "
                            f"{emergency_result['status']}"
                        )


            # =================================================
            # RECOVERY
            # =================================================

            if fall_confirmed:

                if body_is_normal:

                    if recovery_start is None:

                        recovery_start = (
                            time.time()
                        )


                    recovery_elapsed = (
                        time.time()
                        - recovery_start
                    )


                    if (
                        recovery_elapsed
                        >= RECOVERY_CONFIRMATION_TIME
                    ):

                        log_event(
                            "Person recovered - "
                            "returning to normal state"
                        )


                        fall_confirmed = False

                        fall_candidate = False

                        fall_candidate_start = None

                        recovery_start = None

                        body_y_history.clear()


                        # Allow another future fall
                        emergency_alert_sent = False


                else:

                    recovery_start = None


            # ------------------------------------------------
            # UPDATE HISTORY
            # ------------------------------------------------

            previous_body_y = (
                current_body_y
            )

            previous_time = (
                current_time_seconds
            )


        else:

            # ------------------------------------------------
            # NO PERSON
            # ------------------------------------------------

            previous_body_y = None

            previous_time = None

            body_y_history.clear()


        # ====================================================
        # STATUS
        # ====================================================

        if fall_confirmed:

            status = "FALL CONFIRMED"

        elif fall_candidate:

            status = "POSSIBLE FALL"

        elif person_count == 0:

            status = "NO PERSON"

        else:

            status = "NORMAL"


        # ====================================================
        # DISPLAY
        # ====================================================

        if current_angle is not None:

            cv2.putText(
                annotated_frame,
                f"Body angle: {current_angle:.1f}",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )


        if current_body_y is not None:

            cv2.putText(
                annotated_frame,
                f"Body Y: {current_body_y:.3f}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )


        cv2.putText(
            annotated_frame,
            f"Vertical speed: {vertical_speed:.3f}",
            (20, 95),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2
        )


        cv2.putText(
            annotated_frame,
            f"People: {person_count}",
            (20, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2
        )


        cv2.putText(
            annotated_frame,
            f"Status: {status}",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 255),
            2
        )


        current_time_display = (
            datetime.now().strftime(
                "%H:%M:%S"
            )
        )


        cv2.putText(
            annotated_frame,
            f"Time: {current_time_display}",
            (20, 195),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )


        # ====================================================
        # CAMERA WINDOW
        # ====================================================

        cv2.imshow(
            "Smart Health Monitoring - Fall Detection",
            annotated_frame
        )


        # ====================================================
        # QUIT
        # ====================================================

        if (
            cv2.waitKey(1) & 0xFF
            == ord("q")
        ):

            break


    # ========================================================
    # CLEANUP
    # ========================================================

    camera.release()

    cv2.destroyAllWindows()

    pose.close()


    print()
    print("Fall detection system stopped.")


    return True


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    run_fall_detection()