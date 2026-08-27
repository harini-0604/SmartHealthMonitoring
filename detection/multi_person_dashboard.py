import cv2
import mediapipe as mp
from ultralytics import YOLO
import math
import time


# ============================================================
# SETTINGS
# ============================================================

PERSON_CONFIDENCE = 0.50
LANDMARK_VISIBILITY = 0.60

DOWNWARD_DISTANCE_THRESHOLD = 0.15
HORIZONTAL_ANGLE_THRESHOLD = 45

MOVEMENT_WINDOW = 8
FALL_CONFIRMATION_TIME = 2.0


# ============================================================
# INITIALIZATION
# ============================================================

model = YOLO("yolo11n.pt")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


# ============================================================
# CREATE PERSON STATE
# ============================================================

def create_person_state():

    return {
        "body_y_history": [],
        "previous_body_y": None,
        "previous_time": None,
        "fall_candidate": False,
        "fall_confirmed": False,
        "fall_candidate_start": None
    }


# ============================================================
# PROCESS PERSON
# ============================================================

def process_person(
    person_crop,
    state,
    person_pose
):

    current_time = time.time()

    body_y = None
    body_angle = None
    vertical_speed = 0.0
    status = "POSE NOT DETECTED"


    # --------------------------------------------------------
    # RGB
    # --------------------------------------------------------

    rgb_person = cv2.cvtColor(
        person_crop,
        cv2.COLOR_BGR2RGB
    )


    # --------------------------------------------------------
    # MEDIAPIPE
    # --------------------------------------------------------

    pose_results = person_pose.process(
        rgb_person
    )


    if not pose_results.pose_landmarks:

        return (
            person_crop,
            state,
            body_angle,
            vertical_speed,
            status
        )


    landmarks = pose_results.pose_landmarks


    # --------------------------------------------------------
    # DRAW RED DOTS + BLUE LINES
    # --------------------------------------------------------

    mp_drawing.draw_landmarks(

        person_crop,

        landmarks,

        mp_pose.POSE_CONNECTIONS,

        mp_drawing.DrawingSpec(
            color=(0, 0, 255),
            thickness=2,
            circle_radius=3
        ),

        mp_drawing.DrawingSpec(
            color=(255, 0, 0),
            thickness=2,
            circle_radius=2
        )
    )


    # --------------------------------------------------------
    # IMPORTANT LANDMARKS
    # --------------------------------------------------------

    left_shoulder = landmarks.landmark[
        mp_pose.PoseLandmark.LEFT_SHOULDER
    ]

    right_shoulder = landmarks.landmark[
        mp_pose.PoseLandmark.RIGHT_SHOULDER
    ]

    left_hip = landmarks.landmark[
        mp_pose.PoseLandmark.LEFT_HIP
    ]

    right_hip = landmarks.landmark[
        mp_pose.PoseLandmark.RIGHT_HIP
    ]


    # --------------------------------------------------------
    # VISIBILITY
    # --------------------------------------------------------

    if not (

        left_shoulder.visibility
        >= LANDMARK_VISIBILITY

        and

        right_shoulder.visibility
        >= LANDMARK_VISIBILITY

        and

        left_hip.visibility
        >= LANDMARK_VISIBILITY

        and

        right_hip.visibility
        >= LANDMARK_VISIBILITY

    ):

        status = "POSE UNCERTAIN"

        return (
            person_crop,
            state,
            body_angle,
            vertical_speed,
            status
        )


    # --------------------------------------------------------
    # BODY CENTERS
    # --------------------------------------------------------

    shoulder_x = (
        left_shoulder.x
        + right_shoulder.x
    ) / 2

    shoulder_y = (
        left_shoulder.y
        + right_shoulder.y
    ) / 2


    hip_x = (
        left_hip.x
        + right_hip.x
    ) / 2

    hip_y = (
        left_hip.y
        + right_hip.y
    ) / 2


    body_y = (
        shoulder_y
        + hip_y
    ) / 2


    # --------------------------------------------------------
    # BODY ANGLE
    # --------------------------------------------------------

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


    if raw_angle > 90:

        body_angle = 180 - raw_angle

    else:

        body_angle = raw_angle


    # --------------------------------------------------------
    # VERTICAL SPEED
    # --------------------------------------------------------

    if (

        state["previous_body_y"] is not None

        and

        state["previous_time"] is not None

    ):

        delta_y = (
            body_y
            - state["previous_body_y"]
        )

        delta_time = (
            current_time
            - state["previous_time"]
        )


        if delta_time > 0:

            vertical_speed = (
                delta_y
                / delta_time
            )


    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    state["body_y_history"].append(
        body_y
    )


    if len(
        state["body_y_history"]
    ) > MOVEMENT_WINDOW:

        state["body_y_history"].pop(0)


    downward_distance = 0.0


    if len(
        state["body_y_history"]
    ) >= 2:

        downward_distance = (

            state["body_y_history"][-1]

            -

            state["body_y_history"][0]

        )


    # --------------------------------------------------------
    # FALL CONDITIONS
    # --------------------------------------------------------

    significant_downward_motion = (

        downward_distance
        > DOWNWARD_DISTANCE_THRESHOLD

    )


    body_is_horizontal = (

        body_angle
        < HORIZONTAL_ANGLE_THRESHOLD

    )


    body_is_normal = (

        body_angle
        >= HORIZONTAL_ANGLE_THRESHOLD

    )


    # --------------------------------------------------------
    # POSSIBLE FALL
    # --------------------------------------------------------

    if (

        significant_downward_motion

        and

        body_is_horizontal

        and

        not state["fall_confirmed"]

    ):

        if not state["fall_candidate"]:

            state["fall_candidate"] = True

            state["fall_candidate_start"] = (
                current_time
            )


    # --------------------------------------------------------
    # CONFIRM FALL
    # --------------------------------------------------------

    if (

        state["fall_candidate"]

        and

        not state["fall_confirmed"]

        and

        state["fall_candidate_start"] is not None

    ):

        elapsed = (

            current_time

            -

            state["fall_candidate_start"]

        )


        if elapsed >= FALL_CONFIRMATION_TIME:

            state["fall_confirmed"] = True

            state["fall_candidate"] = False

            state["fall_candidate_start"] = None


    # --------------------------------------------------------
    # RECOVERY
    # --------------------------------------------------------

    if state["fall_confirmed"]:

        if body_is_normal:

            state["fall_confirmed"] = False

            state["fall_candidate"] = False

            state["fall_candidate_start"] = None

            state["body_y_history"].clear()


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if state["fall_confirmed"]:

        status = "FALL CONFIRMED"

    elif state["fall_candidate"]:

        status = "POSSIBLE FALL"

    else:

        status = "NORMAL"


    # --------------------------------------------------------
    # SAVE STATE
    # --------------------------------------------------------

    state["previous_body_y"] = body_y
    state["previous_time"] = current_time


    return (
        person_crop,
        state,
        body_angle,
        vertical_speed,
        status
    )


# ============================================================
# PROCESS ONE CAMERA FRAME
# ============================================================

def process_multi_person_frame(
    frame,
    person_states
):

    annotated_frame = frame.copy()

    results = model.track(

        frame,

        persist=True,

        classes=[0],

        conf=PERSON_CONFIDENCE,

        verbose=False

    )


    current_ids = set()

    people = []


    # --------------------------------------------------------
    # PROCESS TRACKED PEOPLE
    # --------------------------------------------------------

    for result in results:

        if result.boxes is None:

            continue


        for box in result.boxes:

            if box.id is None:

                continue


            track_id = int(
                box.id[0]
            )


            confidence = float(
                box.conf[0]
            )


            if confidence < PERSON_CONFIDENCE:

                continue


            current_ids.add(
                track_id
            )


            if track_id not in person_states:

                person_states[track_id] = (
                    create_person_state()
                )


            state = person_states[
                track_id
            ]


            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )


            frame_height, frame_width = (
                frame.shape[:2]
            )


            x1 = max(
                0,
                x1
            )

            y1 = max(
                0,
                y1
            )

            x2 = min(
                frame_width,
                x2
            )

            y2 = min(
                frame_height,
                y2
            )


            if x2 <= x1 or y2 <= y1:

                continue


            person_crop = frame[
                y1:y2,
                x1:x2
            ].copy()


            if person_crop.size == 0:

                continue


            person_pose = mp_pose.Pose(

                static_image_mode=True,

                model_complexity=1,

                enable_segmentation=False,

                min_detection_confidence=0.5,

                min_tracking_confidence=0.5

            )


            (
                person_crop,
                state,
                body_angle,
                vertical_speed,
                status
            ) = process_person(

                person_crop,

                state,

                person_pose

            )


            person_pose.close()


            annotated_frame[
                y1:y2,
                x1:x2
            ] = person_crop


            # ------------------------------------------------
            # BOUNDING BOX
            # ------------------------------------------------

            cv2.rectangle(

                annotated_frame,

                (x1, y1),

                (x2, y2),

                (0, 255, 0),

                2

            )


            # ------------------------------------------------
            # PERSON ID
            # ------------------------------------------------

            cv2.putText(

                annotated_frame,

                f"Person ID: {track_id}",

                (
                    x1,
                    max(
                        25,
                        y1 - 30
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.60,

                (0, 255, 0),

                2

            )


            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            cv2.putText(

                annotated_frame,

                status,

                (
                    x1,
                    max(
                        50,
                        y1 - 8
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.55,

                (0, 255, 255),

                2

            )


            # ------------------------------------------------
            # ANGLE
            # ------------------------------------------------

            if body_angle is not None:

                cv2.putText(

                    annotated_frame,

                    f"Angle: {body_angle:.1f}",

                    (
                        x1,
                        min(
                            frame_height - 10,
                            y2 + 20
                        )
                    ),

                    cv2.FONT_HERSHEY_SIMPLEX,

                    0.50,

                    (255, 255, 255),

                    1

                )


            people.append({

                "id": track_id,

                "status": status,

                "body_angle": body_angle,

                "vertical_speed": vertical_speed,

                "fall_confirmed":
                    state["fall_confirmed"]

            })


    # --------------------------------------------------------
    # REMOVE OLD STATES
    # --------------------------------------------------------

    old_ids = [

        track_id

        for track_id in person_states

        if track_id not in current_ids

    ]


    for track_id in old_ids:

        del person_states[
            track_id
        ]


    # --------------------------------------------------------
    # PEOPLE COUNT
    # --------------------------------------------------------

    cv2.putText(

        annotated_frame,

        f"People Detected: {len(current_ids)}",

        (20, 35),

        cv2.FONT_HERSHEY_SIMPLEX,

        0.75,

        (0, 255, 255),

        2

    )


    return (
        annotated_frame,
        people,
        person_states
    )