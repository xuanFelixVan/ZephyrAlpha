# [BLUEPRINT] MOD-INF-019 | 03_modules/l01_infrastructure/agent-spec/blueprint.md | §

# [MODULE] zephyr.agent_spec.skill_telemetry

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — Skill Telemetry
Blueprint: docs/03_modules/l01_infrastructure/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill Telemetry——使用遥测采集与聚合分析.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional


class SkillTelemetry:
    """Skill Telemetry——使用遥测采集与聚合分析."""

    _TELEMETRY_LOG = Path("_journals/skill_telemetry.jsonl")
    _MAX_EVENTS = 500

    def __init__(self):
        self._events: List[Dict[str, Any]] = []

    def record(self, skill_id: str, event: str,
               metadata: Optional[Dict[str, Any]] = None) -> None:
        entry = {
            "skill_id": skill_id, "event": event,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "epoch": time.time(),
        }
        self._events.append(entry)
        if len(self._events) > self._MAX_EVENTS:
            self._events = self._events[-self._MAX_EVENTS:]
        self._persist(entry)

    def query(self, skill_id: str,
              since_hours: int = 24) -> List[Dict[str, Any]]:
        cutoff = time.time() - since_hours * 3600
        return [e for e in self._events
                if e["skill_id"] == skill_id and e["epoch"] > cutoff]

    def stats(self, skill_id: Optional[str] = None) -> Dict[str, Any]:
        events = self._events
        if skill_id:
            events = [e for e in events if e["skill_id"] == skill_id]
        if not events:
            return {"total_events": 0}

        event_counts: Dict[str, int] = {}
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

    def _persist(self, entry: Dict[str, Any]):
        try:
            self._TELEMETRY_LOG.parent.mkdir(parents=True, exist_ok=True)
            with open(self._TELEMETRY_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError:
            pass


__all__ = ["SkillTelemetry"]
