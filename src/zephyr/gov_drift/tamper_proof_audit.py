# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.tamper_proof_audit
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.shared.contracts.protocols
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_analysis.py; tests/audit/test_tamper_proof_audit.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审计记录不可篡改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_tamper_proof_audit | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Tamper-Proof Audit — 防篡改审计 D-023-37 · §6.26。


append_only_events: SQLite TRIGGER禁止UPDATE/DELETE + event sourcing


git_commit_audit_log: 每DEEP scan AUDIT_<scan_id>.yaml(sha256+per state计数)commit到Git


anomaly_detection: 总行数减少/批量清洗/回溯修改 -> P0 CRITICAL从Git恢复


对标 blueprint.md §6.26。


同时写入核心 zephyr.governance.audit_trail.writer.AuditWriter 不可变审计链。"""

from __future__ import annotations

from typing import Final
from zephyr.shared.io.serialization import dumps

import logging

logger = logging.getLogger(__name__)

import hashlib
import os
import sqlite3
from zephyr.governance.persistence.sqlite_schema import get_db_connection
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import final


@final
@dataclass
class AuditRecord:
    scan_id: str

    state_counts: dict[str, int]

    events_hash: str

    file_hashes: dict[str, str]

    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    committed_to_git: bool = False

    verified: bool = False


@final
@dataclass
class AnomalyAlert:
    alert_id: str

    anomaly_type: str

    severity: str = "CRITICAL"

    description: str = ""

    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    recovery_suggestion: str = ""


APPEND_ONLY_TRIGGERS: Final[str] = """


CREATE TRIGGER IF NOT EXISTS drift_events_no_update


BEFORE UPDATE ON drift_events


BEGIN


    SELECT RAISE(FAIL, 'UPDATE denied on drift_events — append_only');


END;


CREATE TRIGGER IF NOT EXISTS drift_events_no_delete


BEFORE DELETE ON drift_events


BEGIN


    SELECT RAISE(FAIL, 'DELETE denied on drift_events — append_only');


END;


"""


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def setup_append_only(db_path: str) -> bool:
    # 5.49.3 修复：原 try/except 中 conn 未在异常分支关闭，导致连接泄漏。改用 try/finally 保证关闭。
    conn = None
    try:
        conn = get_db_connection(db_path)
        conn.executescript(APPEND_ONLY_TRIGGERS)
        conn.commit()
        return True
    except Exception as e:  # 5.70.4 修复：异常路径添加日志，区分"真阴性"和"异常降级"
        logger.warning("setup_append_only failed: %s", e, exc_info=True)
        return False
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception as e:
                logger.debug("suppressed error in tamper_proof_audit", exc_info=True)


def snapshot_event_hash(db_path: str) -> str:
    # 5.49.3 修复：原 try/except 中 conn 未在异常分支关闭。改用 try/finally 保证关闭。
    conn = None
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT event_id, detector_id, severity, state FROM drift_events ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        data = dumps([list(r) for r in rows])
        return _sha256(data)
    except Exception:
        return ""
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception as e:
                logger.debug("suppressed error in tamper_proof_audit", exc_info=True)


def count_states(db_path: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    # 5.49.3 修复：原 try/except 中 conn 未在异常分支关闭。改用 try/finally 保证关闭。
    conn = None
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT state, COUNT(*) FROM drift_events GROUP BY state")
        for row in cursor.fetchall():
            counts[str(row[0])] = int(row[1])
    except Exception as e:
        logger.debug("suppressed error in tamper_proof_audit", exc_info=True)
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception as e:
                logger.debug("suppressed error in tamper_proof_audit", exc_info=True)
    return counts


def generate_audit_log(
    scan_id: str,
    db_path: str,
    project_root: str,
) -> AuditRecord:
    state_counts = count_states(db_path)

    events_hash = snapshot_event_hash(db_path)

    src_files: dict[str, str] = {}

    src_root = Path(project_root) / "src"

    # 5.37.10 修复：原 [:30] 仅哈希前30个 .py 文件，项目有数千个 .py 文件，
    # 第31个及之后的文件篡改完全不可检测。移除 [:30] 切片，哈希全部 .py 文件。
    for pf in list(src_root.rglob("*.py")):
        try:
            content = pf.read_text(encoding="utf-8")

            src_files[pf.relative_to(project_root).as_posix()] = _sha256(content)

        except Exception as e:
            logger.warning("suppressed error in tamper_proof_audit", exc_info=True)

    record = AuditRecord(
        scan_id=scan_id,
        state_counts=state_counts,
        events_hash=events_hash,
        file_hashes=src_files,
    )

    audit_dir = Path(project_root) / "data" / "drift"

    audit_dir.mkdir(parents=True, exist_ok=True)

    audit_path = audit_dir / f"AUDIT_{scan_id}.yaml"

    tmp_path = str(audit_path) + f".{os.getpid()}.tmp"

    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(f"# Audit Log: {scan_id}\n")

            f.write(f"timestamp: {record.timestamp.isoformat()}\n")

            f.write(f"events_hash: {events_hash}\n")

            f.write("state_counts:\n")

            for s, c in state_counts.items():
                f.write(f"  {s}: {c}\n")

            f.write("file_hashes:\n")

            for fp, fh in src_files.items():
                # 5.37.10 修复：原 fh[:16] 将 sha256 截断为16个十六进制字符（64位），
                # 降低碰撞阻力。保留完整 sha256（64个十六进制字符=256位）。
                f.write(f"  {fp}: {fh}\n")

            # 5.74.4 修复：os.replace 前刷盘，确保 tmp 内容落盘，防止崩溃后
            # 目标文件存在但内容为空/不完整，破坏审计完整性。
            f.flush()
            os.fsync(f.fileno())

        os.replace(tmp_path, str(audit_path))

    except PermissionError:
        try:
            os.remove(tmp_path)

        except OSError:
            pass

    try:
        # 5.75.1 修复：检查 git add/commit 返回码，失败时不置 committed_to_git=True
        add_result = subprocess.run(
            ["git", "add", str(audit_path.relative_to(project_root))],
            capture_output=True,
            timeout=10,
            cwd=project_root,
        )

        if add_result.returncode != 0:
            logger.warning(
                "tamper_proof_audit: git add failed (returncode=%d): %s",
                add_result.returncode,
                add_result.stderr.decode("utf-8", errors="replace").strip(),
            )
        else:
            commit_result = subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    f"audit_log: {scan_id} sha256={events_hash[:12]}",
                ],
                capture_output=True,
                timeout=10,
                cwd=project_root,
            )

            if commit_result.returncode != 0:
                logger.warning(
                    "tamper_proof_audit: git commit failed (returncode=%d): %s",
                    commit_result.returncode,
                    commit_result.stderr.decode("utf-8", errors="replace").strip(),
                )
            else:
                record.committed_to_git = True

    except Exception as e:
        logger.warning("suppressed error in tamper_proof_audit", exc_info=True)

    import importlib as _importlib

    _write_to_core = _importlib.import_module("zephyr.governance.audit_trail.bridge").write_to_core
    _write_to_core(
        "drift_tamper_proof_audit",
        {
            "scan_id": scan_id,
            "events_hash": events_hash[:16],
            "committed_to_git": record.committed_to_git,
            "state_counts": state_counts,
        },
    )

    return record


def detect_anomalies(
    current: AuditRecord,
    previous: AuditRecord | None = None,
) -> list[AnomalyAlert]:
    alerts: list[AnomalyAlert] = []

    if previous:
        total_before = sum(previous.state_counts.values())

        total_after = sum(current.state_counts.values())

        if total_after < total_before * 0.5 and total_before > 10:
            alerts.append(
                AnomalyAlert(
                    alert_id=f"anomaly-total-drop-{current.scan_id}",
                    anomaly_type="TOTAL_ROW_DROP",
                    description=(f"Event count dropped from {total_before} to {total_after} — possible batch purge"),
                    severity="CRITICAL",
                    recovery_suggestion="Restore from git and re-import events",
                )
            )

        resolved_before = previous.state_counts.get("RESOLVED", 0)

        resolved_after = current.state_counts.get("RESOLVED", 0)

        if resolved_after < resolved_before * 0.5 and resolved_before > 5:
            alerts.append(
                AnomalyAlert(
                    alert_id=f"anomaly-resolved-rewind-{current.scan_id}",
                    anomaly_type="RESOLVED_REWIND",
                    description=(f"RESOLVED count dropped: {resolved_before} -> {resolved_after}"),
                    recovery_suggestion="Check for retroactive state modification",
                )
            )

    return alerts
