from typing import List, Dict, Set
from collections import defaultdict
from pytctracer.config.constants import (
    TraceDataHeaders,
    TestingMethodTypes,
    EventTypes,
    FunctionTypes,
)


def find_functions_called_by_test(data: List[Dict[str, str]]) -> Dict[str, Set[str]]:
    functions_called_by_test_dict = defaultdict(set)
    current_test = None

    for record in data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            current_test = record[TraceDataHeaders.FULLY_QUALIFIED_FUNCTION_NAME]
        elif (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test is not None
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE
        ):
            functions_called_by_test_dict[current_test].add(
                record[TraceDataHeaders.FULLY_QUALIFIED_FUNCTION_NAME]
            )

    return functions_called_by_test_dict


def find_functions_called_by_test_count(
    data: List[Dict[str, str]]
) -> Dict[str, Dict[str, int]]:
    functions_called_by_test_count_dict = defaultdict(lambda: defaultdict(int))
    current_test = None

    for record in data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            current_test = record[TraceDataHeaders.FULLY_QUALIFIED_FUNCTION_NAME]
        elif (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test is not None
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE
            and record[TraceDataHeaders.EVENT_TYPE] == EventTypes.CALL
        ):
            functions_called_by_test_count_dict[current_test][
                record[TraceDataHeaders.FULLY_QUALIFIED_FUNCTION_NAME]
            ] += 1

    return functions_called_by_test_count_dict


def find_tests_that_call_function(data: List[Dict[str, str]]) -> Dict[str, Set[str]]:
    tests_that_call_function_dict = defaultdict(set)
    current_test = None

    for record in data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            current_test = record[TraceDataHeaders.FULLY_QUALIFIED_FUNCTION_NAME]
        elif (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test is not None
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE
        ):
            tests_that_call_function_dict[
                record[TraceDataHeaders.FULLY_QUALIFIED_FUNCTION_NAME]
            ].add(current_test)

    return tests_that_call_function_dict


def find_functions_called_by_test_depth(
    data: List[Dict[str, str]]
) -> Dict[str, Dict[str, int]]:
    # Each function appears once for a test, at the highest depth
    functions_called_by_test_depth_dict = defaultdict(dict)
    current_test = None
    current_test_depth = 0

    for record in data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            current_test = record[TraceDataHeaders.FULLY_QUALIFIED_FUNCTION_NAME]
            current_test_depth = int(record[TraceDataHeaders.DEPTH])
        elif (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test is not None
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE
        ):
            function_name = record[TraceDataHeaders.FULLY_QUALIFIED_FUNCTION_NAME]
            function_depth = int(record[TraceDataHeaders.DEPTH])
            if (
                current_test in functions_called_by_test_depth_dict
                and function_name in functions_called_by_test_depth_dict[current_test]
            ):
                function_depth = min(
                    function_depth,
                    functions_called_by_test_depth_dict[current_test][function_name],
                )
            functions_called_by_test_depth_dict[current_test][function_name] = (
                function_depth - current_test_depth
            )

    return functions_called_by_test_depth_dict


__all__ = [
    "find_functions_called_by_test_depth",
    "find_functions_called_by_test",
    "find_functions_called_by_test_count",
    "find_tests_that_call_function",
]
