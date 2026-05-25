import os
from google.genai import types

from config import MAX_CHARS
from functions.path_utils import resolve_path

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the contents of a file relative to the working directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file relative to the working directory",
            ),
        },
        required=["file_path"],
    ),
)


def get_file_content(working_directory: str, file_path: str) -> str:
    target_file, error = resolve_path(working_directory, file_path)
    if error:
        return error

    if target_file is None:
        return f'Error: Invalid path "{file_path}"'

    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(target_file, encoding="utf-8", errors="replace") as f:
            content = f.read(MAX_CHARS + 1)

        if len(content) > MAX_CHARS:
            return (
                content[:MAX_CHARS]
                + f'\n[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            )

        return content
    except Exception as e:
        return f"Error: {e}"
