# [BLUEPRINT] MOD-SELL-017 | docs/03_modules/_domain_sell_decision/blueprint.md
# [MODULE] zephyr.sell_decision.core.trade_level_circuit_breaker
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] stdlib
# [CONSUMERS] 策略级仓位缩放链(42号§3.10: budget×position_cap×circuit_breaker_scale×conformal_scale 乘性叠加)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 交易维度熔断(按笔计数, 42号§3.10); 连续2笔亏损起递减减仓(Li 2026 reduction_factor=0.25); 盈利一笔即重置(reset_on_win); min_scale=0.25 减速非停车(与Kill Switch清仓区分); ≥threshold+3 笔阻断新开仓(允许平仓); 策略级独立计数(非账户级)
# [MODIFY-GUARD] 42_sell_flow.md §3.10
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/sell_decision/test_trade_level_circuit_breaker.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: trade_pnl_pct(每笔交易盈亏百分比, 平仓后喂入) + 参数(threshold=2/reduction=0.25/min_scale=0.25/reset_on_win=True, 42号§3.10 Li 2026 实证)
# F1: on_trade_close(pnl)——负盈亏累计连亏计数; 正盈亏重置(reset_on_win); 零盈亏不动
# F2: get_position_scale()——连亏≥threshold 起 scale=1.0-(1+excess)×0.25, 下限 0.25
# F3: is_blocked()——连亏≥threshold+3 暂停该策略开新仓(只允许平仓)
# O1: 仓位缩放因子 [0.25, 1.0] + 阻断标记 -> 策略级仓位合成链
# [/ALGO_FLOW]
"""D_SELL_DECISION — 交易级连续亏损熔断（42 号 §3.10，AI-NIGHT-001 包P）。

时间熔断（日度/Kill Switch）在"每天小亏、连续多天"场景反应迟钝；本类按笔
计数——策略连续亏损 N 笔即递减减仓，是时间熔断的前馈补充（42 号 §3.10）。
参数真源：Li, Laryea & Ihlamur 2026（arXiv:2604.27150）网格最优
（N=2 / reduction_factor=0.25）+ A 股适配（min_scale=0.25 减速非停车）。
与 CUSUM 正交：本类管短期失配"急救减仓"，CUSUM 管结构性衰减"诊断停研"。
"""

from __future__ import annotations


class TradeLevelCircuitBreaker:
    """策略级连续亏损熔断：连续 N 笔亏损→递减减仓，盈利→重置（42 号 §3.10 施工算法）。"""

    def __init__(
        self,
        consecutive_loss_threshold: int = 2,
        reduction_factor: float = 0.25,
        min_scale: float = 0.25,
        reset_on_win: bool = True,
    ):
        self.consecutive_losses = 0
        self.consecutive_loss_threshold = consecutive_loss_threshold  # Li 2026: N=2
        self.reduction_factor = reduction_factor  # Li 2026: 0.25 per step
        self.min_scale = min_scale  # 最低降至 25%（减速非停车，与 Kill Switch 清仓区分）
        self.reset_on_win = reset_on_win  # 盈利一笔即重置（快速恢复）

    def on_trade_close(self, trade_pnl_pct: float) -> None:
        """每笔交易平仓后更新连续亏损计数（零盈亏不增不减——非亏非赢证据不足）。"""
        if trade_pnl_pct < 0:
            self.consecutive_losses += 1
        elif self.reset_on_win and trade_pnl_pct > 0:
            self.consecutive_losses = 0  # 盈利重置

    def get_position_scale(self) -> float:
        """返回当前仓位缩放因子 [min_scale, 1.0]。"""
        if self.consecutive_losses < self.consecutive_loss_threshold:
            return 1.0  # 未触发
        # 每超 1 笔减 reduction_factor，最低 min_scale
        excess = self.consecutive_losses - self.consecutive_loss_threshold
        scale = max(1.0 - (1 + excess) * self.reduction_factor, self.min_scale)
        return scale

    def is_blocked(self) -> bool:
        """连续亏损超 threshold+3 → 暂停该策略开新仓（只允许平仓，等 CUSUM 判定）。"""
        return self.consecutive_losses >= self.consecutive_loss_threshold + 3


__all__ = ["TradeLevelCircuitBreaker"]
