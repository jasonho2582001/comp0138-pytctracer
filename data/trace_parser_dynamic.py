from collections import defaultdict
from typing import Optional, Set, List, Dict, Tuple
from math import log
import csv
import json
import sys
from sklearn.metrics import precision_recall_curve, auc

csv.field_size_limit(sys.maxsize)

THRESHOLD_FOR_LCSU = 0.75
THRESHOLD_FOR_LCSB = 0.65
THRESHOLD_FOR_LEVENSHTEIN = 0.95
THRESHOLD_FOR_TARANTULA = 0.95
THRESHOLD_FOR_TFIDF = 0.9
THRESHOLD_FOR_TFIDF_COUNT = 0.9
THRESHOLD_FOR_AVERAGE = sum(threshold_arr := [THRESHOLD_FOR_LCSU, THRESHOLD_FOR_LCSB, THRESHOLD_FOR_TFIDF_COUNT, THRESHOLD_FOR_LEVENSHTEIN, THRESHOLD_FOR_TARANTULA, THRESHOLD_FOR_TFIDF])/len(threshold_arr)
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


def extract_function_class_and_test_class_names_tuple(data: List[Dict[str, str]]) -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    test_class_names_tuple = set([(record["Fully Qualified Class Name"], record["Class Name"]) for record in data if record["Testing Method"] == "TEST METHOD CALL" and record["Class Name"]])
    function_class_names_tuple = set([(record["Fully Qualified Class Name"], record["Class Name"]) for record in data if record["Function Type"] == "SOURCE" and record["Class Name"]])

    return function_class_names_tuple, test_class_names_tuple

def find_function_classes_called_by_each_test_class(data: List[Dict[str, str]]) -> Dict[str, Set[str]]:
    function_classes_called_by_each_test_classes_dict = defaultdict(set)
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Class Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test and record["Function Type"] == "SOURCE" and record["Fully Qualified Class Name"]:
            function_classes_called_by_each_test_classes_dict[current_test].add(record["Fully Qualified Class Name"])
    
    return function_classes_called_by_each_test_classes_dict


def find_function_classes_called_by_each_test_class_count(data: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    function_classes_called_by_each_test_classes_count_dict = defaultdict(lambda: defaultdict(int))
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Class Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test and record["Function Type"] == "SOURCE" and record["Fully Qualified Class Name"] and record["Event Type"] == "CALL":
            function_classes_called_by_each_test_classes_count_dict[current_test][record["Fully Qualified Class Name"]] += 1
    
    return function_classes_called_by_each_test_classes_count_dict


def find_test_classes_that_call_each_function_class(data: List[Dict[str, str]]) -> Dict[str, Set[str]]:
    test_classes_that_call_each_function_class_dict = defaultdict(set)
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Class Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test and record["Function Type"] == "SOURCE" and record["Fully Qualified Class Name"]:
            test_classes_that_call_each_function_class_dict[record["Fully Qualified Class Name"]].add(current_test)

    return test_classes_that_call_each_function_class_dict


def find_depths_of_function_classes_called_by_each_test_class(data: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
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
        elif current_test_class is not None and record["Function Type"] == "SOURCE" and record["Fully Qualified Class Name"]:
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

def find_functions_called_by_each_test_count(data: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    functions_called_by_each_test_dict_count = defaultdict(lambda: defaultdict(int))
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Function Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test is not None and record["Function Type"] == "SOURCE" and record["Event Type"] == "CALL":
            functions_called_by_each_test_dict_count[current_test][record["Fully Qualified Function Name"]] += 1
    
    return functions_called_by_each_test_dict_count

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
            naming_conventions_dict[test_fully_qualified_name][function_fully_qualified_name] = (1 if function_name == stripped_test_function_name else 0) if function_fully_qualified_name in functions_called_by_test else 0
    
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
            naming_conventions_contains_dict[test_fully_qualified_name][function_fully_qualified_name] = (1 if function_name in stripped_test_function_name else 0) if function_fully_qualified_name in functions_called_by_test else 0
    
    return naming_conventions_contains_dict

def normalise_dict(result_dict: Dict[str, Dict[str, float]], functions_called_by_each_test_dict: Dict[str, Set[str]]) -> Dict[str, Dict[str, float]]:
    normalised_result_dict = {test: function_results.copy() for test, function_results in result_dict.items()}

    for test_fully_qualified_name in result_dict:
        # find maximum score and normalise w.r.t to it
        functions_called_by_test = result_dict[test_fully_qualified_name]
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
        if test_fully_qualified_name == "tests.test_crypto._PKeyInteractionTestsMixin":
            print(test_function_name)
        functions_called_by_test = functions_called_by_each_test_dict[test_fully_qualified_name]
        for function_fully_qualified_name, function_name in function_names_tuple:
            if test_function_name.startswith("test_"):
                stripped_test_function_name = test_function_name[5:]
            else:
                # assumption that all test functions must begin with test
                stripped_test_function_name = test_function_name[4:]

            lcsb_result = (find_lcs(stripped_test_function_name, function_name))/(max(len(stripped_test_function_name), len(function_name))) if function_fully_qualified_name in functions_called_by_test else 0
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

            lcsu_result = (find_lcs(stripped_test_function_name, function_name))/len(function_name) if function_fully_qualified_name in functions_called_by_test else 0
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
            levenshtein_result = (1 - (find_levenshtein_distance(stripped_test_function_name, function_name))/(max(len(stripped_test_function_name), len(function_name)))) if function_fully_qualified_name in functions_called_by_test else 0
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
        elif current_test and last_returned_function and record["Function Type"] == "ASSERT":
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


def tfidf_count(functions_called_by_each_test_count_dict: Dict[str, Dict[str, int]], tests_that_call_each_function_dict: Dict[str, Set[str]], function_names: Set[str], test_names: Set[str], depths_of_functions_called_by_each_test_dict: Dict[str, Dict[str, int]]) -> Dict[str, Dict[str, float]]:
    number_of_tests = len(test_names)
    idf_set = {}

    tfidf_dict = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}

    for function_name in tests_that_call_each_function_dict:
        number_of_tests_that_call_function = len(tests_that_call_each_function_dict[function_name])
        # number_of_tests_that_call_function = 0 
        # for test_name in tests_that_call_each_function_dict[function_name]:
        #     number_of_tests_that_call_function += functions_called_by_each_test_count_dict[test_name][function_name]
        idf_set[function_name] = log(1 + number_of_tests/(number_of_tests_that_call_function))
    
    for test_name in functions_called_by_each_test_count_dict:
        number_of_functions_called_by_test = sum(functions_called_by_each_test_count_dict[test_name].values())
        for function_name in functions_called_by_each_test_count_dict[test_name]:
            number_of_times_function_called = functions_called_by_each_test_count_dict[test_name][function_name]
            tf = log(1+number_of_times_function_called/(number_of_functions_called_by_test))
            tfidf_dict[test_name][function_name] = tf * idf_set[function_name]
    
    return normalise_dict(use_call_depth_discounting_dict(tfidf_dict, depths_of_functions_called_by_each_test_dict), functions_called_by_each_test_count_dict)


def find_average_score(result_dicts: List[Dict[str, Dict[str, float]]], function_names: Set[str], test_names: Set[str], functions_called_by_each_test_dict: Dict[str, Set[str]]) -> Dict[str, Dict[str, float]]:
    average_score_dict = None
    num_of_result_dicts = 9
    for result_dict in result_dicts:
        if average_score_dict is None:
            average_score_dict = defaultdict(lambda: defaultdict(float))
        for test_name, res in result_dict.items():
            for function_name, score in res.items():
                average_score_dict[test_name][function_name] += score/num_of_result_dicts
    
    return normalise_dict(average_score_dict, functions_called_by_each_test_dict)

def generate_predicted_links(dict_result: Dict[str, Dict[str, float]], threshold: Optional[float] = 1, tests_to_create_links_for: Optional[Set[str]] = None) -> Dict[str, Set[str]]:
    if tests_to_create_links_for is None:
        tests_to_create_links_for = set(dict_result.keys())
    
    predicted_links_dict = {test_name: [] for test_name in tests_to_create_links_for}

    for fully_qualified_test_name, results_for_test_dict in dict_result.items():
        predicted_functions_and_score = []
        if fully_qualified_test_name in tests_to_create_links_for:
            for fully_qualified_function_name, score in results_for_test_dict.items():
                if score >= threshold:
                    predicted_functions_and_score.append((fully_qualified_function_name, score))
            predicted_functions_and_score.sort(key=lambda x: x[1], reverse=True)
            predicted_functions_for_test = [function_name for function_name, _ in predicted_functions_and_score]
            predicted_links_dict[fully_qualified_test_name] = predicted_functions_for_test
    
    return predicted_links_dict

def calculate_auc(dict_result: Dict[str, Dict[str, float]], ground_truth_links: Dict[str, List[str]]) -> float:
    ground_truth_labels = []
    predicted_labels = []

    for test in ground_truth_links.keys():
        ground_truth_set = set(ground_truth_links[test])
        for function in dict_result[test]:
            ground_truth_labels.append(1 if function in ground_truth_set else 0)
            predicted_labels.append(dict_result[test][function])

    precision, recall, _ = precision_recall_curve(ground_truth_labels, predicted_labels)

    auc_score = 100 * auc(recall, precision)

    return auc_score

def calculate_map(predicted_links: Dict[str, List[str]], ground_truth_links: Dict[str, List[str]]) -> float:
    # Initialize total AP
    total_ap = 0

    # For each test
    for test in ground_truth_links.keys():
        # Get the true links for this test
        true_links = set(ground_truth_links[test])

        # Get the predicted links for this test
        predicted_links_for_test = predicted_links[test]

        # Initialize count of true links and sum of precisions
        count_true_links = 0
        sum_precisions = 0

        # For each link in the predicted links
        for i, link in enumerate(predicted_links_for_test):
            # If this link is a true link
            if link in true_links:
                # Increment count of true links
                count_true_links += 1

                # Calculate precision at this rank and add to sum of precisions
                precision = count_true_links / (i + 1)
                sum_precisions += precision

        # Calculate AP for this test and add to total AP
        ap = sum_precisions / len(true_links)
        total_ap += ap

    # Calculate MAP
    map_score = 100 * total_ap / len(ground_truth_links)

    return map_score

def calculate_evalution_measures(predicted_links: Dict[str, List[str]], ground_truth_links: Dict[str, List[str]], result_dict: Optional[Dict[str, Dict[str, float]]] = None) -> Tuple[Dict[str, float], Dict[str, Dict[str, str]]]:
    breakdown_dict = defaultdict(dict)
    found_true_positives = 0
    found_false_positives = 0
    found_false_negatives = 0
    total_true_links = 0
    for fully_qualified_test_name in predicted_links:
        predicted_links_for_test = set(predicted_links[fully_qualified_test_name])
        ground_truth_links_for_test = set(ground_truth_links[fully_qualified_test_name])
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

    evaluation_dict["MAP"] = calculate_map(predicted_links, ground_truth_links)

    if result_dict:
        evaluation_dict["AUC"] = calculate_auc(result_dict, ground_truth_links)
    else:
        evaluation_dict["AUC"] = "-"

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
                row[metric] = score if not isinstance(score, float) else round(score, 1)
            csv_writer.writerow(row)

def print_combined_evaluation_results(combined_evaluation_dict: Dict[str, Dict[str, float]], title: str) -> None:
    print(f"{'='*15} {title} {'='*15}\n")
    for technique, evaluation_dict in combined_evaluation_dict.items():
        print(f"{'='*5} {technique} {'='*5}")
        for metric, score in evaluation_dict.items():
            if isinstance(score, float):
                print(f"{metric}: {score:.5f}")
            else:
                print(f"{metric}: {score}")
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

def write_breakdown_dict_to_json(breakdown_dict: Dict[str, Dict[str, str]], file_path: str, sort_keys: bool = True) -> None:
    with open(file_path, "w") as file:
        json.dump(breakdown_dict, file, indent=4, sort_keys=sort_keys)

def load_link_json(link_path: str) -> Dict[str, List[str]]:
    with open(link_path, "r") as file:
        link_dict = json.load(file)

    return link_dict


def analyse_trace(file_path: str, ground_truth_path: str, analysis_log_output_path: str, breakdown_output_path: str, copilot_prediction_path: str, copilot_breakdown_output_path: str) -> None:
    # PARSE DATA
    ground_truth_dict = load_link_json(ground_truth_path)
    copilot_prediction_dict = load_link_json(copilot_prediction_path)

    columns, data = read_csv_log(file_path)
    function_names_tuple, test_names_tuple = extract_function_and_test_names_tuple(data)
    fully_qualified_function_names = set(fully_qualified_function_name for fully_qualified_function_name, _ in function_names_tuple)
    fully_qualified_test_names = set(fully_qualified_test_name for fully_qualified_test_name, _ in test_names_tuple)
    functions_called_by_each_test_dict = find_functions_called_by_each_test(data)
    functions_called_by_each_test_count_dict = find_functions_called_by_each_test_count(data)
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
    tfidf_count_dict = tfidf_count(functions_called_by_each_test_count_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names, depths_of_functions_called_by_each_test_dict)

    result_dicts = [naming_conventions_dict, naming_convention_contains_dict, lcsb_dict, lcsu_dict, levenshtein_dict, lcba_dict, tarantula_dict, tfidf_dict, tfidf_count_dict]
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
    predicted_links_for_tfidf_count = generate_predicted_links(tfidf_count_dict, THRESHOLD_FOR_TFIDF_COUNT, tests_to_create_links_for)
    predicted_links_for_average = generate_predicted_links(average_dict, 0.85, tests_to_create_links_for)

    evaluation_dict_for_naming_convention, _ = calculate_evalution_measures(predicted_links_for_naming_convention, ground_truth_dict)
    evaluation_dict_for_naming_convention_contains, _  = calculate_evalution_measures(predicted_links_for_naming_convention_contains, ground_truth_dict)
    evaluation_dict_for_lcsb, t  = calculate_evalution_measures(predicted_links_for_lcsb, ground_truth_dict, lcsb_dict)
    evaluation_dict_for_lcsu, a  = calculate_evalution_measures(predicted_links_for_lcsu, ground_truth_dict, lcsu_dict)
    evaluation_dict_for_levenshtein, _  = calculate_evalution_measures(predicted_links_for_levenshtein, ground_truth_dict, levenshtein_dict)
    evaluation_dict_for_lcba, _  = calculate_evalution_measures(predicted_links_for_lcba, ground_truth_dict)
    evaluation_dict_for_tarauntula, _  = calculate_evalution_measures(predicted_links_for_tarantula, ground_truth_dict, tarantula_dict)
    evaluation_dict_for_tfidf, _  = calculate_evalution_measures(predicted_links_for_tfidf, ground_truth_dict, tfidf_dict)
    evaluation_dict_for_tfidf_count, _ = calculate_evalution_measures(predicted_links_for_tfidf_count, ground_truth_dict, tfidf_count_dict)
    evaluation_dict_for_average, breakdown_dict = calculate_evalution_measures(predicted_links_for_average, ground_truth_dict, average_dict)

    evaluation_dict_for_copilot, copilot_breakdown_dict = calculate_evalution_measures(copilot_prediction_dict, ground_truth_dict)

    combined_evaluation_dict["Naming Conventions"] = evaluation_dict_for_naming_convention
    combined_evaluation_dict["Naming Conventions - Contains"] = evaluation_dict_for_naming_convention_contains
    combined_evaluation_dict["Longest Common Subsequence - Both"] = evaluation_dict_for_lcsb
    combined_evaluation_dict["Longest Common Subsequence - Unit"] = evaluation_dict_for_lcsu
    combined_evaluation_dict["Levenshtein Distance"] = evaluation_dict_for_levenshtein
    combined_evaluation_dict["Last Call Before Assert"] = evaluation_dict_for_lcba
    combined_evaluation_dict["Tarantula"] = evaluation_dict_for_tarauntula
    combined_evaluation_dict["TF-IDF"] = evaluation_dict_for_tfidf
    combined_evaluation_dict["TF-IDF (Multiset)"] = evaluation_dict_for_tfidf_count
    combined_evaluation_dict["Simple Average"] = evaluation_dict_for_average
    combined_evaluation_dict["Copilot"] = evaluation_dict_for_copilot

    # OUTPUT
    # print_predicted_links(predicted_links_for_naming_convention, evaluation_dict_for_naming_convention, "Predicted Links for Naming Convention")
    # print_predicted_links(predicted_links_for_naming_convention, evaluation_dict_for_naming_convention_contains, "Predicted Links for Naming Convention - Contains")
    # print_predicted_links(predicted_links_for_levenshtein, evaluation_dict_for_levenshtein, "Predicted Links for Levenshtein Distance")
    
    print_combined_evaluation_results(combined_evaluation_dict, "Evaluation Metrics")
    write_evaluation_dict_to_csv(combined_evaluation_dict, analysis_log_output_path)
    write_breakdown_dict_to_json(breakdown_dict, breakdown_output_path)
    write_breakdown_dict_to_json(copilot_breakdown_dict, copilot_breakdown_output_path)
    # write_breakdown_dict_to_json(t, "k.json")
    # write_breakdown_dict_to_json(a, "a.json")

def analyse_trace_class_level(file_path: str, ground_truth_path: str, analysis_log_output_path: str, breakdown_output_path: str, ground_truth_function_class_path: str, ground_truth_test_class_path: str, copilot_prediction_path: str, copilot_breakdown_output_path: str) -> None:
    ground_truth_dict = load_link_json(ground_truth_path)
    copilot_prediction_dict = load_link_json(copilot_prediction_path)
    columns, data = read_csv_log(file_path)
    ground_truth_function_class_names, ground_truth_test_class_names = extract_ground_truth_class_names(ground_truth_function_class_path, ground_truth_test_class_path)
    
    function_names_tuple, test_names_tuple = extract_function_class_and_test_class_names_tuple(data)
    fully_qualified_function_names = set(fully_qualified_function_name for fully_qualified_function_name, _ in function_names_tuple)
    fully_qualified_test_names = set(fully_qualified_test_name for fully_qualified_test_name, _ in test_names_tuple)
    functions_called_by_each_test_dict = find_function_classes_called_by_each_test_class(data)
    functions_called_by_each_test_count_dict = find_function_classes_called_by_each_test_class_count(data)
    tests_that_call_each_function_dict = find_test_classes_that_call_each_function_class(data)
    tests_to_create_links_for = set(ground_truth_dict.keys())
    depths_of_functions_called_by_each_test_dict = find_depths_of_function_classes_called_by_each_test_class(data)
    
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
    tfidf_count_dict = tfidf_count(functions_called_by_each_test_count_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names, depths_of_functions_called_by_each_test_dict)
    result_dicts = [naming_conventions_dict, naming_convention_contains_dict, lcsb_dict, lcsu_dict, levenshtein_dict, lcba_dict, tarantula_dict, tfidf_dict, tfidf_count_dict]
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
    predicted_links_for_tfidf_count = generate_predicted_links(tfidf_count_dict, THRESHOLD_FOR_TFIDF_COUNT, tests_to_create_links_for)
    predicted_links_for_average = generate_predicted_links(average_dict, THRESHOLD_FOR_AVERAGE, tests_to_create_links_for)

    evaluation_dict_for_naming_convention, _ = calculate_evalution_measures(predicted_links_for_naming_convention, ground_truth_dict)
    evaluation_dict_for_naming_convention_contains, a  = calculate_evalution_measures(predicted_links_for_naming_convention_contains, ground_truth_dict)
    evaluation_dict_for_lcsb, b = calculate_evalution_measures(predicted_links_for_lcsb, ground_truth_dict, lcsb_dict)
    evaluation_dict_for_lcsu, _  = calculate_evalution_measures(predicted_links_for_lcsu, ground_truth_dict, lcsu_dict)
    evaluation_dict_for_levenshtein, c  = calculate_evalution_measures(predicted_links_for_levenshtein, ground_truth_dict, levenshtein_dict)
    evaluation_dict_for_lcba, _  = calculate_evalution_measures(predicted_links_for_lcba, ground_truth_dict)
    evaluation_dict_for_tarauntula, _  = calculate_evalution_measures(predicted_links_for_tarantula, ground_truth_dict, tarantula_dict)
    evaluation_dict_for_tfidf, _  = calculate_evalution_measures(predicted_links_for_tfidf, ground_truth_dict, tfidf_dict)
    evaluation_dict_for_tfidf_count, _  = calculate_evalution_measures(predicted_links_for_tfidf_count, ground_truth_dict, tfidf_count_dict)
    evaluation_dict_for_average, breakdown_dict = calculate_evalution_measures(predicted_links_for_average, ground_truth_dict, average_dict)
    evaluation_dict_for_copilot, copilot_breakdown_dict = calculate_evalution_measures(copilot_prediction_dict, ground_truth_dict)

    combined_evaluation_dict["Naming Conventions"] = evaluation_dict_for_naming_convention
    combined_evaluation_dict["Naming Conventions - Contains"] = evaluation_dict_for_naming_convention_contains
    combined_evaluation_dict["Longest Common Subsequence - Both"] = evaluation_dict_for_lcsb
    combined_evaluation_dict["Longest Common Subsequence - Unit"] = evaluation_dict_for_lcsu
    combined_evaluation_dict["Levenshtein Distance"] = evaluation_dict_for_levenshtein
    combined_evaluation_dict["Last Call Before Assert"] = evaluation_dict_for_lcba
    combined_evaluation_dict["Tarantula"] = evaluation_dict_for_tarauntula
    combined_evaluation_dict["TF-IDF"] = evaluation_dict_for_tfidf
    combined_evaluation_dict["TF-IDF (Multiset)"] = evaluation_dict_for_tfidf_count
    combined_evaluation_dict["Simple Average"] = evaluation_dict_for_average
    combined_evaluation_dict["Copilot"] = evaluation_dict_for_copilot

    # OUTPUT
    # print_predicted_links(predicted_links_for_naming_convention, evaluation_dict_for_naming_convention, "Predicted Links for Naming Convention")
    # print_predicted_links(predicted_links_for_naming_convention, evaluation_dict_for_naming_convention_contains, "Predicted Links for Naming Convention - Contains")
    # print_predicted_links(predicted_links_for_levenshtein, evaluation_dict_for_levenshtein, "Predicted Links for Levenshtein Distance")
    
    print_combined_evaluation_results(combined_evaluation_dict, "Evaluation Metrics")
    write_evaluation_dict_to_csv(combined_evaluation_dict, analysis_log_output_path)
    write_breakdown_dict_to_json(breakdown_dict, breakdown_output_path)
    write_breakdown_dict_to_json(copilot_breakdown_dict, copilot_breakdown_output_path)
    write_breakdown_dict_to_json(a, "a.json")
    write_breakdown_dict_to_json(b, "b.json")
    write_breakdown_dict_to_json(c, "c.json")

import matplotlib.pyplot as plt

def vary_threshold():
    file_paths = ["tracing-logs/kedro/kedro_pytest_tracer_logs.csv", 
                  "tracing-logs/arrow/arrow_pytest_tracer_logs.csv", 
                  "tracing-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv",
                  "tracing-logs/chartify/chartify_pytest_tracer_logs.csv"]
    ground_truth_paths = ["ground-truth-data/kedro/function/kedro_ground_truth.json",
                          "ground-truth-data/arrow/function/arrow_ground_truth.json",
                          "ground-truth-data/pyopenssl/function/pyopenssl_ground_truth.json",
                          "ground-truth-data/chartify/function/chartify_ground_truth.json"]

    lcsb_dicts = []
    lcsu_dicts = []
    levenshtein_dicts = []
    tarantula_dicts = []
    tfidf_dicts = []
    tfidf_count_dicts = []
    average_dicts = []

    for i in range(4):
        file_path = file_paths[i]
        ground_truth_path = ground_truth_paths[i]
        ground_truth_dict = load_link_json(ground_truth_path)

        columns, data = read_csv_log(file_path)
        function_names_tuple, test_names_tuple = extract_function_and_test_names_tuple(data)
        functions_called_by_each_test_dict = find_functions_called_by_each_test(data)
        fully_qualified_function_names = set(fully_qualified_function_name for fully_qualified_function_name, _ in function_names_tuple)
        fully_qualified_test_names = set(fully_qualified_test_name for fully_qualified_test_name, _ in test_names_tuple)
        functions_called_by_each_test_count_dict = find_functions_called_by_each_test_count(data)
        tests_that_call_each_function_dict = find_tests_that_call_each_function(data)
        tests_to_create_links_for = set(ground_truth_dict.keys())
        depths_of_functions_called_by_each_test_dict = find_depths_of_functions_called_by_each_test(data)

        lcsb_dict = longest_common_subsequence_both(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict, depths_of_functions_called_by_each_test_dict)
        naming_conventions_dict = naming_conventions(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
        naming_convention_contains_dict = naming_convention_contains(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
        lcsb_dict = longest_common_subsequence_both(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict, depths_of_functions_called_by_each_test_dict)
        lcsu_dict = longest_common_subsequence_unit(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict, depths_of_functions_called_by_each_test_dict)
        levenshtein_dict = levenshtein_distance(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict, depths_of_functions_called_by_each_test_dict)
        lcba_dict = last_call_before_assert_class(data, fully_qualified_function_names, fully_qualified_test_names)
        tarantula_dict = tarantula(functions_called_by_each_test_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names, depths_of_functions_called_by_each_test_dict)
        tfidf_dict = tfidf(functions_called_by_each_test_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names, depths_of_functions_called_by_each_test_dict)
        tfidf_count_dict = tfidf_count(functions_called_by_each_test_count_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names, depths_of_functions_called_by_each_test_dict)
        result_dicts = [naming_conventions_dict, naming_convention_contains_dict, lcsb_dict, lcsu_dict, levenshtein_dict, lcba_dict, tarantula_dict, tfidf_dict, tfidf_count_dict]
        average_dict = find_average_score(result_dicts, fully_qualified_function_names, fully_qualified_test_names, functions_called_by_each_test_dict)

        # PRODUCING PREDICTIONS

        lcsb_res_dict = defaultdict(list)
        thresholds = [i/100 for i in range(1, 101, 1)]
        for threshold in thresholds:
            predicted_links_for_lcsb = generate_predicted_links(lcsb_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_lcsb, t  = calculate_evalution_measures(predicted_links_for_lcsb, ground_truth_dict, lcsb_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_lcsb[metric]
                lcsb_res_dict[metric].append(score)
    
        lcsb_dicts.append(lcsb_res_dict)

        lcsu_res_dict = defaultdict(list)
        thresholds = [i/100 for i in range(1, 101, 1)]
        for threshold in thresholds:
            predicted_links_for_lcsu = generate_predicted_links(lcsu_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_lcsu, t  = calculate_evalution_measures(predicted_links_for_lcsu, ground_truth_dict, lcsu_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_lcsu[metric]
                lcsu_res_dict[metric].append(score)
    
        lcsu_dicts.append(lcsu_res_dict)
        thresholds = [i/100 for i in range(1, 101, 1)]
        levenshtein_res_dict = defaultdict(list)

        for threshold in thresholds:
            predicted_links_for_levenshtein = generate_predicted_links(levenshtein_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_levenshtein, t  = calculate_evalution_measures(predicted_links_for_levenshtein, ground_truth_dict, levenshtein_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_levenshtein[metric]
                levenshtein_res_dict[metric].append(score)
    
        levenshtein_dicts.append(levenshtein_res_dict)

        tarantula_res_dict = defaultdict(list)

        for threshold in thresholds:
            predicted_links_for_tarantula = generate_predicted_links(tarantula_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_tarantula, t  = calculate_evalution_measures(predicted_links_for_tarantula, ground_truth_dict, tarantula_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_tarantula[metric]
                tarantula_res_dict[metric].append(score)
    
        tarantula_dicts.append(tarantula_res_dict)

        tfidf_res_dict = defaultdict(list)
        
        for threshold in thresholds:
            predicted_links_for_tfidf = generate_predicted_links(tfidf_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_tfidf, t  = calculate_evalution_measures(predicted_links_for_tfidf, ground_truth_dict, tfidf_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_tfidf[metric]
                tfidf_res_dict[metric].append(score)
    
        tfidf_dicts.append(tfidf_res_dict)


        tfidf_count_res_dict = defaultdict(list)
        
        for threshold in thresholds:
            predicted_links_for_tfidf_count = generate_predicted_links(tfidf_count_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_tfidf_count, t  = calculate_evalution_measures(predicted_links_for_tfidf_count, ground_truth_dict, tfidf_count_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_tfidf_count[metric]
                tfidf_count_res_dict[metric].append(score)
    
        tfidf_count_dicts.append(tfidf_count_res_dict)

        average_res_dict = defaultdict(list)
        
        for threshold in thresholds:
            predicted_links_for_average = generate_predicted_links(average_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_average, t  = calculate_evalution_measures(predicted_links_for_average, ground_truth_dict, average_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_average[metric]
                average_res_dict[metric].append(score)
    
        average_dicts.append(average_res_dict)
    
    def plot_threshold_sensitivity(dicts, normal_threshold, title):
        final_res_dict = defaultdict(list)
        for metric in ["Precision", "Recall", "F1", "MAP"]:
            res_lists = []
            for res_dict in dicts:
                res_lists.append(res_dict[metric])
            for i in range(len(res_lists[0])):
                s = 0
                for j in range(len(res_lists)):
                    s += res_lists[j][i]
                s /= len(res_lists)
                final_res_dict[metric].append(s)

        plt.figure(figsize=(10, 6))

        # Use the 'seaborn' style
        plt.style.use('ggplot')

        # For each metric
        for metric in ["Precision", "Recall", "F1", "MAP"]:
            # Plot the metric values against the threshold values with increased line width
            plt.plot(thresholds, final_res_dict[metric], label=metric, linewidth=2)

        # Add a vertical line at threshold 0.5
        plt.axvline(x=normal_threshold, color='black', linestyle='--', label=f't = {normal_threshold}')
        # Set the x-axis range to [0, 1]
        plt.xlim([0, 1])
        font = {
                'weight': 'normal',
                'size': 14,
                'style': 'italic'}
        # Set the y-axis range to [0, 1]
        plt.ylim([0, 100])
        plt.xticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        # Add labels and title with increased font size
        plt.xlabel('Threshold', fontdict=font)
        plt.ylabel('Value',  fontdict=font)
        plt.title(title, fontsize=16)

        # Add a legend
        plt.legend()

        # Add a grid
        plt.grid(True)
        plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
        # Show the plot
        plt.show()
    
    plot_threshold_sensitivity(lcsb_dicts, THRESHOLD_FOR_LCSB, "Threshold Sensitivity for LCS-B (Function Level)")
    plot_threshold_sensitivity(lcsu_dicts, THRESHOLD_FOR_LCSU, "Threshold Sensitivity for LCS-U (Function Level)")
    plot_threshold_sensitivity(levenshtein_dicts, THRESHOLD_FOR_LEVENSHTEIN, "Threshold Sensitivity for Levenshtein (Function Level)")
    plot_threshold_sensitivity(tarantula_dicts, THRESHOLD_FOR_TARANTULA, "Threshold Sensitivity for Tarantula (Function Level)")
    plot_threshold_sensitivity(tfidf_dicts, THRESHOLD_FOR_TFIDF, "Threshold Sensitivity for TF-IDF (Function Level)")
    plot_threshold_sensitivity(tfidf_count_dicts, THRESHOLD_FOR_TFIDF_COUNT, "Threshold Sensitivity for TF-IDF* (Function Level)")
    plot_threshold_sensitivity(average_dicts, THRESHOLD_FOR_AVERAGE, "Threshold Sensitivity for Combined (Function Level)")


def vary_threshold_class():
    file_paths = ["tracing-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv",
                    "tracing-logs/arrow/arrow_pytest_tracer_logs.csv",
                  "tracing-logs/kedro/kedro_pytest_tracer_logs.csv", 
                  "tracing-logs/chartify/chartify_pytest_tracer_logs.csv"]
    ground_truth_paths = ["ground-truth-data/pyopenssl/class/pyopenssl_ground_truth_classes.json",
                          "ground-truth-data/arrow/class/arrow_ground_truth_classes.json",
                          "ground-truth-data/kedro/class/kedro_ground_truth_classes.json",
                          "ground-truth-data/chartify/class/chartify_ground_truth_classes.json"]
    ground_truth_function_class_paths = ["ground-truth-data/pyopenssl/class/pyopenssl_all_function_class_names.txt",
                                            "ground-truth-data/arrow/class/arrow_all_function_class_names.txt",
                                            "ground-truth-data/kedro/class/kedro_all_function_class_names.txt",
                                            "ground-truth-data/chartify/class/chartify_all_function_class_names.txt"]
    
    ground_truth_test_class_paths = ["ground-truth-data/pyopenssl/class/pyopenssl_all_test_class_names.txt",
                                        "ground-truth-data/arrow/class/arrow_all_test_class_names.txt",
                                        "ground-truth-data/kedro/class/kedro_all_test_class_names.txt",
                                        "ground-truth-data/chartify/class/chartify_all_test_class_names.txt"]
    lcsb_dicts = []
    lcsu_dicts = []
    levenshtein_dicts = []
    tarantula_dicts = []
    tfidf_dicts = []
    tfidf_count_dicts = []
    average_dicts = []

    for i in range(4):
        file_path = file_paths[i]
        ground_truth_path = ground_truth_paths[i]
        ground_truth_dict = load_link_json(ground_truth_path)
        ground_truth_function_class_path = ground_truth_function_class_paths[i]
        ground_truth_test_class_path = ground_truth_test_class_paths[i]
        columns, data = read_csv_log(file_path)
        ground_truth_function_class_names, ground_truth_test_class_names = extract_ground_truth_class_names(ground_truth_function_class_path, ground_truth_test_class_path)
        
        function_names_tuple, test_names_tuple = extract_function_class_and_test_class_names_tuple(data, ground_truth_function_class_names, ground_truth_test_class_names)
        fully_qualified_function_names = set(fully_qualified_function_name for fully_qualified_function_name, _ in function_names_tuple)
        fully_qualified_test_names = set(fully_qualified_test_name for fully_qualified_test_name, _ in test_names_tuple)
        functions_called_by_each_test_dict = find_function_classes_called_by_each_test_class(data, ground_truth_function_class_names, ground_truth_test_class_names)
        functions_called_by_each_test_count_dict = find_function_classes_called_by_each_test_class_count(data, ground_truth_function_class_names, ground_truth_test_class_names)
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
        tfidf_count_dict = tfidf_count(functions_called_by_each_test_count_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names, depths_of_functions_called_by_each_test_dict)
        result_dicts = [naming_conventions_dict, naming_convention_contains_dict, lcsb_dict, lcsu_dict, levenshtein_dict, lcba_dict, tarantula_dict, tfidf_dict, tfidf_count_dict]
        average_dict = find_average_score(result_dicts, fully_qualified_function_names, fully_qualified_test_names, functions_called_by_each_test_dict)


        lcsb_res_dict = defaultdict(list)
        thresholds = [i/100 for i in range(1, 101, 1)]
        for threshold in thresholds:
            predicted_links_for_lcsb = generate_predicted_links(lcsb_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_lcsb, t  = calculate_evalution_measures(predicted_links_for_lcsb, ground_truth_dict, lcsb_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_lcsb[metric]
                lcsb_res_dict[metric].append(score)
    
        lcsb_dicts.append(lcsb_res_dict)

        lcsu_res_dict = defaultdict(list)
        thresholds = [i/100 for i in range(1, 101, 1)]
        for threshold in thresholds:
            predicted_links_for_lcsu = generate_predicted_links(lcsu_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_lcsu, t  = calculate_evalution_measures(predicted_links_for_lcsu, ground_truth_dict, lcsu_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_lcsu[metric]
                lcsu_res_dict[metric].append(score)
    
        lcsu_dicts.append(lcsu_res_dict)
        thresholds = [i/100 for i in range(1, 101, 1)]
        levenshtein_res_dict = defaultdict(list)

        for threshold in thresholds:
            predicted_links_for_levenshtein = generate_predicted_links(levenshtein_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_levenshtein, t  = calculate_evalution_measures(predicted_links_for_levenshtein, ground_truth_dict, levenshtein_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_levenshtein[metric]
                levenshtein_res_dict[metric].append(score)
    
        levenshtein_dicts.append(levenshtein_res_dict)

        tarantula_res_dict = defaultdict(list)

        for threshold in thresholds:
            predicted_links_for_tarantula = generate_predicted_links(tarantula_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_tarantula, t  = calculate_evalution_measures(predicted_links_for_tarantula, ground_truth_dict, tarantula_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_tarantula[metric]
                tarantula_res_dict[metric].append(score)
    
        tarantula_dicts.append(tarantula_res_dict)

        tfidf_res_dict = defaultdict(list)
        
        for threshold in thresholds:
            predicted_links_for_tfidf = generate_predicted_links(tfidf_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_tfidf, t  = calculate_evalution_measures(predicted_links_for_tfidf, ground_truth_dict, tfidf_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_tfidf[metric]
                tfidf_res_dict[metric].append(score)
    
        tfidf_dicts.append(tfidf_res_dict)


        tfidf_count_res_dict = defaultdict(list)
        
        for threshold in thresholds:
            predicted_links_for_tfidf_count = generate_predicted_links(tfidf_count_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_tfidf_count, t  = calculate_evalution_measures(predicted_links_for_tfidf_count, ground_truth_dict, tfidf_count_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_tfidf_count[metric]
                tfidf_count_res_dict[metric].append(score)
    
        tfidf_count_dicts.append(tfidf_count_res_dict)

        average_res_dict = defaultdict(list)
        
        for threshold in thresholds:
            predicted_links_for_average = generate_predicted_links(average_dict, threshold, tests_to_create_links_for)
            evaluation_dict_for_average, t  = calculate_evalution_measures(predicted_links_for_average, ground_truth_dict, average_dict)
            for metric in ["Precision", "Recall", "F1", "MAP"]:
                score = evaluation_dict_for_average[metric]
                average_res_dict[metric].append(score)
    
        average_dicts.append(average_res_dict)
    
    def plot_threshold_sensitivity(dicts, normal_threshold, title):
        final_res_dict = defaultdict(list)
        for metric in ["Precision", "Recall", "F1", "MAP"]:
            res_lists = []
            for res_dict in dicts:
                res_lists.append(res_dict[metric])
            for i in range(len(res_lists[0])):
                s = 0
                for j in range(len(res_lists)):
                    s += res_lists[j][i]
                s /= len(res_lists)
                final_res_dict[metric].append(s)

        plt.figure(figsize=(10, 6))

        # Use the 'seaborn' style
        plt.style.use('ggplot')

        # For each metric
        for metric in ["Precision", "Recall", "F1", "MAP"]:
            # Plot the metric values against the threshold values with increased line width
            plt.plot(thresholds, final_res_dict[metric], label=metric, linewidth=2)

        # Add a vertical line at threshold 0.5
        plt.axvline(x=normal_threshold, color='black', linestyle='--', label=f't = {normal_threshold}')
        # Set the x-axis range to [0, 1]
        plt.xlim([0, 1])
        font = {
                'weight': 'normal',
                'size': 14,
                'style': 'italic'}
        # Set the y-axis range to [0, 1]
        plt.ylim([0, 100])
        plt.xticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        plt.yticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        # Add labels and title with increased font size
        plt.xlabel('Threshold', fontdict=font)
        plt.ylabel('Value',  fontdict=font)
        plt.title(title, fontsize=16)

        # Add a legend
        plt.legend()

        # Add a grid
        plt.grid(True)
        plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
        # Show the plot
        plt.show()
    
    plot_threshold_sensitivity(lcsb_dicts, THRESHOLD_FOR_LCSB, "Threshold Sensitivity for LCS-B (Class Level)")
    plot_threshold_sensitivity(lcsu_dicts, THRESHOLD_FOR_LCSU, "Threshold Sensitivity for LCS-U (Class Level)")
    plot_threshold_sensitivity(levenshtein_dicts, THRESHOLD_FOR_LEVENSHTEIN, "Threshold Sensitivity for Levenshtein (Class Level)")
    plot_threshold_sensitivity(tarantula_dicts, THRESHOLD_FOR_TARANTULA, "Threshold Sensitivity for Tarantula (Class Level)")
    plot_threshold_sensitivity(tfidf_dicts, THRESHOLD_FOR_TFIDF, "Threshold Sensitivity for TF-IDF (Class Level)")
    plot_threshold_sensitivity(tfidf_count_dicts, THRESHOLD_FOR_TFIDF_COUNT, "Threshold Sensitivity for TF-IDF* (Class Level)")
    plot_threshold_sensitivity(average_dicts, THRESHOLD_FOR_AVERAGE, "Threshold Sensitivity for Combined (Class Level)")



kedro_tracer_logs_path = "tracing-logs/kedro/kedro_pytest_tracer_logs.csv"
kedro_ground_truth_path = "ground-truth-data/kedro/function/kedro_ground_truth.json"
kedro_analysis_path = "analysis/kedro/function/kedro_predictions_results.csv"
kedro_breakdown_path = "analysis/kedro/function/kedro_breakdown.json"
kedro_copilot_function_breakdown_path = "analysis/kedro/function/kedro_copilot_breakdown.json"
kedro_copilot_class_breakdown_path = "analysis/kedro/class/kedro_copilot_class_breakdown.json"

kedro_ground_truth_class_path = "ground-truth-data/kedro/class/kedro_ground_truth_classes.json"
kedro_class_level_analysis_path = "analysis/kedro/class/kedro_class_predictions_results.csv"
kedro_class_level_breakdown_path = "analysis/kedro/class/kedro_class_breakdown.json"
kedro_ground_truth_function_class_path = "ground-truth-data/kedro/class/kedro_all_function_class_names.txt"
kedro_ground_truth_test_class_path = "ground-truth-data/kedro/class/kedro_all_test_class_names.txt"
kedro_copilot_function_prediction_path = "copilot-predictions/kedro/function/kedro_copilot_function_predictions.json"
kedro_copilot_class_prediction_path = "copilot-predictions/kedro/class/kedro_copilot_class_predictions.json"

arrow_tracer_logs_path = "tracing-logs/arrow/arrow_pytest_tracer_logs.csv"
arrow_ground_truth_path = "ground-truth-data/arrow/function/arrow_ground_truth.json"
arrow_analysis_path = "analysis/arrow/function/arrow_predictions_results.csv"
arrow_breakdown_path = "analysis/arrow/function/arrow_breakdown.json"
arrow_copilot_function_breakdown_path = "analysis/arrow/function/arrow_copilot_breakdown.json"
arrow_copilot_class_breakdown_path = "analysis/arrow/class/arrow_copilot_class_breakdown.json"

arrow_ground_truth_class_path = "ground-truth-data/arrow/class/arrow_ground_truth_classes.json"
arrow_class_level_analysis_path = "analysis/arrow/class/arrow_predictions_class_results.csv"
arrow_class_level_breakdown_path = "analysis/arrow/class/arrow_class_breakdown.json"
arrow_ground_truth_function_class_path = "ground-truth-data/arrow/class/arrow_all_function_class_names.txt"
arrow_ground_truth_test_class_path = "ground-truth-data/arrow/class/arrow_all_test_class_names.txt"
arrow_copilot_function_prediction_path = "copilot-predictions/arrow/function/arrow_copilot_function_predictions.json"
arrow_copilot_class_prediction_path = "copilot-predictions/arrow/class/arrow_copilot_class_predictions.json"


pyopenssl_tracer_logs_path = "tracing-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv"
pyopenssl_ground_truth_path = "ground-truth-data/pyopenssl/function/pyopenssl_ground_truth.json"
pyopenssl_analysis_path = "analysis/pyopenssl/function/pyopenssl_predictions_results.csv"
pyopenssl_breakdown_path = "analysis/pyopenssl/function/pyopenssl_breakdown.json"
pyopenssl_copilot_function_breakdown_path = "analysis/pyopenssl/function/pyopenssl_copilot_breakdown.json"
pyopenssl_copilot_class_breakdown_path = "analysis/pyopenssl/class/pyopenssl_copilot_class_breakdown.json"

pyopenssl_ground_truth_class_path = "ground-truth-data/pyopenssl/class/pyopenssl_ground_truth_classes.json"
pyopenssl_class_level_analysis_path = "analysis/pyopenssl/class/pyopenssl_predictions_class_results.csv"
pyopenssl_class_level_breakdown_path = "analysis/pyopenssl/class/pyopenssl_class_breakdown.json"
pyopenssl_ground_truth_function_class_path = "ground-truth-data/pyopenssl/class/pyopenssl_all_function_class_names.txt"
pyopenssl_ground_truth_test_class_path = "ground-truth-data/pyopenssl/class/pyopenssl_all_test_class_names.txt"
pyopenssl_copilot_function_prediction_path = "copilot-predictions/pyopenssl/function/pyopenssl_copilot_function_predictions.json"
pyopenssl_copilot_class_prediction_path = "copilot-predictions/pyopenssl/class/pyopenssl_copilot_class_predictions.json"

chartify_tracer_logs_path = "tracing-logs/chartify/chartify_pytest_tracer_logs.csv"
chartify_ground_truth_path = "ground-truth-data/chartify/function/chartify_ground_truth.json"
chartify_analysis_path = "analysis/chartify/function/chartify_predictions_results.csv"
chartify_breakdown_path = "analysis/chartify/function/chartify_breakdown.json"
chartify_copilot_function_breakdown_path = "analysis/chartify/function/chartify_copilot_breakdown.json"
chartify_copilot_class_breakdown_path = "analysis/chartify/class/chartify_copilot_class_breakdown.json"

chartify_ground_truth_class_path = "ground-truth-data/chartify/class/chartify_ground_truth_classes.json"
chartify_class_level_analysis_path = "analysis/chartify/class/chartify_predictions_class_results.csv"
chartify_class_level_breakdown_path = "analysis/chartify/class/chartify_class_breakdown.json"
chartify_ground_truth_function_class_path = "ground-truth-data/chartify/class/chartify_all_function_class_names.txt"
chartify_ground_truth_test_class_path = "ground-truth-data/chartify/class/chartify_all_test_class_names.txt"
chartify_copilot_function_prediction_path = "copilot-predictions/chartify/function/chartify_copilot_function_predictions.json"
chartify_copilot_class_prediction_path = "copilot-predictions/chartify/class/chartify_copilot_class_predictions.json"

if __name__ == "__main__":
    # analyse_trace(pyopenssl_tracer_logs_path, pyopenssl_ground_truth_path, pyopenssl_analysis_path, pyopenssl_breakdown_path, pyopenssl_copilot_function_prediction_path, pyopenssl_copilot_function_breakdown_path)
    # analyse_trace(arrow_tracer_logs_path, arrow_ground_truth_path, arrow_analysis_path, arrow_breakdown_path, arrow_copilot_function_prediction_path, arrow_copilot_function_breakdown_path)
    # analyse_trace(kedro_tracer_logs_path, kedro_ground_truth_path, kedro_analysis_path, kedro_breakdown_path, kedro_copilot_function_prediction_path, kedro_copilot_function_breakdown_path)
    # analyse_trace(chartify_tracer_logs_path, chartify_ground_truth_path, chartify_analysis_path, chartify_breakdown_path, chartify_copilot_function_prediction_path, chartify_copilot_function_breakdown_path)
    
    analyse_trace_class_level(pyopenssl_tracer_logs_path, pyopenssl_ground_truth_class_path, pyopenssl_class_level_analysis_path, pyopenssl_class_level_breakdown_path, pyopenssl_ground_truth_function_class_path, pyopenssl_ground_truth_test_class_path, pyopenssl_copilot_class_prediction_path, pyopenssl_copilot_class_breakdown_path)
    # analyse_trace_class_level(arrow_tracer_logs_path, arrow_ground_truth_class_path, arrow_class_level_analysis_path, arrow_class_level_breakdown_path, arrow_ground_truth_function_class_path, arrow_ground_truth_test_class_path, arrow_copilot_class_prediction_path, arrow_copilot_class_breakdown_path)
    # analyse_trace_class_level(kedro_tracer_logs_path, kedro_ground_truth_class_path, kedro_class_level_analysis_path, kedro_class_level_breakdown_path, kedro_ground_truth_function_class_path, kedro_ground_truth_test_class_path, kedro_copilot_class_prediction_path, kedro_copilot_class_breakdown_path)
    # analyse_trace_class_level(chartify_tracer_logs_path, chartify_ground_truth_class_path, chartify_class_level_analysis_path, chartify_class_level_breakdown_path, chartify_ground_truth_function_class_path, chartify_ground_truth_test_class_path, chartify_copilot_class_prediction_path, chartify_copilot_class_breakdown_path)

    # vary_threshold()
    # vary_threshold_class()