from typing import List, Optional, Dict, Any, Tuple, Set
from src.config.constants import LevelTypes, TechniqueParameters
from src.config import Config
from src.io.input import read_trace_csv_log, load_link_json
from src.io.output import (
    display_predicted_links,
    write_dict_to_json,
    write_evaluation_metrics_to_csv,
    display_evaluation_results,
    display_classifications,
)
from src.parsing import (
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
    find_tests_that_call_function_classes
)
from src.evaluation.metrics import ArgNameToMetricMapper
from src.evaluation import classify_predictions, evaluate_predictions
from src.techniques import ArgNameToTechniqueMapper, Combined


# 1. produce predictions at both function and class level
# (requires csv log path, can select techniques used, and whether to add combined technique, output path for predictions)
# 2. produce predictions and compare against ground truth (requires csv log path, ground truth path
# techniques used, whether to add combined technique, what metrics to use, output path for metrics, output path for classifications)
# 3. read predictions and compare against ground truth (requires csv log path, ground truth path, output path for metrics)
# techniques used, whether to add combined technique, what metrics to use, output path for metrics, output path for classifications)
class Analyser:
    def __init__(self) -> None:
        self.arg_name_to_technique_map = ArgNameToTechniqueMapper()
        self.arg_name_to_metric_map = ArgNameToMetricMapper()
        self.default_technique_names = Config.DEFAULT_CHOSEN_TECHNIQUE_NAMES
        self.default_metric_names = Config.DEFAULT_CHOSEN_METRIC_NAMES

    def evaluate_traceability_links_for_trace(
        self,
        trace_csv_log_path: str,
        ground_truth_path: str,
        traceability_level: LevelTypes,
        add_combined_technique: bool,
        chosen_technique_names: Optional[List[str]] = None,
        chosen_metric_names: Optional[List[str]] = None,
        classifications_output_directory_path: Optional[str] = None,
        evaluation_metrics_output_path: Optional[str] = None,
        display_classifications: bool = False,
        metric_as_percentage: bool = False,
    ) -> int:
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
        if display_classifications:
            self._display_classifications_for_techniques(classifications_for_techniques)

        display_evaluation_results(
            evaluation_metric_dict=evaluation_metrics_for_techniques,
            title="Evaluation Metrics",
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

    def produce_traceability_links_for_trace(
        self,
        trace_csv_log_path: str,
        traceability_level: LevelTypes,
        add_combined_technique: bool,
        chosen_technique_names: Optional[List[str]] = None,
        prediction_output_directory_path: Optional[str] = None,
    ) -> int:
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

    def _write_classifications_for_techniques(
        self,
        classifications_for_techniques: Dict[str, Dict[str, List[str]]],
        classifications_output_directory_path: str,
        traceability_level: LevelTypes,
    ) -> None:
        for (
            technique_arg_name,
            classifications,
        ) in classifications_for_techniques.items():
            technique_arg_name = technique_arg_name.replace("-", "_")
            file_path = f"{classifications_output_directory_path}/{technique_arg_name}_{traceability_level.lower()}_classifications.json"
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

    def _compute_metrics(
        self,
        link_predictions_for_techniques: Dict[str, Dict[str, List[str]]],
        ground_truth_links: Dict[str, List[str]],
        traceability_scores_for_techniques: Dict[str, Dict[str, Dict[str, float]]],
        chosen_metric_names: List[str],
        metric_as_percentage: bool,
    ) -> Dict[str, Dict[str, float]]:
        chosen_metrics = []
        for metric_arg_name in chosen_metric_names:
            metric = self.arg_name_to_metric_map.get_metric(metric_arg_name)()
            chosen_metrics.append(metric)

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
        traceability_level: LevelTypes,
        add_combined_technique: bool,
        test_to_create_links_for: Optional[Set[str]] = None,
    ) -> Tuple[Dict[str, Dict[str, Dict[str, float]]], Dict[str, Dict[str, List[str]]]]:
        if traceability_level == LevelTypes.FUNCTION:
            technique_parameter_map = self._parse_function_level_data(trace_csv_log_path)
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
        traceability_level: LevelTypes,
    ) -> None:
        for (
            technique_arg_name,
            link_predictions,
        ) in link_predictions_for_techniques.items():
            technique_arg_name = technique_arg_name.replace("-", "_")
            file_path = f"{prediction_output_directory_path}/{technique_arg_name}_{traceability_level.lower()}_predicted_links.json"
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
        link_predictions_for_technqiues = {}
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
            link_predictions_for_technqiues[technique_arg_name] = link_predictions

        return link_predictions_for_technqiues

    def _run_technique_scoring(
        self,
        chosen_technique_names: List[str],
        technique_parameter_map: Dict[TechniqueParameters, Any],
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
    ) -> Dict[TechniqueParameters, Any]:
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
            TechniqueParameters.FUNCTION_NAMES_TUPLE: function_names_tuple,
            TechniqueParameters.TEST_NAMES_TUPLE: test_names_tuple,
            TechniqueParameters.FUNCTIONS_CALLED_BY_TESTS: functions_called_by_test,
            TechniqueParameters.FUNCTIONS_CALLED_BY_TEST_COUNT: functions_called_by_test_count,
            TechniqueParameters.FUNCTIONS_CALLED_BY_TEST_DEPTH: functions_called_by_test_depth,
            TechniqueParameters.FUNCTIONS_CALLED_BY_TEST_BEFORE_ASSERT: functions_called_by_test_before_assert,
            TechniqueParameters.TESTS_THAT_CALL_FUNCTIONS: tests_that_call_function,
        }
    
    def _parse_class_level_data(
            self, trace_csv_log_path: str
    ) -> Dict[TechniqueParameters, Any]:
        trace_data = read_trace_csv_log(trace_csv_log_path)
        function_class_names_tuple = find_function_class_names_tuple(trace_data)
        test_class_names_tuple = find_test_class_names_tuple(trace_data)
        functions_called_by_test_class = find_function_classes_called_by_test(trace_data)
        functions_called_by_test_class_count = find_function_classes_called_by_test_count(trace_data)
        functions_called_by_test_class_depth = find_function_classes_called_by_test_depth(trace_data)
        functions_called_by_test_class_before_assert = find_classes_called_before_assert_for_each_test(trace_data)
        tests_that_call_function_classes = find_tests_that_call_function_classes(trace_data)

        return {
            TechniqueParameters.FUNCTION_NAMES_TUPLE: function_class_names_tuple,
            TechniqueParameters.TEST_NAMES_TUPLE: test_class_names_tuple,
            TechniqueParameters.FUNCTIONS_CALLED_BY_TESTS: functions_called_by_test_class,
            TechniqueParameters.FUNCTIONS_CALLED_BY_TEST_COUNT: functions_called_by_test_class_count,
            TechniqueParameters.FUNCTIONS_CALLED_BY_TEST_DEPTH: functions_called_by_test_class_depth,
            TechniqueParameters.FUNCTIONS_CALLED_BY_TEST_BEFORE_ASSERT: functions_called_by_test_class_before_assert,
            TechniqueParameters.TESTS_THAT_CALL_FUNCTIONS: tests_that_call_function_classes,
        }


    # def _produce_traceability_links(
    #     self,
    #     trace_csv_log_path: str,
    #     chosen_technique_names: List[str],
    #     traceability_level: LevelTypes,
    #     add_combined_technique: bool,
    #     prediction_output_path: Optional[str] = None,
    # ) -> int:

    # columns, data = read_csv_log(file_path)
    # function_names_tuple, test_names_tuple = extract_function_and_test_names_tuple(data)
    # fully_qualified_function_names = set(fully_qualified_function_name for fully_qualified_function_name, _ in function_names_tuple)
    # fully_qualified_test_names = set(fully_qualified_test_name for fully_qualified_test_name, _ in test_names_tuple)
    # functions_called_by_each_test_dict = find_functions_called_by_each_test(data)
    # functions_called_by_each_test_count_dict = find_functions_called_by_each_test_count(data)
    # tests_that_call_each_function_dict = find_tests_that_call_each_function(data)
    # tests_to_create_links_for = set(ground_truth_dict.keys())
    # depths_of_functions_called_by_each_test_dict = find_depths_of_functions_called_by_each_test(data)


__all__ = ["Analyser"]
