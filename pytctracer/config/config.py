class Config:
    """
    Class storing configuration variables for the package.
    """
    SELECTABLE_TECHNIQUE_NAMES = [
        "nc",
        "ncc",
        "lcsb",
        "lcsu",
        "leven",
        "lcba",
        "tarantula",
        "tfidf",
        "tfidf_multiset",
    ]
    SELECTABLE_METRIC_NAMES = [
        "precision",
        "recall",
        "f1",
        "map",
        "auc",
        "tp",
        "fp",
        "fn",
    ]
    DEFAULT_CHOSEN_TECHNIQUE_NAMES = [
        "nc",
        "ncc",
        "lcsb",
        "lcsu",
        "leven",
        "lcba",
        "tarantula",
        "tfidf",
        "tfidf_multiset",
    ]
    DEFAULT_CHOSEN_METRIC_NAMES = [
        "precision",
        "recall",
        "f1",
        "map",
        "auc",
        "tp",
        "fp",
        "fn",
    ]
    EVALUATION_METRICS_TITLE = "Evaluation Metrics"
    DEFAULT_THRESHOLDS = {
        "lcsu": 0.75,
        "lcsb": 0.55,
        "leven": 0.95,
        "tarantula": 0.95,
        "tfidf": 0.9,
        "tfidf_multiset": 0.9,
        "combined": 0.85,
    }

__all__ = ["Config"]
