from pathlib import Path

from functions.get_project_tree import get_project_tree


def test_lists_files_and_directories(sandbox: Path):
    result = get_project_tree(str(sandbox))
    assert "main.py" in result
    assert "pkg/" in result
    assert "util.py" in result


def test_skips_pycache(sandbox: Path):
    result = get_project_tree(str(sandbox))
    assert "__pycache__" not in result
    assert "ignored.pyc" not in result


def test_respects_max_depth(sandbox: Path):
    nested = sandbox / "a" / "b" / "c"
    nested.mkdir(parents=True)
    (nested / "deep.py").write_text("# deep", encoding="utf-8")
    result = get_project_tree(str(sandbox), max_depth=1)
    assert "a/" in result
    assert "deep.py" not in result
