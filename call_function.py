from collections.abc import Callable
from google.genai import types

from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.get_project_tree import get_project_tree, schema_get_project_tree
from functions.grep_files import grep_files, schema_grep_files
from functions.write_file import write_file, schema_write_file
from functions.edit_file import edit_file, schema_edit_file
from functions.format_file import format_file, schema_format_file
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.run_command import run_command, schema_run_command
from functions.install_dependencies import (
    install_dependencies,
    schema_install_dependencies,
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_project_tree,
        schema_get_files_info,
        schema_get_file_content,
        schema_grep_files,
        schema_write_file,
        schema_edit_file,
        schema_format_file,
        schema_run_python_file,
        schema_run_command,
        schema_install_dependencies,
    ],
)

function_map: dict[str, Callable[..., str]] = {
    "get_project_tree": get_project_tree,
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "grep_files": grep_files,
    "write_file": write_file,
    "edit_file": edit_file,
    "format_file": format_file,
    "run_python_file": run_python_file,
    "run_command": run_command,
    "install_dependencies": install_dependencies,
}


def call_function(
    function_call: types.FunctionCall,
    working_directory: str,
    verbose: bool = False,
) -> tuple[types.Content, str]:
    function_name = function_call.name or ""

    if verbose:
        print(f"Calling function: {function_name}({function_call.args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in function_map:
        error = f"Unknown function: {function_name}"
        return (
            types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"error": error},
                    )
                ],
            ),
            error,
        )

    args = dict(function_call.args) if function_call.args else {}
    args["working_directory"] = working_directory

    function_result = function_map[function_name](**args)

    return (
        types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        ),
        function_result,
    )
