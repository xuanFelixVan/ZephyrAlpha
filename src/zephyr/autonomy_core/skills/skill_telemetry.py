# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_telemetry
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
MOD-INF-019: Agent Spec — Skill Telemetry
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill Telemetry——使用遥测采集与聚合分析.
"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class SkillTelemetry:
    """Skill Telemetry——使用遥测采集与聚合分析."""

    _TELEMETRY_LOG = Path("_journals/skill_telemetry.jsonl")
    _MAX_EVENTS = 500

    def __init__(self):
        self._events: list[dict[str, Any]] = []

    def record(self, skill_id: str, event: str, metadata: dict[str, Any] | None = None) -> None:
        entry = {
            "skill_id": skill_id,
            "event": event,
            "metadata": metadata or {},
            "timestamp": datetime.now(UTC).isoformat(),
            "epoch": time.time(),
        }
        self._events.append(entry)
        if len(self._events) > self._MAX_EVENTS:
            self._events = self._events[-self._MAX_EVENTS :]
        self._persist(entry)

    def query(self, skill_id: str, since_hours: int = 24) -> list[dict[str, Any]]:
        cutoff = time.time() - since_hours * 3600
        return [e for e in self._events if e["skill_id"] == skill_id and e["epoch"] > cutoff]

    def stats(self, skill_id: str | None = None) -> dict[str, Any]:
        events = self._events
        if skill_id:
            events = [e for e in events if e["skill_id"] == skill_id]
        if not events:
            return {"total_events": 0}

        event_counts: dict[str, int] = {}
        for e in events:
            evt = e["event"]
            event_counts[evt] = event_counts.get(evt, 0) + 1

        return {
            "total_events": len(events),
            "skill_count": len(set(e["skill_id"] for e in events)),
            "event_breakdown": event_counts,
            "first_event": events[0]["timestamp"],
            "last_event": events[-1]["timestamp"],
        }

    def _persist(self, entry: dict[str, Any]):
        try:
            self._TELEMETRY_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(self._TELEMETRY_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError:
            pass


__all__ = ["SkillTelemetry"]
