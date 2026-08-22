import cv2
import mediapipe as mp


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


def run_activity_detection():

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("ERROR: Could not open camera.")
        return

    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        while True:

            success, frame = camera.read()

            if not success:
                print("ERROR: Could not read camera frame.")
                break

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            results = pose.process(rgb_frame)

            activity = "No Person Detected"

            if results.pose_landmarks:

                landmarks = results.pose_landmarks.landmark

                left_hip = landmarks[
                    mp_pose.PoseLandmark.LEFT_HIP
                ]

                left_knee = landmarks[
                    mp_pose.PoseLandmark.LEFT_KNEE
                ]

                right_hip = landmarks[
                    mp_pose.PoseLandmark.RIGHT_HIP
                ]

                right_knee = landmarks[
                    mp_pose.PoseLandmark.RIGHT_KNEE
                ]

                hip_y = (
                    left_hip.y +
                    right_hip.y
                ) / 2

                knee_y = (
                    left_knee.y +
                    right_knee.y
                ) / 2

                if knee_y - hip_y < 0.20:
                    activity = "Sitting"

                else:
                    activity = "Standing / Moving"

                mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS
                )

            cv2.putText(
                frame,
                f"Activity: {activity}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            cv2.imshow(
                "Activity Detection",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_activity_detection()