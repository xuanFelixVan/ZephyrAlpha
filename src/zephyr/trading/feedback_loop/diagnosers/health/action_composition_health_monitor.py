# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.health.action_composition_health_monitor
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_action_composition_health_monitor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R511: ActionCompositionHealthMonitor
复合动作链整体健康 — 负协同效应检测（整体<部分之和）
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
