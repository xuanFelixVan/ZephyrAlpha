# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.strategies.event_driven_sleeve_strategy
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.strategies.strategy_base; zephyr.shared.contracts.selection_result; zephyr.intelligence.event_score; zephyr.intelligence.event_anomaly_detector
# [CONSUMERS] zephyr.pf_core.strategies（lazy re-export）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] canonical 输出=权重 dict[str,float]（对齐 StrategyBase）；权重和<=1.0（归一化后 max_single 截顶只减不增）；仅做多（A股不能做空，利空事件只能剔除/回避，event_score 模块不变量同源）；依赖成熟度如实标注：event_score=design 态（MOD-INT-EVENT-SCORE，事件链 NLP 管道未闭环 #ARCH-NLP-PIPELINE-001），event_anomaly_detector=production；本模块 MUST 只被 import 一次（@StrategyRegistry.register 对重复 strategy_id 直接 raise，双注册陷阱见 strategies/__init__.py）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 universe/空 signals->返回空 dict（不抛异常）；单标的 EventScoreError/EventAnomalyError 契约违反->剔除该标的+告警（不整批抛异常）
# [TESTS] tests/pf_core/test_eventdriven_sleeve_strategy.py
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: strategy_implementation
# status: active
# created: "2026-08-21"
# ---

"""
D_PORTFOLIO_CORE — 事件驱动 sleeve 组装策略（CAND-SIG-012 晋升，P0-4① 施工）

组装 intelligence 域组件（直接 import 调用不重复造轮子）：
  - event_score（MOD-INT-EVENT-SCORE，[MATURITY] design——事件链 NLP 管道未闭环，
    登记 #ARCH-NLP-PIPELINE-001；本类按宪章 B-007 testing 封顶，依赖成熟度如实标注）：
    compute_event_score 调度族（业绩类三/双因子、其余五类单因子降级链，
    score 已含 decay_stage_factor × extreme_reaction_modifier，即 21 号 §3.6 L320
    event_impact_score × decay_phase_factor 裁定式）
  - event_anomaly_detector（production）：detect_anomaly 盘中异动确认——
    负向异动（anomaly_type=negative）→ 剔除；正向异动 → 确认保留

过滤（26 号 §2.5 + 21 号 §3.6）：|score|<0.2 噪声不动作；score<0 利空剔除
（A 股不能做空）；单标的契约违反剔除+告警。

urgency=next_open（次日开盘，21 号 L255-259 映射表：T+1 开盘买入，2-3 天收敛）。

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.5/§3.6

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: event_driven_sleeve_strategy.py
# 层: 算法
# - id: A1
#   name_zh: ① EventDrivenSleeveStrategy
#   name_en: EventDrivenSleeveStrategy
#   intro: 事件驱动 sleeve 组装策略——事件冲击评分 × 异动确认取 Top-N。
#   desc: 事件驱动 sleeve 组装策略——事件冲击评分 × 异动确认取 Top-N。 signals 负载约定（dict[str, dict]，键=标的代码）： { "600519":…；公共方法（定义序）: generat…
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: EventDrivenSleeveStrategy
#   downstream: zephyr.pf_core.strategies（lazy re-export）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Final

from zephyr.governance.strategies.strategy_base import (
    StrategyBase,
    StrategyMeta,
    StrategyRegistry,
)
from zephyr.intelligence.event_anomaly_detector import (
    ANOMALY_TYPE_NEGATIVE,
    EventAnomalyError,
    detect_anomaly,
)
from zephyr.intelligence.event_score import (
    SIGNAL_NOISE_THRESHOLD,
    EarningsFactorData,
    EventRecord,
    EventScoreError,
    compute_event_score,
)
from zephyr.shared.contracts.selection_result import (
    URGENCY_NEXT_OPEN,
    SelectionResult,
    SignalInput,
    TargetPosition,
)

# ORPHAN-MODULE 可发现性（2026-08-28，AI-WAVE3A-001）：TYPE_CHECKING 静态引用——
# 仅类型检查期生效，运行时不执行；事件漏斗（MOD-INT_EVENT_FUNNEL，BM-SEL-19 事件侧
# 编排：候选池→过滤→排序→~30）是本策略选股收敛上游，待接线（当前本策略自承载逐标的
# 评分过滤），接线后由 run_event_funnel 输出喂 generate_target_weights。
if TYPE_CHECKING:
    from zephyr.intelligence.event_funnel import EventFunnelResult, run_event_funnel

_logger = logging.getLogger(__name__)


@StrategyRegistry.register
class EventDrivenSleeveStrategy(StrategyBase):
    """事件驱动 sleeve 组装策略——事件冲击评分 × 异动确认取 Top-N。

    signals 负载约定（dict[str, dict]，键=标的代码）：
        {
          "600519": {
            "event": EventRecord 实例或其字段 dict（symbol 自动注入）,  # 必填
            "earnings": EarningsFactorData 实例或字段 dict / None,       # 可选（业绩类）
            "intraday_returns": [分钟级收益率...],                       # 可选（异动确认）
            "benchmark_returns": [基准分钟级收益率...],                  # 可选（与上等长）
          },
        }

    constraints：{"top_n": int=10, "max_single": float=0.10}

    用法：
        strategy = EventDrivenSleeveStrategy()
        weights = strategy.generate_target_weights(universe, signals, constraints)
        result = strategy.select(SignalInput(...))  # → SelectionResult(urgency=next_open)
    """

    meta = StrategyMeta(
        strategy_id="eventdriven-sleeve",
        name="事件驱动sleeve组装策略",
        description="组装事件冲击评分（compute_event_score族）+盘中异动确认，评分降序取Top-N，urgency=next_open",
        strategy_type="equity_long_only",
        version="1.0.0",
        author="zephyr-agent",
        factor_dependencies=[],
        tags=["event_driven", "sleeve", "event_score", "anomaly_confirm", "a_share"],
        supported_markets=["a_share"],
    )

    _URGENCY = URGENCY_NEXT_OPEN

    def generate_target_weights(
        self,
        universe: list[str] | None = None,
        signals: dict[str, dict[str, Any]] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """事件冲击评分逐标的过滤排序，Top-N 按评分比例归一化。

        Returns:
            {symbol: weight}，权重和 <= 1.0。空输入/无有效评分返回 {}。
        """
        if not universe or not signals:
            _logger.debug(
                "eventdriven-sleeve: 空 universe/signals，返回空权重 (universe=%d signals=%d)",
                len(universe or []),
                len(signals or {}),
            )
            return {}

        cons = constraints or {}
        top_n = int(cons.get("top_n", 10))
        max_single = float(cons.get("max_single", 0.10))

        scored: list[tuple[str, float]] = []
        for sym in universe:
            payload = signals.get(sym)
            if not isinstance(payload, dict):
                continue
            score = self._score_symbol(sym, payload)
            if score > 0:
                scored.append((sym, score))

        if not scored:
            _logger.debug("eventdriven-sleeve: 无有效事件评分，返回空权重")
            return {}

        scored.sort(key=lambda x: x[1], reverse=True)
        picks = scored[:top_n]
        total = sum(s for _, s in picks)
        if total <= 0:
            return {}

        # 评分比例归一化（和=1.0）后 max_single 截顶——截顶只减不增，权重和 ≤1.0 不变量成立
        weights = {sym: min(s / total, max_single) for sym, s in picks}

        _logger.info(
            "eventdriven-sleeve: 选出 %d 只（top_n=%d, max_single=%.4f, 权重和=%.4f）",
            len(weights),
            top_n,
            max_single,
            sum(weights.values()),
        )
        return weights

    def _score_symbol(self, symbol: str, payload: dict[str, Any]) -> float:
        """单标的：事件评分 → 噪声/利空过滤 → 异动确认。0.0=剔除。"""
        raw_event = payload.get("event")
        if raw_event is None:
            return 0.0
        event = raw_event if isinstance(raw_event, EventRecord) else EventRecord(symbol=symbol, **raw_event)

        raw_earnings = payload.get("earnings")
        earnings = (
            raw_earnings
            if raw_earnings is None or isinstance(raw_earnings, EarningsFactorData)
            else EarningsFactorData(**raw_earnings)
        )

        try:
            score = compute_event_score(event, earnings)
        except EventScoreError as exc:
            _logger.warning("eventdriven-sleeve: %s 事件评分契约违反，剔除（%s）", symbol, exc)
            return 0.0

        # 噪声不动作 + 利空剔除（A 股不能做空，26 号 §2.5/event_score 模块不变量）
        if score < SIGNAL_NOISE_THRESHOLD:
            return 0.0

        # 异动确认（可选负载）：负向异动→剔除；降级→视为无确认信息放行
        stock_ret = payload.get("intraday_returns")
        bench_ret = payload.get("benchmark_returns")
        if stock_ret is not None and bench_ret is not None:
            try:
                anomaly = detect_anomaly(symbol, stock_ret, bench_ret)
            except EventAnomalyError as exc:
                _logger.warning("eventdriven-sleeve: %s 异动识别契约违反，剔除（%s）", symbol, exc)
                return 0.0
            if not anomaly.degraded and anomaly.is_anomaly and anomaly.anomaly_type == ANOMALY_TYPE_NEGATIVE:
                return 0.0

        return float(score)

    def select(self, signal_input: SignalInput) -> SelectionResult:
        """21 号 §3.5 标准接口：SignalInput → SelectionResult（urgency=next_open）。

        SignalInput.signals 元素约定：dict 且含 "symbol" 键，其余键为事件负载
        （event/earnings/intraday_returns/benchmark_returns）。
        """
        signals_map: dict[str, dict[str, Any]] = {}
        for s in signal_input.signals:
            if isinstance(s, dict) and "symbol" in s:
                signals_map[str(s["symbol"])] = {k: v for k, v in s.items() if k != "symbol"}
        constraints = {"regime_budget": signal_input.regime_budget, **signal_input.metadata}
        weights = self.generate_target_weights(list(signal_input.universe), signals_map, constraints)
        portfolio = [
            TargetPosition(
                symbol=sym,
                target_weight=w,
                signal_source=self.meta.strategy_id,
                urgency=self._URGENCY,
            )
            for sym, w in weights.items()
        ]
        return SelectionResult(
            target_portfolio=portfolio,
            signals=list(signal_input.signals),
            confidence=self._placeholder_confidence(weights),
            metadata={
                "sleeve": "event_driven",
                "urgency": self._URGENCY,
                "dependency_maturity": "event_score=design（#ARCH-NLP-PIPELINE-001 未闭环）",
                "confidence_note": "占位算法（21号§6待裁定-5）：入选标的权重和，非定稿置信度",
            },
        )

    @staticmethod
    def _placeholder_confidence(weights: dict[str, float]) -> float:
        """占位置信度（21 号 §6 待裁定-5：算法未定，先用权重和 ∈[0,1] 占位）。"""
        if not weights:
            return 0.0
        return min(1.0, sum(weights.values()))


__all__: Final = ["EventDrivenSleeveStrategy"]
