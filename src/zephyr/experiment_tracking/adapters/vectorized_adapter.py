# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md | §M4
# [MODULE] zephyr.experiment_tracking.adapters.vectorized_adapter
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.experiment_tracker (get_tracker); typing.TYPE_CHECKING (backtest 类型仅静态检查，运行时鸭子类型——破 backtest↔experiment_tracking 循环)
# [CONSUMERS] 向量化回测入口（track 时 lazy import 调用）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] BacktestResult → 实验跟踪 run（config/指标/净值曲线）；tracker 降级 no-op 不抛；nav_series=None 跳过净值 artifact
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tracking 失败→stderr warning 不抛（不崩回测业务）；run_id 返回（NullBackend 返回 "null-run"）
# [TESTS] tests/experiment_tracking/test_component_adapters.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-OBS-EXP-TRACK-001
# [ALGO_FLOW]
# I1: result(BacktestResult 鸭子类型: strategy_id/start_date/end_date/sharpe_ratio/max_drawdown/annual_return/total_return/win_rate/trades_count)
# I2: config(BacktestConfig,可选: initial_capital/commission_rate/slippage_bps/benchmark_symbol/risk_free_rate) + nav_series(净值序列,可选) + lineage(上游 run_id,可选)
# F1: _extract_params(config 五字段 + 策略 + 日期范围) / _extract_metrics(七项核心指标)
# F2: track_vectorized_backtest(start_run(component=vectorized-backtest) → log_* + nav CSV artifact → run_id)
# O1: run_id（NullBackend="null-run"）
# [/ALGO_FLOW]
"""
L_INFRA_TELEMETRY — vectorized_engine 回测结果 → 实验跟踪语义适配器（50 号 §3 ⑥，M4）。

把一次 ``DefaultBacktestEngine.run`` 产出（BacktestResult）翻译为一个实验跟踪 run：
每次回测的 config + 指标 + 净值曲线（50 号 §3 ⑥ 接入要求）。运行时全鸭子类型
（TYPE_CHECKING 隔离，不 import backtest 域，破包级循环）。

依据: 50_backtest_observability_workplan §3 ⑥
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: result 参数
#   fields: 参数 result，类型注解 BacktestResult
#   code: vectorized_adapter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: vectorized_adapter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: nav_series 参数
#   fields: 参数 nav_series（无注解）
#   code: vectorized_adapter.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: lineage 参数
#   fields: 参数 lineage（无注解）
#   code: vectorized_adapter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① track_vectorized_backtest
#   name_en: track_vectorized_backtest
#   intro: 把一次向量化回测结果记录为一个实验跟踪 run。
#   desc: 把一次向量化回测结果记录为一个实验跟踪 run。 Args: result: CTR-P1-016 回测结果（鸭子类型，读 strategy_id/日期/七项指标）。 confi…；源码 L95-L157
#   inputs: result config nav_series lineage extra_tags
#   outputs: str
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 向量化回测入口（track 时 lazy import 调用）
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

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Final

from zephyr.experiment_tracking.experiment_tracker import get_tracker

if TYPE_CHECKING:  # 仅静态类型检查，运行时不 import backtest（破循环）
    import pandas as pd

    from zephyr.backtest.core.engine_base import BacktestResult
    from zephyr.backtest.implementations.vectorized_engine import BacktestConfig

__all__: Final = ["track_vectorized_backtest"]

_COMPONENT = "vectorized-backtest"


def track_vectorized_backtest(
    result: BacktestResult,
    *,
    config: BacktestConfig | None = None,
    nav_series: pd.Series | None = None,
    lineage: dict[str, str] | None = None,
    extra_tags: dict[str, str] | None = None,
) -> str:
    """把一次向量化回测结果记录为一个实验跟踪 run。

    Args:
        result: CTR-P1-016 回测结果（鸭子类型，读 strategy_id/日期/七项指标）。
        config: 回测配置（可选；None 时跳过 config params）。
        nav_series: 净值曲线（可选；None 时跳过净值 CSV artifact）。
        lineage: 上游零件 run_id 映射（如 {"regime_run_id"/"feature_run_id"}），写入 tags。
        extra_tags: 额外 tags（可选）。

    Returns:
        run_id（NullBackend 返回 "null-run"）。
    """
    tracker = get_tracker()
    tags: dict[str, str] = {
        "component": _COMPONENT,
        "strategy_id": str(result.strategy_id),
    }
    if lineage:
        tags.update({f"lineage_{k}": str(v) for k, v in lineage.items()})
    if extra_tags:
        tags.update({k: str(v) for k, v in extra_tags.items()})

    params: dict[str, Any] = {
        "strategy_id": result.strategy_id,
        "start_date": result.start_date.isoformat() if result.start_date else "",
        "end_date": result.end_date.isoformat() if result.end_date else "",
    }
    if config is not None:
        params.update(
            {
                "initial_capital": str(config.initial_capital),
                "commission_rate": str(config.commission_rate),
                "slippage_bps": str(config.slippage_bps),
                "benchmark_symbol": config.benchmark_symbol,
                "risk_free_rate": float(config.risk_free_rate),
            }
        )

    metrics: dict[str, float] = {
        "sharpe_ratio": float(result.sharpe_ratio),
        "max_drawdown": float(result.max_drawdown),
        "annual_return": float(result.annual_return),
        "total_return": float(result.total_return),
        "win_rate": float(result.win_rate),
        "trades_count": float(result.trades_count),
    }

    run_name = f"vb_{result.strategy_id}_{datetime.now(UTC):%Y%m%d_%H%M%S}"
    with tracker.start_run(_COMPONENT, run_name=run_name, tags=tags) as run:
        run.log_params(params)
        run.log_metrics(metrics)
        if nav_series is not None and len(nav_series) > 0:
            csv_bytes = nav_series.to_csv(index=True, header=["nav"]).encode("utf-8")
            run.log_artifact_bytes(csv_bytes, "nav_curve.csv", artifact_path="nav")
    return run.run_id
