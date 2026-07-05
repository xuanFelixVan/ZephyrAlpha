# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.drift_hotfix_bypass
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES] zephyr.shared.contracts.protocols
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_drift.py; src/zephyr/governance/rule_enforcement/drift_detector.py (+3 more)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 旁路必须72h自动过期
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_drift_hotfix_bypass | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drift Hotfix Bypass — drift_hotfix_bypass.py





module_id: MOD-INF-023


P0 Hotfix 快速旁路处理：[HOTFIX]/[EMERGENCY] commit 自动标记为 ACKNOWLEDGED + SUPPRESSED(72h)。


对标 blueprint.md §2.12（热修复/紧急变更旁路）。


同时写入核心 zephyr.governance.audit_trail.writer.AuditWriter 不可变审计链。"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

_CORE_AUDIT_AVAILABLE = False


try:
    from zephyr.shared.contracts.protocols import AuditWriterProtocol

    _CORE_AUDIT_AVAILABLE = True
except ImportError:
    _CORE_AUDIT_AVAILABLE = False


HOTFIX_PREFIXES: tuple[str, ...] = ("[HOTFIX]", "[EMERGENCY]", "[HOTFIX]", "[EMERGENCY]")


SUPPRESSION_TTL_HOURS: int = 72


@dataclass
class HotfixAuditEntry:
    entry_id: uuid.UUID

    commit_hash: str

    module_ids: list[str]

    dimensions: list[str]

    owner_ack: str = ""

    timestamp: datetime | None = None

    suppressed_until: datetime | None = None


class HotfixBypass:
    def __init__(self, project_root: str | None = None) -> None:
        if project_root is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        self._project_root = project_root

        self._audit_dir = os.path.join(project_root, "data", "drift_audit")

        os.makedirs(self._audit_dir, exist_ok=True)

        self._audit_log_path = os.path.join(self._audit_dir, "hotfix_audit.jsonl")

        self._active_hotfixes: dict[str, HotfixAuditEntry] = {}

        self._core_writer = None

        if _CORE_AUDIT_AVAILABLE:
            try:
                import importlib as _importlib

                _CoreAuditWriter = _importlib.import_module("zephyr.governance.audit_trail.writer").AuditWriter
                self._core_writer = _CoreAuditWriter()

            except Exception as e:
                logger.warning("suppressed error in drift_hotfix_bypass", exc_info=True)

    def is_hotfix_commit(self, commit_message: str) -> bool:
        upper = commit_message.strip().upper()

        for prefix in HOTFIX_PREFIXES:
            if upper.startswith(prefix):
                return True

        return False

    def process_hotfix(
        self,
        commit_hash: str,
        commit_message: str,
        module_ids: list[str],
        affected_dimensions: list[str],
        owner_ack: str = "",
    ) -> HotfixAuditEntry:
        now = datetime.now(UTC)

        entry = HotfixAuditEntry(
            entry_id=uuid.uuid4(),
            commit_hash=commit_hash,
            module_ids=module_ids,
            dimensions=affected_dimensions,
            owner_ack=owner_ack,
            timestamp=now,
            suppressed_until=now + timedelta(hours=SUPPRESSION_TTL_HOURS),
        )

        self._active_hotfixes[commit_hash] = entry

        self._write_audit_log(entry)

        return entry

    def check_expired_hotfixes(self) -> list[str]:
        now = datetime.now(UTC)

        expired: list[str] = []

        for ch, entry in list(self._active_hotfixes.items()):
            if entry.suppressed_until and now >= entry.suppressed_until:
                expired.append(ch)

                del self._active_hotfixes[ch]

        return expired

    def is_suppressed(self, commit_hash: str) -> bool:
        entry = self._active_hotfixes.get(commit_hash)

        if entry is None:
            return False

        if entry.suppressed_until and datetime.now(UTC) < entry.suppressed_until:
            return True

        return False

    def _write_audit_log(self, entry: HotfixAuditEntry) -> None:
        record = {
            "entry_id": str(entry.entry_id),
            "commit_hash": entry.commit_hash,
            "module_ids": entry.module_ids,
            "dimensions": entry.dimensions,
            "owner_ack": entry.owner_ack,
            "timestamp": entry.timestamp.isoformat() if entry.timestamp else "",
            "suppressed_until": entry.suppressed_until.isoformat() if entry.suppressed_until else "",
        }

        if self._core_writer is not None:
            try:
                core_event = dict(record)

                core_event["event_type"] = "drift_hotfix_bypass"

                core_event["agent_id"] = entry.owner_ack or "hotfix_bypass"

                core_event["session_id"] = str(entry.entry_id)

                core_event["target_path"] = entry.commit_hash

                core_event["status"] = "suppressed"

                self._core_writer.write(core_event)

                return

            except Exception as e:
                logger.warning("suppressed error in drift_hotfix_bypass", exc_info=True)

        with open(self._audit_log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

            fh.flush()
