# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.governance.audit_trail.provenance_tracker
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-GOV_provenance_tracker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel


class ProvenanceRecord(BaseModel):
    module_id: str
    source_section: str
    agent_session_id: str
    generated_at: str


def generate_provenance(
    module_id: str,
    source_section: str,
    agent_session_id: str = "session-20260507-005",
) -> ProvenanceRecord:
    return ProvenanceRecord(
        module_id=module_id,
        source_section=source_section,
        agent_session_id=agent_session_id,
        generated_at=datetime.now(UTC).isoformat(),
    )


def embed_provenance(target_dict: dict[str, object], record: ProvenanceRecord) -> dict[str, object]:
    target_dict["__provenance__"] = {
        "module_id": record.module_id,
        "source_section": record.source_section,
        "agent_session_id": record.agent_session_id,
        "generated_at": record.generated_at,
    }
    return target_dict


def extract_provenance(obj: object) -> ProvenanceRecord | None:
    prov = getattr(obj, "_zephyr_provenance", None) or getattr(obj, "__provenance__", None)
    if isinstance(prov, dict):
        return ProvenanceRecord(
            module_id=str(prov.get("module_id", "UNKNOWN")),
            source_section=str(prov.get("source_section", "UNKNOWN")),
            agent_session_id=str(prov.get("agent_session_id", "UNKNOWN")),
            generated_at=str(prov.get("generated_at", "")),
        )
    return None


def is_session_owned(prov: ProvenanceRecord, session_id: str) -> bool:
    return prov.agent_session_id == session_id


def provenance_key(prov: ProvenanceRecord) -> str:
    return f"{prov.module_id}/{prov.source_section}"
