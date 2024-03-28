from typing import Dict
from collections import defaultdict
from src.techniques import Technique
from src.config.constants import TechniqueThresholds


class Combined(Technique):
    """
    Class implementing the Combined
    traceability technique.
    """

    full_name = "Combined (Simple Average)"
    short_name = "Combined"
    arg_name = "combined"
    description = "TBC"
    required_parameters = {}
    uses_threshold = True
    threshold = TechniqueThresholds.THRESHOLD_FOR_COMBINED
    normalise = True

    def run(
        self, traceability_scores_for_techniques: Dict[str, Dict[str, Dict[str, float]]]
    ) -> Dict[str, Dict[str, float]]:
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
