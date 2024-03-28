from typing import Dict, List
from sklearn.metrics import precision_recall_curve, auc
from src.config.constants import MetricScoreTypes
from src.evaluation.metrics.metric import Metric


class AreaUnderCurve(Metric):
    full_name = "Area Under Curve"
    short_name = "AUC"
    arg_name = "auc"
    metric_type = MetricScoreTypes.THRESHOLD_INDEPENDENT

    def calculate(
        self,
        _: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        traceability_score_dict: Dict[str, Dict[str, float]],
    ) -> float:
        ground_truth_labels = []
        predicted_labels = []

        for full_qualified_test_name in ground_truth_links:
            ground_truth_links_for_test = set(
                ground_truth_links[full_qualified_test_name]
            )
            for fully_qualified_function_name in traceability_score_dict[
                full_qualified_test_name
            ]:
                ground_truth_labels.append(
                    1
                    if fully_qualified_function_name in ground_truth_links_for_test
                    else 0
                )
                predicted_labels.append(
                    traceability_score_dict[full_qualified_test_name][
                        fully_qualified_function_name
                    ]
                )

        precision, recall, _ = precision_recall_curve(
            ground_truth_labels, predicted_labels
        )

        auc_score = auc(recall, precision)

        return auc_score


__all__ = ["AreaUnderCurve"]
