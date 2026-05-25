from pathlib import Path

from functions.grep_files import grep_files


def test_finds_matches_across_project(sandbox: Path):
    result = grep_files(str(sandbox), r"def \w+")
    assert "main.py" in result
    assert "util.py" in result
    assert "def greet" in result
    assert "def double" in result


def test_filters_by_extension(sandbox: Path):
    result = grep_files(str(sandbox), "text", file_extension=".txt")
    assert "notes.txt" in result
    assert "main.py" not in result


def test_returns_no_match_message(sandbox: Path):
    result = grep_files(str(sandbox), "this_pattern_definitely_not_present_xyz")
    assert "No matches" in result


def test_rejects_invalid_regex(sandbox: Path):
    result = grep_files(str(sandbox), "(unclosed")
    assert result.startswith("Error:")
    assert "regex" in result.lower()


def test_skips_ignored_directories(sandbox: Path):
    (sandbox / "__pycache__" / "match_me.py").write_text(
        "should_not_match", encoding="utf-8"
    )
    result = grep_files(str(sandbox), "should_not_match")
    assert "No matches" in result or "__pycache__" not in result
