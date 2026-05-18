# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/manage_error_budget.py | §
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


import os
import argparse
import json as json_mod
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_EB_PATH = _REPO_ROOT / "scripts" / "governance" / "meta" / "error_budget_state.yaml"
_KILL_SWITCH_PATH = _REPO_ROOT / "scripts" / "governance" / "meta" / "kill_switch_state.yaml"

# 从 thresholds.yaml 读取阈值
_THRESHOLDS_PATH = _REPO_ROOT / "scripts" / "governance" / "_shared" / "thresholds.yaml"

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


def _load_thresholds() -> dict:
    """_load_thresholds implementation."""
    if not _THRESHOLDS_PATH.exists():
        return {}
    with open(_THRESHOLDS_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _load_eb() -> dict:
    """_load_eb implementation."""
    if not _EB_PATH.exists():
        return _init_eb()
    with open(_EB_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return _ensure_window(data)


def _save_eb(data: dict) -> None:
    """_save_eb implementation."""
    _EB_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = f"{_EB_PATH}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    
        os.replace(tmp_path, _EB_PATH)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
def _init_eb() -> dict:
    """_init_eb implementation."""
    t = _load_thresholds()
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

    t = _load_thresholds()
    eb = t.get("error_budget", {}).get("burn_rate", {})
    critical_th = eb.get("critical_1h_percent", 0.02) * 100

    data["burn_rate"] = {
        "last_1h_percent": round(h1_consumed, 4),
        "last_6h_percent": round(h6_consumed, 4),
        "critical_alert": h1_consumed > critical_th,
        "warning_alert": h6_consumed > 5.0,
    }
    return data


def _activate_feature_freeze(data: dict, reason: str) -> dict:
    """_activate_feature_freeze implementation."""
    t = _load_thresholds()
    freeze_hours = t.get("error_budget", {}).get("freeze_auto_lift_after_hours", 72)
    now = datetime.now(UTC)

    data["feature_freeze"] = {
        "active": True,
        "activated_at": now.isoformat(),
        "reason": reason,
        "auto_lift_at": (now + timedelta(hours=freeze_hours)).isoformat(),
    }

    ks_data = {"scripts": {}, "global_freeze": True, "freeze_reason": reason, "freeze_set_at": now.isoformat()}
    _KILL_SWITCH_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = f"{_KILL_SWITCH_PATH}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, encoding="utf-8") as f:
            yaml.dump(ks_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
        os.replace(tmp_path, _KILL_SWITCH_PATH)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    return data


def record_consumption(consumption_type: str, percent: float, detail: str = "") -> dict:
    """record_consumption implementation."""
    data = _load_eb()
    now = datetime.now(UTC)

    data["budget"]["accuracy_consumed_percent"] += percent
    data["budget"]["accuracy_consumed_percent"] = round(data["budget"]["accuracy_consumed_percent"], 4)
    data["budget"]["accuracy_remaining_percent"] = round(
        5.0 - data["budget"]["accuracy_consumed_percent"], 4
    )

    log = data.setdefault("consumption_log", [])
    log.append({
        "timestamp": now.isoformat(),
        "event": consumption_type,
        "consumed_percent": percent,
        "detail": detail,
        "source": "run_all.py",
    })
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
                    tmp_path = f"{_KILL_SWITCH_PATH}.{os.getpid()}.tmp"
                    try:
                        with open(tmp_path, encoding="utf-8") as f:
                            yaml.dump(ks_data, f, allow_unicode=True, default_flow_style=False)
                        os.replace(tmp_path, _KILL_SWITCH_PATH)
                    except PermissionError:
                        try:
                            os.remove(tmp_path)
                        except OSError:
                            pass
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
        print(f"\n[ERROR-BUDGET] 当前状态", file=sys.stderr)
        print(f"  可用性: {b['remaining_minutes']}/{b['total_minutes']} min ({b['remaining_percent']:.1f}%)", file=sys.stderr)
        print(f"  准确率: {b['accuracy_remaining_percent']:.2f}% 剩余", file=sys.stderr)
        print(f"  Burn Rate 1h: {br['last_1h_percent']:.2f}% {'🔴' if br['critical_alert'] else '🟢'}", file=sys.stderr)
        print(f"  Feature Freeze: {'🔴 ACTIVE' if ff['active'] else '🟢 INACTIVE'}", file=sys.stderr)
        if ff['active']:
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
