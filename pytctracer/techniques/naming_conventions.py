from typing import Dict, Union, List, Tuple, Set
from collections import defaultdict
from pytctracer.techniques.technique import Technique
from pytctracer.config.constants import TechniqueParameter


class NamingConventions(Technique):
    """
    Class implementing the Naming Conventions traceability technique.
    """

    full_name = "Naming Conventions"
    short_name = "NC"
    description = "TBC"
    arg_name = "nc"
    required_parameters = {
        TechniqueParameter.FUNCTION_NAMES_TUPLE,
        TechniqueParameter.TEST_NAMES_TUPLE,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TESTS,
    }

    def run(
        self,
        function_names_tuple: List[Tuple[str, str]],
        test_names_tuple: List[Tuple[str, str]],
        functions_called_by_tests: Dict[str, Set[str]],
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Invokes the Naming Conventions traceability technique to produce
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
        )

    def _run(
        self,
        function_names_tuple: List[Tuple[str, str]],
        test_names_tuple: List[Tuple[str, str]],
        functions_called_by_tests: Dict[str, Set[str]],
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        nc_scores = defaultdict(dict)

        for fully_qualified_test_name, test_name in test_names_tuple:
            functions_called_by_test = functions_called_by_tests[
                fully_qualified_test_name
            ]
            for fully_qualified_function_name, function_name in function_names_tuple:
                nc_scores[fully_qualified_test_name][fully_qualified_function_name] = 0
                if fully_qualified_function_name in functions_called_by_test:
                    nc_scores[fully_qualified_test_name][
                        fully_qualified_function_name
                    ] = self._compute_nc_score(function_name, test_name)

        return nc_scores

    def _compute_nc_score(self, function_name: str, test_name: str) -> int:
        stripped_test_name = self._strip_test_name(test_name)

        return 1 if function_name == stripped_test_name else 0


class NamingConventionsContains(NamingConventions):
    """
    Class implementing the Naming Conventions traceability technique.
    """

    full_name = "Naming Conventions - Contains"
    short_name = "NCC"
    description = "TBC"
    arg_name = "ncc"
    required_parameters = {
        TechniqueParameter.FUNCTION_NAMES_TUPLE,
        TechniqueParameter.TEST_NAMES_TUPLE,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TESTS,
    }

    def run(
        self,
        function_names_tuple: List[Tuple[str, str]],
        test_names_tuple: List[Tuple[str, str]],
        functions_called_by_tests: Dict[str, Set[str]],
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Invokes the Naming Conventions - Contains traceability technique
        to produce binary traceability scores for each test-to-code pair given.

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
        )

    def _compute_nc_score(self, function_name: str, test_name: str) -> int:
        stripped_test_name = self._strip_test_name(test_name)

        return 1 if function_name in stripped_test_name else 0


__all__ = ["NamingConventions", "NamingConventionsContains"]
