# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §3.2
# [MODULE] zephyr.autonomy_core.skills.skill_freshness_ext
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__; zephyr.shared.event_bus
# [CONSUMERS] auto_runtime_core.py, event_bus subscribers
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] scan_all and auto_deprecate must not be inlined into skill_freshness.py — they get lost on file overwrite
# [MODIFY-GUARD] skill_freshness.py, skill_lifecycle.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
MOD-INF-019: Agent Spec — Skill Freshness Extensions

Standalone module for scan_all() and auto_deprecate() that were
previously inlined into skill_freshness.py and skill_lifecycle.py
but kept getting lost on file overwrites.

This module is the canonical location. Import from here.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from typing import Any

from zephyr.autonomy_core.skills.skill_freshness import FreshnessDecayModel
from zephyr.autonomy_core.skills.skill_lifecycle import SkillLifecycle
from zephyr.autonomy_core.skills.skill_model import SkillStatus


def scan_all_freshness(model: FreshnessDecayModel | None = None) -> dict[str, Any]:
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
        from zephyr.shared.event_bus import EventPriority, bus

        if criticals:
            bus.emit("skill.freshness_critical", {"criticals": criticals}, priority=EventPriority.HIGH)
        if warnings:
            bus.emit("skill.freshness_warning", {"warnings": warnings}, priority=EventPriority.NORMAL)
    except Exception as e:
        logger.warning("suppressed error in skill_freshness_ext", exc_info=True)
    return {"total_scanned": len(data), "healthy": len(healthy), "warnings": len(warnings), "criticals": len(criticals)}


def auto_deprecate_skill(
    lifecycle: SkillLifecycle, skill_id: str, freshness_score: float, reason: str = ""
) -> dict[str, Any]:
    current = lifecycle.current_status(skill_id)
    if current != SkillStatus.ACTIVE.value:
        return {"action": "skipped", "skill_id": skill_id, "current_status": current, "reason": "not active"}
    if freshness_score <= 10.0:
        result = lifecycle.transition(
            skill_id,
            SkillStatus.DEPRECATED.value,
            reason=reason or f"freshness_score={freshness_score:.1f} <= critical",
        )
        try:
            from zephyr.shared.event_bus import EventPriority, bus

            bus.emit(
                "skill.deprecated",
                {"skill_id": skill_id, "freshness_score": freshness_score},
                priority=EventPriority.HIGH,
            )
        except Exception as e:
            logger.warning("suppressed error in skill_freshness_ext", exc_info=True)
        return result
    if freshness_score <= 30.0:
        try:
            from zephyr.shared.event_bus import EventPriority, bus

            bus.emit(
                "skill.freshness_warning",
                {"skill_id": skill_id, "freshness_score": freshness_score},
                priority=EventPriority.NORMAL,
            )
        except Exception as e:
            logger.warning("suppressed error in skill_freshness_ext", exc_info=True)
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


__all__ = ["auto_deprecate_skill", "increment_round", "scan_all_freshness", "should_load_onboarding"]
