import os
import sys
import csv

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st

from data.ground_truth import GroundTruthLogger
from data.risk_ground_truth import RiskGroundTruthLogger


st.set_page_config(
    page_title="Ground Truth Annotation",
    layout="centered"
)


st.title("Ground Truth Annotation")

st.info(
    "Ground truth must be assigned independently by the human "
    "annotator. Do not use the AI prediction as the ground-truth label."
)


# ============================================================
# LOAD MULTIMODAL SAMPLES
# ============================================================

DATASET_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "multimodal_dataset.csv"
)


def get_sample_ids():

    if not os.path.exists(DATASET_PATH):
        return []

    sample_ids = []

    with open(
        DATASET_PATH,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            sample_id = row.get(
                "sample_id",
                ""
            ).strip()

            if sample_id:
                sample_ids.append(sample_id)

    return sample_ids


# ============================================================
# LOGGER INITIALIZATION
# ============================================================

if "ground_truth_logger" not in st.session_state:

    st.session_state.ground_truth_logger = (
        GroundTruthLogger()
    )


if "risk_ground_truth_logger" not in st.session_state:

    st.session_state.risk_ground_truth_logger = (
        RiskGroundTruthLogger()
    )


logger = st.session_state.ground_truth_logger

risk_logger = st.session_state.risk_ground_truth_logger


# ============================================================
# SAMPLE SELECTION
# ============================================================

sample_ids = get_sample_ids()


if not sample_ids:

    st.warning(
        "No multimodal samples are available for annotation."
    )

else:

    sample_id = st.selectbox(
        "Sample ID",
        sample_ids
    )


    # ========================================================
    # OBSERVED EVENT
    # ========================================================

    st.subheader("Observed Event")

    ground_truth_event = st.selectbox(
        "Event Label",
        [
            "NORMAL",
            "PRE_FALL",
            "FALL",
            "POST_FALL"
        ]
    )


    # ========================================================
    # EVENT ANNOTATOR NOTE
    # ========================================================

    annotator_note = st.text_area(
        "Event Annotator Note",
        placeholder=(
            "Describe what was actually observed..."
        )
    )


    # ========================================================
    # SAVE EVENT GROUND TRUTH
    # ========================================================

    if st.button("Save Event Ground Truth"):

        try:

            sample = logger.log_ground_truth(
                sample_id=sample_id,
                ground_truth_event=ground_truth_event,
                annotator_note=annotator_note
            )

            st.success(
                f"Event ground truth saved for {sample_id}"
            )

            st.json(sample)

        except Exception as error:

            st.error(
                f"Event ground truth annotation failed: {error}"
            )


    st.divider()


    # ========================================================
    # MULTIMODAL RISK GROUND TRUTH
    # ========================================================

    st.subheader("Multimodal Risk Ground Truth")

    st.info(
        "Assign the overall human-observed risk level independently "
        "from the AI prediction."
    )


    ground_truth_risk = st.selectbox(
        "Risk Level",
        [
            "LOW",
            "MODERATE",
            "HIGH",
            "CRITICAL"
        ]
    )


    # ========================================================
    # RISK ANNOTATOR NOTE
    # ========================================================

    risk_annotator_note = st.text_area(
        "Risk Annotator Note",
        placeholder=(
            "Explain why this overall risk level was assigned..."
        )
    )


    # ========================================================
    # SAVE RISK GROUND TRUTH
    # ========================================================

    if st.button("Save Risk Ground Truth"):

        try:

            sample = risk_logger.log_risk_ground_truth(
                sample_id=sample_id,
                ground_truth_risk=ground_truth_risk,
                annotator_note=risk_annotator_note
            )

            st.success(
                f"Risk ground truth saved for {sample_id}"
            )

            st.json(sample)

        except Exception as error:

            st.error(
                f"Risk ground truth annotation failed: {error}"
            )