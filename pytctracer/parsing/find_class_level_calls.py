from typing import Dict, List, Set
from collections import defaultdict
from pytctracer.config.constants import (
    TraceDataHeader,
    TestingMethodType,
    EventType,
    FunctionType,
)


def find_function_classes_called_by_test(
    trace_data: List[Dict[str, str]]
) -> Dict[str, Set[str]]:
    """
    Find the function classes called by each test in the trace data.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.
    
    Returns:
        Dict[str, Set[str]]: A dictionary where the keys are the fully qualified
        names of the unit test, and the values are sets containing the
        fully qualified names of each function class invoked.
    """
    function_classes_called_by_test_dict = defaultdict(set)
    current_test = None

    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            current_test = record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
        elif (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE
            and record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
        ):
            function_classes_called_by_test_dict[current_test].add(
                record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
            )

    return function_classes_called_by_test_dict


def find_function_classes_called_by_test_count(
    trace_data: List[Dict[str, str]]
) -> Dict[str, Dict[str, int]]:
    """
    Find the function classes called by each test in the trace data, along with the
    number of times each function class was called.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.
    
    Returns:
        Dict[str, Dict[str, int]]: A dictionary where the keys are the fully
        qualified names of the unit test, and the values are dictionaries
        containing the fully qualified names of each function class invoked, along
        with the number of times each function class was called.
    """
    function_classes_called_by_test_count_dict = defaultdict(lambda: defaultdict(int))
    current_test = None

    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            current_test = record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
        elif (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE
            and record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
            and record[TraceDataHeader.EVENT_TYPE] == EventType.CALL
        ):
            function_classes_called_by_test_count_dict[current_test][
                record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
            ] += 1

    return function_classes_called_by_test_count_dict


def find_tests_that_call_function_classes(
    trace_data: List[Dict[str, str]],
) -> Dict[str, Set[str]]:
    """
    Find the tests that call each function class in the trace data.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.
    
    Returns:
        Dict[str, Set[str]]: A dictionary where the keys are the fully qualified
        names of the function class, and the values are sets containing the
        fully qualified names of each test that calls the function class.
    """
    tests_that_call_function_classes_dict = defaultdict(set)
    current_test = None

    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            current_test = record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
        elif (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE
            and record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
        ):
            tests_that_call_function_classes_dict[
                record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
            ].add(current_test)

    return tests_that_call_function_classes_dict


def find_function_classes_called_by_test_depth(
    trace_data: List[Dict[str, str]],
) -> Dict[str, Dict[str, int]]:
    """
    Find the function classes called by each test in the trace data, along with the
    depth at which each function class was called. If a function class is called 
    multiple times by a test class, the lowest depth is recorded.

    Args:
        trace_data (List[Dict[str, str]]): The tracing CSV log as a dictionary.
    
    Returns:
        Dict[str, Dict[str, int]]: A dictionary where the keys are the fully
        qualified names of the unit test, and the values are dictionaries
        containing the fully qualified names of each function class invoked, along
        with the depth at which each function class was called.
    """
    # Each function appears once for a test, at the highest depth
    function_classes_called_by_test_depth_dict = defaultdict(dict)
    current_test_class = None
    current_test_class_depth = 0

    for record in trace_data:
        if record[TraceDataHeader.TESTNG_METHOD] == TestingMethodType.TEST_METHOD_CALL:
            current_test_class = record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
            current_test_class_depth = int(record[TraceDataHeader.DEPTH])
        elif (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_RETURN
        ):
            current_test_class = None
        elif (
            current_test_class is not None
            and record[TraceDataHeader.FUNCTION_TYPE] == FunctionType.SOURCE
            and record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
        ):
            function_class_name = record[TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME]
            function_class_depth = int(record[TraceDataHeader.DEPTH])
            if (
                current_test_class in function_classes_called_by_test_depth_dict
                and function_class_name
                in function_classes_called_by_test_depth_dict[current_test_class]
            ):
                function_class_depth = min(
                    function_class_depth,
                    function_classes_called_by_test_depth_dict[current_test_class][
                        function_class_name
                    ],
                )
            function_classes_called_by_test_depth_dict[current_test_class][
                function_class_name
            ] = (function_class_depth - current_test_class_depth)

    return function_classes_called_by_test_depth_dict


__all__ = [
    "find_function_classes_called_by_test",
    "find_function_classes_called_by_test_count",
    "find_tests_that_call_function_classes",
    "find_function_classes_called_by_test_depth",
]
