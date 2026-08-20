# [BLUEPRINT] MOD-L05-001 | docs/03_modules/_domain_portfolio_core/blueprint.md
# [MODULE] zephyr.pf_core.topn_momentum_strategy
# [DOMAIN] D_PF_CORE
# [DEPENDENCIES] zephyr.governance.strategies.strategy_base
# [CONSUMERS] zephyr.pf_core.strategy_engine.strategy_runner
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] canonical 输出=权重 dict[str,float]（对齐 StrategyBase + MatchingEngine + EventDrivenEngine 钩子）；权重和<=1.0；多/空仅做多
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 universe/signals->返回空 dict（不抛异常）；信号全 NaN->返回空 dict
# [TESTS] tests/pf_core/test_strategy_runner_mvp.py
# [A_module] module_id=MOD-L05-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: pf_core
# category: strategy_implementation
# status: active
# created: "2026-07-30"
# ---

"""D_PORTFOLIO_CORE — TopN 动量等权策略

截面动量打分取前 N 等权配置。Phase A MVP 证链策略——验证 因子→策略→回测 端到端链路。

设计要点：
  - canonical 输出 = dict[str, float]（目标权重），对齐：
      * StrategyBase.generate_target_weights 抽象声明（dict[str,float]）
      * MatchingEngine.generate_fills(target_weights: dict) 入参
      * EventDrivenEngine.run_tick(strategy_callback)->dict 钩子
  - 三态共用：盘后回测 / 盘中模拟盘 / QMT 实盘 均调本类的 generate_target_weights
  - 不生成 Order（Order 生成下沉到 Phase B ExecutionAdapter，回测路径不需要）
  - signals 已由 StrategyRunner 做 PIT 平移（signal[t]=factor[t-1]），本类不再平移

CTR 契约：
  消费者 — CTR-002 (FactorSignal) ← D_FACTOR（经 StrategyRunner 合成后传入 signals dict）
  消费者 — CTR-003 (RiskLimits) ← D_RISK（经 constraints 传入 max_single）
  生产者 — 目标权重 dict → MatchingEngine（回测）/ ExecutionAdapter（实盘）

SSoT: docs/03_modules/_domain_portfolio_core/blueprint.md
"""

from __future__ import annotations

import logging
import math
from typing import Any, ClassVar

from zephyr.governance.strategies.strategy_base import (
    StrategyBase,
    StrategyMeta,
    StrategyRegistry,
)

_logger = logging.getLogger(__name__)


@StrategyRegistry.register
class TopNMomentumStrategy(StrategyBase):
    """TopN 动量等权策略——截面信号打分取前 N 等权。

    用法：
        strategy = TopNMomentumStrategy()
        weights = strategy.generate_target_weights(
            universe=["600519", "000001", ...],
            signals={"600519": 0.12, "000001": -0.05, ...},
            constraints={"top_n": 10, "max_single": 0.10},
        )
        # weights = {"600519": 0.10, ...}  权重和 <= 1.0
    """

    meta = StrategyMeta(
        strategy_id="topn-momentum",
        name="TopN动量等权策略",
        description="截面动量打分取前N等权，A股多头，Phase A MVP证链策略",
        strategy_type="equity_long_only",
        version="1.0.0",
        author="zephyr-agent",
        factor_dependencies=["momentum_20d"],
        tags=["momentum", "topn", "equal_weight", "a_share", "mvp"],
        supported_markets=["a_share"],
    )

    def generate_target_weights(
        self,
        universe: list[str] | None = None,
        signals: dict[str, float] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, float]:
        """按信号打分取前 N 等权配置。

        Args:
            universe: 候选标的列表（纯数字代码，如 "600519"）
            signals: {symbol: 信号得分}，已由 StrategyRunner 做 PIT 平移。
                     正值=做多信号强度，NaN/缺失=剔除。
            constraints: {"top_n": int=10, "max_single": float=0.10}

        Returns:
            {symbol: weight}，权重和 <= 1.0。空输入返回 {}。
        """
        if not universe or not signals:
            _logger.debug(
                "topn-momentum: 空 universe/signals，返回空权重 (universe=%d signals=%d)",
                len(universe or []),
                len(signals or {}),
            )
            return {}

        cons = constraints or {}
        top_n = int(cons.get("top_n", 10))
        max_single = float(cons.get("max_single", 0.10))

        # 过滤 universe 内、信号存在且非 NaN 的标的，按信号降序排序
        scored: list[tuple[str, float]] = []
        for sym in universe:
            val = signals.get(sym)
            if val is None:
                continue
            try:
                v = float(val)
            except (TypeError, ValueError):
                continue
            if math.isnan(v):
                continue
            scored.append((sym, v))

        if not scored:
            _logger.debug("topn-momentum: 无有效信号，返回空权重")
            return {}

        # 降序取前 top_n
        scored.sort(key=lambda x: x[1], reverse=True)
        picks = [sym for sym, _ in scored[:top_n]]

        if not picks:
            return {}

        weight = min(1.0 / len(picks), max_single)
        weights = {sym: weight for sym in picks}

        _logger.info(
            "topn-momentum: 选出 %d 只（top_n=%d, w=%.4f, max_single=%.4f）",
            len(picks),
            top_n,
            weight,
            max_single,
        )
        return weights

    def validate_constraints(self, weights: dict[str, float]) -> bool:
        """校验权重和 <= 1.0 且单标的 <= max_single（默认 0.10）。"""
        if not weights:
            return True
        if sum(weights.values()) > 1.0 + 1e-9:
            return False
        if any(w > 0.10 + 1e-9 for w in weights.values()):
            return False
        return True


__all__ = ["TopNMomentumStrategy"]
