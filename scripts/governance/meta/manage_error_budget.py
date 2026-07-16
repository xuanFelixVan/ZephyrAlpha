# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/manage_error_budget.py | §
# [MODULE] scripts.governance.meta.manage_error_budget
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
"""manage_error_budget.py — Error Budget + Burn Rate 管理引擎

对标 B14（Error Budget + Burn Rate）+ Google SRE Ch.5-6。
管理可用性 Error Budget 和准确率 Error Budget 的消耗/监控/冻结。
每次 run_all.py 扫描后调用 --record 记录消耗。
Burn Rate 超过阈值 → Alert。Error Budget 耗尽 → Feature Freeze。

Usage:
    python scripts/governance/meta/manage_error_budget.py --status
    python scripts/governance/meta/manage_error_budget.py --record --type false_positive --percent 0.1 --detail "validate_frontmatter 误报3条"
    python scripts/governance/meta/manage_error_budget.py --record --type scan_failure --percent 2.0 --detail "run_all.py D7 扫描异常"
    python scripts/governance/meta/manage_error_budget.py --reset-window
    python scripts/governance/meta/manage_error_budget.py --check-thresholds
    python scripts/governance/meta/manage_error_budget.py --json
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  Error Budget + Burn Rate 管理引擎——管理可用性 Error Budget 和准确率 Error Budget 的消耗/监控/冻结，
  Burn Rate 超过阈值 → Alert，Error Budget 耗尽 → Feature Freeze。
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""


import argparse
import json as json_mod
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
from _shared.thresholds import get_thresholds_safe  # noqa: E402  治本(ARCH-036 P1-4): 收敛本地 _load_thresholds 重复实现→共享 graceful 变体

_EB_PATH = _REPO_ROOT / "config" / "runtime" / "error_budget_state.yaml"
_KILL_SWITCH_PATH = _REPO_ROOT / "config" / "runtime" / "kill_switch_state.yaml"

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _load_eb() -> dict:
    """_load_eb implementation."""
    if not _EB_PATH.exists():
        return _init_eb()
    with open(_EB_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return _ensure_window(data)


def _save_eb(data: dict) -> None:
    """_save_eb implementation."""
    content = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    atomic_write_safe(_EB_PATH, content)


def _init_eb() -> dict:
    """_init_eb implementation."""
    t = get_thresholds_safe()
    now = datetime.now(UTC)
    window_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(days=30)
    slo = t.get("error_budget", {}).get("availability_slo", 0.99)
    total_minutes = round(30 * 24 * 60 * (1 - slo), 1)

    return {
        "tracking_window": {
            "start": window_start.isoformat(),
            "end": window_end.isoformat(),
            "duration_days": 30,
        },
        "budget": {
            "total_minutes": total_minutes,
            "consumed_minutes": 0.0,
            "remaining_minutes": total_minutes,
            "remaining_percent": 100.0,
            "accuracy_total_percent": 5.0,
            "accuracy_consumed_percent": 0.0,
            "accuracy_remaining_percent": 5.0,
        },
        "burn_rate": {
            "last_1h_percent": 0.0,
            "last_6h_percent": 0.0,
            "critical_alert": False,
            "warning_alert": False,
        },
        "feature_freeze": {
            "active": False,
            "activated_at": "",
            "reason": "",
            "auto_lift_at": "",
        },
        "consumption_log": [],
    }


def _ensure_window(data: dict) -> dict:
    """_ensure_window implementation."""
    now = datetime.now(UTC)
    end_str = data.get("tracking_window", {}).get("end", "")
    if end_str:
        try:
            if now > datetime.fromisoformat(end_str):
                return _init_eb()
        except ValueError:
            pass
    return data


def _update_burn_rate(data: dict) -> dict:
    """_update_burn_rate implementation."""
    now = datetime.now(UTC)
    log = data.get("consumption_log", [])
    one_hour_ago = now - timedelta(hours=1)
    six_hours_ago = now - timedelta(hours=6)

    h1_consumed = 0.0
    h6_consumed = 0.0
    for entry in log:
        try:
            ts = datetime.fromisoformat(entry["timestamp"])
        except (ValueError, KeyError):
            continue
        if ts >= one_hour_ago:
            h1_consumed += entry.get("consumed_percent", 0)
        if ts >= six_hours_ago:
            h6_consumed += entry.get("consumed_percent", 0)

    t = get_thresholds_safe()
    eb = t.get("error_budget", {}).get("burn_rate", {})
    critical_th = eb.get("critical_1h_percent", 0.02) * 100
    warning_th = eb.get("warning_6h_percent", 0.05) * 100

    data["burn_rate"] = {
        "last_1h_percent": round(h1_consumed, 4),
        "last_6h_percent": round(h6_consumed, 4),
        "critical_alert": h1_consumed > critical_th,
        "warning_alert": h6_consumed > warning_th,
    }
    return data


def _activate_feature_freeze(data: dict, reason: str) -> dict:
    """_activate_feature_freeze implementation."""
    t = get_thresholds_safe()
    freeze_hours = t.get("error_budget", {}).get("freeze_auto_lift_after_hours", 72)
    now = datetime.now(UTC)

    data["feature_freeze"] = {
        "active": True,
        "activated_at": now.isoformat(),
        "reason": reason,
        "auto_lift_at": (now + timedelta(hours=freeze_hours)).isoformat(),
    }

    ks_data = {"scripts": {}, "global_freeze": True, "freeze_reason": reason, "freeze_set_at": now.isoformat()}
    content = yaml.dump(ks_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    atomic_write_safe(_KILL_SWITCH_PATH, content)
    return data


def record_consumption(consumption_type: str, percent: float, detail: str = "") -> dict:
    """record_consumption implementation."""
    data = _load_eb()
    now = datetime.now(UTC)

    data["budget"]["accuracy_consumed_percent"] += percent
    data["budget"]["accuracy_consumed_percent"] = round(data["budget"]["accuracy_consumed_percent"], 4)
    data["budget"]["accuracy_remaining_percent"] = round(5.0 - data["budget"]["accuracy_consumed_percent"], 4)

    log = data.setdefault("consumption_log", [])
    log.append(
        {
            "timestamp": now.isoformat(),
            "event": consumption_type,
            "consumed_percent": percent,
            "detail": detail,
            "source": "run_all.py",
        }
    )
    if len(log) > 1000:
        data["consumption_log"] = log[-500:]

    data = _update_burn_rate(data)

    accuracy_remaining = data["budget"]["accuracy_remaining_percent"]
    if accuracy_remaining <= 0 and not data["feature_freeze"]["active"]:
        data = _activate_feature_freeze(data, f"准确率 Error Budget 耗尽 (剩余 {accuracy_remaining}%)")

    if data["burn_rate"]["critical_alert"] and not data["feature_freeze"]["active"]:
        data = _activate_feature_freeze(data, "Burn Rate Critical Alert: 1h 消耗超过 2%")

    _save_eb(data)
    return data


def check_thresholds() -> dict:
    """Check compliance and report findings."""
    data = _load_eb()
    data = _update_burn_rate(data)
    _save_eb(data)

    if data["feature_freeze"]["active"]:
        freeze_at = data["feature_freeze"]["auto_lift_at"]
        if freeze_at:
            try:
                if datetime.now(UTC) > datetime.fromisoformat(freeze_at):
                    data["feature_freeze"]["active"] = False
                    ks_data = {"scripts": {}, "global_freeze": False}
                    content = yaml.dump(ks_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
                    atomic_write_safe(_KILL_SWITCH_PATH, content)
                    data["feature_freeze"]["auto_lift_at"] = ""
                    _save_eb(data)
                    return {"status": "auto_lifted", "freeze": False}
            except ValueError:
                pass

    return {
        "status": "ok" if not data["feature_freeze"]["active"] else "frozen",
        "accuracy_remaining_percent": data["budget"]["accuracy_remaining_percent"],
        "burn_rate_critical": data["burn_rate"]["critical_alert"],
        "burn_rate_warning": data["burn_rate"]["warning_alert"],
        "feature_freeze_active": data["feature_freeze"]["active"],
    }


def status(json_output: bool = False) -> dict:
    """status implementation."""
    data = _ensure_window(_load_eb())
    if json_output:
        print(json_mod.dumps(data, ensure_ascii=False, indent=2))
    else:
        b = data["budget"]
        br = data["burn_rate"]
        ff = data["feature_freeze"]
        print("\n[ERROR-BUDGET] 当前状态", file=sys.stderr)
        print(
            f"  可用性: {b['remaining_minutes']}/{b['total_minutes']} min ({b['remaining_percent']:.1f}%)",
            file=sys.stderr,
        )
        print(f"  准确率: {b['accuracy_remaining_percent']:.2f}% 剩余", file=sys.stderr)
        print(f"  Burn Rate 1h: {br['last_1h_percent']:.2f}% {'🔴' if br['critical_alert'] else '🟢'}", file=sys.stderr)
        print(f"  Feature Freeze: {'🔴 ACTIVE' if ff['active'] else '🟢 INACTIVE'}", file=sys.stderr)
        if ff["active"]:
            print(f"    原因: {ff['reason']}", file=sys.stderr)
            print(f"    自动解冻: {ff.get('auto_lift_at', '手动')}", file=sys.stderr)
    return data


def reset_window() -> dict:
    """reset_window implementation."""
    data = _init_eb()
    _save_eb(data)
    return data


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Error Budget 管理引擎")
    parser.add_argument("--status", action="store_true", help="查看当前 Error Budget 状态")
    parser.add_argument("--record", action="store_true", help="记录一次消耗事件")
    parser.add_argument("--type", type=str, default="unknown", help="消耗类型")
    parser.add_argument("--percent", type=float, default=0.0, help="消耗百分比")
    parser.add_argument("--detail", type=str, default="", help="消耗详情")
    parser.add_argument("--check-thresholds", action="store_true", help="检查阈值并触发相应动作")
    parser.add_argument("--reset-window", action="store_true", help="重置 Error Budget 窗口")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    if args.status:
        status(args.json)
    elif args.record:
        result = record_consumption(args.type, args.percent, args.detail)
        print(f"[ERROR-BUDGET] 消耗记录: {args.type} ({args.percent}%)", file=sys.stderr)
        if result["feature_freeze"]["active"]:
            print(f"  🔴 Feature Freeze 已激活！{result['feature_freeze']['reason']}", file=sys.stderr)
    elif args.check_thresholds:
        result = check_thresholds()
        print(f"[ERROR-BUDGET] 阈值检查: {result}", file=sys.stderr)
    elif args.reset_window:
        result = reset_window()
        print("[ERROR-BUDGET] 窗口已重置", file=sys.stderr)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
