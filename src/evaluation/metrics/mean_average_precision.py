from typing import Dict, List
from src.config.constants import MetricScoreTypes
from src.evaluation.metrics.metric import Metric


class MeanAveragePrecision(Metric):
    full_name = "Mean Average Precision"
    short_name = "MAP"
    arg_name = "map"
    metric_type = MetricScoreTypes.CONTINUOUS

    def calculate(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        _: Dict[str, Dict[str, float]],
    ) -> float:
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
