class Config:
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


__all__ = ["Config"]
