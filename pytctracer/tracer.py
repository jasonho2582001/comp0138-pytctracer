from types import FrameType, CodeType
from typing import List, Optional, Any, Tuple
import os
import inspect
import pytest
import csv
import threading
import dis
from pytctracer.config.constants import (
    TraceDataHeader,
    TestingMethodType,
    TraceDataVariable,
    EventType,
    FunctionType,
    InstructionOpname,
    SetProfileCEventType,
    SetTraceEventType,
)

TRACE_QUALIFIED_NAME = "PytestTracer.trace"
TEST_PREFIX = "test"
TEST_CLASS_PREFIX = "Test"
LOCALS = "<locals>"
MODULE = "<module>"


class PytestTracer:
    def __init__(
        self,
        project_root: str,
        test_folders: List[str],
        source_folders: List[str],
        output_csv_file_name: str,
    ) -> None:
        project_root = os.path.normcase(project_root)
        self._project_root = os.path.normcase(os.path.abspath(project_root))
        self._test_folders = [
            os.path.normcase(os.path.join(self._project_root, test_folder))
            for test_folder in test_folders
        ]
        self._source_folders = [
            os.path.normcase(os.path.join(self._project_root, source_folder))
            for source_folder in source_folders
        ]
        self._pytest_path = os.path.normcase(os.path.dirname(inspect.getfile(pytest)))
        # Retrieves the absolute file path to the directory of the pytest module
        self._csv_headers = [header for header in TraceDataHeader]
        self._csv_name = output_csv_file_name
        self._test_function_stack = []
        self._function_stack = []
        self._current_depth = 0
        self._file_of_last_assert = None
        self._line_of_last_assert = None
        self._csv_data = []
        self._in_line_functions_left_list = []
        self._assert_line_values = []
        self._handle_in_line_functions = False
        self._in_line_function_calls = 0

    def trace(self, frame: FrameType, event, arg=None):
        if not self.our_frame(frame):
            code_of_current_frame = frame.f_code
            file_name = os.path.normcase(code_of_current_frame.co_filename)
            function_name = code_of_current_frame.co_name
            qualified_function_name = code_of_current_frame.co_qualname
            current_thread_id = threading.current_thread().ident
            line_number = frame.f_lineno
            function_type = self._check_function_type(
                file_name=file_name,
                function_name=function_name,
                qualified_function_name=qualified_function_name,
                line_number=line_number,
                code=code_of_current_frame,
            )

            # Only trace after if the function is one of unittest, test or source
            if function_type and MODULE not in qualified_function_name:
                qualified_class_name, class_name = self._get_class_names(
                    code_qualified_name=qualified_function_name,
                    function_name=function_name,
                    file_name=file_name,
                    function_type=function_type,
                )
                fully_qualified_function_name = self._get_fully_qualified_name(
                    file_name=file_name,
                    code_qualified_name=qualified_function_name,
                    function_type=function_type,
                )
                fully_qualified_class_name = self._get_fully_qualified_name(
                    file_name=file_name,
                    code_qualified_name=qualified_class_name,
                    function_type=function_type,
                )
                if (
                    event == SetTraceEventType.LINE
                    and function_type == FunctionType.ASSERT
                ):
                    if self._check_in_line_functions_in_assert():
                        self._save_assert_line_values(
                            depth=self._current_depth,
                            function_type=function_type,
                            function_name=function_name,
                            fully_qualified_function_name=fully_qualified_function_name,
                            class_name=class_name,
                            fully_qualified_class_name=fully_qualified_class_name,
                            line_number=line_number,
                            event_type=EventType.LINE,
                            return_value=str(arg),
                            return_type=str(type(arg)),
                            testing_method="",
                            thread_id=current_thread_id,
                        )
                    else:
                        self._add_csv_row_data(
                            depth=self._current_depth,
                            function_type=function_type,
                            function_name=function_name,
                            fully_qualified_function_name=fully_qualified_function_name,
                            class_name=class_name,
                            fully_qualified_class_name=fully_qualified_class_name,
                            line_number=line_number,
                            event_type=EventType.LINE,
                            return_value=str(arg),
                            return_type=str(type(arg)),
                            testing_method="",
                            thread_id=current_thread_id,
                        )

                elif event == SetTraceEventType.CALL:
                    testing_method = (
                        TestingMethodType.TEST_METHOD_CALL
                        if function_type == FunctionType.TEST_FUNCTION
                        and len(self._test_function_stack) == 0
                        else ""
                    )  # Testing method is whether the actual function is a unit test or not
                    self._add_csv_row_data(
                        depth=self._current_depth,
                        function_type=function_type,
                        function_name=function_name,
                        fully_qualified_function_name=fully_qualified_function_name,
                        class_name=class_name,
                        fully_qualified_class_name=fully_qualified_class_name,
                        line_number=line_number,
                        event_type=EventType.CALL,
                        testing_method=testing_method,
                        thread_id=current_thread_id,
                    )
                    self._function_stack.append(
                        (fully_qualified_function_name, self._current_depth)
                    )
                    if function_type.startswith(TEST_PREFIX.upper()):
                        self._test_function_stack.append(fully_qualified_function_name)

                    self._current_depth += 1

                elif event == SetTraceEventType.RETURN:
                    # Keep track of the last function that was last returned
                    self._current_depth -= 1
                    self._function_stack.pop()
                    # print(f"{'  ' * (self._current_depth)}< {self._current_depth}: Function '{fully_qualified_function_name}()' returned at line {line_number} with value: '{arg}' of type {type(arg)}")
                    if (
                        function_type.startswith(TEST_PREFIX.upper())
                        or function_type == FunctionType.ASSERT
                    ):
                        self._test_function_stack.pop()
                        # if len(self._test_function_stack) == 0:
                        #     print(f"=== EXITING TEST FUNCTION '{fully_qualified_function_name}\n")
                    if function_type == FunctionType.ASSERT:
                        # If an assert happens to be on the last line, it may get caught as a return event, so we add a duplicate entry to account for assert line and return
                        self._add_csv_row_data(
                            depth=self._current_depth + 1,
                            function_type=function_type,
                            function_name=function_name,
                            fully_qualified_function_name=fully_qualified_function_name,
                            class_name=class_name,
                            fully_qualified_class_name=fully_qualified_class_name,
                            line_number=line_number,
                            event_type=EventType.RETURN,
                            return_value=str(arg),
                            return_type=str(type(arg)),
                            testing_method="",
                            thread_id=current_thread_id,
                        )
                        function_type = FunctionType.TEST_FUNCTION
                    testing_method = (
                        TestingMethodType.TEST_METHOD_RETURN
                        if function_type == FunctionType.TEST_FUNCTION
                        and len(self._test_function_stack) == 0
                        else ""
                    )
                    self._add_csv_row_data(
                        depth=self._current_depth,
                        function_type=function_type,
                        function_name=function_name,
                        fully_qualified_function_name=fully_qualified_function_name,
                        class_name=class_name,
                        fully_qualified_class_name=fully_qualified_class_name,
                        line_number=line_number,
                        event_type=EventType.RETURN,
                        return_value=str(arg),
                        return_type=str(type(arg)),
                        testing_method=testing_method,
                        thread_id=current_thread_id,
                    )
                    self._check_remaining_in_line_functions(self._current_depth)

                elif event == SetTraceEventType.EXCEPTION:
                    exc_type, exc_value, exc_traceback = arg
                    # print(f"{'  ' * (self._current_depth - 1)}- {self._current_depth}: Function '{fully_qualified_function_name}()' at line {line_number} has raised an Exception, with exception type: {exc_type} and message: '{str(exc_value)}'")
                    self._add_csv_row_data(
                        depth=self._current_depth,
                        function_type=function_type,
                        function_name=function_name,
                        fully_qualified_function_name=fully_qualified_function_name,
                        class_name=class_name,
                        fully_qualified_class_name=fully_qualified_class_name,
                        line_number=line_number,
                        event_type=EventType.EXCEPTION,
                        exception_type=exc_type,
                        exception_message=str(exc_value),
                    )

        return self.trace

    def trace_in_built(self, _frame: FrameType, event, _arg=None):
        # Handle in-line function returns that don't get captured by sys.settrace, for assert checking
        # For example, isinstance within an assert statement
        # These built in functions won't be caught by the sys.settrace function, so we need to check
        # for them here.
        if event == SetProfileCEventType.C_CALL:
            self._current_depth += 1
        if (
            event == SetProfileCEventType.C_RETURN
            or event == SetProfileCEventType.C_EXCEPTION
        ):
            self._current_depth -= 1
            self._check_remaining_in_line_functions(self._current_depth)

    def write_to_csv(self) -> None:
        with open(self._csv_name, "w", newline="") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=self._csv_headers)
            csv_writer.writeheader()
            for data_row in self._csv_data:
                csv_writer.writerow(data_row)

    def our_frame(self, frame: FrameType) -> bool:
        """Return true if `frame` is in the current (inspecting) class."""
        return frame.f_code.co_qualname == TRACE_QUALIFIED_NAME

    def _add_csv_row_data(
        self,
        depth: int,
        function_type: str,
        function_name: str,
        fully_qualified_function_name: str,
        class_name: str,
        fully_qualified_class_name: str,
        line_number: int,
        event_type: str,
        return_value: Optional[Any] = "",
        return_type: Optional[str] = "",
        exception_type: Optional[str] = "",
        exception_message: Optional[str] = "",
        testing_method: Optional[str] = "",
        thread_id: Optional[int] = None,
    ):
        data = {
            TraceDataHeader.DEPTH: depth,
            TraceDataHeader.FUNCTION_TYPE: function_type,
            TraceDataHeader.TESTNG_METHOD: testing_method,
            TraceDataHeader.FUNCTION_NAME: function_name,
            TraceDataHeader.FULLY_QUALIFIED_FUNCTION_NAME: fully_qualified_function_name,
            TraceDataHeader.CLASS_NAME: class_name,
            TraceDataHeader.FULLY_QUALIFIED_CLASS_NAME: fully_qualified_class_name,
            TraceDataHeader.LINE: line_number,
            TraceDataHeader.EVENT_TYPE: event_type,
            TraceDataHeader.RETURN_VALUE: return_value,
            TraceDataHeader.RETURN_TYPE: return_type,
            TraceDataHeader.EXCEPTION_TYPE: exception_type,
            TraceDataHeader.EXCEPTION_MESSAGE: exception_message,
            TraceDataHeader.THREAD_ID: thread_id,
        }
        self._csv_data.append(data)

    def _get_class_names(
        self,
        code_qualified_name: str,
        function_name: str,
        file_name: str,
        function_type: str,
    ) -> Tuple[str, str]:
        if code_qualified_name != function_name and not code_qualified_name.startswith(
            LOCALS
        ):
            class_name_list = code_qualified_name.split(".")

            # Remove last element, which should be the function name
            class_name_list.pop()

            # Check current last element is not <locals>. If it is, we need to remove it, and the previous element
            # This represents an inner function, so we need to remove it as well to get the actual class
            while class_name_list and class_name_list[-1] == LOCALS:
                class_name_list.pop()
                class_name_list.pop()

            if class_name_list:
                return ".".join(class_name_list), class_name_list[-1]

        module_name = self._get_module_name(file_name, function_type)

        return "", module_name.split(".")[-1]

    def _get_module_name(self, file_name: str, function_type: str) -> str:
        relative_file_path = os.path.relpath(file_name, self._project_root)
        relative_file_path = relative_file_path.replace(os.path.sep, "/")

        # remove file extension
        module_path, _ = os.path.splitext(relative_file_path)

        module_name = module_path.replace("/", ".")

        return module_name

    def _get_fully_qualified_name(
        self, file_name: str, code_qualified_name: str, function_type: str
    ) -> str:
        module_name = self._get_module_name(file_name, function_type)

        return (
            (module_name + "." + code_qualified_name)
            if code_qualified_name
            else module_name
        )

    def _check_assert_and_in_line_functions(
        self, file_name: str, code: CodeType, line_number: int
    ) -> bool:
        byte_code_iterator = dis.Bytecode(code)
        assert_found = False
        call_line_numbers = []
        for instruction in byte_code_iterator:
            byte_code_line_number = instruction.positions.lineno
            if InstructionOpname.CALL in instruction.opname:
                call_line_numbers.append(byte_code_line_number)
            if (
                line_number == byte_code_line_number
                and instruction.opname == InstructionOpname.LOAD_ASSERTION_ERROR
                and (
                    line_number != self._line_of_last_assert
                    or file_name != self._file_of_last_assert
                )
            ):
                self._line_of_last_assert = line_number
                self._file_of_last_assert = file_name
                assert_found = True

        if assert_found:
            count = call_line_numbers.count(line_number)
            if count > 0:
                self._in_line_functions_left_list.append(count)
                self._handle_in_line_functions = True

        return assert_found

    def _check_in_line_functions_in_assert(self) -> bool:
        if self._in_line_function_calls > 0:
            self._in_line_functions_left_list.append(self._in_line_function_calls)
            return True

        return False

    def _check_is_assert(
        self, file_name: str, line_number: int, code: CodeType
    ) -> bool:
        byte_code_iterator = dis.Bytecode(code)
        is_assert = False
        calls = 0
        for instruction in byte_code_iterator:
            byte_code_line_number = instruction.positions.lineno
            if (
                line_number == byte_code_line_number
                and InstructionOpname.CALL in instruction.opname
            ):
                calls += 1
            if (
                line_number == byte_code_line_number
                and instruction.opname == InstructionOpname.LOAD_ASSERTION_ERROR
                and (
                    line_number != self._line_of_last_assert
                    or file_name != self._file_of_last_assert
                )
            ):
                self._line_of_last_assert = line_number
                self._file_of_last_assert = file_name
                is_assert = True

        if is_assert:
            self._in_line_function_calls = calls
            return True
        else:
            self._in_line_function_calls = 0

        return False

    def _check_function_type(
        self,
        file_name: str,
        function_name: str,
        qualified_function_name: str,
        line_number: int,
        code: CodeType,
    ) -> str:
        if file_name.startswith(self._pytest_path):
            # ignore calls to the pytest library code
            return None

        for test_folder in self._test_folders:
            if file_name.startswith(test_folder):
                if (
                    function_name == qualified_function_name
                    and qualified_function_name.startswith(TEST_CLASS_PREFIX)
                ):
                    return FunctionType.TEST_CLASS
                if self._check_is_assert(file_name, line_number, code):
                    return FunctionType.ASSERT
                if function_name.startswith(TEST_PREFIX):
                    return FunctionType.TEST_FUNCTION
                return FunctionType.TEST_HELPER

        for source_folder in self._source_folders:
            if file_name.startswith(source_folder):
                return FunctionType.SOURCE

        return None

    def _save_assert_line_values(
        self,
        depth: int,
        function_type: str,
        function_name: str,
        fully_qualified_function_name: str,
        class_name: str,
        fully_qualified_class_name: str,
        line_number: str,
        event_type: str,
        return_value: str,
        return_type: str,
        testing_method: str,
        thread_id: int,
    ) -> None:
        assert_line_data = {
            TraceDataVariable.DEPTH: depth,
            TraceDataVariable.FUNCTION_TYPE: function_type,
            TraceDataVariable.FUNCTION_NAME: function_name,
            TraceDataVariable.FULLY_QUALIFIED_FUNCTION_NAME: fully_qualified_function_name,
            TraceDataVariable.CLASS_NAME: class_name,
            TraceDataVariable.FULLY_QUALIFIED_CLASS_NAME: fully_qualified_class_name,
            TraceDataVariable.LINE_NUMBER: line_number,
            TraceDataVariable.EVENT_TYPE: event_type,
            TraceDataVariable.RETURN_VALUE: return_value,
            TraceDataVariable.RETURN_TYPE: return_type,
            TraceDataVariable.TESTING_METHOD: testing_method,
            TraceDataVariable.THREAD_ID: thread_id,
        }
        # Data of the line of trace occuring due to an in-line assert, so that we store
        # to add to the trace later

        self._assert_line_values.append(assert_line_data)

    def _check_remaining_in_line_functions(self, depth: int) -> bool:
        if self._in_line_functions_left_list:
            prev_assert_depth = self._assert_line_values[-1][TraceDataVariable.DEPTH]
            if prev_assert_depth == depth:
                self._in_line_functions_left_list[-1] -= 1
                if self._in_line_functions_left_list[-1] == 0:
                    self._in_line_functions_left_list.pop()
                    last_assert_values = self._assert_line_values.pop()
                    self._add_csv_row_data(**last_assert_values)
                return True

        return False


__all__ = ["PytestTracer"]
