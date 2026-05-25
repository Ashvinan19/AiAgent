import os
from google.genai import types

from config import IGNORE_DIRS, IGNORE_EXTENSIONS, MAX_TREE_DEPTH
from functions.path_utils import resolve_path

schema_get_project_tree = types.FunctionDeclaration(
    name="get_project_tree",
    description=(
        "Returns a recursive directory tree of the project relative to the working "
        "directory. Skips common noise directories (.git, __pycache__, .venv, etc.)."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "max_depth": types.Schema(
                type=types.Type.INTEGER,
                description=f"Maximum directory depth to traverse (default {MAX_TREE_DEPTH})",
            ),
        },
    ),
)


def _should_skip(name: str, is_dir: bool) -> bool:
    if is_dir and name in IGNORE_DIRS:
        return True
    if not is_dir:
        _, ext = os.path.splitext(name)
        if ext in IGNORE_EXTENSIONS:
            return True
    return False


def _build_tree(root: str, prefix: str, depth: int, max_depth: int) -> list[str]:
    if depth > max_depth:
        return [f"{prefix}... (max depth reached)"]

    lines: list[str] = []

    try:
        entries = sorted(os.listdir(root))
    except OSError as e:
        return [f"{prefix}[error listing: {e}]"]

    for name in entries:
        path = os.path.join(root, name)
        is_dir = os.path.isdir(path)

        if _should_skip(name, is_dir):
            continue

        if is_dir:
            lines.append(f"{prefix}{name}/")
            lines.extend(_build_tree(path, prefix + "  ", depth + 1, max_depth))
        else:
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            lines.append(f"{prefix}{name} ({size} bytes)")

    return lines


def get_project_tree(
    working_directory: str,
    max_depth: int = MAX_TREE_DEPTH,
) -> str:
    target_dir, error = resolve_path(working_directory, ".")
    if error:
        return error

    if target_dir is None or not os.path.isdir(target_dir):
        return "Error: Working directory is not valid"

    max_depth = max(1, min(max_depth, MAX_TREE_DEPTH))
    lines = [f"Project tree (max_depth={max_depth}):"]
    lines.extend(_build_tree(target_dir, "", 0, max_depth))
    return "\n".join(lines)
