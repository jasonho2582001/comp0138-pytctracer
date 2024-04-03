from typing import Dict, Union, List, Tuple, Set
from math import log
from collections import defaultdict
from pytctracer.techniques.technique import Technique
from pytctracer.config.constants import TechniqueParameter, TechniqueThreshold


class TFIDF(Technique):
    """
    Class implementing the TF-IDF
    traceability technique.
    """

    full_name = "TF-IDF"
    short_name = "TF-IDF"
    arg_name = "tfidf"
    description = "TBC"
    required_parameters = {
        TechniqueParameter.FUNCTION_NAMES_TUPLE,
        TechniqueParameter.TEST_NAMES_TUPLE,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TESTS,
        TechniqueParameter.TESTS_THAT_CALL_FUNCTIONS,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_DEPTH,
    }
    uses_threshold = True
    threshold = TechniqueThreshold.THRESHOLD_FOR_TFIDF
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
        Invokes the TF-IDF traceability technique
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

            tests_that_call_functions (Dict[str, Set[str]]): A dictionary
            where the keys are the fully qualified names of the function or
            function classes, and the values are sets containing the fully
            qualified names of each test or test class that invokes the
            function or function class.

        Returns:
            Dict[str, Dict[str, Union[int, float]]]: A dictionary where the
            keys are the fully qualified names of the test or test classes,
            and the values are dictionaries containing the traceability scores
            for each function or function class.
        """
        tfidf_scores = defaultdict(dict)
        idf_scores = {}
        number_of_tests = len(test_names_tuple)

        for fully_qualified_function_name in tests_that_call_functions:
            idf_scores[fully_qualified_function_name] = self._compute_idf_score(
                fully_qualified_function_name,
                tests_that_call_functions,
                number_of_tests,
            )

        for fully_qualified_test_name, _ in test_names_tuple:
            functions_called_by_test = functions_called_by_tests[
                fully_qualified_test_name
            ]
            tf_score = self._compute_tf_score(
                fully_qualified_test_name, functions_called_by_tests
            )
            for fully_qualified_function_name, _ in function_names_tuple:
                tfidf_scores[fully_qualified_test_name][
                    fully_qualified_function_name
                ] = 0
                if fully_qualified_function_name in functions_called_by_test:
                    tfidf_scores[fully_qualified_test_name][
                        fully_qualified_function_name
                    ] = (tf_score * idf_scores[fully_qualified_function_name])

        if self.call_depth_discount:
            tfidf_scores = self._use_call_depth_discounting_dict(
                tfidf_scores, functions_called_by_test_depth
            )
        if self.normalise:
            tfidf_scores = self._normalise_dict(tfidf_scores)

        return tfidf_scores

    def _compute_tf_score(
        self,
        fully_qualified_test_name: str,
        functions_called_by_tests: Dict[str, Set[str]],
    ) -> float:
        number_of_functions_called_by_test = len(
            functions_called_by_tests[fully_qualified_test_name]
        )

        tf_score = (
            log(1 + 1 / (number_of_functions_called_by_test))
            if number_of_functions_called_by_test > 0
            else 0
        )

        return tf_score

    def _compute_idf_score(
        self,
        fully_qualified_function_name: str,
        tests_that_call_functions: Dict[str, Set[str]],
        number_of_tests: int,
    ) -> float:
        number_of_tests_that_call_function = len(
            tests_that_call_functions[fully_qualified_function_name]
        )

        idf_score = (
            log(1 + number_of_tests / (number_of_tests_that_call_function))
            if number_of_tests_that_call_function > 0
            else 0
        )

        return idf_score


class TFIDFMultiset(TFIDF):
    """
    Class implementing the TF-IDF
    traceability technique.
    """

    full_name = "TF-IDF (Multiset)"
    short_name = "TF-IDF*"
    description = "TBC"
    arg_name = "tfidf_multiset"
    required_parameters = {
        TechniqueParameter.FUNCTION_NAMES_TUPLE,
        TechniqueParameter.TEST_NAMES_TUPLE,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_COUNT,
        TechniqueParameter.TESTS_THAT_CALL_FUNCTIONS,
        TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_DEPTH,
    }
    threshold = TechniqueThreshold.THRESHOLD_FOR_TFIDF_MULTISET

    def run(
        self,
        function_names_tuple: List[Tuple[str, str]],
        test_names_tuple: List[Tuple[str, str]],
        functions_called_by_test_count: Dict[str, Dict[str, int]],
        tests_that_call_functions: Dict[str, Set[str]],
        functions_called_by_test_depth: Dict[str, Dict[str, int]],
    ) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Invokes the TF-IDF traceability technique
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

            functions_called_by_test_count (Dict[str, Dict[str, int]]): A
            dictionary where the keys are the fully qualified names of the function or
            function classes, and the values are dictionaries containing each
            function or function class called by the test or test class and the
            number of times it was called.

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
        tfidf_scores = defaultdict(dict)
        idf_scores = {}
        number_of_tests = len(test_names_tuple)

        for fully_qualified_function_name in tests_that_call_functions:
            idf_scores[fully_qualified_function_name] = self._compute_idf_score(
                fully_qualified_function_name,
                tests_that_call_functions,
                number_of_tests,
            )

        for fully_qualified_test_name, _ in test_names_tuple:
            number_of_functions_called_by_test = sum(
                functions_called_by_test_count[fully_qualified_test_name].values()
            )
            for fully_qualified_function_name, _ in function_names_tuple:
                tfidf_scores[fully_qualified_test_name][
                    fully_qualified_function_name
                ] = 0
                functions_count = functions_called_by_test_count[
                    fully_qualified_test_name
                ]
                if fully_qualified_function_name in functions_count:
                    tf_score = self._compute_tf_multiset_score(
                        fully_qualified_function_name,
                        number_of_functions_called_by_test,
                        functions_count,
                    )
                    tfidf_scores[fully_qualified_test_name][
                        fully_qualified_function_name
                    ] = (tf_score * idf_scores[fully_qualified_function_name])

        if self.call_depth_discount:
            tfidf_scores = self._use_call_depth_discounting_dict(
                tfidf_scores, functions_called_by_test_depth
            )
        if self.normalise:
            tfidf_scores = self._normalise_dict(tfidf_scores)

        return tfidf_scores

    def _compute_tf_multiset_score(
        self,
        fully_qualified_function_name: str,
        number_of_functions_called_by_test: int,
        functions_count: Dict[str, int],
    ) -> float:
        number_of_times_function_called = functions_count[fully_qualified_function_name]

        tf_multiset_score = (
            log(
                1
                + number_of_times_function_called / (number_of_functions_called_by_test)
            )
            if number_of_functions_called_by_test > 0
            else 0
        )

        return tf_multiset_score


__all__ = ["TFIDF", "TFIDFMultiset"]
