from typing import Dict, List, Optional
from pytctracer.config.constants import MetricScoreType
from pytctracer.evaluation.metrics.metric import Metric
from pytctracer.evaluation.metrics.false_positives import FalsePositives
from pytctracer.evaluation.metrics.true_positives import TruePositives


class Precision(Metric):
    full_name = "Precision"
    short_name = "Precision"
    arg_name = "precision"
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
        false_positives = FalsePositives().calculate(
            predicted_links, ground_truth_links, _
        )

        precision = 1
        if true_positives + false_positives > 0:
            precision = true_positives / (true_positives + false_positives)

        return precision


__all__ = ["Precision"]
