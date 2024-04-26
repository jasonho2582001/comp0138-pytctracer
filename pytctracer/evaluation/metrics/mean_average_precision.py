from typing import Dict, List, Optional
from pytctracer.config.constants import MetricScoreType
from pytctracer.evaluation.metrics.metric import Metric


class MeanAveragePrecision(Metric):
    """
    Class implementing the Mean Average Precision (mAP) metric.
    """
    full_name = "Mean Average Precision"
    short_name = "MAP"
    arg_name = "map"
    metric_type = MetricScoreType.CONTINUOUS

    def calculate(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        _: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> float:
        """
        Calculate the Mean Average Precision (mAP) metric score given 
        the predicted links and ground truth links.

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
            float: The Mean Average Precision (mAP) metric score.
        """
        total_ap = 0

        for fully_qualified_test_name in ground_truth_links:
            ground_truth_links_for_test = set(
                ground_truth_links[fully_qualified_test_name]
            )
            predicted_links_for_test = predicted_links[fully_qualified_test_name]

            count_true_links = 0
            sum_precisions = 0

            for i, link in enumerate(predicted_links_for_test):
                if link in ground_truth_links_for_test:
                    count_true_links += 1

                    # Calculate precision at this rank and add to sum of precisions
                    precision = count_true_links / (i + 1)
                    sum_precisions += precision

            ap = sum_precisions / len(ground_truth_links_for_test)
            total_ap += ap

        # Calculate MAP
        map_score = total_ap / len(ground_truth_links)

        return map_score


__all__ = ["MeanAveragePrecision"]
