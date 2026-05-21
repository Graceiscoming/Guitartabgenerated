"""
Pytest hooks — ปิด log รบกวนระหว่างรัน test
"""
import logging

import pytest

_QUIET_LOGGERS = (
    "API_MAIN",
    "GUITAR_LOGIC",
    "LEARNING",
    "httpx",
    "httpcore",
    "asyncio",
    "uvicorn",
    "urllib3",
)


@pytest.fixture(scope="session", autouse=True)
def quiet_logs():
    logging.basicConfig(level=logging.WARNING, force=True)
    for name in _QUIET_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
    yield


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """สรุปผลท้ายรัน — แสดงเมื่อไม่มี pytest-sugar"""
    if config.pluginmanager.hasplugin("sugar"):
        return

    stats = terminalreporter.stats
    passed = len(stats.get("passed", []))
    failed = len(stats.get("failed", []))
    errors = len(stats.get("error", []))
    skipped = len(stats.get("skipped", []))
    total = passed + failed + errors + skipped

    green, red, yellow, reset, bold = "\033[92m", "\033[91m", "\033[93m", "\033[0m", "\033[1m"
    print(f"\n{bold}{'-' * 52}{reset}")
    print(f"  {bold}Summary{reset}  total {total} tests")
    print(f"  {green}[PASS]{reset}  {passed}")
    if failed:
        print(f"  {red}[FAIL]{reset}  {failed}")
    if errors:
        print(f"  {red}[ERR ]{reset}  {errors}")
    if skipped:
        print(f"  {yellow}[SKIP]{reset} {skipped}")
    if exitstatus == 0:
        print(f"\n  {green}{bold}All tests passed{reset}\n")
    else:
        print(f"\n  {red}{bold}Some tests failed{reset}\n")
