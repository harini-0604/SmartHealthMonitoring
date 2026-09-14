import sys
from pathlib import Path
from datetime import datetime

import streamlit as st

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
    get_ambulance_status,
)

st.set_page_config(
    page_title="Ambulance Emergency Response",
    page_icon="🚑",
    layout="wide",
)

if "ambulance_logged_in" not in st.session_state:
    st.session_state.ambulance_logged_in = False

if not st.session_state.ambulance_logged_in:
    ambulance_authentication()
    st.stop()

if st.sidebar.button("Logout"):
    st.session_state.ambulance_logged_in = False
    st.rerun()

# Keep the same dashboard font sizing used in the current dashboard.
st.markdown(
    """
<style>
[data-testid="stMetricLabel"] {
    font-size: 24px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] > div {
    font-size: 24px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] > div > div {
    font-size: 24px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 24px !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    font-size: 21px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("🚑 Ambulance Emergency Response Dashboard")
st.subheader("Emergency Dispatch and Response Monitoring")

incidents = get_incidents()

# Make the newest incident appear first.
try:
    incidents = sorted(incidents, key=lambda item: item[1], reverse=True)
except Exception:
    pass

st.header("🚨 Emergency Alert")

if not incidents:
    st.info("No emergency incidents received.")
else:
    latest = incidents[0]
    incident_id, timestamp, source, reason, status = latest

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Incident ID", incident_id)

    with col2:
        st.metric("Emergency Type", source)

    with col3:
        st.metric("Status", status)

    with col4:
        st.metric("Alert Time", timestamp)

    st.subheader("Emergency Details")
    st.write(f"**Reason:** {reason}")
    st.write(f"**Detected Time:** {timestamp}")
    st.write(f"**Detection Source:** {source}")


st.header("🚑 Ambulance Status")

if not incidents:
    st.info("WAITING FOR EMERGENCY ALERT")
else:
    ambulance_info = get_ambulance_status(incident_id)
    current_status = ambulance_info.get("status", "NOT_DISPATCHED")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.success("📡 ALERT RECEIVED")

    with col2:
        st.info("🚑 AMBULANCE DISPATCH RECORD")
        st.write(f"**Incident:** #{incident_id}")
        st.write(f"**Current Status:** {current_status}")

    with col3:
        if current_status == "NOT_DISPATCHED":
            st.warning("AMBULANCE NOT DISPATCHED")
            if st.button("Dispatch Ambulance", key="dispatch_ambulance"):
                update_ambulance_status(incident_id, "DISPATCHED")
                st.success("Ambulance dispatched successfully.")
                st.rerun()

        elif current_status == "DISPATCHED":
            st.success("AMBULANCE DISPATCHED")
            if st.button("Mark Ambulance En Route", key="ambulance_en_route"):
                update_ambulance_status(incident_id, "EN_ROUTE")
                st.success("Ambulance is now en route.")
                st.rerun()

        elif current_status == "EN_ROUTE":
            st.info("AMBULANCE EN ROUTE")
            if st.button("Mark Ambulance Arrived", key="ambulance_arrived"):
                update_ambulance_status(incident_id, "ARRIVED")
                st.success("Ambulance has arrived.")
                st.rerun()

        elif current_status == "ARRIVED":
            st.success("AMBULANCE ARRIVED")

        else:
            st.info(f"AMBULANCE STATUS: {current_status}")


st.header("📍 Response Information")

col1, col2 = st.columns(2)

with col1:
    st.write("**Patient Location:** Not Available")

with col2:
    st.write("**Response Status:** Ambulance Tracking Active")


st.header("📋 Emergency Incident History")

if not incidents:
    st.info("No incidents available.")
else:
    for incident in incidents:
        incident_id, timestamp, source, reason, status = incident

        with st.expander(f"Incident #{incident_id} — {status}"):
            st.write(f"**Time:** {timestamp}")
            st.write(f"**Emergency Type:** {source}")
            st.write(f"**Reason:** {reason}")
            st.write(f"**Status:** {status}")

            ambulance_info = get_ambulance_status(incident_id)
            ambulance_status = ambulance_info.get("status", "NOT_DISPATCHED")

            # Human-readable dispatch state for the selected incident.
            if ambulance_status == "NOT_DISPATCHED":
                st.write("**Ambulance Status:** Not Dispatched")
                st.write("**Delay:** Waiting for ambulance dispatch")
            elif ambulance_status == "DISPATCHED":
                st.write("**Ambulance Status:** Dispatched")
                st.write("**Delay:** Dispatch recorded")
            elif ambulance_status == "EN_ROUTE":
                st.write("**Ambulance Status:** En Route")
                st.write("**Delay:** Ambulance en route")
            elif ambulance_status == "ARRIVED":
                st.write("**Ambulance Status:** Arrived")
                st.write("**Delay:** Response completed")
            else:
                st.write(f"**Ambulance Status:** {ambulance_status}")
                st.write("**Delay:** Not Available")

            if ambulance_info.get("updated_at"):
                st.write(f"**Last Update:** {ambulance_info['updated_at']}")
            else:
                st.write("**Last Update:** Not Available")