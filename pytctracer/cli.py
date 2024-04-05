from typing import Tuple, Optional
import click
from pytctracer import Analyser
from pytctracer.config import Config
from pytctracer.config.constants import LevelType


@click.group(
    "pytctracer",
    help="""CLI for producing, analysing and comparing test-to-code
    traceability links for Python projects using the Pytest framework.""",
)
def cli():
    pass


@cli.command(
    "produce-links",
    short_help="Produce test-to-code traceability links for a given trace.",
    help="""Produce test-to-code traceability links
    for a given trace log CSV file using specified
    traceability techniques.
    
    The CSV should be in the exact format generated from using the PytestTracer
    class. The resulting predictions will be a list of code artefact names for
    each test artefact in the trace log. The predictions can be saved to a JSON
    file for each technique used.""",
)
@click.argument("trace-csv-log-path", type=click.Path(exists=True))
@click.option(
    "--technique",
    type=click.Choice(Config.SELECTABLE_TECHNIQUE_NAMES),
    multiple=True,
    help="""Use a specified technique (can be multiple of this flag). 
    If omitted, all selectable techniques are used by default.""",
)
@click.option(
    "--level",
    type=click.Choice([LevelType.FUNCTION, LevelType.CLASS]),
    default=LevelType.FUNCTION,
    help="""What level of traceability to produce links for (function or class). 
    If omitted, links are produced at the function level by default.""",
)
@click.option(
    "--add-combined",
    is_flag=True,
    default=False,
    help="""Produce an additional set of links using a combined scoring 
    technique of the selected techniques (simple average).""",
)
@click.option(
    "--output-directory",
    type=click.Path(exists=True),
    help="""Directory to write the output links to. 
    Each technique's links will be written to a separate JSON file. If omitted,
    the links are printed to standard output only.""",
)
def produce_links(
    trace_csv_log_path: str,
    technique: Optional[Tuple[str]],
    level: str,
    add_combined: bool,
    output_directory: Optional[str],
):
    analyser = Analyser()
    chosen_technique_names = list(technique)
    analyser.produce_traceability_links_for_trace(
        trace_csv_log_path=trace_csv_log_path,
        traceability_level=level,
        add_combined_technique=add_combined,
        chosen_technique_names=chosen_technique_names,
        prediction_output_directory_path=output_directory,
    )


@cli.command(
    "evaluate-links",
    short_help="Produce and evaluate links against a ground truth.",
    help="""Produce and evaluate test-to-code traceability links against
    ground truth links for a given trace log CSV file, 
    using specified traceability techniques and evaluation metrics.
    
    The CSV should be in the exact format generated from using the PytestTracer
    class. For each of the generated links for each technique, a JSON object will
    be generated containing the classifications of each test-to-code pair. This will
    show for each test artefact, which code artefacts were classified as true positives,
    false positives, and false negatives. The evaluation metrics will be reported for
    each set of links, and is saveable to a CSV file.
    """,
)
@click.argument("trace-csv-log-path", type=click.Path(exists=True))
@click.argument("ground-truth-path", type=click.Path(exists=True))
@click.option(
    "--technique",
    type=click.Choice(Config.SELECTABLE_TECHNIQUE_NAMES),
    multiple=True,
    help="""Use a specified technique (can be multiple of this flag). If omitted,
    all selectable techniques are used by default.""",
)
@click.option(
    "--metric",
    type=click.Choice(Config.SELECTABLE_METRIC_NAMES),
    multiple=True,
    help="""Use a specified evaluation metric (can be multiple of this flag). If omitted,
    all selectable metrics are used by default.""",
)
@click.option(
    "--level",
    type=click.Choice([LevelType.FUNCTION, LevelType.CLASS]),
    default=LevelType.FUNCTION,
    help="""What level of traceability to produce links for (function or class).
    If omitted, links are produced at the function level by default.""",
)
@click.option(
    "--add-combined",
    is_flag=True,
    default=False,
    help="""Produce an additional set of links using a combined scoring 
              technique of the selected techniques (simple average).""",
)
@click.option(
    "--as-percentage",
    is_flag=True,
    default=False,
    help="""Report continous metrics as percentages. If omitted,
              metrics are reported as raw values by default.""",
)
@click.option(
    "--display-classifications",
    is_flag=True,
    default=False,
    help="""
              Display all classifications for all techniques in standard output.""",
)
@click.option(
    "--classifications-output-directory",
    type=click.Path(exists=True),
    help="""Directory to write the output classifications to. 
              Each technique's classifications will be written to a separate JSON file.""",
)
@click.option(
    "--metrics-output-path",
    type=click.Path(exists=True),
    help="""Path to write the CSV containing the evaluation metric results to.""",
)
def evaluate_links(
    trace_csv_log_path: str,
    ground_truth_path: str,
    technique: Optional[Tuple[str]],
    metric: Optional[Tuple[str]],
    level: str,
    add_combined: bool,
    as_percentage: bool,
    classifications_output_directory: Optional[str],
    metrics_output_path: Optional[str],
):
    analyser = Analyser()
    chosen_technique_names = list(technique)
    chosen_metric_names = list(metric)
    analyser.evaluate_traceability_links_for_trace(
        trace_csv_log_path=trace_csv_log_path,
        ground_truth_path=ground_truth_path,
        traceability_level=level,
        add_combined_technique=add_combined,
        metric_as_percentage=as_percentage,
        chosen_technique_names=chosen_technique_names,
        chosen_metric_names=chosen_metric_names,
        classifications_output_directory_path=classifications_output_directory,
        evaluation_metrics_output_path=metrics_output_path,
    )


@cli.command(
    "compare-links",
    short_help="Compare a set of links against a ground truth.",
    help="""Compare a set of test-to-code traceability links against ground truth links
    using specified evaluation metrics.
    
    Both the predicted links and ground truth links should be JSON files containing
    keys of the test artefact names, and values of a single list of code artefact names
    that the test artefact is linked to. Both JSON objects will need to have the
    exact same test artefact names as keys.
    
    A JSON object willbe generated containing the classifications of each test-to-code pair. This will
    show for each test artefact, which code artefacts were classified as true positives,
    false positives, and false negatives. The evaluation metrics will be reported for
    each set of links, and is saveable to a CSV file.""",
)
@click.argument("predicted-links-path", type=click.Path(exists=True))
@click.argument("ground-truth-path", type=click.Path(exists=True))
@click.option(
    "--metric",
    type=click.Choice(Config.SELECTABLE_METRIC_NAMES),
    multiple=True,
    help="""Use a specified evaluation metric (can be multiple of this flag). If omitted,
    all selectable metrics are used by default.""",
)
@click.option(
    "--level",
    type=click.Choice([LevelType.FUNCTION, LevelType.CLASS]),
    default=LevelType.FUNCTION,
    help="""What level of traceability to produce links for (function or class).
    If omitted, links are produced at the function level by default.""",
)
@click.option(
    "--as-percentage",
    is_flag=True,
    default=False,
    help="""Report continous metrics as percentages. If omitted,
              metrics are reported as raw values by default.""",
)
@click.option(
    "--classifications-output-path",
    type=click.Path(exists=True),
    help="""Path to write the JSON containing the classifications to.""",
)
@click.option(
    "--metrics-output-path",
    type=click.Path(exists=True),
    help="""Path to write the CSV containing the evaluation metric results to.""",
)
def compare_links(
    predicted_links_path: str,
    ground_truth_path: str,
    metric: Optional[Tuple[str]],
    level: str,
    as_percentage: bool,
    classifications_output_path: Optional[str],
    metrics_output_path: Optional[str],
):
    analyser = Analyser()
    chosen_metric_names = list(metric)
    analyser.compare_traceability_links(
        predicted_links_path=predicted_links_path,
        ground_truth_path=ground_truth_path,
        chosen_metric_names=chosen_metric_names,
        metric_as_percentage=as_percentage,
        classifications_output_path=classifications_output_path,
        evaluation_metrics_output_path=metrics_output_path,
    )
    # predicted_links_path="copilot-predictions/pyopenssl/function/pyopenssl_copilot_function_predictions.json",
    # ground_truth_path="ground-truth-data/pyopenssl/function/pyopenssl_ground_truth.json",


# tracing-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv

# trace_csv_log_path="tracing-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv",
# ground_truth_path="ground-truth-data/pyopenssl/class/pyopenssl_ground_truth_classes.json",


if __name__ == "__main__":
    cli()
