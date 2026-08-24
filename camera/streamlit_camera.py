import cv2
import streamlit as st


st.set_page_config(
    page_title="Live Camera Test",
    layout="wide"
)

st.title("Smart Health Monitoring - Live Camera")

start_camera = st.checkbox("Start Camera")

frame_placeholder = st.empty()

camera = None

if start_camera:

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():

        st.error("Could not open the camera.")

    else:

        st.success("Camera started successfully.")

        while start_camera:

            ret, frame = camera.read()

            if not ret:

                st.error("Could not read camera frame.")
                break

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            frame_placeholder.image(
                frame,
                channels="RGB",
                use_container_width=True
            )

        camera.release()