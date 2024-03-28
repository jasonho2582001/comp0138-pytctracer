from src import Analyser

analyser = Analyser()

# analyser.produce_traceability_links_for_trace(
#     trace_csv_log_path="tracing-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv",
#     traceability_level="function",
#     add_combined_technique=False,
#     chosen_technique_names=["lcba"]
# )

analyser.evaluate_traceability_links_for_trace(
    trace_csv_log_path="tracing-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv",
    ground_truth_path="ground-truth-data/pyopenssl/class/pyopenssl_ground_truth_classes.json",
    traceability_level="class",
    add_combined_technique=False,
    metric_as_percentage=True,
    chosen_technique_names=["ncc", "lcsb", "leven"],
    classifications_output_directory_path="ze"
)

