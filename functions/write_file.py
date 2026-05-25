import os
from google.genai import types

from functions.path_utils import resolve_path

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites a file relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file relative to the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file",
            ),
        },
        required=["file_path", "content"],
    ),
)


def write_file(working_directory: str, file_path: str, content: str) -> str:
    target_file, error = resolve_path(working_directory, file_path)
    if error:
        return error

    if target_file is None:
        return f'Error: Invalid path "{file_path}"'

    if os.path.isdir(target_file):
        return f'Error: Cannot write to "{file_path}" as it is a directory'

    try:
        parent_dir = os.path.dirname(target_file)
        os.makedirs(parent_dir, exist_ok=True)

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(content)

        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )
    except Exception as e:
        return f"Error: {e}"
