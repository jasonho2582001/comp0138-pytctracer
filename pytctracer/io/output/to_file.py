import json
import csv
from typing import Dict

TECHNIQUE = "Technique"


def write_dict_to_json(
    dict_to_write: Dict[str, Dict[str, str]],
    file_path: str,
    sort_keys: bool = True,
) -> None:
    """
    Write a dictionary to a JSON file.

    Args:
        dict_to_write (Dict[str, Dict[str, str]): The dictionary to write to the JSON file.
        file_path (str): The path to the JSON file to write to.
        sort_keys (bool, optional): Whether to sort the keys in the JSON file. Defaults to True.
    """
    try:
        with open(file_path, "w", encoding="utf8") as file:
            json.dump(dict_to_write, file, indent=4, sort_keys=sort_keys)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at path: {file_path}")

    except:
        raise ValueError(
            f"An error occurred while writing to the JSON file with path: {file_path}."
        )


def write_evaluation_metrics_to_csv(
    combined_evaluation_dict: Dict[str, Dict[str, float]], csv_name: str
) -> None:
    """
    Write the evaluation metrics for the traceability predictions to a CSV file.

    Args:
        combined_evaluation_dict (Dict[str, Dict[str, float]]): A dictionary where the keys are the
        names of the techniques, and the values are dictionaries where the keys are the evaluation
        metrics, and the values are the scores for the metrics.

        csv_name (str): The name of the CSV file to write the evaluation metrics to.
    """
    csv_headers = [TECHNIQUE] + list(list(combined_evaluation_dict.values())[0].keys())
    try:
        with open(csv_name, "w", newline="", encoding="utf8") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
            csv_writer.writeheader()
            for technique, evaluation_dict in combined_evaluation_dict.items():
                row = {TECHNIQUE: technique}
                for metric, score in evaluation_dict.items():
                    row[metric] = (
                        score if not isinstance(score, float) else round(score, 1)
                    )
                csv_writer.writerow(row)

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at path: {csv_name}")

    except:
        raise ValueError(
            f"An error occurred while writing to the CSV file with path: {csv_name}."
        )


__all__ = ["write_classifications_to_json", "write_evaluation_metrics_to_csv"]
