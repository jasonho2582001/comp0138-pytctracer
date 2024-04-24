from typing import Dict, Set, List


def display_evaluation_results(
    evaluation_metric_dict: Dict[str, Dict[str, float]], title: str
) -> None:
    """
    Display the evaluation metric results for each technique. Each technique will be
    displayed with the evaluation metrics and their scores.

    Args:
        evaluation_metric_dict (Dict[str, Dict[str, float]]): A dictionary where the keys
        are the names of the techniques, and the values are dictionaries where the keys are
        the evaluation metrics, and the values are the scores for the metrics.

        title (str): The title of the evaluation results.
    """
    print(f"{'='*15} {title} {'='*15}\n")
    for technique, evaluation_dict in evaluation_metric_dict.items():
        print(f"{'='*5} {technique} {'='*5}")
        for metric, score in evaluation_dict.items():
            if isinstance(score, float):
                print(f"{metric}: {score:.5f}")
            else:
                print(f"{metric}: {score}")
        print("\n")
    print("=" * 50 + "\n\n")


def display_predicted_links(predicted_links: Dict[str, Set[str]], title: str) -> None:
    """
    Display the predicted links for each test. Each test will be displayed with the
    functions predicted to be linked to the test.

    Args:
        predicted_links (Dict[str, Set[str]]): A dictionary where the keys are the test names,
        and the values are sets containing the function names predicted to be linked to the test.

        title (str): The title of the predicted links.
    """
    print(f"{'='*15} {title} {'='*15}\n")

    for test, predicted_links_for_test in predicted_links.items():
        print(f"{'='*5} {test} {'='*5}")
        i = 1
        for function_name in predicted_links_for_test:
            print(f"{str(i).ljust(3)}: {function_name}")
            i += 1
        print("\n")

    print("=" * 50 + "\n")


def display_classifications(
    classifications: Dict[str, Dict[str, List[str]]], title: str
) -> None:
    """
    Display the prediction classifications for each test. Each test will be
    displayed with the functions classified as True Positives, False Positives,
    and False Negatives.

    Args:
        classifications (Dict[str, Dict[str, List[str]]]): A dictionary where the keys
        are the test names, and the values are dictionaries where the keys are the
        classification types, and the values are lists of the function names classified
        as that type.

        title (str): The title of the classification results.
    """
    print(f"{'='*15} {title} {'='*15}\n")

    for test, classifications_for_test in classifications.items():
        print(f"{'='*5} {test} {'='*5}")
        for classification_type, function_list in classifications_for_test.items():
            print(f"{classification_type}:")
            i = 1
            for function_name in function_list:
                print(f"{str(i).ljust(3)}: {function_name}")
                i += 1
            print("\n")
        print("\n")

    print("=" * 50 + "\n")


__all__ = [
    "display_evaluation_results",
    "display_predicted_links",
    "display_classifications",
]
