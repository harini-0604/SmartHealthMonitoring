import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from database.database import get_incidents
from detection.person_detection import run_person_detection
from detection.pose_detection import run_pose_detection
from detection.fall_detection import run_fall_detection
from detection.activity_detection import run_activity_detection


LOG_FILE = PROJECT_ROOT / "logs" / "emergency_log.txt"


st.set_page_config(
    page_title="Smart Health Monitoring",
    page_icon="H",
    layout="wide"
)


st.title("Smart Health Monitoring System")
st.subheader("AI-Based Health Monitoring and Emergency Response")

if st.button("Refresh Dashboard"):
    st.rerun()

st.divider()


# ============================================================
# MONITORING STATUS
# ============================================================

st.header("Monitoring Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Monitoring", "ACTIVE")

with col2:
    st.metric("Person Detection", "READY")

with col3:
    st.metric("Emergency System", "READY")


st.divider()


# ============================================================
# CAMERA MONITORING
# ============================================================

st.header("Camera Monitoring")

camera_col1, camera_col2, camera_col3, camera_col4 = st.columns(4)

with camera_col1:

    if st.button("Run Person Detection"):

        st.info("Starting person detection...")

        try:
            run_person_detection()
            st.success("Person detection completed.")

        except Exception as error:
            st.error(f"Person detection error: {error}")


with camera_col2:

    if st.button("Run Pose Detection"):

        st.info("Starting pose detection...")

        try:
            run_pose_detection()
            st.success("Pose detection completed.")

        except Exception as error:
            st.error(f"Pose detection error: {error}")


with camera_col3:

    if st.button("Run Fall Detection"):

        st.warning("Starting fall detection...")

        try:
            run_fall_detection()
            st.success("Fall detection completed.")

        except Exception as error:
            st.error(f"Fall detection error: {error}")

with camera_col4:

    if st.button("Run Activity Detection"):

        st.info("Starting activity detection...")

        try:
            run_activity_detection()

            st.success(
                "Activity detection completed."
            )

        except Exception as error:

            st.error(
                f"Activity detection error: {error}"
            )


st.divider()


# ============================================================
# DETECTION MODULES
# ============================================================

st.header("Detection Modules")

detection_col1, detection_col2 = st.columns(2)

with detection_col1:

    st.write("Person Detection")
    st.success("Module Available")

    st.write("Pose Detection")
    st.success("Module Available")


with detection_col2:

    st.write("Fall Detection")
    st.success("Module Available")

    st.write("Activity Detection")
    st.success("Module Available")


st.divider()


# ============================================================
# HEALTH SENSORS
# ============================================================

st.header("Health Sensors")

sensor_col1, sensor_col2, sensor_col3 = st.columns(3)

with sensor_col1:
    st.metric("Heart Rate", "No Data")

with sensor_col2:
    st.metric("SpO2", "No Data")

with sensor_col3:
    st.metric("Temperature", "No Data")


st.info(
    "Physical sensors are not connected. "
    "Sensor interfaces are ready for future ESP32 integration."
)


st.divider()


# ============================================================
# EMERGENCY ALERTS
# ============================================================

st.header("Emergency Alerts")

if LOG_FILE.exists():

    with open(
        LOG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        emergency_logs = file.readlines()

    if emergency_logs:

        for log in reversed(emergency_logs[-10:]):

            st.warning(log.strip())

    else:

        st.info("No emergency alerts recorded.")

else:

    st.info("Emergency log file does not exist yet.")


st.divider()


# ============================================================
# INCIDENT HISTORY
# ============================================================

st.header("Incident History")

incidents = get_incidents()

if incidents:

    for incident in incidents:

        incident_id, timestamp, source, reason, status = incident

        with st.container():

            st.write(f"Incident ID: {incident_id}")
            st.write(f"Time: {timestamp}")
            st.write(f"Source: {source}")
            st.write(f"Reason: {reason}")
            st.write(f"Status: {status}")

            st.divider()

else:

    st.info("No incidents recorded yet.")


st.caption("Smart Health Monitoring System")
