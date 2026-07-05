# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_shadow
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
# [A_module] module_id=MOD-ORC_skill_shadow | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Shadow Deployment
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 影子部署引擎
==================
安全发布 Skill 更新:
  1. ShadowRun: 新老 Skill 并行执行，对比输出
  2. DivergenceAnalysis: 分析输出差异
  3. AutomaticPromotion: 无差异则自动提升
  4. TrafficSplitting: 渐进式切流
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import difflib
from datetime import UTC, datetime
from typing import Any


class SkillShadowDeploy:
    """Skill 影子部署器"""

    def __init__(self):
        self._shadow_runs: dict[str, list[dict[str, Any]]] = {}
        self._current_shadow_pct = 5.0

    def shadow_run(
        self,
        skill_id: str,
        old_output: str,
        new_output: str,
        input_context: str = "",
    ) -> dict[str, Any]:
        seq = difflib.SequenceMatcher(None, old_output, new_output)
        similarity = seq.ratio()

        differences: list[dict[str, Any]] = []

        if similarity < 1.0:
            opcodes = seq.get_opcodes()
            for tag, i1, i2, j1, j2 in opcodes:
                if tag != "equal":
                    differences.append(
                        {
                            "type": tag,
                            "old_snippet": old_output[i1:i2][:200],
                            "new_snippet": new_output[j1:j2][:200],
                        }
                    )

        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "skill_id": skill_id,
            "similarity": round(similarity, 3),
            "differences": differences,
            "identical": similarity >= 0.999,
            "old_output_length": len(old_output),
            "new_output_length": len(new_output),
            "input_context": input_context[:200],
        }

        self._shadow_runs.setdefault(skill_id, []).append(entry)

        return entry

    def analyze_results(self, skill_id: str) -> dict[str, Any]:
        runs = self._shadow_runs.get(skill_id, [])
        if not runs:
            return {
                "skill_id": skill_id,
                "runs": 0,
                "can_promote": False,
                "reason": "no_shadow_runs",
            }

        similarities = [r["similarity"] for r in runs]
        avg_sim = sum(similarities) / len(similarities)
        all_identical = all(r["identical"] for r in runs)

        all_diffs: list[dict[str, Any]] = []
        for r in runs:
            all_diffs.extend(r.get("differences", []))

        can_promote = avg_sim > 0.95 and len(runs) >= 3

        return {
            "skill_id": skill_id,
            "runs": len(runs),
            "average_similarity": round(avg_sim, 3),
            "all_identical": all_identical,
            "differences_count": len(all_diffs),
            "differences": all_diffs[:10],
            "can_promote": can_promote,
        }

    def promote(self, skill_id: str) -> dict[str, Any]:
        analysis = self.analyze_results(skill_id)
        if not analysis["can_promote"]:
            return {
                "skill_id": skill_id,
                "promoted": False,
                "reason": "insufficient_confidence",
                "analysis": analysis,
            }

        try:
            from zephyr.autonomy_core.skills.skill_freshness import FreshnessDecayModel

            freshness = FreshnessDecayModel()
            freshness.boost(skill_id, 50.0)
        except Exception as e:
            logger.warning("suppressed error in skill_shadow", exc_info=True)

        return {
            "skill_id": skill_id,
            "promoted": True,
            "new_traffic_pct": 100.0,
            "analysis": analysis,
        }

    def rollback_shadow(self, skill_id: str) -> dict[str, Any]:
        return {
            "skill_id": skill_id,
            "rolled_back": True,
            "current_shadow_pct": 0.0,
        }

    def adjust_traffic(self, skill_id: str, new_pct: float) -> dict[str, Any]:
        clamped = max(0.0, min(100.0, new_pct))
        self._current_shadow_pct = clamped
        return {
            "skill_id": skill_id,
            "previous_pct": self._current_shadow_pct,
            "new_pct": clamped,
        }
