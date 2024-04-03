from typing import Dict, Union, List, Tuple, Set
from abc import ABC, abstractmethod
from collections import defaultdict
from pytctracer.techniques.technique import Technique
from pytctracer.config.constants import TechniqueParameter, TechniqueThreshold


class LongestCommonSubsequence(Technique, ABC):
    """
    Parent Class for the LCS-B and LCS-U traceability techniques.
    """

    full_name = "Longest Common Subsequence"
    short_name = "LCS"
    description = "TBC"
    required_parameters = {
        TechniqueParameter.FUNCTION_NAMES_TUPLE,
        TechniqueParameter.TEST_NAMES_TUPLE,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TESTS,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_DEPTH,
    }
    uses_threshold = True
    normalise = True
    call_depth_discount = True

    def run(
        self,
        function_names_tuple: List[Tuple[str, str]],
        test_names_tuple: List[Tuple[str, str]],
        functions_called_by_tests: Dict[str, Set[str]],
        functions_called_by_test_depth: Dict[str, Dict[str, int]],
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Parent method to run an LCS based technique
        to produce traceability scores for each test-to-code pair given.

        Args:
            function_names_tuple (List[Tuple[str, str]]): A list of tuples,
            where the first element of each tuple is the fully qualified
            (full path) name of a function or function class, and the second
            element is the short name of the function or function class.

            test_names_tuple (List[Tuple[str, str]]): A list of tuples,
            where the first element of each tuple is the fully qualified
            (full path) name of a test or test class, and the second element
            is the short name of the test or test class.

            functions_called_by_tests (Dict[str, Set[str]]): A dictionary
            where the keys are the fully qualified names of the test or test
            classes, and the values are sets containing the fully qualified
            names of each function or function class invoked.

        Returns:
            Dict[str, Dict[str, Union[int, float]]]: A dictionary where the
            keys are the fully qualified names of the test or test classes,
            and the values are dictionaries containing the traceability scores
            for each function or function class.
        """
        return self._run(
            function_names_tuple=function_names_tuple,
            test_names_tuple=test_names_tuple,
            functions_called_by_tests=functions_called_by_tests,
            functions_called_by_test_depth=functions_called_by_test_depth,
        )

    def _run(
        self,
        function_names_tuple: List[Tuple[str, str]],
        test_names_tuple: List[Tuple[str, str]],
        functions_called_by_tests: Dict[str, Set[str]],
        functions_called_by_test_depth: Dict[str, Dict[str, int]],
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        lcs_scores = defaultdict(dict)

        for fully_qualified_test_name, test_name in test_names_tuple:
            functions_called_by_test = functions_called_by_tests[
                fully_qualified_test_name
            ]
            for fully_qualified_function_name, function_name in function_names_tuple:
                lcs_scores[fully_qualified_test_name][fully_qualified_function_name] = 0
                if fully_qualified_function_name in functions_called_by_test:
                    lcs_scores[fully_qualified_test_name][
                        fully_qualified_function_name
                    ] = self._compute_lcs_score(function_name, test_name)

        if self.call_depth_discount:
            lcs_scores = self._use_call_depth_discounting_dict(
                lcs_scores, functions_called_by_test_depth
            )

        if self.normalise:
            lcs_scores = self._normalise_dict(lcs_scores)

        return lcs_scores

    @abstractmethod
    def _compute_lcs_score(self, _function_name: str, _test_name: str) -> int:
        raise NotImplementedError(
            """LCS classes must implement this method 
                                  to compute the traceability score"""
        )

    def _compute_lcs(self, function_name: str, test_name: str) -> int:
        m = len(function_name)
        n = len(test_name)
        lcs_matrix = [[0 for _ in range(n + 1)] for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if function_name[i - 1] == test_name[j - 1]:
                    lcs_matrix[i][j] = lcs_matrix[i - 1][j - 1] + 1
                else:
                    lcs_matrix[i][j] = max(lcs_matrix[i - 1][j], lcs_matrix[i][j - 1])

        return lcs_matrix[m][n]


class LongestCommonSubsequenceUnit(LongestCommonSubsequence):
    """
    Class implementing the Longest Common Subsequence - Unit
    traceability technique.
    """

    full_name = "Longest Common Subsequence - Unit"
    short_name = "LCS-U"
    description = "TBC"
    arg_name = "lcsu"
    threshold = TechniqueThreshold.THRESHOLD_FOR_LCSU

    def run(
        self,
        function_names_tuple: List[Tuple[str, str]],
        test_names_tuple: List[Tuple[str, str]],
        functions_called_by_tests: Dict[str, Set[str]],
        functions_called_by_test_depth: Dict[str, Dict[str, int]],
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Invokes the Longest Common Subsequence - Unit traceability technique
        to produce traceability scores for each test-to-code pair given.

        Args:
            function_names_tuple (List[Tuple[str, str]]): A list of tuples,
            where the first element of each tuple is the fully qualified
            (full path) name of a function or function class, and the second
            element is the short name of the function or function class.

            test_names_tuple (List[Tuple[str, str]]): A list of tuples,
            where the first element of each tuple is the fully qualified
            (full path) name of a test or test class, and the second element
            is the short name of the test or test class.

            functions_called_by_tests (Dict[str, Set[str]]): A dictionary
            where the keys are the fully qualified names of the test or test
            classes, and the values are sets containing the fully qualified
            names of each function or function class invoked.

        Returns:
            Dict[str, Dict[str, Union[int, float]]]: A dictionary where the
            keys are the fully qualified names of the test or test classes,
            and the values are dictionaries containing the traceability scores
            for each function or function class.
        """
        return self._run(
            function_names_tuple=function_names_tuple,
            test_names_tuple=test_names_tuple,
            functions_called_by_tests=functions_called_by_tests,
            functions_called_by_test_depth=functions_called_by_test_depth,
        )

    def _compute_lcs_score(self, function_name: str, test_name: str) -> int:
        stripped_test_name = self._strip_test_name(test_name)

        lcsu_score = (self._compute_lcs(stripped_test_name, function_name)) / len(
            function_name
        )

        return lcsu_score


class LongestCommonSubsequenceBoth(LongestCommonSubsequence):
    """
    Class implementing the Longest Common Subsequence - Bpth
    traceability technique.
    """

    full_name = "Longest Common Subsequence - Both"
    short_name = "LCS-B"
    arg_name = "lcsb"
    description = "TBC"
    threshold = TechniqueThreshold.THRESHOLD_FOR_LCSB

    def run(
        self,
        function_names_tuple: List[Tuple[str, str]],
        test_names_tuple: List[Tuple[str, str]],
        functions_called_by_tests: Dict[str, Set[str]],
        functions_called_by_test_depth: Dict[str, Dict[str, int]],
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Invokes the Longest Common Subsequence - Both traceability technique
        to produce traceability scores for each test-to-code pair given.

        Args:
            function_names_tuple (List[Tuple[str, str]]): A list of tuples,
            where the first element of each tuple is the fully qualified
            (full path) name of a function or function class, and the second
            element is the short name of the function or function class.

            test_names_tuple (List[Tuple[str, str]]): A list of tuples,
            where the first element of each tuple is the fully qualified
            (full path) name of a test or test class, and the second element
            is the short name of the test or test class.

            functions_called_by_tests (Dict[str, Set[str]]): A dictionary
            where the keys are the fully qualified names of the test or test
            classes, and the values are sets containing the fully qualified
            names of each function or function class invoked.

        Returns:
            Dict[str, Dict[str, Union[int, float]]]: A dictionary where the
            keys are the fully qualified names of the test or test classes,
            and the values are dictionaries containing the traceability scores
            for each function or function class.
        """
        return self._run(
            function_names_tuple=function_names_tuple,
            test_names_tuple=test_names_tuple,
            functions_called_by_tests=functions_called_by_tests,
            functions_called_by_test_depth=functions_called_by_test_depth,
        )

    def _compute_lcs_score(self, function_name: str, test_name: str) -> int:
        stripped_test_name = self._strip_test_name(test_name)

        lcsb_score = (self._compute_lcs(stripped_test_name, function_name)) / (
            max(len(stripped_test_name), len(function_name))
        )

        return lcsb_score


__all__ = [
    "LongestCommonSubsequenceUnit",
    "LongestCommonSubsequenceBoth",
    "LongestCommonSubsequence",
]
