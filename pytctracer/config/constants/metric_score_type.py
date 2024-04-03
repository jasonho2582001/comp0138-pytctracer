from enum import StrEnum


class MetricScoreType(StrEnum):
    BINARY = "BINARY"
    CONTINUOUS = "CONTINUOUS"
    THRESHOLD_INDEPENDENT = "THRESHOLD_INDEPENDENT"
    INTEGER = "INTEGER"
    NA = "N/A"
