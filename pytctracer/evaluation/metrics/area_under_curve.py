from typing import Dict, List, Optional
from sklearn.metrics import precision_recall_curve, auc
from pytctracer.config.constants import MetricScoreType
from pytctracer.evaluation.metrics.metric import Metric


class AreaUnderCurve(Metric):
    """
    Class implementing the Area Under Curve (AUC) metric.
    """
    full_name = "Area Under Curve"
    short_name = "AUC"
    arg_name = "auc"
    metric_type = MetricScoreType.THRESHOLD_INDEPENDENT

    def calculate(
        self,
        _: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        traceability_score_dict: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> float:
        """
        Calculate the Area Under Curve (AUC) metric score given the ground truth links and the 
        traceability score dictionary. This is the precision-recall curve variant of AUC. 
        This metric is also threshold independent, and doesn't require the predicted links, 
        as they were created with the traceability score. 
        
        Args:
            _: A dictionary where the keys are the fully qualified names of the unit tests,
                and the values are lists of fully qualified names of the functions predicted
                to be linked to the unit test. This argument is not used in this metric.
            ground_truth_links (Dict[str, List[str]]): A dictionary where the keys are the
                fully qualified names of the unit tests, and the values are lists of fully
                qualified names of the functions that are actually linked to the unit test.
            traceability_score_dict (Optional[Dict[str, Dict[str, float]]]): A dictionary
                where the keys are the fully qualified names of the unit tests, and the values
                are dictionaries where the keys are the fully qualified names of the functions
                and the values are the traceability scores between the unit test and the function.
        
        Returns:
            float: The Area Under Curve metric score.
        """
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
