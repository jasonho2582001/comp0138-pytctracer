from typing import List, Tuple, Set, Dict
import csv
import random
import sys

csv.field_size_limit(sys.maxsize)

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

    return columns, data

def extract_function_and_test_names(data: List[Dict[str, str]], test_names_file: str, function_names_file: str) -> Tuple[List[str], List[str]]:
    test_names = set([record["Fully Qualified Function Name"] for record in data if record["Testing Method"] == "TEST METHOD CALL" and record["Fully Qualified Function Name"]])
    function_names = set([record["Fully Qualified Function Name"] for record in data if record["Function Type"] == "SOURCE" and record["Fully Qualified Function Name"]])

    with open(test_names_file, "w") as test_file:
        for test_name in test_names:
            test_file.write(test_name + "\n")

    with open(function_names_file, "w") as function_file:
        for function_name in function_names:
            function_file.write(function_name + "\n")
        
    return list(function_names), list(test_names)

def extract_function_class_and_test_class_names(data: List[Dict[str, str]], test_names_file: str, function_names_file: str) -> Tuple[List[str], List[str]]:
    test_class_names = set([record["Fully Qualified Class Name"] for record in data if record["Testing Method"] == "TEST METHOD CALL" and record["Fully Qualified Class Name"]])
    function_class_names = set([record["Fully Qualified Class Name"] for record in data if record["Function Type"] == "SOURCE" and record["Fully Qualified Class Name"]])

    with open(test_names_file, "w") as test_file:
        for test_name in test_class_names:
            test_file.write(test_name + "\n")

    with open(function_names_file, "w") as function_file:
        for function_name in function_class_names:
            function_file.write(function_name + "\n")
        
    return list(function_class_names), list(test_class_names)

def choose_sample_tests(test_names: List[str], sample_test_file: str, n: int = 50) -> List[str]:
    n = min(n, len(test_names))
    sample_tests = random.sample(test_names, n)
    with open(sample_test_file, "w") as sample_file:
        for test_name in sample_tests:
            sample_file.write(test_name + "\n")
    
    return sample_tests
        

pyopenssl_tracing_log_path = "tracing_logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv"
pyopenssl_all_test_class_names_path = "ground_truth_data/pyopenssl/class/pyopenssl_all_test_class_names.txt"
pyopenssl_all_function_class_names_path = "ground_truth_data/pyopenssl/class/pyopenssl_all_function_class_names.txt"
pyopenssl_sample_test_class_names_path = "ground_truth_data/pyopenssl/class/pyopenssl_sample_test_class_names.txt"

arrow_tracing_log_path = "tracing_logs/arrow/arrow_pytest_tracer_logs.csv"
arrow_all_test_class_names_path = "ground_truth_data/arrow/class/arrow_all_test_class_names.txt"
arrow_all_function_class_names_path = "ground_truth_data/arrow/class/arrow_all_function_class_names.txt"
arrow_sample_test_class_names_path = "ground_truth_data/arrow/class/arrow_sample_test_class_names.txt"

kedro_tracing_log_path = "tracing_logs/kedro/kedro_pytest_tracer_logs.csv"
kedro_all_test_class_names_path = "ground_truth_data/kedro/class/kedro_all_test_class_names.txt"
kedro_all_function_class_names_path = "ground_truth_data/kedro/class/kedro_all_function_class_names.txt"
kedro_sample_test_class_names_path = "ground_truth_data/kedro/class/kedro_sample_test_class_names.txt"

chartify_tracing_log_path = "tracing_logs/chartify/chartify_pytest_tracer_logs.csv"
chartify_all_test_class_names_path = "ground_truth_data/chartify/class/chartify_all_test_class_names.txt"
chartify_all_function_class_names_path = "ground_truth_data/chartify/class/chartify_all_function_class_names.txt"
chartify_sample_test_class_names_path = "ground_truth_data/chartify/class/chartify_sample_test_class_names.txt"

chartify_all_test_names_path = "ground_truth_data/chartify/function/chartify_all_test_names.txt"
chartify_all_function_names_path = "ground_truth_data/chartify/function/chartify_all_function_names.txt"
chartify_sample_test_names_path = "ground_truth_data/chartify/function/chartify_sample_test_names.txt"

if __name__ == "__main__":
    # columns, data = read_csv_log(pyopenssl_tracing_log_path)
    # function_class_names, test_class_names = extract_function_class_and_test_class_names(data, pyopenssl_all_test_class_names_path, pyopenssl_all_function_class_names_path)
    # sample_test_classes = choose_sample_tests(test_class_names, pyopenssl_sample_test_class_names_path)
    # columns, data = read_csv_log(arrow_tracing_log_path)
    # function_class_names, test_class_names = extract_function_class_and_test_class_names(data, arrow_all_test_class_names_path, arrow_all_function_class_names_path)
    # sample_test_classes = choose_sample_tests(test_class_names, arrow_sample_test_class_names_path)
    # columns, data = read_csv_log(kedro_tracing_log_path)
    # function_class_names, test_class_names = extract_function_class_and_test_class_names(data, kedro_all_test_class_names_path, kedro_all_function_class_names_path)
    # sample_test_classes = choose_sample_tests(test_class_names, kedro_sample_test_class_names_path)
    columns, data = read_csv_log(chartify_tracing_log_path)
    function_class_names, test_class_names = extract_function_and_test_names(data, chartify_all_test_names_path, chartify_all_function_names_path)
    sample_tests = choose_sample_tests(test_class_names, chartify_sample_test_names_path)
    print(sample_tests)

    function_class_names, test_class_names = extract_function_class_and_test_class_names(data, chartify_all_test_class_names_path, chartify_all_function_class_names_path)
    sample_test_classes = choose_sample_tests(test_class_names, chartify_sample_test_class_names_path)
    print(sample_test_classes)