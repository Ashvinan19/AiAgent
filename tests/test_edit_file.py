from pathlib import Path

from functions.edit_file import edit_file


def test_replaces_single_occurrence(sandbox: Path):
    result = edit_file(str(sandbox), "main.py", "hello", "hi")
    assert "Successfully edited" in result
    assert "hi" in (sandbox / "main.py").read_text(encoding="utf-8")


def test_errors_when_old_string_not_found(sandbox: Path):
    result = edit_file(str(sandbox), "main.py", "nonexistent_text_xyz", "new")
    assert result.startswith("Error:")
    assert "not found" in result


def test_errors_when_old_string_ambiguous(sandbox: Path):
    (sandbox / "dup.txt").write_text("apple\napple\n", encoding="utf-8")
    result = edit_file(str(sandbox), "dup.txt", "apple", "banana")
    assert result.startswith("Error:")
    assert "appears 2 times" in result


def test_replace_all_handles_multiple_occurrences(sandbox: Path):
    (sandbox / "dup.txt").write_text("apple\napple\napple\n", encoding="utf-8")
    result = edit_file(
        str(sandbox), "dup.txt", "apple", "banana", replace_all=True
    )
    assert "Successfully edited" in result
    assert (sandbox / "dup.txt").read_text(encoding="utf-8") == "banana\nbanana\nbanana\n"


def test_blocks_path_traversal(sandbox: Path):
    result = edit_file(str(sandbox), "../outside.txt", "a", "b")
    assert result.startswith("Error:")


def test_errors_on_missing_file(sandbox: Path):
    result = edit_file(str(sandbox), "missing.txt", "a", "b")
    assert result.startswith("Error:")
    assert "not found" in result.lower()
