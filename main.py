#!/usr/bin/env python3
"""CLI wrapper for the src layout."""

from __future__ import annotations

import sys
from pathlib import Path


def _ensure_src_on_path() -> None:
    root = Path(__file__).resolve().parent
    src_path = root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def main() -> int:
    _ensure_src_on_path()
    from deepresearcher.main import main as run_main

    return run_main()


if __name__ == "__main__":
    raise SystemExit(main())
