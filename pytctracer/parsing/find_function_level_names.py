from typing import Tuple, Set, Dict, List
from pytctracer.config.constants import (
    TraceDataHeader,
    FunctionType,
    TestingMethodType,
)


def find_function_names_tuple(trace_data: List[Dict[str, str]]) -> Set[Tuple[str, str]]:
    """
    Find the function and fully qualified names of the functions found in the
    trace data.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.

    Returns:
        Set[Tuple[str, str]]: A set of tuples where the first element of each
        tuple is the fully qualified (full path) name of a function, and the second
        element is the short name of the function.
    """
    function_names_tuple = set()
    for record in trace_data:
        if record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE:
            function_names_tuple.add(
                (
                    record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME],
                    record[TraceDataHeader.FUNCTION_NAME],
                )
            )

    return function_names_tuple


def find_test_names_tuple(trace_data: List[Dict[str, str]]) -> Set[Tuple[str, str]]:
    """
    Find the function and fully qualified names of the tests found in the
    trace data.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.

    Returns:
        Set[Tuple[str, str]]: A set of tuples where the first element of each
        tuple is the fully qualified (full path) name of a test, and the second
        element is the short name of the test.
    """
    test_names_tuple = set()
    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            test_names_tuple.add(
                (
                    record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME],
                    record[TraceDataHeader.FUNCTION_NAME],
                )
            )

    return test_names_tuple


__all__ = ["find_function_names_tuple", "find_test_names_tuple"]
