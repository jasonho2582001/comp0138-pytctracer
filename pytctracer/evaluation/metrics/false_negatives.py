from typing import Dict, List, Optional
from pytctracer.config.constants import MetricScoreType
from pytctracer.evaluation.metrics.metric import Metric


class FalseNegatives(Metric):
    full_name = "False Negatives"
    short_name = "FN"
    arg_name = "fn"
    metric_type = MetricScoreType.INTEGER

    def calculate(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        _: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> float:
        false_negatives = 0
        for fully_qualified_test_name in ground_truth_links:
            predicted_links_for_test = set(predicted_links[fully_qualified_test_name])
            ground_truth_links_for_test = set(
                ground_truth_links[fully_qualified_test_name]
            )
            false_negatives += len(
                ground_truth_links_for_test - predicted_links_for_test
            )

        return false_negatives


__all__ = ["FalseNegatives"]
