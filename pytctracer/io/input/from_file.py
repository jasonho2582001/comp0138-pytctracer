import sys
import csv
import json
from typing import List, Dict

# Increase the maximum field size limit for CSV files,
# for very large trace logs
try:
    csv.field_size_limit(sys.maxsize)
except OverflowError:
    csv.field_size_limit(int(1e9))


def read_trace_csv_log(file_path: str) -> List[Dict[str, str]]:
    """
    Read a CSV file containing trace data and return it as a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.
    
    Returns:
        List[Dict[str, str]]: A list of dictionaries where each dictionary represents
        a row in the CSV file, with the keys being the column names and the values
        being the corresponding values in the row.
    """
    data = []
    try:
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

    except FileNotFoundError:
        raise FileNotFoundError(f"Trace log not found at path: {file_path}")

    except:
        raise ValueError(f"An error occurred while reading the trace log at path: {file_path}.")


def load_link_json(link_path: str) -> Dict[str, List[str]]:
    """
    Loads a JSON file containing test-to-code links as a dictionary.

    Args:
        link_path (str): The path to the JSON file containing test-to-code links.
    
    Returns:
        Dict[str, List[str]]: A dictionary where the keys are the fully qualified names
        of the test or test classes, and the values are lists containing the fully
        qualified names of the function or function classes that the test invokes.
    """
    try:
        with open(link_path, encoding="utf8") as file:
            link_dict = json.load(file)

    except FileNotFoundError:
        raise FileNotFoundError(f"Link file not found at path: {link_path}")

    except:
        raise ValueError(f"An error occurred while reading the link file at path: {link_path}.")

    return link_dict


__all__ = ["read_trace_csv_log", "load_link_json"]
