from typing import Dict, List
from collections import defaultdict
from pytctracer.config.constants import ClassificationType


def classify_predictions(
    predicted_links: Dict[str, List[str]], ground_truth_links: Dict[str, List[str]]
) -> Dict[str, Dict[str, List[str]]]:
    """
    Takes a dictionary of predicted links and a dictionary of ground truth links
    and classifies the predictions into true positives, false positives, and
    false negatives.

    Args:
        predicted_links (Dict[str, List[str]]): A dictionary where the keys are
            the fully qualified names of the unit tests, and the values are lists
            of fully qualified names of the functions predicted to be linked to
            the unit test.
        ground_truth_links (Dict[str, List[str]]): A dictionary where the keys are
            the fully qualified names of the unit tests, and the values are lists
            of fully qualified names of the functions that are actually linked
            to the unit test.
        
    Returns:
        Dict[str, Dict[str, List[str]]]: A dictionary where the keys are the fully
        qualified names of the unit tests, and the values are dictionaries
        containing the true positives, false positives, and false negatives for
        each unit test.
    """
    classification_dict = defaultdict(dict)

    for fully_qualified_test_name in ground_truth_links:
        predicted_links_for_test = set(predicted_links[fully_qualified_test_name])
        ground_truth_links_for_test = set(ground_truth_links[fully_qualified_test_name])

        true_positive_set = predicted_links_for_test.intersection(
            ground_truth_links_for_test
        )
        false_positive_set = predicted_links_for_test - ground_truth_links_for_test
        false_negatives_set = ground_truth_links_for_test - predicted_links_for_test

        classification_dict[fully_qualified_test_name][
            ClassificationType.TRUE_POSITIVES
        ] = list(true_positive_set)
        classification_dict[fully_qualified_test_name][
            ClassificationType.FALSE_POSITIVES
        ] = list(false_positive_set)
        classification_dict[fully_qualified_test_name][
            ClassificationType.FALSE_NEGATIVES
        ] = list(false_negatives_set)

    return classification_dict


__all__ = ["classify_predictions"]
