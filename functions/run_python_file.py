import os
import sys
from google.genai import types

from config import PYTHON_TIMEOUT_SECONDS
from functions.path_utils import resolve_path
from functions.subprocess_utils import format_process_output, run_in_sandbox

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional command line arguments",
            ),
        },
        required=["file_path"],
    ),
)


def run_python_file(
    working_directory: str,
    file_path: str,
    args: list[str] | None = None,
) -> str:
    target_file, error = resolve_path(working_directory, file_path)
    if error:
        return error

    if target_file is None:
        return f'Error: Invalid path "{file_path}"'

    if not os.path.isfile(target_file):
        return f'Error: "{file_path}" does not exist or is not a regular file'

    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file'

    working_dir_abs = os.path.abspath(working_directory)
    command = [sys.executable, target_file]
    if args:
        command.extend(args)

    result, run_error = run_in_sandbox(
        command, working_dir_abs, timeout=PYTHON_TIMEOUT_SECONDS
    )
    if run_error:
        return run_error

    if result is None:
        return "Error: No result from Python execution"

    return format_process_output(result)
