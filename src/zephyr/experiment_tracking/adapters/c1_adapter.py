# [BLUEPRINT] MOD-OBS-001 | docs/03_modules/_domain_infrastructure_operations/blueprint_experiment_tracking.md | §M1-3
# [MODULE] zephyr.experiment_tracking.adapters.c1_adapter
# [DOMAIN] D_INFRA_TELEMETRY
# [DEPENDENCIES] zephyr.experiment_tracking.experiment_tracker (get_tracker); typing.TYPE_CHECKING (C1 类型仅静态检查，运行时鸭子类型——破 backtest↔experiment_tracking 循环)
# [CONSUMERS] zephyr.backtest.regime_validation.c1_runner (track=True 时 lazy import 调用)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] C1ComparisonResult → 实验跟踪 run（params/metrics/artifacts/tags）；tracker 降级时 no-op 不抛；comparator=None 时跳过 nav artifact；matplotlib 未装时跳过 PNG（仅写 CSV）；不依赖 backtest 运行时 import（TYPE_CHECKING 隔离）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tracking 失败→stderr warning 不抛（不崩 C1 业务）；run_id 返回（NullBackend 返回 "null-run"）
# [TESTS] tests/experiment_tracking/test_c1_adapter.py
# [A_module] module_id=MOD-OBS-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-REGIME-DEADZONE-001 #ARCH-OBS-EXP-TRACK-001
"""L_INFRA_TELEMETRY — C1 对比结果 → 实验跟踪语义适配器（M1-3，单一 JSON 后端）。

把 ``C1ComparisonResult`` 翻译为一个实验跟踪 run，使人/AI 能通过 Panel「实验历史」Tab 或
``experiment_tracking.query`` 对比多次 C1 运行（开/关四项指标 + 净值曲线）。
（MLflow 已裁定完全卸载——51 号；存储=FallbackBackend 本地 JSON。）

Zephyr 语义 → 实验跟踪映射:
  - params   : C1 门槛配置（sharpe_tolerance 等）+ 模式 + 策略名 + 数据日期范围
  - metrics  : baseline_/experiment_ sharpe/maxdd/turnover/calmar + 各 verdict 值 + passed
  - artifacts: nav_curve_baseline.csv / nav_curve_experiment.csv / nav_curve_comparison.png / c1_summary.md
  - tags     : component=c1-validation / mode / passed / veto_reason

循环依赖规避
-------------
``c1_runner``（backtest 域）在 ``track=True`` 时调用本 adapter；本 adapter 需引用
``C1ComparisonResult``/``C1ShrinkageComparator``（backtest 域）类型。直接 runtime import
会形成 backtest → experiment_tracking → backtest 包级循环。故：
  - C1 类型仅 ``TYPE_CHECKING`` 下导入（静态检查用），运行时全鸭子类型（属性访问）
  - ``c1_runner`` 对本函数 lazy import（仅 ``track=True`` 分支内 import）

降级
----
``get_tracker()`` 已封装 backend 选择（FallbackBackend JSON / NullBackend no-op）。
本 adapter 只调 ``start_run`` + ``log_*``，不关心 backend 选择——tracker 关闭时 NullBackend
全 no-op，run_id="null-run"。所有 log 失败由 ``RunContext`` 内 try/except 兜住，不抛。

依据: 11_regime_backtest_validation_plan §3 ② + backtest_observability_mlflow_plan.md M1-3
Version: 0.1.0
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Final, Optional

from zephyr.experiment_tracking.experiment_tracker import get_tracker

if TYPE_CHECKING:  # 仅静态类型检查，运行时不 import backtest（破循环）
    from zephyr.backtest.regime_validation.c1_comparator import (
        C1ComparisonResult,
        C1ShrinkageComparator,
    )

_logger = logging.getLogger(__name__)

__all__: Final = ["track_c1_result"]

# component → experiment 名映射（tracker 内部拼 "zephyr-{component}"）
_COMPONENT = "c1-validation"


def _extract_params(
    result: "C1ComparisonResult",
    comparator: "C1ShrinkageComparator" | None,
    mode: str,
    strategy_name: str,
) -> dict[str, Any]:
    """提取 params：C1 门槛 + 模式 + 策略 + 数据日期范围。"""
    params: dict[str, Any] = {
        "mode": mode,
        "strategy_name": strategy_name,
        "passed": result.passed,
    }
    # C1 门槛配置（comparator 持有，result 不含）
    if comparator is not None:
        cfg = comparator.config
        params.update(
            {
                "c1_sharpe_tolerance": cfg.sharpe_tolerance,
                "c1_maxdd_improvement_pp": cfg.maxdd_improvement_pp,
                "c1_calmar_improvement_ratio": cfg.calmar_improvement_ratio,
                "c1_turnover_max_ratio": cfg.turnover_max_ratio,
                "c1_trading_days_per_year": cfg.trading_days_per_year,
            }
        )
    # 数据日期范围 + 策略 id（baseline_result 持有）
    br = result.baseline_result
    params["strategy_id"] = br.strategy_id
    params["start_date"] = br.start_date.isoformat() if br.start_date else ""
    params["end_date"] = br.end_date.isoformat() if br.end_date else ""
    params["baseline_trades_count"] = br.trades_count
    params["experiment_trades_count"] = result.experiment_result.trades_count
    return params


def _extract_metrics(result: "C1ComparisonResult") -> dict[str, float]:
    """提取 metrics：baseline_/experiment_ 核心指标 + per-verdict 值 + passed。"""
    br, er = result.baseline_result, result.experiment_result
    metrics: dict[str, float] = {
        "baseline_sharpe": float(br.sharpe_ratio),
        "experiment_sharpe": float(er.sharpe_ratio),
        "baseline_maxdd": float(br.max_drawdown),
        "experiment_maxdd": float(er.max_drawdown),
        "baseline_annual_return": float(br.annual_return),
        "experiment_annual_return": float(er.annual_return),
        "baseline_total_return": float(br.total_return),
        "experiment_total_return": float(er.total_return),
        "baseline_win_rate": float(br.win_rate),
        "experiment_win_rate": float(er.win_rate),
        "baseline_turnover": float(result.baseline_turnover),
        "experiment_turnover": float(result.experiment_turnover),
        "baseline_calmar": float(result.baseline_calmar),
        "experiment_calmar": float(result.experiment_calmar),
        "passed": 1.0 if result.passed else 0.0,
    }
    # 各 verdict 的 baseline/experiment 值 + 通过标志（name 小写归一化）
    for v in result.metric_verdicts:
        key = v.name.lower().replace(" ", "_")
        metrics[f"{key}_baseline"] = float(v.baseline_value)
        metrics[f"{key}_experiment"] = float(v.experiment_value)
        metrics[f"{key}_passed"] = 1.0 if v.passed else 0.0
    return metrics


def _render_nav_png(nav_data: dict[str, Any]) -> bytes | None:
    """渲染 baseline/experiment 净值曲线对比图为 PNG bytes。

    matplotlib 未安装时返回 None（调用方跳过 PNG，仅写 CSV）。
    """
    try:
        import matplotlib

        matplotlib.use("Agg")  # 非交互后端，不弹窗
        import matplotlib.pyplot as plt
    except ImportError:
        _logger.warning("c1_adapter: matplotlib 未安装，跳过净值曲线 PNG")
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    for label, nav_series in nav_data.items():
        display_label = "baseline (Shrinkage OFF)" if label == "baseline" else "experiment (Shrinkage ON)"
        ax.plot(nav_series.index, nav_series.values, label=display_label, linewidth=1.2)
    ax.set_title("NAV Curve Comparison")
    ax.set_xlabel("Time")
    ax.set_ylabel("NAV")
    ax.legend()
    ax.grid(True, alpha=0.3)

    from io import BytesIO

    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    return buf.getvalue()


def _log_nav_artifacts(
    run: Any,
    comparator: "C1ShrinkageComparator" | None,
) -> None:
    """把 baseline/experiment 净值曲线写为 CSV + PNG artifact（comparator=None 或无 nav 时跳过）。"""
    if comparator is None:
        return
    nav_data: dict[str, Any] = {}
    for label, portfolio in (
        ("baseline", comparator.last_baseline_portfolio),
        ("experiment", comparator.last_experiment_portfolio),
    ):
        if portfolio is None:
            continue
        try:
            nav_series = portfolio.nav_series
        except Exception as e:  # noqa: BLE001 — nav 提取失败不阻断 tracking
            _logger.warning("c1_adapter: 提取 %s nav_series 失败(跳过): %s", label, e)
            continue
        if nav_series is None or len(nav_series) == 0:
            continue
        nav_data[label] = nav_series
        csv_bytes = nav_series.to_csv(index=True, header=["nav"]).encode("utf-8")
        run.log_artifact_bytes(csv_bytes, f"nav_curve_{label}.csv", artifact_path="nav")

    # PNG 对比图（两条曲线画在同一张图上，matplotlib 未装时跳过）
    if nav_data:
        try:
            png_bytes = _render_nav_png(nav_data)
            if png_bytes is not None:
                run.log_artifact_bytes(png_bytes, "nav_curve_comparison.png", artifact_path="nav")
        except Exception as e:  # noqa: BLE001 — PNG 渲染失败不阻断 tracking
            _logger.warning("c1_adapter: 渲染净值曲线 PNG 失败(跳过): %s", e)


def _build_summary_md(result: "C1ComparisonResult") -> str:
    """构建 c1_summary.md：人类可读总结 + verdicts 表。"""
    lines = [
        "# C1 Shrinkage 开/关对比结果",
        "",
        f"- **passed**: {result.passed}",
        f"- **veto_reason**: {result.veto_reason or '(无——四项全过)'}",
        "",
        "## 指标裁定",
        "",
        "| 指标 | 基准(关) | 实验(开) | 通过 | 说明 |",
        "|---|---|---|---|---|",
    ]
    for v in result.metric_verdicts:
        lines.append(
            f"| {v.name} | {v.baseline_value} | {v.experiment_value} | {'✅' if v.passed else '❌'} | {v.detail} |"
        )
    lines.extend(["", "## 总结", "", result.summary])
    return "\n".join(lines)


def track_c1_result(
    result: "C1ComparisonResult",
    *,
    comparator: "C1ShrinkageComparator" | None = None,
    mode: str = "unknown",
    strategy_name: str = "c1-shrinkage",
    extra_tags: dict[str, str] | None = None,
) -> str:
    """把 ``C1ComparisonResult`` 记录为一个实验跟踪 run。

    Args:
        result: C1 开/关对比结果（含四项 verdicts + passed + summary）。
        comparator: C1 对比器实例——提供门槛配置 + last_baseline/experiment_portfolio
            （净值曲线 artifact）。None 时跳过 nav artifact 与门槛 params。
        mode: 运行模式（"mock" / "regime"），写入 tags 供筛选。
        strategy_name: 策略名，写入 params。
        extra_tags: 额外 tags（可选）。

    Returns:
        run_id（NullBackend 返回 "null-run"；FallbackBackend 返回真实 id）。
        tracker 降级时仍返回 id（FallbackBackend 写 JSON）。
    语义:
      - tracker 关闭（enable_tracking=False）→ NullBackend no-op，返回 "null-run"
      - 默认 → FallbackBackend 写本地 JSON（单一后端，MLflow 已退役），返回伪 id
      - 任何 log 失败 → RunContext 内 try/except 兜住，不抛、不崩 C1 业务
    """
    tracker = get_tracker()
    tags: dict[str, str] = {
        "component": _COMPONENT,
        "mode": mode,
        "passed": str(result.passed),
    }
    if result.veto_reason:
        tags["veto_reason"] = result.veto_reason
    if extra_tags:
        tags.update({k: str(v) for k, v in extra_tags.items()})

    run_name = f"c1_{mode}_{datetime.now(UTC):%Y%m%d_%H%M%S}"
    with tracker.start_run(_COMPONENT, run_name=run_name, tags=tags) as run:
        run.log_params(_extract_params(result, comparator, mode, strategy_name))
        run.log_metrics(_extract_metrics(result))
        _log_nav_artifacts(run, comparator)
        run.log_artifact_bytes(
            _build_summary_md(result).encode("utf-8"),
            "c1_summary.md",
            artifact_path="report",
        )
    return run.run_id
