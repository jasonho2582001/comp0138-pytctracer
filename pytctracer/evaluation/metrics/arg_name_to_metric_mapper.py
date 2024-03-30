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
        return self._arg_names

    def get_metric(self, arg_name: str) -> Metric:
        if arg_name not in self._arg_name_to_metric:
            raise ValueError(
                f"Invalid evaluation metric arg name: {arg_name} for retriving metric class."
            )

        return self._arg_name_to_metric[arg_name]

    def get_full_name(self, arg_name: str) -> Metric:
        if arg_name not in self._self._arg_name_to_full_name:
            raise ValueError(
                f"Invalid evaluation metric arg name: {arg_name} for retrieving full name."
            )

        return self._arg_name_to_full_name[arg_name]

    def get_short_name(self, arg_name: str) -> Metric:
        if arg_name not in self._arg_name_to_short_name:
            raise ValueError(
                f"Invalid evaluation metric arg name: {arg_name} for retrieving short name."
            )

        return self._arg_name_to_short_name[arg_name]


__all__ = ["ArgNameToMetricMapper"]
