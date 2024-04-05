from typing import Dict, List, Set
from collections import defaultdict
from pytctracer.config.constants import (
    TraceDataHeader,
    TestingMethodType,
    EventType,
    FunctionType,
)


def find_function_classes_called_by_test(
    data: List[Dict[str, str]]
) -> Dict[str, Set[str]]:
    function_classes_called_by_test_dict = defaultdict(set)
    current_test = None

    for record in data:
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
    data: List[Dict[str, str]]
) -> Dict[str, Dict[str, int]]:
    function_classes_called_by_test_count_dict = defaultdict(lambda: defaultdict(int))
    current_test = None

    for record in data:
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
    data: List[Dict[str, str]],
) -> Dict[str, Set[str]]:
    tests_that_call_function_classes_dict = defaultdict(set)
    current_test = None

    for record in data:
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
    data: List[Dict[str, str]],
) -> Dict[str, Dict[str, int]]:
    # Each function appears once for a test, at the highest depth
    function_classes_called_by_test_depth_dict = defaultdict(dict)
    current_test_class = None
    current_test_class_depth = 0

    for record in data:
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
