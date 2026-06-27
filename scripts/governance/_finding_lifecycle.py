# [BLUEPRINT] GOV-068 | docs/03_modules/_domain_governance/blueprint.md | §3.9
# [MODULE] scripts.governance._finding_lifecycle
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] run_all.py;phase_manager.py
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 活跃Finding不可自动清理;归档操作可逆
# [MODIFY-GUARD] TTL规则变更需同步finding_state_machine.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] FindingNotFoundError;ArchiveCorruptionError
# [TESTS] tests/test_finding_lifecycle.py
# [TTL] task_bound

from __future__ import annotations

__manifest__ = """
args: []
description: >
  Finding TTL 管理 + 自动清理——扫描过期 Finding，归档终态 Finding（30天），
  降级 OVERDUE Finding 为 WONTFIX（90天），防止磁盘爆满。
dimensions:
- D1
- D5
priority: P2
timeout_seconds: 60
warn_only: true
"""

import argparse
import json as json_mod
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_STATE_DB_PATH = _REPO_ROOT / "scripts" / "governance" / "meta" / "finding_state_db.json"

_src = _REPO_ROOT / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

try:
    from _shared.constants import EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS
except ImportError:
    EXIT_PASS = 0
    EXIT_FINDINGS = 1
    EXIT_ERROR = 2

ARCHIVE_STATUSES = frozenset({"CLOSED", "FALSE_POSITIVE", "WONTFIX", "ACCEPTED_RISK"})
DEGRADE_STATUSES = frozenset({"OVERDUE"})
ACTIVE_STATUSES = frozenset({"OPEN", "IN_PROGRESS", "FIXED", "VERIFIED", "DEFERRED"})

TTL_DAYS_ARCHIVE = 30
TTL_DAYS_DEGRADE = 90
TTL_WARN_DAYS = 7

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


class FindingNotFoundError(Exception):
    def __init__(self, finding_id: str):
        self.finding_id = finding_id
        super().__init__(f"Finding not found: {finding_id}")


class ArchiveCorruptionError(Exception):
    def __init__(self, path: Path, detail: str):
        self.path = path
        self.detail = detail
        super().__init__(f"Archive corruption at {path}: {detail}")


def _load_state_db() -> dict:
    if not _STATE_DB_PATH.exists():
        return {"findings": {}, "audit_log": []}
    with open(_STATE_DB_PATH, encoding="utf-8") as f:
        return json_mod.load(f)


def _save_state_db(data: dict) -> None:
    _STATE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = f"{_STATE_DB_PATH}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json_mod.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, _STATE_DB_PATH)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def _append_audit(data: dict, finding_id: str, action: str, detail: str) -> None:
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "finding_id": finding_id,
        "action": action,
        "detail": detail,
    }
    data.setdefault("audit_log", []).append(entry)
    if len(data["audit_log"]) > 5000:
        data["audit_log"] = data["audit_log"][-3000:]


def _parse_iso_or_none(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def _days_since(dt: datetime | None) -> float | None:
    if dt is None:
        return None
    return (datetime.now(UTC) - dt).total_seconds() / 86400


class FindingLifecycleManager:
    def __init__(self, findings_dir: Path | None = None, archive_dir: Path | None = None):
        self.findings_dir = findings_dir or _REPO_ROOT / "data" / "findings"
        self.archive_dir = archive_dir or self.findings_dir / "archive"
        self.state_db_path = _STATE_DB_PATH

    def scan_expired(self) -> dict[str, list[dict]]:
        data = _load_state_db()
        now = datetime.now(UTC)
        archive_expired: list[dict] = []
        degrade_expired: list[dict] = []
        archive_warn: list[dict] = []
        degrade_warn: list[dict] = []

        for fid, finding in data.get("findings", {}).items():
            status = finding.get("status", "")
            updated_at = _parse_iso_or_none(finding.get("updated_at"))
            days = _days_since(updated_at)

            if status in ARCHIVE_STATUSES:
                if days is not None and days >= TTL_DAYS_ARCHIVE:
                    archive_expired.append(
                        {
                            "finding_id": fid,
                            "status": status,
                            "days_expired": round(days - TTL_DAYS_ARCHIVE, 1),
                            "updated_at": finding.get("updated_at", ""),
                        }
                    )
                elif days is not None and days >= TTL_DAYS_ARCHIVE - TTL_WARN_DAYS:
                    archive_warn.append(
                        {
                            "finding_id": fid,
                            "status": status,
                            "days_remaining": round(TTL_DAYS_ARCHIVE - days, 1),
                            "updated_at": finding.get("updated_at", ""),
                        }
                    )

            elif status in DEGRADE_STATUSES:
                if days is not None and days >= TTL_DAYS_DEGRADE:
                    degrade_expired.append(
                        {
                            "finding_id": fid,
                            "status": status,
                            "days_expired": round(days - TTL_DAYS_DEGRADE, 1),
                            "updated_at": finding.get("updated_at", ""),
                        }
                    )
                elif days is not None and days >= TTL_DAYS_DEGRADE - TTL_WARN_DAYS:
                    degrade_warn.append(
                        {
                            "finding_id": fid,
                            "status": status,
                            "days_remaining": round(TTL_DAYS_DEGRADE - days, 1),
                            "updated_at": finding.get("updated_at", ""),
                        }
                    )

        return {
            "archive": archive_expired,
            "degrade": degrade_expired,
            "archive_warn": archive_warn,
            "degrade_warn": degrade_warn,
        }

    def archive_finding(self, finding_id: str) -> Path:
        data = _load_state_db()
        finding = data.get("findings", {}).get(finding_id)
        if finding is None:
            raise FindingNotFoundError(finding_id)

        self.archive_dir.mkdir(parents=True, exist_ok=True)

        archive_file = self.archive_dir / f"{finding_id}.json"
        archive_data = {
            "finding_id": finding_id,
            "archived_at": datetime.now(UTC).isoformat(),
            "original_status": finding.get("status", ""),
            "finding_data": finding,
        }
        tmp_path = f"{archive_file}.{os.getpid()}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json_mod.dump(archive_data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, archive_file)
        except PermissionError:
            try:
                os.remove(tmp_path)
            except OSError:
                pass
            raise

        del data["findings"][finding_id]
        _append_audit(data, finding_id, "ARCHIVED", f"归档自状态 {finding.get('status', '')}, TTL={TTL_DAYS_ARCHIVE}天")
        _save_state_db(data)

        return archive_file

    def degrade_overdue(self, finding_id: str) -> dict:
        data = _load_state_db()
        finding = data.get("findings", {}).get(finding_id)
        if finding is None:
            raise FindingNotFoundError(finding_id)

        old_status = finding.get("status", "")
        if old_status != "OVERDUE":
            return {
                "finding_id": finding_id,
                "error": f"只能降级 OVERDUE 状态的 Finding，当前状态: {old_status}",
            }

        finding["status"] = "WONTFIX"
        finding["updated_at"] = datetime.now(UTC).isoformat()
        finding["transition_count"] = finding.get("transition_count", 0) + 1

        _append_audit(data, finding_id, "DEGRADED", f"OVERDUE→WONTFIX, TTL={TTL_DAYS_DEGRADE}天自动降级")
        _save_state_db(data)

        return {
            "finding_id": finding_id,
            "from": old_status,
            "to": "WONTFIX",
            "degraded_at": finding["updated_at"],
        }

    def run_cleanup(self, dry_run: bool = True) -> dict:
        expired = self.scan_expired()
        archived: list[dict] = []
        degraded: list[dict] = []
        errors: list[dict] = []

        for item in expired["degrade"]:
            fid = item["finding_id"]
            if dry_run:
                degraded.append({"finding_id": fid, "action": "DEGRADE(dry-run)", "status": "OVERDUE"})
            else:
                try:
                    result = self.degrade_overdue(fid)
                    degraded.append(result)
                except FindingNotFoundError:
                    errors.append({"finding_id": fid, "error": "not_found"})

        for item in expired["archive"]:
            fid = item["finding_id"]
            if dry_run:
                archived.append({"finding_id": fid, "action": "ARCHIVE(dry-run)", "status": item["status"]})
            else:
                try:
                    path = self.archive_finding(fid)
                    archived.append({"finding_id": fid, "action": "ARCHIVED", "path": str(path)})
                except FindingNotFoundError:
                    errors.append({"finding_id": fid, "error": "not_found"})

        return {
            "dry_run": dry_run,
            "archived_count": len(archived),
            "degraded_count": len(degraded),
            "error_count": len(errors),
            "archived": archived,
            "degraded": degraded,
            "errors": errors,
            "warn_archive": expired["archive_warn"],
            "warn_degrade": expired["degrade_warn"],
        }

    def stats(self) -> dict:
        data = _load_state_db()
        findings = data.get("findings", {})
        now = datetime.now(UTC)

        status_counts: dict[str, int] = {}
        severity_counts: dict[str, int] = {}
        ttl_summary: dict[str, dict] = {}

        for finding in findings.values():
            status = finding.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
            sev = finding.get("severity", "UNKNOWN")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

            updated_at = _parse_iso_or_none(finding.get("updated_at"))
            days = _days_since(updated_at)

            if status in ARCHIVE_STATUSES:
                remaining = max(0, TTL_DAYS_ARCHIVE - (days or 0))
                ttl_summary.setdefault("archive", {"total": 0, "expired": 0, "warning": 0})
                ttl_summary["archive"]["total"] += 1
                if days is not None and days >= TTL_DAYS_ARCHIVE:
                    ttl_summary["archive"]["expired"] += 1
                elif days is not None and days >= TTL_DAYS_ARCHIVE - TTL_WARN_DAYS:
                    ttl_summary["archive"]["warning"] += 1
            elif status in DEGRADE_STATUSES:
                remaining = max(0, TTL_DAYS_DEGRADE - (days or 0))
                ttl_summary.setdefault("degrade", {"total": 0, "expired": 0, "warning": 0})
                ttl_summary["degrade"]["total"] += 1
                if days is not None and days >= TTL_DAYS_DEGRADE:
                    ttl_summary["degrade"]["expired"] += 1
                elif days is not None and days >= TTL_DAYS_DEGRADE - TTL_WARN_DAYS:
                    ttl_summary["degrade"]["warning"] += 1

        archive_count = 0
        if self.archive_dir.exists():
            archive_count = sum(1 for p in self.archive_dir.glob("*.json") if p.is_file())

        return {
            "total_active": len(findings),
            "total_archived": archive_count,
            "by_status": status_counts,
            "by_severity": severity_counts,
            "ttl_summary": ttl_summary,
            "ttl_rules": {
                "archive_days": TTL_DAYS_ARCHIVE,
                "degrade_days": TTL_DAYS_DEGRADE,
                "warn_days": TTL_WARN_DAYS,
                "archive_statuses": sorted(ARCHIVE_STATUSES),
                "degrade_statuses": sorted(DEGRADE_STATUSES),
                "active_statuses": sorted(ACTIVE_STATUSES),
            },
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Finding TTL 管理 + 自动清理")
    parser.add_argument("--dry-run", action="store_true", default=True, help="只报告不执行（默认开启）")
    parser.add_argument("--execute", action="store_true", help="实际执行清理（关闭 dry-run）")
    parser.add_argument("--warn-only", action="store_true", help="有发现时返回 EXIT_PASS 而非 EXIT_FINDINGS")
    parser.add_argument("--stats", action="store_true", help="输出统计信息")
    parser.add_argument("--scan", action="store_true", help="扫描过期 Finding")
    args = parser.parse_args()

    mgr = FindingLifecycleManager()

    if args.stats:
        result = mgr.stats()
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))
        return EXIT_PASS

    if args.scan:
        result = mgr.scan_expired()
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))
        return EXIT_PASS

    dry_run = not args.execute
    result = mgr.run_cleanup(dry_run=dry_run)

    print(f"[LIFECYCLE] 清理{'(dry-run)' if dry_run else '(执行)'}:", file=sys.stderr)
    print(f"  归档: {result['archived_count']} 个", file=sys.stderr)
    print(f"  降级: {result['degraded_count']} 个", file=sys.stderr)
    print(f"  错误: {result['error_count']} 个", file=sys.stderr)

    if result["warn_archive"]:
        print(f"  即将过期(归档): {len(result['warn_archive'])} 个", file=sys.stderr)
        for w in result["warn_archive"]:
            print(f"    - {w['finding_id']} ({w['status']}) 剩余 {w['days_remaining']}天", file=sys.stderr)

    if result["warn_degrade"]:
        print(f"  即将过期(降级): {len(result['warn_degrade'])} 个", file=sys.stderr)
        for w in result["warn_degrade"]:
            print(f"    - {w['finding_id']} ({w['status']}) 剩余 {w['days_remaining']}天", file=sys.stderr)

    if not dry_run and (result["archived_count"] > 0 or result["degraded_count"] > 0):
        print(json_mod.dumps(result, ensure_ascii=False, indent=2))

    has_expired = result["archived_count"] > 0 or result["degraded_count"] > 0
    if has_expired and not args.warn_only:
        return EXIT_FINDINGS
    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
