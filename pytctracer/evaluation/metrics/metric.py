from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from pytctracer.config.constants import MetricScoreType


class Metric(ABC):
    """
    Abstract class for implementing a metric. The Metric class
    provides a common interface for implementing a metric with quantifies
    the performance of a set of predictions. The class provides methods 
    which can be overriden for specific metric implementations.

    Attributes:
        full_name (str): The full name of the metric.
        short_name (str): The short name of the metric.
        arg_name (str): The argument name of the metric
        (the string used to invoke the metric through the CLI).
        metric_type (MetricScoreType): The type of metric score.
    """
    full_name = "Metric"
    short_name = "Metric"
    arg_name = "metric"
    metric_type = MetricScoreType.NA

    @abstractmethod
    def calculate(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        traceability_score_dict: Optional[Dict[str, Dict[str, float]]],
        to_percentage: bool = False,
    ) -> float:
        """
        Abstract method to implement the calculation of the metric score given
        the predicted links, ground truth links, and optionally the traceability
        scores.

        Args:
            predicted_links (Dict[str, List[str]]): A dictionary where the keys are
                the fully qualified names of the unit tests, and the values are lists
                of fully qualified names of the functions predicted to be linked to
                the unit test.
            ground_truth_links (Dict[str, List[str]]): A dictionary where the keys are
                the fully qualified names of the unit tests, and the values are lists
                of fully qualified names of the functions that are actually linked
                to the unit test.
            traceability_score_dict (Optional[Dict[str, Dict[str, float]], optional): A dictionary
                of traceability scores for each test and source code pair. Defaults to None.
            to_percentage (bool, optional): Whether to report the metric as a percentage.
                Defaults to False.
        """
        raise NotImplementedError(
            "The 'calculate' method must be implemented by the subclass."
        )

    def to_percentage(self, decimal: float) -> float:
        """
        Converts decimal scores to percentage scores.

        Args:
            decimal (float): The decimal score to convert to a percentage.
        
        Returns:
            float: The percentage score.
        """
        return decimal * 100
