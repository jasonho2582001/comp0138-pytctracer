import os
from enum import Enum
from dotenv import load_dotenv
from pytctracer.config.config import Config

DEFAULT_THRESHOLDS = Config.DEFAULT_THRESHOLDS

load_dotenv()


class TechniqueThreshold(float, Enum):
    THRESHOLD_FOR_LCSU = os.environ.get(
        "THRESHOLD_FOR_LCSU", DEFAULT_THRESHOLDS["lcsu"]
    )
    THRESHOLD_FOR_LCSB = os.environ.get(
        "THRESHOLD_FOR_LCSB", DEFAULT_THRESHOLDS["lcsb"]
    )
    THRESHOLD_FOR_LEVENSHTEIN = os.environ.get(
        "THRESHOLD_FOR_LEVENSHTEIN", DEFAULT_THRESHOLDS["leven"]
    )
    THRESHOLD_FOR_TARANTULA = os.environ.get(
        "THRESHOLD_FOR_TARANTULA", DEFAULT_THRESHOLDS["tarantula"]
    )
    THRESHOLD_FOR_TFIDF = os.environ.get(
        "THRESHOLD_FOR_TFIDF", DEFAULT_THRESHOLDS["tfidf"]
    )
    THRESHOLD_FOR_TFIDF_MULTISET = os.environ.get(
        "THRESHOLD_FOR_TFIDF_MULTISET", DEFAULT_THRESHOLDS["tfidf_multiset"]
    )
    THRESHOLD_FOR_COMBINED = os.environ.get(
        "THRESHOLD_FOR_COMBINED", DEFAULT_THRESHOLDS["combined"]
    )
