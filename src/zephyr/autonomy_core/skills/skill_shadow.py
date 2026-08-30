# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_shadow
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: skill_shadow.py
# 层: 算法
# - id: A1
#   name_zh: ① SkillShadowDeploy
#   name_en: SkillShadowDeploy
#   intro: Skill 影子部署器
#   desc: Skill 影子部署器；公共方法（定义序）: current_shadow_pct, shadow_runs, shadow_run, analyze_results, promote, rollback_shadow…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: SkillShadowDeploy
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def current_shadow_pct(self):
        """只读：current_shadow_pct（Stage 4 公共化）。"""
        return self._current_shadow_pct

    @current_shadow_pct.setter
    def current_shadow_pct(self, value):
        """写入：current_shadow_pct（Stage 4 公共化）。"""
        self._current_shadow_pct = value

    @property
    def shadow_runs(self) -> dict[str, list[dict[str, Any]]]:
        """只读：shadow_runs（Stage 4 公共化）。"""
        return self._shadow_runs

    @shadow_runs.setter
    def shadow_runs(self, value):
        """写入：shadow_runs（Stage 4 公共化）。"""
        self._shadow_runs = value

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
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
