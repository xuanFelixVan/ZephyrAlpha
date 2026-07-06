# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.audit_chain_verifier
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.rule_enforcement.gate_context; zephyr.governance.audit_trail.writer
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_audit_chain_verifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""审计链验证工具——独立重放门禁判定+Hash链完整性校验（beta）
同时将门禁审计事件写入核心 zephyr.governance.audit_trail.writer.AuditWriter 不可变审计链
"""

from zephyr.shared.io.serialization import dumps
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

from zephyr.governance.rule_enforcement.gate_engine.gate_context import GateContext, GateResult, GateStatus

_CORE_AUDIT_AVAILABLE = False
try:
    from zephyr.governance.audit_trail.writer import AuditWriter as _CoreAuditWriter

    _CORE_AUDIT_AVAILABLE = True
except ImportError:
    _CoreAuditWriter = None

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    gate_id: str
    status: GateStatus
    reasons: list[str]
    previous_hash: str
    hash: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class AuditReport:
    entries: list[AuditEntry]
    chain_valid: bool
    reproduced: bool
    verified_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def summary(self) -> str:
        return (
            f"AuditReport: {len(self.entries)} entries, "
            f"chain={'OK' if self.chain_valid else 'BROKEN'}, "
            f"reproduced={'OK' if self.reproduced else 'MISMATCH'}"
        )


class AuditChainVerifier:
    def __init__(self) -> None:
        self._chain: list[AuditEntry] = []
        self._last_hash = "0" * 64
        self._core_writer: _CoreAuditWriter | None = None
        if _CORE_AUDIT_AVAILABLE:
            try:
                self._core_writer = _CoreAuditWriter()
            except Exception as e:
                logger.warning("suppressed error in audit_chain_verifier", exc_info=True)

    def append(self, gate_id: str, result: GateResult) -> AuditEntry:
        payload = {
            "gate_id": gate_id,
            "status": result.status.name,
            "reasons": result.reasons,
            "timestamp": result.timestamp.isoformat(),
            "previous_hash": self._last_hash,
        }
        entry_hash = self._compute_hash(payload)
        entry = AuditEntry(
            gate_id=gate_id,
            status=result.status,
            reasons=list(result.reasons),
            previous_hash=self._last_hash,
            hash=entry_hash,
        )
        self._chain.append(entry)
        self._last_hash = entry_hash
        logger.debug("audit entry #%d: %s -> %s", len(self._chain), gate_id, entry_hash[:16])

        if self._core_writer is not None:
            try:
                core_event = {
                    "event_type": "gate_audit",
                    "agent_id": "gate_engine",
                    "session_id": gate_id,
                    "target_path": gate_id,
                    "operation": "gate_check",
                    "status": result.status.name,
                    "reasons": list(result.reasons),
                    "entry_hash": entry_hash,
                }
                self._core_writer.write(core_event)
            except Exception as e:
                logger.warning("suppressed error in audit_chain_verifier", exc_info=True)

        return entry

    def verify_chain(self) -> AuditReport:
        prev = "0" * 64
        valid = True
        for entry in self._chain:
            if entry.previous_hash != prev:
                logger.error(
                    "chain break at %s: expected=%s got=%s", entry.gate_id, prev[:16], entry.previous_hash[:16]
                )
                valid = False
                break
            payload = {
                "gate_id": entry.gate_id,
                "status": entry.status.name,
                "reasons": entry.reasons,
                "timestamp": entry.timestamp.isoformat(),
                "previous_hash": prev,
            }
            computed = self._compute_hash(payload)
            if computed != entry.hash:
                logger.error("hash mismatch at %s", entry.gate_id)
                valid = False
                break
            prev = entry.hash
        return AuditReport(entries=list(self._chain), chain_valid=valid, reproduced=valid)

    def replay(self, ctx: GateContext, checkers: dict[str, callable]) -> AuditReport:
        results: list[GateResult] = []
        for gate_id, checker in checkers.items():
            results.append(checker(ctx))

        reproduced = True
        for result in results:
            matching = [e for e in self._chain if e.gate_id == result.gate_id]
            if not matching or matching[-1].status != result.status:
                reproduced = False
                break

        return AuditReport(
            entries=list(self._chain), chain_valid=self.verify_chain().chain_valid, reproduced=reproduced
        )

    @staticmethod
    def _compute_hash(payload: dict) -> str:
        payload_str = dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode()).hexdigest()

    @property
    def length(self) -> int:
        return len(self._chain)

    def clear(self, reason: str = "") -> None:
        # 5.17.4 修复：clear() 前写入审计事件，留痕可追溯（防止无审计抹除链）
        if self._core_writer is not None:
            try:
                self._core_writer.write({
                    "event_type": "chain_cleared",
                    "agent_id": "audit_chain_verifier",
                    "reason": reason or "unspecified",
                    "chain_length": len(self._chain),
                    "last_hash": self._last_hash,
                })
            except Exception as e:
                logger.warning("suppressed error in audit_chain_verifier", exc_info=True)
        self._chain.clear()
        self._last_hash = "0" * 64


__all__ = ["AuditChainVerifier", "AuditEntry", "AuditReport"]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
