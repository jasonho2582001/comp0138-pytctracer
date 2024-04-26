# Replication Guidelines
This README provides guidelines for how to run the commands which allow for replicating or manipulating most of the experimental results (mainly the data found in `experiment-data/`). This assumes that you have read the main README and have understood how the package works, and you have installed `pytctracer`. If not, simply run:
```bash
pip install pytctracer
```
## Obtaining trace data
Firstly, to obtain the trace data used in the experiments, you must clone the following 4 repositories, and perform the necessary set up for each, including installing dependencies. You can check that you've installed the projects and their dependencies correctly if you run the test suite with the command: `pytest` without any errors:
* PyOpenSSL: https://github.com/pyca/pyopenssl
* Arrow: https://github.com/arrow-py/arrow
* Kedro: https://github.com/kedro-org/kedro
* Chartify: https://github.com/spotify/chartify

Once the repos have been cloned, you may choose to start with one and obtain the trace log for it. These instructions assume that you are in some terminal or code editor at the root of the project. 

With the project directory open, create a new `conftest.py` file at the project root (alternatively, you can also find any `conftest.py` that already has been defined within the test directories). Now, we want to set up the tracing of the Pytest test suite. This can be done by using the `PytestTracer` class, and the `pytest_sessionstart` and `pytest_sessionfinish` hooks. The code you add should be of the following form:

```python
import sys
from pytctracer import PytestTracer

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

def pytest_sessionfinish(session, exitstatus):
    tracer.write_to_csv()
```
To obtain the root of the project, you can run the command:
```bash
pwd
```
and paste the result into the `project_root` parameter. Pay attention to the project, and ensure that the `test_folders` and `source_folders` are correctly set. For these projects, there should only be one of each, and you should set them to the relative paths to the folders (it should just be the folder names, e.g. `["chartify"]` and `["tests"]`). Ensure you set `output_csv_file_name` to be a desired string path.

Once this is set up, you can now invoke the Pytest suite. This can simply be done with:
```bash
pytest --assert=plain
```
It is imperative that the `--assert=plain` option is selected, as it is required for the tracer to correctly extract assert statements.

Allow the test suite to run, and once it is complete, you will see that a CSV file will have been created at the path you specified. This trace log will be the ones present in `experiment-data/`.

## Produce test-to-code traceability predictions
Now that you've obtained a tracing log, you can use the `pytctracer` CLI to process and produce links for it. If you haven't obtained a tracing log, you can just use the ones located in `experiment-data/trace-logs/...`. 

Now, you can be in any directory, but it is recommended to be in the root of this `pytctracer` project, so that you also have access to `experiment-data/` for later.

Assuming that the trace log is called `trace_log.csv`, and is located at the root, create a new directory called `link-predictions`, which will store the predictions we will generate:
```bash
mkdir link-predictions
```

Now, you can run the following command to generate traceability predictions for all techniques, as well as the combined technique for the function level with the following command:
```bash
pytctracer produce-links --level function --add-combined --output-directory predictions trace_log.csv
```
After running the above command, you will see that the `predictions` directory is populated with JSON files, showing the predictions of the different techniques.

We can do the same to produce the links at the class level. Make a new directory called `class-predictions`, and use the following command:
```bash
pytctracer produce-links --level class --add-combined --output-directory class-predictions trace_log.csv
```
In a similar fashion, the `class-predictions` directory will be populated with JSON files.

You can also generate predictions for any of the trace logs in the `experiment-data` directory. The equivalent of the first command is shown, except we use the PyOpenSSL trace log found in `experiment-data/trace-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv`:
```bash
pytctracer produce-links --level function --add-combined --output-directory class-predictions  experiment-data/trace-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv
```

If the trace log was one of the example repos, you can verify that the predictions are the same as the ones in `experiment-data/link-predictions`.

## Evaluate test-to-code traceability predictions
We can also show how to replicate the classification and metric results. To do this, we will use the data found in `experiment-data` and the `evaluate-links` command. Make a directory called `classifications`. Now, choose a trace log from `experiment-data`, and a corresponding ground truth either for the function or class level. E.g. if you pick the PyOpenSSL log, then choose the ground truth for PyOpenSSL at the function or class level. 

For this example, I choose PyOpenSSL's trace located at `experiment-data/trace-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv`, and the function level ground truth at `experiment-data/ground-truths/function-level/pyopenssl/pyopenssl_ground_truth_function_level.json`. I will now generate the link classifications for every technique at the function level, as well as computing all of the metrics and storing them a csv file at the project root called `metrics.csv`.

```bash
pytctracer evaluate-links --level function --add-combined --as-percentage --classifications-output-directory classifications --metrics-output-path metrics.csv experiment-data/trace-logs/pyopenssl/pyopenssl_pytest_tracer_logs.csv experiment-data/ground-truths/function-level/pyopenssl/pyopenssl_ground_truth_function_level.json
```
As a result, the `classifications` directory will contain the classifications of the predictions for each technique, and the `metrics.csv` file will contain the metrics for each technique. You can verify that the `classifications` are the same as reported, as well as the metrics. 

## Comparing Copilot predictions and ground truth
The GitHub Copilot results can be replicated with the `compare-links` command. Assuming as before, you have a directory at the root called `copilot-classifications`, then select a set of Copilot predictions to do, and a corresponding ground truth. 

As an example, I will choose the PyOpenSSL Copilot predictions at the function level. The predictions are located at `experiment-data/link-predictions/copilot/function-level/pyopenssl/copilot_function_predicted_links.json`, and the function level ground truth at `experiment-data/ground-truths/function-level/pyopenssl/pyopenssl_ground_truth_function_level.json`. I will now generate the classifications at the function level and store in a single file, since this time we are only performing a evaluation of 1 set of predictions. I choose this file to be called `copilot_classifications.json`, as well as all of the metrics and storing them at `copilot_metrics.csv`

```bash
pytctracer compare-links --as-percentage --classifications-output-path copilot_classifications.json --metrics-output-path copilot_metrics.csv experiment-data/link-predictions/copilot/function-level/pyopenssl/copilot_function_predicted_links.json experiment-data/ground-truths/function-level/pyopenssl/pyopenssl_ground_truth_function_level.json
```
Now, you can repeat this process for another pair of Copilot predictions, and the ground truth.

## Varying the commands
As per reading the original documentation README, you can see how you can change what techniques you want to run, and what metrics you want to compute for. With the examples above, you should have sufficient information to fully leverage the customisability of the commands.





