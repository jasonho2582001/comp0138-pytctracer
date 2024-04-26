
# Complete Replication Commands
This README outlines a set of commands to automatically reproduce the bulk of the experimental data and results generated for `pytctracer`. So long as `pytctracer` is installed, and that you are in the project root of this repo, the following commands should work, and produce the same results as the equivalent stored in `experiment-data/`

## Generate Predictions
The following command generates the test-to-code link predictions for all 4 projects, for every traceability technique, at the function and class level.

```bash
mkdir predictions
mkdir predictions/function-level
mkdir predictions/class-level
mkdir predictions/function-level/pyopenssl
mkdir predictions/function-level/arrow
mkdir predictions/function-level/kedro
mkdir predictions/function-level/chartify
mkdir predictions/class-level/pyopenssl
mkdir predictions/class-level/arrow
mkdir predictions/class-level/kedro
mkdir predictions/class-level/chartify

pytctracer produce-links --level function --add-combined --output-directory predictions/function-level/pyopenssl experiment-data/trace-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv

pytctracer produce-links --level function --add-combined --output-directory predictions/function-level/arrow experiment-data/trace-logs/arrow/arrow_pytest_tracer_logs.csv

pytctracer produce-links --level function --add-combined --output-directory predictions/function-level/kedro experiment-data/trace-logs/kedro/kedro_pytest_tracer_logs.csv

pytctracer produce-links --level function --add-combined --output-directory predictions/function-level/chartify experiment-data/trace-logs/chartify/chartify_pytest_tracer_logs.csv

pytctracer produce-links --level class --add-combined --output-directory predictions/class-level/pyopenssl experiment-data/trace-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv

pytctracer produce-links --level class --add-combined --output-directory predictions/class-level/arrow experiment-data/trace-logs/arrow/arrow_pytest_tracer_logs.csv

pytctracer produce-links --level class --add-combined --output-directory predictions/class-level/kedro experiment-data/trace-logs/kedro/kedro_pytest_tracer_logs.csv

pytctracer produce-links --level class --add-combined --output-directory predictions/class-level/chartify experiment-data/trace-logs/chartify/chartify_pytest_tracer_logs.csv
```

## Generate Evaluation Metrics
The following command generates the classifications and evaluation metrics for the test-to-code link predictions for all 4 projects, for every traceability technique, at the function and class level.

```bash
mkdir classifications
mkdir classifications/function-level
mkdir classifications/class-level
mkdir classifications/function-level/pyopenssl
mkdir classifications/function-level/arrow
mkdir classifications/function-level/kedro
mkdir classifications/function-level/chartify
mkdir classifications/class-level/pyopenssl
mkdir classifications/class-level/arrow
mkdir classifications/class-level/kedro
mkdir classifications/class-level/chartify

mkdir evaluation-metrics
mkdir evaluation-metrics/function-level
mkdir evaluation-metrics/class-level
mkdir evaluation-metrics/function-level/pyopenssl
mkdir evaluation-metrics/function-level/arrow
mkdir evaluation-metrics/function-level/kedro
mkdir evaluation-metrics/function-level/chartify
mkdir evaluation-metrics/class-level/chartify

pytctracer evaluate-links --level function --add-combined --as-percentage --classifications-output-directory classifications/function-level/pyopenssl --metrics-output-path evaluation-metrics/function-level/pyopenssl/pyopenssl_metrics_function_level.csv experiment-data/trace-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv experiment-data/ground-truths/function-level/pyopenssl/pyopenssl_ground_truth_function_level.json

pytctracer evaluate-links --level function --add-combined --as-percentage --classifications-output-directory classifications/function-level/arrow --metrics-output-path evaluation-metrics/function-level/arrow/arrow_metrics_function_level.csv experiment-data/trace-logs/arrow/arrow_pytest_tracer_logs.csv experiment-data/ground-truths/function-level/arrow/arrow_ground_truth_function_level.json

pytctracer evaluate-links --level function --add-combined --as-percentage --classifications-output-directory classifications/function-level/kedro --metrics-output-path evaluation-metrics/function-level/kedro/kedro_metrics_function_level.csv experiment-data/trace-logs/kedro/kedro_pytest_tracer_logs.csv experiment-data/ground-truths/function-level/kedro/kedro_ground_truth_function_level.json

pytctracer evaluate-links --level function --add-combined --as-percentage --classifications-output-directory classifications/function-level/chartify --metrics-output-path evaluation-metrics/function-level/chartify/chartify_metrics_function_level.csv experiment-data/trace-logs/chartify/chartify_pytest_tracer_logs.csv experiment-data/ground-truths/function-level/chartify/chartify_ground_truth_function_level.json

pytctracer evaluate-links --level class --add-combined --as-percentage --classifications-output-directory classifications/class-level/pyopenssl --metrics-output-path evaluation-metrics/class-level/pyopenssl/pyopenssl_metrics_class_level.csv experiment-data/trace-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv experiment-data/ground-truths/class-level/pyopenssl/pyopenssl_ground_truth_class_level.json

pytctracer evaluate-links --level class --add-combined --as-percentage --classifications-output-directory classifications/class-level/arrow --metrics-output-path evaluation-metrics/class-level/arrow/arrow_metrics_class_level.csv experiment-data/trace-logs/arrow/arrow_pytest_tracer_logs.csv experiment-data/ground-truths/class-level/arrow/arrow_ground_truth_class_level.json

pytctracer evaluate-links --level class --add-combined --as-percentage --classifications-output-directory classifications/class-level/kedro --metrics-output-path evaluation-metrics/class-level/kedro/kedro_metrics_class_level.csv experiment-data/trace-logs/kedro/kedro_pytest_tracer_logs.csv experiment-data/ground-truths/class-level/kedro/kedro_ground_truth_class_level.json

pytctracer evaluate-links --level class --add-combined --as-percentage --classifications-output-directory classifications/class-level/chartify --metrics-output-path evaluation-metrics/class-level/chartify/chartify_metrics_class_level.csv experiment-data/trace-logs/chartify/chartify_pytest_tracer_logs.csv experiment-data/ground-truths/class-level/chartify/chartify_ground_truth_class_level.json
```

## Copilot predictions
The following command generates the classifications and evaluation metrics for the Copilot predictions for all 4 projects, at the function and class level.

```bash
mkdir copilot-classifications
mkdir copilot-classifications/function-level
mkdir copilot-classifications/class-level
mkdir copilot-classifications/function-level/pyopenssl
mkdir copilot-classifications/function-level/arrow
mkdir copilot-classifications/function-level/kedro
mkdir copilot-classifications/function-level/chartify
mkdir copilot-classifications/class-level/pyopenssl
mkdir copilot-classifications/class-level/arrow
mkdir copilot-classifications/class-level/kedro
mkdir copilot-classifications/class-level/chartify

mkdir copilot-evaluation-metrics
mkdir copilot-evaluation-metrics/function-level
mkdir copilot-evaluation-metrics/class-level
mkdir copilot-evaluation-metrics/function-level/pyopenssl
mkdir copilot-evaluation-metrics/function-level/arrow
mkdir copilot-evaluation-metrics/function-level/kedro
mkdir copilot-evaluation-metrics/function-level/chartify
mkdir copilot-evaluation-metrics/class-level/pyopenssl
mkdir copilot-evaluation-metrics/class-level/arrow
mkdir copilot-evaluation-metrics/class-level/kedro
mkdir copilot-evaluation-metrics/class-level/chartify

pytctracer compare-links --as-percentage --classifications-output-path copilot-evaluation-metrics/function-level/pyopenssl/copilot_function_classifications.json --metrics-output-path copilot-evaluation-metrics/function-level/pyopenssl/copilot_metrics.csv experiment-data/link-predictions/copilot/function-level/pyopenssl/copilot_function_predicted_links.json experiment-data/ground-truths/function-level/pyopenssl/pyopenssl_ground_truth_function_level.json

pytctracer compare-links --as-percentage --classifications-output-path copilot-evaluation-metrics/function-level/arrow/copilot_function_classifications.json --metrics-output-path copilot-evaluation-metrics/function-level/arrow/copilot_metrics.csv experiment-data/link-predictions/copilot/function-level/arrow/copilot_function_predicted_links.json experiment-data/ground-truths/function-level/arrow/arrow_ground_truth_function_level.json

pytctracer compare-links --as-percentage --classifications-output-path copilot-evaluation-metrics/function-level/kedro/copilot_function_classifications.json --metrics-output-path copilot-evaluation-metrics/function-level/kedro/copilot_metrics.csv experiment-data/link-predictions/copilot/function-level/kedro/copilot_function_predicted_links.json experiment-data/ground-truths/function-level/kedro/kedro_ground_truth_function_level.json

pytctracer compare-links --as-percentage --classifications-output-path copilot-evaluation-metrics/function-level/chartify/copilot_function_classifications.json --metrics-output-path copilot-evaluation-metrics/function-level/chartify/copilot_metrics.csv experiment-data/link-predictions/copilot/function-level/chartify/copilot_function_predicted_links.json experiment-data/ground-truths/function-level/chartify/chartify_ground_truth_function_level.json

pytctracer compare-links --as-percentage --classifications-output-path copilot-evaluation-metrics/class-level/pyopenssl/copilot_class_classifications.json --metrics-output-path copilot-evaluation-metrics/class-level/pyopenssl/copilot_metrics.csv experiment-data/link-predictions/copilot/class-level/pyopenssl/copilot_class_predicted_links.json experiment-data/ground-truths/class-level/pyopenssl/pyopenssl_ground_truth_class_level.json

pytctracer compare-links --as-percentage --classifications-output-path copilot-evaluation-metrics/class-level/arrow/copilot_class_classifications.json --metrics-output-path copilot-evaluation-metrics/class-level/arrow/copilot_metrics.csv experiment-data/link-predictions/copilot/class-level/arrow/copilot_class_predicted_links.json experiment-data/ground-truths/class-level/arrow/arrow_ground_truth_class_level.json

pytctracer compare-links --as-percentage --classifications-output-path copilot-evaluation-metrics/class-level/kedro/copilot_class_classifications.json --metrics-output-path copilot-evaluation-metrics/class-level/kedro/copilot_metrics.csv experiment-data/link-predictions/copilot/class-level/kedro/copilot_class_predicted_links.json experiment-data/ground-truths/class-level/kedro/kedro_ground_truth_class_level.json

pytctracer compare-links --as-percentage --classifications-output-path copilot-evaluation-metrics/class-level/chartify/copilot_class_classifications.json --metrics-output-path copilot-evaluation-metrics/class-level/chartify/copilot_metrics.csv experiment-data/link-predictions/copilot/class-level/chartify/copilot_class_predicted_links.json experiment-data/ground-truths/class-level/chartify/chartify_ground_truth_class_level.json
```