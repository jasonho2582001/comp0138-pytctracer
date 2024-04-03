from typing import Tuple, Set, Dict, List
from pytctracer.config.constants import (
    TraceDataHeader,
    FunctionType,
    TestingMethodType,
)


def find_function_names_tuple(trace_data: List[Dict[str, str]]) -> Set[Tuple[str, str]]:
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
    test_names_tuple = set()
    for record in trace_data:
        if (
            record[TraceDataHeader.TESTNG_METHOD]
            == TestingMethodType.TEST_METHOD_CALL
        ):
            test_names_tuple.add(
                (
                    record[TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME],
                    record[TraceDataHeader.FUNCTION_NAME],
                )
            )

    return test_names_tuple


__all__ = ["find_function_names_tuple", "find_test_names_tuple"]
