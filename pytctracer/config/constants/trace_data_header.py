from enum import StrEnum


class TraceDataHeader(StrEnum):
    DEPTH = "Depth"
    FUNCTION_TYPE = "Function Type"
    TESTNG_METHOD = "Testing Method"
    FUNCTION_NAME = "Function Name"
    FULLY_QUALIFIED_FUNCTION_NAME = "Fully Qualified Function Name"
    CLASS_NAME = "Class Name"
    FULLY_QUALIFIED_CLASS_NAME = "Fully Qualified Class Name"
    LINE = "Line"
    EVENT_TYPE = "Event Type"
    RETURN_VALUE = "Return Value"
    RETURN_TYPE = "Return Type"
    EXCEPTION_TYPE = "Exception Type"
    EXCEPTION_MESSAGE = "Exception Message"
    THREAD_ID = "Thread ID"
