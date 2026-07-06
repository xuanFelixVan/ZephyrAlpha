# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.io.backtest_result_sink
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.engine_base
# [CONSUMERS] zephyr.backtest.io.result_repository; zephyr.frontend.dashboard.components.backtest_results
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] PIT铁律(零前瞻偏差); 转换幂等(相同BacktestResult→相同BacktestSinkData)
# [MODIFY-GUARD] no structural changes without owner approval
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BacktestResultSinkError
# [TESTS]
# [A_module] module_id=MOD-BT-001-io-sink | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""backtest_result_sink · 回测结果数据落地模块（v1.3.0 新增，#ARCH-047）

蓝图规格: docs/03_modules/_domain_backtest/blueprint.md §16.7
数据源: D_BACKTEST core/engine_base.py BacktestResult(CTR-P1-016)
产出: BacktestSinkData(可视化数据模型, 供 D_FRONTEND backtest_results 组件渲染)

职责:
  - 从 BacktestResult(CTR-P1-016) 提取回测结果, 转化为前端可视化数据模型 BacktestSinkData
  - 含净值序列/绩效汇总/交易明细等可视化字段
  - 仅做数据提取与转换, 不持久化(持久化由 result_repository.py 负责)

约束:
  - BacktestResult 字段映射必须与 CTR-P1-016 契约冻结字段对齐(15字段)
  - 转换幂等: 相同 BacktestResult 必须产生相同 BacktestSinkData
  - PIT 铁律: equity_curve/trade_log 数据不得引用时序点之后的信息
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from zephyr.backtest.core.engine_base import BacktestResult


class BacktestResultSinkError(Exception):
    """回测结果数据落地错误"""

    error_code = "ZA-BT-0012"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


# ===== 时序数据点 dataclass =====


@dataclass(frozen=True)
class EquityPoint:
    """净值曲线数据点（PIT: timestamp 时刻的 equity 不得引用之后信息）"""
    timestamp: str  # ISO8601
    equity: float


@dataclass(frozen=True)
class TradeRecord:
    """交易记录（PIT: timestamp 时刻的成交信息）"""
    timestamp: str  # ISO8601
    symbol: str
    side: str  # "buy" / "sell"
    price: float
    quantity: int
    commission: float = 0.0


@dataclass(frozen=True)
class DrawdownPoint:
    """回撤曲线数据点"""
    timestamp: str  # ISO8601
    drawdown: float  # 正数小数, 0.2=20%


@dataclass(frozen=True)
class BenchmarkPoint:
    """基准曲线数据点"""
    timestamp: str  # ISO8601
    value: float


# ===== 可视化数据模型 =====


@dataclass(frozen=True)
class BacktestSinkData:
    """回测结果可视化数据模型（#ARCH-047）

    由 sink_backtest_result 从 BacktestResult(CTR-P1-016) 提取转化。
    含净值序列/绩效汇总/交易明细等可视化字段，供 D_FRONTEND backtest_results 组件渲染。

    汇总指标字段与 CTR-P1-016 BacktestResult 15字段对齐。
    时序明细字段为可选, 由调用方在运行时填充(回测引擎产出)。
    """
    # --- 汇总指标（从 BacktestResult 映射, CTR-P1-016 冻结字段）---
    strategy_id: str
    run_id: str  # = BacktestResult.idempotency_key
    start_date: datetime
    end_date: datetime
    total_return: float  # 总收益率(小数, 0.15=15%)
    annual_return: float  # 年化收益率(小数)
    sharpe_ratio: float
    max_drawdown: float  # 正数小数, 0.2=20%
    win_rate: float  # 0.0-1.0
    trades_count: int
    timestamp: datetime  # 回测完成时间戳(UTC)
    overfitting_flag: bool = False
    benchmark_symbol: Optional[str] = None
    schema_version: str = "1.0"

    # --- 时序明细（可选, 由调用方填充）---
    equity_curve: tuple[EquityPoint, ...] = ()
    trade_log: tuple[TradeRecord, ...] = ()
    drawdown_curve: tuple[DrawdownPoint, ...] = ()
    benchmark_curve: tuple[BenchmarkPoint, ...] = ()

    def to_metrics_dict(self) -> dict[str, Any]:
        """提取汇总指标为 dict（供 BacktestRunArtifact.metrics 快照）"""
        return {
            "strategy_id": self.strategy_id,
            "run_id": self.run_id,
            "start_date": self.start_date.isoformat() if self.start_date else "",
            "end_date": self.end_date.isoformat() if self.end_date else "",
            "total_return": self.total_return,
            "annual_return": self.annual_return,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "win_rate": self.win_rate,
            "trades_count": self.trades_count,
            "overfitting_flag": self.overfitting_flag,
            "benchmark_symbol": self.benchmark_symbol,
        }


# ===== 核心转换函数 =====


def sink_backtest_result(
    result: BacktestResult,
    equity_curve: Optional[list[dict[str, Any]]] = None,
    trade_log: Optional[list[dict[str, Any]]] = None,
    drawdown_curve: Optional[list[dict[str, Any]]] = None,
    benchmark_curve: Optional[list[dict[str, Any]]] = None,
) -> BacktestSinkData:
    """从 BacktestResult 提取并转化为可视化数据模型 BacktestSinkData。

    蓝图 §16.7: io/backtest_result_sink.py 详细规格

    Args:
        result: CTR-P1-016 BacktestResult dataclass 实例
        equity_curve: 净值曲线时序数据 [{timestamp: ISO8601, equity: float}, ...]
        trade_log: 交易记录 [{timestamp, symbol, side, price, quantity, commission}, ...]
        drawdown_curve: 回撤曲线 [{timestamp, drawdown}, ...]
        benchmark_curve: 基准曲线 [{timestamp, value}, ...]

    Returns:
        BacktestSinkData(含净值序列/绩效汇总/交易明细等可视化字段)

    Raises:
        BacktestResultSinkError: result 为 None 或关键字段为空

    副作用: 无（纯转换, 不持久化）
    幂等性: 相同 BacktestResult + 相同时序输入 → 相同 BacktestSinkData
    """
    if result is None:
        raise BacktestResultSinkError("BacktestResult 不能为 None")

    if not result.strategy_id:
        raise BacktestResultSinkError("BacktestResult.strategy_id 不能为空")

    if not result.idempotency_key:
        raise BacktestResultSinkError("BacktestResult.idempotency_key 不能为空")

    # 转换时序数据（PIT 铁律: 调用方负责确保时序数据零前瞻偏差）
    equity_points = tuple(EquityPoint(**p) for p in (equity_curve or []))
    trade_records = tuple(TradeRecord(**p) for p in (trade_log or []))
    drawdown_points = tuple(DrawdownPoint(**p) for p in (drawdown_curve or []))
    benchmark_points = tuple(BenchmarkPoint(**p) for p in (benchmark_curve or []))

    return BacktestSinkData(
        strategy_id=result.strategy_id,
        run_id=result.idempotency_key,
        start_date=result.start_date,
        end_date=result.end_date,
        total_return=result.total_return,
        annual_return=result.annual_return,
        sharpe_ratio=result.sharpe_ratio,
        max_drawdown=result.max_drawdown,
        win_rate=result.win_rate,
        trades_count=result.trades_count,
        timestamp=result.timestamp,
        overfitting_flag=result.overfitting_flag,
        benchmark_symbol=result.benchmark_symbol,
        schema_version=result.schema_version,
        equity_curve=equity_points,
        trade_log=trade_records,
        drawdown_curve=drawdown_points,
        benchmark_curve=benchmark_points,
    )


__all__ = [
    "BacktestResultSinkError",
    "EquityPoint",
    "TradeRecord",
    "DrawdownPoint",
    "BenchmarkPoint",
    "BacktestSinkData",
    "sink_backtest_result",
]
