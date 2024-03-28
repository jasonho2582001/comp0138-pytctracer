from typing import List
from .last_call_before_assert import LastCallBeforeAssert
from .levenshtein_distance import LevenshteinDistance
from .longest_common_subsequence import (
    LongestCommonSubsequenceBoth,
    LongestCommonSubsequenceUnit,
)
from .naming_conventions import NamingConventions, NamingConventionsContains
from .tarantula import Tarantula
from .tfidf import TFIDF, TFIDFMultiset
from .technique import Technique
from .combined import Combined


class ArgNameToTechniqueMapper:
    def __init__(self):
        self._arg_name_to_technique = {
            LevenshteinDistance.arg_name: LevenshteinDistance,
            NamingConventions.arg_name: NamingConventions,
            NamingConventionsContains.arg_name: NamingConventionsContains,
            LastCallBeforeAssert.arg_name: LastCallBeforeAssert,
            LongestCommonSubsequenceBoth.arg_name: LongestCommonSubsequenceBoth,
            LongestCommonSubsequenceUnit.arg_name: LongestCommonSubsequenceUnit,
            Tarantula.arg_name: Tarantula,
            TFIDF.arg_name: TFIDF,
            TFIDFMultiset.arg_name: TFIDFMultiset,
            Combined.arg_name: Combined,
        }
        self._arg_name_to_full_name = {
            LevenshteinDistance.arg_name: LevenshteinDistance.full_name,
            NamingConventions.arg_name: NamingConventions.full_name,
            NamingConventionsContains.arg_name: NamingConventionsContains.full_name,
            LastCallBeforeAssert.arg_name: LastCallBeforeAssert.full_name,
            LongestCommonSubsequenceBoth.arg_name: LongestCommonSubsequenceBoth.full_name,
            LongestCommonSubsequenceUnit.arg_name: LongestCommonSubsequenceUnit.full_name,
            Tarantula.arg_name: Tarantula.full_name,
            TFIDF.arg_name: TFIDF.full_name,
            TFIDFMultiset.arg_name: TFIDFMultiset.full_name,
            Combined.arg_name: Combined.full_name,
        }
        self._arg_name_to_short_name = {
            LevenshteinDistance.arg_name: LevenshteinDistance.short_name,
            NamingConventions.arg_name: NamingConventions.short_name,
            NamingConventionsContains.arg_name: NamingConventionsContains.short_name,
            LastCallBeforeAssert.arg_name: LastCallBeforeAssert.short_name,
            LongestCommonSubsequenceBoth.arg_name: LongestCommonSubsequenceBoth.short_name,
            LongestCommonSubsequenceUnit.arg_name: LongestCommonSubsequenceUnit.short_name,
            Tarantula.arg_name: Tarantula.short_name,
            TFIDF.arg_name: TFIDF.short_name,
            TFIDFMultiset.arg_name: TFIDFMultiset.short_name,
            Combined.arg_name: Combined.short_name,
        }
        self._arg_names = list(self._arg_name_to_technique.keys())

    def get_arg_names(self) -> List[str]:
        return self._arg_names

    def get_technique(self, arg_name: str) -> Technique:
        if arg_name not in self._arg_name_to_technique:
            raise ValueError(
                f"Invalid technique arg name: {arg_name} for retrieving technique class."
            )

        return self._arg_name_to_technique[arg_name]

    def get_full_name(self, arg_name: str) -> Technique:
        if arg_name not in self._self._arg_name_to_full_name:
            raise ValueError(
                f"Invalid technique arg name: {arg_name} for retrieving full name."
            )

        return self._arg_name_to_full_name[arg_name]

    def get_short_name(self, arg_name: str) -> Technique:
        if arg_name not in self._arg_name_to_short_name:
            raise ValueError(
                f"Invalid technique arg name: {arg_name} for retrieving short name."
            )

        return self._arg_name_to_short_name[arg_name]


__all__ = ["ArgNameToTechniqueMapper"]
