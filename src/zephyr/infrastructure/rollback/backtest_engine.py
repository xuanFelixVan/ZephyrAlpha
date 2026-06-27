# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md
# [MODULE] zephyr.infrastructure.rollback.backtest_engine
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.rollback.__init__
# [CONSUMERS] MOD-INF-020;MOD-GATE_ENGINE;MOD-INF-022
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Git-native回滚;SQLite Dump Checkpoint;自动回滚
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_core/rollback-system/blueprint.md;src/zephyr/rollback/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] RollbackError;CheckpointError;VerificationError
# [TESTS] tests/test_rollback/
# [A_module] module_id=MOD-INF_backtest_engine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


BENCHMARKS: dict[str, str] = {
    "CSI300": "沪深300",
    "CSI500": "中证500",
    "TREASURY": "国债指数",
}

TARGET_FF: float = 0.70


@dataclass
class BacktestResult:
    annual_return: float = 0.0
    max_drawdown: float = 0.0
    sharpe: float = 0.0
    calmar: float = 0.0
    daily_pnl: list[float] = field(default_factory=list)
    turnover: float = 0.0
    benchmark_vs_csi300: float = 0.0
    benchmark_vs_csi500: float = 0.0
    benchmark_vs_treasury: float = 0.0


@dataclass
class ExecutionSim:
    slippage_bps: float = 2.0
    commission_bps: float = 0.03
    impact_bps: float = 1.0

    def simulate(self, notional: float, side: str = "BUY") -> float:
        cost_bps = self.slippage_bps + self.commission_bps + self.impact_bps
        return notional * (1.0 - cost_bps / 10000.0) if side == "BUY" else notional * (1.0 + cost_bps / 10000.0)


class BacktestEngine:
    def __init__(self) -> None:
        self.exec_sim = ExecutionSim()

    def run(
        self,
        signals: list[dict[str, object]],
        prices: list[float],
    ) -> BacktestResult:
        result = BacktestResult()
        result.daily_pnl = [0.0] * min(len(signals), len(prices))
        return result

    def compare_benchmarks(self, strategy_return: float) -> dict[str, float]:
        return {
            "CSI300_excess": round(strategy_return - 0.08, 4),
            "CSI500_excess": round(strategy_return - 0.10, 4),
            "TREASURY_excess": round(strategy_return - 0.03, 4),
        }


def compute_sharpe(daily_returns: list[float], risk_free: float = 0.03) -> float:
    if not daily_returns:
        return 0.0
    import statistics

    mean = statistics.mean(daily_returns)
    std = statistics.stdev(daily_returns) if len(daily_returns) > 1 else 1e-6
    if std == 0:
        return 0.0
    return (mean - risk_free / 252) / std * (252**0.5)
