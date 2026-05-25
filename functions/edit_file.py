import os
from google.genai import types

from functions.path_utils import resolve_path

schema_edit_file = types.FunctionDeclaration(
    name="edit_file",
    description=(
        "Edits an existing file by replacing old_string with new_string. "
        "Use for surgical patches instead of rewriting entire files. "
        "old_string must appear exactly once unless replace_all is true."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file relative to the working directory",
            ),
            "old_string": types.Schema(
                type=types.Type.STRING,
                description="Exact text to find and replace",
            ),
            "new_string": types.Schema(
                type=types.Type.STRING,
                description="Replacement text",
            ),
            "replace_all": types.Schema(
                type=types.Type.BOOLEAN,
                description="Replace every occurrence (default false)",
            ),
        },
        required=["file_path", "old_string", "new_string"],
    ),
)


def edit_file(
    working_directory: str,
    file_path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
) -> str:
    target_file, error = resolve_path(working_directory, file_path)
    if error:
        return error

    if target_file is None:
        return f'Error: Invalid path "{file_path}"'

    if not os.path.isfile(target_file):
        return f'Error: File not found: "{file_path}"'

    try:
        with open(target_file, encoding="utf-8") as f:
            content = f.read()

        count = content.count(old_string)
        if count == 0:
            return (
                f'Error: old_string not found in "{file_path}". '
                "Read the file first to get the exact text."
            )

        if not replace_all and count > 1:
            return (
                f'Error: old_string appears {count} times in "{file_path}". '
                "Provide more context or set replace_all=true."
            )

        if replace_all:
            updated = content.replace(old_string, new_string)
            replaced_count = count
        else:
            updated = content.replace(old_string, new_string, 1)
            replaced_count = 1

        with open(target_file, "w", encoding="utf-8") as f:
            f.write(updated)

        return (
            f'Successfully edited "{file_path}" '
            f"({replaced_count} replacement(s), {len(updated)} characters total)"
        )

    except Exception as e:
        return f"Error: {e}"
