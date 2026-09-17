# [BLUEPRINT] MOD-PA-030 | docs/03_modules/_domain_portfolio_alloc/regime_meta_allocator/blueprint.md
# [MODULE] zephyr.pf_alloc.allocation_orchestrator
# [DOMAIN] D_PF_ALLOC
# [DEPENDENCIES] zephyr.pf_alloc.allocation_config/inputs/persistence;
#   zephyr.pf_alloc.core.regime_meta_allocator(MOD-PA-007);
#   zephyr.pf_alloc.batched_position_builder(MOD-PA-006);
#   zephyr.position.core.budget_change_handler(MOD-POS-022);
#   zephyr.position.core.strategy_book(MOD-POS-020);
#   zephyr.position.core.position_adjudication_center(MOD-POS-024);
#   zephyr.position.core.single_name_cap_caliber(MOD-POS 三层口径真源);
#   zephyr.position.core.calendar_position_constraint(MOD-POS-019 动态层)
# [CONSUMERS] scripts/backtest/sim_paper_ledger（AutoRuntime 事件链上的纸面盘日账，计划中的唯一
#   生产消费方——接线 diff 待主会话落地）; handle_pf_alloc_daily_event（事件正门，kind 派发待登记）;
#   CLI python -m zephyr.pf_alloc.allocation_orchestrator（人工/排障）
# [STARTUP] event_driven（DataScheduler task_completed → SIM_DAILY_WAKE_TASKS → run_sim_ledger_daily → 本件）
# [MATURITY] experimental
# [INVARIANTS] 本件=MOD-PA-007 五模块链的 **G15→G14 装配体**（挖矿 PFA-1 判"链从未被组装"的治本件）：
#   regime → RegimeMetaAllocator → BudgetChangeHandler → StrategyBook → AdjudicationCenter
#   → BatchedPositionBuilder → 账本钱包额度，单向数据流，无回环；
#   触发面=AutoRuntime 事件链（宪法 §9.3 禁 cron/Timer/sleep-loop），本件自身不注册任何定时器；
#   Σ allocations=1.0（分配器硬不变量，装配后 verify_allocation_invariants 复核）；
#   面板卫生=死成员/零权重成员**显式剔除并留痕**（budget=0，入 alloc_budget_daily），全灭面板
#     fail-closed 抛 AllocationInputError——绝不静默等权再归一（同期车道 A 的 T3② 口径）；
#   现金三账闭合：deployed + cash_drag（钱包级闲置）+ unallocated_cash（组合级预备金）
#     = portfolio_total，逐钱包 CashSeat 留痕，cash_weight≥0.5 升 warning（PFA-2 空转的计量面）；
#   Σ effective_budget ≤ global_shrinkage ≤ 1.0；Σ wallet_capital ≤ portfolio_total_capital；
#   缺教材/缺 alpha 一律 fail-closed（0.30 最低档节流 / 空仓），禁 flat 满部署、禁伪造信号；
#   任何资金常量经 AllocationConfig 真值，禁硬编码（PFA-2 的 1,000,000 只作为可回退缺省口径）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_suggest_only
# [ERROR_CONTRACT] AllocationInputError(日期/宇宙/面板全死/分配器不变量破裂) ;
#   AllocationPersistenceError(未落库) ; AllocationConfigError(配置非法)；
#   分配器 AllocationError(无策略可分配) 透传不吞；alloc_budget_daily 未建表=带 DDL 指针的
#   AllocationInputError（不降级为"无历史"）；单策略子步异常 → 该策略 budget=0 + warning
#   （逐策略隔离，不污染他策略，不静默丢整轮）
# [TESTS] tests/pf_alloc/test_allocation_chain.py; tests/pf_alloc/test_allocation_orchestrator.py;
#   tests/pf_alloc/test_pf_alloc_e2e.py
# [A_module] module_id=MOD-PA-030 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_suggest_only
# [TTL] permanent
# [CREATION-TOKEN] allocation-orchestrator-mod-pa-030-20260916
"""allocation_orchestrator——MOD-PA-007 五模块链的生产装配体（车道 D，2026-09-16）。

真源：docs/_working/full-auto-chain/S11_assembled_backtest/nodes/pf_alloc_consumer_mining.md
  PFA-1 五模块链零生产调用方（"链从未被组装"）→ 本件即缺失的装配体；
  PFA-2 账本 flat 100 万与"组合分配"叙事脱钩 → wallet_capital 由本件产出；
  PFA-3 regime/Shrinkage 实盘零消费 → 本件把 regime_snapshot_history PIT 概率喂进分配器；
  PFA-4 三实物缺口（base_weights 无源 / PerformanceScore 无生产者 / 再权无调度体）
        → 前两缺由 allocation_inputs 供件，第三缺由"事件驱动装配体"消解
          （无需月度 cron：每个 SIM_DAILY 事件即再权节拍，防抖在 BudgetChangeHandler 内）。

裁定依据：裁定#257③ 曾判"不接线、挂触发"，其挂起触发条件本身写的是"G15→G14 编排件立项"；
Owner 2026-09-16 明令"清单里所有还没开工的、全是设计态的，全线施工""不要留任何需要我裁定的内容"
= 该触发条件已由 Owner 令满足（同族先例：裁定#264 承 #257⑥ 同一条明令解除挂起）。
故本件按第一性原理落地真实接线，不再停在登记态。

[ALGO_FLOW]
输入: trade_date（业务日）+ 策略宇宙（注册表 sim 条目）+ 注入式 reader/sink/alpha_provider
前置检查: config.enabled；宇宙非空；日期字面量合法；allocator/handler/center 可注入（测试缝）
执行: ① load_regime_input  PIT 教材（无教材→平坦概率 0.30 档）
      ② build_base_weights  PP-001 sleeve 先验（未命中→均值补齐，来源逐条登记）
      ③ load_performance_scores  钱包净值→规范 Sortino 映射
      ④ StrategyBook.get_cold_start_ratio  三段式冷启动 ×0.3/×0.6/×1.0
      ⑤ RegimeMetaAllocator.allocate  → allocations/global_shrinkage/effective_budgets
      ⑥ BudgetChangeHandler.sync_from_allocator（含下线钱包显式 0.0）→ 防抖+三级升级+E-POS-40/41
      ⑦ LedgerStrategyBook.build_target_portfolio(budget=effective_budget) → 标的粗仓位
      ⑧ PositionAdjudicationCenter 四层（组合 PP-001 上限/策略 budget+Tier1|Tier3/标的 三层单票口径/
         动态 日历约束）→ final_weight+adjudication_id
      ⑨ BatchedPositionBuilder.build_plan + clip_to_available_capital → 分批计划
      ⑩ allocation_persistence 三表落库（write_to_db 可关）
输出: AllocationRunResult（含 wallet_capital: {strategy_id: 元}，账本据此开钱包）
降级: 无 alpha→该策略空仓但额度仍分配（禁伪造信号）；无教材→0.30 档节流；
      CH 不可达→写侧 local_durable/not_durable（后者抛错，禁"算了没落地"）
不变量: 同输入（含注入 reader/sink）→ 同输出（除 run_id 随机后缀，可注入 run_suffix 复现）
[/ALGO_FLOW]
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import uuid
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from zephyr.pf_alloc.allocation_config import AllocationConfig, load_allocation_config
from zephyr.pf_alloc.allocation_inputs import (
    AllocationInputError,
    BaseWeightTable,
    PerformanceScoreTable,
    RegimeInput,
    build_base_weights,
    load_performance_scores,
    load_previous_effective_budgets,
    load_regime_input,
    universe_from_registry,
    validate_date_literal,
)
from zephyr.pf_alloc.allocation_persistence import (
    WriteSink,
    write_budget_change_log,
    write_budget_daily,
    write_shrinkage_daily,
)
from zephyr.pf_alloc.batched_position_builder import (
    BatchedEntryPlan,
    BatchedPositionBuilder,
    clip_to_available_capital,
)
from zephyr.position.core.budget_change_handler import (
    BudgetChangeHandler,
    BudgetHandlerEvent,
    TierLevel,
)
from zephyr.position.core.calendar_position_constraint import (
    CalendarPositionConstraint,
    PositionInfo,
)
from zephyr.position.core.position_adjudication_center import (
    AdjudicatedPositionPlan,
    AdjudicationRequest,
    IntendedAction,
    LayerVerdict,
    PositionAdjudicationCenter,
)
from zephyr.position.core.single_name_cap_caliber import (
    LAYER_FINAL_HARD,
    LAYER_FIRM_AGG,
    LAYER_STRATEGY,
    SINGLE_NAME_CAP_LAYERS,
)
from zephyr.position.core.strategy_book import StrategyBook, TargetPortfolio

logger = logging.getLogger(__name__)

SCHEMA_VERSION = "1.0"

# 中文策略类型 → MOD-PA-006 分批阈值键（AGGRESSIVE_THRESHOLD 的键域）
BUILDER_STRATEGY_TYPE: dict[str, str] = {
    "打板": "daban",
    "多因子": "multifactor",
    "事件驱动": "event",
}

# 等权默认 confidence（TargetWeight.confidence 缺省，C-031 未接线的诚实值）
DEFAULT_CONFIDENCE = 0.5

AlphaProvider = Callable[[str, Any], Sequence[str]]
AvailableCashProvider = Callable[[str, float], float]

# 现金席位占钱包比例超过该值 → 产出可见 cash drag 告警（PFA-2"百万级现金平钱包空转"的
# 计量口径：病灶不是"拿着现金"，而是"拿着现金没人知道"）。
CASH_DRAG_WARN_RATIO = 0.50


@dataclass(frozen=True)
class ExcludedMember:
    """被显式剔除的死成员/零权重成员（**不静默再归一**，逐条留痕入结果与 note）。"""

    strategy_id: str
    reason: str
    base_weight: float
    perf_score: float
    sample_days: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "reason": self.reason,
            "base_weight": round(float(self.base_weight), 8),
            "perf_score": round(float(self.perf_score), 8),
            "sample_days": int(self.sample_days),
        }


@dataclass(frozen=True)
class CashSeat:
    """一个钱包的现金席位（钱包口径，Σ仓位 + cash = 1.0）。

    平钱包/无 alpha/可用资金不足都会把额度顶成现金——本件不隐藏这个事实：
    cash_weight>0 即逐钱包留痕，cash_drag=True 进 warnings，钱包级未投金额进
    batch_plan_json 与 alloc_shrinkage_daily.unallocated_cash（组合级）。
    """

    strategy_id: str
    wallet_capital: float
    invested_weight: float  # 绝对组合占比（Σ final_weight）
    cash_weight: float  # 钱包内现金占比 ∈[0,1]
    cash_capital: float
    clip_scale: float  # 可用资金裁剪系数（1.0=未裁剪）
    degrade_reason: str | None = None

    @property
    def cash_drag(self) -> bool:
        return self.cash_weight >= CASH_DRAG_WARN_RATIO

    def as_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "wallet_capital": round(self.wallet_capital, 2),
            "invested_weight": round(self.invested_weight, 8),
            "cash_weight": round(self.cash_weight, 8),
            "cash_capital": round(self.cash_capital, 2),
            "clip_scale": round(self.clip_scale, 8),
            "cash_drag": self.cash_drag,
            "degrade_reason": self.degrade_reason,
        }


@dataclass(frozen=True)
class SymbolPlan:
    """单标的：意图权重 → 裁决终值 → 分批计划（下单链凭证留痕）。"""

    symbol: str
    intended_weight: float
    final_weight: float
    allowed: bool
    adjudication_id: str
    reason: str
    confidence: float
    batches: tuple[dict[str, Any], ...] = ()
    degrade_reason: str | None = None


@dataclass(frozen=True)
class StrategyAllocation:
    """单策略一轮分配的完整事实（=alloc_budget_daily 一行的域形）。"""

    strategy_id: str
    strategy_type: str
    base_weight: float
    base_weight_source: str
    perf_score: float
    perf_sample_days: int
    allocation: float
    global_shrinkage: float
    cold_start_ratio: float
    effective_budget: float
    previous_budget: float
    allocated_capital: float
    final_weight: float  # 本策略经裁决后允许承载的总权重（绝对组合占比）
    budget_action: str
    current_tier: str
    freeze_new_positions: bool
    retain_ratio: float | None
    adjudication_ids: tuple[str, ...]
    symbols: tuple[SymbolPlan, ...]
    cash_seat: CashSeat | None = None
    excluded_reason: str = ""  # 非空=本成员被显式剔除（死成员/零权重），budget 恒 0
    note: str = ""

    def to_row(self, run_id: str, trade_date: str) -> dict[str, Any]:
        return {
            "run_id": run_id,
            "trade_date": trade_date,
            "strategy_id": self.strategy_id,
            "strategy_type": self.strategy_type,
            "base_weight": round(self.base_weight, 8),
            "base_weight_source": self.base_weight_source,
            "perf_score": round(self.perf_score, 8),
            "perf_sample_days": int(self.perf_sample_days),
            "allocation": round(self.allocation, 8),
            "global_shrinkage": round(self.global_shrinkage, 8),
            "cold_start_ratio": round(self.cold_start_ratio, 8),
            "effective_budget": round(self.effective_budget, 8),
            "previous_budget": round(self.previous_budget, 8),
            "allocated_capital": round(self.allocated_capital, 2),
            "final_weight": round(self.final_weight, 8),
            "adjudication_id": ",".join(self.adjudication_ids)[:128],
            "budget_action": self.budget_action,
            "current_tier": self.current_tier,
            "batch_plan_json": json.dumps(
                {
                    "strategy_id": self.strategy_id,
                    "symbols": [
                        {
                            "symbol": s.symbol,
                            "intended_weight": round(s.intended_weight, 8),
                            "final_weight": round(s.final_weight, 8),
                            "allowed": s.allowed,
                            "adjudication_id": s.adjudication_id,
                            "confidence": round(s.confidence, 6),
                            "batches": list(s.batches),
                            "degrade_reason": s.degrade_reason,
                        }
                        for s in self.symbols
                    ],
                    # 现金席位与剔除理由入 JSON（三表 DDL 无对应列，改列=跨域 schema 变更）
                    "cash_seat": self.cash_seat.as_dict() if self.cash_seat else None,
                    "excluded_reason": self.excluded_reason,
                    "note": self.note,
                    "schema_version": SCHEMA_VERSION,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            "note": self.note,
            "schema_version": SCHEMA_VERSION,
        }


@dataclass(frozen=True)
class AllocationRunResult:
    """一轮分配的完整输出（账本消费 wallet_capital）。"""

    run_id: str
    trade_date: str
    enabled: bool
    portfolio_total_capital: float
    global_shrinkage: float
    sum_effective_budget: float
    unallocated_cash: float
    wallet_capital: dict[str, float]
    strategies: tuple[StrategyAllocation, ...]
    regime: dict[str, Any]
    change_log_rows: tuple[dict[str, Any], ...]
    persisted: dict[str, str]
    warnings: tuple[str, ...] = ()
    excluded_members: tuple[ExcludedMember, ...] = ()
    cash_seats: tuple[CashSeat, ...] = ()
    cash_drag_capital: float = 0.0
    config_snapshot: dict[str, Any] = field(default_factory=dict)

    def summary(self) -> dict[str, Any]:
        """人读/日志/账本 note 用的 JSON-safe 摘要。"""
        return {
            "run_id": self.run_id,
            "trade_date": self.trade_date,
            "enabled": self.enabled,
            "portfolio_total_capital": round(self.portfolio_total_capital, 2),
            "global_shrinkage": round(self.global_shrinkage, 6),
            "sum_effective_budget": round(self.sum_effective_budget, 6),
            "unallocated_cash": round(self.unallocated_cash, 2),
            "cash_drag_capital": round(self.cash_drag_capital, 2),
            "wallet_capital": {k: round(v, 2) for k, v in self.wallet_capital.items()},
            "excluded_members": [e.as_dict() for e in self.excluded_members],
            "cash_seats": [c.as_dict() for c in self.cash_seats],
            "regime": dict(self.regime),
            "warnings": list(self.warnings),
            "persisted": dict(self.persisted),
        }


class LedgerStrategyBook(StrategyBook):
    """账本侧策略账本：选股由注入的 alpha 提供器给出（无 alpha=空仓，禁伪造信号）。

    MOD-POS-020 的 select_stocks 是子类钩子（挖矿 PFA-1 指出该链"每模块都在、无人调用"）；
    本子类即"生产消费端"的最小实现——把分配链的 budget 真正送进 build_target_portfolio，
    alpha 侧仍由各策略引擎（翻译件重放/实盘信号）注入，本件不代造。
    """

    def __init__(
        self,
        strategy_id: str,
        *,
        alpha_provider: AlphaProvider | None = None,
        sizing_method: str = "equal_weight",
        strategy_type: str = "多因子",
        live_start_date: date | None = None,
    ) -> None:
        super().__init__(
            strategy_id,
            sizing_method=sizing_method,
            strategy_type=strategy_type,
            live_start_date=live_start_date,
        )
        self._alpha_provider = alpha_provider

    def select_stocks(self, alpha_signals: dict[str, Any]) -> list[str]:
        if self._alpha_provider is None:
            return []
        picked = self._alpha_provider(self.strategy_id, alpha_signals) or []
        return [str(s) for s in picked if str(s).strip()]


# ── 裁决四层（组合/策略/标的/动态）──────────────────────────────────


@dataclass
class _LayerFacts:
    """一次 run 内四层裁决共享的只读事实（由装配体填充，层函数只读）。"""

    sleeve_cap: float
    total_cap: float
    sum_effective: float
    symbol_aggregate: dict[str, float]
    freeze: dict[str, bool]
    retain: dict[str, float | None]
    calendar_block_new: bool
    calendar_cap_adjustment: float
    is_crisis: bool


def _clip01(value: float) -> float:
    if not math.isfinite(value):
        return 0.0
    return max(0.0, min(1.0, value))


def _portfolio_layer(facts: _LayerFacts) -> Callable[[AdjudicationRequest], LayerVerdict]:
    """组合层：PP-001 单 sleeve 上限 + 总暴露天花板 + 跨策略同票聚合上限（8% firm 口径）。"""

    def _run(request: AdjudicationRequest) -> LayerVerdict:
        weight = request.intended_weight
        violations: list[str] = []
        reasons: list[str] = []
        ctx = request.context or {}
        strategy_budget = float(ctx.get("strategy_effective_budget", 1.0))

        if strategy_budget > facts.sleeve_cap > 0:
            scale = facts.sleeve_cap / strategy_budget
            weight *= scale
            violations.append("SLEEVE_CAP")
            reasons.append(f"PP-001 max_single_sleeve={facts.sleeve_cap:.2f} 策略占比裁剪×{scale:.3f}")

        if 0 < facts.total_cap < facts.sum_effective:
            scale = facts.total_cap / facts.sum_effective
            weight *= scale
            violations.append("TOTAL_POSITION_CAP")
            reasons.append(f"max_total_position={facts.total_cap:.2f} 总暴露裁剪×{scale:.3f}")

        aggregate = float(facts.symbol_aggregate.get(request.symbol, 0.0))
        firm_cap = SINGLE_NAME_CAP_LAYERS[LAYER_FIRM_AGG]
        if aggregate > firm_cap > 0:
            scale = firm_cap / aggregate
            weight *= scale
            violations.append("SYMBOL_AGGREGATE_CAP")
            reasons.append(f"跨策略同票聚合 {aggregate:.4f} > firm 口径 {firm_cap:.2f}，×{scale:.3f}")

        return LayerVerdict(
            layer="portfolio",
            allowed=True,  # 组合层做裁剪不做否决（否决权在策略/动态层，语义分层）
            adjusted_weight=_clip01(weight),
            violations=tuple(violations),
            reason="; ".join(reasons) or "组合层无裁剪",
        )

    return _run


def _strategy_layer(facts: _LayerFacts) -> Callable[[AdjudicationRequest], LayerVerdict]:
    """策略层：budget 硬约束 + Tier1/Tier3 冻结新开仓（MOD-POS-022 指令落地为下单语义）。"""

    def _run(request: AdjudicationRequest) -> LayerVerdict:
        ctx = request.context or {}
        budget = float(ctx.get("strategy_effective_budget", 1.0))
        sid = request.strategy_id
        if facts.freeze.get(sid):
            return LayerVerdict(
                layer="strategy",
                allowed=False,
                adjusted_weight=0.0,
                violations=("TIER1_FREEZE_NEW_POSITIONS",),
                reason="BudgetChangeHandler Tier1/强裁冻结：本日禁新开仓（现有仓位不动）",
            )
        retain = facts.retain.get(sid)
        if retain is not None and retain < 1.0:
            return LayerVerdict(
                layer="strategy",
                allowed=False,
                adjusted_weight=0.0,
                violations=("TIER3_TRIM_PENDING",),
                reason=f"Tier3 强裁未执行完（retain_ratio={retain:.3f}），先减仓后开仓",
            )
        weight = min(request.intended_weight, max(0.0, budget))
        return LayerVerdict(
            layer="strategy",
            allowed=True,
            adjusted_weight=_clip01(weight),
            violations=()
            if request.intended_weight <= budget + 1e-12
            else ("STRATEGY_BUDGET_CAP",),
            reason=f"策略 budget={budget:.4f} 硬约束"
            + ("" if request.intended_weight <= budget + 1e-12 else "（裁剪至上限）"),
        )

    return _run


def _symbol_layer(_facts: _LayerFacts) -> Callable[[AdjudicationRequest], LayerVerdict]:
    """标的层：三层单票口径取最严（策略层 5% / 最终硬限 5%，真源=single_name_cap_caliber）。"""
    cap = min(SINGLE_NAME_CAP_LAYERS[LAYER_STRATEGY], SINGLE_NAME_CAP_LAYERS[LAYER_FINAL_HARD])

    def _run(request: AdjudicationRequest) -> LayerVerdict:
        weight = min(request.intended_weight, cap)
        return LayerVerdict(
            layer="symbol",
            allowed=True,
            adjusted_weight=_clip01(weight),
            violations=() if request.intended_weight <= cap + 1e-12 else ("SINGLE_NAME_CAP",),
            reason=f"单票上限 {cap:.2%}（MOD-POS 三层口径最严值）",
        )

    return _run


def _dynamic_layer(facts: _LayerFacts) -> Callable[[AdjudicationRequest], LayerVerdict]:
    """动态层：A 股风险日历约束（MOD-POS-019）——交割日/报告期等否决新开仓 + 上限下调。"""

    def _run(request: AdjudicationRequest) -> LayerVerdict:
        if facts.calendar_block_new:
            return LayerVerdict(
                layer="dynamic",
                allowed=False,
                adjusted_weight=0.0,
                violations=("CALENDAR_BLOCK_NEW",),
                reason="风险日历约束命中：本日否决新开仓（仅允许减仓）",
            )
        weight = request.intended_weight * max(0.0, facts.calendar_cap_adjustment)
        return LayerVerdict(
            layer="dynamic",
            allowed=True,
            adjusted_weight=_clip01(weight),
            violations=() if facts.calendar_cap_adjustment >= 1.0 else ("CALENDAR_CAP_ADJUST",),
            reason=f"日历仓位上限系数 {facts.calendar_cap_adjustment:.2f}",
        )

    return _run


def build_adjudication_center(facts: _LayerFacts) -> PositionAdjudicationCenter:
    """四层注入式装配（裁决中心只编排不判定——本件提供四层的判定实现与事实）。"""
    return PositionAdjudicationCenter(
        portfolio_layer=_portfolio_layer(facts),
        strategy_layer=_strategy_layer(facts),
        symbol_layer=_symbol_layer(facts),
        dynamic_layer=_dynamic_layer(facts),
    )


# ── 事件流水（E-POS-40/41 → alloc_budget_change_log）─────────────────


class ChangeLogCollector:
    """订阅 BudgetChangeHandler 的 E-POS-40/41，转成落地行（进程内事件 → 可审计事实）。"""

    def __init__(self, run_id: str, trade_date: str, debounce_pct: float) -> None:
        self.rows: list[dict[str, Any]] = []
        self._seq: dict[str, int] = {}
        self._run_id = run_id
        self._trade_date = trade_date
        self._debounce_pct = debounce_pct

    def __call__(self, event: BudgetHandlerEvent) -> None:  # noqa: D102 — 订阅者协议
        payload = dict(event.payload or {})
        sid = str(payload.get("strategy_id") or event.strategy_id)
        seq = self._seq.get(sid, 0)
        self._seq[sid] = seq + 1
        old = float(payload.get("old_budget") or 0.0)
        target = float(payload.get("target_budget") or 0.0)
        tiers = [str(t) for t in (payload.get("instruction_tiers") or [])]
        trim = payload.get("trim_ratio")
        current_tier = str(payload.get("current_tier") or payload.get("to_tier") or "")
        self.rows.append(
            {
                "run_id": self._run_id,
                "trade_date": self._trade_date,
                "strategy_id": sid,
                "seq": seq,
                "event_id": event.event_id,
                "event_name": event.name,
                "old_budget": round(old, 8),
                "target_budget": round(target, 8),
                "delta_pct": round((target - old) / old, 8) if old > 0 else 0.0,
                "current_tier": current_tier,
                "action": str(payload.get("action") or f"ESCALATION:{payload.get('from_tier', '')}→{payload.get('to_tier', '')}"),
                "debounce_pct": round(self._debounce_pct, 6),
                "freeze_new_positions": 1 if ("1" in tiers or "2" in tiers or "3" in tiers) else 0,
                "trim_ratio": float(trim) if isinstance(trim, (int, float)) else float("nan"),
                "reason": str(payload.get("reason") or payload.get("action") or "")[:500],
                "payload_json": json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str),
                "schema_version": SCHEMA_VERSION,
            }
        )

    def freeze_flags(self) -> dict[str, bool]:
        """本 run 内被 Tier1+ 冻结新开仓的策略（最后一事件口径）。"""
        out: dict[str, bool] = {}
        for row in self.rows:
            out[row["strategy_id"]] = bool(row["freeze_new_positions"])
        return out


# ── 装配体主入口 ────────────────────────────────────────────────


def make_run_id(trade_date: str, suffix: str | None = None) -> str:
    """run 标识=业务日 + 随机后缀（**不含墙钟**，RULE-SCHEMA-TZ；重跑=新 run_id 追加）。"""
    return f"alloc-{trade_date}-{(suffix or uuid.uuid4().hex[:6])}"


def _regime_dict(regime: RegimeInput) -> dict[str, Any]:
    return {
        "probs": [round(p, 6) for p in regime.probabilities],
        "dominant": regime.dominant,
        "max_probability": round(regime.max_probability, 6),
        "source_run_id": regime.source_run_id,
        "source_date": regime.source_date.strftime("%Y-%m-%d") if regime.source_date else None,
        "lag_days": int(regime.lag_days),
        "snapshot_shrinkage": regime.snapshot_shrinkage,
        "risk_signal": round(regime.risk_signal, 6),
        "risk_signal_source": regime.risk_signal_source,
        "is_crisis": bool(regime.is_crisis),
    }


def screen_panel(
    strategy_ids: Sequence[str],
    base: BaseWeightTable,
    perf: PerformanceScoreTable,
) -> tuple[list[str], tuple[ExcludedMember, ...]]:
    """面板卫生：死成员/零权重成员**显式剔除**，全灭则 fail-closed（不静默再归一）。

    为什么在本件（装配层）而非 MOD-PA-007 内部做：分配器 `_normalize_and_clip` 的
    "raw 全零→回退等权 1/N" 分支会把"整个面板已死"伪装成"均仓可执行"（同期车道 A
    的 T3② 治本口径）。装配层是**唯一看得见 base_weight 与 perf 双输入**的位置，
    在这里剔除并留痕，分配器只需在活成员上做归一，语义不变、无静默路径。

    Returns:
        (活成员列表, ExcludedMember 元组)

    Raises:
        AllocationInputError: 面板为空或全部成员为死成员（禁等权兜底继续下单）
    """
    alive: list[str] = []
    excluded: list[ExcludedMember] = []
    for sid in strategy_ids:
        bw = float(base.weights.get(sid, 0.0) or 0.0)
        ps = float(perf.scores.get(sid, 0.0) or 0.0)
        days = int(perf.sample_days.get(sid, 0) or 0)
        reason = ""
        if not math.isfinite(bw) or bw <= 0:
            reason = f"死成员：base_weight={bw} 非正/非有限（PP-001 先验缺席或登记为 0）"
        elif not math.isfinite(ps) or ps <= 0:
            reason = f"死成员：performance_score={ps} 非正/非有限（后验归零）"
        if reason:
            excluded.append(ExcludedMember(sid, reason, bw, ps, days))
        else:
            alive.append(sid)
    if not alive:
        raise AllocationInputError(
            f"面板 {len(strategy_ids)} 个成员全部为死成员/零权重"
            f"（{[e.strategy_id for e in excluded]}）——拒绝等权兜底（静默再归一=把"
            "'无仓可分'伪装成'满仓可分'，与 PFA-2 平钱包空转同源）"
        )
    return alive, tuple(excluded)


def verify_allocation_invariants(
    allocation: Any,
    alive: Sequence[str],
) -> None:
    """分配器输出的硬不变量复核（违约抛错，禁"信库件一定会对"）。"""
    allocs = {k: float(v) for k, v in dict(allocation.allocations).items()}
    eff = {k: float(v) for k, v in dict(allocation.effective_budgets).items()}
    gs = float(allocation.global_shrinkage)
    if set(allocs) != set(alive) or set(eff) != set(alive):
        raise AllocationInputError(
            f"分配输出成员集与面板不一致（alloc={sorted(allocs)} vs alive={sorted(alive)}）"
        )
    total = sum(allocs.values())
    if abs(total - 1.0) > 1e-6:
        raise AllocationInputError(f"Σallocations={total:.10f}≠1.0（MOD-PA-007 硬不变量破裂）")
    if not 0.0 <= gs <= 1.0:
        raise AllocationInputError(f"global_shrinkage={gs} 越界 [0,1]")
    sum_eff = sum(eff.values())
    if sum_eff > gs + 1e-9:
        raise AllocationInputError(
            f"Σeffective_budget={sum_eff:.10f} > global_shrinkage={gs:.10f}（总暴露越天花板）"
        )
    for sid, v in eff.items():
        if v < -1e-12:
            raise AllocationInputError(f"策略 {sid} effective_budget={v} 为负")
        if v > 1.0 + 1e-9:
            # 单 sleeve 的 PP-001 上限由组合裁决层裁剪（_portfolio_layer），此处只拦
            # "逻辑不可能"值：任何策略的占比都不可能超过总盘子
            raise AllocationInputError(f"策略 {sid} effective_budget={v} > 1.0（占比越总盘）")


def run_daily_allocation(
    trade_date: str | date,
    *,
    universe: Iterable[Mapping[str, Any]] | None = None,
    config: AllocationConfig | None = None,
    reader: Callable[[str], Sequence[Any]] | None = None,
    sink: WriteSink | None = None,
    alpha_provider: AlphaProvider | None = None,
    available_cash_provider: AvailableCashProvider | None = None,
    allocator: Any = None,
    handler: BudgetChangeHandler | None = None,
    write: bool | None = None,
    run_suffix: str | None = None,
    discipline_guard: Any = None,
) -> AllocationRunResult:
    """一次分配周期的完整装配（账本/CLI/测试共用的唯一入口）。

    Args:
        trade_date: 业务交易日（分配 as-of 日；防抖与净值窗口都以它为界）
        universe: 策略宇宙（None=注册表 lifecycle==sim 条目）
        config: 运行配置（None=load_allocation_config()）
        reader/sink: CH 读写注入缝（测试用假件，禁在测试里写真库）
        alpha_provider: {strategy_id}->标的列表 的 alpha 提供器；None=一律空仓（禁伪造信号）
        available_cash_provider: 钱包可用资金提供器（T+1 冻结口径注入点），None=额度即现金
        allocator/handler: 分配器与 budget 处理器注入（测试用）
        write: 是否落库（None=跟随 config.write_to_db；sink 显式注入时默认落该 sink）
        run_suffix: 固定 run_id 后缀（E2E 复现用）
        discipline_guard: MOD-CMP-002 四项严禁引擎（下单前闸，本件只做计划不提交订单）

    Returns:
        AllocationRunResult（wallet_capital 即账本应使用的钱包额度）

    Raises:
        AllocationInputError: 日期/宇宙契约非法
        AllocationPersistenceError: 落库未确认（fail-closed）
    """
    day = validate_date_literal(trade_date)
    cfg = config or load_allocation_config()
    run_id = make_run_id(day, run_suffix)
    do_write = (True if sink is not None else cfg.write_to_db) if write is None else bool(write)
    warnings: list[str] = []

    specs = list(universe) if universe is not None else universe_from_registry()
    strategy_ids = [str(s.get("strategy_id") or "").strip() for s in specs]
    strategy_ids = [s for s in strategy_ids if s]
    types = {str(s.get("strategy_id")): str(s.get("strategy_type") or "多因子") for s in specs}
    live_starts = {
        str(s.get("strategy_id")): s.get("live_start_date") for s in specs
    }

    if not cfg.enabled:
        # 显式回退真值：账本走 flat 口径，本件不产额度也不落库（回退路径=配置，不是删码）
        return AllocationRunResult(
            run_id=run_id,
            trade_date=day,
            enabled=False,
            portfolio_total_capital=cfg.resolve_portfolio_total(max(len(strategy_ids), 1)),
            global_shrinkage=1.0,
            sum_effective_budget=0.0,
            unallocated_cash=0.0,
            wallet_capital={},
            strategies=(),
            regime={},
            change_log_rows=(),
            persisted={"disabled": "allocation_disabled"},
            warnings=tuple(warnings),
            config_snapshot=cfg.to_dict(),
        )

    if not strategy_ids:
        raise AllocationInputError(f"{day} 策略宇宙为空——无法分配（检查注册表 sim 条目）")

    regime = load_regime_input(day, cfg, reader=reader)
    if not regime.has_snapshot:
        warnings.append("regime_no_snapshot: 无 PIT 教材→平坦概率（ConfidenceSignal 最低档 0.30）")
    base = build_base_weights(strategy_ids, cfg)
    if base.plan_id == "":
        warnings.append("pp001_unavailable: PP-001 先验缺席→等权先验")
    perf: PerformanceScoreTable = load_performance_scores(
        strategy_ids, day, cfg, reader=reader
    )

    # ── 面板卫生（T3② 口径：死成员显式剔除、全灭 fail-closed，绝不静默等权再归一）──
    alive, excluded = screen_panel(strategy_ids, base, perf)
    excluded_reasons = {e.strategy_id: e.reason for e in excluded}
    if excluded:
        warnings.append(
            "dead_members_excluded: "
            + "; ".join(f"{e.strategy_id}<-{e.reason}" for e in excluded)
        )

    meta_allocator = allocator or _default_allocator(base, cfg)
    cold_ratios: dict[str, float] = {}
    for sid in alive:
        book = LedgerStrategyBook(
            sid,
            alpha_provider=None,  # 冷启动比例与 alpha 无关
            strategy_type=types.get(sid, "多因子"),
            live_start_date=_as_date(live_starts.get(sid)),
        )
        cold_ratios[sid] = book.get_cold_start_ratio(
            today=_as_date(day), perf_valid_observations=perf.sample_days.get(sid, 0)
        )

    allocation = meta_allocator.allocate(
        regime_probabilities=list(regime.probabilities),
        performance_scores={sid: float(perf.scores[sid]) for sid in alive},
        risk_signal_inputs={
            "risk_base": regime.risk_signal,
            "resonance_penalty": 1.0,
            "opportunity_recovery": 0.0,
        },
        strategy_sample_days={sid: int(perf.sample_days.get(sid, 0)) for sid in alive},
        is_crisis=regime.is_crisis,
        cold_start_ratios=cold_ratios,
    )
    verify_allocation_invariants(allocation, alive)
    effective: dict[str, float] = {k: float(v) for k, v in allocation.effective_budgets.items()}
    # 被剔除成员以"显式 0 budget"入下游（on_budget_allocation 口径：0 须显式传，
    # 不传=不处置；此处显式传 0 → 其既有钱包走三级升级削清，不留静默残留仓位）
    for sid in excluded_reasons:
        effective[sid] = 0.0
    global_shrinkage = float(allocation.global_shrinkage)

    # ── MOD-POS-022：budget 变动裁决（防抖 + 三级升级 + E-POS-40/41）──
    if handler is None:
        _ensure_parent_dir(cfg.persist_full_path)  # TierState 快照目录自建（否则 _save_snapshot 裸炸）
    budget_handler = handler or BudgetChangeHandler(persist_path=str(cfg.persist_full_path))
    collector = ChangeLogCollector(run_id, day, float(getattr(budget_handler, "debounce_threshold", 0.05)))
    budget_handler.subscribe(collector)
    try:
        previous = load_previous_effective_budgets(day, reader=reader)
    except Exception as exc:  # noqa: BLE001 — 仅翻译"表未建"这一种可归因形态，其余原样上抛
        if "alloc_budget_daily" in str(exc):
            raise AllocationInputError(
                "读取上期 effective_budget 失败——alloc_budget_daily 很可能尚未建表。"
                "先执行 `python scripts/ch/apply_pf_alloc_ddl.py --apply`（CREATE IF NOT EXISTS 幂等）"
                "再重跑；本件**不**按『无历史』继续（那会让 BudgetChangeHandler 防抖整轮失效）。"
                f"原始错误：{type(exc).__name__}: {exc}"
            ) from exc
        raise
    orphans = sorted(set(previous) - set(effective))
    sync_target = dict(effective)
    for sid in orphans:  # 策略下线须显式传 0（on_budget_allocation 的口径：不自动强裁缺口）
        sync_target[sid] = 0.0
    if orphans:
        warnings.append(f"orphan_wallets: {orphans} 上期有本期无→显式 budget→0 交三级升级")
    results = budget_handler.sync_from_allocator(
        sync_target,
        previous_budgets=(previous or None),
        strategy_types=types,
        current_date=day,
    )
    freeze_flags = collector.freeze_flags()
    retains: dict[str, float | None] = {}
    actions: dict[str, str] = {}
    tiers: dict[str, str] = {}
    for sid, res in (results or {}).items():
        actions[sid] = str(getattr(res, "action", ""))
        state = getattr(res, "state", None)
        tiers[sid] = str(getattr(getattr(state, "current_tier", None), "value", TierLevel.IDLE.value))
        for instr in getattr(res, "instructions", []) or []:
            payload = instr.get("instruction") if isinstance(instr, dict) else None
            retain = getattr(payload, "retain_ratio", None)
            if retain is not None:
                retains[sid] = float(retain)

    portfolio_total = cfg.resolve_portfolio_total(len(strategy_ids))
    sum_effective = round(sum(effective.get(sid, 0.0) for sid in strategy_ids), 10)
    symbol_aggregate: dict[str, float] = {}
    # 默认值先置、真实裁决后覆盖（顺序反了会把 Tier1 冻结/ Tier3 保留比例抹掉——真 bug）
    freeze_flags = {sid: False for sid in strategy_ids} | freeze_flags
    retains = {sid: None for sid in strategy_ids} | retains
    centers_facts = _LayerFacts(
        sleeve_cap=float(base.max_single_sleeve or cfg.max_single_sleeve),
        total_cap=float(base.max_total_position or cfg.max_total_position),
        sum_effective=sum_effective,
        symbol_aggregate=symbol_aggregate,
        freeze=freeze_flags,
        retain=retains,
        is_crisis=bool(regime.is_crisis),
        **_calendar_facts(_as_date(day)),
    )
    center = build_adjudication_center(centers_facts)
    builder = BatchedPositionBuilder(discipline_guard=discipline_guard)

    failed: dict[str, str] = {}
    budgets: dict[str, float] = {sid: float(effective.get(sid, 0.0)) for sid in strategy_ids}

    # ── Pass A：各策略目标组合（先把跨策略同票聚合算全，组合层才看得见真实总暴露）──
    portfolios: dict[str, TargetPortfolio] = {}
    for sid in alive:
        try:
            book = LedgerStrategyBook(
                sid,
                alpha_provider=alpha_provider,
                strategy_type=types.get(sid, "多因子"),
                live_start_date=_as_date(live_starts.get(sid)),
            )
            portfolio = book.build_target_portfolio(
                alpha_signals={"trade_date": day, "budget": budgets[sid]},
                budget=budgets[sid],
            )
        except Exception as exc:  # noqa: BLE001 — 逐策略隔离：单策略失败不毁整轮
            logger.warning("策略 %s 目标组合构建失败（budget 置 0）: %s", sid, exc)
            failed[sid] = f"{type(exc).__name__}: {exc}"
            budgets[sid] = 0.0
            warnings.append(f"strategy_build_failed: {sid}")
            continue
        portfolios[sid] = portfolio
        for sym, tw in portfolio.positions.items():
            symbol_aggregate[sym] = symbol_aggregate.get(sym, 0.0) + float(tw.target_weight)

    # ── Pass B：四层裁决 + 分批计划 + 逐策略结果（含被剔除成员，逐笔可追溯）──
    built: list[StrategyAllocation] = []
    cash_seats: list[CashSeat] = []
    for sid in strategy_ids:
        budget = budgets[sid]
        capital = round(portfolio_total * budget, 2)
        note_parts = [f"run={run_id}", f"regime={regime.source_run_id}/{regime.dominant}"]
        detail = perf.details.get(sid)
        if detail is not None and detail.note:
            note_parts.append(detail.note)
        portfolio = portfolios.get(sid)
        symbols: tuple[SymbolPlan, ...] = ()
        seat: CashSeat | None = None
        if sid in excluded_reasons:
            note_parts.append(
                f"死成员显式剔除（{excluded_reasons[sid]}）→ budget=0"
                "（不静默等权再归一，额度回流为组合级未分配预备金）"
            )
        elif portfolio is not None:
            symbols, seat = _adjudicate_symbols(
                portfolio=portfolio,
                strategy_id=sid,
                budget=budget,
                capital=capital,
                portfolio_total=portfolio_total,
                center=center,
                builder=builder,
                strategy_type=types.get(sid, "多因子"),
                available_cash_provider=available_cash_provider,
                run_id=run_id,
            )
            if not portfolio.positions:
                note_parts.append("alpha 未接线或无信号→空仓（额度仍按分配生效，禁伪造信号）")
        elif sid in failed:
            note_parts.append(f"目标组合构建失败→budget=0（{failed[sid]}）")
        approved = round(sum(s.final_weight for s in symbols), 10)
        if seat is None:  # 剔除/失败成员：无钱包即无现金拖累（如实 0，不造记录）
            seat = CashSeat(
                strategy_id=sid,
                wallet_capital=capital,
                invested_weight=approved,
                cash_weight=1.0 if capital > 0 else 0.0,
                cash_capital=capital,
                clip_scale=1.0,
            )
        cash_seats.append(seat)
        if seat.cash_drag and seat.cash_capital > 0:
            warnings.append(
                f"cash_drag: {sid} 钱包 {seat.cash_capital:.2f} 元"
                f"（{seat.cash_weight:.1%}）闲置"
                + (f"｜{seat.degrade_reason}" if seat.degrade_reason else "")
            )
        built.append(
            StrategyAllocation(
                strategy_id=sid,
                strategy_type=types.get(sid, "多因子"),
                base_weight=float(base.weights.get(sid, 0.0)),
                base_weight_source=base.sources.get(sid, "unknown"),
                perf_score=float(perf.scores.get(sid, 1.0)),
                perf_sample_days=int(perf.sample_days.get(sid, 0)),
                allocation=round(float(allocation.allocations.get(sid, 0.0)), 10),
                global_shrinkage=global_shrinkage,
                cold_start_ratio=float(cold_ratios.get(sid, 1.0)),
                effective_budget=budget,
                previous_budget=float(previous.get(sid, budget)),
                allocated_capital=capital,
                final_weight=approved,
                budget_action=actions.get(sid, "NO_PREV"),
                current_tier=tiers.get(sid, TierLevel.IDLE.value),
                freeze_new_positions=bool(centers_facts.freeze.get(sid)),
                retain_ratio=retains.get(sid),
                adjudication_ids=tuple(s.adjudication_id for s in symbols),
                symbols=symbols,
                cash_seat=seat,
                excluded_reason=excluded_reasons.get(sid, ""),
                note=" | ".join(note_parts)[:500],
            )
        )

    wallet_capital = {x.strategy_id: float(x.allocated_capital) for x in built}
    sum_wallet = sum(wallet_capital.values())
    unallocated = round(max(0.0, portfolio_total - sum_wallet), 2)
    cash_drag_capital = round(sum(c.cash_capital for c in cash_seats), 2)

    rows = [s.to_row(run_id, day) for s in built]
    shrinkage_row = _shrinkage_row(
        run_id, day, cfg, regime, allocation, built, portfolio_total, unallocated, base,
        cash_seats, cash_drag_capital,
    )
    persisted: dict[str, str] = {}
    if do_write:
        _, persisted["budget_daily"] = write_budget_daily(rows, sink=sink)
        _, persisted["shrinkage_daily"] = write_shrinkage_daily([shrinkage_row], sink=sink)
        if collector.rows:
            _, persisted["budget_change_log"] = write_budget_change_log(collector.rows, sink=sink)
    else:
        persisted["budget_daily"] = "skipped_write_disabled"
        persisted["shrinkage_daily"] = "skipped_write_disabled"
        if collector.rows:
            persisted["budget_change_log"] = "skipped_write_disabled"

    result = AllocationRunResult(
        run_id=run_id,
        trade_date=day,
        enabled=True,
        portfolio_total_capital=portfolio_total,
        global_shrinkage=global_shrinkage,
        sum_effective_budget=sum_effective,
        unallocated_cash=unallocated,
        wallet_capital=wallet_capital,
        strategies=tuple(built),
        regime=_regime_dict(regime),
        change_log_rows=tuple(collector.rows),
        persisted=persisted,
        warnings=tuple(warnings),
        excluded_members=tuple(excluded),
        cash_seats=tuple(cash_seats),
        cash_drag_capital=cash_drag_capital,
        config_snapshot=cfg.to_dict(),
    )
    logger.info("分配完成 %s", json.dumps(result.summary(), ensure_ascii=False, default=str))
    return result


def _default_allocator(base: BaseWeightTable, cfg: AllocationConfig) -> Any:
    from zephyr.pf_alloc.core.regime_meta_allocator import RegimeMetaAllocator

    return RegimeMetaAllocator(
        base_weights=base.as_allocator_weights(),
        shrinkage_enabled=cfg.shrinkage_enabled,
    )


def _as_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if value is None:
        return None
    text = str(value)[:10]
    try:
        y, m, d = (int(x) for x in text.split("-"))
        return date(y, m, d)
    except ValueError:
        return None


def _ensure_parent_dir(path: Path) -> Path:
    """按需自建父目录（TierState 快照落盘前置；失败如实上抛，禁静默降级到进程内）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _calendar_facts(day: date | None) -> dict[str, Any]:
    """动态层事实：A 股风险日历（MOD-POS-019 纯日期函数，无外部 IO）。"""
    if day is None:
        return {"calendar_block_new": False, "calendar_cap_adjustment": 1.0}
    alert = CalendarPositionConstraint().check(day, positions=[PositionInfo(symbol="")])
    return {
        "calendar_block_new": bool(alert.block_new_positions),
        "calendar_cap_adjustment": float(alert.overall_cap_adjustment),
    }


def _adjudicate_symbols(
    *,
    portfolio: TargetPortfolio,
    strategy_id: str,
    budget: float,
    capital: float,
    portfolio_total: float,
    center: PositionAdjudicationCenter,
    builder: BatchedPositionBuilder,
    strategy_type: str,
    available_cash_provider: AvailableCashProvider | None,
    run_id: str,
) -> tuple[tuple[SymbolPlan, ...], CashSeat]:
    """标的层裁决 + 可用资金裁剪 + 分批计划：TargetPortfolio → (SymbolPlan, CashSeat)。

    权重口径（本件唯一口径，混算即出"假现金位"）：
      - ``tw.target_weight`` 是**绝对组合占比**（StrategyBook 保证 Σ ≤ budget）；
      - ``clip_to_available_capital`` 要的是**钱包内占比**（Σ + CASH = 1）；
      - 故先 ``wallet_w = abs_w / budget`` 送裁剪，裁剪后再乘回 budget 送裁决。
    现金席位：钱包内没投出去的钱必须成为一条可见事实（PFA-2 的病不是持币，
    是"百万现金躺在平钱包里没人知道"）——空仓、可用资金不足、裁决否决三种成因
    都产 CashSeat，cash_weight ≥ CASH_DRAG_WARN_RATIO 由调用方升为 warning。

    注：跨策略同票聚合表 ``symbol_aggregate`` 由 Pass A 权威累计（组合层裁决读它），
    本函数**不再**重复累加——重复累加会让 firm 8% 口径的裁剪力度翻倍。
    """
    wallet_total = float(capital) if capital > 0 else 0.0
    intents = {sym: _clip01(float(tw.target_weight)) for sym, tw in portfolio.positions.items()}
    if not intents:
        return (), CashSeat(
            strategy_id=strategy_id,
            wallet_capital=wallet_total,
            invested_weight=0.0,
            cash_weight=1.0 if wallet_total > 0 else 0.0,
            cash_capital=wallet_total,
            clip_scale=1.0,
        )

    # ① 钱包口径持仓 + 现金席位（Σ ≤ 1，余量=钱包内现金）
    wallet_weights = {
        sym: (w / budget if budget > 0 else 0.0) for sym, w in intents.items()
    }
    holdings: dict[str, float] = dict(wallet_weights)
    holdings["CASH"] = max(0.0, 1.0 - sum(wallet_weights.values()))
    available = (
        float(available_cash_provider(strategy_id, capital))
        if available_cash_provider is not None
        else wallet_total
    )
    if available < 0 or not math.isfinite(available):
        available = 0.0
    # ② 可用资金 pro-rata 削减（41 §3.6）——**必须应用**，否则注入的 T+1 冻结口径无效
    clipped = clip_to_available_capital(holdings, available, wallet_total if wallet_total > 0 else 1.0)
    raw = clipped.get("_degrade_reason")
    degrade = raw if isinstance(raw, str) and raw else None
    target_invest_frac = sum(wallet_weights.values())
    kept_invest_frac = sum(
        float(clipped[s]) for s in clipped if s != "CASH" and not s.startswith("_")
    )
    clip_scale = (kept_invest_frac / target_invest_frac) if target_invest_frac > 0 else 1.0

    plans: list[SymbolPlan] = []
    for sym, tw in portfolio.positions.items():
        intended = _clip01(float(clipped.get(sym, 0.0)) * (budget if budget > 0 else 0.0))
        request = AdjudicationRequest(
            request_id=f"{run_id}:{strategy_id}:{sym}",
            strategy_id=strategy_id,
            symbol=sym,
            action=IntendedAction.OPEN,
            intended_weight=intended,
            context={
                "strategy_effective_budget": budget,
                "wallet_capital": wallet_total,
                "trade_date_run": run_id,
            },
        )
        verdict: AdjudicatedPositionPlan = center.adjudicate(request)
        batches: tuple[dict[str, Any], ...] = ()
        if verdict.allowed and verdict.final_weight > 0:
            plan: BatchedEntryPlan = builder.build_plan(
                symbol=sym,
                total_weight=verdict.final_weight,
                confidence_score_c031=float(getattr(tw, "confidence", DEFAULT_CONFIDENCE)),
                strategy_type=BUILDER_STRATEGY_TYPE.get(strategy_type, "multifactor"),
            )
            batches = tuple(
                {
                    "batch_id": b.batch_id,
                    "weight_fraction": round(float(b.weight_fraction), 6),
                    "trigger_conditions": list(b.trigger_conditions),
                    "status": b.status,
                }
                for b in plan.batches
            )
        plans.append(
            SymbolPlan(
                symbol=sym,
                intended_weight=intended,
                final_weight=_clip01(float(verdict.final_weight)),
                allowed=bool(verdict.allowed),
                adjudication_id=verdict.adjudication_id,
                reason=(verdict.reason or "")[:400],
                confidence=float(getattr(tw, "confidence", DEFAULT_CONFIDENCE)),
                batches=batches,
                degrade_reason=degrade,
            )
        )

    invested_abs = round(sum(p.final_weight for p in plans), 12)
    cash_abs = max(0.0, (budget if budget > 0 else 0.0) - invested_abs)
    cash_capital = round(cash_abs * portfolio_total, 2)
    # 钱包被裁到零（无额度）→ 没有可拖累的现金，不造 100% 现金记录
    cash_weight = (cash_capital / wallet_total) if wallet_total > 0 else 0.0
    return tuple(plans), CashSeat(
        strategy_id=strategy_id,
        wallet_capital=wallet_total,
        invested_weight=invested_abs,
        cash_weight=_clip01(cash_weight),
        cash_capital=cash_capital,
        clip_scale=round(max(0.0, min(1.0, clip_scale)), 8),
        degrade_reason=degrade,
    )


def _shrinkage_row(
    run_id: str,
    day: str,
    cfg: AllocationConfig,
    regime: RegimeInput,
    allocation: Any,
    built: Sequence[StrategyAllocation],
    portfolio_total: float,
    unallocated: float,
    base: BaseWeightTable,
    cash_seats: Sequence[CashSeat] = (),
    cash_drag: float = 0.0,
) -> dict[str, Any]:
    detail = getattr(allocation, "shrinkage_detail", None)
    snapshot = regime.snapshot_shrinkage
    gs = float(getattr(detail, "final_shrinkage", allocation.global_shrinkage))
    sum_eb = round(sum(b.effective_budget for b in built), 10)
    deployed = round(sum(c.invested_weight for c in cash_seats) * portfolio_total, 2)
    return {
        "run_id": run_id,
        "trade_date": day,
        "regime_source_run_id": regime.source_run_id,
        "regime_source_date": regime.source_date.strftime("%Y-%m-%d") if regime.source_date else day,
        "regime_lag_days": int(regime.lag_days),
        "dominant": regime.dominant,
        "max_probability": round(float(regime.max_probability), 8),
        "confidence_signal": round(float(getattr(detail, "confidence_signal", 0.0)), 8),
        "risk_signal": round(float(getattr(detail, "risk_signal", regime.risk_signal)), 8),
        "raw_shrinkage": round(float(getattr(detail, "raw_shrinkage", gs)), 8),
        "global_shrinkage": round(gs, 8),
        "shrinkage_enabled": 1 if cfg.shrinkage_enabled else 0,
        "is_crisis": 1 if regime.is_crisis else 0,
        "risk_signal_source": regime.risk_signal_source,
        "snapshot_shrinkage": snapshot if snapshot is not None else float("nan"),
        "delta_vs_snapshot": round(gs - snapshot, 8) if snapshot is not None else float("nan"),
        "portfolio_total_capital": round(portfolio_total, 2),
        "sum_effective_budget": sum_eb,
        "unallocated_cash": round(unallocated, 2),
        "probs_json": json.dumps(
            {
                "probs": list(regime.probabilities),
                "source_run_id": regime.source_run_id,
                "source_date": regime.source_date.strftime("%Y-%m-%d") if regime.source_date else None,
                "base_weight_plan": base.plan_id,
                # 现金三账（alloc_shrinkage_daily 无对应列，JSON 留痕=跨域改列零侵入）：
                #   unallocated_cash=组合级未分配预备金；cash_drag_capital=钱包级闲置；
                #   deployed_capital=真投出金额。三者相加=portfolio_total 才是对账闭合。
                "cash_seats": [c.as_dict() for c in cash_seats],
                "cash_drag_capital": round(float(cash_drag), 2),
                "deployed_capital": deployed,
                "excluded_members": [
                    {"strategy_id": b.strategy_id, "reason": b.excluded_reason}
                    for b in built
                    if b.excluded_reason
                ],
                "config": cfg.to_dict(),
                "schema_version": SCHEMA_VERSION,
            },
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        ),
        "schema_version": SCHEMA_VERSION,
    }


# ── 事件触发正门（AutoRuntime 事件链唯一入口；本件不注册任何定时器，宪法 §9.3）──

# 可消费的 pipeline_events kind（登记义务见模块报告：pipeline_events.LIGHT_KINDS + 派发分支）
SUPPORTED_EVENT_KINDS: tuple[str, ...] = ("pf_alloc_daily", "sim_ledger_daily")


def _event_attr(event: Any, name: str, default: Any = None) -> Any:
    """事件字段读取（Mapping 与对象两形态鸭子兼容，不绑死具体事件类）。"""
    if isinstance(event, Mapping):
        return event.get(name, default)
    return getattr(event, name, default)


def handle_pf_alloc_daily_event(
    event: Any,
    *,
    config: AllocationConfig | None = None,
    **run_kwargs: Any,
) -> AllocationRunResult:
    """分配链的事件正门：一个事件 = 一个分配周期（节拍由事件链给，不由本件给）。

    PFA-4 缺口 2（"月度再权无调度体"）在此消解：无需月度 cron——SIM 日事件链每交易日
    派发一次，防抖与三级升级由 BudgetChangeHandler 承担（收敛窗口 2/3/4 日）。

    Args:
        event: 领域事件（对象或映射），需含 kind 与 payload.trade_date（或 biz_date）
        config: 运行配置（None=load_allocation_config()）
        **run_kwargs: 透传 run_daily_allocation（reader/sink/alpha_provider/... 测试与影子缝）

    Returns:
        AllocationRunResult（wallet_capital 即账本应开的钱包额度）

    Raises:
        AllocationInputError: kind 不受支持 / payload 缺业务日期（fail-closed，禁静默跳过）
    """
    kind = str(_event_attr(event, "kind", "") or _event_attr(event, "event_kind", "") or "")
    if kind not in SUPPORTED_EVENT_KINDS:
        raise AllocationInputError(
            f"未知事件 kind={kind!r}（本件只认 {SUPPORTED_EVENT_KINDS}）"
            "——不静默跳过：kind 拼错=分配链整日不跑，必须炸在派发处"
        )
    payload = _event_attr(event, "payload", {}) or {}
    if not isinstance(payload, Mapping):
        raise AllocationInputError(f"事件 payload 非映射（got {type(payload).__name__}）")
    trade_date = payload.get("trade_date") or payload.get("biz_date")
    if not trade_date:
        raise AllocationInputError(
            f"{kind} 事件缺 trade_date——禁按墙钟猜交易日（RULE-SCHEMA-TZ 同源纪律）"
        )
    universe = payload.get("universe")
    return run_daily_allocation(
        trade_date,
        universe=list(universe) if universe else None,
        config=config,
        **run_kwargs,
    )


# ── CLI（人工/排障入口；生产触发面是事件链，不是本 CLI）─────────────


def _cli(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MOD-PA-007 分配链装配体（一次性运行，非定时器）")
    ap.add_argument("--date", required=True, help="业务交易日 YYYY-MM-DD")
    ap.add_argument("--no-write", action="store_true", help="只算不落库（影子/排障）")
    ap.add_argument("--strategy-id", action="append", default=None, help="限定策略（可重复）")
    ap.add_argument("--run-suffix", default=None, help="固定 run_id 后缀（复现用）")
    args = ap.parse_args(list(argv) if argv is not None else None)
    universe = None
    if args.strategy_id:
        universe = [{"strategy_id": s, "strategy_type": "多因子"} for s in args.strategy_id]
    result = run_daily_allocation(
        args.date,
        universe=universe,
        write=not args.no_write,
        run_suffix=args.run_suffix,
    )
    print(json.dumps(result.summary(), ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    raise SystemExit(_cli())
