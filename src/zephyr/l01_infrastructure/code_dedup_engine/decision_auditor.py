# [BLUEPRINT] MOD-INF-017 | 03_modules/l01_infrastructure/code-dedup-engine/blueprint.md | §

# [MODULE] zephyr.l01_infrastructure.code_dedup_engine.decision_auditor

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""决策审计链 — DecisionFingerprint 不可变追加日志."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
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
        now = datetime.now(timezone.utc).isoformat()
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
