from typing import Dict, List, Optional
from pytctracer.config.constants import MetricScoreType
from pytctracer.evaluation.metrics.metric import Metric


class TruePositives(Metric):
    """
    Class implementing the True Positives metric. 
    """
    full_name = "True Positives"
    short_name = "TP"
    arg_name = "tp"
    metric_type = MetricScoreType.INTEGER

    def calculate(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        _: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> int:
        """
        Calculates the number of true positives in the predicted links, which is
        the number of links that were correctly predicted to be linked according
        to the ground truth links.

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
            int: The number of true positives in the predicted links.
        """
        true_positives = 0
        for fully_qualified_test_name in ground_truth_links:
            predicted_links_for_test = set(predicted_links[fully_qualified_test_name])
            ground_truth_links_for_test = set(
                ground_truth_links[fully_qualified_test_name]
            )
            true_positives += len(
                predicted_links_for_test.intersection(ground_truth_links_for_test)
            )

        return true_positives


__all__ = ["TruePositives"]
