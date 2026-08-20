# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md | §M4
# [MODULE] zephyr.experiment_tracking.adapters.strategy_runner_adapter
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.experiment_tracker (get_tracker); typing.TYPE_CHECKING (pf_core 类型仅静态检查，运行时鸭子类型——破 pf_core↔experiment_tracking 循环)
# [CONSUMERS] StrategyRunner 全链路回测入口（track 时 lazy import 调用）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] BacktestResult+StrategyRunnerConfig → 实验跟踪 run（全链路 config 含滑点/手续费细节 + 指标）；tracker 降级 no-op 不抛；lineage tags 串联上游 run_id
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
# I1: result(BacktestResult 鸭子类型) + runner_config(StrategyRunnerConfig,可选: strategy_id/factor_ids/synthesis_method/rebalance_freq/pit_shift/top_n/max_single/backtest_config)
# I2: lineage(上游 run_id 映射,可选)
# F1: _extract_params(全链路配置: 因子/合成/调仓/PIT/成本细节——滑点/手续费来自 backtest_config)
# F2: track_strategy_runner_result(start_run(component=full-chain-backtest) → log_* → run_id)
# O1: run_id（NullBackend="null-run"）
# [/ALGO_FLOW]
"""L_INFRA_TELEMETRY — StrategyRunner 全链路回测 → 实验跟踪语义适配器（50 号 §3 ⑥，M4）。

把一次 ``StrategyRunner.run_backtest`` 产出（BacktestResult）翻译为一个实验跟踪 run：
全链路配置（因子 → 合成 → 策略产权重 → 回测引擎，含滑点/手续费成本细节，50 号 §3 ⑥
接入要求）。运行时全鸭子类型（TYPE_CHECKING 隔离，不 import pf_core 域）。

依据: 50_backtest_observability_workplan §3 ⑥
Version: 0.1.0
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Final

from zephyr.experiment_tracking.experiment_tracker import get_tracker

if TYPE_CHECKING:  # 仅静态类型检查，运行时不 import pf_core/backtest（破循环）
    from zephyr.backtest.core.engine_base import BacktestResult
    from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunnerConfig

__all__: Final = ["track_strategy_runner_result"]

_COMPONENT = "full-chain-backtest"


def track_strategy_runner_result(
    result: "BacktestResult",
    *,
    runner_config: "StrategyRunnerConfig | None" = None,
    lineage: dict[str, str] | None = None,
    extra_tags: dict[str, str] | None = None,
) -> str:
    """把一次 StrategyRunner 全链路回测记录为一个实验跟踪 run。

    Args:
        result: CTR-P1-016 回测结果（鸭子类型）。
        runner_config: 策略运行器配置（可选；None 时跳过链路 params）。
            含因子/合成/调仓/PIT 配置 + backtest_config 成本细节（滑点/手续费）。
        lineage: 上游零件 run_id 映射，写入 tags 串联全链路。
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
    if runner_config is not None:
        params.update(
            {
                "factor_ids": ",".join(runner_config.factor_ids),
                "synthesis_method": runner_config.synthesis_method,
                "rebalance_freq": runner_config.rebalance_freq,
                "pit_shift": runner_config.pit_shift,
                "top_n": runner_config.top_n,
                "max_single": runner_config.max_single,
                "initial_capital": runner_config.initial_capital,
            }
        )
        bt = runner_config.backtest_config
        if bt is not None:
            # 全链路成本细节（50 号 §3 ⑥：含滑点/手续费/冲击成本细节）
            params["commission_rate"] = str(bt.commission_rate)
            params["slippage_bps"] = str(bt.slippage_bps)
            params["benchmark_symbol"] = bt.benchmark_symbol

    metrics: dict[str, float] = {
        "sharpe_ratio": float(result.sharpe_ratio),
        "max_drawdown": float(result.max_drawdown),
        "annual_return": float(result.annual_return),
        "total_return": float(result.total_return),
        "win_rate": float(result.win_rate),
        "trades_count": float(result.trades_count),
    }

    run_name = f"fc_{result.strategy_id}_{datetime.now(UTC):%Y%m%d_%H%M%S}"
    with tracker.start_run(_COMPONENT, run_name=run_name, tags=tags) as run:
        run.log_params(params)
        run.log_metrics(metrics)
    return run.run_id
