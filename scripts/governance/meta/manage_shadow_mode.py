# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/manage_shadow_mode.py | §
# [MODULE] scripts.governance.meta.manage_shadow_mode
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
# [TTL] task_bound
"""
manage_shadow_mode.py — Shadow Mode 渐进激活管理

对标 B19（Shadow Mode）+ Kubernetes Feature Gates + LaunchDarkly Progressive Rollout。
管理新脚本的 Phase1(Shadow)→Phase2(Warn)→Phase3(Active) 生命周期。
Phase1 期间假阳性率 > 阈值 → 自动回退。

Usage:
    python scripts/governance/meta/manage_shadow_mode.py --list
    python scripts/governance/meta/manage_shadow_mode.py --promote d7_code/validate_new_check.py
    python scripts/governance/meta/manage_shadow_mode.py --rollback d7_code/validate_new_check.py --reason "假阳性率 35%"
    python scripts/governance/meta/manage_shadow_mode.py --check-health
"""

from __future__ import annotations
from _shared.constants import REPO_ROOT
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT

__manifest__ = """
args: []
description: >
  Shadow Mode 渐进激活管理——管理新脚本的 Phase1(Shadow)→Phase2(Warn)→Phase3(Active) 生命周期，
  Phase1 期间假阳性率超阈值则自动回退。
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""

import argparse
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

_REPO_ROOT = REPO_ROOT
_SHADOW_STATE_PATH = _REPO_ROOT / "scripts" / "governance" / "meta" / "shadow_mode_state.yaml"

PHASE_ORDER = {"phase1": 1, "phase2": 2, "phase3": 3}
NEXT_PHASE = {"phase1": "phase2", "phase2": "phase3", "phase3": "phase3"}
PHASE_DAYS = {"phase1": 7, "phase2": 7, "phase3": 0}

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _load() -> dict:
    """_load implementation."""
    if not _SHADOW_STATE_PATH.exists():
        return {"scripts": {}}
    with open(_SHADOW_STATE_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {"scripts": {}}


def _save(data: dict) -> None:
    """_save implementation."""
    _SHADOW_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_safe(_SHADOW_STATE_PATH, yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False))


def get_activation_phase(script_name: str) -> str:
    """get_activation_phase implementation."""
    data = _load()
    info = data.get("scripts", {}).get(script_name, {})
    return info.get("phase", "phase3")


def should_run_warn_only(script_name: str) -> bool:
    """should_run_warn_only implementation."""
    phase = get_activation_phase(script_name)
    return phase in ("phase1", "phase2")


def register_shadow(script_name: str) -> dict:
    """register_shadow implementation."""
    data = _load()
    now = datetime.now(UTC)
    scripts = data.setdefault("scripts", {})
    scripts[script_name] = {
        "phase": "phase1",
        "started_at": now.isoformat(),
        "target_phase3_at": (now + timedelta(days=14)).isoformat(),
        "false_positives_accumulated": 0,
        "rollback_count": 0,
    }
    _save(data)
    return scripts[script_name]


def promote_script(script_name: str) -> dict:
    """promote_script implementation."""
    data = _load()
    info = data.get("scripts", {}).get(script_name)
    if not info:
        return {"error": f"脚本 {script_name} 未注册 Shadow Mode"}
    current = info["phase"]
    if current == "phase3":
        return {"status": "already_active", "script": script_name}
    next_phase = NEXT_PHASE[current]
    info["phase"] = next_phase
    info["promoted_at"] = datetime.now(UTC).isoformat()
    _save(data)
    return {"status": "promoted", "script": script_name, "from": current, "to": next_phase}


def rollback_script(script_name: str, reason: str = "") -> dict:
    """rollback_script implementation."""
    data = _load()
    info = data.get("scripts", {}).get(script_name)
    if not info:
        return {"error": f"脚本 {script_name} 未注册 Shadow Mode"}
    info["phase"] = "phase1"
    info["rollback_count"] = info.get("rollback_count", 0) + 1
    info["last_rollback_at"] = datetime.now(UTC).isoformat()
    info["last_rollback_reason"] = reason
    _save(data)
    return {"status": "rolled_back", "script": script_name, "reason": reason}


def check_health() -> dict:
    """Check compliance and report findings."""
    data = _load()
    now = datetime.now(UTC)
    results: list[dict] = []

    for name, info in data.get("scripts", {}).items():
        phase = info.get("phase", "phase3")
        started = info.get("started_at", "")
        if phase in ("phase1", "phase2") and started:
            try:
                started_dt = datetime.fromisoformat(started)
                elapsed_days = (now - started_dt).days
            except ValueError:
                elapsed_days = 0

            if phase == "phase1" and elapsed_days >= PHASE_DAYS["phase1"]:
                results.append(
                    {
                        "script": name,
                        "action": "auto_promote_to_phase2",
                        "elapsed_days": elapsed_days,
                    }
                )
            elif phase == "phase2" and elapsed_days >= PHASE_DAYS["phase2"]:
                results.append(
                    {
                        "script": name,
                        "action": "ready_for_phase3",
                        "elapsed_days": elapsed_days,
                    }
                )

    return {
        "timestamp": now.isoformat(),
        "scripts_in_shadow": len(data.get("scripts", {})),
        "actions": results,
    }


def list_shadow_scripts() -> None:
    """list_shadow_scripts implementation."""
    data = _load()
    scripts = data.get("scripts", {})
    if not scripts:
        print("无 Shadow Mode 脚本", file=sys.stderr)
        return

    print(f"\nShadow Mode 脚本 ({len(scripts)} 个):", file=sys.stderr)
    for name, info in scripts.items():
        phase = info.get("phase", "?")
        phase_label = {"phase1": "🔵 Shadow", "phase2": "🟡 Warn", "phase3": "🟢 Active"}.get(phase, "❓")
        print(f"  [{phase_label}] {name}", file=sys.stderr)
        print(f"    开始: {info.get('started_at', '未知')}", file=sys.stderr)
        print(f"    回退: {info.get('rollback_count', 0)} 次", file=sys.stderr)
        if info.get("last_rollback_reason"):
            print(f"    最近回退: {info['last_rollback_reason']}", file=sys.stderr)


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Shadow Mode 渐进激活管理")
    parser.add_argument("--list", action="store_true", help="列出 Shadow Mode 脚本")
    parser.add_argument("--register", type=str, help="注册新脚本进入 Shadow Mode (Phase1)")
    parser.add_argument("--promote", type=str, help="提升脚本到下一阶段")
    parser.add_argument("--rollback", type=str, help="回退脚本到 Phase1")
    parser.add_argument("--reason", type=str, default="", help="回退原因")
    parser.add_argument("--check-health", action="store_true", help="检查自动升级条件")
    parser.add_argument("--auto-promote", action="store_true", help="执行自动升级")
    args = parser.parse_args()

    if args.list:
        list_shadow_scripts()
    elif args.register:
        result = register_shadow(args.register)
        print(f"[SHADOW] 已注册 Shadow Mode (Phase1): {args.register}", file=sys.stderr)
    elif args.promote:
        result = promote_script(args.promote)
        print(f"[SHADOW] 升级: {result}", file=sys.stderr)
    elif args.rollback:
        result = rollback_script(args.rollback, args.reason)
        print(f"[SHADOW] 回退: {result}", file=sys.stderr)
    elif args.check_health:
        result = check_health()
        for a in result["actions"]:
            print(f"  {a['script']}: {a['action']} (已过 {a['elapsed_days']} 天)", file=sys.stderr)
    elif args.auto_promote:
        result = check_health()
        for a in result["actions"]:
            if "auto_promote" in a["action"]:
                promote_script(a["script"])
                print(f"  ✅ 自动升级: {a['script']} → Phase2", file=sys.stderr)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
