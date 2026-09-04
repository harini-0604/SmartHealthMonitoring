import cv2

from detection.multi_person_dashboard import (
    process_multi_person_frame
)


camera = cv2.VideoCapture(0)

person_states = {}


if not camera.isOpened():

    print("ERROR: Could not open camera.")
    exit()


print("=" * 60)
print("MULTI-PERSON DASHBOARD INTEGRATION TEST")
print("=" * 60)
print("Press Q to close.")


while True:

    ret, frame = camera.read()

    if not ret:

        print("ERROR: Could not read camera frame.")
        break


    (
        annotated_frame,
        people,
        person_states
    ) = process_multi_person_frame(

        frame,

        person_states

    )


    for person in people:

        print(
            f"Person ID: {person['id']} | "
            f"Status: {person['status']} | "
            f"Angle: {person['body_angle']}"
        )


    cv2.imshow(
        "Multi-Person Dashboard Integration Test",
        annotated_frame
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


camera.release()
cv2.destroyAllWindows()

print("Test completed.")