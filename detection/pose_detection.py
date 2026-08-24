import cv2
import mediapipe as mp
from datetime import datetime
import math


# ============================================================
# POSE ESTIMATION
# ============================================================

def run_pose_detection():

    # --------------------------------------------------------
    # Initialize MediaPipe Pose
    # --------------------------------------------------------

    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )


    # --------------------------------------------------------
    # Open webcam
    # --------------------------------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        print(
            "ERROR: Could not open the camera."
        )

        pose.close()

        return False


    # --------------------------------------------------------
    # START MESSAGE
    # --------------------------------------------------------

    print("=" * 60)
    print("SMART HEALTH MONITORING SYSTEM")
    print("POSE ESTIMATION STARTED")
    print("=" * 60)
    print("Press Q to close.\n")


    # ========================================================
    # HELPER FUNCTION
    # ========================================================

    def get_landmark(
        landmarks,
        landmark_name
    ):
        """
        Return x, y, z and visibility
        for a MediaPipe landmark.
        """

        landmark_id = getattr(
            mp_pose.PoseLandmark,
            landmark_name
        )

        point = landmarks.landmark[
            landmark_id
        ]

        return (
            point.x,
            point.y,
            point.z,
            point.visibility
        )


    # ========================================================
    # MAIN LOOP
    # ========================================================

    while True:

        # ----------------------------------------------------
        # Read camera frame
        # ----------------------------------------------------

        ret, frame = camera.read()

        if not ret:

            print(
                "ERROR: Could not read camera frame."
            )

            break


        # ----------------------------------------------------
        # Convert BGR → RGB
        # ----------------------------------------------------

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # ----------------------------------------------------
        # Process frame with MediaPipe
        # ----------------------------------------------------

        results = pose.process(
            rgb_frame
        )


        # ====================================================
        # POSE DETECTED
        # ====================================================

        if results.pose_landmarks:

            landmarks = results.pose_landmarks


            # ------------------------------------------------
            # Important body landmarks
            # ------------------------------------------------

            nose = get_landmark(
                landmarks,
                "NOSE"
            )

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

            left_knee = get_landmark(
                landmarks,
                "LEFT_KNEE"
            )

            right_knee = get_landmark(
                landmarks,
                "RIGHT_KNEE"
            )

            left_ankle = get_landmark(
                landmarks,
                "LEFT_ANKLE"
            )

            right_ankle = get_landmark(
                landmarks,
                "RIGHT_ANKLE"
            )


            # ------------------------------------------------
            # Calculate shoulder center
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
            # Calculate hip center
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
            # Calculate body angle
            # ------------------------------------------------

            dx = hip_x - shoulder_x
            dy = hip_y - shoulder_y

            angle = math.degrees(
                math.atan2(dy, dx)
            )


            # ------------------------------------------------
            # Draw skeleton
            # ------------------------------------------------

            mp_drawing.draw_landmarks(
                frame,
                landmarks,
                mp_pose.POSE_CONNECTIONS
            )


        # ----------------------------------------------------
        # Display camera
        # ----------------------------------------------------

        cv2.imshow(
            "Smart Health Monitoring - Pose Estimation",
            frame
        )


        # ----------------------------------------------------
        # Press Q to close
        # ----------------------------------------------------

        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


    # ========================================================
    # CLEANUP
    # ========================================================

    camera.release()

    cv2.destroyAllWindows()

    pose.close()


    print()
    print("Pose estimation stopped.")


    return True


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    run_pose_detection()

# ============================================================
# REAL-TIME FRAME POSE DETECTION
# ============================================================

def process_pose_frame(
    frame,
    pose
):

    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = pose.process(
        rgb_frame
    )

    pose_detected = False
    body_angle = None

    if results.pose_landmarks:

        pose_detected = True

        landmarks = results.pose_landmarks

        def get_landmark(
            landmark_name
        ):

            landmark_id = getattr(
                mp_pose.PoseLandmark,
                landmark_name
            )

            point = landmarks.landmark[
                landmark_id
            ]

            return (
                point.x,
                point.y,
                point.z,
                point.visibility
            )

        left_shoulder = get_landmark(
            "LEFT_SHOULDER"
        )

        right_shoulder = get_landmark(
            "RIGHT_SHOULDER"
        )

        left_hip = get_landmark(
            "LEFT_HIP"
        )

        right_hip = get_landmark(
            "RIGHT_HIP"
        )

        shoulder_x = (
            left_shoulder[0]
            + right_shoulder[0]
        ) / 2

        shoulder_y = (
            left_shoulder[1]
            + right_shoulder[1]
        ) / 2

        hip_x = (
            left_hip[0]
            + right_hip[0]
        ) / 2

        hip_y = (
            left_hip[1]
            + right_hip[1]
        ) / 2

        dx = hip_x - shoulder_x
        dy = hip_y - shoulder_y

        body_angle = math.degrees(
            math.atan2(dy, dx)
        )

        mp_drawing.draw_landmarks(
            frame,
            landmarks,
            mp_pose.POSE_CONNECTIONS
        )

    

    return (
        frame,
        pose_detected,
        body_angle
    )
