import sys
from pathlib import Path
from datetime import datetime

import cv2
import streamlit as st
import mediapipe as mp


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from database.database import get_incidents
from emergency.emergency_manager import handle_emergency
from detection.person_detection import (
    run_person_detection, 
    process_person_frame)
from detection.pose_detection import (
    run_pose_detection,
    process_pose_frame)
from detection.fall_detection import (
    run_fall_detection,
    process_fall_frame)
from detection.activity_detection import run_activity_detection

from ultralytics import YOLO

from sensors.esp32 import get_esp32_connection
from sensors.heart_rate import create_heart_rate_sensor
from sensors.spo2 import create_spo2_sensor
from sensors.temperature import create_temperature_sensor
from sensors.health_monitor import create_health_monitor


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
# LIVE CAMERA + FALL MONITORING
# ============================================================

st.header("Live Camera Monitoring")

start_live_camera = st.checkbox(
    "Start Live Health Monitoring"
)

live_camera_placeholder = st.empty()

person_status_placeholder = st.empty()

fall_status_placeholder = st.empty()


if start_live_camera:

    model = YOLO("yolo11n.pt")

    camera = cv2.VideoCapture(0)

    mp_pose = mp.solutions.pose

    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    body_y_history = []

    previous_body_y = None
    previous_time = None

    fall_candidate = False
    fall_confirmed = False
    fall_candidate_start = None
    emergency_alert_sent = False

    if not camera.isOpened():

        st.error(
            "Unable to open the camera."
        )

    else:

        st.success(
            "Live health monitoring is running."
        )

        try:

            while True:

                ret, frame = camera.read()

                if not ret:

                    st.error(
                        "Unable to read camera frame."
                    )

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


                # ------------------------------------------------
                # BODY ANGLE
                # ------------------------------------------------

                if body_angle is not None:

                    cv2.putText(
                        annotated_frame,
                        f"Body angle: {body_angle:.1f}",
                        (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        (0, 255, 0),
                        2
                    )


                # ------------------------------------------------
                # BODY Y
                # ------------------------------------------------

                if body_y is not None:

                    cv2.putText(
                        annotated_frame,
                        f"Body Y: {body_y:.3f}",
                        (20, 65),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        (0, 255, 0),
                        2
                    )


                # ------------------------------------------------
                # VERTICAL SPEED
                # ------------------------------------------------

                cv2.putText(
                    annotated_frame,
                    f"Vertical speed: {vertical_speed:.3f}",
                    (20, 95),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 0),
                    2
                )


                # ------------------------------------------------
                # PEOPLE
                # ------------------------------------------------

                cv2.putText(
                    annotated_frame,
                    f"People: {person_count}",
                    (20, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 0),
                    2
                )


                # ------------------------------------------------
                # STATUS
                # ------------------------------------------------

                cv2.putText(
                    annotated_frame,
                    f"Status: {status}",
                    (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (0, 255, 255),
                    2
                )


                # ------------------------------------------------
                # TIME
                # ------------------------------------------------

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


                # ------------------------------------------------
                # STREAMLIT DISPLAY
                # ------------------------------------------------

                annotated_frame = cv2.cvtColor(
                    annotated_frame,
                    cv2.COLOR_BGR2RGB
                )


                live_camera_placeholder.image(
                    annotated_frame,
                    channels="RGB",
                    use_container_width=True
                )


                person_status_placeholder.metric(
                    "People Detected",
                    person_count
                )


                fall_status_placeholder.metric(
                    "Fall Status",
                    status
                )


        finally:

            camera.release()

            pose.close()

# ============================================================
# HEALTH SENSORS
# ============================================================

st.header("Health Sensors")

# ------------------------------------------------------------
# ESP32 CONNECTION
# ------------------------------------------------------------

st.subheader("ESP32 Connection")


# ------------------------------------------------------------
# CREATE ESP32 CONNECTION
# ------------------------------------------------------------

if "esp32" not in st.session_state:

    st.session_state.esp32 = (
        get_esp32_connection()
    )


esp32 = st.session_state.esp32


# ------------------------------------------------------------
# CONNECTION STATUS
# ------------------------------------------------------------

if esp32.connected:

    st.success(
        "ESP32 connection interface is READY."
    )

else:

    st.warning(
        "ESP32 is currently disconnected."
    )


# ------------------------------------------------------------
# CONNECT / DISCONNECT
# ------------------------------------------------------------

connection_col1, connection_col2 = st.columns(2)


with connection_col1:

    if st.button("Connect ESP32"):

        connected = esp32.connect()

        if connected:

            st.success(
                "ESP32 connected successfully."
            )

        else:

            st.error(
                "ESP32 connection failed."
            )


with connection_col2:

    if st.button("Disconnect ESP32"):

        esp32.disconnect()

        st.info(
            "ESP32 disconnected."
        )


# ------------------------------------------------------------
# ESP32 DATA
# ------------------------------------------------------------

if esp32.connected:

    esp32_data = esp32.read_data()

    st.subheader("ESP32 Sensor Data")

    data_col1, data_col2, data_col3 = (
        st.columns(3)
    )


    with data_col1:

        st.metric(
            "Heart Rate",
            f"{esp32_data.get('heart_rate', 'No Data')} BPM"
        )


    with data_col2:

        st.metric(
            "SpO2",
            f"{esp32_data.get('spo2', 'No Data')} %"
        )


    with data_col3:

        st.metric(
            "Temperature",
            f"{esp32_data.get('temperature', 'No Data')} °C"
        )


    st.caption(
        f"Data source: "
        f"{esp32_data.get('source', 'ESP32')}"
    )


else:

    st.info(
        "Connect the ESP32 interface to display "
        "sensor data."
    )


st.info(
    "Hardware connection is currently simulated. "
    "No physical ESP32 device is connected."
)


# ------------------------------------------------------------
# SENSOR SIMULATION
# ------------------------------------------------------------

st.subheader("Sensor Simulation")

st.info(
    "Physical sensors are not connected. "
    "The values below are software-simulated for development."
)

# ------------------------------------------------------------
# SENSOR OBJECTS
# ------------------------------------------------------------

if "heart_rate_sensor" not in st.session_state:

    st.session_state.heart_rate_sensor = (
        create_heart_rate_sensor()
    )


if "spo2_sensor" not in st.session_state:

    st.session_state.spo2_sensor = (
        create_spo2_sensor()
    )


if "temperature_sensor" not in st.session_state:

    st.session_state.temperature_sensor = (
        create_temperature_sensor()
    )


heart_rate_sensor = st.session_state.heart_rate_sensor
spo2_sensor = st.session_state.spo2_sensor
temperature_sensor = st.session_state.temperature_sensor

sensor_col1, sensor_col2, sensor_col3 = st.columns(3)


with sensor_col1:

    heart_rate_value = st.number_input(
        "Heart Rate (BPM)",
        min_value=0.0,
        max_value=250.0,
        value=75.0,
        step=1.0
    )

    heart_rate_sensor.update(
        heart_rate_value
    )


with sensor_col2:

    spo2_value = st.number_input(
        "SpO2 (%)",
        min_value=0.0,
        max_value=100.0,
        value=98.0,
        step=1.0
    )

    spo2_sensor.update(
        spo2_value
    )


with sensor_col3:

    temperature_value = st.number_input(
        "Temperature (°C)",
        min_value=0.0,
        max_value=50.0,
        value=36.7,
        step=0.1
    )

    temperature_sensor.update(
        temperature_value
    )


st.divider()

# ------------------------------------------------------------
# HEALTH MONITOR
# ------------------------------------------------------------

if "health_monitor" not in st.session_state:

    st.session_state.health_monitor = (
        create_health_monitor()
    )

health_monitor = st.session_state.health_monitor

# ------------------------------------------------------------
# CURRENT SENSOR VALUES
# ------------------------------------------------------------

st.subheader("Current Sensor Values")

value_col1, value_col2, value_col3 = st.columns(3)


with value_col1:

    st.metric(
        "❤️ Heart Rate",
        f"{heart_rate_sensor.read():.0f} BPM"
    )


with value_col2:

    st.metric(
        "🫁 SpO2",
        f"{spo2_sensor.read():.0f} %"
    )


with value_col3:

    st.metric(
        "🌡️ Temperature",
        f"{temperature_sensor.read():.1f} °C"
    )


st.success(
    "Sensor interface is ready for future ESP32 integration."
)

st.divider()

# ============================================================
# HEALTH STATUS
# ============================================================

st.header("Health Status")

health_result = health_monitor.check_all(
    heart_rate=heart_rate_sensor.read(),
    spo2=spo2_sensor.read(),
    temperature=temperature_sensor.read()
)


if health_result["alert"]:

    st.error(
        "⚠️ ABNORMAL HEALTH READING DETECTED"
    )

else:

    st.success(
        "✅ HEALTH READINGS WITHIN CONFIGURED RANGE"
    )

# ------------------------------------------------------------
# AUTOMATIC HEALTH EMERGENCY TRIGGER
# ------------------------------------------------------------

if health_result["alert"]:

    if not st.session_state.health_emergency_active:

        alert_reasons = []

        for alert in health_result["alerts"]:

            alert_reasons.append(
                f"{alert['reason']} "
                f"(Value: {alert['value']})"
            )

        combined_reason = "; ".join(
            alert_reasons
        )

        try:

            emergency_result = handle_emergency(
                reason=(
                    "Abnormal health reading: "
                    + combined_reason
                ),
                source="HEALTH SENSOR"
            )

            st.session_state.health_emergency_active = True

            st.warning(
                "Emergency response pipeline triggered "
                "for abnormal health readings."
            )

        except Exception as error:

            st.error(
                f"Health emergency handling failed: {error}"
            )

else:

    # Reset after readings return to normal
    st.session_state.health_emergency_active = False

# ------------------------------------------------------------
# INDIVIDUAL SENSOR STATUS
# ------------------------------------------------------------

status_col1, status_col2, status_col3 = st.columns(3)


with status_col1:

    heart_status = health_result["heart_rate"]

    if heart_status["alert"]:

        st.error(
            f"Heart Rate: {heart_status['status']}"
        )

    else:

        st.success(
            f"Heart Rate: {heart_status['status']}"
        )


with status_col2:

    spo2_status = health_result["spo2"]

    if spo2_status["alert"]:

        st.error(
            f"SpO2: {spo2_status['status']}"
        )

    else:

        st.success(
            f"SpO2: {spo2_status['status']}"
        )


with status_col3:

    temperature_status = (
        health_result["temperature"]
    )

    if temperature_status["alert"]:

        st.error(
            f"Temperature: "
            f"{temperature_status['status']}"
        )

    else:

        st.success(
            f"Temperature: "
            f"{temperature_status['status']}"
        )


# ------------------------------------------------------------
# ALERT DETAILS
# ------------------------------------------------------------

if health_result["alerts"]:

    st.subheader("Health Alerts")

    for alert in health_result["alerts"]:

        st.warning(
            f"{alert['reason']} "
            f"(Value: {alert['value']})"
        )

else:

    st.info(
        "No health threshold alerts detected."
    )


st.caption(
    "Health status uses software demonstration "
    "thresholds and is not a medical diagnosis."
)


st.divider()

# ============================================================
# EMERGENCY SYSTEM TEST
# ============================================================

st.header("Emergency System Test")

st.info(
    "Use this button only to test the emergency-response "
    "software pipeline. It does not contact real emergency services."
)

if st.button("🚨 Test Emergency System"):

    try:

        test_result = handle_emergency(
            reason="Dashboard emergency system test",
            source="DASHBOARD TEST"
        )

        st.success(
            f"Emergency test completed: "
            f"{test_result['status']}"
        )

        st.write(
            "Notification:",
            test_result["notification"]["status"]
        )

        st.write(
            "Hospital:",
            test_result["hospital"]["status"]
        )

        st.write(
            "Emergency Service:",
            test_result["ambulance"]["status"]
        )

    except Exception as error:

        st.error(
            f"Emergency system test failed: {error}"
        )


st.divider()

# ============================================================
# EMERGENCY ALERTS
# ============================================================

st.header("Emergency Alerts")

# Read emergency incidents directly from SQLite database
incidents = get_incidents()

emergency_alerts = [
    incident
    for incident in incidents
    if incident[4] == "POSSIBLE EMERGENCY"
]

if emergency_alerts:

    for incident in emergency_alerts[:10]:

        incident_id = incident[0]
        incident_time = incident[1]
        incident_source = incident[2]
        incident_reason = incident[3]

        st.error(
            "🚨 POSSIBLE EMERGENCY"
        )

        st.write(
            f"**Incident #{incident_id}**"
        )

        st.write(
            f"**Time:** {incident_time}"
        )

        st.write(
            f"**Source:** {incident_source}"
        )

        st.write(
            f"**Reason:** {incident_reason}"
        )

        st.divider()

else:

    st.success(
        "✅ No emergency alerts recorded."
    )


# ============================================================
# INCIDENT HISTORY
# ============================================================

st.header("Incident History")

incidents = get_incidents()

if incidents:

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total_incidents = len(incidents)

    emergency_incidents = [
        incident
        for incident in incidents
        if incident[4] == "POSSIBLE EMERGENCY"
    ]

    emergency_count = len(emergency_incidents)

    latest_incident = incidents[0]

    latest_source = latest_incident[2]

    # --------------------------------------------------------
    # DASHBOARD METRICS
    # --------------------------------------------------------

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:

        st.metric(
            "Total Incidents",
            total_incidents
        )

    with metric_col2:

        st.metric(
            "Emergency Alerts",
            emergency_count
        )

    with metric_col3:

        st.metric(
            "Latest Source",
            latest_source
        )

    st.divider()

    # --------------------------------------------------------
    # LATEST EMERGENCY
    # --------------------------------------------------------

    if emergency_incidents:

        latest_emergency = emergency_incidents[0]

        st.subheader("Latest Emergency")

        emergency_id = latest_emergency[0]
        emergency_time = latest_emergency[1]
        emergency_source = latest_emergency[2]
        emergency_reason = latest_emergency[3]
        emergency_status = latest_emergency[4]

        st.error(
            f"🚨 {emergency_status}"
        )

        detail_col1, detail_col2 = st.columns(2)

        with detail_col1:

            st.write(
                f"**Incident ID:** {emergency_id}"
            )

            st.write(
                f"**Time:** {emergency_time}"
            )

            st.write(
                f"**Source:** {emergency_source}"
            )

        with detail_col2:

            st.write(
                f"**Reason:** {emergency_reason}"
            )

            st.write(
                f"**Status:** {emergency_status}"
            )

    st.divider()

    # --------------------------------------------------------
    # ALL INCIDENTS
    # --------------------------------------------------------

    st.subheader("All Incidents")

    for incident in incidents:

        (
            incident_id,
            timestamp,
            source,
            reason,
            status
        ) = incident

        with st.expander(
            f"Incident #{incident_id} — {status}"
        ):

            st.write(
                f"**Time:** {timestamp}"
            )

            st.write(
                f"**Source:** {source}"
            )

            st.write(
                f"**Reason:** {reason}"
            )

            if status == "POSSIBLE EMERGENCY":

                st.error(
                    f"Status: {status}"
                )

            else:

                st.info(
                    f"Status: {status}"
                )

else:

    st.info(
        "No incidents recorded yet."
    )


st.caption("Smart Health Monitoring System")
