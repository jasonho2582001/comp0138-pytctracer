from collections import defaultdict
from typing import Optional, Set, List, Dict, Tuple
from math import log
import csv

def read_csv_log(file_path: str) -> Tuple[List[str], List[Dict[str, str]]]:
    data = []
    with open(file_path) as file:
        lines = csv.reader(file)

        # Iterate through each line in the CSV file, extract the fields
        for index, record in enumerate(lines):
            # Extract column names from first row
            if index == 0:
                columns = record
                continue
            data.append({columns[i]: record[i] for i in range(len(columns))})

    return columns, data

def extract_function_and_test_names_tuple(data: List[Dict[str, str]]) -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]]]:
    test_names_tuple = set([(record["Fully Qualified Name"], record["Function Name"]) for record in data if record["Testing Method"] == "TEST METHOD CALL"])
    function_names_tuple = set([(record["Fully Qualified Name"], record["Function Name"]) for record in data if record["Function Type"] == "SOURCE"])

    return function_names_tuple, test_names_tuple

def naming_convention(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]]) -> Dict[str, Dict[str, float]]:
    naming_conventions_dict = defaultdict(dict)

    for test_fully_qualified_name, test_function_name in test_names_tuple:
        for function_fully_qualified_name, function_name in function_names_tuple:
            if test_function_name.startswith("test_"):
                stripped_test_function_name = test_function_name[5:]
            else:
                # assumption that all test functions must begin with test
                stripped_test_function_name = test_function_name[4:]
            naming_conventions_dict[test_fully_qualified_name][function_fully_qualified_name] = 1 if function_name == stripped_test_function_name else 0
    
    return naming_conventions_dict

def naming_convention_contains(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]]) -> Dict[str, Dict[str, float]]:
    naming_conventions_contains_dict = defaultdict(dict)

    for test_fully_qualified_name, test_function_name in test_names_tuple:
        for function_fully_qualified_name, function_name in function_names_tuple:
            if test_function_name.startswith("test_"):
                stripped_test_function_name = test_function_name[5:]
            else:
                # assumption that all test functions must begin with test
                stripped_test_function_name = test_function_name[4:]
            naming_conventions_contains_dict[test_fully_qualified_name][function_fully_qualified_name] = 1 if function_name in stripped_test_function_name else 0
    
    return naming_conventions_contains_dict


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

def longest_common_subsequence_both(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]]) -> Dict[str, Dict[str, float]]:
    lcsb_dict = defaultdict(dict)

    for test_fully_qualified_name, test_function_name in test_names_tuple:
        for function_fully_qualified_name, function_name in function_names_tuple:
            lcsb_result = (find_lcs(test_function_name, function_name))/(max(len(test_function_name), len(function_name)))
            lcsb_dict[test_fully_qualified_name][function_fully_qualified_name] = lcsb_result
    
    return lcsb_dict

def longest_common_subsequence_unit(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]]) -> Dict[str, Dict[str, float]]:
    lcsu_dict = defaultdict(dict)

    for test_fully_qualified_name, test_function_name in test_names_tuple:
        for function_fully_qualified_name, function_name in function_names_tuple:
            lcsu_result = (find_lcs(test_function_name, function_name))/len(function_name)
            lcsu_dict[test_fully_qualified_name][function_fully_qualified_name] = lcsu_result
    
    return lcsu_dict

def print_dict_results(dict_result: Dict[str, Dict[str, float]], title: str, limit: Optional[int] = 10) -> None:
    print(f"{'='*15} {title} {'='*15}\n")

    for test, results_for_test_dict in dict_result.items():
        print(f"{'='*5} {test} {'='*5}")
        results_for_test_list = list(results_for_test_dict.items())
        results_for_test_list.sort(key=lambda x: x[1], reverse=True)
        for i in range(1, len(results_for_test_list) + 1 if not limit else min(len(results_for_test_dict), limit) + 1):
            score = f"{results_for_test_list[i-1][1]:.5f}"
            function_name = results_for_test_list[i-1][0]
            print(f"Rank: {str(i).ljust(10)} | Score: {score.ljust(10)} | Function: {function_name}")
        print("\n")
    print("="*50 + "\n\n")



def levenshtein_distance(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]]) -> Dict[str, Dict[str, float]]:
    levenshtein_dict = defaultdict(dict)

    for test_fully_qualified_name, test_function_name in test_names_tuple:
        for function_fully_qualified_name, function_name in function_names_tuple:
            levenshtein_result = 1 - (find_levenshtein_distance(test_function_name, function_name))/(max(len(test_function_name), len(function_name)))
            levenshtein_dict[test_fully_qualified_name][function_fully_qualified_name] = levenshtein_result
    
    return levenshtein_dict

def find_functions_called_by_each_test(data: List[Dict[str, str]]) -> Dict[str, Set[str]]:
    functions_called_by_each_test_dict = defaultdict(set)
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test is not None and record["Function Type"] == "SOURCE":
            functions_called_by_each_test_dict[current_test].add(record["Fully Qualified Name"])
    
    return functions_called_by_each_test_dict


def find_functions_called_by_each_test_multiple(data: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    functions_called_by_each_test_dict_multiple = defaultdict(lambda: defaultdict(int))
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test is not None and record["Function Type"] == "SOURCE":
            functions_called_by_each_test_dict_multiple[current_test][record["Fully Qualified Name"]] += 1
    
    return functions_called_by_each_test_dict_multiple

def find_tests_that_call_each_function(data: List[Dict[str, str]]) -> Dict[str, Set[str]]:
    tests_that_call_each_function_dict = defaultdict(set)
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test is not None and record["Function Type"] == "SOURCE":
            tests_that_call_each_function_dict[record["Fully Qualified Name"]].add(current_test)

    return tests_that_call_each_function_dict

def find_tests_that_call_each_function_multiple(data: List[Dict[str, str]]) -> Dict[str, Dict[str, int]]:
    tests_that_call_each_function_dict_multiple = defaultdict(lambda: defaultdict(int))
    current_test = None

    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Name"]
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test is not None and record["Function Type"] == "SOURCE":
            tests_that_call_each_function_dict_multiple[record["Fully Qualified Name"]][current_test] += 1

    return tests_that_call_each_function_dict_multiple

def last_call_before_assert(data: List[Dict[str, str]], function_names: Set[str], test_names: Set[str]) -> Dict[str, Set[str]]:
    functions_called_before_assert_for_each_test = defaultdict(set)
    current_test = None
    last_returned_function = None
    
    for record in data:
        if record["Testing Method"] == "TEST METHOD CALL":
            current_test = record["Fully Qualified Name"]
            last_returned_function = None
        elif record["Testing Method"] == "TEST METHOD RETURN":
            current_test = None
        elif current_test is not None and record["Event Type"] == "RETURN" and record["Function Type"] == "SOURCE":
            last_returned_function = record["Fully Qualified Name"]
        elif current_test is not None and last_returned_function is not None and record["Function Type"] == "ASSERT":
            # Won't catch the last returned function if there was no return before an assert in the current test
            functions_called_before_assert_for_each_test[current_test].add(last_returned_function)
    
    lcba_dict = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}

    for test_name, functions_called_before_assert in functions_called_before_assert_for_each_test.items():
        for function_name in functions_called_before_assert:
            lcba_dict[test_name][function_name] = 1
    
    return lcba_dict

            
def tarantula(functions_called_by_each_test_dict: Dict[str, Set[str]], tests_that_call_each_function_dict: Dict[str, Set[str]], function_names: Set[str], test_names: Set[str]) -> Dict[str, Dict[str, float]]:
    number_of_tests = len(test_names)
    # number_of_functions = len(fully_qualified_function_names)

    tarantula_dict = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}

    for test_name in functions_called_by_each_test_dict:
        for function_name in tests_that_call_each_function_dict:
            if function_name in functions_called_by_each_test_dict[test_name]:
                number_of_tests_that_call_function = len(tests_that_call_each_function_dict[function_name])
                tarantula_dict[test_name][function_name] = 1/(((number_of_tests_that_call_function - 1)/(number_of_tests - 1))+1) 
    
    return tarantula_dict

def tarantula_multiple(functions_called_by_each_test_dict_multiple: Dict[str, Dict[str, int]], tests_that_call_each_function_dict_multiple: Dict[str, Dict[str, int]], function_names: Set[str], test_names: Set[str]) -> Dict[str, Dict[str, float]]:
    number_of_tests = len(test_names)
    # number_of_functions = len(fully_qualified_function_names)

    tarantula_dict_multiple = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}

    for test_name in functions_called_by_each_test_dict_multiple:
        for function_name in tests_that_call_each_function_dict_multiple:
            if function_name in functions_called_by_each_test_dict_multiple[test_name]:
                number_of_tests_that_call_function = sum(count for _, count in tests_that_call_each_function_dict_multiple[function_name].items())
                tarantula_dict_multiple[test_name][function_name] = 1/(((number_of_tests_that_call_function - 1)/(number_of_tests - 1))+1) 
    
    return tarantula_dict_multiple

def tfidf(functions_called_by_each_test_dict: Dict[str, Set[str]], tests_that_call_each_function_dict: Dict[str, Set[str]], function_names: Set[str], test_names: Set[str]) -> Dict[str, Dict[str, float]]:
    number_of_tests = len(test_names)
    idf_set = {}

    tfidf_dict = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}

    for function_name in tests_that_call_each_function_dict:
        number_of_tests_that_call_function = len(tests_that_call_each_function_dict[function_name])
        idf_set[function_name] = log(1 + number_of_tests/(number_of_tests_that_call_function))
        print(idf_set, number_of_tests, number_of_tests_that_call_function)
    

    for test_name in functions_called_by_each_test_dict:
        number_of_functions_called_by_test = len(functions_called_by_each_test_dict[test_name])
        tf = log(1+1/(number_of_functions_called_by_test)) if number_of_functions_called_by_test > 0 else 0
        for function_name in tests_that_call_each_function_dict:
            tfidf_dict[test_name][function_name] = tf * idf_set[function_name]
    
    return tfidf_dict

def tfidf_multiple(functions_called_by_each_test_dict_multiple: Dict[str, Dict[str, int]], tests_that_call_each_function_dict_multiple: Dict[str, Dict[str, int]], function_names: Set[str], test_names: Set[str]) -> Dict[str, Dict[str, float]]:
    number_of_tests = len(test_names)
    idf_set_multiple = {}

    tfidf_dict_multiple = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}

    for function_name in tests_that_call_each_function_dict_multiple:
        number_of_tests_that_call_function = sum(count for _, count in tests_that_call_each_function_dict_multiple[function_name].items())
        idf_set_multiple[function_name] = log(1 + number_of_tests/(number_of_tests_that_call_function))
        
    for test_name in functions_called_by_each_test_dict_multiple:
        number_of_functions_called_by_test = sum(count for _, count in functions_called_by_each_test_dict_multiple[test_name].items())
        tf = log(1+1/(number_of_functions_called_by_test))
        for function_name in tests_that_call_each_function_dict_multiple:
            tfidf_dict_multiple[test_name][function_name] = tf * idf_set_multiple[function_name]
    
    return tfidf_dict_multiple

def find_average_score(result_dicts: List[Dict[str, Dict[str, float]]], function_names: Set[str], test_names: Set[str]) -> Dict[str, Dict[str, float]]:
    average_score_dict = {test_name: {function_name: 0 for function_name in function_names} for test_name in test_names}
    num_of_result_dicts = len(result_dicts)
    for result_dict in result_dicts:
        for test_name in test_names:
            for function_name in function_names:
                average_score_dict[test_name][function_name] += result_dict[test_name][function_name]/num_of_result_dicts
    
    return average_score_dict


if __name__ == "__main__":
    columns, data = read_csv_log("pyopenssl_pytest_tracer_logs.csv")
    function_names_tuple, test_names_tuple = extract_function_and_test_names_tuple(data)
    fully_qualified_function_names = set(fully_qualified_function_name for fully_qualified_function_name, _ in function_names_tuple)
    fully_qualified_test_names = set(fully_qualified_test_name for fully_qualified_test_name, _ in test_names_tuple)

    
    # result_dicts = []
    # result_dicts_multple = []
    
    # naming_convention_contains_dict = naming_convention_contains(function_names_tuple, test_names_tuple)
    # result_dicts.append(naming_convention_contains_dict)
    # result_dicts_multple.append(naming_convention_contains_dict)
    # print_dict_results(naming_convention_contains_dict, "Results for Naming Convention - Contains")

    # lcsb_dict = longest_common_subsequence_both(function_names_tuple, test_names_tuple)
    # result_dicts.append(lcsb_dict)
    # result_dicts_multple.append(lcsb_dict)
    # print_dict_results(lcsb_dict, "Results for Longest Common Subsequence - Both")

    # lcsu_dict = longest_common_subsequence_unit(function_names_tuple, test_names_tuple)
    # result_dicts.append(lcsu_dict)
    # result_dicts_multple.append(lcsu_dict)
    # print_dict_results(lcsu_dict, "Results for Longest Common Subsequence - Unit")

    # levenshtein_dict = levenshtein_distance(function_names_tuple, test_names_tuple)
    # result_dicts.append(levenshtein_dict)
    # result_dicts_multple.append(levenshtein_dict)
    # print_dict_results(levenshtein_dict, "Results for Levenshtein Distance")

    # functions_called_by_each_test_dict = find_functions_called_by_each_test(data)
    # tests_that_call_each_function_dict = find_tests_that_call_each_function(data)
    # tarantula_dict = tarantula(functions_called_by_each_test_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names)
    # result_dicts.append(tarantula_dict)
    # print_dict_results(tarantula_dict, "Results for Tarantula")

    # tfidf_dict = tfidf(functions_called_by_each_test_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names)
    # result_dicts.append(tfidf_dict)
    # print_dict_results(tfidf_dict, "Results for TF-IDF")

    # lcba_dict = last_call_before_assert(data, fully_qualified_function_names, fully_qualified_test_names)
    # result_dicts.append(lcba_dict)
    # result_dicts_multple.append(lcba_dict)
    # print_dict_results(lcba_dict, "Results for LCBA")

    # functions_called_by_each_test_dict_multiple = find_functions_called_by_each_test_multiple(data)
    # tests_that_call_each_function_dict_multiple = find_tests_that_call_each_function_multiple(data)

    # average_score_dict = find_average_score(result_dicts, fully_qualified_function_names, fully_qualified_test_names)
    # print_dict_results(average_score_dict, "Final averaged results - Single Set for TF-IDF and Tarantula")

    # tfidf_dict_multiple = tfidf_multiple(functions_called_by_each_test_dict_multiple, tests_that_call_each_function_dict_multiple, fully_qualified_function_names, fully_qualified_test_names)
    # result_dicts_multple.append(tfidf_dict_multiple)
    # print_dict_results(tfidf_dict_multiple, "Results for TF-IDF - Multi")

    # tarantula_dict_multiple = tarantula_multiple(functions_called_by_each_test_dict_multiple, tests_that_call_each_function_dict_multiple, fully_qualified_function_names, fully_qualified_test_names)
    # result_dicts_multple.append(tarantula_dict_multiple)
    # print_dict_results(tarantula_dict_multiple, "Results for Tarantula - Multi")

    # average_score_dict_multiple = find_average_score(result_dicts_multple, fully_qualified_function_names, fully_qualified_test_names)
    # print_dict_results(average_score_dict_multiple, "Final averaged results - Multi Set for TF-IDF and Tarantula")
    # print(fully_qualified_test_names)

    import random

    chosen_tests_ground_truth = random.sample(list(fully_qualified_test_names), 50)

    print(list(fully_qualified_function_names))
    # print(chosen_tests_ground_truth)

    

