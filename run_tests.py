#!/usr/bin/env python3
"""
รัน unit tests แบบ output สวย (pytest + pytest-sugar)
"""
from __future__ import annotations

import subprocess
import sys


def _enable_windows_ansi() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass


def main() -> int:
    _enable_windows_ansi()

    c, b, r = "\033[96m", "\033[1m", "\033[0m"
    def _line(msg: str) -> None:
        print(msg, flush=True)

    _line("")
    _line(f"{c}{b}  +==================================================+{r}")
    _line(f"{c}{b}  |     Guitar Tab Generator - Test Suite          |{r}")
    _line(f"{c}{b}  +==================================================+{r}")
    _line("")

    try:
        import pytest  # noqa: F401
    except ImportError:
        print("  ยังไม่มี pytest — รัน: pip install -r requirements-dev.txt")
        print()
        return 1

    cmd = [sys.executable, "-m", "pytest", "tests"]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
