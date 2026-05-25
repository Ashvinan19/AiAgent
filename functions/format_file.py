import os
import sys
from google.genai import types

from functions.path_utils import resolve_path
from functions.subprocess_utils import format_process_output, run_in_sandbox

schema_format_file = types.FunctionDeclaration(
    name="format_file",
    description=(
        "Formats a Python file using ruff (PEP 8 style). "
        "Install ruff in the environment if formatting fails."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file relative to the working directory",
            ),
        },
        required=["file_path"],
    ),
)


def format_file(working_directory: str, file_path: str) -> str:
    target_file, error = resolve_path(working_directory, file_path)
    if error:
        return error

    if target_file is None:
        return f'Error: Invalid path "{file_path}"'

    if not os.path.isfile(target_file):
        return f'Error: File not found: "{file_path}"'

    if not file_path.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file'

    working_dir_abs = os.path.abspath(working_directory)
    command = [sys.executable, "-m", "ruff", "format", target_file]

    result, run_error = run_in_sandbox(command, working_dir_abs, timeout=30)
    if run_error:
        return (
            f"{run_error}. Try install_dependencies with packages=['ruff'] first."
        )

    if result is None:
        return "Error: No result from formatter"

    if result.returncode == 0:
        return f'Successfully formatted "{file_path}"'

    return format_process_output(result, label=f'Error formatting "{file_path}"')
