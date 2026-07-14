# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/finding_state_machine.py | §
# [MODULE] scripts.governance.meta.finding_state_machine
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
finding_state_machine.py — Finding 全生命周期状态机

对标 B20（Finding 全生命周期状态机）+ ITIL 4 Incident Management + Jira SLA timers。
管理每个 Finding 从 OPEN→FIXED→VERIFIED 的完整生命周期。
包括 SLA 定时器（超时升级）、状态转换审计日志、跨 run 持久化。

Finding 状态机：
  OPEN → IN_PROGRESS → FIXED → VERIFIED
  OPEN → FALSE_POSITIVE → CLOSED
  OPEN → WONTFIX → ACCEPTED_RISK
  任意状态 → OVERDUE（定时器触发）

Usage:
    python scripts/governance/meta/finding_state_machine.py --load findings.jsonl
    python scripts/governance/meta/finding_state_machine.py --transition <finding_id> --to IN_PROGRESS
    python scripts/governance/meta/finding_state_machine.py --list OVERDUE
    python scripts/governance/meta/finding_state_machine.py --check-sla
    python scripts/governance/meta/finding_state_machine.py --stats
"""

from __future__ import annotations

from _shared.constants import EXIT_PASS, REPO_ROOT
from _shared.file_utils import atomic_write_safe  # noqa: E402  治本(ARCH-036 P1-1): 收敛本地 tmp+replace 样板→共享 SSoT
from _shared.thresholds import get as _get_threshold  # noqa: E402  治本(ARCH-036 P3-A5): SLA 阈值读 SSoT

__manifest__ = """
args: []
description: >
  Finding 全生命周期状态机——管理每个 Finding 从 OPEN→FIXED→VERIFIED 的完整生命周期，
  包括 SLA 定时器、状态转换审计日志、跨 run 持久化。
dimensions:
- D1
- D5
priority: P1
timeout_seconds: 30
warn_only: false
"""
import argparse
import hashlib
import json as json_mod
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

_REPO_ROOT = REPO_ROOT
_STATE_DB_PATH = _REPO_ROOT / "scripts" / "governance" / "meta" / "finding_state_db.json"

_src = _REPO_ROOT / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from zephyr.infrastructure.script_system.finding import LIFECYCLE_STATUS_VALUES

VALID_STATUSES = list(LIFECYCLE_STATUS_VALUES)

VALID_TRANSITIONS = {
    "OPEN": ["IN_PROGRESS", "FALSE_POSITIVE", "WONTFIX", "DEFERRED", "OVERDUE"],
    "IN_PROGRESS": ["FIXED", "WONTFIX", "OVERDUE"],
    "FIXED": ["VERIFIED", "OPEN"],
    "VERIFIED": ["OPEN"],
    "FALSE_POSITIVE": ["CLOSED", "OPEN"],
    "WONTFIX": ["ACCEPTED_RISK", "OPEN"],
    "ACCEPTED_RISK": ["OPEN"],
    "CLOSED": ["OPEN"],
    "OVERDUE": ["IN_PROGRESS", "FIXED", "WONTFIX"],
    "DEFERRED": ["OPEN", "IN_PROGRESS"],
}

# SLA 定时器：严重度 → 最大修复时间（小时）
# ARCH-036 P3-A5: 从 SSoT (thresholds.yaml) 读取，消除第二真源
SLA_DEADLINES: dict[str, int | None] = {
    "CRITICAL": _get_threshold("sla_timers.fix_deadline_hours.CRITICAL", 24),
    "HIGH": _get_threshold("sla_timers.fix_deadline_hours.HIGH", 168),
    "MEDIUM": _get_threshold("sla_timers.fix_deadline_hours.MEDIUM", 720),
    "LOW": None,
    "INFO": None,
}

# 超时升级：超过修复时间 N 小时后 → 升级严重度
# ARCH-036 P3-A5: 从 SSoT (thresholds.yaml) 读取
OVERDUE_ESCALATION: dict[str, int] = {
    "CRITICAL": _get_threshold("sla_timers.overdue_escalation.CRITICAL", 48),
    "HIGH": _get_threshold("sla_timers.overdue_escalation.HIGH", 336),
    "MEDIUM": _get_threshold("sla_timers.overdue_escalation.MEDIUM", 1440),
}

# PERSISTENT 升级：连续存在超过 N 天 → 升级
# ARCH-036 P3-A5: 从 SSoT (thresholds.yaml) 读取
PERSISTENT_UPGRADE: dict[str, tuple[int, str]] = {
    "MEDIUM": (_get_threshold("sla_timers.persistent_upgrade_days.MEDIUM_to_HIGH", 30), "HIGH"),
    "HIGH": (_get_threshold("sla_timers.persistent_upgrade_days.HIGH_to_CRITICAL", 60), "CRITICAL"),
}

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _load_states() -> dict:
    """_load_states implementation."""
    if not _STATE_DB_PATH.exists():
        return {"findings": {}, "audit_log": []}
    with open(_STATE_DB_PATH, encoding="utf-8") as f:
        return json_mod.load(f)


def _save_states(data: dict) -> None:
    """_save_states implementation."""
    _STATE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_safe(_STATE_DB_PATH, json_mod.dumps(data, ensure_ascii=False, indent=2))


def _finding_id(finding: dict) -> str:
    """_finding_id implementation."""
    raw = f"{finding.get('dimension', '')}|{finding.get('check_id', '')}|"
    raw += f"{finding.get('target', {}).get('file_path', '')}|{finding.get('description', '')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _audit_log(data: dict, finding_id: str, from_status: str, to_status: str, reason: str = "") -> None:
    """_audit_log implementation."""
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "finding_id": finding_id,
        "from": from_status,
        "to": to_status,
        "reason": reason,
    }
    data.setdefault("audit_log", []).append(entry)
    if len(data["audit_log"]) > 5000:
        data["audit_log"] = data["audit_log"][-3000:]


def load_findings(findings_file: str | Path) -> dict:
    """load_findings implementation."""
    data = _load_states()
    findings_db = data.setdefault("findings", {})

    with open(findings_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                finding = json_mod.loads(line)
            except json_mod.JSONDecodeError:
                continue

            fid = _finding_id(finding)
            if fid not in findings_db:
                findings_db[fid] = {
                    "finding_id": fid,
                    "status": "OPEN",
                    "severity": finding.get("severity", "LOW"),
                    "dimension": finding.get("dimension", ""),
                    "description": finding.get("description", "")[:200],
                    "file_path": finding.get("target", {}).get("file_path", ""),
                    "created_at": datetime.now(UTC).isoformat(),
                    "updated_at": datetime.now(UTC).isoformat(),
                    "first_seen_at": datetime.now(UTC).isoformat(),
                    "last_seen_at": datetime.now(UTC).isoformat(),
                    "sla_deadline_at": _calc_sla_deadline(finding.get("severity", "LOW")),
                    "persistent_days": 0,
                    "false_positive_count": 0,
                    "transition_count": 0,
                }
            else:
                findings_db[fid]["last_seen_at"] = datetime.now(UTC).isoformat()
                days_persistent = _calc_persistent_days(findings_db[fid])
                findings_db[fid]["persistent_days"] = days_persistent
                _check_persistent_upgrade(data, fid)

    _save_states(data)
    return {"loaded": len(findings_db), "new": 0, "updated": 0}


def _calc_sla_deadline(severity: str) -> str | None:
    """_calc_sla_deadline implementation."""
    hours = SLA_DEADLINES.get(severity)
    if hours is None:
        return None
    return (datetime.now(UTC) + timedelta(hours=hours)).isoformat()


def _calc_persistent_days(finding_state: dict) -> float:
    """_calc_persistent_days implementation."""
    try:
        first_seen = datetime.fromisoformat(finding_state["first_seen_at"])
        return (datetime.now(UTC) - first_seen).total_seconds() / 86400
    except (ValueError, KeyError):
        return EXIT_PASS


def _check_persistent_upgrade(data: dict, finding_id: str) -> None:
    """_check_persistent_upgrade implementation."""
    finding = data["findings"].get(finding_id)
    if not finding:
        return
    sev = finding["severity"]
    days = finding.get("persistent_days", 0)
    if sev in PERSISTENT_UPGRADE:
        threshold, new_sev = PERSISTENT_UPGRADE[sev]
        if days >= threshold:
            old_sev = finding["severity"]
            finding["severity"] = new_sev
            finding["sla_deadline_at"] = _calc_sla_deadline(new_sev)
            _audit_log(data, finding_id, f"PERSISTENT_{old_sev}", f"UPGRADED_{new_sev}", f"连续存在 {days:.0f} 天")


def transition(finding_id: str, to_status: str, reason: str = "") -> dict:
    """transition implementation."""
    data = _load_states()
    finding = data["findings"].get(finding_id)
    if not finding:
        return {"error": f"Finding {finding_id} 不存在"}

    if to_status not in VALID_STATUSES:
        return {"error": f"无效状态: {to_status}"}

    from_status = finding["status"]
    if to_status not in VALID_TRANSITIONS.get(from_status, []):
        return {"error": f"状态转换无效: {from_status} → {to_status}"}

    finding["status"] = to_status
    finding["updated_at"] = datetime.now(UTC).isoformat()
    finding["transition_count"] = finding.get("transition_count", 0) + 1
    if to_status == "FALSE_POSITIVE":
        finding["false_positive_count"] = finding.get("false_positive_count", 0) + 1

    _audit_log(data, finding_id, from_status, to_status, reason)
    _save_states(data)
    return {"status": "ok", "finding_id": finding_id, "from": from_status, "to": to_status}


def check_sla() -> dict:
    """Check compliance and report findings."""
    data = _load_states()
    now = datetime.now(UTC)
    overdue: list[dict] = []

    for fid, finding in data["findings"].items():
        if finding["status"] in ("CLOSED", "VERIFIED", "ACCEPTED_RISK"):
            continue
        deadline = finding.get("sla_deadline_at")
        if not deadline:
            continue
        try:
            dl = datetime.fromisoformat(deadline)
        except ValueError:
            continue
        if now > dl and finding["status"] != "OVERDUE":
            finding["status"] = "OVERDUE"
            finding["updated_at"] = now.isoformat()
            _audit_log(data, fid, "OPEN", "OVERDUE", f"SLA 定时器触发 ({finding['severity']})")
            overdue.append(
                {
                    "finding_id": fid,
                    "severity": finding["severity"],
                    "description": finding.get("description", "")[:100],
                    "deadline_was": deadline,
                }
            )

    _save_states(data)
    return {
        "checked_at": now.isoformat(),
        "overdue_count": len(overdue),
        "overdue": overdue,
    }


def stats() -> dict:
    """stats implementation."""
    data = _load_states()
    counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}
    for finding in data["findings"].values():
        status = finding["status"]
        counts[status] = counts.get(status, 0) + 1
        sev = finding["severity"]
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    return {
        "total_findings": len(data["findings"]),
        "by_status": counts,
        "by_severity": severity_counts,
        "audit_log_entries": len(data.get("audit_log", [])),
    }


def list_by_status(status_filter: str) -> list[dict]:
    """list_by_status implementation."""
    data = _load_states()
    result = []
    for fid, finding in data["findings"].items():
        if finding["status"] == status_filter:
            result.append(finding)
    return result


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="Finding 生命周期状态机")
    parser.add_argument("--load", type=str, help="加载 findings.jsonl 并初始化状态追踪")
    parser.add_argument("--transition", type=str, help="转换指定 Finding 的状态")
    parser.add_argument("--to", type=str, help="目标状态")
    parser.add_argument("--reason", type=str, default="", help="转换原因")
    parser.add_argument("--check-sla", action="store_true", help="检查 SLA 定时器")
    parser.add_argument("--list", type=str, help="列出指定状态的 Finding")
    parser.add_argument("--stats", action="store_true", help="统计信息")
    args = parser.parse_args()

    if args.load:
        result = load_findings(args.load)
        print(f"[FSM] 已加载: {result['loaded']} 个 Finding 状态追踪", file=sys.stderr)
    elif args.transition and args.to:
        result = transition(args.transition, args.to, args.reason)
        print(f"[FSM] 状态转换: {result}", file=sys.stderr)
    elif args.check_sla:
        result = check_sla()
        print(f"[FSM] SLA 检查: {result['overdue_count']} 个超时", file=sys.stderr)
        for o in result["overdue"]:
            print(f"  ⏰ [{o['severity']}] {o['finding_id']}: {o['description']}", file=sys.stderr)
    elif args.list:
        items = list_by_status(args.list)
        for item in items:
            print(f"  [{item['severity']}] {item['finding_id']}: {item.get('description', '')[:100]}", file=sys.stderr)
    elif args.stats:
        result = stats()
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
