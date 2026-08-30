# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.tamper_proof_audit
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.shared.contracts.protocols
# [CONSUMERS] src/zephyr/gov_drift/_analysis.py ; tests/audit/test_tamper_proof_audit.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审计记录不可篡改
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Tamper-Proof Audit — 防篡改审计 D-023-37 · §6.26。


append_only_events: SQLite TRIGGER禁止UPDATE/DELETE + event sourcing


git_commit_audit_log: 每DEEP scan AUDIT_<scan_id>.yaml(sha256+per state计数)commit到Git


anomaly_detection: 总行数减少/批量清洗/回溯修改 -> P0 CRITICAL从Git恢复


对标 blueprint.md §6.26。


同时写入核心 zephyr.gov_audit.writer.AuditWriter 不可变审计链。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: db_path 参数
#   fields: 参数 db_path，类型注解 str
#   code: tamper_proof_audit.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: scan_id 参数
#   fields: 参数 scan_id，类型注解 str
#   code: tamper_proof_audit.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 str
#   code: tamper_proof_audit.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: current 参数
#   fields: 参数 current，类型注解 AuditRecord
#   code: tamper_proof_audit.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① setup_append_only
#   name_en: setup_append_only
#   intro: setup_append_only(db_path) 源码 L210-L226
#   desc: 源码 L210-L226
#   inputs: db_path
#   outputs: bool
# - id: A2
#   name_zh: ② snapshot_event_hash
#   name_en: snapshot_event_hash
#   intro: snapshot_event_hash(db_path) 源码 L229-L246
#   desc: 源码 L229-L246
#   inputs: db_path
#   outputs: str
# - id: A3
#   name_zh: ③ count_states
#   name_en: count_states
#   intro: count_states(db_path) 源码 L249-L267
#   desc: 源码 L249-L267
#   inputs: db_path
#   outputs: dict[str, int]
# - id: A4
#   name_zh: ④ generate_audit_log
#   name_en: generate_audit_log
#   intro: generate_audit_log(scan_id, db_path, project_root)…
#   desc: 源码 L270-L391
#   inputs: scan_id db_path project_root
#   outputs: AuditRecord
# - id: A5
#   name_zh: ⑤ detect_anomalies
#   name_en: detect_anomalies
#   intro: detect_anomalies(current, previous) 源码 L394-L430
#   desc: 源码 L394-L430
#   inputs: current previous
#   outputs: list[AnomalyAlert]
#   （注：A5 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_analysis.py ; tests/audit/test_tamper_proof_audit.py
# - id: O2
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_analysis.py ; tests/audit/test_tamper_proof_audit.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
from typing import Final

from zephyr.shared.io.serialization import dumps

logger = logging.getLogger(__name__)

import hashlib
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import final

from zephyr.governance.persistence.sqlite_schema import get_db_connection


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
    except Exception as e:  # 5.70.4 修复：异常路径添加日志，区分"真阴性"和"异常降级"  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("setup_append_only failed: %s", e, exc_info=True)
        return False
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return ""
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.debug("suppressed error in tamper_proof_audit", exc_info=True)
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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

        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        # 5.37.6 治本：原 subprocess 裸 git add/commit 绕过 GitCommitGateway——
        # post_commit_guard（#ARCH-050）会 git reset --soft 撤销无 [GW:] 标记的
        # commit，审计锚定静默失效。改走 GitCommitGateway._commit_auto（reconciler
        # auto-commit 统一入口）：本函数在 DEEP scan 流程中运行，无 AI session
        # 上下文，_commit_auto 不要求 session claim，自带 _GlobalCommitLock 串行锁
        # + DIRECTORY-CONTRACT/TTL/FILE-PLACEMENT gate + [GW:...:auto] 标记。
        # status==OK 才置 committed_to_git；gate 阻断/失败仅告警（审计文件已落盘，
        # 不中断 scan 主流程）。
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
            CommitStatus,
            GitCommitGateway,
        )

        gateway = GitCommitGateway(project_root=project_root)
        commit_result = gateway._commit_auto(
            session_id="drift-tamper-proof-audit",
            files=[str(audit_path)],
            message=f"audit_log: {scan_id} sha256={events_hash[:12]}",
        )

        if commit_result.status == CommitStatus.OK:
            record.committed_to_git = True
        elif commit_result.status == CommitStatus.NOTHING_TO_COMMIT:
            logger.info("tamper_proof_audit: audit log unchanged, nothing to commit")
        else:
            logger.warning(
                "tamper_proof_audit: gateway auto-commit not OK (status=%s): %s",
                commit_result.status,
                commit_result.message,
            )

    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning("tamper_proof_audit: gateway auto-commit failed: %s", e, exc_info=True)

    import importlib as _importlib

    _write_to_core = _importlib.import_module("zephyr.gov_audit.bridge").write_to_core
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
