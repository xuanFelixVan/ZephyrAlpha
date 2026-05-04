# AI-generated: T-4-01 (A28) 全自动进化引擎
"""
auto_evolution · 全自动进化引擎（T-4-01 / stable）
====================================================

Task ID     : T-4-01 (A28)
依赖        : T-3-14（evolution_engine）+ T-3-16（fitness_functions）+ T-2-29（FeedbackCollector）
safety_level: H

beta 的 :class:`zephyr.feedback_loop.evolution_engine.EvolutionEngine` 只产出
**dry-run 风格的提案**——Owner 审批后才由外部流程手工 apply。stable 在其
之上增加 **全自动闭环**：

1. ``dry_run`` 默认 *OFF*（区别于 beta）
2. **H/CRITICAL 级提案仍强制 Owner 审批** —— 在没有 owner 授权时被阻塞
3. **基于 Fitness 报告的自动触发**：
   - 知识激活率 < 30% **连续 3 天** → ``knowledge_expansion`` 提案
   - 合规率        < 90% **连续 2 天** → ``gate_tightening`` 提案
   - 幻觉拦截率    < 70%（一次即触发）  → ``hallucination_upgrade`` 提案
4. 最终把 AutoTrigger 产生的提案与 :func:`evolution_engine.evolve` 的三层
   反馈提案合并后，统一走 safety gate + apply_fn。

只读契约
--------

- **不修改** :class:`EvolutionEngine` 本身，只做组合（`has-a`）。
- **不写入磁盘**（历史记录保存在内存，调用方可通过 :meth:`export_history`
  自行持久化）。
- **零外部 LLM 依赖** —— 纯函数 / 协议注入。

API 入口
--------

::

    from zephyr.feedback_loop.auto_evolution import AutoEvolutionEngine, AutoTriggerType

    engine = AutoEvolutionEngine(
        evolution_engine=EvolutionEngine(collector, apply_fn=real_apply),
    )
    for fitness_report in daily_reports:
        outcome = engine.run_auto_cycle(
            fitness_report=fitness_report,
            owner_approved_high=True,   # Owner 预授权 H/CRITICAL 级别
        )

    print(outcome.applied_count, outcome.blocked_by_safety_gate)
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from zephyr.feedback_loop.evolution_engine import (
    ApplyFn,
    EvolutionEngine,
    EvolutionProposal,
    EvolutionReport,
    EvolutionSignal,
    FeedbackLayer,
    Severity,
)
from zephyr.feedback_loop.fitness_functions import (
    METRIC_COMPLIANCE_RATE,
    METRIC_HALLUCINATION_INTERCEPTION,
    METRIC_KNOWLEDGE_ACTIVATION,
    FitnessReport,
    MetricStatus,
)
from zephyr.shared.time_utils import default_now

__all__ = [
    "AutoTriggerType",
    "AutoTrigger",
    "AutoEvolutionOutcome",
    "AutoEvolutionConfig",
    "DEFAULT_AUTO_CONFIG",
    "AutoEvolutionEngine",
]

# ---------------------------------------------------------------------------
# 枚举 & 数据模型
# ---------------------------------------------------------------------------

class AutoTriggerType(str, Enum):
    """stable 自动触发类型（与 T-4-01 验收一一对应）。"""

    KNOWLEDGE_EXPANSION = "knowledge_expansion"
    GATE_TIGHTENING = "gate_tightening"
    HALLUCINATION_UPGRADE = "hallucination_upgrade"

# safety_level → 是否必须 Owner 审批
_H_SEVERITIES: frozenset[Severity] = frozenset({Severity.HIGH, Severity.CRITICAL})

@dataclass(frozen=True)
class AutoTrigger:
    """单个已经"成熟"的自动触发事件。"""

    trigger_type: AutoTriggerType
    severity: Severity
    consecutive_days: int
    evidence: tuple[str, ...]
    rationale: str

@dataclass
class AutoEvolutionOutcome:
    """一次 :meth:`AutoEvolutionEngine.run_auto_cycle` 的汇总结果。"""

    fitness_snapshot_date: datetime
    triggers: list[AutoTrigger] = field(default_factory=list)
    evolution_report: EvolutionReport | None = None
    proposals: list[EvolutionProposal] = field(default_factory=list)
    applied_count: int = 0
    blocked_by_safety_gate: int = 0
    history_length: int = 0

@dataclass(frozen=True)
class AutoEvolutionConfig:
    """stable 自动触发阈值（与 phase-4-cards.md T-4-01 一致）。

    - ``knowledge_activation_floor = 0.30``：激活率低于此值算"异常"。
    - ``compliance_floor = 0.90``：合规率低于此值算"异常"。
    - ``hallucination_interception_floor = 0.70``：一次即触发。
    - ``knowledge_consecutive_days = 3``：连续天数门限。
    - ``compliance_consecutive_days = 2``：同上。
    - ``history_max_days = 30``：环形历史长度上限，防止内存膨胀。
    """

    knowledge_activation_floor: float = 0.30
    compliance_floor: float = 0.90
    hallucination_interception_floor: float = 0.70
    knowledge_consecutive_days: int = 3
    compliance_consecutive_days: int = 2
    history_max_days: int = 30

DEFAULT_AUTO_CONFIG: AutoEvolutionConfig = AutoEvolutionConfig()

# ---------------------------------------------------------------------------
# AutoEvolutionEngine
# ---------------------------------------------------------------------------

@dataclass
class _DailySnapshot:
    """一天的 fitness 指标切片。"""

    taken_at: datetime
    knowledge_activation: float | None
    compliance_rate: float | None
    hallucination_interception: float | None

class AutoEvolutionEngine:
    """全自动进化引擎。

    Parameters
    ----------
    evolution_engine : EvolutionEngine
        已经构造好的 beta evolution 引擎（含 apply_fn / feedback collector）。
    apply_fn : ApplyFn | None
        **可选** 覆盖 evolution_engine 的 apply_fn；None 时复用构造参数。
    config : AutoEvolutionConfig | None
        stable 触发阈值，None 时使用 :data:`DEFAULT_AUTO_CONFIG`。
    now : Callable[[], datetime]
        时间注入（测试友好）。
    """

    def __init__(
        self,
        evolution_engine: EvolutionEngine,
        *,
        apply_fn: ApplyFn | None = None,
        config: AutoEvolutionConfig | None = None,
        now: Callable[[], datetime] = default_now,
    ) -> None:
        self._engine = evolution_engine
        self._external_apply = apply_fn
        self._config = config or DEFAULT_AUTO_CONFIG
        self._now = now
        self._history: list[_DailySnapshot] = []
        self._proposal_seq = 1

    # ---- public -----------------------------------------------------

    @property
    def config(self) -> AutoEvolutionConfig:
        return self._config

    @property
    def history(self) -> list[_DailySnapshot]:
        return list(self._history)

    def record_fitness(self, report: FitnessReport) -> _DailySnapshot:
        """把一次 FitnessReport 的关键指标记入历史，返回写入的快照。

        同一 UTC 日的第二次写入会 **覆盖** 当日快照（避免同日计多次）。
        """
        snap = _DailySnapshot(
            taken_at=self._now(),
            knowledge_activation=_read_metric_value(report, METRIC_KNOWLEDGE_ACTIVATION),
            compliance_rate=_read_metric_value(report, METRIC_COMPLIANCE_RATE),
            hallucination_interception=_read_metric_value(report, METRIC_HALLUCINATION_INTERCEPTION),
        )
        self._history = [s for s in self._history if s.taken_at.date() != snap.taken_at.date()]
        self._history.append(snap)
        # ring buffer：历史长度上限
        if len(self._history) > self._config.history_max_days:
            overflow = len(self._history) - self._config.history_max_days
            self._history = self._history[overflow:]
        return snap

    def detect_triggers(self) -> list[AutoTrigger]:
        """基于内部历史检测已经成熟的自动触发。"""
        triggers: list[AutoTrigger] = []

        # 1. 知识激活率：连续 N 天 < floor
        k_days = self._consecutive_tail_violations(
            attr="knowledge_activation",
            floor=self._config.knowledge_activation_floor,
        )
        if k_days >= self._config.knowledge_consecutive_days:
            triggers.append(
                AutoTrigger(
                    trigger_type=AutoTriggerType.KNOWLEDGE_EXPANSION,
                    severity=Severity.HIGH,
                    consecutive_days=k_days,
                    evidence=tuple(
                        f"day-{i}:ka={_fmt_rate(s.knowledge_activation)}" for i, s in enumerate(self._history[-k_days:])
                    ),
                    rationale=(
                        f"知识激活率连续 {k_days} 天 < "
                        f"{self._config.knowledge_activation_floor:.0%}，自动扩充知识库。"
                    ),
                )
            )

        # 2. 合规率：连续 N 天 < floor
        c_days = self._consecutive_tail_violations(
            attr="compliance_rate",
            floor=self._config.compliance_floor,
        )
        if c_days >= self._config.compliance_consecutive_days:
            triggers.append(
                AutoTrigger(
                    trigger_type=AutoTriggerType.GATE_TIGHTENING,
                    severity=Severity.HIGH,
                    consecutive_days=c_days,
                    evidence=tuple(
                        f"day-{i}:cr={_fmt_rate(s.compliance_rate)}" for i, s in enumerate(self._history[-c_days:])
                    ),
                    rationale=(f"合规率连续 {c_days} 天 < " f"{self._config.compliance_floor:.0%}，自动收紧门禁。"),
                )
            )

        # 3. 幻觉拦截率：一次即触发
        if self._history:
            last = self._history[-1]
            if (
                last.hallucination_interception is not None
                and last.hallucination_interception < self._config.hallucination_interception_floor
            ):
                triggers.append(
                    AutoTrigger(
                        trigger_type=AutoTriggerType.HALLUCINATION_UPGRADE,
                        severity=Severity.CRITICAL,
                        consecutive_days=1,
                        evidence=(f"latest:hi={_fmt_rate(last.hallucination_interception)}",),
                        rationale=(
                            f"幻觉拦截率 {last.hallucination_interception:.0%} "
                            f"< {self._config.hallucination_interception_floor:.0%}，"
                            "立即升级 CoVe 配置。"
                        ),
                    )
                )
        return triggers

    def build_trigger_proposals(self, triggers: list[AutoTrigger]) -> list[EvolutionProposal]:
        """把 AutoTrigger 转成 EvolutionProposal（L3 架构层）。"""
        out: list[EvolutionProposal] = []
        for t in triggers:
            out.append(
                EvolutionProposal(
                    proposal_id=self._next_proposal_id(),
                    signal=_trigger_to_signal(t.trigger_type),
                    layer=FeedbackLayer.L3_ARCHITECTURE,
                    severity=t.severity,
                    title=f"auto-trigger: {t.trigger_type.value}",
                    rationale=t.rationale,
                    evidence=list(t.evidence),
                    affected_task_ids=[],
                    recommended_action=_TRIGGER_ACTIONS[t.trigger_type],
                    estimated_impact=_TRIGGER_IMPACTS[t.trigger_type],
                    requires_owner_approval=t.severity in _H_SEVERITIES,
                    owner_approved=False,
                    dry_run=False,
                    created_at=self._now(),
                )
            )
        return out

    def run_auto_cycle(
        self,
        *,
        fitness_report: FitnessReport | None = None,
        owner_approved_high: bool = False,
        apply_evolution_proposals: bool = True,
        baseline_avg_score: float | None = None,
    ) -> AutoEvolutionOutcome:
        """stable 一次完整自动闭环。

        Parameters
        ----------
        fitness_report : FitnessReport | None
            当天的 fitness 报告；None 时只用已有历史检测触发器。
        owner_approved_high : bool
            H/CRITICAL 级提案是否已拿到 Owner 授权；未授权则安全门禁阻塞。
        apply_evolution_proposals : bool
            是否把 evolution_engine 生成的 L1/L2/L3 提案一并 apply。
        baseline_avg_score : float | None
            传给 evolution_engine 用于 L3 drift。

        Returns
        -------
        AutoEvolutionOutcome
        """
        now_dt = self._now()
        if fitness_report is not None:
            self.record_fitness(fitness_report)

        triggers = self.detect_triggers()
        trigger_props = self.build_trigger_proposals(triggers)

        # stable 的关键：evolve() 在 dry_run=True 下只产出提案；apply 由
        # AutoEvolutionEngine **按 severity gate** 执行，确保 H/CRITICAL
        # 必须 owner_approved_high=True 才能真正落地。
        evolution_report: EvolutionReport | None = None
        base_props: list[EvolutionProposal] = []
        if apply_evolution_proposals:
            evolution_report = self._engine.evolve(
                dry_run=True,
                owner_approved=False,
                baseline_avg_score=baseline_avg_score,
            )
            base_props = list(evolution_report.proposals)

        applied = 0
        blocked = 0
        for p in base_props + trigger_props:
            if p.severity in _H_SEVERITIES and not owner_approved_high:
                p.owner_approved = False
                p.dry_run = True
                blocked += 1
                continue
            p.owner_approved = True
            p.dry_run = False
            if self._apply_target() is not None and self._invoke_apply(p):
                applied += 1

        all_props = base_props + trigger_props
        return AutoEvolutionOutcome(
            fitness_snapshot_date=now_dt,
            triggers=triggers,
            evolution_report=evolution_report,
            proposals=all_props,
            applied_count=applied,
            blocked_by_safety_gate=blocked,
            history_length=len(self._history),
        )

    def export_history(self) -> list[dict[str, object]]:
        """导出历史（便于 JSON 持久化）。"""
        return [
            {
                "taken_at": s.taken_at.isoformat(),
                "knowledge_activation": s.knowledge_activation,
                "compliance_rate": s.compliance_rate,
                "hallucination_interception": s.hallucination_interception,
            }
            for s in self._history
        ]

    # ---- internals ----------------------------------------------------

    def _consecutive_tail_violations(self, *, attr: str, floor: float) -> int:
        """从历史尾部向前计数"连续违约"天数。"""
        count = 0
        for snap in reversed(self._history):
            value = getattr(snap, attr)
            if value is None or value >= floor:
                break
            count += 1
        return count

    def _apply_target(self) -> ApplyFn | None:
        """解析真正执行的 apply_fn（外部覆盖优先）。"""
        if self._external_apply is not None:
            return self._external_apply
        return getattr(self._engine, "_apply_fn", None)

    def _invoke_apply(self, proposal: EvolutionProposal) -> bool:
        fn = self._apply_target()
        if fn is None:
            return False
        try:
            return bool(fn(proposal))
        except Exception:  # — apply 错误必须被收敛
            return False

    def _next_proposal_id(self) -> str:
        pid = f"AE-{self._proposal_seq:04d}"
        self._proposal_seq += 1
        return pid

# ---------------------------------------------------------------------------
# 文案映射
# ---------------------------------------------------------------------------

def _trigger_to_signal(trigger: AutoTriggerType) -> EvolutionSignal:
    """把 AutoTriggerType 映射到 EvolutionSignal（L3 层归类）。"""
    return {
        AutoTriggerType.KNOWLEDGE_EXPANSION: EvolutionSignal.LOW_KNOWLEDGE_HIT,
        AutoTriggerType.GATE_TIGHTENING: EvolutionSignal.ACCEPTANCE_DRIFT,
        AutoTriggerType.HALLUCINATION_UPGRADE: EvolutionSignal.ACCEPTANCE_DRIFT,
    }[trigger]

_TRIGGER_ACTIONS: dict[AutoTriggerType, str] = {
    AutoTriggerType.KNOWLEDGE_EXPANSION: ("自动运行 KB 扩充脚本：补充缺失 KE / 重建向量索引 / 同步 SSOT 映射。"),
    AutoTriggerType.GATE_TIGHTENING: ("提升 G1/G2/G4 门禁阈值并锁定高风险目录，直到合规率恢复。"),
    AutoTriggerType.HALLUCINATION_UPGRADE: ("升级 CoVe 验证深度（多模型投票 + 延长验证链），提高幻觉拦截率。"),
}

_TRIGGER_IMPACTS: dict[AutoTriggerType, str] = {
    AutoTriggerType.KNOWLEDGE_EXPANSION: "提升 knowledge_activation_rate，缓解 KE 缺口。",
    AutoTriggerType.GATE_TIGHTENING: "短期合规率提升，长期减少返工。",
    AutoTriggerType.HALLUCINATION_UPGRADE: "hallucination_interception_rate ↑，误判减少。",
}

# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------

def _read_metric_value(report: FitnessReport, metric_name: str) -> float | None:
    metric = report.get_metric(metric_name)
    if metric is None:
        return None
    # FAIL/WARN/PASS 都有 value；我们关心数值，PASS 也会被历史记录以便"恢复"识别
    if metric.status == MetricStatus.PASS and metric_name == METRIC_COMPLIANCE_RATE:
        # 合规率 PASS 直接记录当前值
        return float(metric.value)
    return float(metric.value)

def _fmt_rate(value: float | None) -> str:
    if value is None:
        return "N/A"
    return f"{value:.0%}"
