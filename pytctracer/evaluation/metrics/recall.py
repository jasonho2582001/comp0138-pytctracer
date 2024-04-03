from typing import Dict, List, Optional
from pytctracer.config.constants import MetricScoreType
from pytctracer.evaluation.metrics.metric import Metric
from pytctracer.evaluation.metrics.false_negatives import FalseNegatives
from pytctracer.evaluation.metrics.true_positives import TruePositives


class Recall(Metric):
    full_name = "Recall"
    short_name = "Recall"
    arg_name = "recall"
    metric_type = MetricScoreType.CONTINUOUS

    def calculate(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        _: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> float:
        true_positives = TruePositives().calculate(
            predicted_links, ground_truth_links, _
        )
        false_negatives = FalseNegatives().calculate(
            predicted_links, ground_truth_links, _
        )

        recall = 1
        if true_positives + false_negatives > 0:
            recall = true_positives / (true_positives + false_negatives)

        return recall


__all__ = ["Recall"]
