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
    """
    Evaluate the predicted links using the selected metrics against the ground
    truth links.

    Args:
        predicted_links (Dict[str, List[str]]): A dictionary where the keys are
            the fully qualified names of the unit tests, and the values are lists
            of fully qualified names of the functions predicted to be linked to
            the unit test.
        ground_truth_links (Dict[str, List[str]]): A dictionary where the keys are
            the fully qualified names of the unit tests, and the values are lists
            of fully qualified names of the functions that are actually linked
            to the unit test.
        selected_metrics (List[Metric]): A list of Metric objects to evaluate the
            predicted links.
        traceability_score_dict (Optional[Dict[str, Dict[str, float]], optional): A dictionary
            of traceability scores for each test and source code pair. Defaults to None.
        metric_as_percentage (bool, optional): Whether to report continous metrics as
            percentages. If omitted, metrics are reported as raw values by default.
            Defaults to False.
        uses_threshold (bool, optional): Whether the technique uses a threshold value
            to generate predicted links (Used if an evaluation is for predictions generated
            from a technique class). Defaults to True.

    Returns:
        Dict[str, float]: A dictionary where the keys are the argument names of the
            selected metrics, and the values are the scores for the metrics.
    """
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
