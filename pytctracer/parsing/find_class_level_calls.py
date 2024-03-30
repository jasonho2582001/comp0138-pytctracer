from typing import Dict, List, Set
from collections import defaultdict
from pytctracer.config.constants import (
    TraceDataHeaders,
    TestingMethodTypes,
    EventTypes,
    FunctionTypes,
)


def find_function_classes_called_by_test(
    data: List[Dict[str, str]]
) -> Dict[str, Set[str]]:
    function_classes_called_by_test_dict = defaultdict(set)
    current_test = None

    for record in data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            current_test = record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
        elif (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE
            and record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
        ):
            function_classes_called_by_test_dict[current_test].add(
                record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
            )

    return function_classes_called_by_test_dict


def find_function_classes_called_by_test_count(
    data: List[Dict[str, str]]
) -> Dict[str, Dict[str, int]]:
    function_classes_called_by_test_count_dict = defaultdict(lambda: defaultdict(int))
    current_test = None

    for record in data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            current_test = record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
        elif (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE
            and record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
            and record[TraceDataHeaders.EVENT_TYPE] == EventTypes.CALL
        ):
            function_classes_called_by_test_count_dict[current_test][
                record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
            ] += 1

    return function_classes_called_by_test_count_dict


def find_tests_that_call_function_classes(
    data: List[Dict[str, str]],
) -> Dict[str, Set[str]]:
    tests_that_call_function_classes_dict = defaultdict(set)
    current_test = None

    for record in data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            current_test = record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
        elif (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_RETURN
        ):
            current_test = None
        elif (
            current_test
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE
            and record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
        ):
            tests_that_call_function_classes_dict[
                record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
            ].add(current_test)

    return tests_that_call_function_classes_dict


def find_function_classes_called_by_test_depth(
    data: List[Dict[str, str]],
) -> Dict[str, Dict[str, int]]:
    # Each function appears once for a test, at the highest depth
    function_classes_called_by_test_depth_dict = defaultdict(dict)
    current_test_class = None
    current_test_class_depth = 0

    for record in data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            current_test_class = record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
            current_test_class_depth = int(record[TraceDataHeaders.DEPTH])
        elif (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_RETURN
        ):
            current_test_class = None
        elif (
            current_test_class is not None
            and record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE
            and record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
        ):
            function_class_name = record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME]
            function_class_depth = int(record[TraceDataHeaders.DEPTH])
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