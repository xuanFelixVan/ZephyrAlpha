# [BLUEPRINT] MOD-INF-005 | scripts/governance/check_registry_consistency.py | §
"""Module docstring — see module-level docstring for details."""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
"""薄封装：保持历史路径 `scripts/governance/check_registry_consistency.py` 可用。

实现位于 `d3_metadata/check_registry_consistency.py`。"""

__manifest__ = {
    "args": [],
    "description": "兼容入口：转发执行 d3_metadata/check_registry_consistency.py",
    "dimensions": ["D3", "D5", "D11"],
    "priority": "P1",
    "timeout_seconds": 60,
    "warn_only": False,
}

import runpy
from pathlib import Path

_SHIM = Path(__file__).resolve().parent / "d3_metadata" / "check_registry_consistency.py"

if __name__ == "__main__":
    runpy.run_path(str(_SHIM), run_name="__main__")
