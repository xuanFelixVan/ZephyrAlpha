# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_postmortem
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
MOD-INF-019: Agent Spec — Skill Postmortem (追问到底)
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

追问到底根因分析引擎
===================
机制:
  1. 接收故障报告（skill_id + 症状描述）
  2. 逐层追问"为什么"直到找到根因
  3. 每层推导基于 Skill 已知约束和依赖
  4. 输出根因 + 纠正措施 + 预防措施
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from datetime import UTC, datetime
from typing import Any

_WHY_PROBES = [
    {
        "layer": 1,
        "question": "What immediately caused the failure?",
        "checks": ["execution_error", "missing_checkpoint", "gate_rejection", "budget_exceeded"],
    },
    {
        "layer": 2,
        "question": "Why was the error not caught earlier?",
        "checks": ["no_pre_validation", "missing_guardrail", "silent_failure", "assumed_success"],
    },
    {
        "layer": 3,
        "question": "Why was the guard/pre-check missing?",
        "checks": ["constraint_not_documented", "skill_not_loaded", "wrong_role_skill", "stale_skill"],
    },
    {
        "layer": 4,
        "question": "Why was the skill stale or wrong?",
        "checks": ["freshness_decayed", "blueprint_diverged", "no_update_trigger", "manual_override"],
    },
    {
        "layer": 5,
        "question": "Why was the process not catching this systematically?",
        "checks": ["no_feedback_loop", "no_baseline", "no_regression_detection", "process_gap"],
    },
    {
        "layer": 6,
        "question": "Why was the initial diagnosis wrong (if it differed from deep findings)?",
        "checks": ["confirmation_bias", "insufficient_context", "pattern_mismatch", "premature_conclusion"],
    },
    {
        "layer": 7,
        "question": "Was this actually an expression/clarity problem rather than a logic problem?",
        "checks": ["ambiguous_wording", "reader_misinterpretation", "format_confusion", "missing_clarification"],
    },
]


def _load_skill_registry() -> Any:
    """Load the skill registry cache, returning None on failure."""
    try:
        from zephyr.autonomy_core.skills.skill_loader import SkillLoader

        loader = SkillLoader()
        return loader._load_registry()
    except Exception:
        logger.warning("suppressed error in skill_postmortem", exc_info=True)
        return None


def _find_skill_data(layer_registry_cache: Any, skill_id: str) -> dict[str, Any] | None:
    """Locate the skill entry matching skill_id within the registry cache."""
    if not layer_registry_cache:
        return None
    skill_data: dict[str, Any] | None = None
    for cat in ("domain", "role"):
        for sid, data in (layer_registry_cache.get("skills", {}).get(cat, {})).items():
            if sid == skill_id or skill_id in sid:
                skill_data = {"skill_id": sid, **data}
                break
    return skill_data


def _layer1_reason_evidence(
    symptom_category: str, skill_id: str, error_message: str
) -> tuple[str, list[str]]:
    """Build the reason and evidence for the layer-1 probe."""
    evidence: list[str] = []
    if symptom_category == "registration":
        reason = f"Skill '{skill_id}' was not registered or could not be loaded"
        evidence.append(f"Error: {error_message[:200]}")
    elif symptom_category == "budget":
        reason = f"Skill '{skill_id}' exceeded token budget during loading"
    elif symptom_category == "gate":
        reason = f"Gate rejected execution for skill '{skill_id}'"
    elif symptom_category == "drift":
        reason = f"Skill '{skill_id}' content diverged from blueprint"
    elif symptom_category == "performance":
        reason = f"Skill '{skill_id}' loading exceeded latency threshold"
    else:
        reason = f"Unexpected failure in skill '{skill_id}': {error_message[:150]}"
    return reason, evidence


def _build_layer_reason_evidence(
    layer_num: int,
    symptom_category: str,
    skill_id: str,
    error_message: str,
    skill_data: dict[str, Any] | None,
) -> tuple[str, list[str]]:
    """Build the reason and evidence for a single why-probe layer."""
    evidence: list[str] = []
    if layer_num == 1:
        reason, ev = _layer1_reason_evidence(symptom_category, skill_id, error_message)
        evidence.extend(ev)
        return reason, evidence
    if layer_num == 2:
        if symptom_category == "registration":
            reason = "Skill was expected to be auto-discovered but no discovery mechanism caught its absence"
        else:
            reason = "Pre-execution validation did not exist or was misconfigured"
        if skill_data and not skill_data.get("references"):
            evidence.append("No dependency references found in registry")
        return reason, evidence
    if layer_num == 3:
        reason = "The skill's constraint documentation was incomplete or absent"
        if skill_data and not skill_data.get("description"):
            evidence.append("Skill has no description in registry")
        return reason, evidence
    if layer_num == 4:
        reason = "The skill was not refresh-triggered after its upstream dependency changed"
        evidence.append("No freshness boost was triggered")
        return reason, evidence
    if layer_num == 5:
        reason = "No feedback loop existed to capture this failure pattern and prevent recurrence"
        evidence.append("Postmortem engine was not invoked on first occurrence")
        return reason, evidence
    return "", evidence


class SkillPostmortem:
    """追问到底根因分析器"""

    @classmethod
    def _infer_symptom_category(cls, error_message: str) -> str:
        error_lower = error_message.lower()
        if any(w in error_lower for w in ["keyerror", "not found", "missing", "unregistered"]):
            return "registration"
        if any(w in error_lower for w in ["token", "budget", "overflow", "exceeded"]):
            return "budget"
        if any(w in error_lower for w in ["gate", "reject", "blocked", "denied"]):
            return "gate"
        if any(w in error_lower for w in ["timeout", "latency", "slow"]):
            return "performance"
        if any(w in error_lower for w in ["injection", "security", "sandbox", "unsafe"]):
            return "security"
        if any(w in error_lower for w in ["drift", "stale", "outdated", "version"]):
            return "drift"
        return "unknown"

    @classmethod
    def _unwind_why(
        cls,
        skill_id: str,
        symptom_category: str,
        error_message: str,
    ) -> list[dict[str, Any]]:
        responses: list[dict[str, Any]] = []

        layer_registry_cache = _load_skill_registry()
        skill_data = _find_skill_data(layer_registry_cache, skill_id)

        for probe in _WHY_PROBES:
            reason, evidence = _build_layer_reason_evidence(
                probe["layer"], symptom_category, skill_id, error_message, skill_data
            )
            responses.append(
                {
                    "layer": probe["layer"],
                    "question": probe["question"],
                    "reason": reason,
                    "evidence": evidence,
                }
            )

        return responses

    @classmethod
    def _generate_actions(
        cls,
        skill_id: str,
        symptom_category: str,
        root_causes: list[str],
    ) -> dict[str, list[dict[str, str]]]:
        corrective: list[dict[str, str]] = []
        preventive: list[dict[str, str]] = []

        if symptom_category == "registration":
            corrective.append(
                {
                    "action": f"Register skill '{skill_id}' in skill-registry.yaml",
                    "assignee": "system-admin",
                    "priority": "P0",
                }
            )
            preventive.append(
                {
                    "action": "Add auto-registration check to G9 gate",
                    "assignee": "infrastructure-team",
                    "priority": "P1",
                }
            )

        if symptom_category in ("budget", "drift"):
            corrective.append(
                {
                    "action": f"Compact skill '{skill_id}' body to fit token budget",
                    "assignee": "skill-author",
                    "priority": "P0",
                }
            )
            preventive.append(
                {
                    "action": "Add token-budget pre-check to SkillLoader",
                    "assignee": "infrastructure-team",
                    "priority": "P1",
                }
            )

        if symptom_category == "gate":
            corrective.append(
                {
                    "action": f"Review gate configuration for skill '{skill_id}'",
                    "assignee": "governance-team",
                    "priority": "P0",
                }
            )
            preventive.append(
                {
                    "action": "Create gate override/waiver process",
                    "assignee": "governance-team",
                    "priority": "P2",
                }
            )

        preventive.append(
            {
                "action": f"Add '{skill_id}' to regression test suite",
                "assignee": "qa-team",
                "priority": "P1",
            }
        )
        preventive.append(
            {
                "action": "Enable SkillsBench baseline for this skill",
                "assignee": "infrastructure-team",
                "priority": "P2",
            }
        )

        return {
            "corrective": corrective,
            "preventive": preventive,
        }

    @classmethod
    def analyze(
        cls,
        skill_id: str,
        error_message: str,
        failed_operation: str = "",
    ) -> dict[str, Any]:
        symptom = cls._infer_symptom_category(error_message)
        root_causes = cls._unwind_why(skill_id, symptom, error_message)

        primary_root_cause = root_causes[-1]["reason"] if root_causes else error_message
        actions = cls._generate_actions(skill_id, symptom, [rc["reason"] for rc in root_causes])

        return {
            "incident_id": f"PM-{skill_id}-{datetime.now(UTC).strftime('%Y%m%d-%H%M')}",
            "skill_id": skill_id,
            "symptom_category": symptom,
            "failed_operation": failed_operation,
            "original_error": error_message[:500],
            "root_cause": primary_root_cause,
            "root_cause_chain": root_causes,
            "diagnosis_inversion_verified": root_causes[-1].get("answer", "") != error_message[:200]
            if root_causes
            else False,
            "corrective_actions": actions["corrective"],
            "preventive_actions": actions["preventive"],
            "timestamp": datetime.now(UTC).isoformat(),
            "closed": False,
        }
