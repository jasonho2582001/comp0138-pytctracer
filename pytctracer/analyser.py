from typing import List, Optional, Dict, Any, Tuple, Set
from pytctracer.config.constants import LevelType, TechniqueParameter
from pytctracer.config import Config
from pytctracer.io.input import read_trace_csv_log, load_link_json
from pytctracer.io.output import (
    display_predicted_links,
    write_dict_to_json,
    write_evaluation_metrics_to_csv,
    display_evaluation_results,
    display_classifications,
)
from pytctracer.parsing import (
    find_function_names_tuple,
    find_test_names_tuple,
    find_functions_called_by_test,
    find_functions_called_by_test_count,
    find_functions_called_by_test_depth,
    find_tests_that_call_function,
    find_functions_called_before_assert_for_each_test,
    find_function_classes_called_by_test_depth,
    find_classes_called_before_assert_for_each_test,
    find_function_class_names_tuple,
    find_test_class_names_tuple,
    find_function_classes_called_by_test,
    find_function_classes_called_by_test_count,
    find_tests_that_call_function_classes,
)
from pytctracer.evaluation.metrics import ArgNameToMetricMapper, Metric
from pytctracer.evaluation import classify_predictions, evaluate_predictions
from pytctracer.techniques import ArgNameToTechniqueMapper, Combined


class Analyser:
    """
    Class which handles the the generation, evaluation and comparison
    of test-to-code traceability links.
    """

    def __init__(self) -> None:
        self.arg_name_to_technique_map = ArgNameToTechniqueMapper()
        self.arg_name_to_metric_map = ArgNameToMetricMapper()
        self.default_technique_names = Config.DEFAULT_CHOSEN_TECHNIQUE_NAMES
        self.default_metric_names = Config.DEFAULT_CHOSEN_METRIC_NAMES

    def produce_traceability_links_for_trace(
        self,
        trace_csv_log_path: str,
        traceability_level: LevelType,
        add_combined_technique: bool = False,
        chosen_technique_names: Optional[List[str]] = None,
        prediction_output_directory_path: Optional[str] = None,
    ) -> None:
        """
        Produces traceability links for a given dynamic trace log. The
        chosen technique names, whether to add a combined technique, the
        level to produce links at, and an output output directory path can
        be specified. If no directory is specified, the links are printed to
        standard output.

        Args:
            trace_csv_log_path (str): The path to the dynamic trace log CSV file.
            traceability_level (LevelType): The level of traceability to produce links for.
            add_combined_technique (bool): Whether to produce links with the combined technique.
            chosen_technique_names (Optional[List[str]]): The arg names of the techniques to use.
            prediction_output_directory_path (Optional[str]): The directory to write the output links to.
        """
        if not chosen_technique_names:
            chosen_technique_names = self.default_technique_names
        _, link_predictions_for_techniques = self._predict_links(
            trace_csv_log_path=trace_csv_log_path,
            chosen_technique_names=chosen_technique_names,
            traceability_level=traceability_level,
            add_combined_technique=add_combined_technique,
        )
        if not prediction_output_directory_path:
            self._display_predicted_links_for_techniques(
                link_predictions_for_techniques
            )
        else:
            self._write_predicted_links_for_techniques(
                link_predictions_for_techniques,
                prediction_output_directory_path,
                traceability_level,
            )

    def evaluate_traceability_links_for_trace(
        self,
        trace_csv_log_path: str,
        ground_truth_path: str,
        traceability_level: LevelType,
        add_combined_technique: bool = False,
        chosen_technique_names: Optional[List[str]] = None,
        chosen_metric_names: Optional[List[str]] = None,
        classifications_output_directory_path: Optional[str] = None,
        evaluation_metrics_output_path: Optional[str] = None,
        display_classifications_to_stdout: bool = False,
        metric_as_percentage: bool = False,
    ) -> None:
        """
        Produces traceability links for a given dynamic trace log, and then
        evaluates them against a specified ground truth. Allows for choosing
        the technique names to evaluate predictions for, the metric names to
        compute, and whether to add a combined technique as well as output
        paths for the classifications and metrics.

        Args:
            trace_csv_log_path (str): The path to the dynamic trace log CSV file.
            ground_truth_path (str): The path to the ground truth JSON file.
            traceability_level (LevelType): The level of traceability to produce links for.
            add_combined_technique (bool): Whether to produce links with the combined technique.
            chosen_technique_names (Optional[List[str]]): The arg names of the techniques to use.
            chosen_metric_names (Optional[List[str]]): The arg names of the metrics to use.
            classifications_output_directory_path (Optional[str]): The directory to write the output
            classifications to.
            evaluation_metrics_output_path (Optional[str]): The path to write the CSV containing the
            evaluation metric results to.
            display_classifications_to_stdout (bool): Whether to display the classifications to
            standard output.
            metric_as_percentage (bool): Whether to report metrics as percentages.
        """
        if not chosen_technique_names:
            chosen_technique_names = self.default_technique_names

        if not chosen_metric_names:
            chosen_metric_names = self.default_metric_names

        ground_truth_links = load_link_json(ground_truth_path)
        ground_truth_tests = set(ground_truth_links.keys())

        traceability_scores_for_techniques, link_predictions_for_techniques = (
            self._predict_links(
                trace_csv_log_path=trace_csv_log_path,
                chosen_technique_names=chosen_technique_names,
                traceability_level=traceability_level,
                add_combined_technique=add_combined_technique,
                test_to_create_links_for=ground_truth_tests,
            )
        )

        evaluation_metrics_for_techniques = self._compute_metrics(
            link_predictions_for_techniques=link_predictions_for_techniques,
            ground_truth_links=ground_truth_links,
            traceability_scores_for_techniques=traceability_scores_for_techniques,
            chosen_metric_names=chosen_metric_names,
            metric_as_percentage=metric_as_percentage,
        )
        classifications_for_techniques = self._compute_classifications(
            link_predictions_for_techniques=link_predictions_for_techniques,
            ground_truth_links=ground_truth_links,
        )
        if display_classifications_to_stdout:
            self._display_classifications_for_techniques(classifications_for_techniques)

        display_evaluation_results(
            evaluation_metric_dict=evaluation_metrics_for_techniques,
            title=Config.EVALUATION_METRICS_TITLE,
        )

        if classifications_output_directory_path:
            self._write_classifications_for_techniques(
                classifications_for_techniques=classifications_for_techniques,
                classifications_output_directory_path=classifications_output_directory_path,
                traceability_level=traceability_level,
            )

        if evaluation_metrics_output_path:
            write_evaluation_metrics_to_csv(
                combined_evaluation_dict=evaluation_metrics_for_techniques,
                csv_name=evaluation_metrics_output_path,
            )

    def compare_traceability_links(
        self,
        predicted_links_path: str,
        ground_truth_path: str,
        chosen_metric_names: Optional[List[str]] = None,
        classifications_output_path: Optional[str] = None,
        evaluation_metrics_output_path: Optional[str] = None,
        display_classifications_to_stdout: bool = False,
        metric_as_percentage: bool = False,
    ) -> None:
        """
        Compare a JSON of predicted traceability links against a JSON of ground truth links.
        Allows for choosing the metric names to compute, and output paths for the classifications
        and metrics.

        Args:
            predicted_links_path (str): The path to the JSON file containing the predicted links.
            ground_truth_path (str): The path to the JSON file containing the ground truth links.
            chosen_metric_names (Optional[List[str]]): The arg names of the metrics to use.
            classifications_output_path (Optional[str]): The path to write the output classifications to.
            evaluation_metrics_output_path (Optional[str]): The path to write the CSV containing the
            evaluation metric results to.
            display_classifications_to_stdout (bool): Whether to display the classifications to
            standard output.
            metric_as_percentage (bool): Whether to report metrics as percentages.
        """
        predicted_links = load_link_json(predicted_links_path)
        ground_truth_links = load_link_json(ground_truth_path)

        self._check_ground_truth_tests_in_predicted_links(
            predicted_links, ground_truth_links
        )

        if not chosen_metric_names:
            chosen_metric_names = self.default_metric_names

        chosen_metrics = self._get_chosen_metric_classes(chosen_metric_names)

        evaluation_metrics = {
            predicted_links_path: evaluate_predictions(
                predicted_links=predicted_links,
                ground_truth_links=ground_truth_links,
                selected_metrics=chosen_metrics,
                metric_as_percentage=metric_as_percentage,
                uses_threshold=False,
            )
        }

        classifications = classify_predictions(
            predicted_links=predicted_links, ground_truth_links=ground_truth_links
        )

        if display_classifications_to_stdout:
            display_classifications(classifications, predicted_links_path)

        display_evaluation_results(
            evaluation_metric_dict=evaluation_metrics,
            title=Config.EVALUATION_METRICS_TITLE,
        )

        if classifications_output_path:
            write_dict_to_json(classifications, classifications_output_path)

        if evaluation_metrics_output_path:
            write_evaluation_metrics_to_csv(
                combined_evaluation_dict=evaluation_metrics,
                csv_name=evaluation_metrics_output_path,
            )

    def _check_ground_truth_tests_in_predicted_links(
        self,
        predicted_links: Dict[str, List[str]],
        ground_truth_links: Dict[str, List[str]],
    ) -> None:
        tests_in_predicted_links = set(predicted_links.keys())
        for test in ground_truth_links:
            if test not in tests_in_predicted_links:
                raise ValueError(
                    f"Test '{test}' in ground truth but not in predicted links"
                )

    def _write_classifications_for_techniques(
        self,
        classifications_for_techniques: Dict[str, Dict[str, List[str]]],
        classifications_output_directory_path: str,
        traceability_level: LevelType,
    ) -> None:
        for (
            technique_arg_name,
            classifications,
        ) in classifications_for_techniques.items():
            technique_arg_name = technique_arg_name.replace("-", "_")
            file_path = f"""{classifications_output_directory_path}/{technique_arg_name}_{traceability_level.lower()}_classifications.json"""
            write_dict_to_json(classifications, file_path)

    def _display_classifications_for_techniques(
        self, classifications_for_techniques: Dict[str, Dict[str, List[str]]]
    ) -> None:
        for (
            technique_arg_name,
            classifications,
        ) in classifications_for_techniques.items():
            technique_short_name = self.arg_name_to_technique_map.get_short_name(
                technique_arg_name
            )
            display_classifications(classifications, technique_short_name)

    def _compute_classifications(
        self,
        link_predictions_for_techniques: Dict[str, Dict[str, List[str]]],
        ground_truth_links: Dict[str, List[str]],
    ) -> Dict[str, Dict[str, List[str]]]:
        classifications_for_techniques = {}
        for (
            technique_arg_name,
            link_predictions,
        ) in link_predictions_for_techniques.items():
            classifications = classify_predictions(
                predicted_links=link_predictions, ground_truth_links=ground_truth_links
            )
            classifications_for_techniques[technique_arg_name] = classifications

        return classifications_for_techniques

    def _get_chosen_metric_classes(
        self, chosen_metric_names: List[str]
    ) -> List[Metric]:
        chosen_metrics = []
        for metric_arg_name in chosen_metric_names:
            metric = self.arg_name_to_metric_map.get_metric(metric_arg_name)()
            chosen_metrics.append(metric)

        return chosen_metrics

    def _compute_metrics(
        self,
        link_predictions_for_techniques: Dict[str, Dict[str, List[str]]],
        ground_truth_links: Dict[str, List[str]],
        traceability_scores_for_techniques: Dict[str, Dict[str, Dict[str, float]]],
        chosen_metric_names: List[str],
        metric_as_percentage: bool,
    ) -> Dict[str, Dict[str, float]]:
        chosen_metrics = self._get_chosen_metric_classes(chosen_metric_names)

        evaluation_metrics_for_techniques = {}
        for (
            technique_arg_name,
            link_predictions,
        ) in link_predictions_for_techniques.items():
            technique_uses_threshold = self.arg_name_to_technique_map.get_technique(
                technique_arg_name
            ).uses_threshold
            evaluation_metrics = evaluate_predictions(
                predicted_links=link_predictions,
                ground_truth_links=ground_truth_links,
                traceability_score_dict=traceability_scores_for_techniques[
                    technique_arg_name
                ],
                selected_metrics=chosen_metrics,
                metric_as_percentage=metric_as_percentage,
                uses_threshold=technique_uses_threshold,
            )
            evaluation_metrics_for_techniques[technique_arg_name] = evaluation_metrics

        return evaluation_metrics_for_techniques

    def _predict_links(
        self,
        trace_csv_log_path: str,
        chosen_technique_names: List[str],
        traceability_level: LevelType,
        add_combined_technique: bool,
        test_to_create_links_for: Optional[Set[str]] = None,
    ) -> Tuple[Dict[str, Dict[str, Dict[str, float]]], Dict[str, Dict[str, List[str]]]]:
        if traceability_level == LevelType.FUNCTION:
            technique_parameter_map = self._parse_function_level_data(
                trace_csv_log_path
            )
        else:
            technique_parameter_map = self._parse_class_level_data(trace_csv_log_path)
        traceability_scores_for_techniques = self._run_technique_scoring(
            chosen_technique_names=chosen_technique_names,
            technique_parameter_map=technique_parameter_map,
        )
        link_predictions_for_techniques = self._run_technique_link_prediction(
            traceability_scores_for_techniques=traceability_scores_for_techniques,
            tests_to_create_links_for=test_to_create_links_for,
        )

        if add_combined_technique:
            combined_technique = Combined()
            combined_traceability_scores = combined_technique.run(
                traceability_scores_for_techniques
            )
            traceability_scores_for_techniques[combined_technique.arg_name] = (
                combined_traceability_scores
            )
            combined_link_predictions = combined_technique.generate_predicted_links(
                traceability_score_dict=combined_traceability_scores,
                tests_to_create_links_for=test_to_create_links_for,
            )
            link_predictions_for_techniques[combined_technique.arg_name] = (
                combined_link_predictions
            )

        return traceability_scores_for_techniques, link_predictions_for_techniques

    def _write_predicted_links_for_techniques(
        self,
        link_predictions_for_techniques: Dict[str, Dict[str, List[str]]],
        prediction_output_directory_path: str,
        traceability_level: LevelType,
    ) -> None:
        for (
            technique_arg_name,
            link_predictions,
        ) in link_predictions_for_techniques.items():
            technique_arg_name = technique_arg_name.replace("-", "_")
            file_path = f"""{prediction_output_directory_path}/{technique_arg_name}_{traceability_level.lower()}_predicted_links.json"""
            write_dict_to_json(link_predictions, file_path)

    def _display_predicted_links_for_techniques(
        self, link_predictions_for_techniques: Dict[str, Dict[str, List[str]]]
    ) -> None:
        for (
            technique_arg_name,
            link_predictions,
        ) in link_predictions_for_techniques.items():
            technique_short_name = self.arg_name_to_technique_map.get_short_name(
                technique_arg_name
            )
            display_predicted_links(link_predictions, technique_short_name)

    def _run_technique_link_prediction(
        self,
        traceability_scores_for_techniques: Dict[str, Dict[str, Dict[str, float]]],
        tests_to_create_links_for: Optional[Set[str]] = None,
    ) -> Dict[str, Dict[str, List[str]]]:
        link_predictions_for_techniques = {}
        for (
            technique_arg_name,
            traceability_scores,
        ) in traceability_scores_for_techniques.items():
            technique = self.arg_name_to_technique_map.get_technique(
                technique_arg_name
            )()
            link_predictions = technique.generate_predicted_links(
                traceability_score_dict=traceability_scores,
                tests_to_create_links_for=tests_to_create_links_for,
            )
            link_predictions_for_techniques[technique_arg_name] = link_predictions

        return link_predictions_for_techniques

    def _run_technique_scoring(
        self,
        chosen_technique_names: List[str],
        technique_parameter_map: Dict[TechniqueParameter, Any],
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        traceability_scores_for_techniques = {}
        for technique_arg_name in chosen_technique_names:
            technique = self.arg_name_to_technique_map.get_technique(
                technique_arg_name
            )()

            technique_parameters = {
                required_parameter: technique_parameter_map[required_parameter]
                for required_parameter in technique.required_parameters
            }

            traceability_scores = technique.run(**technique_parameters)
            traceability_scores_for_techniques[technique_arg_name] = traceability_scores

        return traceability_scores_for_techniques

    def _parse_function_level_data(
        self, trace_csv_log_path: str
    ) -> Dict[TechniqueParameter, Any]:
        trace_data = read_trace_csv_log(trace_csv_log_path)
        function_names_tuple = find_function_names_tuple(trace_data)
        test_names_tuple = find_test_names_tuple(trace_data)
        functions_called_by_test = find_functions_called_by_test(trace_data)
        functions_called_by_test_count = find_functions_called_by_test_count(trace_data)
        functions_called_by_test_depth = find_functions_called_by_test_depth(trace_data)
        functions_called_by_test_before_assert = (
            find_functions_called_before_assert_for_each_test(trace_data)
        )
        tests_that_call_function = find_tests_that_call_function(trace_data)

        return {
            TechniqueParameter.FUNCTION_NAMES_TUPLE: function_names_tuple,
            TechniqueParameter.TEST_NAMES_TUPLE: test_names_tuple,
            TechniqueParameter.FUNCTIONS_CALLED_BY_TESTS: functions_called_by_test,
            TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_COUNT: functions_called_by_test_count,
            TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_DEPTH: functions_called_by_test_depth,
            TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_BEFORE_ASSERT: functions_called_by_test_before_assert,
            TechniqueParameter.TESTS_THAT_CALL_FUNCTIONS: tests_that_call_function,
        }

    def _parse_class_level_data(
        self, trace_csv_log_path: str
    ) -> Dict[TechniqueParameter, Any]:
        trace_data = read_trace_csv_log(trace_csv_log_path)
        function_class_names_tuple = find_function_class_names_tuple(trace_data)
        test_class_names_tuple = find_test_class_names_tuple(trace_data)
        functions_called_by_test_class = find_function_classes_called_by_test(
            trace_data
        )
        functions_called_by_test_class_count = (
            find_function_classes_called_by_test_count(trace_data)
        )
        functions_called_by_test_class_depth = (
            find_function_classes_called_by_test_depth(trace_data)
        )
        functions_called_by_test_class_before_assert = (
            find_classes_called_before_assert_for_each_test(trace_data)
        )
        tests_that_call_function_classes = find_tests_that_call_function_classes(
            trace_data
        )

        return {
            TechniqueParameter.FUNCTION_NAMES_TUPLE: function_class_names_tuple,
            TechniqueParameter.TEST_NAMES_TUPLE: test_class_names_tuple,
            TechniqueParameter.FUNCTIONS_CALLED_BY_TESTS: functions_called_by_test_class,
            TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_COUNT: functions_called_by_test_class_count,
            TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_DEPTH: functions_called_by_test_class_depth,
            TechniqueParameter.FUNCTIONS_CALLED_BY_TEST_BEFORE_ASSERT: functions_called_by_test_class_before_assert,
            TechniqueParameter.TESTS_THAT_CALL_FUNCTIONS: tests_that_call_function_classes,
        }


__all__ = ["Analyser"]
