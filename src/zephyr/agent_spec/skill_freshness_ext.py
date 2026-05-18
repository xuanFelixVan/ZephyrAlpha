# [BLUEPRINT] MOD-INF-019 | 03_modules/l01_infrastructure/agent-spec/blueprint.md | §3.2
# [MODULE] zephyr.agent_spec.skill_freshness_ext
# [INVARIANTS] scan_all and auto_deprecate must not be inlined into skill_freshness.py — they get lost on file overwrite
# [MODIFY-GUARD] skill_freshness.py, skill_lifecycle.py
# [CONSUMERS] auto_runtime_core.py (CircadianScheduler), event_bus subscribers
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""
MOD-INF-019: Agent Spec — Skill Freshness Extensions

Standalone module for scan_all() and auto_deprecate() that were
previously inlined into skill_freshness.py and skill_lifecycle.py
but kept getting lost on file overwrites.

This module is the canonical location. Import from here.
"""
from __future__ import annotations

from typing import Dict, Any

from zephyr.agent_spec.skill_freshness import FreshnessDecayModel
from zephyr.agent_spec.skill_lifecycle import SkillLifecycle
from zephyr.agent_spec.skill_model import SkillStatus


def scan_all_freshness(model: FreshnessDecayModel | None = None) -> Dict[str, Any]:
    if model is None:
        model = FreshnessDecayModel()
    data = model._load()
    warnings: list = []
    criticals: list = []
    healthy: list = []
    for skill_id, entry in data.items():
        score = model.compute(entry.get("last_validated", ""))
        info = {"skill_id": skill_id, "freshness_score": round(score, 1)}
        if score <= model.CRITICAL_THRESHOLD:
            criticals.append(info)
        elif score <= model.WARNING_THRESHOLD:
            warnings.append(info)
        else:
            healthy.append(info)
    try:
        from zephyr.shared.event_bus import bus, EventPriority
        if criticals:
            bus.emit("skill.freshness_critical", {"criticals": criticals}, priority=EventPriority.HIGH)
        if warnings:
            bus.emit("skill.freshness_warning", {"warnings": warnings}, priority=EventPriority.NORMAL)
    except Exception:
        pass
    return {"total_scanned": len(data), "healthy": len(healthy),
            "warnings": len(warnings), "criticals": len(criticals)}


def auto_deprecate_skill(lifecycle: SkillLifecycle, skill_id: str,
                         freshness_score: float, reason: str = "") -> Dict[str, Any]:
    current = lifecycle.current_status(skill_id)
    if current != SkillStatus.ACTIVE.value:
        return {"action": "skipped", "skill_id": skill_id, "current_status": current, "reason": "not active"}
    if freshness_score <= 10.0:
        result = lifecycle.transition(skill_id, SkillStatus.DEPRECATED.value,
                                      reason=reason or f"freshness_score={freshness_score:.1f} <= critical")
        try:
            from zephyr.shared.event_bus import bus, EventPriority
            bus.emit("skill.deprecated", {"skill_id": skill_id, "freshness_score": freshness_score},
                     priority=EventPriority.HIGH)
        except Exception:
            pass
        return result
    if freshness_score <= 30.0:
        try:
            from zephyr.shared.event_bus import bus, EventPriority
            bus.emit("skill.freshness_warning", {"skill_id": skill_id, "freshness_score": freshness_score},
                     priority=EventPriority.NORMAL)
        except Exception:
            pass
        return {"action": "warning_issued", "skill_id": skill_id, "freshness_score": freshness_score}
    return {"action": "no_action", "skill_id": skill_id, "freshness_score": freshness_score}


def should_load_onboarding(loader, session_id: str, max_rounds: int = 3) -> bool:
    conv_rounds = getattr(loader, "_conversation_round", {})
    return conv_rounds.get(session_id, 0) < max_rounds


def increment_round(loader, session_id: str) -> int:
    if not hasattr(loader, "_conversation_round"):
        loader._conversation_round = {}
    loader._conversation_round[session_id] = loader._conversation_round.get(session_id, 0) + 1
    return loader._conversation_round[session_id]


__all__ = ["scan_all_freshness", "auto_deprecate_skill", "should_load_onboarding", "increment_round"]
