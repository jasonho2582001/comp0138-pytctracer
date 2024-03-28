from typing import List, Dict, Tuple, Set
from src.config.constants import TraceDataHeaders, FunctionTypes, TestingMethodTypes


def find_function_class_names_tuple(
    trace_data: List[Dict[str, str]]
) -> Set[Tuple[str, str]]:
    function_class_names_tuple = set()
    for record in trace_data:
        if record[TraceDataHeaders.FUNCTION_TYPE] == FunctionTypes.SOURCE:
            function_class_names_tuple.add(
                (
                    record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME],
                    record[TraceDataHeaders.CLASS_NAME],
                )
            )

    return function_class_names_tuple


def find_test_class_names_tuple(
    trace_data: List[Dict[str, str]]
) -> Set[Tuple[str, str]]:
    test_class_names_tuple = set()
    for record in trace_data:
        if (
            record[TraceDataHeaders.TESTNG_METHOD]
            == TestingMethodTypes.TEST_METHOD_CALL
        ):
            test_class_names_tuple.add(
                (
                    record[TraceDataHeaders.FULLY_QUALIFIED_CLASS_NAME],
                    record[TraceDataHeaders.CLASS_NAME],
                )
            )

    return test_class_names_tuple


__all__ = ["find_function_class_names_tuple", "find_test_class_names_tuple"]
