from enum import StrEnum


class TraceDataHeaders(StrEnum):
    TESTNG_METHOD = "Testing Method"
    EVENT_TYPE = "Event Type"
    FUNCTION_TYPE = "Function Type"
    FULLY_QUALIFIED_FUNCTION_NAME = "Fully Qualified Function Name"
    FUNCTION_NAME = "Function Name"
    FULLY_QUALIFIED_CLASS_NAME = "Fully Qualified Class Name"
    CLASS_NAME = "Class Name"
    DEPTH = "Depth"
