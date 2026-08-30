# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §3.2
# [MODULE] zephyr.autonomy_core.skills.skill_freshness_ext
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__; zephyr.shared.event_bus
# [CONSUMERS] auto_runtime_core.py, event_bus subscribers
# [STARTUP] imported
# [MATURITY] production
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: model 参数
#   fields: 参数 model，类型注解 FreshnessDecayModel | None
#   code: skill_freshness_ext.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: lifecycle 参数
#   fields: 参数 lifecycle，类型注解 SkillLifecycle
#   code: skill_freshness_ext.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: skill_id 参数
#   fields: 参数 skill_id，类型注解 str
#   code: skill_freshness_ext.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: freshness_score 参数
#   fields: 参数 freshness_score，类型注解 float
#   code: skill_freshness_ext.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① scan_all_freshness
#   name_en: scan_all_freshness
#   intro: scan_all_freshness(model) 源码 L110-L135
#   desc: 源码 L110-L135
#   inputs: model
#   outputs: dict[str, Any]
# - id: A2
#   name_zh: ② auto_deprecate_skill
#   name_en: auto_deprecate_skill
#   intro: auto_deprecate_skill(lifecycle, skill_id, freshness_score,…
#   desc: 源码 L138-L173
#   inputs: lifecycle skill_id freshness_score reason
#   outputs: dict[str, Any]
# - id: A3
#   name_zh: ③ should_load_onboarding
#   name_en: should_load_onboarding
#   intro: should_load_onboarding(loader, session_id, max_rounds) 源码 L…
#   desc: 源码 L176-L178
#   inputs: loader session_id max_rounds
#   outputs: bool
# - id: A4
#   name_zh: ④ increment_round
#   name_en: increment_round
#   intro: increment_round(loader, session_id) 源码 L181-L185
#   desc: 源码 L181-L185
#   inputs: loader session_id
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: auto_runtime_core.py, event_bus subscribers
# - id: O2
#   name_zh: bool
#   name_en: bool
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: auto_runtime_core.py, event_bus subscribers
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
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
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
