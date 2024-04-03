from enum import StrEnum


class TechniqueParameter(StrEnum):
    FUNCTION_NAMES_TUPLE = "function_names_tuple"
    TEST_NAMES_TUPLE = "test_names_tuple"
    TESTS_THAT_CALL_FUNCTIONS = "tests_that_call_functions"
    FUNCTIONS_CALLED_BY_TESTS = "functions_called_by_tests"
    FUNCTIONS_CALLED_BY_TEST_COUNT = "functions_called_by_test_count"
    FUNCTIONS_CALLED_BY_TEST_DEPTH = "functions_called_by_test_depth"
    FUNCTIONS_CALLED_BY_TEST_BEFORE_ASSERT = "functions_called_by_test_before_assert"


__all__ = ["TechniqueParameter"]
