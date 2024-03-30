from enum import StrEnum


class MetricScoreTypes(StrEnum):
    BINARY = "BINARY"
    CONTINUOUS = "CONTINUOUS"
    THRESHOLD_INDEPENDENT = "THRESHOLD_INDEPENDENT"
    INTEGER = "INTEGER"
    NA = "N/A"
