import cv2
import mediapipe as mp
from ultralytics import YOLO
from datetime import datetime
import math


# ============================================================
# INITIALIZATION
# ============================================================

# Load YOLO model
model = YOLO("yolo11n.pt")

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Open webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open the camera.")
    exit()


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_landmark(landmarks, landmark_name):
    """
    Get x, y, z and visibility of a MediaPipe landmark.
    """

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
# START MESSAGE
# ============================================================

print("=" * 65)
print("SMART HEALTH MONITORING SYSTEM")
print("YOLO + MEDIAPIPE POSE")
print("=" * 65)
print("Press Q to close.\n")


previous_person_count = -1


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    # --------------------------------------------------------
    # Read camera frame
    # --------------------------------------------------------

    ret, frame = camera.read()

    if not ret:
        print("ERROR: Could not read camera frame.")
        break


    # --------------------------------------------------------
    # YOLO PERSON DETECTION
    # --------------------------------------------------------

    results = model(
        frame,
        verbose=False
    )


    # Count people
    person_count = 0

    # Store largest person bounding box
    largest_person = None
    largest_area = 0


    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            # YOLO class 0 = person
            if class_id == 0 and confidence >= 0.50:

                person_count += 1

                # Bounding box
                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                width = x2 - x1
                height = y2 - y1

                area = width * height

                # Select largest detected person
                if area > largest_area:

                    largest_area = area

                    largest_person = (
                        x1,
                        y1,
                        x2,
                        y2
                    )


    # --------------------------------------------------------
    # PRINT WHEN PERSON COUNT CHANGES
    # --------------------------------------------------------

    if person_count != previous_person_count:

        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )

        if person_count == 0:

            print(
                f"[{current_time}] "
                f"No person detected - 0"
            )

        elif person_count == 1:

            print(
                f"[{current_time}] "
                f"1 person detected"
            )

        else:

            print(
                f"[{current_time}] "
                f"{person_count} people detected"
            )

        previous_person_count = person_count


    # --------------------------------------------------------
    # DRAW YOLO BOXES
    # --------------------------------------------------------

    annotated_frame = results[0].plot()


    # --------------------------------------------------------
    # MEDIAPIPE POSE
    # --------------------------------------------------------

    if largest_person is not None:

        x1, y1, x2, y2 = largest_person

        # Keep coordinates inside frame
        frame_height, frame_width = frame.shape[:2]

        x1 = max(0, x1)
        y1 = max(0, y1)

        x2 = min(frame_width, x2)
        y2 = min(frame_height, y2)


        # Crop largest person
        person_crop = frame[
            y1:y2,
            x1:x2
        ]


        if person_crop.size > 0:

            # Convert BGR → RGB
            rgb_person = cv2.cvtColor(
                person_crop,
                cv2.COLOR_BGR2RGB
            )


            # Run MediaPipe
            pose_results = pose.process(
                rgb_person
            )


            if pose_results.pose_landmarks:

                landmarks = pose_results.pose_landmarks


                # ------------------------------------------------
                # GET SHOULDERS
                # ------------------------------------------------

                left_shoulder = get_landmark(
                    landmarks,
                    "LEFT_SHOULDER"
                )

                right_shoulder = get_landmark(
                    landmarks,
                    "RIGHT_SHOULDER"
                )


                # ------------------------------------------------
                # GET HIPS
                # ------------------------------------------------

                left_hip = get_landmark(
                    landmarks,
                    "LEFT_HIP"
                )

                right_hip = get_landmark(
                    landmarks,
                    "RIGHT_HIP"
                )


                # ------------------------------------------------
                # CALCULATE SHOULDER CENTER
                # ------------------------------------------------

                shoulder_x = (
                    left_shoulder[0] +
                    right_shoulder[0]
                ) / 2

                shoulder_y = (
                    left_shoulder[1] +
                    right_shoulder[1]
                ) / 2


                # ------------------------------------------------
                # CALCULATE HIP CENTER
                # ------------------------------------------------

                hip_x = (
                    left_hip[0] +
                    right_hip[0]
                ) / 2

                hip_y = (
                    left_hip[1] +
                    right_hip[1]
                ) / 2


                # ------------------------------------------------
                # BODY ANGLE
                # ------------------------------------------------

                dx = hip_x - shoulder_x
                dy = hip_y - shoulder_y

                angle = math.degrees(
                    math.atan2(dy, dx)
                )


                # ------------------------------------------------
                # DRAW POSE ON PERSON CROP
                # ------------------------------------------------

                mp_drawing.draw_landmarks(
                    person_crop,
                    landmarks,
                    mp_pose.POSE_CONNECTIONS
                )


                # Put modified crop back
                annotated_frame[
                    y1:y2,
                    x1:x2
                ] = person_crop


                # ------------------------------------------------
                # DISPLAY BODY ANGLE
                # ------------------------------------------------

                cv2.putText(
                    annotated_frame,
                    f"Body angle: {angle:.1f}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )


    # --------------------------------------------------------
    # DISPLAY PERSON COUNT
    # --------------------------------------------------------

    cv2.putText(
        annotated_frame,
        f"People: {person_count}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


    # --------------------------------------------------------
    # DISPLAY SYSTEM TIME
    # --------------------------------------------------------

    current_time = datetime.now().strftime(
        "%H:%M:%S"
    )

    cv2.putText(
        annotated_frame,
        f"Time: {current_time}",
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )


    # --------------------------------------------------------
    # DISPLAY CAMERA
    # --------------------------------------------------------

    cv2.imshow(
        "Smart Health Monitoring - YOLO + Pose",
        annotated_frame
    )


    # --------------------------------------------------------
    # QUIT
    # --------------------------------------------------------

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

camera.release()
cv2.destroyAllWindows()
pose.close()

print("\nYOLO + MediaPipe system stopped.")