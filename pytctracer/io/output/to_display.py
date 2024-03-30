from typing import Dict, Set, List


def display_evaluation_results(
    evaluation_metric_dict: Dict[str, Dict[str, float]], title: str
) -> None:
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
