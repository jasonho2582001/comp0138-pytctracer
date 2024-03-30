import json
import csv
from typing import Dict

TECHNIQUE = "Technique"


def write_dict_to_json(
    dict_to_write: Dict[str, Dict[str, str]],
    file_path: str,
    sort_keys: bool = True,
) -> None:
    with open(file_path, "w", encoding="utf8") as file:
        json.dump(dict_to_write, file, indent=4, sort_keys=sort_keys)


def write_evaluation_metrics_to_csv(
    combined_evaluation_dict: Dict[str, Dict[str, float]], csv_name: str
) -> None:
    csv_headers = [TECHNIQUE] + list(list(combined_evaluation_dict.values())[0].keys())

    with open(csv_name, "w", newline="", encoding="utf8") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
        csv_writer.writeheader()
        for technique, evaluation_dict in combined_evaluation_dict.items():
            row = {TECHNIQUE: technique}
            for metric, score in evaluation_dict.items():
                row[metric] = score if not isinstance(score, float) else round(score, 1)
            csv_writer.writerow(row)


__all__ = ["write_classifications_to_json", "write_evaluation_metrics_to_csv"]
