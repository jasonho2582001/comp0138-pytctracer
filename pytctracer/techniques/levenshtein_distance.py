from typing import Dict, Union, List, Tuple, Set
from collections import defaultdict
from pytctracer.techniques.technique import Technique
from pytctracer.config.constants import TechniqueParameter, TechniqueThreshold


class LevenshteinDistance(Technique):
    """
    Class implementing the Levenshtein
    traceability technique.
    """

    full_name = "Levenshtein Distance"
    short_name = "Leven"
    arg_name = "leven"
    description = "TBC"
    required_parameters = {
        TechniqueParameter.FUNCTION_NAMES_TUPLE,
        TechniqueParameter.TEST_NAMES_TUPLE,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TESTS,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_DEPTH,
    }
    uses_threshold = True
    threshold = TechniqueThreshold.THRESHOLD_FOR_LEVENSHTEIN
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
        Invokes the Levenshtein Distance traceability technique
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
        levenshtein_scores = defaultdict(dict)

        for fully_qualified_test_name, test_name in test_names_tuple:
            functions_called_by_test = functions_called_by_tests[
                fully_qualified_test_name
            ]
            for fully_qualified_function_name, function_name in function_names_tuple:
                levenshtein_scores[fully_qualified_test_name][
                    fully_qualified_function_name
                ] = 0
                if fully_qualified_function_name in functions_called_by_test:
                    levenshtein_scores[fully_qualified_test_name][
                        fully_qualified_function_name
                    ] = self._compute_levenshtein_score(function_name, test_name)

        if self.call_depth_discount:
            levenshtein_scores = self._use_call_depth_discounting_dict(
                levenshtein_scores, functions_called_by_test_depth
            )
        if self.normalise:
            levenshtein_scores = self._normalise_dict(levenshtein_scores)

        return levenshtein_scores

    def _compute_levenshtein_score(self, function_name: str, test_name: str) -> int:
        stripped_test_name = self._strip_test_name(test_name)

        levenshtein_score = 1 - (
            self._compute_levenshtein(function_name, stripped_test_name)
        ) / (max(len(stripped_test_name), len(function_name)))

        return levenshtein_score

    def _compute_levenshtein(self, function_name: str, test_name: str) -> int:
        m = len(function_name)
        n = len(test_name)
        edit_distance_matrix = [[0 for _ in range(n + 1)] for _ in range(m + 1)]

        for i in range(n + 1):
            edit_distance_matrix[0][i] = i

        for j in range(m + 1):
            edit_distance_matrix[j][0] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                edit_distance_matrix[i][j] = min(
                    edit_distance_matrix[i][j - 1] + 1,
                    edit_distance_matrix[i - 1][j] + 1,
                    edit_distance_matrix[i - 1][j - 1]
                    + (1 if function_name[i - 1] != test_name[j - 1] else 0),
                )

        return edit_distance_matrix[m][n]


__all__ = ["LevenshteinDistance"]
