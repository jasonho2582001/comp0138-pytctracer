from typing import Dict, Union, List, Tuple, Set
from collections import defaultdict
from pytctracer.techniques.technique import Technique
from pytctracer.config.constants import TechniqueParameter


class LastCallBeforeAssert(Technique):
    """
    Parent Class implementing the Last Call Before Assert traceability technique.
    """

    full_name = "Last Call Before Assert"
    short_name = "LCBA"
    arg_name = "lcba"
    description = "TBC"
    required_parameters = {
        TechniqueParameter.FUNCTION_NAMES_TUPLE,
        TechniqueParameter.TEST_NAMES_TUPLE,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TESTS,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_BEFORE_ASSERT,
    }

    def run(
        self,
        function_names_tuple: List[Tuple[str, str]],
        test_names_tuple: List[Tuple[str, str]],
        functions_called_by_tests: Dict[str, Set[str]],
        functions_called_by_test_before_assert: Dict[str, Set[str]],
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Invokes the Last Call Before Assert traceability technique to produce
        binary traceability scores for each test-to-code pair given.

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

            functions_called_by_test_before_assert (Dict[str, Set[str]]): A
            dictionary where the keys are the fully qualified names of the test
            or test classes, and the values are sets containing the fully
            qualified names of each function or function class called before
            an assert statement.

        Returns:
            Dict[str, Dict[str, Union[int, float]]]: A dictionary where the
            keys are the fully qualified names of the test or test classes,
            and the values are dictionaries containing the traceability scores
            for each function or function class.
        """
        lcba_scores = defaultdict(dict)

        for fully_qualified_test_name, _ in test_names_tuple:
            functions_called_by_test = functions_called_by_tests[
                fully_qualified_test_name
            ]
            for fully_qualified_function_name, _ in function_names_tuple:
                lcba_scores[fully_qualified_test_name][
                    fully_qualified_function_name
                ] = 0
                if fully_qualified_function_name in functions_called_by_test:
                    lcba_scores[fully_qualified_test_name][
                        fully_qualified_function_name
                    ] = self._compute_lcba_score(
                        fully_qualified_function_name,
                        fully_qualified_test_name,
                        functions_called_by_test_before_assert,
                    )

        return lcba_scores

    def _compute_lcba_score(
        self,
        fully_qualified_function_name: str,
        fully_qualified_test_name: str,
        functions_called_by_test_before_assert: Dict[str, Set[str]],
    ) -> int:
        return (
            1
            if fully_qualified_function_name
            in functions_called_by_test_before_assert[fully_qualified_test_name]
            else 0
        )


__all__ = ["LastCallBeforeAssert"]
