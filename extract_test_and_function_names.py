from typing import List, Tuple, Set, Dict
import csv
import random

def read_csv_log(file_path: str) -> Tuple[List[str], List[Dict[str, str]]]:
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
    c = 0
    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            c += 1
    print(c)
    return columns, data

def extract_function_and_test_names(data: List[Dict[str, str]], test_names_file: str, function_names_file: str) -> Tuple[List[str], List[str]]:
    test_names = set([record["Fully Qualified Name"] for record in data if record["Testing Method"] == "TEST METHOD CALL"])
    function_names = set([record["Fully Qualified Name"] for record in data if record["Function Type"] == "SOURCE"])

    with open(test_names_file, "w") as test_file:
        for test_name in test_names:
            test_file.write(test_name + "\n")

    with open(function_names_file, "w") as function_file:
        for function_name in function_names:
            function_file.write(function_name + "\n")
        
    return list(function_names), list(test_names)

def choose_sample_tests(test_names: List[str], sample_test_file: str, n: int = 50) -> List[str]:
    sample_tests = random.sample(test_names, n)
    with open(sample_test_file, "w") as sample_file:
        for test_name in sample_tests:
            sample_file.write(test_name + "\n")
    
    return sample_tests
        

if __name__ == "__main__":
    columns, data = read_csv_log("tracing_logs/kedro_pytest_tracer_logs.csv")
    function_names, test_names = extract_function_and_test_names(data, "ground_truth_data/analysis_for_kedro/kedro_all_test_names.txt", "ground_truth_data/analysis_for_kedro/kedro_all_function_names.txt")
    sample_tests = choose_sample_tests(test_names, "ground_truth_data/analysis_for_kedro/kedro_sample_test_names.txt")
    print(sample_tests)