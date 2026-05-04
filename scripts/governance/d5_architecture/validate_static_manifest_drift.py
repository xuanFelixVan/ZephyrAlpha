#!/usr/bin/env python3
"""
GATE-19：静态清单漂移阻断（validate_static_manifest_drift.py）
===============================================================

__manifest__ = """
args:
- {flag: --check, type: bool, description: "仅检测漂移（pre-commit模式）"}
description: >
  运行所有生成器的 --check 模式，对比自动生成版 vs 磁盘版。
  任何不一致 → 阻断提交。对标 §6.16 静态清单自动生成铁律。
dimensions:
- D5
priority: P0
timeout_seconds: 30
warn_only: false
"""


权威依据
--------
AGENTS.md §6.16 静态清单自动生成铁律：
  任何"条目列表+计数"的文件必须由生成器产出，标注 generated_at。
  手工编辑的清单将在本门禁中被检测并阻断。

检测范围
--------
  1. script_manifest.yaml  ← generate_script_manifest.py --check
  2. gate-registry.yaml    ← generate_gate_registry.py --check（pre-commit部分）

门禁逻辑
--------
  - 每个生成器以 --check 模式运行
  - 任意生成器返回非零 → 记录差异
  - 汇总输出 → exit(1) 阻断提交

Usage:
    python validate_static_manifest_drift.py --check
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
GENERATORS_DIR = SCRIPTS_DIR / "generators"

CHECKS = [
    {
        "name": "script_manifest.yaml",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_script_manifest.py"), "--check"],
    },
    {
        "name": "gate-registry.yaml (pre-commit)",
        "cmd": [sys.executable, str(GENERATORS_DIR / "generate_gate_registry.py"), "--check"],
    },
]


def main() -> None:
    failures = []
    for check in CHECKS:
        result = subprocess.run(
            check["cmd"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(SCRIPTS_DIR.parent.parent),
        )
        if result.returncode != 0:
            msg = (result.stdout + result.stderr).strip()
            failures.append(f"FAIL [{check['name']}]: {msg}")
        else:
            print(f"PASS [{check['name']}]: {result.stdout.strip()}")

    if not failures:
        print("\nGATE-19 PASS: 所有静态清单与生成源一致，无漂移。")
        sys.exit(0)

    print(f"\nGATE-19 FAIL: {len(failures)} 个静态清单漂移:\n")
    for f in failures:
        print(f"  - {f}")
    print(
        "\n修复: 运行 cd D:\\ZephyrAlpha && python scripts/governance/generators/generate_script_manifest.py"
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
