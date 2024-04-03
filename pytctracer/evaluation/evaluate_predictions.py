from typing import Dict, List, Optional
from pytctracer.evaluation.metrics import Metric
from pytctracer.config.constants import MetricScoreType


def evaluate_predictions(
    predicted_links: Dict[str, List[str]],
    ground_truth_links: Dict[str, List[str]],
    selected_metrics: List[Metric],
    traceability_score_dict: Optional[Dict[str, Dict[str, float]]] = None,
    metric_as_percentage: bool = False,
    uses_threshold: bool = True,
) -> Dict[str, float]:
    evaluation_dict = {}
    for metric in selected_metrics:
        if metric.metric_type == MetricScoreType.THRESHOLD_INDEPENDENT and (
            not uses_threshold or traceability_score_dict is None
        ):
            metric_result = 0
        else:
            metric_result = metric.calculate(
                predicted_links, ground_truth_links, traceability_score_dict
            )
            if metric_as_percentage and metric.metric_type in [
                MetricScoreType.CONTINUOUS,
                MetricScoreType.THRESHOLD_INDEPENDENT,
            ]:
                metric_result = metric.to_percentage(metric_result)

        evaluation_dict[metric.arg_name] = metric_result

    return evaluation_dict


__all__ = ["evaluate_predictions"]
