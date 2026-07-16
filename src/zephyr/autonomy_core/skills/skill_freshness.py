# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_freshness
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Freshness Decay
Author: factory-agent
Version: 0.3.0

720h linear decay model
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_HISTORY = Path(__file__).resolve().parent / "_freshness.json"


class FreshnessDecayModel:
    HOURS_TO_ZERO = 720
    WARNING_THRESHOLD = 30.0
    CRITICAL_THRESHOLD = 10.0

    @classmethod
    def compute(cls, validated_at: str) -> float:
        try:
            t = datetime.fromisoformat(validated_at)
            elapsed = (datetime.now(UTC) - t).total_seconds() / 3600
            return max(0.0, 100.0 - (elapsed / cls.HOURS_TO_ZERO) * 100.0)
        except (ValueError, TypeError):
            return 0.0

    def current_state(self, skill_id: str) -> dict[str, Any]:
        data = self._load()
        entry = data.get(skill_id)
        if entry:
            score = self.compute(entry.get("last_validated", ""))
            return {
                "skill_id": skill_id,
                "freshness_score": round(score, 1),
                "last_validated": entry["last_validated"],
                "registered": True,
            }
        return {"skill_id": skill_id, "freshness_score": 50.0, "registered": False}

    def boost(self, skill_id: str, amount: float = 50.0):
        data = self._load()
        data[skill_id] = {"last_validated": datetime.now(UTC).isoformat(), "boost": amount}
        self._save(data)

    def _load(self) -> dict:
        if _HISTORY.exists():
            try:
                return json.loads(_HISTORY.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass
        return {}

    def _save(self, data: dict):
        try:
            _HISTORY.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass
