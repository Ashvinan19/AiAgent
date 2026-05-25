import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def sandbox(tmp_path: Path) -> Path:
    """Create a small project tree to act as a working directory."""
    (tmp_path / "pkg").mkdir()
    (tmp_path / "main.py").write_text(
        "def greet(name):\n    return f'hello {name}'\n\nprint(greet('world'))\n",
        encoding="utf-8",
    )
    (tmp_path / "pkg" / "util.py").write_text(
        "VALUE = 42\n\ndef double(x):\n    return x * 2\n",
        encoding="utf-8",
    )
    (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("plain text file\n", encoding="utf-8")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "ignored.pyc").write_bytes(b"\x00\x01")
    return tmp_path


@pytest.fixture
def outside_path(tmp_path: Path) -> str:
    """Return a path outside the sandbox for traversal tests."""
    outside = tmp_path.parent / "outside_secret.txt"
    outside.write_text("secret", encoding="utf-8")
    return str(outside)
