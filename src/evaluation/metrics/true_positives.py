from typing import Dict, List
from src.config.constants import MetricScoreTypes
from src.evaluation.metrics.metric import Metric


class TruePositives(Metric):
    full_name = "True Positives"
    short_name = "TP"
    arg_name = "tp"
    metric_type = MetricScoreTypes.INTEGER

    def calculate(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        _: Dict[str, Dict[str, float]],
    ) -> float:
        true_positives = 0
        for fully_qualified_test_name in predicted_links:
            predicted_links_for_test = set(predicted_links[fully_qualified_test_name])
            ground_truth_links_for_test = set(
                ground_truth_links[fully_qualified_test_name]
            )
            true_positives += len(
                predicted_links_for_test.intersection(ground_truth_links_for_test)
            )

        return true_positives


__all__ = ["TruePositives"]
