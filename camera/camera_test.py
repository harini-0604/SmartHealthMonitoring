import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open the camera.")
    exit()

print("Camera started successfully.")
print("Press Q to close the camera.")

while True:
    ret, frame = camera.read()

    if not ret:
        print("ERROR: Could not read frame.")
        break

    cv2.imshow("Smart Health Monitoring - CCTV", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()