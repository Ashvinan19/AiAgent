import os
import shlex
from google.genai import types

from config import COMMAND_TIMEOUT_SECONDS
from functions.path_utils import resolve_path
from functions.subprocess_utils import format_process_output

schema_run_command = types.FunctionDeclaration(
    name="run_command",
    description=(
        "Runs a shell command in the working directory sandbox. "
        "Use for pytest, uv, pip, ruff, or other CLI tools. "
        "Examples: 'python -m pytest tests.py', 'python main.py \"3+5\"'."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "command": types.Schema(
                type=types.Type.STRING,
                description="Shell command to run (executed in the working directory)",
            ),
        },
        required=["command"],
    ),
)

BLOCKED_SUBSTRINGS = [
    "rm -rf /",
    "rm -rf /*",
    ":(){ :|:& };:",
    "mkfs.",
    "dd if=",
]


def run_command(working_directory: str, command: str) -> str:
    _, error = resolve_path(working_directory, ".")
    if error:
        return error

    working_dir_abs = os.path.abspath(working_directory)

    lowered = command.lower()
    for blocked in BLOCKED_SUBSTRINGS:
        if blocked in lowered:
            return f"Error: Command blocked for safety: {command}"

    try:
        import subprocess

        if os.name == "nt":
            cmd_list = command
            use_shell = True
        else:
            cmd_list = shlex.split(command)
            use_shell = False

        result = subprocess.run(
            cmd_list,
            cwd=working_dir_abs,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT_SECONDS,
            shell=use_shell,
        )
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {COMMAND_TIMEOUT_SECONDS} seconds"
    except ValueError as e:
        return f"Error: Could not parse command: {e}"
    except Exception as e:
        return f"Error: {e}"

    return format_process_output(result)
