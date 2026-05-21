#!/usr/bin/env python3
"""
Static Testing Runner - Runs Flake8, Mypy, and Bandit with colored output summaries.
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


def run_check(name: str, cmd: list[str]) -> bool:
    c_blue, c_green, c_red, c_bold, c_reset = "\033[94m", "\033[92m", "\033[91m", "\033[1m", "\033[0m"
    print(f"{c_blue}{c_bold}[*] Running {name}...{c_reset}", flush=True)
    print(f"Command: {' '.join(cmd)}", flush=True)
    print("-" * 60, flush=True)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            print(f"{c_green}{c_bold}[+] {name} PASSED successfully!{c_reset}\n")
            return True
        else:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            print(f"{c_red}{c_bold}[-] {name} FAILED! Issues were detected.{c_reset}\n")
            return False
    except FileNotFoundError:
        print(f"{c_red}{c_bold}[-] Error: {cmd[0]} is not installed or not in PATH.{c_reset}\n")
        return False


def main() -> int:
    _enable_windows_ansi()

    c_cyan, c_bold, c_reset = "\033[96m", "\033[1m", "\033[0m"
    print("")
    print(f"{c_cyan}{c_bold}  +==================================================+{c_reset}")
    print(f"{c_cyan}{c_bold}  |     Guitar Tab Generator - Static Test Suite     |{c_reset}")
    print(f"{c_cyan}{c_bold}  +==================================================+{c_reset}")
    print("")

    # Define the static checks to run
    # 1. Flake8 (Linting & Style Checks)
    flake8_cmd = [sys.executable, "-m", "flake8", "app.py", "core", "tests", "--max-line-length=120"]
    
    # 2. Mypy (Static Type Safety Check)
    mypy_cmd = [sys.executable, "-m", "mypy", "app.py", "core", "--ignore-missing-imports"]
    
    # 3. Bandit (Security Scanning)
    bandit_cmd = [sys.executable, "-m", "bandit", "-r", "app.py", "core", "-ll"]

    # Run the checks
    checks = [
        ("Flake8 (Code Style & Linting)", flake8_cmd),
        ("Mypy (Type Safety Check)", mypy_cmd),
        ("Bandit (Security Vulnerability Scan)", bandit_cmd),
    ]

    all_passed = True
    for name, cmd in checks:
        passed = run_check(name, cmd)
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print(f"\033[92m\033[1m[SUCCESS] All static tests passed successfully! Code is clean and secure! [OK]\033[0m")
        return 0
    else:
        print(f"\033[91m\033[1m[FAILURE] Static testing detected issues. Please review and fix them. [FAIL]\033[0m")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
