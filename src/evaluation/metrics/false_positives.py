from typing import Dict, List
from src.config.constants import MetricScoreTypes
from src.evaluation.metrics.metric import Metric


class FalsePositives(Metric):
    full_name = "False Positives"
    short_name = "FN"
    arg_name = "fp"
    metric_type = MetricScoreTypes.INTEGER

    def calculate(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        _: Dict[str, Dict[str, float]],
    ) -> float:
        false_positives = 0
        for fully_qualified_test_name in predicted_links:
            predicted_links_for_test = set(predicted_links[fully_qualified_test_name])
            ground_truth_links_for_test = set(
                ground_truth_links[fully_qualified_test_name]
            )
            false_positives += len(
                predicted_links_for_test - ground_truth_links_for_test
            )

        return false_positives


__all__ = ["FalsePositives"]
