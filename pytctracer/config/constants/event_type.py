from enum import StrEnum


class EventType(StrEnum):
    RETURN = "RETURN"
    CALL = "CALL"
    EXCEPTION = "EXCEPTION"
    LINE = "LINE"


class SetTraceEventType(StrEnum):
    CALL = "call"
    RETURN = "return"
    LINE = "line"
    EXCEPTION = "exception"


class SetProfileCEventType(StrEnum):
    C_CALL = "c_call"
    C_RETURN = "c_return"
    C_EXCEPTION = "c_exception"
