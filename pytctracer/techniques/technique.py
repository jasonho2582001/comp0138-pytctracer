from collections import defaultdict
from copy import deepcopy
from abc import ABC, abstractmethod
from typing import Dict, Union, Set, Optional

DISCOUNT_FACTOR = 0.5
TEST_NAME_PREFIX = "test"
TEST_NAME_PREFIX_UNDERSCORE = "test_"


class Technique(ABC):
    """
    Abstract class for implementing a traceability technique. The Technique class
    provides a common interface for all traceability techniques to implement. It
    features a number of class attributes that subclasses may override to induce
    specific behaviour.

    Attributes:
        full_name (str): The full name of the technique.
        short_name (str): The short name of the technique.
        arg_name (str): The argument name of the technique
        (the string used to invoke the technique through the CLI).
        description (str): A description of the technique.
        required_parameters (Dict[str, str]): A dictionary of required parameters for the technique.
        uses_threshold (bool): A boolean indicating whether the technique uses a threshold.
        threshold (int): The threshold value for the technique.
        normalise (bool): A boolean indicating whether the technique normalises scores.
        call_depth_discount (bool): A boolean indicating whether the technique discounts scores based on call depth.
    """

    full_name = "Technique"
    short_name = "Technique"
    arg_name = "technique"
    description = "An abstract traceability technique."
    required_parameters = {}
    uses_threshold = False
    threshold = 0
    normalise = False
    call_depth_discount = False

    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Abstract method for running the traceability technique to produce trace links.
        """
        raise NotImplementedError(
            "The 'run' method must be implemented by the subclass."
        )

    def _use_call_depth_discounting_dict(
        self,
        traceability_score_dict: Dict[str, Dict[str, float]],
        functions_called_by_test_depth_dict: Dict[str, Dict[str, int]],
    ) -> Dict[str, Dict[str, float]]:
        discounted_score_dict = deepcopy(traceability_score_dict)

        for fully_qualified_test_name, _ in discounted_score_dict.items():
            for function_fully_qualified_name in functions_called_by_test_depth_dict[
                fully_qualified_test_name
            ]:
                original_score = discounted_score_dict[fully_qualified_test_name][
                    function_fully_qualified_name
                ]
                depth = functions_called_by_test_depth_dict[fully_qualified_test_name][
                    function_fully_qualified_name
                ]
                discounted_score_dict[fully_qualified_test_name][
                    function_fully_qualified_name
                ] = original_score * DISCOUNT_FACTOR ** (depth - 1)

        return discounted_score_dict

    def _normalise_dict(
        self, traceability_score_dict: Dict[str, Dict[str, float]]
    ) -> Dict[str, Dict[str, float]]:
        normalised_score_dict = deepcopy(traceability_score_dict)

        for test_fully_qualified_name in traceability_score_dict:
            # find maximum score and normalise w.r.t to it
            functions_called_by_test = traceability_score_dict[
                test_fully_qualified_name
            ]
            max_score = 0
            for function_fully_qualified_name in functions_called_by_test:
                max_score = max(
                    max_score,
                    traceability_score_dict[test_fully_qualified_name][
                        function_fully_qualified_name
                    ],
                )

            for function_fully_qualified_name in functions_called_by_test:
                if max_score > 0:
                    normalised_score_dict[test_fully_qualified_name][
                        function_fully_qualified_name
                    ] /= max_score

        return normalised_score_dict

    def generate_predicted_links(
        self,
        traceability_score_dict: Dict[str, Dict[str, float]],
        tests_to_create_links_for: Optional[Set[str]] = None,
    ) -> Dict[str, Set[str]]:
        """
        Takes a dictionary traceability scores for each test and source code pair,
        and returns a dictionary of predicted links for each test. The predicted links
        are generated either using a threshold value, or from binary classification
        depending on the technique.

        Args:
            traceability_score_dict (Dict[str, Dict[str, float]]): A dictionary of traceability
                scores for each test and source code pair.
            tests_to_create_links_for (Optional[Set[str]], optional): A set of test names to
                generate links for. If None, links will be generated for all tests. Defaults to None.

        Returns:
            Dict[str, Set[str]]: A dictionary of predicted links for each test.
        """
        if not tests_to_create_links_for:
            tests_to_create_links_for = set(traceability_score_dict.keys())

        predicted_links_dict = defaultdict(list)

        for (
            fully_qualified_test_name,
            results_for_test_dict,
        ) in traceability_score_dict.items():
            predicted_functions_and_score = []

            if fully_qualified_test_name in tests_to_create_links_for:
                for (
                    fully_qualified_function_name,
                    score,
                ) in results_for_test_dict.items():
                    if (not self.uses_threshold and score == 1) or (
                        self.uses_threshold and score >= self.threshold
                    ):
                        predicted_functions_and_score.append(
                            (fully_qualified_function_name, score)
                        )
                predicted_functions_and_score.sort(key=lambda x: x[1], reverse=True)
                predicted_functions_for_test = [
                    function_name for function_name, _ in predicted_functions_and_score
                ]
                predicted_links_dict[fully_qualified_test_name] = (
                    predicted_functions_for_test
                )

        return predicted_links_dict

    def _strip_test_name(self, test_name: str) -> str:
        # Use lowercase since test class may be PascalCase by convention.

        lower_test_name = test_name.lower()
        if lower_test_name.startswith(TEST_NAME_PREFIX_UNDERSCORE):
            stripped_test_name = test_name[len(TEST_NAME_PREFIX_UNDERSCORE) :]
        elif lower_test_name.startswith(TEST_NAME_PREFIX):
            # Assumption that all test functions must begin with `test'
            stripped_test_name = test_name[len(TEST_NAME_PREFIX) :]
        else:
            stripped_test_name = test_name

        return stripped_test_name


__all__ = ["Technique"]
