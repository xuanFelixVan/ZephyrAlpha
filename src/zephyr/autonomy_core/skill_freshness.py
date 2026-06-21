# [A_module] module_id=MOD-ORC_skill_freshness | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md

# [MODULE] zephyr.orchestration.agent_lifecycle.skill_freshness

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — Skill Freshness Decay
Author: factory-agent
Version: 0.3.0

720h linear decay model
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

_HISTORY = Path(__file__).resolve().parent / "_freshness.json"

class FreshnessDecayModel:
    HOURS_TO_ZERO = 720
    WARNING_THRESHOLD = 30.0
    CRITICAL_THRESHOLD = 10.0

    @classmethod
    def compute(cls, validated_at: str) -> float:
        try:
            t = datetime.fromisoformat(validated_at)
            elapsed = (datetime.now(timezone.utc) - t).total_seconds() / 3600
            return max(0.0, 100.0 - (elapsed / cls.HOURS_TO_ZERO) * 100.0)
        except (ValueError, TypeError):
            return 0.0

    def current_state(self, skill_id: str) -> Dict[str, Any]:
        data = self._load()
        entry = data.get(skill_id)
        if entry:
            score = self.compute(entry.get("last_validated", ""))
            return {"skill_id": skill_id, "freshness_score": round(score, 1),
                    "last_validated": entry["last_validated"], "registered": True}
        return {"skill_id": skill_id, "freshness_score": 50.0, "registered": False}

    def boost(self, skill_id: str, amount: float = 50.0):
        data = self._load()
        data[skill_id] = {"last_validated": datetime.now(timezone.utc).isoformat(), "boost": amount}
        self._save(data)

    def _load(self) -> Dict:
        if _HISTORY.exists():
            try:
                return json.loads(_HISTORY.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save(self, data: Dict):
        try:
            _HISTORY.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except IOError:
            pass
