import csv
import os
from datetime import datetime


RISK_GROUND_TRUTH_PATH = os.path.join(
    "data",
    "risk_ground_truth_dataset.csv"
)


VALID_RISK_LEVELS = [
    "LOW",
    "MODERATE",
    "HIGH",
    "CRITICAL"
]


RISK_CLASSES = {
    "LOW": 0,
    "MODERATE": 1,
    "HIGH": 2,
    "CRITICAL": 3
}


FIELDNAMES = [
    "sample_id",
    "timestamp",
    "ground_truth_risk",
    "risk_class",
    "annotator_note"
]


class RiskGroundTruthLogger:

    def __init__(
        self,
        dataset_path=RISK_GROUND_TRUTH_PATH
    ):

        self.dataset_path = dataset_path

        directory = os.path.dirname(
            self.dataset_path
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True
            )

        self._initialize_dataset()

    def _initialize_dataset(self):

        if (
            not os.path.exists(
                self.dataset_path
            )
            or os.path.getsize(
                self.dataset_path
            ) == 0
        ):

            with open(
                self.dataset_path,
                "w",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=FIELDNAMES
                )

                writer.writeheader()

    def log_risk_ground_truth(
        self,
        sample_id,
        ground_truth_risk,
        annotator_note=""
    ):

        sample_id = str(
            sample_id
        ).strip()

        if not sample_id:

            raise ValueError(
                "sample_id cannot be empty."
            )

        ground_truth_risk = str(
            ground_truth_risk
        ).upper().strip()

        if ground_truth_risk not in VALID_RISK_LEVELS:

            raise ValueError(
                "Invalid risk ground truth. "
                f"Expected one of: {VALID_RISK_LEVELS}"
            )

        sample = {

            "sample_id": sample_id,

            "timestamp": datetime.now().isoformat(
                timespec="milliseconds"
            ),

            "ground_truth_risk":
                ground_truth_risk,

            "risk_class":
                RISK_CLASSES[
                    ground_truth_risk
                ],

            "annotator_note":
                str(annotator_note)
        }

        with open(
            self.dataset_path,
            "a",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=FIELDNAMES
            )

            writer.writerow(sample)

        return sample


def create_risk_ground_truth_logger():

    return RiskGroundTruthLogger()
