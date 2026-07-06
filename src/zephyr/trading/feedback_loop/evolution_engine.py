from typing import Final

# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.evolution_engine
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.security.llm_defense.llm_security.gateway
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
# [A_module] module_id=MOD-UNK_evolution_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging

logger = logging.getLogger(__name__)

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np
from zephyr.shared.utils.async_utils import run_sync  # 5.12.8 修复：统一 async/sync 边界


class Severity(Enum):
    # 5.92.2 修复: 统一日志格式, 返回 value 而非 ClassName.MEMBER
    def __str__(self) -> str:
        return self.value

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FeedbackLayer(Enum):
    # 5.92.2 修复: 统一日志格式, 返回 value 而非 ClassName.MEMBER
    def __str__(self) -> str:
        return self.value

    L1_TASK = "L1_TASK"
    L2_PATTERN = "L2_PATTERN"
    L3_ARCHITECTURE = "L3_ARCHITECTURE"


class EvolutionSignal(Enum):
    # 5.92.2 修复: 统一日志格式, 返回 value 而非 ClassName.MEMBER
    def __str__(self) -> str:
        return self.value

    HIGH_RETRY_RATE = "HIGH_RETRY_RATE"
    ACCEPTANCE_DRIFT = "ACCEPTANCE_DRIFT"
    CONTEXT_OVERFLOW = "CONTEXT_OVERFLOW"
    DEPENDENCY_BOTTLENECK = "DEPENDENCY_BOTTLENECK"
    LOW_KNOWLEDGE_HIT = "LOW_KNOWLEDGE_HIT"


LowScoreHook = Callable[[Any], None]
ApplyFn = Callable[["EvolutionProposal"], bool]

DEFAULT_THRESHOLDS: Final[dict[str, float | int]] = {
    "low_score_threshold": 3,
    "pattern_min_count": 3,
    "context_overflow_threshold": 3,
    "dependency_bottleneck_threshold": 3,
    "low_knowledge_hit_threshold": 3,
    "drift_delta_threshold": 0.5,
    "low_score_rate_rise_threshold": 0.30,
}

_PATTERN_TAG_GROUPS: dict[EvolutionSignal, set[str]] = {
    EvolutionSignal.HIGH_RETRY_RATE: {"retry", "flaky"},
    EvolutionSignal.CONTEXT_OVERFLOW: {"context-overflow", "too-long", "truncated"},
    EvolutionSignal.DEPENDENCY_BOTTLENECK: {"blocked", "dependency", "waiting"},
    EvolutionSignal.LOW_KNOWLEDGE_HIT: {"needs-review", "stale", "missing-ke"},
}


@dataclass(frozen=True)
class EvolutionProposal:
    proposal_id: str
    signal: EvolutionSignal
    layer: FeedbackLayer
    severity: Severity
    title: str
    rationale: str
    recommended_action: str
    created_at: datetime
    evidence: list[str] = field(default_factory=list)
    affected_task_ids: list[str] = field(default_factory=list)
    estimated_impact: str = ""
    requires_owner_approval: bool = False
    owner_approved: bool = False
    dry_run: bool = True


@dataclass
class EvolutionReport:
    window_entry_count: int = 0
    proposals: list[EvolutionProposal] = field(default_factory=list)
    l1_triggered: int = 0
    l2_triggered: int = 0
    l3_triggered: int = 0
    applied_count: int = 0


class EvolutionEngine:
    learning_rate: float = 0.1
    discount_factor: float = 0.9
    epsilon: float = 0.1
    ewc_lambda: float = 0.4
    q_table: dict[str, dict[str, float]]
    fisher_information: dict[str, dict[str, float]]
    optimal_weights: dict[str, dict[str, float]]

    def __init__(
        self,
        collector: Any = None,
        *,
        on_low_score: LowScoreHook | None = None,
        apply_fn: ApplyFn | None = None,
        now: Callable[[], datetime] | None = None,
        thresholds: dict[str, float | int] | None = None,
    ) -> None:
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1
        self.ewc_lambda = 0.4
        self.q_table = {}
        self.fisher_information = {}
        self.optimal_weights = {}
        self._collector = collector
        self._on_low_score = on_low_score
        self._apply_fn = apply_fn
        self._now = now or datetime.now
        self._thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    def _state_key(self, state: str) -> str:
        return state

    def _action_key(self, action: str) -> str:
        return action

    def get_q(self, state: str, action: str) -> float:
        sk = self._state_key(state)
        ak = self._action_key(action)
        if sk not in self.q_table:
            self.q_table[sk] = {}
        return self.q_table[sk].get(ak, 0.0)

    def set_q(self, state: str, action: str, value: float) -> None:
        sk = self._state_key(state)
        ak = self._action_key(action)
        if sk not in self.q_table:
            self.q_table[sk] = {}
        self.q_table[sk][ak] = value

    def update(
        self,
        state: str,
        action: str,
        reward: float,
        next_state: str,
    ) -> None:
        current_q = self.get_q(state, action)
        next_actions = self.q_table.get(self._state_key(next_state), {})
        max_next_q = max(next_actions.values()) if next_actions else 0.0
        td_target = reward + self.discount_factor * max_next_q
        new_q = current_q + self.learning_rate * (td_target - current_q)

        sk = self._state_key(state)
        ak = self._action_key(action)
        if sk in self.fisher_information and ak in self.fisher_information[sk]:
            f_val = self.fisher_information[sk][ak]
            old_q = self.optimal_weights.get(sk, {}).get(ak, current_q)
            penalty = (self.ewc_lambda / 2.0) * f_val * (new_q - old_q) ** 2
            new_q -= self.learning_rate * penalty

        self.set_q(state, action, new_q)

    def select_action(self, state: str, actions: list[str]) -> str:
        if np.random.random() < self.epsilon:
            return np.random.choice(actions)
        q_values = [self.get_q(state, a) for a in actions]
        max_idx = int(np.argmax(q_values))
        return actions[max_idx]

    def consolidate_knowledge(self) -> None:
        for sk, actions in self.q_table.items():
            if sk not in self.optimal_weights:
                self.optimal_weights[sk] = {}
            for ak, val in actions.items():
                self.optimal_weights[sk][ak] = val
                if sk not in self.fisher_information:
                    self.fisher_information[sk] = {}
                self.fisher_information[sk][ak] = 1.0

    # ------------------------------------------------------------------
    # evolve() — full three-layer feedback loop
    # ------------------------------------------------------------------

    def evolve(
        self,
        *,
        baseline_avg_score: float | None = None,
        baseline_low_score_rate: float | None = None,
        dry_run: bool = True,
        owner_approved: bool = False,
        task_id: str | None = None,
    ) -> EvolutionReport:
        collector = self._collector
        if collector is None:
            return EvolutionReport(window_entry_count=0)

        entries = collector.get_entries(task_id=task_id)
        report = EvolutionReport(window_entry_count=len(entries))

        if not entries:
            return report

        scores = [e.score for e in entries]
        all_tags: list[str] = []
        for e in entries:
            all_tags.extend(e.tags)

        # --- L1: low-score aggregation -----------------------------------
        low_scores = [e for e in entries if e.score < self._thresholds["low_score_threshold"]]
        if low_scores:
            for e in low_scores:
                if self._on_low_score is not None:
                    self._on_low_score(e)

            low_ids = list({e.task_id for e in low_scores})
            severity = Severity.HIGH if len(low_ids) >= 3 else Severity.MEDIUM
            report.proposals.append(
                EvolutionProposal(
                    proposal_id=f"EP-L1-{self._now().strftime('%Y%m%d-%H%M%S')}",
                    signal=EvolutionSignal.ACCEPTANCE_DRIFT,
                    layer=FeedbackLayer.L1_TASK,
                    severity=severity,
                    title="Low-score acceptance drift detected",
                    rationale=f"{len(low_ids)} task(s) below score threshold",
                    evidence=[f"Task {tid}: score={e.score}" for tid, e in zip(low_ids, low_scores, strict=False)],
                    affected_task_ids=list(low_ids),
                    recommended_action="Review low-scoring tasks and adjust thresholds",
                    estimated_impact="Reduced pipeline quality",
                    requires_owner_approval=False,
                    owner_approved=owner_approved,
                    dry_run=dry_run,
                    created_at=self._now(),
                )
            )
            report.l1_triggered = 1

        # --- L2: tag-based pattern detection -----------------------------
        tag_counter = Counter(all_tags)
        l2_triggered = 0
        for signal, tag_set in _PATTERN_TAG_GROUPS.items():
            matched_count = sum(tag_counter.get(t, 0) for t in tag_set)
            threshold_key = {
                EvolutionSignal.HIGH_RETRY_RATE: "pattern_min_count",
                EvolutionSignal.CONTEXT_OVERFLOW: "context_overflow_threshold",
                EvolutionSignal.DEPENDENCY_BOTTLENECK: "dependency_bottleneck_threshold",
                EvolutionSignal.LOW_KNOWLEDGE_HIT: "low_knowledge_hit_threshold",
            }.get(signal, "pattern_min_count")
            if matched_count >= self._thresholds[threshold_key]:
                report.proposals.append(
                    EvolutionProposal(
                        proposal_id=f"EP-L2-{signal.value}-{self._now().strftime('%Y%m%d-%H%M%S')}",
                        signal=signal,
                        layer=FeedbackLayer.L2_PATTERN,
                        severity=Severity.HIGH,
                        title=f"Pattern detected: {signal.value}",
                        rationale=f"Aggregated {matched_count} tag(s) matching {signal.value}",
                        evidence=[f"Matched tags: {tag_set} → count={matched_count}"],
                        affected_task_ids=[e.task_id for e in entries if set(e.tags) & tag_set],
                        recommended_action=f"Investigate {signal.value} pattern",
                        estimated_impact="Recurring pattern may affect stability",
                        requires_owner_approval=True,
                        owner_approved=owner_approved,
                        dry_run=dry_run,
                        created_at=self._now(),
                    )
                )
                l2_triggered += 1
        report.l2_triggered = l2_triggered

        # --- L3: architecture-level score drift --------------------------
        if baseline_avg_score is not None:
            current_avg = sum(scores) / len(scores)
            delta = baseline_avg_score - current_avg
            if delta > self._thresholds["drift_delta_threshold"]:
                report.proposals.append(
                    EvolutionProposal(
                        proposal_id=f"EP-L3-{self._now().strftime('%Y%m%d-%H%M%S')}",
                        signal=EvolutionSignal.ACCEPTANCE_DRIFT,
                        layer=FeedbackLayer.L3_ARCHITECTURE,
                        severity=Severity.HIGH if delta > 1.5 else Severity.CRITICAL if delta > 2.0 else Severity.HIGH,
                        title="KBG reaudit triggered by score drift",
                        rationale=f"Average score dropped from {baseline_avg_score} to {current_avg:.2f}",
                        evidence=[f"Delta: {delta:.2f} > threshold {self._thresholds['drift_delta_threshold']}"],
                        recommended_action="Reaudit architecture decision records",
                        estimated_impact="Systemic quality regression possible",
                        requires_owner_approval=True,
                        owner_approved=owner_approved,
                        dry_run=dry_run,
                        created_at=self._now(),
                    )
                )
                report.l3_triggered = 1

        if baseline_low_score_rate is not None:
            low_count = sum(1 for s in scores if s < self._thresholds["low_score_threshold"])
            current_rate = low_count / len(scores) if scores else 0.0
            if current_rate - baseline_low_score_rate > self._thresholds["low_score_rate_rise_threshold"]:
                if not report.l3_triggered:
                    report.proposals.append(
                        EvolutionProposal(
                            proposal_id=f"EP-L3R-{self._now().strftime('%Y%m%d-%H%M%S')}",
                            signal=EvolutionSignal.ACCEPTANCE_DRIFT,
                            layer=FeedbackLayer.L3_ARCHITECTURE,
                            severity=Severity.HIGH,
                            title="Low-score rate rise triggers KBG reaudit",
                            rationale=f"Low-score rate rose from {baseline_low_score_rate:.2f} to {current_rate:.2f}",
                            evidence=[f"Rate delta: {current_rate - baseline_low_score_rate:.2f}"],
                            recommended_action="Reaudit architecture decisions",
                            estimated_impact="Quality regression trend",
                            requires_owner_approval=True,
                            owner_approved=owner_approved,
                            dry_run=dry_run,
                            created_at=self._now(),
                        )
                    )
                    report.l3_triggered = 1

        self._lsg_scan_proposals(report)

        # --- Apply proposals ---------------------------------------------
        if not dry_run and owner_approved and self._apply_fn is not None:
            for p in report.proposals:
                if p.requires_owner_approval and not owner_approved:
                    continue
                try:
                    if self._apply_fn(p):
                        report.applied_count += 1
                except Exception as e:
                    logger.warning("suppressed error in evolution_engine", exc_info=True)

        return report

    def _lsg_scan_proposals(self, report: EvolutionReport) -> None:
        try:
            import asyncio

            from zephyr.security.llm_defense.llm_security.gateway import LSGSecurityGateway

            gateway = LSGSecurityGateway()
            flagged = []
            for p in report.proposals:
                content = f"{p.title} {p.rationale} {p.recommended_action}"
                result = run_sync(gateway.scan_output(content))
                if result.decision.value not in ("allow", "ALLOW"):
                    flagged.append(p.proposal_id)
            if flagged:
                report.proposals = [p for p in report.proposals if p.proposal_id not in flagged]
        except ImportError:
            pass
        except Exception as e:
            logger.warning("suppressed error in evolution_engine", exc_info=True)


def evolve(
    collector: Any,
    *,
    baseline_avg_score: float | None = None,
    baseline_low_score_rate: float | None = None,
    dry_run: bool = True,
    owner_approved: bool = False,
    task_id: str | None = None,
    now: Callable[[], datetime] | None = None,
    thresholds: dict[str, float | int] | None = None,
) -> EvolutionReport:
    engine = EvolutionEngine(collector, now=now, thresholds=thresholds)
    return engine.evolve(
        baseline_avg_score=baseline_avg_score,
        baseline_low_score_rate=baseline_low_score_rate,
        dry_run=dry_run,
        owner_approved=owner_approved,
        task_id=task_id,
    )
