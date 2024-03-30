from collections import defaultdict
from typing import Dict, List, Set
from pytctracer.config.constants import (
    TestingMethodTypes,
    TraceDataHeaders,
    EventTypes,
    FunctionTypes,
)


def find_functions_called_before_assert_for_each_test(
    trace_data: List[Dict[str, str]]
) -> Dict[str, Set[str]]:
    functions_called_before_assert_for_each_test = defaultdict(set)
    current_test = None
    last_returned_function = None

    for record in trace_data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            current_test = record[TraceDataHeaders.FULLY_QUALIFIED_FUNCTION_NAME]
            last_returned_function = None
        elif (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test is not None
            and record[TraceDataHeaders.EVENT_TYPE] == EventTypes.RETURN
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE
        ):
            last_returned_function = record[
                TraceDataHeaders.FULLY_QUALIFIED_FUNCTION_NAME
            ]
        elif (
            current_test is not None
            and last_returned_function is not None
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.ASSERT
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
    function_classes_called_before_assert_for_each_test = defaultdict(set)
    current_test_class = None
    last_returned_function_class = None

    for record in trace_data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            current_test_class = record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
            last_returned_function_class = None
        elif (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_RETURN
        ):
            current_test_class = None
        elif (
            current_test_class
            and record[TraceDataHeaders.EVENT_TYPE] == EventTypes.RETURN
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE
        ):
            last_returned_function_class = record[
                TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME
            ]
        elif (
            current_test_class
            and last_returned_function_class
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.ASSERT
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
