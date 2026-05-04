# AI-generated: T-3-14 Evolution Engine (ADR-0034)
"""
EvolutionEngine · 自进化闭环引擎（三层反馈 + 五类进化信号）
============================================================

Task ID     : T-3-14 (A24)
ADR         : ADR-0034（自进化闭环边界 + Owner 审批门禁）
Depends     : T-3-13（ADR-0034）、T-2-29（C54 feedback_collector）
safety_level: H

核心职责
--------

1. **evolve() 纯函数签名**
   - 输入：``FeedbackCollector`` 采样窗口 + 当前系统状态（只读）
   - 输出：``EvolutionProposal`` 列表（Pydantic 契约）
   - 副作用：仅当 ``dry_run=False`` 且 ``owner_approved=True`` 时调用
     注入的 ``apply_fn``；其他情形 **只读**（dry_run 风格）。

2. **EvolutionProposal Pydantic 契约**
   - 记录信号类型、严重度、证据、推荐动作、估算影响、审批状态。

3. **三层反馈闭环**
   - **L1 任务级**：任意 score ≤ 2 的 FeedbackEntry 立即产生 ``acceptance_drift``
     或 ``high_retry_rate`` 信号。
   - **L2 Pattern 级**：tag 或 comment 的失败模式出现 ≥ 3 次聚合，
     产生 pattern-level 信号。
   - **L3 架构级**：MoM/QoQ 漂移（平均分 / 负面率变化）触发 ADR 重审信号。

4. **五类进化信号处理**
   - ``high_retry_rate`` — 重试标签比例超阈值
   - ``low_knowledge_hit`` — "needs-review" / "stale" 等标签聚集
   - ``context_overflow`` — "context-overflow" / "too-long" 聚集
   - ``dependency_bottleneck`` — "blocked" / "dependency" 聚集
   - ``acceptance_drift`` — 平均分跨窗口下移或 low-score 比例升高

5. **与 feedback_collector 集成**
   - 数据读取契约：仅使用 ``get_entries()`` + ``summarize()``；
     不修改采集器状态。
   - ``on_low_score`` hook：任何 entry.score ≤ 2 时调用注入的回调
     （默认 no-op），便于实时回路。

零外部依赖：仅 ``pydantic`` + 标准库；不 import 任何 LLM / DB。
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field

from zephyr.feedback_loop.feedback_collector import FeedbackCollector, FeedbackEntry
from zephyr.shared.schemas import BASE_CONFIG
from zephyr.shared.time_utils import default_now

__all__ = [
    "EvolutionSignal",
    "Severity",
    "FeedbackLayer",
    "EvolutionProposal",
    "EvolutionReport",
    "LowScoreHook",
    "ApplyFn",
    "evolve",
    "EvolutionEngine",
    "DEFAULT_THRESHOLDS",
]


# ---------------------------------------------------------------------------
# 枚举与阈值常量
# ---------------------------------------------------------------------------


class EvolutionSignal(str, Enum):
    """五类进化信号（ADR-0034 §3.1）。"""

    HIGH_RETRY_RATE = "high_retry_rate"
    LOW_KNOWLEDGE_HIT = "low_knowledge_hit"
    CONTEXT_OVERFLOW = "context_overflow"
    DEPENDENCY_BOTTLENECK = "dependency_bottleneck"
    ACCEPTANCE_DRIFT = "acceptance_drift"


class Severity(str, Enum):
    """严重度（与 safety_level 对齐）。"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackLayer(str, Enum):
    """三层反馈闭环（ADR-0034 §3.2）。"""

    L1_TASK = "L1_task"
    L2_PATTERN = "L2_pattern"
    L3_ARCHITECTURE = "L3_architecture"


# 信号 → 触发标签的映射（可注入覆盖）
DEFAULT_SIGNAL_TAG_MAP: dict[EvolutionSignal, frozenset[str]] = {
    EvolutionSignal.HIGH_RETRY_RATE: frozenset({"retry", "retried", "flaky"}),
    EvolutionSignal.LOW_KNOWLEDGE_HIT: frozenset({"needs-review", "stale", "missing-ke", "low-knowledge"}),
    EvolutionSignal.CONTEXT_OVERFLOW: frozenset({"context-overflow", "too-long", "truncated"}),
    EvolutionSignal.DEPENDENCY_BOTTLENECK: frozenset({"blocked", "dependency", "bottleneck", "waiting"}),
    EvolutionSignal.ACCEPTANCE_DRIFT: frozenset({"low-quality", "rejected", "not-accepted"}),
}

DEFAULT_THRESHOLDS: dict[str, float] = {
    # L1：任务级 low-score 绝对阈值（score ≤ 2 即触发实时回路）
    "low_score_threshold": 2.0,
    # L2：Pattern 级聚合阈值（同一信号 ≥ 3 次）
    "pattern_min_count": 3,
    # L3：架构级漂移阈值
    "mom_score_drop": 0.5,  # 月环比平均分下滑 ≥ 0.5
    "mom_low_score_rate_rise": 0.15,  # 月环比 low-score 比例上升 ≥ 15%
    # signal 比例触发（用于 high_retry_rate 等）
    "ratio_threshold": 0.30,
}


# ---------------------------------------------------------------------------
# Pydantic 契约
# ---------------------------------------------------------------------------


class EvolutionProposal(BaseModel):
    """单个进化提案。Owner 审批门禁的最小原子单位。"""

    model_config = BASE_CONFIG

    proposal_id: str = Field(min_length=1, description="Proposal ID，如 EP-0001")
    signal: EvolutionSignal = Field(description="触发该提案的进化信号")
    layer: FeedbackLayer = Field(description="反馈层 L1/L2/L3")
    severity: Severity = Field(description="严重度")
    title: str = Field(min_length=1, max_length=200, description="提案标题")
    rationale: str = Field(description="触发条件与证据的文字解释")
    evidence: list[str] = Field(default_factory=list, description="证据片段（entry_id / 标签等）")
    affected_task_ids: list[str] = Field(default_factory=list, description="受影响的 task_id")
    recommended_action: str = Field(description="建议的整改动作")
    estimated_impact: str = Field(default="", description="预期影响的文字描述")
    requires_owner_approval: bool = Field(default=True, description="是否需要 Owner 审批")
    owner_approved: bool = Field(default=False, description="是否已通过 Owner 审批")
    dry_run: bool = Field(default=True, description="是否 dry-run（不真正 apply）")
    created_at: datetime = Field(description="创建时间 UTC")


class EvolutionReport(BaseModel):
    """一次 evolve() 的汇总报告。"""

    model_config = BASE_CONFIG

    window_entry_count: int = Field(ge=0, description="本次采样窗口内反馈条数")
    proposals: list[EvolutionProposal] = Field(default_factory=list)
    l1_triggered: int = Field(default=0, ge=0)
    l2_triggered: int = Field(default=0, ge=0)
    l3_triggered: int = Field(default=0, ge=0)
    applied_count: int = Field(default=0, ge=0, description="实际 apply 的提案数")
    dry_run: bool = Field(default=True)
    generated_at: datetime = Field(description="生成时间 UTC")


# ---------------------------------------------------------------------------
# 回调类型
# ---------------------------------------------------------------------------


LowScoreHook = Callable[[FeedbackEntry], None]
"""任务级 low-score 实时回路：score ≤ 阈值的 entry 会被喂给该回调。"""

ApplyFn = Callable[[EvolutionProposal], bool]
"""生产环境的 apply 动作：成功返回 True，否则 False。"""


# ---------------------------------------------------------------------------
# EvolutionEngine
# ---------------------------------------------------------------------------


class EvolutionEngine:
    """封装 evolve() 的实例版本，便于注入回调 / 阈值。

    函数入口 ``evolve()`` 也提供无状态版本。

    Parameters
    ----------
    collector : FeedbackCollector
        反馈采集器（只读访问）。
    apply_fn : ApplyFn | None
        生产环境的真实 apply 动作；None 时视同 dry-run。
    on_low_score : LowScoreHook | None
        任务级 low-score 实时回调；默认 no-op。
    signal_tag_map : dict[EvolutionSignal, frozenset[str]] | None
        信号-标签映射，可注入覆盖默认值。
    thresholds : dict[str, float] | None
        阈值字典，缺省字段使用 DEFAULT_THRESHOLDS。
    now : Callable[[], datetime]
        时间源（便于测试）。
    """

    def __init__(
        self,
        collector: FeedbackCollector,
        *,
        apply_fn: ApplyFn | None = None,
        on_low_score: LowScoreHook | None = None,
        signal_tag_map: dict[EvolutionSignal, frozenset[str]] | None = None,
        thresholds: dict[str, float] | None = None,
        now: Callable[[], datetime] = default_now,
    ) -> None:
        self._collector = collector
        self._apply_fn = apply_fn
        self._hook = on_low_score or (lambda _entry: None)
        self._tag_map = signal_tag_map or DEFAULT_SIGNAL_TAG_MAP
        self._thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
        self._now = now
        self._proposal_seq = 1

    # ---- public entry ------------------------------------------------

    def evolve(
        self,
        *,
        dry_run: bool = True,
        owner_approved: bool = False,
        task_id: str | None = None,
        baseline_avg_score: float | None = None,
        baseline_low_score_rate: float | None = None,
    ) -> EvolutionReport:
        """生成 + 可选应用进化提案。

        Parameters
        ----------
        dry_run : bool
            True 时永不调用 apply_fn，不论 owner_approved。
        owner_approved : bool
            Owner 审批门禁；dry_run=False 且 owner_approved=True 才会真实应用。
        task_id : str | None
            只分析某一 task_id；None 时使用全部窗口。
        baseline_avg_score : float | None
            上一窗口的平均分；用于 L3 MoM 漂移检测。None 表示跳过 L3 drift。
        baseline_low_score_rate : float | None
            上一窗口的 low-score 比例；同上。

        Returns
        -------
        EvolutionReport
        """
        entries = self._collector.get_entries(task_id)
        report = EvolutionReport(
            window_entry_count=len(entries),
            proposals=[],
            dry_run=dry_run,
            generated_at=self._now(),
        )

        if not entries:
            return report

        # L1 任务级：实时回路
        l1_props = self._layer1_task(entries)
        report.l1_triggered = len(l1_props)

        # L2 Pattern 级：聚合
        l2_props = self._layer2_pattern(entries)
        report.l2_triggered = len(l2_props)

        # L3 架构级：MoM 漂移
        l3_props = self._layer3_drift(entries, baseline_avg_score, baseline_low_score_rate)
        report.l3_triggered = len(l3_props)

        proposals = l1_props + l2_props + l3_props
        # 应用 owner_approved 到每个 proposal
        for p in proposals:
            p.owner_approved = owner_approved
            p.dry_run = dry_run

        # 真实 apply（仅非 dry-run + 已审批 + 注入 apply_fn 时）
        applied = 0
        if not dry_run and owner_approved and self._apply_fn is not None:
            for p in proposals:
                try:
                    if self._apply_fn(p):
                        applied += 1
                except Exception:  # — apply 错误必须被收敛
                    continue

        report.proposals = proposals
        report.applied_count = applied
        return report

    # ---- layer 1 -----------------------------------------------------

    def _layer1_task(self, entries: list[FeedbackEntry]) -> list[EvolutionProposal]:
        """对每条 score ≤ 阈值的 entry 触发 hook，并聚合成 acceptance_drift 提案。"""
        low_thresh = self._thresholds["low_score_threshold"]
        low_entries = [e for e in entries if e.score <= low_thresh]
        for entry in low_entries:
            self._hook(entry)
        if not low_entries:
            return []
        evidence = [f"{e.entry_id}:{e.task_id}:score={e.score}" for e in low_entries[:10]]
        tasks = sorted({e.task_id for e in low_entries})
        severity = Severity.HIGH if len(low_entries) >= 3 else Severity.MEDIUM
        return [
            self._mk_proposal(
                signal=EvolutionSignal.ACCEPTANCE_DRIFT,
                layer=FeedbackLayer.L1_TASK,
                severity=severity,
                title=f"L1 task-level low-score alert ({len(low_entries)} entries)",
                rationale=(
                    f"检测到 {len(low_entries)} 条 score ≤ {low_thresh} 的反馈，"
                    "应立刻触发任务级回路（重跑 / 人工复核）。"
                ),
                evidence=evidence,
                affected_task_ids=tasks,
                recommended_action="对受影响 task 执行重试 / 人工介入，并补充缺失的 KE。",
                estimated_impact="降低未来同类任务的 low-score 率。",
            )
        ]

    # ---- layer 2 -----------------------------------------------------

    def _layer2_pattern(self, entries: list[FeedbackEntry]) -> list[EvolutionProposal]:
        """按 tag 聚合，≥ pattern_min_count 才升级为 Pattern 级提案。"""
        min_count = int(self._thresholds["pattern_min_count"])
        ratio_thresh = self._thresholds["ratio_threshold"]

        tag_to_entries: dict[str, list[FeedbackEntry]] = {}
        for e in entries:
            for tag in e.tags:
                tag_to_entries.setdefault(tag.lower(), []).append(e)

        proposals: list[EvolutionProposal] = []
        for signal, tags in self._tag_map.items():
            matched: list[FeedbackEntry] = []
            hit_tags: list[str] = []
            for tag in tags:
                hits = tag_to_entries.get(tag.lower(), [])
                if hits:
                    matched.extend(hits)
                    hit_tags.append(tag)
            if len(matched) < min_count:
                continue
            # 去重
            unique = {e.entry_id: e for e in matched}
            matched = list(unique.values())
            ratio = len(matched) / max(1, len(entries))
            severity = self._pattern_severity(signal, ratio, ratio_thresh)
            tasks = sorted({e.task_id for e in matched})
            proposals.append(
                self._mk_proposal(
                    signal=signal,
                    layer=FeedbackLayer.L2_PATTERN,
                    severity=severity,
                    title=f"L2 pattern: {signal.value} ×{len(matched)}",
                    rationale=(
                        f"标签 {hit_tags} 在 {len(entries)} 条反馈中共命中 {len(matched)} 次"
                        f"（比例 {ratio:.0%}），达到 pattern 阈值。"
                    ),
                    evidence=[f"{e.entry_id}:tags={e.tags}" for e in matched[:10]],
                    affected_task_ids=tasks,
                    recommended_action=_DEFAULT_ACTIONS[signal],
                    estimated_impact=_DEFAULT_IMPACTS[signal],
                )
            )
        return proposals

    # ---- layer 3 -----------------------------------------------------

    def _layer3_drift(
        self,
        entries: list[FeedbackEntry],
        baseline_avg: float | None,
        baseline_low_rate: float | None,
    ) -> list[EvolutionProposal]:
        """MoM 漂移触发 ADR 重审。无 baseline 时跳过。"""
        if baseline_avg is None and baseline_low_rate is None:
            return []

        scores = [e.score for e in entries]
        cur_avg = sum(scores) / len(scores)
        low_thresh = self._thresholds["low_score_threshold"]
        cur_low_rate = sum(1 for s in scores if s <= low_thresh) / len(scores)

        rationales: list[str] = []
        triggered = False

        if baseline_avg is not None:
            delta = baseline_avg - cur_avg
            if delta >= self._thresholds["mom_score_drop"]:
                rationales.append(f"平均分 {baseline_avg:.2f} → {cur_avg:.2f}（下滑 {delta:.2f}）")
                triggered = True

        if baseline_low_rate is not None:
            delta_r = cur_low_rate - baseline_low_rate
            if delta_r >= self._thresholds["mom_low_score_rate_rise"]:
                rationales.append(
                    f"low-score 比例 {baseline_low_rate:.0%} → {cur_low_rate:.0%}" f"（上升 {delta_r:.0%}）"
                )
                triggered = True

        if not triggered:
            return []

        severity = Severity.CRITICAL if len(rationales) == 2 else Severity.HIGH
        return [
            self._mk_proposal(
                signal=EvolutionSignal.ACCEPTANCE_DRIFT,
                layer=FeedbackLayer.L3_ARCHITECTURE,
                severity=severity,
                title="L3 architecture drift: ADR re-review required",
                rationale="；".join(rationales),
                evidence=[
                    f"window_count={len(entries)}",
                    f"current_avg={cur_avg:.2f}",
                    f"current_low_rate={cur_low_rate:.0%}",
                ],
                affected_task_ids=sorted({e.task_id for e in entries}),
                recommended_action=(
                    "触发 ADR 重审流程（`docs/02_enterprise_architecture/adr/index.md`）"
                    "并冻结新增任务直到架构调整完成。"
                ),
                estimated_impact="预计影响范围：跨 wave 的所有后继任务。",
            )
        ]

    # ---- helpers -----------------------------------------------------

    def _pattern_severity(self, signal: EvolutionSignal, ratio: float, ratio_thresh: float) -> Severity:
        if signal in (EvolutionSignal.CONTEXT_OVERFLOW, EvolutionSignal.DEPENDENCY_BOTTLENECK):
            if ratio >= ratio_thresh * 2:
                return Severity.CRITICAL
            if ratio >= ratio_thresh:
                return Severity.HIGH
            return Severity.MEDIUM
        if ratio >= ratio_thresh:
            return Severity.HIGH
        return Severity.MEDIUM

    def _mk_proposal(
        self,
        *,
        signal: EvolutionSignal,
        layer: FeedbackLayer,
        severity: Severity,
        title: str,
        rationale: str,
        evidence: list[str],
        affected_task_ids: list[str],
        recommended_action: str,
        estimated_impact: str,
    ) -> EvolutionProposal:
        pid = f"EP-{self._proposal_seq:04d}"
        self._proposal_seq += 1
        return EvolutionProposal(
            proposal_id=pid,
            signal=signal,
            layer=layer,
            severity=severity,
            title=title,
            rationale=rationale,
            evidence=evidence,
            affected_task_ids=affected_task_ids,
            recommended_action=recommended_action,
            estimated_impact=estimated_impact,
            requires_owner_approval=True,
            owner_approved=False,
            dry_run=True,
            created_at=self._now(),
        )


# ---------------------------------------------------------------------------
# 默认 action / impact 文本
# ---------------------------------------------------------------------------


_DEFAULT_ACTIONS: dict[EvolutionSignal, str] = {
    EvolutionSignal.HIGH_RETRY_RATE: "排查失败重试根因，考虑引入幂等重试或提高上游稳定性。",
    EvolutionSignal.LOW_KNOWLEDGE_HIT: "补充 KE 条目或提升 knowledge base 检索召回。",
    EvolutionSignal.CONTEXT_OVERFLOW: "压缩 prompt 上下文 / 引入分段摘要 / 增大 token 预算。",
    EvolutionSignal.DEPENDENCY_BOTTLENECK: "审查依赖关系图，拆解阻塞链路或引入并行化。",
    EvolutionSignal.ACCEPTANCE_DRIFT: "走 ADR 重审流程并复盘 low-score 根因。",
}

_DEFAULT_IMPACTS: dict[EvolutionSignal, str] = {
    EvolutionSignal.HIGH_RETRY_RATE: "降低重试率 / 减少算力浪费。",
    EvolutionSignal.LOW_KNOWLEDGE_HIT: "提升 KB 命中率、减少 hallucination 风险。",
    EvolutionSignal.CONTEXT_OVERFLOW: "减少 token 成本 / 提高响应稳定性。",
    EvolutionSignal.DEPENDENCY_BOTTLENECK: "缩短端到端延迟 / 提升吞吐。",
    EvolutionSignal.ACCEPTANCE_DRIFT: "恢复任务验收质量。",
}


# ---------------------------------------------------------------------------
# 纯函数入口
# ---------------------------------------------------------------------------


def evolve(
    collector: FeedbackCollector,
    *,
    dry_run: bool = True,
    owner_approved: bool = False,
    apply_fn: ApplyFn | None = None,
    on_low_score: LowScoreHook | None = None,
    task_id: str | None = None,
    baseline_avg_score: float | None = None,
    baseline_low_score_rate: float | None = None,
    thresholds: dict[str, float] | None = None,
    signal_tag_map: dict[EvolutionSignal, frozenset[str]] | None = None,
    now: Callable[[], datetime] = default_now,
) -> EvolutionReport:
    """无状态入口函数：构造 EvolutionEngine → 调用 evolve()。

    使用场景：批处理脚本 / CI 检查。需要长期状态（proposal_seq）时，
    请实例化 ``EvolutionEngine`` 复用。
    """
    engine = EvolutionEngine(
        collector,
        apply_fn=apply_fn,
        on_low_score=on_low_score,
        signal_tag_map=signal_tag_map,
        thresholds=thresholds,
        now=now,
    )
    return engine.evolve(
        dry_run=dry_run,
        owner_approved=owner_approved,
        task_id=task_id,
        baseline_avg_score=baseline_avg_score,
        baseline_low_score_rate=baseline_low_score_rate,
    )


# 兼容占位：保留 Literal 以便未来在 __all__ 中公开 severity 字符串字面量
_SEV_LITERAL: Literal["low", "medium", "high", "critical"] = "low"
