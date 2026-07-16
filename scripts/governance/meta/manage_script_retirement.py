# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/manage_script_retirement.py | §
# [MODULE] scripts.governance.meta.manage_script_retirement
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
"""
manage_script_retirement.py — 脚本退役/废弃生命周期管理



对标 B52（脚本退役流程）。

提供脚本从 ACTIVE → DEPRECATED（过渡期30天，still运行但告警）
→ RETIRED（正式退役，不再运行）的完整流程。

与 run_all.py 联动：deprecated 脚本 → 输出警告后仍执行；retired 脚本 → 跳过。

Usage:
    python scripts/governance/meta/manage_script_retirement.py --list
    python scripts/governance/meta/manage_script_retirement.py --deprecate d7_code/old_check.py --reason "被validate_test_coverage替代"
    python scripts/governance/meta/manage_script_retirement.py --retire d7_code/old_check.py
    python scripts/governance/meta/manage_script_retirement.py --unretire d7_code/old_check.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: ⚠ __manifest__ 缺失——请添加元数据块
dimensions: []
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
# 原 parents[2] 实为 scripts 目录而非 repo root, 变量名误导且路径计算有 bug
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
_STATE_PATH = _REPO_ROOT / "config" / "runtime" / "script_retirement_state.yaml"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _load() -> dict:
    """_load implementation."""
    if not _STATE_PATH.exists():
        return {"scripts": {}}
    with open(_STATE_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {"scripts": {}}


def _save(data: dict) -> None:
    """_save implementation."""
    _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_safe(_STATE_PATH, yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False))


def get_retirement_status(script_name: str) -> str:
    """get_retirement_status implementation."""
    data = _load()
    info = data.get("scripts", {}).get(script_name, {})
    return info.get("status", "active")


def deprecate_script(script_name: str, reason: str, replaced_by: str = "") -> dict:
    """deprecate_script implementation."""
    data = _load()
    now = datetime.now(UTC)
    data.setdefault("scripts", {})[script_name] = {
        "status": "deprecated",
        "deprecated_at": now.isoformat(),
        "sunset_at": (now + timedelta(days=30)).isoformat(),
        "replaced_by": replaced_by,
        "reason": reason,
    }
    _save(data)
    return {"script": script_name, "status": "deprecated", "sunset_at": "30 days"}


def retire_script(script_name: str) -> dict:
    """retire_script implementation."""
    data = _load()
    scripts = data.setdefault("scripts", {})
    if script_name not in scripts:
        scripts[script_name] = {}
    scripts[script_name]["status"] = "retired"
    scripts[script_name]["retired_at"] = datetime.now(UTC).isoformat()
    _save(data)
    return {"script": script_name, "status": "retired"}


def unretire_script(script_name: str) -> dict:
    """unretire_script implementation."""
    data = _load()
    data.setdefault("scripts", {}).pop(script_name, None)
    _save(data)
    return {"script": script_name, "status": "active"}


def list_retired() -> None:
    """list_retired implementation."""
    data = _load()
    scripts = data.get("scripts", {})
    if not scripts:
        print("无退役/废弃脚本", file=sys.stderr)
        return
    for name, info in scripts.items():
        status = info.get("status", "?")
        icon = {"deprecated": "🟡", "retired": "⚫"}.get(status, "❓")
        print(f"  {icon} [{status}] {name}", file=sys.stderr)
        print(f"     {info.get('reason', '未说明')}", file=sys.stderr)
        if info.get("replaced_by"):
            print(f"     替代: {info['replaced_by']}", file=sys.stderr)


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="脚本退役/废弃管理")
    parser.add_argument("--list", action="store_true", help="列出退役/废弃脚本")
    parser.add_argument("--deprecate", type=str, help="废弃脚本（30天过渡期后退役）")
    parser.add_argument("--retire", type=str, help="正式退役脚本")
    parser.add_argument("--unretire", type=str, help="恢复脚本")
    parser.add_argument("--reason", type=str, default="", help="原因")
    parser.add_argument("--replaced-by", type=str, default="", help="替代脚本")
    args = parser.parse_args()

    if args.list:
        list_retired()
    elif args.deprecate:
        deprecate_script(args.deprecate, args.reason, args.replaced_by)
        print(f"[RETIREMENT] 🟡 废弃: {args.deprecate} (30天后退役)", file=sys.stderr)
    elif args.retire:
        retire_script(args.retire)
        print(f"[RETIREMENT] ⚫ 退役: {args.retire}", file=sys.stderr)
    elif args.unretire:
        unretire_script(args.unretire)
        print(f"[RETIREMENT] ✅ 恢复: {args.unretire}", file=sys.stderr)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
