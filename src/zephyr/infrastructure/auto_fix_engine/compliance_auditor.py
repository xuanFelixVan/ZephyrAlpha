# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.compliance_auditor
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;MOD-INF-020(audit-trail)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 每次修复MUST生成ComplianceEvidence;防篡改哈希MUST可验证
# [MODIFY-GUARD] blueprint.md §3;auto_fix_config.yaml compliance段
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ComplianceAuditError
# [TESTS] tests/auto-fix-engine/test_compliance_auditor.py
# [A_module] module_id=MOD-INF_compliance_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import hashlib
import logging
import os
import sqlite3
from zephyr.shared.io.sqlite_factory import get_db_connection
from datetime import UTC, datetime

from zephyr.infrastructure.auto_fix_engine.models import ComplianceEvidence, FixAction
from zephyr.shared.io.paths import DB_PATH

logger = logging.getLogger(__name__)


class ComplianceAuditor:
    def __init__(self, db_path: str = str(DB_PATH), retention_days: int = 90) -> None:
        self._db_path = db_path
        self._retention_days = retention_days
        self._ensure_db()

    def _ensure_db(self) -> None:
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        conn = get_db_connection(self._db_path)
        try:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS fix_compliance "
                "(compliance_id INTEGER PRIMARY KEY AUTOINCREMENT, fix_id TEXT, action_type TEXT, "
                "target TEXT, before_hash TEXT DEFAULT '', after_hash TEXT DEFAULT '', "
                "timestamp TEXT, actor TEXT DEFAULT 'auto-fix-engine', confidence TEXT DEFAULT '', "
                "rbac_decision TEXT DEFAULT '', validation_result TEXT DEFAULT '', "
                "audit_trail_id TEXT DEFAULT '', tamper_proof_hash TEXT NOT NULL)"
            )
            conn.commit()
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            conn.close()

    def audit_fix(self, action: FixAction, rbac_decision: str = "", validation_result: str = "") -> ComplianceEvidence:
        before_hash = hashlib.sha256(action.before.encode()).hexdigest()[:32] if action.before else ""
        after_hash = hashlib.sha256(action.after.encode()).hexdigest()[:32] if action.after else ""
        evidence = ComplianceEvidence(
            fix_id=action.action_id,
            action_type=action.action_type,
            target=action.target,
            before_hash=before_hash,
            after_hash=after_hash,
            actor="auto-fix-engine",
            confidence=action.confidence.value,
            rbac_decision=rbac_decision,
            validation_result=validation_result,
            audit_trail_id=action.audit_trail_id,
        )
        self._persist(evidence)
        return evidence

    def verify_evidence(self, evidence: ComplianceEvidence) -> bool:
        raw = (
            f"{evidence.fix_id}:{evidence.action_type}:{evidence.target}:"
            f"{evidence.before_hash}:{evidence.after_hash}:{evidence.timestamp}"
        )
        expected_hash = hashlib.sha256(raw.encode()).hexdigest()[:32]
        return evidence.tamper_proof_hash == expected_hash

    def get_evidence(self, fix_id: str) -> ComplianceEvidence | None:
        conn = None
        try:
            conn = get_db_connection(self._db_path)
            row = conn.execute(
                "SELECT fix_id, action_type, target, before_hash, after_hash, "
                "timestamp, actor, confidence, rbac_decision, validation_result, "
                "audit_trail_id, tamper_proof_hash FROM fix_compliance WHERE fix_id=?",
                (fix_id,),
            ).fetchone()
            if row:
                return ComplianceEvidence(
                    fix_id=row[0],
                    action_type=row[1],
                    target=row[2],
                    before_hash=row[3],
                    after_hash=row[4],
                    timestamp=row[5],
                    actor=row[6],
                    confidence=row[7],
                    rbac_decision=row[8],
                    validation_result=row[9],
                    audit_trail_id=row[10],
                    tamper_proof_hash=row[11],
                )
        except Exception as e:
            logger.warning("ComplianceAuditor.get_evidence: evidence lookup failed (%s: %s)", type(e).__name__, e, exc_info=True)
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            if conn is not None:
                conn.close()
        return None

    def cleanup_expired(self) -> int:
        cutoff = (datetime.now(UTC) - __import__("datetime").timedelta(days=self._retention_days)).isoformat()
        conn = None
        try:
            conn = get_db_connection(self._db_path)
            cursor = conn.execute("DELETE FROM fix_compliance WHERE timestamp < ?", (cutoff,))
            conn.commit()
            deleted = cursor.rowcount
            return deleted
        except Exception:
            return 0
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            if conn is not None:
                conn.close()

    def _persist(self, evidence: ComplianceEvidence) -> None:
        conn = None
        try:
            conn = get_db_connection(self._db_path)
            conn.execute(
                "INSERT INTO fix_compliance (fix_id, action_type, target, before_hash, after_hash, "
                "timestamp, actor, confidence, rbac_decision, validation_result, "
                "audit_trail_id, tamper_proof_hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    evidence.fix_id,
                    evidence.action_type,
                    evidence.target,
                    evidence.before_hash,
                    evidence.after_hash,
                    evidence.timestamp,
                    evidence.actor,
                    evidence.confidence,
                    evidence.rbac_decision,
                    evidence.validation_result,
                    evidence.audit_trail_id,
                    evidence.tamper_proof_hash,
                ),
            )
            conn.commit()
        except Exception as exc:
            logger.error("Failed to persist compliance evidence: %s", exc, exc_info=True)
        # 5.49.2 修复：异常路径确保连接归还
        finally:
            if conn is not None:
                conn.close()