# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.strategies.multifactor_sleeve_strategy
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.strategies.strategy_base; zephyr.shared.contracts.selection_result; zephyr.factor.analysis.multifactor_synthesis; zephyr.factor.analysis.ic_ir_calc
# [CONSUMERS] zephyr.pf_core.strategies（lazy re-export）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] canonical 输出=权重 dict[str,float]（对齐 StrategyBase）；权重和<=1.0（top-N 等权 min(1/N, max_single)）；仅做多；IC 权重由 ic_ir_calc 离线产出经 constraints 注入（PIT 铁律 INV-004：合成仅用同期因子值，IC 权重来自历史 IC）；本模块 MUST 只被 import 一次（@StrategyRegistry.register 对重复 strategy_id 直接 raise，双注册陷阱见 strategies/__init__.py）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 universe/空 signals->返回空 dict（不抛异常）；截面全 NaN->返回空 dict
# [TESTS] tests/pf_core/test_multifactor_sleeve_strategy.py
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: strategy_implementation
# status: active
# created: "2026-08-21"
# ---

"""D_PORTFOLIO_CORE — 多因子 sleeve 组装策略（CAND-SIG-012 晋升，P0-4① 施工）

组装 factor 域 production 组件（直接 import 调用不重复造轮子）：
  - multifactor_synthesis（MOD-L02-011）：synthesize_equal_weight / synthesize_ic_weighted
    横截面多因子合成，产出 pd.Series 综合打分
  - ic_ir_calc（MOD-L02-011 依赖）：compute_ic_ir_table 批量 IC/IR 评估，
    离线产出 ic_weights 经 constraints 注入（本类不直连数据层，保持纯函数可测）

排序（21 号 §3.6 L319）：横截面因子打分降序（IC 加权，G09），Top-N 等权归一化，
受 budget 约束（regime_budget 经 constraints 透传，精仓位在 firm 层，21 号 §3.7）。

urgency=gradual（逐步建仓，21 号 L255-259 映射表：T+1 起 3-5 天逐步建仓）。

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/21_stock_selection_engine.md §3.5/§3.6
"""

from __future__ import annotations

import logging
from typing import Any, Final

from zephyr.factor.analysis.ic_ir_calc import compute_ic_ir_table
from zephyr.factor.analysis.multifactor_synthesis import synthesize
from zephyr.governance.strategies.strategy_base import (
    StrategyBase,
    StrategyMeta,
    StrategyRegistry,
)
from zephyr.shared.contracts.selection_result import (
    URGENCY_GRADUAL,
    SelectionResult,
    SignalInput,
    TargetPosition,
)

_logger = logging.getLogger(__name__)


@StrategyRegistry.register
class MultifactorSleeveStrategy(StrategyBase):
    """多因子 sleeve 组装策略——横截面多因子合成打分取 Top-N 等权。

    signals 负载约定（dict[str, dict[str, float]]，键=标的代码）：
        {"600519": {"momentum_20d": 0.12, "roe_ttm": 0.08, ...}, ...}
        内层 dict 键=factor_id，值=该标的同期因子值（PIT 平移由上游完成，本类不平移）。

    constraints：
        method     合成方法 "equal_weight"（默认）/"ic_weighted"/"regression"
        ic_weights {factor_id: 历史 IC 均值权重}，method=ic_weighted 时必需，
                   由 compute_ic_weights()（ic_ir_calc 薄封装）离线产出
        top_n      入选数，默认 20
        max_single 单标的权重上限，默认 0.10

    用法：
        strategy = MultifactorSleeveStrategy()
        weights = strategy.generate_target_weights(universe, signals, {"method": "ic_weighted", "ic_weights": w})
        result = strategy.select(SignalInput(...))  # → SelectionResult(urgency=gradual)
    """

    meta = StrategyMeta(
        strategy_id="multifactor-sleeve",
        name="多因子sleeve组装策略",
        description="横截面多因子合成（等权/IC加权）打分取Top-N等权归一化，urgency=gradual",
        strategy_type="equity_long_only",
        version="1.0.0",
        author="zephyr-agent",
        factor_dependencies=[],
        tags=["multifactor", "sleeve", "cross_section", "ic_weighted", "a_share"],
        supported_markets=["a_share"],
    )

    _URGENCY = URGENCY_GRADUAL

    def generate_target_weights(
        self,
        universe: list[str] | None = None,
        signals: dict[str, dict[str, float]] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """横截面多因子合成打分，降序取 Top-N 等权归一化。

        Returns:
            {symbol: weight}，权重和 <= 1.0。空输入/截面无有效打分返回 {}。
        """
        if not universe or not signals:
            _logger.debug(
                "multifactor-sleeve: 空 universe/signals，返回空权重 (universe=%d signals=%d)",
                len(universe or []),
                len(signals or {}),
            )
            return {}

        import pandas as pd  # 函数级 import：模块导入期不引 pandas（轻量启动契约）

        cons = constraints or {}
        method = str(cons.get("method", "equal_weight"))
        ic_weights = dict(cons.get("ic_weights", {}))
        top_n = int(cons.get("top_n", 20))
        max_single = float(cons.get("max_single", 0.10))

        # 透视 {symbol: {factor_id: value}} → {factor_id: pd.Series(symbol→value)}（仅 universe 内标的）
        factor_ids: list[str] = sorted({fid for per_sym in signals.values() if isinstance(per_sym, dict) for fid in per_sym})
        factor_values: dict[str, Any] = {}
        for fid in factor_ids:
            series = pd.Series(
                {
                    sym: float(signals[sym][fid])
                    for sym in universe
                    if isinstance(signals.get(sym), dict) and signals[sym].get(fid) is not None
                },
                dtype=float,
            )
            if not series.empty:
                factor_values[fid] = series

        if not factor_values:
            _logger.debug("multifactor-sleeve: 无有效因子值，返回空权重")
            return {}

        scores = synthesize(factor_values, method=method, ic_weights=ic_weights)
        scores = scores.dropna().sort_values(ascending=False)
        if scores.empty:
            _logger.debug("multifactor-sleeve: 截面打分全 NaN，返回空权重")
            return {}

        picks = list(scores.index[:top_n])
        if not picks:
            return {}

        weight = min(1.0 / len(picks), max_single)
        weights = {sym: weight for sym in picks}

        _logger.info(
            "multifactor-sleeve: 选出 %d 只（method=%s, top_n=%d, w=%.4f）",
            len(picks),
            method,
            top_n,
            weight,
        )
        return weights

    @staticmethod
    def compute_ic_weights(
        factor_ids: list[str],
        symbols: list[str],
        start: str,
        end: str,
        horizon: int = 5,
    ) -> dict[str, float]:
        """IC 权重离线产出路径（ic_ir_calc 薄封装）：{factor_id: ic_mean}。

        供调用方在盘后批量计算后注入 constraints["ic_weights"]；本方法触数据层
        （evaluate_factor），测试不打本路径——经 monkeypatch compute_ic_ir_table 隔离。
        """
        table = compute_ic_ir_table(factor_ids, symbols, start, end, horizon=horizon)
        return {str(row["factor_id"]): float(row["ic_mean"]) for _, row in table.iterrows()}

    def select(self, signal_input: SignalInput) -> SelectionResult:
        """21 号 §3.5 标准接口：SignalInput → SelectionResult（urgency=gradual）。

        SignalInput.signals 元素约定：dict 且含 "symbol" 键 + "factors" 子 dict
        （{factor_id: 因子值}）；合成方法/IC 权重经 SignalInput.metadata 透传。
        """
        signals_map: dict[str, dict[str, float]] = {}
        for s in signal_input.signals:
            if isinstance(s, dict) and "symbol" in s and isinstance(s.get("factors"), dict):
                signals_map[str(s["symbol"])] = dict(s["factors"])
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
                "sleeve": "multifactor",
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


__all__: Final = ["MultifactorSleeveStrategy"]
