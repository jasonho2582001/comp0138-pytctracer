from enum import StrEnum


class EventTypes(StrEnum):
    RETURN = "RETURN"
    CALL = "CALL"
    EXCEPTION = "EXCEPTION"
