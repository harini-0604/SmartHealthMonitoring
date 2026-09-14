import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DASHBOARD_DIR = Path(__file__).resolve().parent

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

from auth_ui import ambulance_authentication

from database.database import (
    get_incidents,
    update_ambulance_status,
    get_ambulance_status
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Ambulance Emergency Response",
    page_icon="Ambulance",
    layout="wide"
)

# ============================================================
# AMBULANCE AUTHENTICATION
# ============================================================

if "ambulance_logged_in" not in st.session_state:
    st.session_state.ambulance_logged_in = False


if not st.session_state.ambulance_logged_in:

    ambulance_authentication()

    st.stop()


# ============================================================
# LOGOUT
# ============================================================

if st.sidebar.button("Logout"):

    st.session_state.ambulance_logged_in = False

    st.rerun()

st.markdown("""
<style>
/* Metric Labels */
[data-testid="stMetricLabel"] {
    font-size: 24px !important;
    font-weight: 600!important;
}

[data-testid="stMetricLabel"] > div {
    font-size: 24px !important;
    font-weight: 600!important;
}

[data-testid="stMetricLabel"] > div > div {
    font-size: 24px !important;
    font-weight: 600!important;
}

[data-testid="stMetricLabel"] p {
    font-size: 24px !important;
    font-weight: 600!important;
}

/* Metric Values */
[data-testid="stMetricValue"] {
    font-size: 21px !important;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# TITLE
# ============================================================

st.title("🚑Ambulance Emergency Response Dashboard")
st.subheader("Emergency Dispatch and Response Monitoring")


# ============================================================
# LATEST EMERGENCY
# ============================================================

incidents = get_incidents()

st.header("🚨Emergency Alert")


if not incidents:

    st.info("No emergency incidents received.")

else:

    latest = incidents[0]

    incident_id, timestamp, source, reason, status = latest

    # --------------------------------------------------------
    # Emergency Information
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Incident ID", incident_id)

    with col2:
        st.metric("Emergency Type", source)

    with col3:
        st.metric("Status", status)

    with col4:
        st.metric("Alert Time", timestamp)

    # --------------------------------------------------------
    # Emergency Details
    # --------------------------------------------------------

    st.subheader("Emergency Details")

    st.write(f"**Reason:** {reason}")
    st.write(f"**Detected Time:** {timestamp}")
    st.write(f"**Detection Source:** {source}")


# ============================================================
# AMBULANCE STATUS
# ============================================================

st.header("🚑Ambulance Status")


if not incidents:

    st.info("WAITING FOR EMERGENCY ALERT")

else:

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # ALERT RECEIVED
    # --------------------------------------------------------

    with col1:

        st.success("ALERT RECEIVED")

    # --------------------------------------------------------
    # AMBULANCE RESPONSE
    # --------------------------------------------------------

    with col2:

        ambulance_status = get_ambulance_status(
            incident_id
        )

        current_status = ambulance_status["status"]


        # ====================================================
        # NOT DISPATCHED
        # ====================================================

        if current_status == "NOT_DISPATCHED":

            st.warning(
                "AMBULANCE DISPATCH REQUIRED"
            )

            if st.button(
                "Dispatch Ambulance",
                key="dispatch_ambulance"
            ):

                update_ambulance_status(
                    incident_id,
                    "DISPATCHED"
                )

                st.success(
                    "Ambulance dispatched successfully."
                )

                st.rerun()


        # ====================================================
        # DISPATCHED
        # ====================================================

        elif current_status == "DISPATCHED":

            st.success(
                "AMBULANCE DISPATCHED"
            )

            if st.button(
                "Mark Ambulance En Route",
                key="ambulance_en_route"
            ):

                update_ambulance_status(
                    incident_id,
                    "EN_ROUTE"
                )

                st.success(
                    "Ambulance is now en route."
                )

                st.rerun()


        # ====================================================
        # EN ROUTE
        # ====================================================

        elif current_status == "EN_ROUTE":

            st.info(
                "AMBULANCE EN ROUTE"
            )

            if st.button(
                "Mark Ambulance Arrived",
                key="ambulance_arrived"
            ):

                update_ambulance_status(
                    incident_id,
                    "ARRIVED"
                )

                st.success(
                    "Ambulance has arrived."
                )

                st.rerun()


        # ====================================================
        # ARRIVED
        # ====================================================

        elif current_status == "ARRIVED":

            st.success(
                "AMBULANCE ARRIVED"
            )


        # ====================================================
        # UNKNOWN STATUS
        # ====================================================

        else:

            st.info(
                f"AMBULANCE STATUS: {current_status}"
            )


# ============================================================
# RESPONSE INFORMATION
# ============================================================

st.header("📍Response Information")

col1, col2 = st.columns(2)

with col1:

    st.write(
        "**Patient Location:** "
        "Not Available"
    )

with col2:

    st.write(
        "**Response Status:** "
        "Ambulance Tracking Active"
    )


# ============================================================
# INCIDENT HISTORY
# ============================================================

st.header("📋Emergency Incident History")


if not incidents:

    st.info("No incidents available.")

else:

    for incident in incidents:

        incident_id, timestamp, source, reason, status = incident

        with st.expander(
            f"Incident #{incident_id} — {status}"
        ):

            st.write(
                f"**Time:** {timestamp}"
            )

            st.write(
                f"**Emergency Type:** {source}"
            )

            st.write(
                f"**Reason:** {reason}"
            )

            st.write(
                f"**Status:** {status}"
            )

            ambulance_info = get_ambulance_status(
                incident_id
            )

            st.write(
                f"**Ambulance Status:** "
                f"{ambulance_info['status']}"
            )

            if ambulance_info["updated_at"]:

                st.write(
                    f"**Last Updated:** "
                    f"{ambulance_info['updated_at']}"
                )