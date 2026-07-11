# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.auto_evolution
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.__init__; zephyr.shared.alert_manager; zephyr.shared.alert_precision_tracker; zephyr.shared.dual_channel_alert; zephyr.shared.error_budget_tracker; zephyr.shared.lifecycle.resource_optimization_engine; zephyr.trading.feedback_loop.collectors.__init__; scripts.governance.d5_architecture.detectors.__init__; zephyr.trading.feedback_loop.diagnosers.__init__; D_FACTOR.FactorSignal 因子信号; zephyr.trading.feedback_loop.verifiers.__init__; D_AUTONOMY_CORE.Evolution Agent 进化Agent; zephyr.governance.drift_detection.forensics_engine; D_AUTONOMY_CORE.对抗性韧性 Adversarial Resilience; D_AUTONOMY_CORE.AWS Agentic AI安全范围矩阵 AWS Agentic AI Security Scope Matrix; architecture_model.layers.b_gates.yaml; zephyr.shared.contracts.protocols; zephyr.trading.feedback_loop.scheduler_act; zephyr.trading.feedback_loop.scheduler_collect_detect; zephyr.trading.feedback_loop.scheduler_health; zephyr.trading.feedback_loop.scheduler_safety
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
# [A_module] module_id=MOD-UNK_auto_evolution | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations

from typing import Final
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from zephyr.trading.feedback_loop.evolution_engine import (
    ApplyFn,
    EvolutionEngine,
    EvolutionProposal,
    EvolutionSignal,
    FeedbackLayer,
    Severity,
)

logger = logging.getLogger(__name__)


class AutoTriggerType(Enum):
    KNOWLEDGE_EXPANSION = "KNOWLEDGE_EXPANSION"
    GATE_TIGHTENING = "GATE_TIGHTENING"
    HALLUCINATION_UPGRADE = "HALLUCINATION_UPGRADE"


@dataclass(frozen=True)
class AutoTrigger:
    trigger_type: AutoTriggerType
    severity: Severity
    rationale: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class AutoEvolutionConfig:
    knowledge_activation_floor: float = 0.30
    compliance_floor: float = 0.90
    hallucination_interception_floor: float = 0.70
    knowledge_consecutive_days: int = 3
    compliance_consecutive_days: int = 2
    history_max_days: int = 90


DEFAULT_AUTO_CONFIG: Final[AutoEvolutionConfig] = AutoEvolutionConfig()


@dataclass
class FitnessSnapshot:
    knowledge_activation: float
    compliance_rate: float
    hallucination_interception: float
    taken_at: datetime


@dataclass
class AutoEvolutionOutcome:
    triggers: list[AutoTrigger] = field(default_factory=list)
    proposals: list[EvolutionProposal] = field(default_factory=list)
    applied_count: int = 0
    blocked_by_safety_gate: int = 0
    history_length: int = 0
    windows_processed: int = 0


@dataclass
class AutoEvolution:
    engine: EvolutionEngine
    interval_seconds: float = 86400.0

    def consolidate(self) -> None:
        """事件驱动入口：由外部事件触发知识合并（替代原 time.wait 轮询）。"""
        try:
            self.engine.consolidate_knowledge()
        except Exception:
            logger.debug("AutoEvolution.consolidate failed", exc_info=True)


@dataclass
class AutoEvolutionEngine:
    evolution_engine: EvolutionEngine
    apply_fn: ApplyFn
    config: AutoEvolutionConfig | None = field(default_factory=AutoEvolutionConfig)
    now: Callable[[], datetime] = field(default_factory=datetime.now)
    history: list[FitnessSnapshot] = field(default_factory=list)
    _consecutive_ka: int = 0
    _consecutive_cr: int = 0

    def __post_init__(self) -> None:
        if self.config is None:
            self.config = AutoEvolutionConfig()

    def record_fitness(self, report: Any) -> FitnessSnapshot:
        ka_val = _extract_metric(report, "METRIC_KNOWLEDGE_ACTIVATION", "knowledge_activation")
        cr_val = _extract_metric(report, "METRIC_COMPLIANCE_RATE", "compliance_rate")
        hi_val = _extract_metric(report, "METRIC_HALLUCINATION_INTERCEPTION", "hallucination_interception")
        now_fn = getattr(self, "_now", None)
        now_dt = now_fn() if now_fn is not None else self.now()

        if self.history:
            last = self.history[-1]
            if last.taken_at.date() == now_dt.date():
                self.history[-1] = FitnessSnapshot(
                    knowledge_activation=ka_val,
                    compliance_rate=cr_val,
                    hallucination_interception=hi_val,
                    taken_at=now_dt,
                )
                return self.history[-1]

        snap = FitnessSnapshot(
            knowledge_activation=ka_val,
            compliance_rate=cr_val,
            hallucination_interception=hi_val,
            taken_at=now_dt,
        )
        self.history.append(snap)

        max_days = self.config.history_max_days
        if len(self.history) > max_days:
            self.history = self.history[-max_days:]

        return snap

    def detect_triggers(self) -> list[AutoTrigger]:
        triggers: list[AutoTrigger] = []
        c = self.config
        rh = self.history
        if not rh:
            return triggers

        # --- hallucination upgrade (immediate) ---
        if rh[-1].hallucination_interception < c.hallucination_interception_floor:
            triggers.append(
                AutoTrigger(
                    trigger_type=AutoTriggerType.HALLUCINATION_UPGRADE,
                    severity=Severity.CRITICAL,
                    rationale=f"Hallucination interception {rh[-1].hallucination_interception:.2f} < floor {c.hallucination_interception_floor}",
                    evidence=[f"hallucination_interception={rh[-1].hallucination_interception:.2f}"],
                )
            )

        # --- knowledge expansion (consecutive days) ---
        ka_streak = _count_consecutive_below(rh, lambda s: s.knowledge_activation, c.knowledge_activation_floor)
        if ka_streak >= c.knowledge_consecutive_days:
            triggers.append(
                AutoTrigger(
                    trigger_type=AutoTriggerType.KNOWLEDGE_EXPANSION,
                    severity=Severity.HIGH,
                    rationale=f"Knowledge activation < {c.knowledge_activation_floor} for {ka_streak} consecutive days",
                    evidence=[f"day_{i}: ka={rh[-(ka_streak - i)].knowledge_activation:.2f}" for i in range(ka_streak)],
                )
            )

        # --- gate tightening (consecutive days) ---
        cr_streak = _count_consecutive_below(rh, lambda s: s.compliance_rate, c.compliance_floor)
        if cr_streak >= c.compliance_consecutive_days:
            triggers.append(
                AutoTrigger(
                    trigger_type=AutoTriggerType.GATE_TIGHTENING,
                    severity=Severity.HIGH,
                    rationale=f"Compliance rate < {c.compliance_floor} for {cr_streak} consecutive days",
                    evidence=[f"day_{i}: cr={rh[-(cr_streak - i)].compliance_rate:.2f}" for i in range(cr_streak)],
                )
            )

        return triggers

    def run_auto_cycle(
        self,
        *,
        fitness_report: Any = None,
        owner_approved_high: bool = False,
        apply_evolution_proposals: bool = True,
    ) -> AutoEvolutionOutcome:
        outcome = AutoEvolutionOutcome()

        if fitness_report is not None:
            self.record_fitness(fitness_report)
        outcome.history_length = len(self.history)

        triggers = self.detect_triggers()
        outcome.triggers = triggers

        if apply_evolution_proposals and self.evolution_engine._collector:
            evo_report = self.evolution_engine.evolve(
                dry_run=False,
                owner_approved=False,
            )
            for p in evo_report.proposals:
                outcome.proposals.append(p)
                if p.dry_run:
                    continue
                if p.requires_owner_approval and not owner_approved_high:
                    continue
                try:
                    if self.apply_fn(p):
                        outcome.applied_count += 1
                except Exception as e:
                    logger.warning("suppressed error in auto_evolution", exc_info=True)
            outcome.windows_processed = 1

        blocked = 0
        for t in triggers:
            if t.severity in (Severity.CRITICAL, Severity.HIGH) and not owner_approved_high:
                blocked += 1
                continue
            ae_p = EvolutionProposal(
                proposal_id=f"AE-{t.trigger_type.value}-{self.now().strftime('%Y%m%d-%H%M%S')}",
                signal=EvolutionSignal.ACCEPTANCE_DRIFT,
                layer=FeedbackLayer.L2_PATTERN,
                severity=t.severity,
                title=f"Auto trigger: {t.trigger_type.value}",
                rationale=t.rationale,
                recommended_action=f"Automated response to {t.trigger_type.value}",
                created_at=self.now(),
                evidence=t.evidence,
                requires_owner_approval=t.severity in (Severity.CRITICAL, Severity.HIGH),
                owner_approved=owner_approved_high,
                dry_run=False,
            )
            outcome.proposals.append(ae_p)
            try:
                if self.apply_fn(ae_p):
                    outcome.applied_count += 1
            except Exception as e:
                logger.warning("suppressed error in auto_evolution", exc_info=True)
        outcome.blocked_by_safety_gate = blocked

        return outcome

    def export_history(self) -> list[dict[str, object]]:
        return [
            {
                "knowledge_activation": s.knowledge_activation,
                "compliance_rate": s.compliance_rate,
                "hallucination_interception": s.hallucination_interception,
                "taken_at": s.taken_at.isoformat(),
            }
            for s in self.history
        ]


def _extract_metric(report: Any, metric_name: str, fallback_attr: str) -> float:
    if hasattr(report, "get_metric"):
        m = report.get_metric(metric_name)
        if m is not None:
            return float(m.value)
    if hasattr(report, fallback_attr):
        return float(getattr(report, fallback_attr))
    if isinstance(report, dict):
        return float(report.get(fallback_attr, 0.0))
    return 0.0


def _count_consecutive_below(
    history: list[FitnessSnapshot],
    getter: Callable[[FitnessSnapshot], float],
    floor: float,
) -> int:
    count = 0
    for snap in reversed(history):
        if getter(snap) < floor:
            count += 1
        else:
            break
    return count
