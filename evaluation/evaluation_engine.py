import csv
import os
from collections import defaultdict


MULTIMODAL_DATASET = os.path.join(
    "data",
    "multimodal_dataset.csv"
)

RISK_GROUND_TRUTH_DATASET = os.path.join(
    "data",
    "risk_ground_truth_dataset.csv"
)


RISK_LABELS = {
    0: "LOW",
    1: "MODERATE",
    2: "HIGH",
    3: "CRITICAL"
}


class AIEvaluationEngine:

    def __init__(
        self,
        multimodal_path=MULTIMODAL_DATASET,
        risk_ground_truth_path=RISK_GROUND_TRUTH_DATASET
    ):

        self.multimodal_path = multimodal_path
        self.risk_ground_truth_path = risk_ground_truth_path


    # ============================================================
    # LOAD AI PREDICTIONS
    # ============================================================

    def _load_multimodal_data(self):

        if not os.path.exists(
            self.multimodal_path
        ):
            return []

        with open(
            self.multimodal_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            return list(
                csv.DictReader(file)
            )


    # ============================================================
    # LOAD HUMAN RISK GROUND TRUTH
    # ============================================================

    def _load_risk_ground_truth(self):

        if not os.path.exists(
            self.risk_ground_truth_path
        ):
            return []

        with open(
            self.risk_ground_truth_path,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            return list(
                csv.DictReader(file)
            )


    # ============================================================
    # EVALUATION
    # ============================================================

    def evaluate(self):

        predictions = self._load_multimodal_data()

        ground_truth = self._load_risk_ground_truth()


        truth_by_id = {

            row["sample_id"]: row

            for row in ground_truth

            if row.get("sample_id")
        }


        evaluated = []


        # ========================================================
        # MATCH AI PREDICTION WITH HUMAN RISK GROUND TRUTH
        # ========================================================

        for prediction in predictions:

            sample_id = prediction.get(
                "sample_id"
            )


            if not sample_id:
                continue


            if sample_id not in truth_by_id:
                continue


            predicted_risk = prediction.get(
                "risk_class"
            )

            actual_risk = truth_by_id[
                sample_id
            ].get(
                "risk_class"
            )


            if predicted_risk in ("", None):
                continue


            if actual_risk in ("", None):
                continue


            try:

                predicted_class = int(
                    float(predicted_risk)
                )

                actual_class = int(
                    float(actual_risk)
                )

            except (
                ValueError,
                TypeError
            ):

                continue


            if predicted_class not in RISK_LABELS:
                continue


            if actual_class not in RISK_LABELS:
                continue


            evaluated.append({

                "sample_id": sample_id,

                "predicted_class":
                    predicted_class,

                "predicted_label":
                    RISK_LABELS[predicted_class],

                "actual_class":
                    actual_class,

                "actual_label":
                    RISK_LABELS[actual_class]
            })


        # ========================================================
        # NO DATA
        # ========================================================

        total = len(evaluated)


        if total == 0:

            return {

                "status":
                    "NO_EVALUATED_SAMPLES",

                "evaluated_samples":
                    0,

                "accuracy":
                    0.0,

                "precision":
                    0.0,

                "recall":
                    0.0,

                "f1_score":
                    0.0,

                "correct_predictions":
                    0,

                "incorrect_predictions":
                    0,

                "confusion_matrix":
                    {},

                "details":
                    []
            }


        # ========================================================
        # ACCURACY
        # ========================================================

        correct = sum(

            1

            for row in evaluated

            if (
                row["predicted_class"]
                ==
                row["actual_class"]
            )
        )


        incorrect = total - correct


        accuracy = correct / total


        # ========================================================
        # CONFUSION MATRIX
        # ========================================================

        classes = sorted(

            set(
                row["actual_class"]
                for row in evaluated
            )
            |
            set(
                row["predicted_class"]
                for row in evaluated
            )
        )


        confusion_matrix = defaultdict(
            lambda: defaultdict(int)
        )


        for row in evaluated:

            actual = row["actual_class"]

            predicted = row["predicted_class"]

            confusion_matrix[
                actual
            ][
                predicted
            ] += 1


        # ========================================================
        # MACRO PRECISION / RECALL / F1
        # ========================================================

        precision_values = []

        recall_values = []

        f1_values = []


        for class_id in classes:

            true_positive = (
                confusion_matrix[class_id][class_id]
            )


            false_positive = sum(

                confusion_matrix[
                    other_class
                ][class_id]

                for other_class in classes

                if other_class != class_id
            )


            false_negative = sum(

                confusion_matrix[
                    class_id
                ][other_class]

                for other_class in classes

                if other_class != class_id
            )


            precision_denominator = (
                true_positive
                +
                false_positive
            )


            recall_denominator = (
                true_positive
                +
                false_negative
            )


            precision = (

                true_positive
                /
                precision_denominator

                if precision_denominator
                else 0.0
            )


            recall = (

                true_positive
                /
                recall_denominator

                if recall_denominator
                else 0.0
            )


            f1_denominator = (
                precision
                +
                recall
            )


            f1 = (

                2
                *
                precision
                *
                recall
                /
                f1_denominator

                if f1_denominator
                else 0.0
            )


            precision_values.append(
                precision
            )

            recall_values.append(
                recall
            )

            f1_values.append(
                f1
            )


        precision = (

            sum(precision_values)
            /
            len(precision_values)

            if precision_values
            else 0.0
        )


        recall = (

            sum(recall_values)
            /
            len(recall_values)

            if recall_values
            else 0.0
        )


        f1_score = (

            sum(f1_values)
            /
            len(f1_values)

            if f1_values
            else 0.0
        )


        # ========================================================
        # READABLE CONFUSION MATRIX
        # ========================================================

        readable_matrix = {}


        for actual in classes:

            actual_label = RISK_LABELS[
                actual
            ]


            readable_matrix[
                actual_label
            ] = {}


            for predicted in classes:

                predicted_label = RISK_LABELS[
                    predicted
                ]


                readable_matrix[
                    actual_label
                ][
                    predicted_label
                ] = confusion_matrix[
                    actual
                ][
                    predicted
                ]


        # ========================================================
        # RESULT
        # ========================================================

        return {

            "status":
                "EVALUATION_COMPLETED",

            "evaluated_samples":
                total,

            "accuracy":
                accuracy,

            "precision":
                precision,

            "recall":
                recall,

            "f1_score":
                f1_score,

            "correct_predictions":
                correct,

            "incorrect_predictions":
                incorrect,

            "confusion_matrix":
                readable_matrix,

            "details":
                evaluated
        }


def create_ai_evaluation_engine():

    return AIEvaluationEngine()


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    engine = create_ai_evaluation_engine()

    result = engine.evaluate()


    print("=" * 70)

    print(
        "SMART HEALTH MONITORING"
    )

    print(
        "MULTIMODAL RISK EVALUATION ENGINE"
    )

    print("=" * 70)

    print(
        "STATUS:",
        result["status"]
    )

    print(
        "EVALUATED SAMPLES:",
        result["evaluated_samples"]
    )

    print(
        "CORRECT:",
        result["correct_predictions"]
    )

    print(
        "INCORRECT:",
        result["incorrect_predictions"]
    )

    print(
        "ACCURACY:",
        f"{result['accuracy'] * 100:.2f}%"
    )

    print(
        "MACRO PRECISION:",
        f"{result['precision'] * 100:.2f}%"
    )

    print(
        "MACRO RECALL:",
        f"{result['recall'] * 100:.2f}%"
    )

    print(
        "MACRO F1 SCORE:",
        f"{result['f1_score'] * 100:.2f}%"
    )

    print()

    print(
        "CONFUSION MATRIX:"
    )

    for actual, predictions in result[
        "confusion_matrix"
    ].items():

        print(
            actual,
            "->",
            predictions
        )

    print()

    print(
        "DETAILS:"
    )

    for row in result["details"]:

        print(row)