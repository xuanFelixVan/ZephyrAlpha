# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_learning
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
MOD-INF-019: Agent Spec — Skill Self-Learning Engine
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 自学习引擎
================
从执行历史中学习并自我改进:
  1. PatternExtraction: 从历史输出中提取成功/失败模式
  2. DeltaComputation: 计算与期望输出的偏离量
  3. ConstraintReinforcement: 发现新模式后追加约束
  4. LearningCurve: 追踪学习进步曲线
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class SkillLearning:
    """Skill 自学习引擎"""

    def __init__(self):
        self._learning_history: dict[str, list[dict[str, Any]]] = {}
        self._learned_patterns: dict[str, list[str]] = {}
        self._session_deltas: dict[str, list[float]] = {}

    def add_execution(
        self,
        skill_id: str,
        output: str,
        expected_output: str | None = None,
        success: bool = False,
    ) -> dict[str, Any]:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "output_preview": output[:500],
            "success": success,
            "output_length": len(output),
        }

        if expected_output is not None:
            import difflib

            seq = difflib.SequenceMatcher(None, expected_output, output)
            delta = 1.0 - seq.ratio()
            entry["delta"] = delta
            self._session_deltas.setdefault(skill_id, []).append(delta)

        self._learning_history.setdefault(skill_id, []).append(entry)

        patterns: list[str] = []

        if success and expected_output is not None and entry.get("delta", 1.0) < 0.1:
            patterns.append("high_accuracy_achieved")

        if entry.get("delta", 1.0) > 0.3:
            patterns.append("significant_divergence")

        if output and "error" in output.lower():
            patterns.append("error_in_output")

        if output and "MUST" in output:
            patterns.append("constraint_aware")

        if patterns:
            self._learned_patterns.setdefault(skill_id, []).extend(patterns)
            self._learned_patterns[skill_id] = list(dict.fromkeys(self._learned_patterns[skill_id]))

        return {
            "skill_id": skill_id,
            "recorded": True,
            "patterns_found": patterns,
            "delta": entry.get("delta", 0.0),
        }

    def get_learning(self, skill_id: str) -> dict[str, Any]:
        history = self._learning_history.get(skill_id, [])
        deltas = self._session_deltas.get(skill_id, [])
        patterns = self._learned_patterns.get(skill_id, [])

        if not deltas:
            return {
                "skill_id": skill_id,
                "updated": False,
                "delta": 0.0,
                "executions": len(history),
                "patterns": patterns,
                "trend": "no_data",
            }

        avg_delta = sum(deltas) / len(deltas)

        if len(deltas) >= 3:
            mid = len(deltas) // 2
            old_avg = sum(deltas[:mid]) / mid
            new_avg = sum(deltas[mid:]) / (len(deltas) - mid)
            trend = "improving" if new_avg < old_avg else ("worsening" if new_avg > old_avg else "stable")
        else:
            trend = "insufficient_data"

        updated = trend == "improving" or avg_delta < 0.15

        return {
            "skill_id": skill_id,
            "updated": updated,
            "delta": round(avg_delta, 3),
            "executions": len(history),
            "patterns": patterns,
            "trend": trend,
        }

    def suggest_improvement(self, skill_id: str) -> dict[str, Any]:
        learning = self.get_learning(skill_id)
        patterns = learning.get("patterns", [])
        trend = learning.get("trend", "no_data")

        suggestions: list[str] = []

        if "significant_divergence" in patterns:
            suggestions.append("add_examples_section")

        if "error_in_output" in patterns:
            suggestions.append("add_error_handling_constraint")

        if trend == "worsening":
            suggestions.append("run_freshness_decay_check")
            suggestions.append("trigger_postmortem")

        if trend == "improving":
            suggestions.append("consider_promotion")

        if "constraint_aware" in patterns:
            suggestions.append("constraints_working_well")

        return {
            "skill_id": skill_id,
            "suggestions": suggestions,
            "learning": learning,
        }
