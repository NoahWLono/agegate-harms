"""Normalize every UTF-8 repository text file to canonical Git-safe whitespace."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path

SKIP_DIRECTORIES = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
}


def candidate_files(root: Path) -> Iterable[Path]:
    """Yield regular files while avoiding repository and environment internals."""
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        if any(part in SKIP_DIRECTORIES for part in path.relative_to(root).parts):
            continue
        yield path


def normalize_text(text: str) -> str:
    """Return canonical LF text with no trailing spaces and one final newline."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "\n".join(line.rstrip(" \t") for line in text.split("\n"))
    if not normalized:
        return normalized
    return normalized.rstrip("\n") + "\n"


def inspect_file(path: Path) -> tuple[bytes, bytes, int, int]:
    """Return original bytes, normalized bytes, CR count, and bad-line count."""
    original = path.read_bytes()
    if b"\0" in original:
        raise UnicodeDecodeError("utf-8", original, 0, 1, "NUL byte")
    text = original.decode("utf-8")
    cr_count = text.count("\r")
    trailing_count = sum(1 for line in text.splitlines() if line.endswith((" ", "\t")))
    normalized = normalize_text(text).encode("utf-8")
    return original, normalized, cr_count, trailing_count


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Rewrite nonconforming UTF-8 files. Without this flag, only check them.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of scripts/.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.resolve()
    changed: list[Path] = []

    for path in candidate_files(root):
        try:
            original, normalized, cr_count, trailing_count = inspect_file(path)
        except UnicodeDecodeError:
            continue
        if original == normalized:
            continue

        relative = path.relative_to(root)
        changed.append(relative)
        details = []
        if cr_count:
            details.append(f"{cr_count} carriage return(s)")
        if trailing_count:
            details.append(f"{trailing_count} trailing-whitespace line(s)")
        if original and not original.endswith((b"\n", b"\r")):
            details.append("missing final newline")
        print(f"{relative}: {', '.join(details) or 'noncanonical text'}")

        if args.write:
            path.write_bytes(normalized)

    if not changed:
        print("Whitespace check passed: every UTF-8 repository file is canonical.")
        return 0

    if args.write:
        print(f"Normalized {len(changed)} file(s).")
        return 0

    print(
        "Whitespace check failed. Run: python scripts/normalize_whitespace.py --write",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
