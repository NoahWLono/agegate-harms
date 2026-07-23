from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_normalizer_repairs_all_utf8_files_including_lockfiles(tmp_path: Path) -> None:
    root = Path(__file__).parents[1]
    script = root / "scripts" / "normalize_whitespace.py"

    (tmp_path / "uv.lock").write_bytes(b'[[package]]\r\nname = "x"  \r\n')
    (tmp_path / "Dockerfile").write_bytes(b"FROM scratch\t\r\n")
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "notes.custom").write_bytes(b"hello   \n\n\n")
    (tmp_path / "image.bin").write_bytes(b"\x00not-text\r\n")

    fixed = subprocess.run(
        [sys.executable, str(script), "--write", "--root", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert fixed.returncode == 0, fixed.stdout + fixed.stderr

    assert (tmp_path / "uv.lock").read_bytes() == b'[[package]]\nname = "x"\n'
    assert (tmp_path / "Dockerfile").read_bytes() == b"FROM scratch\n"
    assert (tmp_path / "nested" / "notes.custom").read_bytes() == b"hello\n"
    assert (tmp_path / "image.bin").read_bytes() == b"\x00not-text\r\n"

    checked = subprocess.run(
        [sys.executable, str(script), "--root", str(tmp_path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert checked.returncode == 0, checked.stdout + checked.stderr
