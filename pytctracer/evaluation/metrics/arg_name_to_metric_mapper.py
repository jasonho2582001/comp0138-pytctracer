from typing import List
from .area_under_curve import AreaUnderCurve
from .f1 import F1
from .false_negatives import FalseNegatives
from .false_positives import FalsePositives
from .mean_average_precision import MeanAveragePrecision
from .precision import Precision
from .recall import Recall
from .true_positives import TruePositives
from .metric import Metric


class ArgNameToMetricMapper:
    """
    Class providing mappings between the argument name of each metric to
    some relevant properties, including the metric's class, full name and
    short name.
    """
    def __init__(self):
        self._arg_name_to_metric = {
            Precision.arg_name: Precision,
            Recall.arg_name: Recall,
            F1.arg_name: F1,
            MeanAveragePrecision.arg_name: MeanAveragePrecision,
            AreaUnderCurve.arg_name: AreaUnderCurve,
            TruePositives.arg_name: TruePositives,
            FalsePositives.arg_name: FalsePositives,
            FalseNegatives.arg_name: FalseNegatives,
        }
        self._arg_name_to_full_name = {
            MeanAveragePrecision.arg_name: MeanAveragePrecision.full_name,
            Precision.arg_name: Precision.full_name,
            Recall.arg_name: Recall.full_name,
            F1.arg_name: F1.full_name,
            AreaUnderCurve.arg_name: AreaUnderCurve.full_name,
            TruePositives.arg_name: TruePositives.full_name,
            FalsePositives.arg_name: FalsePositives.full_name,
            FalseNegatives.arg_name: FalseNegatives.full_name,
        }
        self._arg_name_to_short_name = {
            MeanAveragePrecision.arg_name: MeanAveragePrecision.short_name,
            Precision.arg_name: Precision.short_name,
            Recall.arg_name: Recall.short_name,
            F1.arg_name: F1.short_name,
            AreaUnderCurve.arg_name: AreaUnderCurve.short_name,
            TruePositives.arg_name: TruePositives.short_name,
            FalsePositives.arg_name: FalsePositives.short_name,
            FalseNegatives.arg_name: FalseNegatives.short_name,
        }
        self._arg_names = list(self._arg_name_to_metric.keys())

    def get_arg_names(self) -> List[str]:
        """
        Return the list of valid metric argument names.

        Returns:
            List[str]: List of valid metric argument names.
        """
        return self._arg_names

    def get_metric(self, arg_name: str) -> Metric:
        """
        Return the metric class corresponding to the given argument name.

        Args:
            arg_name (str): The argument name of the metric.

        Returns:
            Metric: The metric class corresponding to the given argument name.
        """
        if arg_name not in self._arg_name_to_metric:
            raise ValueError(
                f"Invalid evaluation metric arg name: {arg_name} for retriving metric class."
            )

        return self._arg_name_to_metric[arg_name]

    def get_full_name(self, arg_name: str) -> Metric:
        """
        Get the full name of the metric corresponding to the given argument name.

        Args:
            arg_name (str): The argument name of the metric.
        
        Returns:
            Metric: The full name of the metric corresponding to the given argument name.
        """
        if arg_name not in self._self._arg_name_to_full_name:
            raise ValueError(
                f"Invalid evaluation metric arg name: {arg_name} for retrieving full name."
            )

        return self._arg_name_to_full_name[arg_name]

    def get_short_name(self, arg_name: str) -> Metric:
        """
        Get the short name of the metric corresponding to the given argument name.

        Args:
            arg_name (str): The argument name of the metric.

        Returns:
            Metric: The short name of the metric corresponding to the given argument name.
        """
        if arg_name not in self._arg_name_to_short_name:
            raise ValueError(
                f"Invalid evaluation metric arg name: {arg_name} for retrieving short name."
            )

        return self._arg_name_to_short_name[arg_name]


__all__ = ["ArgNameToMetricMapper"]
