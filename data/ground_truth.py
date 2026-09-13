import csv
import os
from datetime import datetime


GROUND_TRUTH_PATH = os.path.join(
    "data",
    "ground_truth_dataset.csv"
)


VALID_EVENTS = [
    "NORMAL",
    "PRE_FALL",
    "FALL",
    "POST_FALL"
]


EVENT_CLASSES = {
    "NORMAL": 0,
    "PRE_FALL": 1,
    "FALL": 2,
    "POST_FALL": 3
}


FIELDNAMES = [
    "sample_id",
    "timestamp",
    "ground_truth_event",
    "event_class",
    "annotator_note"
]


class GroundTruthLogger:

    def __init__(
        self,
        dataset_path=GROUND_TRUTH_PATH
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

    def log_ground_truth(
        self,
        sample_id,
        ground_truth_event,
        annotator_note=""
    ):

        sample_id = str(
            sample_id
        ).strip()

        if not sample_id:

            raise ValueError(
                "sample_id cannot be empty."
            )

        ground_truth_event = str(
            ground_truth_event
        ).upper().strip()

        if ground_truth_event not in VALID_EVENTS:

            raise ValueError(
                "Invalid ground-truth event. "
                f"Expected one of: {VALID_EVENTS}"
            )

        sample = {

            "sample_id": sample_id,

            "timestamp": datetime.now().isoformat(
                timespec="milliseconds"
            ),

            "ground_truth_event":
                ground_truth_event,

            "event_class":
                EVENT_CLASSES[
                    ground_truth_event
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


def create_ground_truth_logger():

    return GroundTruthLogger()