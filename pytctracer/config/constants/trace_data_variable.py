from enum import StrEnum


class TraceDataVariable(StrEnum):
    DEPTH = "depth"
    FUNCTION_TYPE = "function_type"
    FUNCTION_NAME = "function_name"
    FULLY_QUALIFIED_FUNCTION_NAME = "fully_qualified_function_name"
    CLASS_NAME = "class_name"
    FULLY_QUALIFIED_CLASS_NAME = "fully_qualified_class_name"
    LINE_NUMBER = "line_number"
    EVENT_TYPE = "event_type"
    RETURN_VALUE = "return_value"
    RETURN_TYPE = "return_type"
    TESTING_METHOD = "testing_method"
    THREAD_ID = "thread_id"
