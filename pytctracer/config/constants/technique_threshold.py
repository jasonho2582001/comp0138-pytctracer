from enum import Enum


class TechniqueThreshold(float, Enum):
    THRESHOLD_FOR_LCSU = 0.75
    THRESHOLD_FOR_LCSB = 0.65
    THRESHOLD_FOR_LEVENSHTEIN = 0.95
    THRESHOLD_FOR_TARANTULA = 0.95
    THRESHOLD_FOR_TFIDF = 0.9
    THRESHOLD_FOR_TFIDF_MULTISET = 0.9
    THRESHOLD_FOR_COMBINED = 0.85