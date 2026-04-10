# -*- coding: utf-8 -*-
r"""兼容入口：实现位于 scripts/governance/generate_01_blueprints_index.py。"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parent / "governance" / "generate_01_blueprints_index.py"),
        run_name="__main__",
    )
