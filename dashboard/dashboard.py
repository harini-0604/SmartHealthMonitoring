import sys
from pathlib import Path
from datetime import datetime
import threading
import time

import cv2
import streamlit as st

import csv
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DASHBOARD_DIR = Path(__file__).resolve().parent

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

from auth_ui import patient_authentication

from database.database import (
    get_incidents,
    get_ambulance_status
)
from emergency.emergency_manager import handle_emergency
from emergency.verification import EmergencyVerification
from emergency.emergency_manager import handle_verified_emergency
from detection.multi_person_dashboard import (
    process_multi_person_frame
)


from sensors.esp32 import get_esp32_connection
from sensors.heart_rate import create_heart_rate_sensor
from sensors.spo2 import create_spo2_sensor
from sensors.temperature import create_temperature_sensor
from sensors.health_monitor import create_health_monitor
from sensors.risk_scoring import create_risk_scoring
from ai.risk_ai import create_ai_risk_scorer
from ai.multimodal_risk_ai import create_multimodal_risk_ai

from data.multimodal_logger import MultimodalDataLogger
from data.ground_truth import GroundTruthLogger
from data.risk_ground_truth import RiskGroundTruthLogger
from evaluation.evaluation_engine import create_ai_evaluation_engine
from data.sample_id import create_sample_id_generator

SHOW_DEVELOPMENT_SECTIONS = False

LOG_FILE = PROJECT_ROOT / "logs" / "emergency_log.txt"


st.set_page_config(
    page_title="Smart Health Monitoring",
    page_icon="H",
    layout="wide"
)

# ============================================================
# PATIENT AUTHENTICATION
# ============================================================

if "patient_logged_in" not in st.session_state:
    st.session_state.patient_logged_in = False


if not st.session_state.patient_logged_in:

    patient_authentication()

    st.stop()


# ============================================================
# LOGOUT
# ============================================================

if st.sidebar.button("Logout"):

    st.session_state.patient_logged_in = False

    st.rerun()

st.title("Smart Health Monitoring System")
st.subheader("AI-Based Health Monitoring and Emergency Response")

if st.button("Refresh Dashboard"):
    st.rerun()

st.divider()

# ============================================================
# EMERGENCY VERIFICATION STATE
# ============================================================

if "emergency_verification" not in st.session_state:

    st.session_state.emergency_verification = None


if "emergency_verification_active" not in st.session_state:

    st.session_state.emergency_verification_active = False


if "verification_thread" not in st.session_state:

    st.session_state.verification_thread = None


if "verification_result" not in st.session_state:

    st.session_state.verification_result = None

if "live_verification_result" not in st.session_state:

    st.session_state.live_verification_result = None

if "simulated_fall_active" not in st.session_state:
    
    st.session_state.simulated_fall_active = False

# ============================================================
# HEALTH TEST VALIDATION STATE
# ============================================================

if "health_test_stage" not in st.session_state:

    st.session_state.health_test_stage = "IDLE"


if "health_test_start_time" not in st.session_state:

    st.session_state.health_test_start_time = None


if "health_test_1" not in st.session_state:

    st.session_state.health_test_1 = None


if "health_test_2" not in st.session_state:

    st.session_state.health_test_2 = None


if "health_test_3" not in st.session_state:

    st.session_state.health_test_3 = None


if "health_test_final" not in st.session_state:

    st.session_state.health_test_final = None


if "health_test_message" not in st.session_state:

    st.session_state.health_test_message = ""

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
# FALL DEMONSTRATION / SIMULATION
# ============================================================

st.header("Fall Emergency Demonstration")

st.write(
    "Use this button to safely demonstrate the emergency "
    "verification workflow without physically falling."
)

if st.button("🔴 SIMULATE FALL", type="primary"):

    if not st.session_state.emergency_verification_active:

        try:

            simulation_reason = (
                "Simulated fall for project demonstration"
            )

            verification = EmergencyVerification(
                duration=30
            )

            verification.start(
                reason=simulation_reason,
                source="SIMULATED FALL"
            )

            st.session_state.emergency_verification = verification
            st.session_state.emergency_verification_active = True

            st.session_state.verification_result = None

            st.session_state.simulated_fall_active = True

            st.rerun()

        except Exception as error:

            st.error(
                f"Fall simulation error: {error}"
            )


# ------------------------------------------------------------
# RUN SIMULATED FALL VERIFICATION
# ------------------------------------------------------------

if (
    st.session_state.emergency_verification_active
    and st.session_state.get("simulated_fall_active", False)
    and st.session_state.emergency_verification is not None
):

    st.warning(
        "SIMULATED FALL DETECTED — Emergency verification started."
    )

    try:

        simulation_result = (
            st.session_state.emergency_verification
            .run_voice_verification()
        )

        st.session_state.verification_result = simulation_result

        st.session_state.emergency_verification_active = False
        st.session_state.simulated_fall_active = False

        status = simulation_result.get("status", "UNKNOWN")

        if status == "CANCELLED":

            st.success(
                "Emergency cancelled — person confirmed they are okay."
            )

        elif status in [
            "CONFIRMED",
            "NO_RESPONSE"
        ]:

            st.error(
                "🚨 Emergency confirmed. Starting Emergency Manager..."
            )

            try:

                emergency_result = handle_emergency(
                    reason=simulation_result.get(
                        "reason",
                        "Simulated fall for project demonstration"
                    ),
                    source="SIMULATED FALL"
                )

                st.session_state.emergency_result = emergency_result
                st.success(
                    "Emergency Manager completed. Alerts processed."
                )

            except Exception as error:

                st.error(
                    f"Emergency Manager error: {error}"
                )

        else:

            st.info(
                f"Verification result: {status}"
            )

    except Exception as error:

        st.session_state.emergency_verification_active = False
        st.session_state.simulated_fall_active = False

        st.error(
            f"Emergency verification error: {error}"
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

with detection_col2:

    st.write("Fall Detection")
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

def run_emergency_verification():

    try:

        result = (
            emergency_verification.run_voice_verification()
        )

        st.session_state["live_verification_result"] = result

    except Exception as error:

        st.session_state["live_verification_result"] = {
            "status": "ERROR",
            "error": str(error)
        }

if start_live_camera:

    #Current camera location
    CAMERA_ROOM = "Living Room"



    CAMERA_SOURCE = 0
    camera = cv2.VideoCapture(CAMERA_SOURCE)

    emergency_alert_sent = False

    # Live camera risk state
    st.session_state["live_inactivity_alert"] = False
    st.session_state["live_possible_fall"] = False
    st.session_state["live_confirmed_fall"] = False

    #Emergency verification state
    emergency_verification = None
    emergency_verification_active = False
    verification_thread = None
    verification_result = None

    # Multi-person tracking state
    multi_person_states = {}

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
                    people,
                    multi_person_states
                ) = process_multi_person_frame(
                    frame,
                    multi_person_states
                )

                # ------------------------------------------------
                # MULTI-PERSON STATUS
                # ------------------------------------------------

                person_count = len(people)

                fall_confirmed = any(
                    person["fall_confirmed"]
                    for person in people
                )

                body_angle = None

                if people:

                    valid_angles = [
                        person["body_angle"]
                        for person in people
                        if person["body_angle"] is not None
                    ]

                    if valid_angles:
                        body_angle = valid_angles[0]

                # Store live camera risk conditions
                st.session_state["live_confirmed_fall"] = fall_confirmed

                st.session_state["live_possible_fall"] = any(
                    person["status"] == "POSSIBLE FALL"
                    for person in people
                )


                st.session_state["live_pre_fall_risk"] = any(
                    person.get("pre_fall_confirmed", False)
                    for person in people
                )
                st.session_state["live_inactivity_alert"] = any(
                    person.get("inactivity_alert", False)
                    for person in people
                )

                # Overall monitoring status

                if fall_confirmed:
                    status = "FALL CONFIRMED"
                elif st.session_state.get("live_pre_fall_risk", False):
                    status = "PRE-FALL RISK"
                elif people:
                    status = "NORMAL"
                else:
                    status = "NO PERSON DETECTED"


                # Overall vertical speed for display

                vertical_speeds = [
                    abs(person["vertical_speed"])
                    for person in people
                    if person["vertical_speed"] is not None
                ]

                vertical_speed = (
                    max(vertical_speeds)
                    if vertical_speeds
                    else 0.0
                )

                # ------------------------------------------------
                # START EMERGENCY VERIFICATION
                # ------------------------------------------------
                
                if (
                    fall_confirmed
                    and not emergency_alert_sent
                    and not emergency_verification_active
                ):

                    fallen_people = [
                        str(person["id"])
                        for person in people
                        if person["fall_confirmed"]
                    ]

                    fall_reason = (
                        "Fall confirmed in "
                        + CAMERA_ROOM
                        + " for Person ID: "
                        + ", ".join(fallen_people)
                    )

                    try:
                        emergency_verification = EmergencyVerification(
                            duration=30
                        )

                        st.session_state.live_verification_result = None
                        emergency_verification_active = True

                        verification_thread = threading.Thread(
                            target=run_emergency_verification,
                            daemon=True
                        )

                        verification_thread.start()

                    except Exception as error:

                        emergency_verification_active = False

                        print(
                            f"Emergency verification error: {error}"
                        )


                # ------------------------------------------------
                # CHECK VERIFICATION RESULT
                # ------------------------------------------------
                
                if (
                    emergency_verification_active
                    and st.session_state.live_verification_result is not
                    None
                ):

                    result_status = st.session_state.live_verification_result.get(
                        "status"
                    )

                    if result_status == "CANCELLED":

                        emergency_alert_sent = False
                        emergency_verification_active = False

                    elif result_status in [
                        "CONFIRMED",
                        "NO_RESPONSE"
                    ]:

                        print()
                        print("🚨 FALL EMERGENCY CONFIRMED")
                        print("Starting Emergency Manager...")

                        try:

                            emergency_result = handle_emergency(
                                reason=st.session_state.live_verification_result.get(
                                    "reason",
                                    "Fall detected by AI system"
                                ),
                                source="FALL DETECTION"
                            )

                            print(
                                "Emergency Manager Result:",
                                emergency_result
                            )

                            emergency_alert_sent = True
                            emergency_verification_active = False

                        except Exception as error:

                            print(
                                "Emergency Manager error:",
                                error
                            )

                            emergency_verification_active = False

                # -----------------------------------------------
                # AUTOMATIC RECOVERY
                # ------------------------------------------------
                
                if not fall_confirmed:

                    if (
                        emergency_verification_active
                        and emergency_verification is not None
                    ):

                        emergency_verification.cancel(
                            reason="Person recovered after fall"
                        )

                        emergency_verification_active = False
                        st.session_state.live_verification_result = {
                            "status": "CANCELLED",
                            "reason": "Person recovered after fall"
                        }

                        emergency_alert_sent = False

                # ------------------------------------------------
                # BODY ANGLE
                # ------------------------------------------------

                if body_angle is not None:

                    cv2.putText(
                        annotated_frame,
                        f"Body angle: {body_angle:.1f}",
                        (20, 95),
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
                    (20, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 0),
                    2
                )

                # ------------------------------------------------
                # ROOM
                # ------------------------------------------------
                
                cv2.putText(
                    annotated_frame,
                    f"Room: {CAMERA_ROOM}",
                    (20, 125),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
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
                    (20, 200),
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

    # Store ESP32 readings for Health Test Validation
    st.session_state.esp32_sensor_data = esp32_data

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
        value=st.session_state.get("heart_rate_input",75.0),
        step=1.0
    )

    heart_rate_sensor.update(
        heart_rate_value
    )
    st.session_state.heart_rate_input = heart_rate_value

with sensor_col2:

    spo2_value = st.number_input(
        "SpO2 (%)",
        min_value=0.0,
        max_value=100.0,
        value=st.session_state.get("spo2_input",98.0),
        step=1.0
    )

    spo2_sensor.update(
        spo2_value
    )
    st.session_state.spo2_input = spo2_value


with sensor_col3:

    temperature_value = st.number_input(
        "Temperature (°C)",
        min_value=0.0,
        max_value=50.0,
        value=st.session_state.get("temperature_input",36.7),
        step=0.1
    )

    temperature_sensor.update(
        temperature_value
    )
    st.session_state.temperature_input = temperature_value

# ------------------------------------------------------------
# BP + EMERGENCY BUTTON
# ------------------------------------------------------------

bp_col1, bp_col2, bp_col3 = st.columns(3)


with bp_col1:

    systolic_bp = st.number_input(
        "Systolic BP (mmHg)",
        min_value=40,
        max_value=250,
        value=st.session_state.get("systolic-bp",118),
    )


with bp_col2:

    diastolic_bp = st.number_input(
        "Diastolic BP (mmHg)",
        min_value=20,
        max_value=150,
        value=st.session_state.get("diastolic_bp",76),
        step=1
    )

st.session_state.systolic_bp = systolic_bp
st.session_state.diastolic_bp = diastolic_bp

st.divider()

# ------------------------------------------------------------
# HEALTH MONITOR
# ------------------------------------------------------------

if "health_monitor" not in st.session_state:

    st.session_state.health_monitor = (
        create_health_monitor()
    )

health_monitor = st.session_state.health_monitor

# ============================================================
# AI RISK SCORING
# ============================================================

if "risk_scoring" not in st.session_state:

    st.session_state.risk_scoring = (
        create_risk_scoring()
    )

risk_scoring = st.session_state.risk_scoring

if "ai_risk_scorer" not in st.session_state:

    st.session_state.ai_risk_scorer = (
        create_ai_risk_scorer()
    )

ai_risk_scorer = st.session_state.ai_risk_scorer

if "multimodal_risk_ai" not in st.session_state:

    st.session_state.multimodal_risk_ai = (
        create_multimodal_risk_ai()
    )

multimodal_risk_ai = st.session_state.multimodal_risk_ai

if "multimodal_logger" not in st.session_state:

    st.session_state.multimodal_logger = (
        MultimodalDataLogger()
    )

multimodal_logger = st.session_state.multimodal_logger

if "ground_truth_logger" not in st.session_state:
    st.session_state.ground_truth_logger = (
        GroundTruthLogger()
    )

ground_truth_logger = st.session_state.ground_truth_logger

if "risk_ground_truth_logger" not in st.session_state:
    st.session_state.risk_ground_truth_logger = (
        RiskGroundTruthLogger()
    )

risk_ground_truth_logger = (
    st.session_state.risk_ground_truth_logger
)


if "ai_evaluation_engine" not in st.session_state:
    st.session_state.ai_evaluation_engine = (
        create_ai_evaluation_engine()
    )

ai_evaluation_engine = (
    st.session_state.ai_evaluation_engine
)

if "sample_id_generator" not in st.session_state:
    st.session_state.sample_id_generator = (
        create_sample_id_generator()
    )

sample_id_generator = st.session_state.sample_id_generator

# ------------------------------------------------------------
# CURRENT SENSOR VALUES
# ------------------------------------------------------------

st.subheader("Current Sensor Values")

value_col1, value_col2, value_col3 = st.columns(3)


with value_col1:

    st.metric(
        "Heart Rate",
        f"{heart_rate_sensor.read():.0f} BPM"
    )


with value_col2:

    st.metric(
        "SpO2",
        f"{spo2_sensor.read():.0f} %"
    )


with value_col3:

    st.metric(
        "Temperature",
        f"{temperature_sensor.read():.1f} °C"
    )


st.success(
    "Sensor interface is ready for future ESP32 integration."
)

st.divider()

# ============================================================
# HEALTH TEST VALIDATION SYSTEM
# ============================================================

st.header("Health Test Validation")

st.info(
    "The system performs multiple health tests with a "
    "stabilization period before AI risk assessment."
)
# ------------------------------------------------------------
# HELPER: GET CURRENT HEALTH VALUES
# ------------------------------------------------------------

def get_current_health_values():

    # Use ESP32 data when connected
    if esp32.connected:

        data = st.session_state.get(
            "esp32_sensor_data",
            {}
        )

        return {
            "heart_rate": data.get(
                "heart_rate",
                heart_rate_sensor.read()
            ),
            "spo2": data.get(
                "spo2",
                spo2_sensor.read()
            ),
            "temperature": data.get(
                "temperature",
                temperature_sensor.read()
            ),
            "systolic_bp": data.get(
                "systolic_bp",
                st.session_state.get(
                    "systolic_bp",
                    118
                )
            ),
            "diastolic_bp": data.get(
                "diastolic_bp",
                st.session_state.get(
                    "diastolic_bp",
                    76
                )
            )
        }

    # Fallback to software simulation
    return {
        "heart_rate": heart_rate_sensor.read(),
        "spo2": spo2_sensor.read(),
        "temperature": temperature_sensor.read(),
        "systolic_bp": st.session_state.get(
            "systolic_bp",
            118
        ),
        "diastolic_bp": st.session_state.get(
            "diastolic_bp",
            76
        )
    }

# ------------------------------------------------------------
# TEST CONTROL
# ------------------------------------------------------------

test_col1, test_col2 = st.columns(2)

with test_col1:

    if st.button(
        "▶ Start Health Test",
        disabled=(
            st.session_state.health_test_stage
            not in ["IDLE", "COMPLETED"]
        )
    ):

        # Capture Test 1
        st.session_state.health_test_1 = (
            get_current_health_values()
        )

        st.session_state.health_test_start_time = (
            datetime.now()
        )

        st.session_state.health_test_stage = (
            "WAITING_FOR_TEST_2"
        )

        st.rerun()


with test_col2:

    if st.button(
        "Reset Health Test",
        disabled=(
            st.session_state.health_test_stage
            == "IDLE"
        )
    ):

        st.session_state.health_test_stage = "IDLE"

        st.session_state.health_test_start_time = None

        st.session_state.health_test_1 = None

        st.session_state.health_test_2 = None

        st.session_state.health_test_3 = None

        st.session_state.health_test_final = None

        st.session_state.health_test_message = ""

        st.rerun()

# ------------------------------------------------------------
# DEVELOPMENT TEST MODE
# ------------------------------------------------------------

with st.expander("Developer Test Settings"):

    test_wait_minutes = st.number_input(
        "Stabilization time (minutes)",
        min_value=0.1,
        max_value=5.0,
        value=5.0,
        step=0.1
    )

    st.session_state.health_test_wait_time = (
        int(test_wait_minutes * 60)
    )

# ------------------------------------------------------------
# 5-MINUTE STABILIZATION PERIOD
# ------------------------------------------------------------

# ------------------------------------------------------------
# 5-MINUTE STABILIZATION PERIOD
# ------------------------------------------------------------

if (
    st.session_state.health_test_stage
    == "WAITING_FOR_TEST_2"
):

    elapsed_seconds = (
        datetime.now()
        - st.session_state.health_test_start_time
    ).total_seconds()

    stabilization_time = st.session_state.get(
        "health_test_wait_time",
        300
    )

    remaining_seconds = max(
        0,
        int(stabilization_time - elapsed_seconds)
    )

    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60

    st.warning(
        "TEST 1 COMPLETED — Stabilization period active"
    )

    st.subheader(
        f"TEST 2 will be available in "
        f"{minutes:02d}:{seconds:02d}"
    )

    st.progress(
        min(
            elapsed_seconds / stabilization_time,
            1.0
        )
    )

    st.info(
        "AI risk assessment is paused during the "
        "stabilization period."
    )

    # Automatically refresh the dashboard every second
    # so the countdown visibly decreases.
    if remaining_seconds > 0:

        time.sleep(1)

        st.rerun()

    else:

        st.session_state.health_test_stage = (
            "READY_FOR_TEST_2"
        )

        st.rerun()


# ------------------------------------------------------------
# TEST 2
# ------------------------------------------------------------

if (
    st.session_state.health_test_stage
    == "READY_FOR_TEST_2"
):

    st.success(
        "5-minute stabilization completed. "
        "Test 2 is ready."
    )

    if st.button("▶ Perform Test 2"):

        st.session_state.health_test_2 = (
            get_current_health_values()
        )

        st.session_state.health_test_stage = (
            "COMPARING"
        )

        st.rerun()


# ------------------------------------------------------------
# DISPLAY TEST RESULTS
# ------------------------------------------------------------

if st.session_state.health_test_1 is not None:

    st.write("### Test 1")

    st.json(
        st.session_state.health_test_1
    )


if st.session_state.health_test_2 is not None:

    st.write("### Test 2")

    st.json(
        st.session_state.health_test_2
    )

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
        "ABNORMAL HEALTH READING DETECTED"
    )

else:

    st.success(
        "HEALTH READINGS WITHIN CONFIGURED RANGE"
    )

# ============================================================
# AI RISK ASSESSMENT
# ============================================================

risk_result = risk_scoring.calculate_score(

    heart_rate_alert=(
        health_result["heart_rate"]["alert"]
    ),

    spo2_alert=(
        health_result["spo2"]["alert"]
    ),

    temperature_alert=(
        health_result["temperature"]["alert"]
    ),

    inactivity_alert=st.session_state.get(
        "live_inactivity_alert",
        False
    ),

    possible_fall=st.session_state.get(
        "live_possible_fall",
        False
    ),

    pre_fall_risk=st.session_state.get(
        "live_pre_fall_risk",
        False
    ),

    confirmed_fall=st.session_state.get(
        "live_confirmed_fall",
        False
    )

)
# HEALTH STATUS + VALIDATED AI ASSESSMENT
# ============================================================

st.header("Health Status")

# ------------------------------------------------------------
# SENSOR FLUCTUATION CHECK
# ------------------------------------------------------------

def calculate_fluctuation(test1, test2):

    differences = {

        "heart_rate": abs(
            test1["heart_rate"]
            - test2["heart_rate"]
        ),

        "spo2": abs(
            test1["spo2"]
            - test2["spo2"]
        ),

        "temperature": abs(
            test1["temperature"]
            - test2["temperature"]
        ),

        "systolic_bp": abs(
            test1["systolic_bp"]
            - test2["systolic_bp"]
        ),

        "diastolic_bp": abs(
            test1["diastolic_bp"]
            - test2["diastolic_bp"]
        )
    }

    thresholds = {

        "heart_rate": 15.0,

        "spo2": 3.0,

        "temperature": 0.5,

        "systolic_bp": 15.0,

        "diastolic_bp": 10.0
    }

    abnormal_sensors = []

    for sensor, difference in differences.items():

        if difference > thresholds[sensor]:

            abnormal_sensors.append(sensor)

    return {
        "differences": differences,
        "abnormal_sensors": abnormal_sensors,
        "large_fluctuation": bool(
            abnormal_sensors
        )
    }


# ------------------------------------------------------------
# TEST 2 COMPARISON
# ------------------------------------------------------------

if (
    st.session_state.health_test_stage
    == "COMPARING"
):

    test1 = st.session_state.health_test_1
    test2 = st.session_state.health_test_2

    fluctuation = calculate_fluctuation(
        test1,
        test2
    )

    st.subheader(
        "Test 1 vs Test 2 Validation"
    )

    if fluctuation["large_fluctuation"]:

        st.warning(
            "Significant sensor fluctuation detected."
        )

        st.write(
            "Sensors requiring additional verification:"
        )

        for sensor in fluctuation[
            "abnormal_sensors"
        ]:

            st.write(
                f"• {sensor}"
            )

        st.session_state.health_test_message = (
            "TEST 3 REQUIRED"
        )

        st.session_state.health_test_stage = (
            "READY_FOR_TEST_3"
        )

    else:

        st.success(
            "Test 1 and Test 2 are sufficiently "
            "consistent."
        )

        # ----------------------------------------------------
        # CALCULATE AVERAGE
        # ----------------------------------------------------

        st.session_state.health_test_final = {

            "heart_rate": (
                test1["heart_rate"]
                + test2["heart_rate"]
            ) / 2,

            "spo2": (
                test1["spo2"]
                + test2["spo2"]
            ) / 2,

            "temperature": (
                test1["temperature"]
                + test2["temperature"]
            ) / 2,

            "systolic_bp": (
                test1["systolic_bp"]
                + test2["systolic_bp"]
            ) / 2,

            "diastolic_bp": (
                test1["diastolic_bp"]
                + test2["diastolic_bp"]
            ) / 2
        }

        st.session_state.health_test_message = (
            "TEST 1 + TEST 2 AVERAGE USED"
        )

        st.session_state.health_test_stage = (
            "COMPLETED"
        )

    st.rerun()


# ------------------------------------------------------------
# TEST 3
# ------------------------------------------------------------

if (
    st.session_state.health_test_stage
    == "READY_FOR_TEST_3"
):

    st.warning(
        "TEST 3 REQUIRED because significant "
        "fluctuation was detected."
    )

    if st.button("▶ Perform Test 3"):

        st.session_state.health_test_3 = (
            get_current_health_values()
        )

        test1 = st.session_state.health_test_1
        test2 = st.session_state.health_test_2
        test3 = st.session_state.health_test_3

        # ----------------------------------------------------
        # FINAL THREE-TEST AVERAGE
        # ----------------------------------------------------

        st.session_state.health_test_final = {

            "heart_rate": (
                test1["heart_rate"]
                + test2["heart_rate"]
                + test3["heart_rate"]
            ) / 3,

            "spo2": (
                test1["spo2"]
                + test2["spo2"]
                + test3["spo2"]
            ) / 3,

            "temperature": (
                test1["temperature"]
                + test2["temperature"]
                + test3["temperature"]
            ) / 3,

            "systolic_bp": (
                test1["systolic_bp"]
                + test2["systolic_bp"]
                + test3["systolic_bp"]
            ) / 3,

            "diastolic_bp": (
                test1["diastolic_bp"]
                + test2["diastolic_bp"]
                + test3["diastolic_bp"]
            ) / 3
        }

        st.session_state.health_test_message = (
            "TEST 1 + TEST 2 + TEST 3 AVERAGE USED"
        )

        st.session_state.health_test_stage = (
            "COMPLETED"
        )

        st.rerun()


# ------------------------------------------------------------
# VALIDATED HEALTH DATA
# ------------------------------------------------------------

final_health_values = (
    st.session_state.health_test_final
)


if final_health_values is None:

    st.info(
        "Complete the health validation test "
        "before final AI risk assessment."
    )

else:

    st.success(
        st.session_state.health_test_message
    )

    st.subheader(
        "Validated Health Values"
    )

    value_col1, value_col2, value_col3, value_col4, value_col5 = (
        st.columns(5)
    )

    with value_col1:

        st.metric(
            "Heart Rate",
            f"{final_health_values['heart_rate']:.1f} BPM"
        )

    with value_col2:

        st.metric(
            "SpO₂",
            f"{final_health_values['spo2']:.1f}%"
        )

    with value_col3:

        st.metric(
            "Temperature",
            f"{final_health_values['temperature']:.1f} °C"
        )

    with value_col4:

        st.metric(
            "Systolic BP",
            f"{final_health_values['systolic_bp']:.1f}"
        )

    with value_col5:

        st.metric(
            "Diastolic BP",
            f"{final_health_values['diastolic_bp']:.1f}"
        )


    # ========================================================
    # HEALTH MONITOR
    # ========================================================

    health_result = health_monitor.check_all(

        heart_rate=final_health_values[
            "heart_rate"
        ],

        spo2=final_health_values[
            "spo2"
        ],

        temperature=final_health_values[
            "temperature"
        ],

        systolic_bp=final_health_values[
            "systolic_bp"
        ],

        diastolic_bp=final_health_values[
            "diastolic_bp"
        ]
    )


    if health_result["alert"]:

        st.error(
            "ABNORMAL VALIDATED HEALTH READING DETECTED"
        )

    else:

        st.success(
            "VALIDATED HEALTH READINGS WITHIN "
            "CONFIGURED RANGE"
        )


    # ========================================================
    # AI MODEL RISK PREDICTION
    # ========================================================

    ai_risk_result = ai_risk_scorer.predict(

        heart_rate=final_health_values[
            "heart_rate"
        ],

        spo2=final_health_values[
            "spo2"
        ],

        systolic_bp=final_health_values[
            "systolic_bp"
        ],

        diastolic_bp=final_health_values[
            "diastolic_bp"
        ],

        temperature=final_health_values[
            "temperature"
        ],

        inactivity_duration=st.session_state.get(
            "live_inactivity_duration",
            0
        ),

        possible_fall=st.session_state.get(
            "live_possible_fall",
            False
        ),

        confirmed_fall=st.session_state.get(
            "live_confirmed_fall",
            False
        )
    )

    # ========================================================
    # MULTIMODAL AI RISK PREDICTION
    # ========================================================

    esp32_sensor_data = st.session_state.get(
        "esp32_sensor_data",
            {}
    )

    imu_data = esp32_sensor_data.get(
        "imu",
        {}
    )

    multimodal_risk_result = multimodal_risk_ai.predict(

        heart_rate=final_health_values[
            "heart_rate"
        ],

        spo2=final_health_values[
            "spo2"
        ],

        systolic_bp=final_health_values[
            "systolic_bp"
        ],

        diastolic_bp=final_health_values[
            "diastolic_bp"
        ],

        temperature=final_health_values[
            "temperature"
        ],

        inactivity_duration=st.session_state.get(
            "live_inactivity_duration",
            0
        ),

        possible_fall=st.session_state.get(
            "live_possible_fall",
            False
        ),

        confirmed_fall=st.session_state.get(
            "live_confirmed_fall",
            False
        ),

        pre_fall_risk=st.session_state.get(
            "live_pre_fall_risk",
            False
        ),

        acceleration_magnitude=imu_data.get(
            "acceleration_magnitude",
            0.0
        ),

        gyroscope_magnitude=imu_data.get(
            "gyroscope_magnitude",
            0.0
        ),

        acceleration_change=imu_data.get(
            "acceleration_change",
            0.0
        ),

        gyroscope_change=imu_data.get(
            "gyroscope_change",
            0.0
        )
    )

    # ========================================================
    # LOG MULTIMODAL AI SAMPLE
    # ========================================================

    multimodal_logger.log_sample(

        heart_rate=final_health_values[
            "heart_rate"
        ],

        spo2=final_health_values[
            "spo2"
        ],

        systolic_bp=final_health_values[
            "systolic_bp"
        ],

        diastolic_bp=final_health_values[
            "diastolic_bp"
        ],

        temperature=final_health_values[
            "temperature"
        ],

        inactivity_duration=st.session_state.get(
            "live_inactivity_duration",
            0
        ),

        possible_fall=st.session_state.get(
            "live_possible_fall",
            False
        ),

        pre_fall_risk=st.session_state.get(
            "live_pre_fall_risk",
            False
        ),

        confirmed_fall=st.session_state.get(
            "live_confirmed_fall",
            False
        ),

        acceleration_magnitude=imu_data.get(
            "acceleration_magnitude",
            0.0
        ),

        gyroscope_magnitude=imu_data.get(
            "gyroscope_magnitude",
            0.0
        ),

        acceleration_change=imu_data.get(
            "acceleration_change",
            0.0
        ),

        gyroscope_change=imu_data.get(
            "gyroscope_change",
            0.0
        ),

        risk_class=multimodal_risk_result[
            "risk_class"
        ],

        risk_level=multimodal_risk_result[
            "risk_level"
        ],

        risk_confidence=multimodal_risk_result[
            "confidence"
        ]
    )

    # ========================================================
    # MULTIMODAL AI RISK DISPLAY
    # ========================================================

    #st.header("Multimodal AI Risk Assessment")

    if SHOW_DEVELOPMENT_SECTIONS:

        mm_col1, mm_col2, mm_col3 = st.columns(3)

        with mm_col1:

            st.metric(
                "AI Risk Class",
                multimodal_risk_result["risk_class"]
            )

        with mm_col2:
 
            st.metric(
                "AI Risk Level",
                multimodal_risk_result["risk_level"]
            )

        with mm_col3:

            st.metric(
                "AI Confidence",
                f"{multimodal_risk_result['confidence']:.2f}%"
            )


        st.write("**Risk Probabilities:**")

        probabilities = multimodal_risk_result["probabilities"]

        for level, probability in probabilities.items():

            st.write(
                f"**{level}** : "
                f"{probability * 100:.2f}%"
            )


    # ========================================================
    # MULTIMODAL AI DECISION
    # ========================================================

    if SHOW_DEVELOPMENT_SECTIONS and multimodal_risk_result["risk_level"] == "CRITICAL":

        st.error(
            "CRITICAL RISK: Emergency verification required."
        )

    elif multimodal_risk_result["risk_level"] == "HIGH":

        st.warning(
            "HIGH RISK: Close monitoring required."
        )

    elif multimodal_risk_result["risk_level"] == "MODERATE":

        st.warning(
            "MODERATE RISK: Continue monitoring."
        )

    else:

        st.success(
            "LOW RISK: No immediate risk detected."
        )

    # ========================================================
    # AI RISK DECISION
    # ========================================================

    if SHOW_DEVELOPMENT_SECTIONS and ai_risk_result["risk_level"] == "CRITICAL":

        st.error(
            "CRITICAL RISK: Emergency verification required."
        )

    elif ai_risk_result["risk_level"] == "HIGH":

        st.warning(
            "HIGH RISK: Close monitoring required."
        )

    elif ai_risk_result["risk_level"] == "MODERATE":

        st.warning(
            "MODERATE RISK: Continue monitoring."
        )

    else:

        st.success(
            "LOW RISK: No immediate risk detected."
        )

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

        reason = alert.get("reason", "Health alert")
        value = alert.get("value")

        if value is not None:

            st.warning(
                f"{reason} "
                f"(Value: {value})"
            )

        else:

            st.warning(reason)

else:

    st.info(
        "No health threshold alerts detected."
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

if st.button("Test Emergency System"):

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
            test_result["emergency_service"]["status"]
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
    if incident[4] in ("POSSIBLE EMERGENCY", "EMERGENCY_CONFIRMED")
]

emergency_alerts = sorted(
    emergency_alerts,
    key=lambda incident: incident[0],
    reverse=True
)

if emergency_alerts:

    for incident in emergency_alerts[:10]:

        incident_id = incident[0]
        incident_time = incident[1]
        incident_source = incident[2]
        incident_reason = incident[3]

        st.error(
            f"{incident[4]}"
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
        "No emergency alerts recorded."
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
        if incident[4] in ("POSSIBLE EMERGENCY", "EMERGENCY_CONFIRMED")
    ]

    emergency_incidents = sorted(
        emergency_incidents,
        key=lambda incident: incident[0],
        reverse=True
    )

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
            f"{emergency_status}"
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

            # --------------------------------------------------------
            # AMBULANCE RESPONSE STATUS
            # --------------------------------------------------------

            ambulance_info = get_ambulance_status(
                emergency_id
            )

            ambulance_status = ambulance_info["status"]

            st.subheader("Ambulance Response")

            ambulance_col1, ambulance_col2 = st.columns(2)

            with ambulance_col1:

                st.write(
                    f"**Ambulance Status:** "
                    f"{ambulance_status}"
                )

            with ambulance_col2:

                if ambulance_status == "NOT_DISPATCHED":

                    st.warning(
                        "AMBULANCE DISPATCH REQUIRED"
                    )

                elif ambulance_status == "DISPATCHED":

                    st.success(
                        "AMBULANCE DISPATCHED"
                    )

                elif ambulance_status == "EN_ROUTE":

                    st.info(
                        "AMBULANCE EN ROUTE"
                    )

                elif ambulance_status == "ARRIVED":

                    st.success(
                        "AMBULANCE ARRIVED"
                    )

                else:

                    st.info(
                        f"AMBULANCE STATUS: "
                        f"{ambulance_status}"
                    )

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
