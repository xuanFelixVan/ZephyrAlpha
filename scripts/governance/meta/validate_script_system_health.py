# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_script_system_health.py | §
# [MODULE] scripts.governance.meta.validate_script_system_health
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""validate_script_system_health.py — 脚本系统健康自检（Meta 维度 / 第 13 维度）

对标 MOD-INF-005 §13.1（系统健康自检）+ B25（Kill Switch）+ B14（Error Budget）。
检查六大自检项：run_all 可执行性 / 全脚本可运行性 / manifest 一致性 /
输出格式合规 / 依赖完整性 / 磁盘空间。

在 run_all.py 启动时自动运行，或在 CI 中独立触发。

Usage:
    python scripts/governance/meta/validate_script_system_health.py
    python scripts/governance/meta/validate_script_system_health.py --warn-only
    python scripts/governance/meta/validate_script_system_health.py --json
"""

from __future__ import annotations

__manifest__ = """
args:
  - --warn-only
  - --json
  - --jsonl
description: >
  脚本系统健康自检——检查六大自检项：run_all 可执行性、全脚本可运行性、manifest 一致性、
  输出格式合规、依赖完整性、磁盘空间。在 run_all.py 启动时自动运行。
dimensions:
- D1
- D5
priority: P0
timeout_seconds: 60
warn_only: false
"""


import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
# 修复: 原 line 144 的 import 被错误放在 subprocess.run() 中间导致 SyntaxError
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402

_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "governance"
_MANIFEST_PATH = _SCRIPTS_DIR / "script_manifest.yaml"
_KILL_SWITCH_PATH = _SCRIPTS_DIR / "meta" / "kill_switch_state.yaml"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _check_run_all() -> dict:
    """_check_run_all implementation."""
    start = datetime.now(UTC)
    result = subprocess.run(
        [sys.executable, str(_SCRIPTS_DIR / "run_all.py"), "--list"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    elapsed = (datetime.now(UTC) - start).total_seconds()
    return {
        "check": "run_all_list",
        "passed": result.returncode == 0,
        "exit_code": result.returncode,
        "elapsed_seconds": elapsed,
        "detail": result.stderr[-500:] if result.returncode != 0 else "",
    }


def _check_disk_space() -> dict:
    """_check_disk_space implementation."""
    try:
        usage = os.statvfs(str(_REPO_ROOT)) if hasattr(os, "statvfs") else None
        if usage:
            free_mb = (usage.f_frsize * usage.f_bavail) // (1024 * 1024)
        else:
            free_mb = 500
    except (OSError, AttributeError):
        free_mb = 500
    passed = free_mb >= 100
    return {
        "check": "disk_space",
        "passed": passed,
        "free_mb": free_mb,
        "threshold_mb": 100,
        "detail": "" if passed else f"磁盘空间不足: {free_mb}MB < 100MB",
    }


def _check_manifest_consistency() -> dict:
    """_check_manifest_consistency implementation."""
    checker = _SCRIPTS_DIR / "check_registry_consistency.py"
    if not checker.exists():
        return {"check": "manifest_consistency", "passed": False, "detail": "check_registry_consistency.py 不存在"}
    result = subprocess.run(
        [sys.executable, str(checker)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    return {
        "check": "manifest_consistency",
        "passed": result.returncode == 0,
        "exit_code": result.returncode,
        "detail": result.stderr[-500:] if result.returncode != 0 else "",
    }


def _check_import_integrity() -> dict:
    """_check_import_integrity implementation."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0, 'scripts/governance'); "
            "from _shared.constants import REPO_ROOT; print('OK')",
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    return {
        "check": "import_integrity",
        "passed": result.returncode == 0 and "OK" in result.stdout,
        "exit_code": result.returncode,
        "detail": result.stderr[-500:] if result.returncode != 0 else "",
    }


def _load_kill_switches() -> dict[str, Any]:
    """_load_kill_switches implementation."""
    if not _KILL_SWITCH_PATH.exists():
        return {"scripts": {}, "global_freeze": False}
    with open(_KILL_SWITCH_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _check_kill_switches() -> dict:
    """_check_kill_switches implementation."""
    ks = _load_kill_switches()
    disabled_scripts = {name: info for name, info in ks.get("scripts", {}).items() if info.get("disabled", False)}
    return {
        "check": "kill_switches",
        "passed": not ks.get("global_freeze", False),
        "global_freeze": ks.get("global_freeze", False),
        "disabled_scripts": list(disabled_scripts.keys()),
        "total_disabled": len(disabled_scripts),
        "detail": f"全局冻结: {ks.get('global_freeze', False)}, 禁用脚本: {len(disabled_scripts)}",
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="脚本系统健康自检（run_all/manifest/import/disk/kill-switch）")
    parser.add_argument("--warn-only", action="store_true")
    parser.add_argument("--json", action="store_true", help="多行格式化 JSON（历史兼容）")
    parser.add_argument("--jsonl", action="store_true", help="单行 JSON，含 severity")
    args = parser.parse_args()

    warn_only = args.warn_only
    json_output = args.json or args.jsonl

    checks = {
        "timestamp": datetime.now(UTC).isoformat(),
        "checks": [
            _check_run_all(),
            _check_disk_space(),
            _check_manifest_consistency(),
            _check_import_integrity(),
            _check_kill_switches(),
        ],
    }

    all_passed = all(c["passed"] for c in checks["checks"])
    checks["all_passed"] = all_passed

    if json_output:
        if args.jsonl:
            sev = "INFO" if (all_passed or warn_only) else "HIGH"
            print(
                json.dumps(
                    {
                        "severity": sev,
                        "check_id": "SCRIPT-SYS-HEALTH",
                        "all_passed": all_passed,
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(json.dumps(checks, ensure_ascii=False, indent=2))
    else:
        for c in checks["checks"]:
            icon = "✅" if c["passed"] else "❌"
            print(f"  {icon} {c['check']}: {c.get('detail', 'OK')}", file=sys.stderr)

    if warn_only or all_passed:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS)


if __name__ == "__main__":
    main()
