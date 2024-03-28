from typing import Dict, List
from collections import defaultdict
from src.config.constants import ClassificationTypes


def classify_predictions(
    predicted_links: Dict[str, List[str]], ground_truth_links: Dict[str, List[str]]
) -> Dict[str, Dict[str, List[str]]]:
    classification_dict = defaultdict(dict)

    for fully_qualified_test_name in predicted_links:
        predicted_links_for_test = set(predicted_links[fully_qualified_test_name])
        ground_truth_links_for_test = set(ground_truth_links[fully_qualified_test_name])

        true_positive_set = predicted_links_for_test.intersection(
            ground_truth_links_for_test
        )
        false_positive_set = predicted_links_for_test - ground_truth_links_for_test
        false_negatives_set = ground_truth_links_for_test - predicted_links_for_test

        classification_dict[fully_qualified_test_name][
            ClassificationTypes.TRUE_POSITIVES
        ] = list(true_positive_set)
        classification_dict[fully_qualified_test_name][
            ClassificationTypes.FALSE_POSITIVES
        ] = list(false_positive_set)
        classification_dict[fully_qualified_test_name][
            ClassificationTypes.FALSE_NEGATIVES
        ] = list(false_negatives_set)

    return classification_dict


__all__ = ["classify_predictions"]
