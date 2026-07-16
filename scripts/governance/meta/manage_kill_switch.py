# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/manage_kill_switch.py | §
# [MODULE] scripts.governance.meta.manage_kill_switch
# [DOMAIN] D_AUTONOMY_PERM
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
"""manage_kill_switch.py — Kill Switch 管理工具

对标 B25（Kill Switch）+ ITIL 4 Emergency Change Management。
提供 CLI 命令禁用/启用脚本、查看状态、设置全局冻结。

Usage:
    python scripts/governance/meta/manage_kill_switch.py --list
    python scripts/governance/meta/manage_kill_switch.py --disable d7_code/validate_test_coverage.py --reason "误报率过高"
    python scripts/governance/meta/manage_kill_switch.py --enable d7_code/validate_test_coverage.py
    python scripts/governance/meta/manage_kill_switch.py --global-freeze --reason "Error Budget 耗尽"
    python scripts/governance/meta/manage_kill_switch.py --global-thaw
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  Kill Switch 管理工具——提供 CLI 命令禁用/启用脚本、查看状态、设置全局冻结。
dimensions:
- D1
- D5
priority: P0
timeout_seconds: 15
warn_only: false
"""


import argparse
import os
import sys
from datetime import UTC, datetime
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
_KILL_SWITCH_PATH = _REPO_ROOT / "config" / "runtime" / "kill_switch_state.yaml"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _load() -> dict:
    """_load implementation."""
    if not _KILL_SWITCH_PATH.exists():
        return {"scripts": {}, "global_freeze": False, "freeze_reason": "", "freeze_set_at": ""}
    with open(_KILL_SWITCH_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _save(data: dict) -> None:
    """_save implementation."""
    _KILL_SWITCH_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_safe(_KILL_SWITCH_PATH, yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False))


def cmd_list() -> None:
    """cmd_list implementation."""
    data = _load()
    if data.get("global_freeze"):
        print(f"\n🔴 全局冻结已激活: {data.get('freeze_reason', '无说明')}", file=sys.stderr)
        print(f"   冻结时间: {data.get('freeze_set_at', '未知')}", file=sys.stderr)
    else:
        print("\n🟢 全局冻结未激活", file=sys.stderr)

    scripts = data.get("scripts", {})
    if not scripts:
        print("   无禁用脚本", file=sys.stderr)
        return

    print(f"\n禁用脚本 ({len(scripts)} 个):", file=sys.stderr)
    for name, info in scripts.items():
        if info.get("disabled"):
            print(f"  ❌ {name}", file=sys.stderr)
            print(f"     原因: {info.get('reason', '未说明')}", file=sys.stderr)
            print(f"     时间: {info.get('disabled_at', '未知')}", file=sys.stderr)


def cmd_disable(script_name: str, reason: str) -> None:
    """cmd_disable implementation."""
    data = _load()
    scripts = data.setdefault("scripts", {})
    scripts[script_name] = {
        "disabled": True,
        "reason": reason,
        "disabled_at": datetime.now(UTC).isoformat(),
        "disabled_by": "owner",
    }
    _save(data)
    print(f"[KILL-SWITCH] ❌ 已禁用: {script_name}", file=sys.stderr)
    print(f"  原因: {reason}", file=sys.stderr)


def cmd_enable(script_name: str) -> None:
    """cmd_enable implementation."""
    data = _load()
    if script_name in data.get("scripts", {}):
        data["scripts"][script_name]["disabled"] = False
        data["scripts"][script_name]["enabled_at"] = datetime.now(UTC).isoformat()
    _save(data)
    print(f"[KILL-SWITCH] ✅ 已启用: {script_name}", file=sys.stderr)


def cmd_global_freeze(reason: str) -> None:
    """cmd_global_freeze implementation."""
    data = _load()
    data["global_freeze"] = True
    data["freeze_reason"] = reason
    data["freeze_set_at"] = datetime.now(UTC).isoformat()
    _save(data)
    print("[KILL-SWITCH] 🔴 全局冻结已激活", file=sys.stderr)
    print(f"  原因: {reason}", file=sys.stderr)
    print("  所有新脚本开发暂停——只允许修复现有脚本的错误", file=sys.stderr)


def cmd_global_thaw() -> None:
    """cmd_global_thaw implementation."""
    data = _load()
    data["global_freeze"] = False
    data["freeze_reason"] = ""
    data["freeze_set_at"] = ""
    _save(data)
    print("[KILL-SWITCH] 🟢 全局冻结已解除", file=sys.stderr)


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="脚本 Kill Switch 管理工具")
    parser.add_argument("--list", action="store_true", help="列出所有禁用脚本")
    parser.add_argument("--disable", type=str, help="禁用指定脚本")
    parser.add_argument("--enable", type=str, help="启用指定脚本")
    parser.add_argument("--reason", type=str, default="人工判定", help="禁用/冻结原因")
    parser.add_argument("--global-freeze", action="store_true", help="激活全局冻结")
    parser.add_argument("--global-thaw", action="store_true", help="解除全局冻结")
    args = parser.parse_args()

    if args.list:
        cmd_list()
    elif args.disable:
        cmd_disable(args.disable, args.reason)
    elif args.enable:
        cmd_enable(args.enable)
    elif args.global_freeze:
        cmd_global_freeze(args.reason)
    elif args.global_thaw:
        cmd_global_thaw()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
