from enum import StrEnum


class EventTypes(StrEnum):
    RETURN = "RETURN"
    CALL = "CALL"
    EXCEPTION = "EXCEPTION"
    LINE = "LINE"


class SetTraceEventTypes(StrEnum):
    CALL = "call"
    RETURN = "return"
    LINE = "line"
    EXCEPTION = "exception"


class SetProfileCEventTypes(StrEnum):
    C_CALL = "c_call"
    C_RETURN = "c_return"
    C_EXCEPTION = "c_exception"
