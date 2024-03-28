from abc import ABC, abstractmethod
from typing import Dict, List
from src.config.constants import MetricScoreTypes


class Metric(ABC):
    full_name = "Metric"
    short_name = "Metric"
    arg_name = "metric"
    metric_type = MetricScoreTypes.NA

    @abstractmethod
    def calculate(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
        traceability_score_dict: Dict[str, Dict[str, float]],
        to_percentage: bool = False,
    ) -> float:
        raise NotImplementedError(
            "The 'calculate' method must be implemented by the subclass."
        )

    def to_percentage(self, decimal: float) -> float:
        return decimal * 100
