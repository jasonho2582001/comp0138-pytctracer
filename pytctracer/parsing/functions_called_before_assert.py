from collections import defaultdict
from typing import Dict, List, Set
from pytctracer.config.constants import (
    TestingMethodType,
    TraceDataHeader,
    EventType,
    FunctionType,
)


def find_functions_called_before_assert_for_each_test(
    trace_data: List[Dict[str, str]]
) -> Dict[str, Set[str]]:
    """
    Finds the fully qualified names of the functions called before an
    assert statement for each test.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.
    
    Returns:
        Dict[str, Set[str]]: A dictionary where the keys are the fully qualified
        names of the unit test, and the values are sets containing the
        fully qualified names of each function invoked before
        an assert statement.
    """
    functions_called_before_assert_for_each_test = defaultdict(set)
    current_test = None
    last_returned_function = None

    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            current_test = record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME]
            last_returned_function = None
        elif (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test is not None
            and record[TraceDataHeader.EVENT_TYPE] == EventType.RETURN
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE
        ):
            last_returned_function = record[
                TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME
            ]
        elif (
            current_test is not None
            and last_returned_function is not None
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.ASSERT
        ):
            # Won't catch the last returned function if there was no return
            # before an assert in the current test
            functions_called_before_assert_for_each_test[current_test].add(
                last_returned_function
            )

    return functions_called_before_assert_for_each_test


def find_classes_called_before_assert_for_each_test(
    trace_data: List[Dict[str, str]]
) -> Dict[str, Set[str]]:
    """
    Finds the fully qualified names of the classes called before an assert
    statement for each test class.
    
    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.
    
    Returns:
        Dict[str, Set[str]]: A dictionary where the keys are the fully qualified
        names of thetest class, and the values are sets containing the
        fully qualified names function class invoked before
        an assert statement.
    """
    function_classes_called_before_assert_for_each_test = defaultdict(set)
    current_test_class = None
    last_returned_function_class = None

    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            current_test_class = record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
            last_returned_function_class = None
        elif (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_RETURN
        ):
            current_test_class = None
        elif (
            current_test_class
            and record[TraceDataHeader.EVENT_TYPE] == EventType.RETURN
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE
        ):
            last_returned_function_class = record[
                TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME
            ]
        elif (
            current_test_class
            and last_returned_function_class
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.ASSERT
        ):
            # Won't catch the last returned function if there was no return
            # before an assert in the current test
            function_classes_called_before_assert_for_each_test[current_test_class].add(
                last_returned_function_class
            )

    return function_classes_called_before_assert_for_each_test


__all__ = [
    "find_functions_called_before_assert_for_each_test",
    "find_classes_called_before_assert_for_each_test",
]
