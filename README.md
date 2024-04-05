# PyTCTracer
PyTCTracer is a test-to-code traceability approach and library, which allows for dynamic code tracing of Python repositories using the Pytest testing framework, and automatic generation of test-to-code traceability links from the trace data using a number of established traceability techniques. 

There are two core components in the library:
- `PytestTracer`: A class that is used to trace the execution of Pytest unit tests and record dynamic tracing information to a CSV log file.
- `pytctracer` CLI: A CLI tool which can read and parse the dynamic information from the log file, apply traceability techniques to generate link predictions, and evaluate the predictions against a ground truth.

This library forms part of an undergraduate research project for a Masters of Engineering in Computer Science at UCL (University College London).