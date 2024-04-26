from typing import Dict, List, Optional
from pytctracer.config.constants import MetricScoreType
from pytctracer.evaluation.metrics.metric import Metric
from pytctracer.evaluation.metrics.precision import Precision
from pytctracer.evaluation.metrics.recall import Recall


class F1(Metric):
    """
    Class implementing the F1 metric.
    """
    full_name = "F1"
    short_name = "F1"
    arg_name = "f1"
    metric_type = MetricScoreType.CONTINUOUS

    def calculate(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        _: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> float:
        """
        Calculate the F1 metric score given the predicted links and ground truth links.

        Args:
            predicted_links (Dict[str, List[str]]): A dictionary where the keys are
                the fully qualified names of the unit tests, and the values are lists
                of fully qualified names of the functions predicted to be linked to
                the unit test.
            ground_truth_links (Dict[str, List[str]]): A dictionary where the keys are
                the fully qualified names of the unit tests, and the values are lists
                of fully qualified names of the functions that are actually linked
                to the unit test.

        Returns:
            float: The F1 metric score.
        """
        precision = Precision().calculate(predicted_links, ground_truth_links, _)
        recall = Recall().calculate(predicted_links, ground_truth_links, _)

        f1 = 0
        if precision + recall > 0:
            f1 = (2 * precision * recall) / (precision + recall)

        return f1


__all__ = ["F1"]
