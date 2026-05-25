import os
import sys
from google.genai import types

from config import COMMAND_TIMEOUT_SECONDS
from functions.path_utils import resolve_path
from functions.subprocess_utils import format_process_output, run_in_sandbox

schema_install_dependencies = types.FunctionDeclaration(
    name="install_dependencies",
    description=(
        "Installs Python packages into the current environment using pip. "
        "Use when imports fail or a library is missing."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "packages": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Package names to install, e.g. ['pytest', 'ruff']",
            ),
        },
        required=["packages"],
    ),
)


def install_dependencies(working_directory: str, packages: list[str]) -> str:
    _, error = resolve_path(working_directory, ".")
    if error:
        return error

    if not packages:
        return "Error: No packages specified"

    working_dir_abs = os.path.abspath(working_directory)
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        *packages,
    ]

    result, run_error = run_in_sandbox(
        command, working_dir_abs, timeout=COMMAND_TIMEOUT_SECONDS
    )
    if run_error:
        return run_error

    if result is None:
        return "Error: No result from pip"

    if result.returncode == 0:
        return f"Successfully installed: {', '.join(packages)}"

    return format_process_output(
        result, label=f"Error installing {', '.join(packages)}"
    )
