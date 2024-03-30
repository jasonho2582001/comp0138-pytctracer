from typing import Tuple, Optional
import click
from pytctracer import Analyser
from pytctracer.config import Config
from pytctracer.config.constants import LevelTypes


@click.group("pytctracer")
def cli():
    pass


@cli.command("produce-links")
@click.argument("trace-csv-log-path", type=click.Path(exists=True))
@click.option(
    "--technique", type=click.Choice(Config.SELECTABLE_TECHNIQUE_NAMES), multiple=True
)
@click.option(
    "--level",
    type=click.Choice([LevelTypes.FUNCTION, LevelTypes.CLASS]),
    default=LevelTypes.FUNCTION,
)
@click.option("--add-combined", is_flag=True, default=False)
@click.option("--output-directory", type=click.Path(exists=True))
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


@cli.command("evaluate-links")
@click.argument("trace-csv-log-path", type=click.Path(exists=True))
@click.argument("ground-truth-path", type=click.Path(exists=True))
@click.option(
    "--technique", type=click.Choice(Config.SELECTABLE_TECHNIQUE_NAMES), multiple=True
)
@click.option(
    "--metric", type=click.Choice(Config.SELECTABLE_METRIC_NAMES), multiple=True
)
@click.option(
    "--level",
    type=click.Choice([LevelTypes.FUNCTION, LevelTypes.CLASS]),
    default=LevelTypes.FUNCTION,
)
@click.option("--add-combined", is_flag=True, default=False)
@click.option("--as-percentage", is_flag=True, default=False)
@click.option("--classifications-output-directory", type=click.Path(exists=True))
@click.option("--metrics-output-path", type=click.Path(exists=True))
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


@cli.command("compare-links")
@click.argument("predicted-links-path", type=click.Path(exists=True))
@click.argument("ground-truth-path", type=click.Path(exists=True))
@click.option(
    "--metric", type=click.Choice(Config.SELECTABLE_METRIC_NAMES), multiple=True
)
@click.option(
    "--level",
    type=click.Choice([LevelTypes.FUNCTION, LevelTypes.CLASS]),
    default=LevelTypes.FUNCTION,
)
@click.option("--as-percentage", is_flag=True, default=False)
@click.option("--classifications-output-path", type=click.Path(exists=True))
@click.option("--metrics-output-path", type=click.Path(exists=True))
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
