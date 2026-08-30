# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.health.action_composition_health_monitor
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R511: ActionCompositionHealthMonitor
复合动作链整体健康 — 负协同效应检测（整体<部分之和）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: action_composition_health_monitor.py
# 层: 算法
# - id: A1
#   name_zh: ① ActionCompositionHealthMonitor
#   name_en: ActionCompositionHealthMonitor
#   intro: class ActionCompositionHealthMonitor 源码 L69-L131
#   desc: 公共方法（定义序）: record_composition_outcome, record_independent_outcome, detect_negative_synergy；源码 L69-L131
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ActionCompositionHealthMonitor
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class ActionComposition:
    composition_id: str
    action_sequence: tuple[str, ...]
    outcomes: list[bool] = field(default_factory=list)
    max_outcomes: int = 50


@dataclass
class IndependentActionStats:
    action_type: str
    outcomes: list[bool] = field(default_factory=list)
    max_outcomes: int = 50


@dataclass
class ActionCompositionHealthMonitor:
    compositions: dict[str, ActionComposition] = field(default_factory=dict)
    independent_stats: dict[str, IndependentActionStats] = field(default_factory=dict)
    negative_synergy_threshold: float = 0.1

    def record_composition_outcome(self, composition_id: str, action_sequence: tuple[str, ...], success: bool) -> None:
        if composition_id not in self.compositions:
            self.compositions[composition_id] = ActionComposition(
                composition_id=composition_id,
                action_sequence=action_sequence,
            )
        comp = self.compositions[composition_id]
        comp.outcomes.append(success)
        if len(comp.outcomes) > comp.max_outcomes:
            comp.outcomes = comp.outcomes[-comp.max_outcomes :]

    def record_independent_outcome(self, action_type: str, success: bool) -> None:
        if action_type not in self.independent_stats:
            self.independent_stats[action_type] = IndependentActionStats(action_type=action_type)
        stats = self.independent_stats[action_type]
        stats.outcomes.append(success)
        if len(stats.outcomes) > stats.max_outcomes:
            stats.outcomes = stats.outcomes[-stats.max_outcomes :]

    def detect_negative_synergy(self) -> dict:
        findings = {}
        for comp_id, comp in self.compositions.items():
            if len(comp.outcomes) < 5:
                continue

            comp_success_rate = sum(comp.outcomes) / len(comp.outcomes)

            independent_rates = []
            for action in comp.action_sequence:
                stats = self.independent_stats.get(action)
                if stats and len(stats.outcomes) >= 5:
                    independent_rates.append(sum(stats.outcomes) / len(stats.outcomes))

            if not independent_rates:
                continue

            expected_rate = min(independent_rates)
            synergy_gap = expected_rate - comp_success_rate

            findings[comp_id] = {
                "composition_success_rate": round(comp_success_rate, 3),
                "min_independent_rate": round(expected_rate, 3),
                "synergy_gap": round(synergy_gap, 3),
                "negative_synergy": synergy_gap > self.negative_synergy_threshold,
                "severity": "critical"
                if synergy_gap > 0.3
                else "warning"
                if synergy_gap > self.negative_synergy_threshold
                else "healthy",
                "sample_count": len(comp.outcomes),
            }

        degraded = {k: v for k, v in findings.items() if v["negative_synergy"]}
        return {
            "degraded_compositions": list(degraded.keys()),
            "findings": findings,
            "total_compositions": len(findings),
        }
