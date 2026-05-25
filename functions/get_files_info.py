import os
from google.genai import types

from functions.path_utils import resolve_path

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)


def get_files_info(working_directory: str, directory: str = ".") -> str:
    target_dir, error = resolve_path(working_directory, directory)
    if error:
        return error

    if target_dir is None:
        return f'Error: Invalid directory "{directory}"'

    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'

    try:
        file_info = []

        for item in sorted(os.listdir(target_dir)):
            item_path = os.path.join(target_dir, item)
            file_size = os.path.getsize(item_path)
            is_dir = os.path.isdir(item_path)

            file_info.append(
                f"- {item}: file_size={file_size} bytes, is_dir={is_dir}"
            )

        return "\n".join(file_info) if file_info else "(empty directory)"
    except Exception as e:
        return f"Error: {e}"
