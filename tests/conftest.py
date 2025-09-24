# tests/conftest.py
import builtins

import pytest

import rsync_time_machine


@pytest.fixture(autouse=True)
def printify_logs(monkeypatch) -> None:
    """Replace module-level logging helper functions with print() during tests.

    This makes assertions that use capsys (or simple text capture) reliable, without
    changing library code.
    """

    # Simple print wrapper to keep behaviour similar (no colour/formatting)
    def _p(msg: str) -> None:
        # ensure str conversion and flush so pytest capture sees it
        builtins.print(str(msg), flush=True)

    for name in ("log_info", "log_warn", "log_error", "log_debug", "log_crtical"):
        if hasattr(rsync_time_machine, name):
            monkeypatch.setattr(rsync_time_machine, name, _p)
