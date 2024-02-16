from collections import defaultdict
from typing import Optional, Set, List, Dict, Tuple
from math import log
import csv
import json
import sys

csv.field_size_limit(sys.maxsize)

THRESHOLD_FOR_LCSU = 0.75
THRESHOLD_FOR_LCSB = 0.65
THRESHOLD_FOR_LEVENSHTEIN = 0.95
THRESHOLD_FOR_TARANTULA = 0.95
THRESHOLD_FOR_TFIDF = 0.9
THRESHOLD_FOR_AVERAGE = sum(threshold_arr := [THRESHOLD_FOR_LCSU, THRESHOLD_FOR_LCSB, THRESHOLD_FOR_LEVENSHTEIN, THRESHOLD_FOR_TARANTULA, THRESHOLD_FOR_TFIDF])/len(threshold_arr)
DISCOUNT_FACTOR = 0.5

def find_lcs(s1: str, s2: str) -> int:
    m = len(s1)
    n = len(s2)
    dp = [[0 for i in range(n+1)] for j in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp[m][n]

def find_levenshtein_distance(s1: str, s2: str) -> int:
    m = len(s1)
    n = len(s2)
    dp = [[0 for i in range(n+1)] for j in range(m+1)]
    for i in range(n+1):
        dp[0][i] = i
    for j in range(m+1):
        dp[j][0] = j
    
    for i in range(1, m+1):
        for j in range(1, n+1):
            dp[i][j] = min(dp[i][j-1] + 1, dp[i-1][j] + 1, dp[i-1][j-1] + (1 if s1[i-1] != s2[j-1] else 0))

    return dp[m][n]

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

def extract_ground_truth_class_names(function_names_path: str, test_names_path: str) -> Tuple[Set[str], Set[str]]:
    function_class_names = set()
    test_class_names = set()
    with open(function_names_path, "r") as function_names_file:
        lines = function_names_file.read().splitlines()
        for line in lines:
            function_class_names.add(line)
    
    with open(test_names_path, "r") as test_names_file:
        lines = test_names_file.read().splitlines()
        for line in lines:
            test_class_names.add(line)
    
    return function_class_names, test_class_names


def extract_function_class_and_test_class_names_tuple(data: List[Dict[str, str]], function_class_names: Set[str], test_class_names: Set[str]) -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    test_class_names_tuple = set([(record["Fully Qualified Class Name"], record["Class Name"]) for record in data if record["Testing Method"] == "TEST METHOD CALL" and record["Class Name"] and record["Fully Qualified Class Name"] in test_class_names])
    function_class_names_tuple = set([(record["Fully Qualified Class Name"], record["Class Name"]) for record in data if record["Function Type"] == "SOURCE" and record["Class Name"] and record["Fully Qualified Class Name"] in function_class_names])

    return function_class_names_tuple, test_class_names_tuple

def find_function_classes_called_by_each_test_class(data: List[Dict[str, str]], function_class_names: Set[str], test_class_names: Set[str]) -> Dict[str, Set[str]]:
    function_classes_called_by_each_test_classes_dict = defaultdict(set)
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Class Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test and current_test in test_class_names and record["Function Type"] == "SOURCE" and record["Fully Qualified Class Name"] and record["Fully Qualified Class Name"] in function_class_names:
            function_classes_called_by_each_test_classes_dict[current_test].add(record["Fully Qualified Class Name"])
    
    return function_classes_called_by_each_test_classes_dict

def find_test_classes_that_call_each_function_class(data: List[Dict[str, str]], function_class_names: Set[str], test_class_names: Set[str]) -> Dict[str, Set[str]]:
    test_classes_that_call_each_function_class_dict = defaultdict(set)
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Class Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test and current_test in test_class_names and record["Function Type"] == "SOURCE" and record["Fully Qualified Class Name"] and record["Fully Qualified Class Name"] in function_class_names:
            test_classes_that_call_each_function_class_dict[record["Fully Qualified Class Name"]].add(current_test)

    return test_classes_that_call_each_function_class_dict

def find_depths_of_function_classes_called_by_each_test_class(data: List[Dict[str, str]], function_class_names: Set[str], test_class_names: Set[str]) -> Dict[str, Dict[str, int]]:
    # Each function appears once for a test, at the highest depth
    depths_of_function_classes_called_by_each_test_class_dict = defaultdict(dict)
    current_test_class = None
    current_test_class_depth = 0

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test_class = record["Fully Qualified Class Name"]
            current_test_class_depth = int(record["Depth"])
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test_class = None
        elif current_test_class is not None and current_test_class in test_class_names and record["Function Type"] == "SOURCE" and record["Fully Qualified Class Name"] and record["Fully Qualified Class Name"] in function_class_names:
            function_class_name = record["Fully Qualified Class Name"]
            function_class_depth = int(record["Depth"])
            if current_test_class in depths_of_function_classes_called_by_each_test_class_dict and function_class_name in depths_of_function_classes_called_by_each_test_class_dict[current_test_class]:
                function_class_depth = min(function_class_depth, depths_of_function_classes_called_by_each_test_class_dict[current_test_class][function_class_name])
            depths_of_function_classes_called_by_each_test_class_dict[current_test_class][function_class_name] = function_class_depth - current_test_class_depth
        
    return depths_of_function_classes_called_by_each_test_class_dict

def extract_function_and_test_names_tuple(data: List[Dict[str, str]]) -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    test_names_tuple = set([(record["Fully Qualified Function Name"], record["Function Name"]) for record in data if record["Testing Method"] == "TEST METHOD CALL"])
    function_names_tuple = set([(record["Fully Qualified Function Name"], record["Function Name"]) for record in data if record["Function Type"] == "SOURCE"])

    return function_names_tuple, test_names_tuple

def find_functions_called_by_each_test(data: List[Dict[str, str]]) -> Dict[str, Set[str]]:
    functions_called_by_each_test_dict = defaultdict(set)
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Function Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test is not None and record["Function Type"] == "SOURCE":
            functions_called_by_each_test_dict[current_test].add(record["Fully Qualified Function Name"])
    
    return functions_called_by_each_test_dict

def find_tests_that_call_each_function(data: List[Dict[str, str]]) -> Dict[str, Set[str]]:
    tests_that_call_each_function_dict = defaultdict(set)
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Function Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test is not None and record["Function Type"] == "SOURCE":
            tests_that_call_each_function_dict[record["Fully Qualified Function Name"]].add(current_test)

    return tests_that_call_each_function_dict

def find_depths_of_functions_called_by_each_test(data: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    # Each function appears once for a test, at the highest depth
    depths_of_functions_called_by_each_test_dict = defaultdict(dict)
    current_test = None
    current_test_depth = 0

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Function Name"]
            current_test_depth = int(record["Depth"])
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test is not None and record["Function Type"] == "SOURCE":
            function_name = record["Fully Qualified Function Name"]
            function_depth = int(record["Depth"])
            if current_test in depths_of_functions_called_by_each_test_dict and function_name in depths_of_functions_called_by_each_test_dict[current_test]:
                function_depth = min(function_depth, depths_of_functions_called_by_each_test_dict[current_test][function_name])
            depths_of_functions_called_by_each_test_dict[current_test][function_name] = function_depth - current_test_depth
        
    return depths_of_functions_called_by_each_test_dict


def naming_conventions(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]], functions_called_by_each_test_dict: Dict[str, Set[str]]) -> Dict[str, Dict[str, float]]:
    naming_conventions_dict = defaultdict(dict)

    for test_fully_qualified_name, test_function_name in test_names_tuple:
        functions_called_by_test = functions_called_by_each_test_dict[test_fully_qualified_name]
        for function_fully_qualified_name, function_name in function_names_tuple:
            if test_function_name.startswith("test_"):
                stripped_test_function_name = test_function_name[5:]
            else:
                # assumption that all test functions must begin with test
                stripped_test_function_name = test_function_name[4:]
            naming_conventions_dict[test_fully_qualified_name][function_fully_qualified_name] = (1 if function_name == stripped_test_function_name else 0) if function_fully_qualified_name in functions_called_by_test else -1
    
    return naming_conventions_dict

def naming_convention_contains(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]], functions_called_by_each_test_dict: Dict[str, Set[str]]) -> Dict[str, Dict[str, float]]:
    naming_conventions_contains_dict = defaultdict(dict)

    for test_fully_qualified_name, test_function_name in test_names_tuple:
        functions_called_by_test = functions_called_by_each_test_dict[test_fully_qualified_name]
        for function_fully_qualified_name, function_name in function_names_tuple:
            if test_function_name.startswith("test_"):
                stripped_test_function_name = test_function_name[5:]
            else:
                # assumption that all test functions must begin with test
                stripped_test_function_name = test_function_name[4:]
            naming_conventions_contains_dict[test_fully_qualified_name][function_fully_qualified_name] = (1 if function_name in stripped_test_function_name else 0) if function_fully_qualified_name in functions_called_by_test else -1
    
    return naming_conventions_contains_dict

def normalise_dict(result_dict: Dict[str, Dict[str, float]], functions_called_by_each_test_dict: Dict[str, Set[str]]) -> Dict[str, Dict[str, float]]:
    normalised_result_dict = {test: function_results.copy() for test, function_results in result_dict.items()}

    for test_fully_qualified_name in result_dict:
        # find maximum score and normalise w.r.t to it
        functions_called_by_test = functions_called_by_each_test_dict[test_fully_qualified_name]
        max_score = 0
        for function_fully_qualified_name in functions_called_by_test:
            max_score = max(max_score, result_dict[test_fully_qualified_name][function_fully_qualified_name])
        for function_fully_qualified_name in functions_called_by_test:
            if max_score > 0:
                normalised_result_dict[test_fully_qualified_name][function_fully_qualified_name] /= max_score

    return normalised_result_dict

def use_call_depth_discounting_dict(result_dict: Dict[str, Dict[str, float]], depths_of_functions_called_by_each_test_dict: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
    discounted_dict = {test: function_results.copy() for test, function_results in result_dict.items()}
    for test_fully_qualified_name, result_for_each_test_dict in discounted_dict.items():
        # We only do the discounting for the functions called by each test (the result_dict has scores of -1 for functions that don't get called by the test)
        for function_fully_qualified_name in depths_of_functions_called_by_each_test_dict[test_fully_qualified_name]:
            original_score = discounted_dict[test_fully_qualified_name][function_fully_qualified_name] 
            depth = depths_of_functions_called_by_each_test_dict[test_fully_qualified_name][function_fully_qualified_name]
            discounted_dict[test_fully_qualified_name][function_fully_qualified_name] = original_score * DISCOUNT_FACTOR**(depth-1)

    return discounted_dict

def longest_common_subsequence_both(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]], functions_called_by_each_test_dict: Dict[str, Set[str]], depths_of_functions_called_by_each_test_dict: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
    lcsb_dict = defaultdict(dict)

    for test_fully_qualified_name, test_function_name in test_names_tuple:
        functions_called_by_test = functions_called_by_each_test_dict[test_fully_qualified_name]
        for function_fully_qualified_name, function_name in function_names_tuple:
            if test_function_name.startswith("test_"):
                stripped_test_function_name = test_function_name[5:]
            else:
                # assumption that all test functions must begin with test
                stripped_test_function_name = test_function_name[4:]

            lcsb_result = (find_lcs(stripped_test_function_name, function_name))/(max(len(stripped_test_function_name), len(function_name))) if function_fully_qualified_name in functions_called_by_test else -1
            lcsb_dict[test_fully_qualified_name][function_fully_qualified_name] = lcsb_result

    return normalise_dict(use_call_depth_discounting_dict(lcsb_dict, depths_of_functions_called_by_each_test_dict), functions_called_by_each_test_dict)

def longest_common_subsequence_unit(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]], functions_called_by_each_test_dict: Dict[str, Set[str]], depths_of_functions_called_by_each_test_dict: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
    lcsu_dict = defaultdict(dict)

    for test_fully_qualified_name, test_function_name in test_names_tuple:
        functions_called_by_test = functions_called_by_each_test_dict[test_fully_qualified_name]
        for function_fully_qualified_name, function_name in function_names_tuple:
            if test_function_name.startswith("test_"):
                stripped_test_function_name = test_function_name[5:]
            else:
                # assumption that all test functions must begin with test
                stripped_test_function_name = test_function_name[4:]

            lcsu_result = (find_lcs(stripped_test_function_name, function_name))/len(function_name) if function_fully_qualified_name in functions_called_by_test else -1
            lcsu_dict[test_fully_qualified_name][function_fully_qualified_name] = lcsu_result

    return normalise_dict(use_call_depth_discounting_dict(lcsu_dict, depths_of_functions_called_by_each_test_dict), functions_called_by_each_test_dict)

def levenshtein_distance(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]], functions_called_by_each_test_dict: Dict[str, Set[str]], depths_of_functions_called_by_each_test_dict: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
    levenshtein_dict = defaultdict(dict)

    for test_fully_qualified_name, test_function_name in test_names_tuple:
        functions_called_by_test = functions_called_by_each_test_dict[test_fully_qualified_name]
        for function_fully_qualified_name, function_name in function_names_tuple:
            if test_function_name.startswith("test_"):
                stripped_test_function_name = test_function_name[5:]
            else:
                # assumption that all test functions must begin with test
                stripped_test_function_name = test_function_name[4:]
            levenshtein_result = (1 - (find_levenshtein_distance(stripped_test_function_name, function_name))/(max(len(stripped_test_function_name), len(function_name)))) if function_fully_qualified_name in functions_called_by_test else -1
            levenshtein_dict[test_fully_qualified_name][function_fully_qualified_name] = levenshtein_result
    
    return normalise_dict(use_call_depth_discounting_dict(levenshtein_dict, depths_of_functions_called_by_each_test_dict), functions_called_by_each_test_dict)

def last_call_before_assert(data: List[Dict[str, str]], function_names: Set[str], test_names: Set[str]) -> Dict[str, Set[str]]:
    """FIX TRACER BECAUSE IF FUNCTION RETURNS IN-LINE WITH AN ASSERT IT WILL NOT CATCH THE ASSERT"""
    functions_called_before_assert_for_each_test = defaultdict(set)
    current_test = None
    last_returned_function = None
    
    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Function Name"]
            last_returned_function = None
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test is not None and record["Event Type"] == "RETURN" and record["Function Type"] == "SOURCE":
            last_returned_function = record["Fully Qualified Function Name"]
        elif current_test is not None and last_returned_function is not None and record["Function Type"] == "ASSERT":
            # Won't catch the last returned function if there was no return before an assert in the current test
            functions_called_before_assert_for_each_test[current_test].add(last_returned_function)
    
    lcba_dict = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}

    for test_name, functions_called_before_assert in functions_called_before_assert_for_each_test.items():
        for function_name in functions_called_before_assert:
            lcba_dict[test_name][function_name] = 1
    
    return lcba_dict

def last_call_before_assert_class(data: List[Dict[str, str]], function_names: Set[str], test_names: Set[str]) -> Dict[str, Set[str]]:
    """FIX TRACER BECAUSE IF FUNCTION RETURNS IN-LINE WITH AN ASSERT IT WILL NOT CATCH THE ASSERT"""
    functions_called_before_assert_for_each_test = defaultdict(set)
    current_test = None
    last_returned_function = None
    
    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Class Name"]
            last_returned_function = None
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test and record["Event Type"] == "RETURN" and record["Function Type"] == "SOURCE":
            last_returned_function = record["Fully Qualified Class Name"]
        elif current_test and current_test in test_names and last_returned_function and last_returned_function in function_names and record["Function Type"] == "ASSERT":
            # Won't catch the last returned function if there was no return before an assert in the current test
            functions_called_before_assert_for_each_test[current_test].add(last_returned_function)
    
    lcba_dict = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}

    for test_name, functions_called_before_assert in functions_called_before_assert_for_each_test.items():
        for function_name in functions_called_before_assert:
            lcba_dict[test_name][function_name] = 1
    
    return lcba_dict


def tarantula(functions_called_by_each_test_dict: Dict[str, Set[str]], tests_that_call_each_function_dict: Dict[str, Set[str]], function_names: Set[str], test_names: Set[str], depths_of_functions_called_by_each_test_dict: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
    number_of_tests = len(test_names)
    # number_of_functions = len(fully_qualified_function_names)

    tarantula_dict = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}

    for test_name in functions_called_by_each_test_dict:
        for function_name in tests_that_call_each_function_dict:
            if function_name in functions_called_by_each_test_dict[test_name]:
                number_of_tests_that_call_function = len(tests_that_call_each_function_dict[function_name])
                tarantula_dict[test_name][function_name] = 1/(((number_of_tests_that_call_function - 1)/(number_of_tests - 1))+1) 
    
    return normalise_dict(use_call_depth_discounting_dict(tarantula_dict, depths_of_functions_called_by_each_test_dict), functions_called_by_each_test_dict)

def tfidf(functions_called_by_each_test_dict: Dict[str, Set[str]], tests_that_call_each_function_dict: Dict[str, Set[str]], function_names: Set[str], test_names: Set[str], depths_of_functions_called_by_each_test_dict: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
    number_of_tests = len(test_names)
    idf_set = {}

    tfidf_dict = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}

    for function_name in tests_that_call_each_function_dict:
        number_of_tests_that_call_function = len(tests_that_call_each_function_dict[function_name])
        idf_set[function_name] = log(1 + number_of_tests/(number_of_tests_that_call_function))
    
    for test_name in functions_called_by_each_test_dict:
        number_of_functions_called_by_test = len(functions_called_by_each_test_dict[test_name])
        tf = log(1+1/(number_of_functions_called_by_test)) if number_of_functions_called_by_test > 0 else 0
        for function_name in functions_called_by_each_test_dict[test_name]:
            tfidf_dict[test_name][function_name] = tf * idf_set[function_name]
    
    return normalise_dict(use_call_depth_discounting_dict(tfidf_dict, depths_of_functions_called_by_each_test_dict), functions_called_by_each_test_dict)

def find_average_score(result_dicts: List[Dict[str, Dict[str, float]]], function_names: Set[str], test_names: Set[str], functions_called_by_each_test_dict: Dict[str, Set[str]]) -> Dict[str, Dict[str, float]]:
    average_score_dict = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}
    num_of_result_dicts = len(result_dicts)
    for result_dict in result_dicts:
        for test_name in test_names:
            for function_name in function_names:
                average_score_dict[test_name][function_name] += result_dict[test_name][function_name]/num_of_result_dicts
    
    return normalise_dict(average_score_dict, functions_called_by_each_test_dict)

def generate_predicted_links(dict_result: Dict[str, Dict[str, float]], threshold: Optional[float] = 1, tests_to_create_links_for: Optional[Set[str]] = None) -> Dict[str, Set[str]]:
    if tests_to_create_links_for is None:
        tests_to_create_links_for = set(dict_result.keys())
    
    predicted_links_dict = {test_name: set() for test_name in tests_to_create_links_for}

    for fully_qualified_test_name, results_for_test_dict in dict_result.items():
        for fully_qualified_function_name, score in results_for_test_dict.items():
            if fully_qualified_test_name in tests_to_create_links_for and score >= threshold:
                predicted_links_dict[fully_qualified_test_name].add(fully_qualified_function_name)
    
    return predicted_links_dict

def calculate_evalution_measures(predicted_links: Dict[str, Set[str]], ground_truth_links: Dict[str, Set[str]]) -> Tuple[Dict[str, float], Dict[str, Dict[str, str]]]:
    breakdown_dict = defaultdict(dict)
    found_true_positives = 0
    found_false_positives = 0
    found_false_negatives = 0
    total_true_links = 0
    for fully_qualified_test_name in predicted_links:
        predicted_links_for_test = predicted_links[fully_qualified_test_name]
        ground_truth_links_for_test = ground_truth_links[fully_qualified_test_name]
        true_positive_set = predicted_links_for_test.intersection(ground_truth_links_for_test)
        false_positive_set = predicted_links_for_test - ground_truth_links_for_test
        false_negatives_set = ground_truth_links_for_test - predicted_links_for_test
        found_true_positives += len(true_positive_set)
        found_false_positives += len(false_positive_set)
        found_false_negatives += len(false_negatives_set)
        breakdown_dict[fully_qualified_test_name]["True Positives"] = list(true_positive_set)
        breakdown_dict[fully_qualified_test_name]["False Positives"] = list(false_positive_set)
        breakdown_dict[fully_qualified_test_name]["False Negative"] = list(false_negatives_set)
        total_true_links += len(ground_truth_links_for_test)

    evaluation_dict = {}
    
    # Precision
    if found_true_positives + found_false_positives == 0:
        precision = 100
    else:
        precision = 100 * (found_true_positives)/(found_true_positives + found_false_positives)

    evaluation_dict["Precision"] = precision

    recall = 100 * (found_true_positives)/(found_true_positives + found_false_negatives)

    f1 = (2 * precision * recall)/(precision + recall) if precision + recall > 0 else 0

    evaluation_dict["Recall"] = recall

    evaluation_dict["F1"] = f1

    evaluation_dict["True Positives"] = found_true_positives

    evaluation_dict["False Positives"] = found_false_positives

    evaluation_dict["False Negatives"] = found_false_negatives

    return evaluation_dict, breakdown_dict
    

def write_evaluation_dict_to_csv(combined_evaluation_dict: Dict[str, Dict[str, float]], csv_name: str) -> None:
    csv_headers = ["Technique"] + list(list(combined_evaluation_dict.values())[0].keys())
    
    with open(csv_name, 'w',  newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
        csv_writer.writeheader()
        for technique, evaluation_dict in combined_evaluation_dict.items():
            row = {"Technique": technique}
            for metric, score in evaluation_dict.items():
                row[metric] = score if isinstance(score, int) else round(score, 3)
            csv_writer.writerow(row)

def print_combined_evaluation_results(combined_evaluation_dict: Dict[str, Dict[str, float]], title: str) -> None:
    print(f"{'='*15} {title} {'='*15}\n")
    for technique, evaluation_dict in combined_evaluation_dict.items():
        print(f"{'='*5} {technique} {'='*5}")
        for metric, score in evaluation_dict.items():
            print(f"{metric}: {score:.5f}")
        print("\n")
    print("="*50 + "\n\n")

def print_dict_results(dict_result: Dict[str, Dict[str, float]], title: str, tests_to_create_links_for: Optional[Set[str]] = None, limit: Optional[int] = 10) -> None:
    print(f"{'='*15} {title} {'='*15}\n")

    for test, results_for_test_dict in dict_result.items():
        if test in tests_to_create_links_for:
            print(f"{'='*5} {test} {'='*5}")
            results_for_test_list = list(results_for_test_dict.items())
            results_for_test_list.sort(key=lambda x: x[1], reverse=True)
            for i in range(1, len(results_for_test_list) + 1 if not limit else min(len(results_for_test_dict), limit) + 1):
                score = f"{results_for_test_list[i-1][1]:.5f}"
                function_name = results_for_test_list[i-1][0]
                print(f"Rank: {str(i).ljust(10)} | Score: {score.ljust(10)} | Function: {function_name}")
            print("\n")
    print("="*50 + "\n\n")

def print_predicted_links(predicted_links: Dict[str, Set[str]], evaluation_dict, title: str) -> None:
    print(f"{'='*15} {title} {'='*15}\n")

    for test, predicted_links_for_test in predicted_links.items():
        print(f"{'='*5} {test} {'='*5}")
        i = 1
        for function_name in predicted_links_for_test:
            print(f"{str(i).ljust(3)}: {function_name}")
            i += 1
        print("\n")
    
    print("="*50 + "\n")

def write_breakdown_dict_to_json(breakdown_dict: Dict[str, Dict[str, str]], file_path: str) -> None:
    with open(file_path, "w") as file:
        json.dump(breakdown_dict, file, indent=4)

def load_ground_truth(ground_truth_path: str) -> Dict[str, Set[str]]:
    with open(ground_truth_path, "r") as file:
        ground_truth_temp = json.load(file)

    return {test_name: set(links) for test_name, links in ground_truth_temp.items()}
    

def analyse_trace(file_path: str, ground_truth_path: str, analysis_log_output_path: str, breakdown_output_path: str) -> None:
    # PARSE DATA
    ground_truth_dict = load_ground_truth(ground_truth_path)
    columns, data = read_csv_log(file_path)
    function_names_tuple, test_names_tuple = extract_function_and_test_names_tuple(data)
    fully_qualified_function_names = set(fully_qualified_function_name for fully_qualified_function_name, _ in function_names_tuple)
    fully_qualified_test_names = set(fully_qualified_test_name for fully_qualified_test_name, _ in test_names_tuple)
    functions_called_by_each_test_dict = find_functions_called_by_each_test(data)
    tests_that_call_each_function_dict = find_tests_that_call_each_function(data)
    tests_to_create_links_for = set(ground_truth_dict.keys())
    depths_of_functions_called_by_each_test_dict = find_depths_of_functions_called_by_each_test(data)

    # TECHNIQUES
    naming_conventions_dict = naming_conventions(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
    naming_convention_contains_dict = naming_convention_contains(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
    lcsb_dict = longest_common_subsequence_both(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict, depths_of_functions_called_by_each_test_dict)
    lcsu_dict = longest_common_subsequence_unit(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict, depths_of_functions_called_by_each_test_dict)
    levenshtein_dict = levenshtein_distance(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict, depths_of_functions_called_by_each_test_dict)
    lcba_dict = last_call_before_assert(data, fully_qualified_function_names, fully_qualified_test_names)
    tarantula_dict = tarantula(functions_called_by_each_test_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names, depths_of_functions_called_by_each_test_dict)
    tfidf_dict = tfidf(functions_called_by_each_test_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names, depths_of_functions_called_by_each_test_dict)

    result_dicts = [naming_conventions_dict, naming_convention_contains_dict, lcsb_dict, lcsu_dict, levenshtein_dict, lcba_dict, tarantula_dict, tfidf_dict]
    average_dict = find_average_score(result_dicts, fully_qualified_function_names, fully_qualified_test_names, functions_called_by_each_test_dict)

    # print_dict_results(naming_conventions_dict, "Results for Naming Convention", 10)
    # print_dict_results(naming_convention_contains_dict, "Results for Naming Convention - Contains", 10)
    # print_dict_results(lcsb_dict, "LCS - Both", tests_to_create_links_for, 10)
    # print_dict_results(lcsu_dict, "LCS - Unit", tests_to_create_links_for, 10)
    # print_dict_results(levenshtein_dict, "Levenshtein", tests_to_create_links_for, 10)
    # print_dict_results(lcba_dict, "LCBA", tests_to_create_links_for, 10)
    # print_dict_results(tarantula_dict, "Tarauntula", tests_to_create_links_for, 10)
    # print_dict_results(tfidf_dict, "Tarauntula", tests_to_create_links_for, 10)z
    # print_dict_results(average_dict, "Simple Average", tests_to_create_links_for, 10)

    # PRODUCING PREDICTIONS
    combined_evaluation_dict = {}
    
    predicted_links_for_naming_convention = generate_predicted_links(naming_conventions_dict, 1, tests_to_create_links_for)
    predicted_links_for_naming_convention_contains = generate_predicted_links(naming_convention_contains_dict, 1, tests_to_create_links_for)
    predicted_links_for_lcsb = generate_predicted_links(lcsb_dict, THRESHOLD_FOR_LCSB, tests_to_create_links_for)
    predicted_links_for_lcsu = generate_predicted_links(lcsu_dict, THRESHOLD_FOR_LCSU, tests_to_create_links_for)
    predicted_links_for_levenshtein = generate_predicted_links(levenshtein_dict, THRESHOLD_FOR_LEVENSHTEIN, tests_to_create_links_for)
    predicted_links_for_lcba = generate_predicted_links(lcba_dict, 1, tests_to_create_links_for)
    predicted_links_for_tarantula = generate_predicted_links(tarantula_dict, THRESHOLD_FOR_TARANTULA, tests_to_create_links_for)
    predicted_links_for_tfidf = generate_predicted_links(tfidf_dict, THRESHOLD_FOR_TFIDF, tests_to_create_links_for)
    predicted_links_for_average = generate_predicted_links(average_dict, THRESHOLD_FOR_AVERAGE, tests_to_create_links_for)

    evaluation_dict_for_naming_convention, _ = calculate_evalution_measures(predicted_links_for_naming_convention, ground_truth_dict)
    evaluation_dict_for_naming_convention_contains, _  = calculate_evalution_measures(predicted_links_for_naming_convention_contains, ground_truth_dict)
    evaluation_dict_for_lcsb, t  = calculate_evalution_measures(predicted_links_for_lcsb, ground_truth_dict)
    evaluation_dict_for_lcsu, a  = calculate_evalution_measures(predicted_links_for_lcsu, ground_truth_dict)
    evaluation_dict_for_levenshtein, _  = calculate_evalution_measures(predicted_links_for_levenshtein, ground_truth_dict)
    evaluation_dict_for_lcba, _  = calculate_evalution_measures(predicted_links_for_lcba, ground_truth_dict)
    evaluation_dict_for_tarauntula, _  = calculate_evalution_measures(predicted_links_for_tarantula, ground_truth_dict)
    evaluation_dict_for_tfidf, _  = calculate_evalution_measures(predicted_links_for_tfidf, ground_truth_dict)
    evaluation_dict_for_average, breakdown_dict = calculate_evalution_measures(predicted_links_for_average, ground_truth_dict)

    combined_evaluation_dict["Naming Conventions"] = evaluation_dict_for_naming_convention
    combined_evaluation_dict["Naming Conventions - Contains"] = evaluation_dict_for_naming_convention_contains
    combined_evaluation_dict["Longest Common Subsequence - Both"] = evaluation_dict_for_lcsb
    combined_evaluation_dict["Longest Common Subsequence - Unit"] = evaluation_dict_for_lcsu
    combined_evaluation_dict["Levenshtein Distance"] = evaluation_dict_for_levenshtein
    combined_evaluation_dict["Last Call Before Assert"] = evaluation_dict_for_lcba
    combined_evaluation_dict["Tarantula"] = evaluation_dict_for_tarauntula
    combined_evaluation_dict["TF-IDF"] = evaluation_dict_for_tfidf
    combined_evaluation_dict["Simple Average"] = evaluation_dict_for_average

    # OUTPUT
    # print_predicted_links(predicted_links_for_naming_convention, evaluation_dict_for_naming_convention, "Predicted Links for Naming Convention")
    # print_predicted_links(predicted_links_for_naming_convention, evaluation_dict_for_naming_convention_contains, "Predicted Links for Naming Convention - Contains")
    # print_predicted_links(predicted_links_for_levenshtein, evaluation_dict_for_levenshtein, "Predicted Links for Levenshtein Distance")
    
    print_combined_evaluation_results(combined_evaluation_dict, "Evaluation Metrics")
    write_evaluation_dict_to_csv(combined_evaluation_dict, analysis_log_output_path)
    write_breakdown_dict_to_json(breakdown_dict, breakdown_output_path)
    # write_breakdown_dict_to_json(t, "k.json")
    # write_breakdown_dict_to_json(a, "a.json")

def analyse_trace_class_level(file_path: str, ground_truth_path: str, analysis_log_output_path: str, breakdown_output_path: str, ground_truth_function_class_path: str, ground_truth_test_class_path: str) -> None:
    ground_truth_dict = load_ground_truth(ground_truth_path)
    columns, data = read_csv_log(file_path)
    ground_truth_function_class_names, ground_truth_test_class_names = extract_ground_truth_class_names(ground_truth_function_class_path, ground_truth_test_class_path)
    
    function_names_tuple, test_names_tuple = extract_function_class_and_test_class_names_tuple(data, ground_truth_function_class_names, ground_truth_test_class_names)
    fully_qualified_function_names = set(fully_qualified_function_name for fully_qualified_function_name, _ in function_names_tuple)
    fully_qualified_test_names = set(fully_qualified_test_name for fully_qualified_test_name, _ in test_names_tuple)
    functions_called_by_each_test_dict = find_function_classes_called_by_each_test_class(data, ground_truth_function_class_names, ground_truth_test_class_names)
    tests_that_call_each_function_dict = find_test_classes_that_call_each_function_class(data, ground_truth_function_class_names, ground_truth_test_class_names)
    tests_to_create_links_for = set(ground_truth_dict.keys())
    depths_of_functions_called_by_each_test_dict = find_depths_of_function_classes_called_by_each_test_class(data, ground_truth_function_class_names, ground_truth_test_class_names)
    # print(function_names_tuple)

    # TECHNIQUES
    naming_conventions_dict = naming_conventions(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
    naming_convention_contains_dict = naming_convention_contains(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
    lcsb_dict = longest_common_subsequence_both(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict, depths_of_functions_called_by_each_test_dict)
    lcsu_dict = longest_common_subsequence_unit(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict, depths_of_functions_called_by_each_test_dict)
    levenshtein_dict = levenshtein_distance(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict, depths_of_functions_called_by_each_test_dict)
    lcba_dict = last_call_before_assert_class(data, fully_qualified_function_names, fully_qualified_test_names)
    tarantula_dict = tarantula(functions_called_by_each_test_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names, depths_of_functions_called_by_each_test_dict)
    tfidf_dict = tfidf(functions_called_by_each_test_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names, depths_of_functions_called_by_each_test_dict)

    result_dicts = [naming_conventions_dict, naming_convention_contains_dict, lcsb_dict, lcsu_dict, levenshtein_dict, lcba_dict, tarantula_dict, tfidf_dict]
    average_dict = find_average_score(result_dicts, fully_qualified_function_names, fully_qualified_test_names, functions_called_by_each_test_dict)

    # print_dict_results(naming_conventions_dict, "Results for Naming Convention", 10)
    # print_dict_results(naming_convention_contains_dict, "Results for Naming Convention - Contains", 10)
    # print_dict_results(lcsb_dict, "LCS - Both", tests_to_create_links_for, 10)
    # print_dict_results(lcsu_dict, "LCS - Unit", tests_to_create_links_for, 10)
    # print_dict_results(levenshtein_dict, "Levenshtein", tests_to_create_links_for, 10)
    # print_dict_results(lcba_dict, "LCBA", tests_to_create_links_for, 10)
    # print_dict_results(tarantula_dict, "Tarauntula", tests_to_create_links_for, 10)
    # print_dict_results(tfidf_dict, "Tarauntula", tests_to_create_links_for, 10)z
    # print_dict_results(average_dict, "Simple Average", tests_to_create_links_for, 10)

    # PRODUCING PREDICTIONS
    combined_evaluation_dict = {}
    
    predicted_links_for_naming_convention = generate_predicted_links(naming_conventions_dict, 1, tests_to_create_links_for)
    predicted_links_for_naming_convention_contains = generate_predicted_links(naming_convention_contains_dict, 1, tests_to_create_links_for)
    predicted_links_for_lcsb = generate_predicted_links(lcsb_dict, THRESHOLD_FOR_LCSB, tests_to_create_links_for)
    predicted_links_for_lcsu = generate_predicted_links(lcsu_dict, THRESHOLD_FOR_LCSU, tests_to_create_links_for)
    predicted_links_for_levenshtein = generate_predicted_links(levenshtein_dict, THRESHOLD_FOR_LEVENSHTEIN, tests_to_create_links_for)
    predicted_links_for_lcba = generate_predicted_links(lcba_dict, 1, tests_to_create_links_for)
    predicted_links_for_tarantula = generate_predicted_links(tarantula_dict, THRESHOLD_FOR_TARANTULA, tests_to_create_links_for)
    predicted_links_for_tfidf = generate_predicted_links(tfidf_dict, THRESHOLD_FOR_TFIDF, tests_to_create_links_for)
    predicted_links_for_average = generate_predicted_links(average_dict, THRESHOLD_FOR_AVERAGE, tests_to_create_links_for)

    evaluation_dict_for_naming_convention, _ = calculate_evalution_measures(predicted_links_for_naming_convention, ground_truth_dict)
    evaluation_dict_for_naming_convention_contains, _  = calculate_evalution_measures(predicted_links_for_naming_convention_contains, ground_truth_dict)
    evaluation_dict_for_lcsb, _ = calculate_evalution_measures(predicted_links_for_lcsb, ground_truth_dict)
    evaluation_dict_for_lcsu, _  = calculate_evalution_measures(predicted_links_for_lcsu, ground_truth_dict)
    evaluation_dict_for_levenshtein, _  = calculate_evalution_measures(predicted_links_for_levenshtein, ground_truth_dict)
    evaluation_dict_for_lcba, _  = calculate_evalution_measures(predicted_links_for_lcba, ground_truth_dict)
    evaluation_dict_for_tarauntula, _  = calculate_evalution_measures(predicted_links_for_tarantula, ground_truth_dict)
    evaluation_dict_for_tfidf, _  = calculate_evalution_measures(predicted_links_for_tfidf, ground_truth_dict)
    evaluation_dict_for_average, breakdown_dict = calculate_evalution_measures(predicted_links_for_average, ground_truth_dict)

    combined_evaluation_dict["Naming Conventions"] = evaluation_dict_for_naming_convention
    combined_evaluation_dict["Naming Conventions - Contains"] = evaluation_dict_for_naming_convention_contains
    combined_evaluation_dict["Longest Common Subsequence - Both"] = evaluation_dict_for_lcsb
    combined_evaluation_dict["Longest Common Subsequence - Unit"] = evaluation_dict_for_lcsu
    combined_evaluation_dict["Levenshtein Distance"] = evaluation_dict_for_levenshtein
    combined_evaluation_dict["Last Call Before Assert"] = evaluation_dict_for_lcba
    combined_evaluation_dict["Tarantula"] = evaluation_dict_for_tarauntula
    combined_evaluation_dict["TF-IDF"] = evaluation_dict_for_tfidf
    combined_evaluation_dict["Simple Average"] = evaluation_dict_for_average

    # OUTPUT
    # print_predicted_links(predicted_links_for_naming_convention, evaluation_dict_for_naming_convention, "Predicted Links for Naming Convention")
    # print_predicted_links(predicted_links_for_naming_convention, evaluation_dict_for_naming_convention_contains, "Predicted Links for Naming Convention - Contains")
    # print_predicted_links(predicted_links_for_levenshtein, evaluation_dict_for_levenshtein, "Predicted Links for Levenshtein Distance")
    
    print_combined_evaluation_results(combined_evaluation_dict, "Evaluation Metrics")
    write_evaluation_dict_to_csv(combined_evaluation_dict, analysis_log_output_path)
    write_breakdown_dict_to_json(breakdown_dict, breakdown_output_path)

kedro_tracer_logs_path = "tracing_logs/kedro/kedro_pytest_tracer_logs.csv"
kedro_ground_truth_path = "ground_truth_data/kedro/function/kedro_ground_truth.json"
kedro_analysis_path = "analysis/kedro/function/kedro_predictions_results.csv"
kedro_breakdown_path = "analysis/kedro/function/kedro_breakdown.json"

kedro_ground_truth_class_path = "ground_truth_data/kedro/class/kedro_ground_truth_classes.json"
kedro_class_level_analysis_path = "analysis/kedro/class/kedro_class_predictions_results.csv"
kedro_class_level_breakdown_path = "analysis/kedro/class/kedro_class_breakdown.json"
kedro_ground_truth_function_class_path = "ground_truth_data/kedro/class/kedro_all_function_class_names.txt"
kedro_ground_truth_test_class_path = "ground_truth_data/kedro/class/kedro_all_test_class_names.txt"

arrow_tracer_logs_path = "tracing_logs/arrow/arrow_pytest_tracer_logs.csv"
arrow_ground_truth_path = "ground_truth_data/arrow/function/arrow_ground_truth.json"
arrow_analysis_path = "analysis/arrow/function/arrow_predictions_results.csv"
arrow_breakdown_path = "analysis/arrow/function/arrow_breakdown.json"

arrow_ground_truth_class_path = "ground_truth_data/arrow/class/arrow_ground_truth_classes.json"
arrow_class_level_analysis_path = "analysis/arrow/class/arrow_predictions_class_results.csv"
arrow_class_level_breakdown_path = "analysis/arrow/class/arrow_class_breakdown.json"
arrow_ground_truth_function_class_path = "ground_truth_data/arrow/class/arrow_all_function_class_names.txt"
arrow_ground_truth_test_class_path = "ground_truth_data/arrow/class/arrow_all_test_class_names.txt"

pyopenssl_tracer_logs_path = "tracing_logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv"
pyopenssl_ground_truth_path = "ground_truth_data/pyopenssl/function/pyopenssl_ground_truth.json"
pyopenssl_analysis_path = "analysis/pyopenssl/function/pyopenssl_predictions_results.csv"
pyopenssl_breakdown_path = "analysis/pyopenssl/function/pyopenssl_breakdown.json"

pyopenssl_ground_truth_class_path = "ground_truth_data/pyopenssl/class/pyopenssl_ground_truth_classes.json"
pyopenssl_class_level_analysis_path = "analysis/pyopenssl/class/pyopenssl_predictions_class_results.csv"
pyopenssl_class_level_breakdown_path = "analysis/pyopenssl/class/pyopenssl_class_breakdown.json"
pyopenssl_ground_truth_function_class_path = "ground_truth_data/pyopenssl/class/pyopenssl_all_function_class_names.txt"
pyopenssl_ground_truth_test_class_path = "ground_truth_data/pyopenssl/class/pyopenssl_all_test_class_names.txt"

chartify_tracer_logs_path = "tracing_logs/chartify/chartify_pytest_tracer_logs.csv"
chartify_ground_truth_path = "ground_truth_data/chartify/function/chartify_ground_truth.json"
chartify_analysis_path = "analysis/chartify/function/chartify_predictions_results.csv"
chartify_breakdown_path = "analysis/chartify/function/chartify_breakdown.json"

chartify_ground_truth_class_path = "ground_truth_data/chartify/class/chartify_ground_truth_classes.json"
chartify_class_level_analysis_path = "analysis/chartify/class/chartify_predictions_class_results.csv"
chartify_class_level_breakdown_path = "analysis/chartify/class/chartify_class_breakdown.json"
chartify_ground_truth_function_class_path = "ground_truth_data/chartify/class/chartify_all_function_class_names.txt"
chartify_ground_truth_test_class_path = "ground_truth_data/chartify/class/chartify_all_test_class_names.txt"

if __name__ == "__main__":
    analyse_trace_class_level(pyopenssl_tracer_logs_path, pyopenssl_ground_truth_class_path, pyopenssl_class_level_analysis_path, pyopenssl_class_level_breakdown_path, pyopenssl_ground_truth_function_class_path, pyopenssl_ground_truth_test_class_path)
    analyse_trace_class_level(arrow_tracer_logs_path, arrow_ground_truth_class_path, arrow_class_level_analysis_path, arrow_class_level_breakdown_path, arrow_ground_truth_function_class_path, arrow_ground_truth_test_class_path)
    analyse_trace_class_level(kedro_tracer_logs_path, kedro_ground_truth_class_path, kedro_class_level_analysis_path, kedro_class_level_breakdown_path, kedro_ground_truth_function_class_path, kedro_ground_truth_test_class_path)
    analyse_trace(pyopenssl_tracer_logs_path, pyopenssl_ground_truth_path, pyopenssl_analysis_path, pyopenssl_breakdown_path)
    analyse_trace(arrow_tracer_logs_path, arrow_ground_truth_path, arrow_analysis_path, arrow_breakdown_path)
    analyse_trace(kedro_tracer_logs_path, kedro_ground_truth_path, kedro_analysis_path, kedro_breakdown_path)
    analyse_trace(chartify_tracer_logs_path, chartify_ground_truth_path, chartify_analysis_path, chartify_breakdown_path)
    analyse_trace_class_level(chartify_tracer_logs_path, chartify_ground_truth_class_path, chartify_class_level_analysis_path, chartify_class_level_breakdown_path, chartify_ground_truth_function_class_path, chartify_ground_truth_test_class_path)
