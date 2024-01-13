from collections import defaultdict
from typing import Optional, Set, List, Dict, Tuple
from math import log
import csv

pyopenssl_ground_truth_dict_lists = {
    "tests.test_crypto.TestPKey.test_pregeneration": ["src.OpenSSL.crypto.PKey.type", "src.OpenSSL.crypto.PKey.bits", "src.OpenSSL.crypto.PKey.check"],
    "tests.test_ssl.TestConnection.test_get_peer_cert_chain_none": ["src.OpenSSL.SSL.Connection.get_peer_cert_chain"],
    "tests.test_ssl.TestMemoryBIO.test_socket_overrides_memory": ["src.OpenSSL.SSL.Connection.bio_read","src.OpenSSL.SSL.Connection.bio_write"],
    "tests.test_ssl.TestServerNameCallback.test_no_servername": ["src.OpenSSL.SSL.Context.set_tlsext_servername_callback", "src.OpenSSL.SSL.Connection.get_servername"],
    "tests.test_ssl.TestConnection.test_get_cipher_version": ["src.OpenSSL.SSL.Connection.get_cipher_version"],
    "tests.test_crypto.TestFunction.test_load_privatekey_passphrase_wrong_return_type": ["src.OpenSSL.crypto.load_privatekey"],
    "tests.test_crypto.TestPKey.test_check_pr_897": ["src.OpenSSL.crypto.load_privatekey", "src.OpenSSL.crypto.PKey.check"],
    "tests.test_ssl.TestDTLS.test_timeout": ["src.OpenSSL.SSL.Connection.DTLSv1_get_timeout", "src.OpenSSL.SSL.Connection.DTLSv1_handle_timeout"],
    "tests.test_crypto.TestX509Req.test_construction": ["src.OpenSSL.crypto.X509Req.__init__"],
    "tests.test_crypto.TestRevoked.test_set_reason_invalid_reason": ["src.OpenSSL.crypto.Revoked.set_reason"],
    "tests.test_crypto.TestRevoked.test_reason": ["src.OpenSSL.crypto.Revoked.all_reasons", "src.OpenSSL.crypto.Revoked.set_reason", "src.OpenSSL.crypto.Revoked.get_reason"],
    "tests.test_ssl.TestConnection.test_set_context": ["src.OpenSSL.SSL.Connection.set_context"],
    "tests.test_crypto.TestX509Name.test_only_string_attributes": ["src.OpenSSL.crypto.X509.get_subject"],
    "tests.test_crypto.TestCRL.test_dump_crl": ["src.OpenSSL.crypto.dump_crl"],
    "tests.test_crypto.TestX509Req.test_undef_oid": ["src.OpenSSL.crypto.X509Extension.get_short_name"],
    "tests.test_crypto.TestFunction.test_load_privatekey_wrongPassphrase": ["src.OpenSSL.crypto.load_privatekey"],
    "tests.test_ssl.TestContext.test_set_timeout_wrong_args": ["src.OpenSSL.SSL.Context.set_timeout"],
    "tests.test_ssl.TestContextConnection.test_use_certificate": ["src.OpenSSL.SSL.Context.use_certificate", "src.OpenSSL.SSL.Connection.use_certificate"],
    "tests.test_ssl.TestConnection.test_connect_wrong_args": ["src.OpenSSL.SSL.Connection.connect"],
    "tests.test_crypto.TestX509StoreContext.test_get_verified_chain_invalid_chain_no_root": ["src.OpenSSL.crypto.X509StoreContext.get_verified_chain"],
    "tests.test_crypto.TestX509StoreContext.test_verify_with_ca_file_location": ["src.OpenSSL.crypto.X509Store.load_locations", "src.OpenSSL.crypto.X509StoreContext.verify_certificate"],
    "tests.test_ssl.TestContext.test_set_default_verify_paths": ["src.OpenSSL.SSL.Context.set_default_verify_paths", "src.OpenSSL.SSL.Connection.send"],
    "tests.test_ssl.TestContext.test_set_options": ["src.OpenSSL.SSL.Context.set_options"],
    "tests.test_ssl.TestConnection.test_set_verify_overrides_context": ["src.OpenSSL.SSL.Context.set_verify"],
    "tests.test_crypto.TestX509.test_convert_from_cryptography": ["src.OpenSSL.crypto.X509Req.from_cryptography"],
    "tests.test_crypto.TestSignVerify.test_sign_with_large_key": ["src.OpenSSL.crypto.sign"],
    "tests.test_crypto.TestX509.test_version": ["src.OpenSSL.crypto.X509.set_version", "src.OpenSSL.crypto.X509.get_version"],
    "tests.test_ssl.TestContext.test_set_keylog_callback": ["src.OpenSSL.SSL.Context.set_keylog_callback"],
    "tests.test_ssl.TestContext.test_set_verify_callback_exception": ["src.OpenSSL.SSL.Context.set_verify"],
    "tests.test_ssl.TestContext.test_set_session_id_unicode": ["src.OpenSSL.SSL.Context.set_session_id"],
    "tests.test_crypto.TestX509Store.test_load_locations_fails_when_all_args_are_none": ["src.OpenSSL.crypto.X509Store.load_locations"],
    "tests.test_crypto.TestX509Req.test_convert_from_cryptography_unsupported_type": ["src.OpenSSL.crypto.X509Req.from_cryptography"],
    "tests.test_crypto.TestX509.test_invalid_digest_algorithm": ["src.OpenSSL.crypto.X509.digest"],
    "tests.test_util.TestErrors.test_exception_from_error_queue_nonexistent_reason": ["src.OpenSSL._util.exception_from_error_queue"],
    "tests.test_crypto.TestX509.test_convert_to_cryptography_key": ["src.OpenSSL.crypto.X509.to_cryptography"],
    "tests.test_crypto.TestCRL.test_export_md5_digest": ["src.OpenSSL.crypto.CRL.export"],
    "tests.test_ssl.TestContext.test_fallback_path_is_not_file_or_dir": ["src.OpenSSL.SSL.Context._fallback_default_verify_paths"],
    "tests.test_ssl.TestContext.test_set_verify_wrong_callable_arg": ["src.OpenSSL.SSL.Context.set_verify"],
    "tests.test_crypto.TestX509.test_set_notBefore": ["src.OpenSSL.crypto.X509.set_notBefore"]
}

pyopenssl_ground_truth_dict = {test_name: set(links) for test_name, links in pyopenssl_ground_truth_dict_lists.items()}

THRESHOLD_FOR_LCSU = 0.75
THRESHOLD_FOR_LCSB = 0.55
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

def longest_common_subsequence_both(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]], functions_called_by_each_test_dict: Dict[str, Set[str]]) -> Dict[str, Dict[str, float]]:
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

    return normalise_dict(lcsb_dict, functions_called_by_each_test_dict)

def longest_common_subsequence_unit(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]], functions_called_by_each_test_dict: Dict[str, Set[str]]) -> Dict[str, Dict[str, float]]:
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

    return normalise_dict(lcsu_dict, functions_called_by_each_test_dict)

def levenshtein_distance(function_names_tuple: Set[Tuple[str, str]], test_names_tuple: Set[Tuple[str, str]], functions_called_by_each_test_dict: Dict[str, Set[str]]) -> Dict[str, Dict[str, float]]:
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
    
    return normalise_dict(levenshtein_dict, functions_called_by_each_test_dict)

def last_call_before_assert(data: List[Dict[str, str]], function_names: Set[str], test_names: Set[str]) -> Dict[str, Set[str]]:
    """FIX TRACER BECAUSE IF FUNCTION RETURNS IN-LINE WITH AN ASSERT IT WILL NOT CATCH THE ASSERT"""
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
    
    return normalise_dict(tarantula_dict, functions_called_by_each_test_dict)

def tfidf(functions_called_by_each_test_dict: Dict[str, Set[str]], tests_that_call_each_function_dict: Dict[str, Set[str]], function_names: Set[str], test_names: Set[str]) -> Dict[str, Dict[str, float]]:
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
    
    return normalise_dict(tfidf_dict, functions_called_by_each_test_dict)

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

def calculate_evalution_measures(predicted_links: Dict[str, Set[str]], ground_truth_links: Dict[str, Set[str]]) -> Dict[str, float]:
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

        total_true_links += len(ground_truth_links_for_test)

    evaluation_dict = {}
    
    # Precision
    if found_true_positives + found_false_positives == 0:
        precision = 100
    else:
        precision = 100 * (found_true_positives)/(found_true_positives + found_false_positives)

    evaluation_dict["Precision"] = precision

    recall = 100 * (found_true_positives)/(found_true_positives + found_false_negatives)

    f1 = (2 * precision * recall)/(precision + recall)

    evaluation_dict["Recall"] = recall

    evaluation_dict["F1"] = f1

    evaluation_dict["True Positives"] = found_true_positives

    evaluation_dict["False Positives"] = found_false_positives

    evaluation_dict["False Negatives"] = found_false_negatives

    return evaluation_dict
    
    


# p = {"1": set([1, 2, 3, 4, 5, 6])}
# gt = {"1": set([1, 2, 3, 4, 5])}


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

def analyse_trace(file_path: str, ground_truth_dict: Dict[str, List[str]]) -> None:
    # PARSE DATA
    columns, data = read_csv_log(file_path)
    function_names_tuple, test_names_tuple = extract_function_and_test_names_tuple(data)
    fully_qualified_function_names = set(fully_qualified_function_name for fully_qualified_function_name, _ in function_names_tuple)
    fully_qualified_test_names = set(fully_qualified_test_name for fully_qualified_test_name, _ in test_names_tuple)
    functions_called_by_each_test_dict = find_functions_called_by_each_test(data)
    tests_that_call_each_function_dict = find_tests_that_call_each_function(data)
    tests_to_create_links_for = set(ground_truth_dict.keys())
    
    # TECHNIQUES
    naming_conventions_dict = naming_conventions(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
    naming_convention_contains_dict = naming_convention_contains(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
    lcsb_dict = longest_common_subsequence_both(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
    lcsu_dict = longest_common_subsequence_unit(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
    levenshtein_dict = levenshtein_distance(function_names_tuple, test_names_tuple, functions_called_by_each_test_dict)
    lcba_dict = last_call_before_assert(data, fully_qualified_function_names, fully_qualified_test_names)
    tarantula_dict = tarantula(functions_called_by_each_test_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names)
    tfidf_dict = tfidf(functions_called_by_each_test_dict, tests_that_call_each_function_dict, fully_qualified_function_names, fully_qualified_test_names)

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

    evaluation_dict_for_naming_convention = calculate_evalution_measures(predicted_links_for_naming_convention, ground_truth_dict)
    evaluation_dict_for_naming_convention_contains = calculate_evalution_measures(predicted_links_for_naming_convention_contains, ground_truth_dict)
    evaluation_dict_for_lcsb = calculate_evalution_measures(predicted_links_for_lcsb, ground_truth_dict)
    evaluation_dict_for_lcsu = calculate_evalution_measures(predicted_links_for_lcsu, ground_truth_dict)
    evaluation_dict_for_levenshtein = calculate_evalution_measures(predicted_links_for_levenshtein, ground_truth_dict)
    evaluation_dict_for_lcba = calculate_evalution_measures(predicted_links_for_lcba, ground_truth_dict)
    evaluation_dict_for_tarauntula = calculate_evalution_measures(predicted_links_for_tarantula, ground_truth_dict)
    evaluation_dict_for_tfidf = calculate_evalution_measures(predicted_links_for_tfidf, ground_truth_dict)
    evaluation_dict_for_average = calculate_evalution_measures(predicted_links_for_average, ground_truth_dict)

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
    write_evaluation_dict_to_csv(combined_evaluation_dict, "pyopenssl_predictions_results.csv")

    print(THRESHOLD_FOR_AVERAGE)

pyopen_ssl_path = "pyopenssl_pytest_tracer_logs.csv"
factorial_path = "factorial_pytest_tracer_logs.csv"

if __name__ == "__main__":
    analyse_trace(pyopen_ssl_path, pyopenssl_ground_truth_dict)