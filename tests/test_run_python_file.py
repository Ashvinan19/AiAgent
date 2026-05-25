from pathlib import Path

from functions.run_python_file import run_python_file


def test_executes_python_file(sandbox: Path):
    result = run_python_file(str(sandbox), "main.py")
    assert "hello world" in result


def test_captures_exit_code_on_failure(sandbox: Path):
    (sandbox / "broken.py").write_text(
        "raise RuntimeError('boom')\n", encoding="utf-8"
    )
    result = run_python_file(str(sandbox), "broken.py")
    assert "Process exited with code" in result
    assert "RuntimeError" in result or "boom" in result


def test_rejects_non_python_file(sandbox: Path):
    result = run_python_file(str(sandbox), "notes.txt")
    assert result.startswith("Error:")
    assert "not a Python file" in result


def test_errors_on_missing_file(sandbox: Path):
    result = run_python_file(str(sandbox), "missing.py")
    assert result.startswith("Error:")


def test_blocks_path_traversal(sandbox: Path):
    result = run_python_file(str(sandbox), "../escape.py")
    assert result.startswith("Error:")
