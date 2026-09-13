import os
import csv


DATASET_PATH = os.path.join(
    "data",
    "multimodal_dataset.csv"
)


class SampleIDGenerator:

    def __init__(self, dataset_path=DATASET_PATH):

        self.dataset_path = dataset_path

        self.counter = self._get_next_number()

    def _get_next_number(self):

        if not os.path.exists(self.dataset_path):
            return 1

        try:

            with open(
                self.dataset_path,
                "r",
                newline="",
                encoding="utf-8"
            ) as file:

                reader = csv.DictReader(file)

                max_number = 0

                for row in reader:

                    sample_id = row.get(
                        "sample_id",
                        ""
                    )

                    if sample_id.startswith("S"):

                        try:

                            number = int(
                                sample_id[1:]
                            )

                            max_number = max(
                                max_number,
                                number
                            )

                        except ValueError:
                            continue

                return max_number + 1

        except Exception:

            return 1

    def next_id(self):

        sample_id = f"S{self.counter:06d}"

        self.counter += 1

        return sample_id


def create_sample_id_generator():

    return SampleIDGenerator()