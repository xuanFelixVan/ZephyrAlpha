# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.strategies.daban_sleeve_strategy
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.strategies.strategy_base; zephyr.shared.contracts.selection_result; zephyr.signal_ashare.short_term_stock_selector; zephyr.signal_ashare.youzi_relay_emotion_engine; zephyr.signal_ashare.quant_short_term_strength_engine; zephyr.signal_ashare.dual_engine_fusion_decision_engine
# [CONSUMERS] zephyr.pf_core.strategies（lazy re-export）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] canonical 输出=权重 dict[str,float]（对齐 StrategyBase）；权重和<=1.0（归一化后 max_single 截顶只减不增）；仅做多；6类决策优先级权重表与 21号 §3.6 L304-317 一致；本模块 MUST 只被 import 一次（@StrategyRegistry.register 对重复 strategy_id 直接 raise，双注册陷阱见 strategies/__init__.py）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 universe/空 signals->返回空 dict（不抛异常）；payload 缺负载/引擎降级/决策"中性"/final_score<=0->剔除该标的不抛异常
# [TESTS] tests/pf_core/test_daban_sleeve_strategy.py
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: strategy_implementation
# status: active
# created: "2026-08-21"
# ---

"""
D_PORTFOLIO_CORE — 打板 sleeve 组装策略（CAND-SIG-012 晋升，P0-4① 施工）

组装 signal_ashare 四引擎（全部 production，直接 import 调用不重复造轮子）：
  - ShortTermStockSelector（BM-SEL-22，MOD-SIG-023）——资格门：降级/推荐"回避"→剔除
  - YouziRelayEmotionEngine（BM-SEL-23，MOD-SIG-033）——游资情绪 6 因子评分
  - QuantShortTermStrengthEngine（BM-SEL-24，MOD-SIG-034）——量化强度 6 维评级
  - DualEngineFusionDecisionEngine（BM-SEL-25，MOD-SIG-035）——双引擎融合 6 类决策

排序算法（21 号 §3.6 L304-317 施工补全）：
  final_score = fused_score × priority_weight(6类决策)，按 final_score 降序取 Top-N
  （打板 sleeve N≤10 容量硬约束），权重按 final_score 比例归一化到 ≤1.0。

urgency=immediate（盘中立即，21 号 L255-259 映射表：T 日盘中买入，T+1 卖出）。

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.5/§3.6

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: selector 参数
#   fields: 参数 selector（无注解）
#   code: daban_sleeve_strategy.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: youzi_engine 参数
#   fields: 参数 youzi_engine（无注解）
#   code: daban_sleeve_strategy.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: quant_engine 参数
#   fields: 参数 quant_engine（无注解）
#   code: daban_sleeve_strategy.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: fusion_engine 参数
#   fields: 参数 fusion_engine（无注解）
#   code: daban_sleeve_strategy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① DabanSleeveStrategy
#   name_en: DabanSleeveStrategy
#   intro: 打板 sleeve 组装策略——双引擎融合评分 × 6 类决策优先级取 Top-N。
#   desc: 打板 sleeve 组装策略——双引擎融合评分 × 6 类决策优先级取 Top-N。 signals 负载约定（dict[str, dict]，键=标的代码）： { "60051…；公共方法（定义序）: generat…
#   inputs: selector youzi_engine quant_engine fusion_engine
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DabanSleeveStrategy
#   downstream: zephyr.pf_core.strategies（lazy re-export）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from typing import Any, Final

from zephyr.governance.strategies.strategy_base import (
    StrategyBase,
    StrategyMeta,
    StrategyRegistry,
)
from zephyr.shared.contracts.selection_result import (
    URGENCY_IMMEDIATE,
    SelectionResult,
    SignalInput,
    TargetPosition,
)
from zephyr.signal_ashare.dual_engine_fusion_decision_engine import (
    DualEngineFusionDecisionEngine,
    FusionDecisionInput,
)
from zephyr.signal_ashare.quant_short_term_strength_engine import (
    QuantShortTermStrengthEngine,
    QuantStrengthInput,
)
from zephyr.signal_ashare.short_term_stock_selector import (
    ShortTermStockSelector,
    StockSelectionInput,
)
from zephyr.signal_ashare.youzi_relay_emotion_engine import (
    YouziEmotionInput,
    YouziRelayEmotionEngine,
)

_logger = logging.getLogger(__name__)

# 6 类决策优先级权重（21 号 §3.6 L308-315 裁定表：final_score = fusion_score × priority_weight）
# P0 主升龙头 / P1 二进三 / P2 跟风 / P3 复苏 / P4 伪强 / P5 地天反包；"中性"→0 剔除
_DECISION_PRIORITY: dict[str, float] = {
    "主升龙头": 1.0,
    "二进三": 0.85,
    "跟风": 0.65,
    "复苏": 0.50,
    "伪强": 0.30,
    "地天反包": 0.20,
}

_EXCLUDE_RECOMMENDATIONS = ("回避",)  # BM-SEL-22 资格门：回避→剔除


@StrategyRegistry.register
class DabanSleeveStrategy(StrategyBase):
    """打板 sleeve 组装策略——双引擎融合评分 × 6 类决策优先级取 Top-N。

    signals 负载约定（dict[str, dict]，键=标的代码）：
        {
          "600519": {
            "selector": {StockSelectionInput 字段（不含 symbol）, 可选——缺省跳过资格门},
            "youzi": {YouziEmotionInput 字段},
            "quant": {QuantStrengthInput 字段},
            "fusion_context": {FusionDecisionInput 上下文字段（连板数/主线/涨跌幅/风险分）, 可选},
          },
        }

    用法：
        strategy = DabanSleeveStrategy()
        weights = strategy.generate_target_weights(universe, signals, {"top_n": 10, "max_single": 0.15})
        result = strategy.select(SignalInput(...))  # → SelectionResult(urgency=immediate)
    """

    meta = StrategyMeta(
        strategy_id="daban-sleeve",
        name="打板sleeve组装策略",
        description="组装短线选股/游资情绪/量化强度/双引擎融合四引擎，融合评分×6类决策优先级取Top-N，urgency=immediate",
        strategy_type="equity_long_only",
        version="1.0.0",
        author="zephyr-agent",
        factor_dependencies=[],
        tags=["daban", "sleeve", "dual_engine_fusion", "a_share", "limit_up"],
        supported_markets=["a_share"],
    )

    _URGENCY = URGENCY_IMMEDIATE

    def __init__(
        self,
        selector: Any | None = None,
        youzi_engine: Any | None = None,
        quant_engine: Any | None = None,
        fusion_engine: Any | None = None,
    ) -> None:
        # 依赖注入：默认真实四引擎（production），测试注入 fake 隔离（不打网络/DB）
        self._selector = selector or ShortTermStockSelector()
        self._youzi = youzi_engine or YouziRelayEmotionEngine()
        self._quant = quant_engine or QuantShortTermStrengthEngine()
        self._fusion = fusion_engine or DualEngineFusionDecisionEngine()

    def generate_target_weights(
        self,
        universe: list[str] | None = None,
        signals: dict[str, Any] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """四引擎逐标的评分，final_score 降序取 Top-N 按比例归一化。

        Args:
            universe: 候选标的列表（涨停标的+连板梯队，漏斗①产出）。
            signals: {symbol: 引擎输入负载}，形态见类 docstring。
            constraints: {"top_n": int=10（打板容量硬约束 N≤10）, "max_single": float=0.15}

        Returns:
            {symbol: weight}，权重和 <= 1.0。空输入/无有效评分返回 {}。
        """
        if not universe or not signals:
            _logger.debug(
                "daban-sleeve: 空 universe/signals，返回空权重 (universe=%d signals=%d)",
                len(universe or []),
                len(signals or {}),
            )
            return {}

        cons = constraints or {}
        top_n = min(int(cons.get("top_n", 10)), 10)  # 21 号 §3.6：打板 sleeve N≤10 容量硬约束
        max_single = float(cons.get("max_single", 0.15))

        scored: list[tuple[str, float]] = []
        for sym in universe:
            payload = signals.get(sym)
            if not isinstance(payload, dict):
                continue
            score = self._score_symbol(sym, payload)
            if score > 0:
                scored.append((sym, score))

        if not scored:
            _logger.debug("daban-sleeve: 无有效融合评分，返回空权重")
            return {}

        scored.sort(key=lambda x: x[1], reverse=True)
        picks = scored[:top_n]
        total = sum(s for _, s in picks)
        if total <= 0:
            return {}

        # 比例归一化（和=1.0）后 max_single 截顶——截顶只减不增，权重和 ≤1.0 不变量成立
        weights = {sym: min(s / total, max_single) for sym, s in picks}

        _logger.info(
            "daban-sleeve: 选出 %d 只（top_n=%d, max_single=%.4f, 权重和=%.4f）",
            len(weights),
            top_n,
            max_single,
            sum(weights.values()),
        )
        return weights

    def _score_symbol(self, symbol: str, payload: dict[str, Any]) -> float:
        """单标的四引擎流水线：资格门 → 游资/量化评分 → 融合决策 × 优先级权重。"""
        # ① BM-SEL-22 资格门（可选负载）：降级或"回避"→剔除
        selector_fields = payload.get("selector")
        if isinstance(selector_fields, dict):
            sel_res = self._selector.analyze(StockSelectionInput(symbol=symbol, **selector_fields))
            if sel_res.is_degraded or sel_res.recommendation in _EXCLUDE_RECOMMENDATIONS:
                return 0.0

        # ②③ BM-SEL-23/24 双引擎评分
        youzi_res = self._youzi.analyze(YouziEmotionInput(**payload.get("youzi", {})))
        quant_res = self._quant.analyze(QuantStrengthInput(**payload.get("quant", {})))

        # ④ BM-SEL-25 融合决策（降级传播契约：上游降级→融合降级→剔除）
        fusion_res = self._fusion.analyze(
            FusionDecisionInput(
                youzi_result=youzi_res,
                quant_result=quant_res,
                **payload.get("fusion_context", {}),
            )
        )
        if fusion_res.is_degraded:
            return 0.0

        priority = _DECISION_PRIORITY.get(str(fusion_res.decision), 0.0)
        if priority <= 0:
            return 0.0
        return float(fusion_res.fused_score) * priority

    def select(self, signal_input: SignalInput) -> SelectionResult:
        """21 号 §3.5 标准接口：SignalInput → SelectionResult（urgency=immediate）。

        SignalInput.signals 元素约定：dict 且含 "symbol" 键，其余键为引擎输入负载。
        """
        signals_map: dict[str, Any] = {}
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
                "sleeve": "daban",
                "urgency": self._URGENCY,
                "confidence_note": "占位算法（21号§6待裁定-5）：入选标的权重和，非定稿置信度",
            },
        )

    @staticmethod
    def _placeholder_confidence(weights: dict[str, float]) -> float:
        """占位置信度（21 号 §6 待裁定-5：算法未定，先用权重和 ∈[0,1] 占位）。"""
        if not weights:
            return 0.0
        return min(1.0, sum(weights.values()))


__all__: Final = ["DabanSleeveStrategy"]
