from typing import Dict
from collections import defaultdict
from pytctracer.techniques.technique import Technique
from pytctracer.config.constants import TechniqueThreshold


class Combined(Technique):
    """
    Class implementing the Combined
    traceability technique. This technique doesn't run any specific
    traceability algorithm, but instead combines the results of other
    techniques through a simple average.

    Attributes:
        full_name (str): The full name of the technique.
        short_name (str): The short name of the technique.
        arg_name (str): The argument name of the technique
        (the string used to invoke the technique through the CLI).
        description (str): A description of the technique.
        required_parameters (Dict[str, str]): A dictionary of 
        required parameters for the technique.
        uses_threshold (bool): A boolean indicating whether the technique 
        uses a threshold.
        threshold (int): The threshold value for the technique.
        normalise (bool): A boolean indicating whether the technique normalises scores.
        call_depth_discount (bool): A boolean indicating whether the technique 
        discounts scores based on call depth.
    """

    full_name = "Combined (Simple Average)"
    short_name = "Combined"
    arg_name = "combined"
    description = "TBC"
    required_parameters = {}
    uses_threshold = True
    threshold = TechniqueThreshold.THRESHOLD_FOR_COMBINED
    normalise = True

    def run(
        self, traceability_scores_for_techniques: Dict[str, Dict[str, Dict[str, float]]]
    ) -> Dict[str, Dict[str, float]]:
        """
        Invokes the Combined traceability technique to produce traceability scores
        for each test-to-code pair given. This simply takes the traceability scores
        for each test-to-code pair from each technique, and produces the simple mean of
        them.

        Args:
            traceability_scores_for_techniques (Dict[str, Dict[str, Dict[str, float]]]): 
            A dictionary where the keys are the names of the techniques, and the values 
            are dictionaries where thekeys are the fully qualified names of the test or 
            test classes, and the values are dictionaries containing the traceability scores
            for each function or function class.
        
        Returns:
            Dict[str, Dict[str, float]]: A dictionary where the keys are the fully qualified
            names of the testor test classes, and the values are dictionaries containing the
            traceability scores for each function or function class.
        """
        number_of_techniques_to_combine = len(traceability_scores_for_techniques)
        combined_scores = None
        for _, traceability_scores in traceability_scores_for_techniques.items():
            if combined_scores is None:
                combined_scores = defaultdict(lambda: defaultdict(float))

            for (
                fully_qualified_test_name,
                function_scores,
            ) in traceability_scores.items():
                for fully_qualified_function_name, score in function_scores.items():
                    combined_scores[fully_qualified_test_name][
                        fully_qualified_function_name
                    ] += (score / number_of_techniques_to_combine)

        if self.normalise:
            combined_scores = self._normalise_dict(combined_scores)

        return combined_scores


__all__ = ["Combined"]
