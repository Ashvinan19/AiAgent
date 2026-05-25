from pathlib import Path

from functions.get_file_content import get_file_content


def test_reads_file(sandbox: Path):
    result = get_file_content(str(sandbox), "main.py")
    assert "def greet" in result
    assert not result.startswith("Error:")


def test_blocks_path_traversal(sandbox: Path):
    result = get_file_content(str(sandbox), "../etc/passwd")
    assert result.startswith("Error:")
    assert "outside" in result


def test_errors_on_missing_file(sandbox: Path):
    result = get_file_content(str(sandbox), "missing.py")
    assert result.startswith("Error:")
    assert "not found" in result.lower()


def test_truncates_large_files(sandbox: Path, monkeypatch):
    monkeypatch.setattr("functions.get_file_content.MAX_CHARS", 50)
    (sandbox / "big.txt").write_text("x" * 500, encoding="utf-8")
    result = get_file_content(str(sandbox), "big.txt")
    assert "truncated" in result
    assert result.count("x") <= 60
