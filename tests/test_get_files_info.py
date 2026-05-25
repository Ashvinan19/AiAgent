from pathlib import Path

from functions.get_files_info import get_files_info


def test_lists_current_directory(sandbox: Path):
    result = get_files_info(str(sandbox), ".")
    assert "main.py" in result
    assert "pkg" in result
    assert "is_dir=True" in result
    assert "is_dir=False" in result


def test_lists_subdirectory(sandbox: Path):
    result = get_files_info(str(sandbox), "pkg")
    assert "util.py" in result
    assert "__init__.py" in result


def test_blocks_path_traversal(sandbox: Path):
    result = get_files_info(str(sandbox), "../")
    assert result.startswith("Error:")
    assert "outside" in result


def test_errors_on_missing_directory(sandbox: Path):
    result = get_files_info(str(sandbox), "does_not_exist")
    assert result.startswith("Error:")
    assert "not a directory" in result


def test_errors_when_target_is_a_file(sandbox: Path):
    result = get_files_info(str(sandbox), "main.py")
    assert result.startswith("Error:")
