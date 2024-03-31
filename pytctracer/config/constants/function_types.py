from enum import StrEnum


class FunctionTypes(StrEnum):
    SOURCE = "SOURCE"
    TEST = "TEST"
    ASSERT = "ASSERT"
    TEST_FUNCTION = "TEST FUNCTION"
    TEST_CLASS = "TEST CLASS"
    TEST_HELPER = "TEST HELPER"
