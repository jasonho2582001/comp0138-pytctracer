from typing import Dict, Union, List, Tuple, Set
from collections import defaultdict
from pytctracer.techniques.technique import Technique
from pytctracer.config.constants import TechniqueParameter, TechniqueThreshold


class Tarantula(Technique):
    """
    Class implementing the Tarantula
    traceability technique.
    """

    full_name = "Tarantula"
    short_name = "Tarantula"
    description = "TBC"
    arg_name = "tarantula"
    required_parameters = {
        TechniqueParameter.FUNCTION_NAMES_TUPLE,
        TechniqueParameter.TEST_NAMES_TUPLE,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TESTS,
        TechniqueParameter.TESTS_THAT_CALL_FUNCTIONS,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_DEPTH,
    }
    uses_threshold = True
    threshold = TechniqueThreshold.THRESHOLD_FOR_TARANTULA
    normalise = True
    call_depth_discount = True

    def run(
        self,
        function_names_tuple: List[Tuple[str, str]],
        test_names_tuple: List[Tuple[str, str]],
        functions_called_by_tests: Dict[str, Set[str]],
        tests_that_call_functions: Dict[str, Set[str]],
        functions_called_by_test_depth: Dict[str, Dict[str, int]],
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Invokes the Tarantula traceability technique
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
            where the keys are the fully qualified names of the test or
            test classes, and the values are sets containing the fully
            qualified names of each function or function class that the
            test invokes.

            tests_that_call_functions (Dict[str, Set[str]]): A dictionary
            where the keys are the fully qualified names of the function or
            function classes, and the values are sets containing each
            test or test class that calls the function or function class

        Returns:
            Dict[str, Dict[str, Union[int, float]]]: A dictionary where the
            keys are the fully qualified names of the test or test classes,
            and the values are dictionaries containing the traceability scores
            for each function or function class.
        """
        tarantula_scores = defaultdict(dict)

        number_of_tests = len(test_names_tuple)

        for fully_qualified_test_name, _ in test_names_tuple:
            functions_called_by_test = functions_called_by_tests[
                fully_qualified_test_name
            ]
            for fully_qualified_function_name, _ in function_names_tuple:
                tarantula_scores[fully_qualified_test_name][
                    fully_qualified_function_name
                ] = 0
                if fully_qualified_function_name in functions_called_by_test:
                    tarantula_scores[fully_qualified_test_name][
                        fully_qualified_function_name
                    ] = self._compute_tarantula_score(
                        fully_qualified_function_name,
                        tests_that_call_functions,
                        number_of_tests,
                    )

        if self.call_depth_discount:
            tarantula_scores = self._use_call_depth_discounting_dict(
                tarantula_scores, functions_called_by_test_depth
            )
        if self.normalise:
            tarantula_scores = self._normalise_dict(tarantula_scores)

        return tarantula_scores

    def _compute_tarantula_score(
        self,
        fully_qualified_function_name: str,
        tests_that_call_functions: Dict[str, Set[str]],
        number_of_tests: int,
    ) -> float:
        number_of_tests_that_call_function = len(
            tests_that_call_functions[fully_qualified_function_name]
        )

        tarantula_score = 1 / (
            ((number_of_tests_that_call_function - 1) / (number_of_tests - 1)) + 1
        )

        return tarantula_score


__all__ = ["Tarantula"]
