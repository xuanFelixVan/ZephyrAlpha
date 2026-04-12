# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# -*- coding: utf-8 -*-
r"""兼容入口：实现位于 scripts/governance/verify_manifest_paths_strict.py。"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(
        str(Path(__file__).resolve().parent / "governance" / "verify_manifest_paths_strict.py"),
        run_name="__main__",
    )
