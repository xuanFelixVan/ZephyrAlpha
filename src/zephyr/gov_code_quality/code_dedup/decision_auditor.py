# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.decision_auditor
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/decision/test_decision_auditor.py; tests/governance/code_quality/test_code_dedup_engine_red_team.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GCQ_decision_auditor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""决策审计链 — DecisionFingerprint 不可变追加日志."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


class DecisionAuditor:
    """去重决策审计链."""

    _CHAIN: Path = Path("data/cache/decision_audit_chain.ndjson")

    def log_decision(
        self,
        decision_id: str,
        decision_type: str,
        dup_group_id: str,
        outcome: str,
        evidence: dict | None = None,
    ) -> dict:
        """记录决策fingerprint到不可变追加日志."""
        now = datetime.now(UTC).isoformat()
        payload = {
            "decision_id": decision_id,
            "timestamp": now,
            "type": decision_type,
            "dup_group_id": dup_group_id,
            "outcome": outcome,
            "evidence": evidence or {},
        }
        payload_str = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        fingerprint = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()[:16]
        payload["decision_fingerprint"] = fingerprint

        self._CHAIN.parent.mkdir(parents=True, exist_ok=True)
        with open(str(self._CHAIN), "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

        return payload

    def get_chain(self, limit: int = 50) -> list[dict]:
        """读取最后N条决策."""
        if not self._CHAIN.exists():
            return []

        entries: list[dict] = []
        for line in self._CHAIN.read_text(encoding="utf-8").strip().splitlines():
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

        return entries[-limit:]
