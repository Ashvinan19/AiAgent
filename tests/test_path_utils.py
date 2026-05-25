import os
from pathlib import Path

from functions.path_utils import resolve_path


def test_resolves_simple_relative_path(sandbox: Path):
    target, error = resolve_path(str(sandbox), "main.py")
    assert error is None
    assert target is not None
    assert os.path.normpath(target) == os.path.normpath(str(sandbox / "main.py"))


def test_resolves_dot(sandbox: Path):
    target, error = resolve_path(str(sandbox), ".")
    assert error is None
    assert target is not None
    assert os.path.normpath(target) == os.path.normpath(str(sandbox))


def test_rejects_parent_traversal(sandbox: Path):
    target, error = resolve_path(str(sandbox), "../escape.txt")
    assert target is None
    assert error is not None
    assert "outside the permitted working directory" in error


def test_rejects_absolute_path_outside_sandbox(sandbox: Path, tmp_path: Path):
    outside = str(tmp_path.parent.resolve())
    target, error = resolve_path(str(sandbox), outside)
    assert target is None
    assert error is not None


def test_accepts_nested_paths(sandbox: Path):
    target, error = resolve_path(str(sandbox), "pkg/util.py")
    assert error is None
    assert target is not None
    assert target.endswith(os.path.join("pkg", "util.py"))
