from typing import List, Dict, Set
from collections import defaultdict
from pytctracer.config.constants import (
    TraceDataHeader,
    TestingMethodType,
    EventType,
    FunctionType,
)


def find_functions_called_by_test(
    trace_data: List[Dict[str, str]]
) -> Dict[str, Set[str]]:
    """
    Find the functions called by each test in the trace data.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.

    Returns:
        Dict[str, Set[str]]: A dictionary where the keys are the fully qualified
        names of the unit test, and the values are sets containing the
        fully qualified names of each function invoked.
    """
    functions_called_by_test_dict = defaultdict(set)
    current_test = None

    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            current_test = record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME]
        elif (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test is not None
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE
        ):
            functions_called_by_test_dict[current_test].add(
                record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME]
            )

    return functions_called_by_test_dict


def find_functions_called_by_test_count(
    trace_data: List[Dict[str, str]]
) -> Dict[str, Dict[str, int]]:
    """
    Find the functions called by each test in the trace data, along with the
    number of times each function was called.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.

    Returns:
        Dict[str, Dict[str, int]]: A dictionary where the keys are the fully
        qualified names of the unit test, and the values are dictionaries
        containing the fully qualified names of each function invoked, along
        with the number of times each function was called.
    """
    functions_called_by_test_count_dict = defaultdict(lambda: defaultdict(int))
    current_test = None

    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            current_test = record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME]
        elif (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test is not None
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE
            and record[TraceDataHeader.EVENT_TYPE] == EventType.CALL
        ):
            functions_called_by_test_count_dict[current_test][
                record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME]
            ] += 1

    return functions_called_by_test_count_dict


def find_tests_that_call_function(
    trace_data: List[Dict[str, str]]
) -> Dict[str, Set[str]]:
    """
    Find the tests that call each function in the trace data.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.

    Returns:
        Dict[str, Set[str]]: A dictionary where the keys are the fully qualified
        names of the function, and the values are sets containing the fully
        qualified names of each test that calls the function.
    """
    tests_that_call_function_dict = defaultdict(set)
    current_test = None

    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            current_test = record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME]
        elif (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test is not None
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE
        ):
            tests_that_call_function_dict[
                record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME]
            ].add(current_test)

    return tests_that_call_function_dict


def find_functions_called_by_test_depth(
    trace_data: List[Dict[str, str]]
) -> Dict[str, Dict[str, int]]:
    """
    Find the functions called by each test in the trace data, along with the
    depth of each call. If a function is called multiple times by a test, the
    lowest depth is recorded.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.

    Returns:
        Dict[str, Dict[str, int]]: A dictionary where the keys are the fully
        qualified names of the unit test, and the values are dictionaries
        containing the fully qualified names of each function invoked, along
        with the call depth of each function.
    """
    # Each function appears once for a test, at the highest depth
    functions_called_by_test_depth_dict = defaultdict(dict)
    current_test = None
    current_test_depth = 0

    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            current_test = record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME]
            current_test_depth = int(record[TraceDataHeader.DEPTH])
        elif (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test is not None
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE
        ):
            function_name = record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME]
            function_depth = int(record[TraceDataHeader.DEPTH])
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
