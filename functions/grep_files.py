import os
import re
from google.genai import types

from config import IGNORE_DIRS, IGNORE_EXTENSIONS, MAX_GREP_MATCHES
from functions.path_utils import resolve_path

schema_grep_files = types.FunctionDeclaration(
    name="grep_files",
    description=(
        "Search for a regex pattern across text files in the working directory. "
        "Returns matching file paths, line numbers, and line content."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "pattern": types.Schema(
                type=types.Type.STRING,
                description="Regex pattern to search for",
            ),
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Subdirectory to search in, relative to working directory (default '.')",
            ),
            "file_extension": types.Schema(
                type=types.Type.STRING,
                description="Optional file extension filter, e.g. '.py' or '.md'",
            ),
        },
        required=["pattern"],
    ),
)


def _iter_files(root: str, directory: str, file_extension: str | None) -> list[str]:
    files: list[str] = []
    start = os.path.join(root, directory) if directory != "." else root

    for dirpath, dirnames, filenames in os.walk(start):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            if file_extension and not filename.endswith(file_extension):
                continue

            _, ext = os.path.splitext(filename)
            if ext in IGNORE_EXTENSIONS:
                continue

            files.append(os.path.join(dirpath, filename))

    return files


def grep_files(
    working_directory: str,
    pattern: str,
    directory: str = ".",
    file_extension: str | None = None,
) -> str:
    root, error = resolve_path(working_directory, ".")
    if error:
        return error

    search_root, search_error = resolve_path(working_directory, directory)
    if search_error:
        return search_error

    if root is None or search_root is None:
        return "Error: Invalid working directory"

    if not os.path.isdir(search_root):
        return f'Error: "{directory}" is not a directory'

    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"Error: Invalid regex pattern: {e}"

    matches: list[str] = []
    files = _iter_files(root, directory, file_extension)

    for file_path in files:
        rel_path = os.path.relpath(file_path, root)
        try:
            with open(file_path, encoding="utf-8", errors="replace") as f:
                for line_no, line in enumerate(f, start=1):
                    if regex.search(line):
                        snippet = line.rstrip("\n")
                        if len(snippet) > 200:
                            snippet = snippet[:200] + "..."
                        matches.append(f"{rel_path}:{line_no}: {snippet}")

                        if len(matches) >= MAX_GREP_MATCHES:
                            matches.append(
                                f"... truncated after {MAX_GREP_MATCHES} matches"
                            )
                            return "\n".join(matches)
        except OSError:
            continue

    if not matches:
        return f'No matches found for pattern "{pattern}"'

    return "\n".join(matches)
