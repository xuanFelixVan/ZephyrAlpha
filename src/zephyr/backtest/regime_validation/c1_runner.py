# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.regime_validation.c1_runner
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.regime_validation.c1_comparator; zephyr.backtest.regime_validation.shrinkage_provider; zephyr.backtest.implementations.shrinkage_engine; zephyr.backtest.implementations.vectorized_engine; zephyr.pf_core.strategy_engine.strategy_runner; zephyr.experiment_tracking.adapters.c1_adapter (lazy: track=True only)
# [CONSUMERS] 11_regime_backtest_validation_plan Phase 1 验证执行 ; scripts/regime/run_c1.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 开/关两组除 Shrinkage 外全等(同config/数据/信号); mock模式不依赖特征管道; regime模式用预计算序列(PIT as-of join); 报告落盘幂等
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] C1RunnerError(ZA-BT-0025); 数据/信号为空->返回空 C1ComparisonResult(不抛)
# [TESTS] tests/backtest/test_c1_runner.py
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #11_regime_backtest_validation_plan #ARCH-REGIME-VALIDATION-001 #ARCH-REGIME-C1-RUNNER-001 #ARCH-OBS-EXP-TRACK-001 #C1-shrinkage-comparator

"""L_BACKTEST — C1 Shrinkage 开/关对比执行器 (11_regime_backtest_validation_plan Phase 1 入口)

编排 C1ShrinkageComparator.compare() 的执行层，提供两种 Shrinkage 供给模式：

  ① mock 模式（run_c1_mock）—— 不依赖特征管道，立即可跑
     - build_volatility_schedule 从 data OHLCV 算市场等权实现波动率（年化）
     - MockShrinkageProvider 波动率 4 档映射驱动（vol<15%→1.0 / 15-25%→0.85 /
       25-40%→0.6 / ≥40%→0.3），模拟 regime 防御行为
     - 用途：C1 开/关对比流程冒烟跑通 + 框架正确性验证
     - 局限：mock 是规则映射非 HMM 概率，C1 结果无 regime 部署决策价值（仅验证流程）

  ② regime 模式（run_c1_regime）—— 特征管道就绪后切换
     - RegimeSeriesOrchestrator 产出 [(date, ShrinkageResult)]（由 MOD-REGIME-002 提供）
     - build_schedule_from_results → ScheduleShrinkageProvider（PIT as-of join）
     - 用途：真实 C1 开/关对比，Phase 1 裁决依据

设计要点:
  - 核心入口 run_c1_with_provider 直接复用 C1ShrinkageComparator.compare()，后者内部
    自动跑基准组(ConstShrinkageProvider(1.0)) + 实验组(传入 provider) 两组回测并裁定
  - 依赖方向 backtest→regime 单向（#ARCH-REGIME-VALIDATION-001），本模块在 backtest 域
    编排，避免 regime→backtest 反向循环依赖
  - mock/regime 两模式共用同一 compare() 管线，切换 provider 即可，回测/裁定逻辑零差异
  - 报告落盘幂等：同输入同输出（C1ComparisonResult 不可变）

依据: 11_regime_backtest_validation_plan §4.3/§5/§6（C1 一票否决 + Phase 1 顺序）
SSoT: depgraph MOD-BT-001 / MOD-REGIME-001 / MOD-REGIME-002
Version: 0.1.0
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

from zephyr.backtest.implementations.vectorized_engine import BacktestConfig
from zephyr.backtest.regime_validation.c1_comparator import (
    C1ComparisonResult,
    C1Config,
    C1ShrinkageComparator,
)
from zephyr.backtest.regime_validation.shrinkage_provider import (
    MockShrinkageProvider,
    ScheduleShrinkageProvider,
    build_schedule_from_results,
)

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

__backtest_id__ = "c1-runner"


class C1RunnerError(ZephyrBaseError):
    """ZA-BT-0025: C1 执行器错误（数据非法/报告落盘失败）。

    改号留痕：原 ZA-BT-0012 与 backtest_result_sink.BacktestResultSinkError 重码，
    #ARCH-ERRCODE-001 裁定 git 首引入者保留 canonical，本类后引入（2026-08-07）改号。
    """

    error_code = "ZA-BT-0025"


# ──────────────────────────────────────────────────────────────────────────────
# 波动率序列构造（mock 模式用，不依赖特征管道）
# ──────────────────────────────────────────────────────────────────────────────


def build_volatility_schedule(
    data: pd.DataFrame,
    window: int = 20,
    trading_days_per_year: int = 252,
) -> dict[datetime, float]:
    """从 OHLCV data 构造市场等权实现波动率序列（年化）。

    把 data 视为全市场标的池，逐日算等权截面日收益率（≈等权指数收益率），
    再取 rolling(window).std() × √(年化天数) 得年化实现波动率。供
    MockShrinkageProvider 波动率 4 档映射驱动 Shrinkage。

    Args:
        data: MultiIndex(symbol/trade_date, 含 'close' 列) OHLCV。来自
            StrategyRunner.build_weight_panel / load_history。
        window: 实现波动率滚动窗口（交易日，默认 20）。
        trading_days_per_year: 年化因子（默认 252）。

    Returns:
        {datetime: 年化波动率}（dropna 后）。空 data → 空dict。
    """
    if data is None or data.empty or "close" not in data.columns:
        return {}

    close = data["close"]
    # 提取 date×symbol close 面板（兼容 symbol 在任意 level）
    if "symbol" in (close.index.names or []):
        panel = close.unstack(level="symbol")
    elif "trade_date" in (close.index.names or []):
        panel = close.unstack(level="trade_date").T
    else:
        panel = close.unstack(level=-1)

    daily_returns = panel.pct_change()
    # 等权截面均值 = 等权指数日收益率
    market_returns = daily_returns.mean(axis=1)
    vol = market_returns.rolling(window).std() * np.sqrt(trading_days_per_year)
    vol = vol.dropna()
    if vol.empty:
        return {}

    return {
        pd.Timestamp(ts).to_pydatetime(): float(v)
        for ts, v in vol.items()
        if np.isfinite(v)
    }


# ──────────────────────────────────────────────────────────────────────────────
# tracking 适配（track=True 时 lazy import c1_adapter，破 backtest↔experiment_tracking 循环）
# ──────────────────────────────────────────────────────────────────────────────


def _track_result(
    result: C1ComparisonResult,
    *,
    comparator: C1ShrinkageComparator,
    mode: str,
    strategy_name: str,
) -> None:
    """track=True 时把 C1 结果记录为实验跟踪 run（lazy import 破循环）。

    仅在 track=True 分支内 import `c1_adapter.track_c1_result`，避免 backtest →
    experiment_tracking 包级强依赖（adapter 仅 TYPE_CHECKING 引用 backtest 类型）。
    tracking 任何失败由 adapter 内 RunContext try/except 兜住，不抛、不崩 C1 业务。
    """
    try:
        from zephyr.experiment_tracking.adapters.c1_adapter import track_c1_result
    except ImportError as e:  # pragma: no cover — experiment_tracking 缺失时降级
        _logger.warning("track=True 但 experiment_tracking 不可用(%s)，跳过 tracking", e)
        return
    try:
        track_c1_result(
            result, comparator=comparator, mode=mode, strategy_name=strategy_name
        )
    except Exception as e:  # noqa: BLE001 — tracking 失败不崩 C1 业务
        _logger.warning("C1 结果 tracking 失败(忽略): %s", e)


# ──────────────────────────────────────────────────────────────────────────────
# 核心入口：用任意 provider 跑 C1 开/关对比
# ──────────────────────────────────────────────────────────────────────────────


def run_c1_with_provider(
    data: pd.DataFrame,
    signals: pd.DataFrame,
    shrinkage_provider: Any,
    backtest_config: Optional[BacktestConfig] = None,
    c1_config: Optional[C1Config] = None,
    strategy_name: str = "c1-shrinkage",
    initial_capital: Optional[float] = None,
    track: bool = False,
    mode: str = "provider",
) -> C1ComparisonResult:
    """核心：用给定 shrinkage_provider 跑 C1 开/关对比。

    直接复用 C1ShrinkageComparator.compare()——后者内部自动跑基准组
    (ConstShrinkageProvider(1.0)) + 实验组(传入 provider) 两组回测并裁定四项
    一票否决。mock/regime 两模式共用此入口，仅 provider 不同。

    Args:
        data: OHLCV（MultiIndex symbol/trade_date，同 DefaultBacktestEngine.run）。
        signals: 信号 DataFrame（date × symbol，目标权重）。
        shrinkage_provider: 实验组（开）的 Shrinkage 供给方。
            mock 模式传 MockShrinkageProvider；regime 模式传 ScheduleShrinkageProvider。
        backtest_config: 回测配置（两组共用）。None 用默认 BacktestConfig()。
        c1_config: C1 门槛配置。None 用默认 C1Config()（11_regime_backtest_validation_plan §5 标准）。
        strategy_name: 策略名（两组共用）。
        initial_capital: 初始资金（两组共用，None 用 config 值）。
        track: True 时把结果记录为实验跟踪 run（lazy import c1_adapter，失败不崩业务）。
        mode: tracking 标签（"mock"/"regime"/"provider"），写入 tags 供筛选。

    Returns:
        C1ComparisonResult（含四项 metric_verdicts + passed + veto_reason + summary）。
        数据/信号为空时返回 passed=False 的空结果（不抛异常）。
    """
    if data is None or data.empty or signals is None or signals.empty:
        _logger.warning("run_c1_with_provider: data/signals 为空，跳过 C1 对比")
        return _empty_c1_result()

    cfg = backtest_config or BacktestConfig()
    comparator = C1ShrinkageComparator(config=c1_config or C1Config())
    result = comparator.compare(
        data=data,
        signals=signals,
        shrinkage_provider=shrinkage_provider,
        backtest_config=cfg,
        strategy_name=strategy_name,
        initial_capital=initial_capital,
    )
    if track:
        _track_result(result, comparator=comparator, mode=mode, strategy_name=strategy_name)
    return result


# ──────────────────────────────────────────────────────────────────────────────
# mock 模式：波动率驱动（不依赖特征管道，立即可跑）
# ──────────────────────────────────────────────────────────────────────────────


def run_c1_mock(
    data: pd.DataFrame,
    signals: pd.DataFrame,
    backtest_config: Optional[BacktestConfig] = None,
    c1_config: Optional[C1Config] = None,
    vol_window: int = 20,
    strategy_name: str = "c1-mock",
    track: bool = False,
) -> C1ComparisonResult:
    """冒烟模式：用 MockShrinkageProvider（波动率 4 档映射）跑 C1。

    从 data 算市场等权实现波动率序列 → MockShrinkageProvider 映射为 Shrinkage
    （vol<15%→1.0 / 15-25%→0.85 / 25-40%→0.6 / ≥40%→0.3）→ C1 开/关对比。

    **不依赖特征管道**——波动率从 data OHLCV 直接算。用途：C1 流程冒烟跑通 +
    框架正确性验证。C1 结果无 regime 部署决策价值（mock 是规则映射非 HMM 概率）。

    Args:
        data/signals/backtest_config/c1_config: 同 run_c1_with_provider。
        vol_window: 实现波动率窗口（默认 20）。
        strategy_name: 策略名。
        track: True 时把结果记录为实验跟踪 run（mode="mock"）。

    Returns:
        C1ComparisonResult。
    """
    vol_schedule = build_volatility_schedule(data, window=vol_window)
    if not vol_schedule:
        _logger.warning("run_c1_mock: 波动率序列为空，实验组将退化为满部署（C1 无意义）")
    provider = MockShrinkageProvider(volatility_schedule=vol_schedule)
    return run_c1_with_provider(
        data=data,
        signals=signals,
        shrinkage_provider=provider,
        backtest_config=backtest_config,
        c1_config=c1_config,
        strategy_name=strategy_name,
        track=track,
        mode="mock",
    )


# ──────────────────────────────────────────────────────────────────────────────
# regime 模式：真实 RegimeDetector 预计算序列（特征管道就绪后用）
# ──────────────────────────────────────────────────────────────────────────────


def run_c1_regime(
    data: pd.DataFrame,
    signals: pd.DataFrame,
    regime_results: list[tuple[datetime, Any]],
    backtest_config: Optional[BacktestConfig] = None,
    c1_config: Optional[C1Config] = None,
    strategy_name: str = "c1-regime",
    track: bool = False,
) -> C1ComparisonResult:
    """真实模式：用 RegimeDetector 预计算序列跑 C1（Phase 1 裁决依据）。

    regime_results 由 RegimeSeriesOrchestrator（MOD-REGIME-002）产出，含逐日
    ShrinkageResult（HMM ConfidenceSignal 节流版，A1 阶段）。经
    build_schedule_from_results 转 {date: shrinkage} → ScheduleShrinkageProvider
    （PIT as-of join，不查未来）→ C1 开/关对比。

    Args:
        data/signals/backtest_config/c1_config: 同 run_c1_with_provider。
        regime_results: [(date, ShrinkageResult), ...] 或 [(date, float), ...]。
            由 RegimeSeriesOrchestrator.run() 产出（特征管道就绪后）。
        strategy_name: 策略名。

    Returns:
        C1ComparisonResult（Phase 1 裁决依据）。
    """
    if not regime_results:
        _logger.warning("run_c1_regime: regime_results 为空，退化为满部署（C1 无意义）")
    schedule = build_schedule_from_results(regime_results)
    provider = ScheduleShrinkageProvider(schedule)
    return run_c1_with_provider(
        data=data,
        signals=signals,
        shrinkage_provider=provider,
        backtest_config=backtest_config,
        c1_config=c1_config,
        strategy_name=strategy_name,
        track=track,
        mode="regime",
    )


# ──────────────────────────────────────────────────────────────────────────────
# 端到端：build_weight_panel → C1 对比
# ──────────────────────────────────────────────────────────────────────────────


def run_c1_end_to_end(
    symbols: list[str],
    start: str,
    end: str,
    runner_config: Any,
    mode: str = "mock",
    regime_results: Optional[list[tuple[datetime, Any]]] = None,
    track: bool = False,
) -> C1ComparisonResult:
    """端到端：StrategyRunner.build_weight_panel → C1 开/关对比。

    Args:
        symbols: 标的代码列表（可带后缀 "600519.SH"）。
        start/end: 起止日期 "YYYY-MM-DD"。
        runner_config: StrategyRunnerConfig（含 strategy_id/factor_ids/...）。
        mode: "mock"=波动率驱动冒烟 / "regime"=真实 RegimeDetector 序列。
        regime_results: mode="regime" 时必填，由 RegimeSeriesOrchestrator 产出。

    Returns:
        C1ComparisonResult。

    Raises:
        C1RunnerError: mode 非法或 regime 模式缺 regime_results。
    """
    if mode not in ("mock", "regime"):
        raise C1RunnerError(f"mode 须为 'mock'/'regime', got '{mode}'")
    if mode == "regime" and not regime_results:
        raise C1RunnerError("regime 模式须提供 regime_results（由 RegimeSeriesOrchestrator 产出）")

    # lazy import 避免模块加载时拉入 factor/backtest 重依赖链
    from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner

    runner = StrategyRunner()
    data, signals = runner.build_weight_panel(symbols, start, end, runner_config)
    if signals.empty or data.empty:
        _logger.warning("run_c1_end_to_end: build_weight_panel 返回空 (symbols=%d)", len(symbols))
        return _empty_c1_result()

    # level 名适配（trade_date → date，同 StrategyRunner.run_backtest）
    if isinstance(data.index, pd.MultiIndex) and "trade_date" in (data.index.names or []):
        data.index = data.index.rename({"trade_date": "date"})

    bt_config = runner_config.backtest_config or BacktestConfig(
        initial_capital=Decimal(str(runner_config.initial_capital))
    )

    if mode == "mock":
        return run_c1_mock(data=data, signals=signals, backtest_config=bt_config, track=track)
    return run_c1_regime(
        data=data, signals=signals, regime_results=regime_results or [],
        backtest_config=bt_config, track=track,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 报告落盘
# ──────────────────────────────────────────────────────────────────────────────


def save_c1_report(
    result: C1ComparisonResult,
    output_path: str | Path,
    mode: str = "mock",
    meta: Optional[dict[str, Any]] = None,
) -> str:
    """C1ComparisonResult → markdown 报告落盘（幂等）。

    Args:
        result: C1 开/关对比结果。
        output_path: 输出文件路径（.md）。
        mode: "mock"/"regime"，写入报告头（标注数据来源）。
        meta: 额外元信息（如 symbols/start/end/strategy_id），写入报告头。

    Returns:
        落盘文件绝对路径。
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    verdict = "✅ 通过" if result.passed else "❌ 一票否决"
    lines: list[str] = [
        "# C1 Shrinkage 开/关对比报告",
        "",
        f"- **模式**: {mode}（{'mock 波动率驱动' if mode == 'mock' else '真实 RegimeDetector 序列'}）",
        f"- **裁定**: {verdict}",
        f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    if mode == "mock":
        # 治本补强（#ARCH-REGIME-C1-RUNNER-001 裁定②）：mock 报告显式警示，防误用做部署决策
        lines.extend([
            "",
            "> ⚠️ **mock 模式警示**：本报告用波动率规则映射驱动 Shrinkage（非 HMM 概率），"
            "C1 结果**无 regime 部署决策价值**，仅验证开/关对比流程管线正确性。"
            "Phase 1 裁决须用 `run_c1_regime`（真实 RegimeDetector 序列）产出的报告。",
        ])
    if meta:
        for k, v in meta.items():
            lines.append(f"- **{k}**: {v}")
    lines.append("")

    if not result.passed and result.veto_reason:
        lines.extend([
            "## ⚠️ 一票否决原因",
            "",
            f"> {result.veto_reason}",
            "",
            "C1 不通过 = regime 检测器不部署（回退静态等权，11_regime_backtest_validation_plan §6）。",
            "",
        ])

    lines.extend(["## 四项指标判定", "", "| 指标 | 关(基准) | 开(实验) | 门槛 | 判定 |",
                  "|---|---|---|---|---|"])
    for v in result.metric_verdicts:
        flag = "✅" if v.passed else "❌"
        lines.append(
            f"| {v.name} | {v.baseline_value:.4f} | {v.experiment_value:.4f} "
            f"| {v.threshold_desc} | {flag} |"
        )
    lines.append("")

    lines.extend(["## 指标明细", ""])
    for v in result.metric_verdicts:
        lines.append(f"- **{v.name}**: {v.detail}")
    lines.append("")

    lines.extend([
        "## 回测结果摘要",
        "",
        "| 指标 | 关(基准组) | 开(实验组) |",
        "|---|---|---|",
        f"| Sharpe | {result.baseline_result.sharpe_ratio:.4f} | {result.experiment_result.sharpe_ratio:.4f} |",
        f"| MaxDD | {result.baseline_result.max_drawdown:.4f} | {result.experiment_result.max_drawdown:.4f} |",
        f"| 年化收益 | {result.baseline_result.annual_return:.4f} | {result.experiment_result.annual_return:.4f} |",
        f"| 总收益 | {result.baseline_result.total_return:.4f} | {result.experiment_result.total_return:.4f} |",
        f"| Calmar | {result.baseline_calmar:.4f} | {result.experiment_calmar:.4f} |",
        f"| Turnover/yr | {result.baseline_turnover:.4f} | {result.experiment_turnover:.4f} |",
        f"| 交易笔数 | {result.baseline_result.trades_count} | {result.experiment_result.trades_count} |",
        "",
        "```",
        result.summary,
        "```",
        "",
    ])

    output_path.write_text("\n".join(lines), encoding="utf-8")
    _logger.info("C1 报告已落盘: %s (passed=%s, mode=%s)", output_path, result.passed, mode)
    return str(output_path.resolve())


# ──────────────────────────────────────────────────────────────────────────────
# 辅助
# ──────────────────────────────────────────────────────────────────────────────


def _empty_c1_result() -> C1ComparisonResult:
    """数据为空时返回的空 C1ComparisonResult（passed=False，不抛异常）。"""
    from zephyr.backtest.core.engine_base import BacktestResult

    now = datetime.now()
    empty_bt = BacktestResult(
        annual_return=0.0, end_date=now, idempotency_key="c1-empty",
        max_drawdown=0.0, sharpe_ratio=0.0, start_date=now, strategy_id="c1-empty",
        timestamp=now, total_return=0.0, trades_count=0, win_rate=0.0,
    )
    from zephyr.backtest.regime_validation.c1_comparator import C1MetricVerdict

    empty_verdict = C1MetricVerdict(
        name="空数据", baseline_value=0.0, experiment_value=0.0,
        threshold_desc="数据/信号为空", passed=False, detail="build_weight_panel 返回空，无法跑 C1",
    )
    return C1ComparisonResult(
        baseline_result=empty_bt, experiment_result=empty_bt,
        baseline_turnover=0.0, experiment_turnover=0.0,
        baseline_calmar=0.0, experiment_calmar=0.0,
        metric_verdicts=[empty_verdict], passed=False,
        veto_reason="数据/信号为空，C1 未执行",
        summary="C1 Shrinkage 开/关对比——未执行（数据为空）",
    )


__all__ = [
    "C1RunnerError",
    "build_volatility_schedule",
    "run_c1_with_provider",
    "run_c1_mock",
    "run_c1_regime",
    "run_c1_end_to_end",
    "save_c1_report",
]
