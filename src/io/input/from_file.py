import sys
import csv
import json
from typing import List, Dict

# Increase the maximum field size limit for CSV files,
# for very large trace logs
csv.field_size_limit(sys.maxsize)


def read_trace_csv_log(file_path: str) -> List[Dict[str, str]]:
    data = []
    with open(file_path, encoding="utf8") as file:
        lines = csv.reader(file)

        # Iterate through each line in the CSV file, extract the fields
        for index, record in enumerate(lines):
            # Extract column names from first row
            if index == 0:
                columns = record
                continue
            data.append({columns[i]: record[i] for i in range(len(columns))})

    return data


def load_link_json(link_path: str) -> Dict[str, List[str]]:
    with open(link_path, encoding="utf8") as file:
        link_dict = json.load(file)

    return link_dict


__all__ = ["read_trace_csv_log", "load_link_json"]
