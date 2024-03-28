class Config:
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


__all__ = ["Config"]
