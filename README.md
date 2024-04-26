# PyTCTracer
PyTCTracer is a test-to-code traceability approach and library, which allows for dynamic code tracing of Python repositories using the Pytest testing framework, and automatic generation of test-to-code traceability links from the trace data using a number of established traceability techniques. 

This library forms part of an undergraduate research project for a Masters of Engineering in Computer Science at UCL (University College London). PyTCTracer follows from TCTracer, which is an approach and implementation for test-to-code traceability for Java projects. This was developed by Robert White, Jens Krinke and Raymond Tan in 2020, and the research expanded on in 2022. The extended research paper introducing TCTracer can be found [here](https://link.springer.com/article/10.1007/s10664-021-10079-1).

There are two core components in the library:
- `PytestTracer`: A class that is used to trace the execution of Pytest unit tests and record dynamic tracing information to a CSV log file.
- `pytctracer` CLI: A CLI tool which can read and parse the dynamic information from the log file, apply traceability techniques to generate link predictions, and evaluate the predictions against a ground truth.

## Installation
PyTCTracer can be simply installed using pip:
```bash
pip install pytctracer
```

## Usage

### `PytestTracer`
The `PytestTracer` is used alongside an invocation of a Pytest test suite run to obtain tracing data from it. This works by utilising `PytestTracer`'s trace functions, which need to be set with `sys.settrace()` and `sys.setprofile()` before running Pytest. After running Pytest, the trace data is saved internally by the class, but needs to be written to an external CSV file before Pytest spins down.

#### Initialisation
The `PytestTracer` class contains the following input parameters:

| Parameter | Type | Description |
| --- | ---- | --- |
| `project_root` | `str` | The root directory of the project. |
| `test_folders` | `List[str]` | A list of directories containing test files. |
| `source_folders` | `List[str]` | A list of directories containing source files. |
| `output_csv_file_name` | `str` | The name of the output CSV file. |

These parameters are required for the class to correctly classify traced artefacts as source code or test code, and to ensure that the artefacts are correctly named. Paths can be either absolute or relative to the current working directory.

#### Methods
The `PytestTracer` class contains the following methods that can be used:
| Method | Description |
| ---- | --- |
| `trace()` | Trace function which traces Python source code and logs relevant data during function calls, returns, exceptions and test assert statements. This function is used by the `sys.settrace()` hook. |
| `trace_in_built()` | Trace function which traces Python in-built functions. These functions are irrelevant for the trace, but are required to ensure accuracy of the overall trace, particular for keeping track of function call depth. This function is used by the `sys.setprofile()` hook. |
| `write_to_csv()` | Writes the stored trace data stored internally by the class to a CSV with with path specified by the `output_csv_file_name` parameter used to initialise the class |

### CSV Output Format
Each row in the CSV file represents a single event in the trace. The columns are as follows:
| Column | Description |
| --- | --- |
Depth | The depth of the function call in the call stack. The depth of the first function call is 0. |
| Function Type | The type of function call. Can be one of TEST HELPER, SOURCE, TEST FUNCTION or ASSERT |
 | Function Name | The name of the function being called. |
 | Fully Qualified Function Name | The fully qualified name of the function being called. |
 | Class Name | The name of the class the function belongs to. If the function called is a top level function, the class name is the module it belongs to. |
 | Fully Qualified Class Name | The fully qualified name of the class the function belongs to. If the function called is a top level function, the fully qualified class name is the module it belongs to. |
 | Line | The line number in the source code corresponding to the event. |
 | Event Type | The type of event. Can be one of CALL, RETURN, EXCEPTION or LINE. |
 | Return Value | The return value of the event, if the event type is RETURN. |
 | Return Type | The type of the return value, if the event type is RETURN. |
| Exception Type | The type of exception raised, if the event type is EXCEPTION. |
| Exception Message | The message of the exception raised, if the event type is EXCEPTION. |
| Thread ID | The ID of the thread the event occurred in. |


#### Workflow
The first step is to initialise the `PytestTracer` class with the required parameters for the project to be traced. Its tracing functions need to be set globally using `sys.settrace()` and `sys.setprofile()` in Pytest's isolated environment, before the test suite runs.

Pytest provides a `pytest_sessionstart()` fixture, which allows for configuration to be added before the test session begins. We can set `PytestTracer`'s trace functions here. This requires defining a `conftest.py` file in the root directory of the project, or at a directory level above every discoverable test by Pytest. The code to initialise the class and set the trace functions in `conftest.py` should look like:

```python
# Top level conftest.py
tracer = PytestTracer(
    project_root=r"path/to/project",
    test_folders=["tests"], 
    source_folders=["src"],
    output_csv_file_name="trace_log.csv"
)

def pytest_sessionstart(session):
    sys.settrace(tracer.trace)
    sys.setprofile(tracer.trace_in_built)
```
Now, the the trace data needs to be written to a CSV file before the Pytest test suite exits. Pytest similiarly provides a `pytest_sessionfinish()` fixture, which allows for configuration to be added after the test session ends. The `write_to_csv()` method can be invoked here. This will also be in the same `conftest.py` file:

```python
def pytest_sessionfinish(session, exitstatus):
    tracer.write_to_csv()
```
This is all the required configuration and set up to correctly trace the test suite. Now, Pytest should be invoked. Automated test invocation methods, or commands which allow for test parallelisation should not be used as this will interfere with the tracing. Instead, the following command should simply be ran:
```bash
pytest --assert=plain
```
The `--assert=plain` flag turns off assert rewriting, which Pytest does internally for improved error message and introspection. However, the tracer requires the original assert statements to be present in the source code to correctly log them.

After the test suite has run, the trace data will appear in the CSV file specified by the `output_csv_file_name` parameter. This file can be used as input to the `pytctracer` CLI tool.


### `pytctracer` CLI
The `pytctracer` CLI tool is used to read and parse the dynamic information from the log file, apply traceability techniques to generate link predictions, and evaluate the predictions against a ground truth. Usage can be seen by running:
```bash
pytctracer --help
```

The CLI tool has 3 subcommands, outlined below:

#### `produce-links`
This command reads a tracing log CSV, applies a number of traceability techniques, and produces a set of link predictions for each test artefact found. The command has the following arguments:

| Argument | Description |
| --- | --- |
| `TRACE_CSV_LOG_PATH` | Path to the CSV log file containing the trace data. |

The command also has the following options:
| Option | Description |
| --- | --- |
| `--technique` | Use a specified technique (can be multiple of this flag). If omitted, all selectable techniques are used by default. |
| `--level` | What level of traceability to produce links for (function or class). If omitted, links are produced at the function level by default. |
| `--add-combined` | Produce an additional set of links using a combined scoring technique of the selected techniques (simple average). |
| `--output-directory` | Directory to write the output links to. Each technique's links will be written to a separate JSON file. If omitted, the links are printed to standard output only. |

##### Example Usage
```bash
pytctracer produce-links tracer_logs.csv --add-combined --technique nc --technique tfidf  --output-directory output_links
```


#### `evaluate-links`
This command first produces sets of link predictions using a number of techniques in the same manner as `produce-links`. It also reads a JSON file containing corresponding ground truth links, and will perform an evaluation of the predictions against the ground truth using a number of specified metrics. The command has the following arguments:

| Argument | Description |
| --- | --- |
| `TRACE_CSV_LOG_PATH` | Path to the CSV log file containing the trace data. |
| `GROUND_TRUTH_JSON_PATH` | Path to the JSON file containing the ground truth links. |

The command also has the following options:
| Option | Description |
| --- | --- |
| `--technique` | Use a specified technique (can be multiple of this flag). If omitted, all selectable techniques are used by default. |
| `--metric` | Use a specified evaluation metric (can be multiple of this flag). If omitted, all selectable metrics are used by default. |
| `--level` | What level of traceability to produce links for (function or class). If omitted, links are produced at the function level by default. |
| `--add-combined` | Produce an additional set of links using a combined scoring technique of the selected techniques (simple average). |
| `--as-percentage` | Report continous metrics as percentages. If omitted, metrics are reported as raw values by default. |
| `--display-classifications` | Display all classifications for all techniques in standard output. |
| `--classifications-output-directory` | Directory to write the output classifications to. Each technique's classifications will be written to a separate JSON file. |
| `--metrics-output-path` | Path to write the CSV containing the evaluation metric results to. |

##### Example Usage
```bash
pytctracer evaluate-links tracer_logs.csv ground_truth.json --add-combined --as-percentage --metrics-output-path metrics.csv 
```

#### `compare-links`
This command reads a set of test-to-code traceability links, a set of ground truth links, and compares them using specified evaluation metrics. The command has the following arguments:

| Argument | Description |
| --- | --- |
| `PREDICTED_LINKS_PATH` | Path to the JSON file containing the predicted links. |
| `GROUND_TRUTH_PATH` | Path to the JSON file containing the ground truth links. |

The command also has the following options:
| Option | Description |
| --- | --- |
| `--metric` | Use a specified evaluation metric (can be multiple of this flag). If omitted, all selectable metrics are used by default. |
| `--as-percentage` | Report continous metrics as percentages. If omitted, metrics are reported as raw values by default. |
| `--classifications-output-path` | Path to write the JSON containing the classifications to. |
| `--metrics-output-path` | Path to write the CSV containing the evaluation metric results to. |

##### Example Usage
```bash
pytctracer compare-links predicted_links.json ground_truth.json --as-percentage --metrics-output-path metrics.csv
```

#### Implemented Traceability Techniques
The following traceability techniques are implemented in PyTCTracer, and can be used with the `--technique` option in the `produce-links` and `evaluate-links` commands:

| Name | Arg Name | Default Threshold |
| --- | --- | --- |
| Naming Conventions | `nc` | N/A |
| Naming Conventions - Contains | `ncc` | N/A |
| Longest Common Subsequence - Both | `lcsb` | 0.55 |
| Longest Common Subsequence - Unit | `lcsu` | 0.75 |
| Levinshtein Distance | `leven` | 0.95 |
| Tarantula | `tarantula` | 0.95 |
| Last Call Before Assert | `lcba` | N/A |
| Term Frequency-Inverse Document Frequency | `tfidf` | 0.9 |
| Term Frequency-Inverse Document Frequency (Multiset) | `tfidf_multiset` | 0.9 |

The combined technique also has an average, which is set to 0.85 by default.

### Metrics
The following evaluation metrics are implemented in PyTCTracer, and can be used with the `--metric` option in the `evaluate-links` and `compare-links` commands:

| Name | Arg Name |
| --- | --- |
| Precision | `precision` |
| Recall | `recall` |
| F1 | `f1` |
| Mean Average Precision | `map` |
| Area Under Curve | `auc` |
| True Positives | `tp` |
| False Positives | `fp` |
| False Negatives | `fn` |


#### Output Formats

#### Link Predictions and Ground Truth
Link predictions and ground truths are stored as JSON objects. Each key is a fully qualified test artefact name, and the value is a list of source code artefact names, with each being a link:
```json
{
    "test_function_1": [
        "function_1"
    ],
    "test_function_2": [
        "function_2"
    ],
    "test_function_combined": [
        "function_1",
        "function_2"
    ]
}
```

#### Link Classifications
Link classifications are also JSON objects. Each key is a fully qualified test artefact name, and the value is another object, listing the links classified as true positives, false positives and true negatives:
```json
{
    "test_function_1": {
        "True Positives": [
            "function_1"
        ],
        "False Positives": [],
        "False Negatives": []
    },
    "test_function_2": {
        "True Positives": [
            "function_2"
        ],
        "False Positives": [
            "function_1"
        ],
        "False Negatives": []
    },
    "test_function_combined": {
        "True Positives": [
            "function_1"
        ],
        "False Positives": [],
        "False Negatives": [
            "function_2"
        ]
    }
}
```


#### Evaluation Metrics
Evaluation metrics are stored in a CSV file. Each row represents a technique, and each column represents a metric. The first column is the technique name:

| Technique | Precision | Recall | F1 | MAP | AUC | TP | FP | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tarantula | 70.3 | 86.5 | 77.6 | 87.2 | 85.9 | 45 | 19 | 7 |
| Combined | 91.3 | 80.7 | 85.7 | 87.6 | 92.4 | 42 | 4 | 10 |


## Development

### Install Dependencies
After cloning the PyTCTracer repository, installing dependencies can be done with:
```bash
pip install .
```
For development, it is recommended to install the package in editable mode, alongside the dev requirements:
```bash
pip install -e .[dev]
```
Optionally, the `env.example` file can be copied to a `.env` file, so that environment variables can be loaded in:
```bash
cp env.example .env
```
Currently, there are environment variables for the threshold of some techniques, which allow for them to be modified 'on-the-fly' without changing the code.


### Implementing a new traceability technique
The project allows for easily extending the package through implementing new traceability techniques. The `Technique` ABC provides a template class for implementing a new technique through a subclass, with specific processing of the tracing data. Only the technique's `run()` method needs to be implemented to score test-to-code pairs. The new technique should have a unique argument name, and references to the new technique need to be added in a few classes:
- `ArgNameToTechniqueMapper`: So that there is a mapping between the argument name and the technique class and its attributes.
- `TechniqueThreshold`: To add a new threshold for the technique, if required, and to map an environment variable to it.
- `Config`: To add the new technique's arg name to the list of selectable techniques, and optionally add a default threshold, and whether it should be a default technique and technique in the combined scoring.

After implementing the above, the new technique should be usable through the CLI tool, and can be selected with the `--technique` option.