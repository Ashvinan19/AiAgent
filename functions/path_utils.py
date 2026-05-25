import os

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".eggs",
}


def resolve_path(working_directory: str, relative_path: str) -> tuple[str | None, str | None]:
    """Resolve a path inside the sandbox. Returns (absolute_path, error_message)."""
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target = os.path.normpath(os.path.join(working_dir_abs, relative_path))

        if os.path.commonpath([working_dir_abs, target]) != working_dir_abs:
            return None, (
                f'Error: Cannot access "{relative_path}" as it is outside '
                "the permitted working directory"
            )

        return target, None
    except ValueError:
        return None, (
            f'Error: Cannot access "{relative_path}" (invalid path for this platform)'
        )
    except Exception as e:
        return None, f"Error: {e}"
