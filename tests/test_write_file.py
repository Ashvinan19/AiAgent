from pathlib import Path

from functions.write_file import write_file


def test_creates_new_file(sandbox: Path):
    result = write_file(str(sandbox), "new.txt", "hello")
    assert "Successfully wrote" in result
    assert (sandbox / "new.txt").read_text(encoding="utf-8") == "hello"


def test_overwrites_existing_file(sandbox: Path):
    result = write_file(str(sandbox), "main.py", "print('new')")
    assert "Successfully wrote" in result
    assert (sandbox / "main.py").read_text(encoding="utf-8") == "print('new')"


def test_creates_missing_parent_directories(sandbox: Path):
    result = write_file(str(sandbox), "deep/dir/file.txt", "content")
    assert "Successfully wrote" in result
    assert (sandbox / "deep" / "dir" / "file.txt").exists()


def test_blocks_path_traversal(sandbox: Path):
    result = write_file(str(sandbox), "../escape.txt", "bad")
    assert result.startswith("Error:")
    assert "outside" in result


def test_refuses_to_overwrite_directory(sandbox: Path):
    result = write_file(str(sandbox), "pkg", "should fail")
    assert result.startswith("Error:")
