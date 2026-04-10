# -*- coding: utf-8 -*-
r"""兼容入口：实现位于 scripts/governance/scan_index_health.py。"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parent / "governance" / "scan_index_health.py"),
        run_name="__main__",
    )
