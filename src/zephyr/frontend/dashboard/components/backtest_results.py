# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.backtest_results
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.frontend.dashboard.components.chart_factory; zephyr.backtest.core.engine_base
# [CONSUMERS] zephyr.frontend.dashboard.app
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L08-001-backtest_results | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""backtest_results · 回测结果可视化组件（v3.0.0 Panel+HoloViz 重构, #ARCH-047）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §16.7.1
数据源: D_BACKTEST BacktestResult(CTR-P1-016, 11必填字段)
渲染依赖: Panel(布局) + ChartFactory.make_equity/make_drawdown(图表)

v3.0.0 变更 (#ARCH-047):
  - Streamlit → Panel (布局)
  - plotly 直接调用 → ChartFactory 工厂方法 (callback仅编排)
  - 净值曲线: HoloViews (via ChartFactory.make_equity)
  - 回撤曲线: plotly_resampler (via ChartFactory.make_drawdown)

布局:
  - 顶部: 关键指标卡片(Sharpe/Sortino/MaxDD/IC/IR/胜率/年化)
  - 中部: 净值曲线(HoloViews)+回撤曲线(plotly_resampler)
  - 底部: 3阶段门控状态(IS→WFA→OOS, 绿色=通过/红色=未通过)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

from zephyr.frontend.dashboard.components.chart_factory import (
    ChartFactoryError,
    make_drawdown,
    make_equity,
)


@dataclass
class BacktestMetrics:
    """绩效指标（用于可视化展示）"""
    sharpe: float = 0.0
    sortino: float = 0.0
    max_drawdown: float = 0.0
    ic: float = 0.0
    ir: float = 0.0
    win_rate: float = 0.0
    annual_return: float = 0.0


@dataclass
class BacktestGateStatus:
    """3阶段决策门控状态（IS→WFA→OOS）

    蓝图约束: 回测流程必须包含3阶段决策门控
    命名: BacktestGateStatus（避免与 gate_context.GateStatus 同名，ARCH-034 CLASS-UNIQUENESS）
    """
    is_passed: bool = False  # 样本内（In-Sample）
    wfa_passed: bool = False  # Walk-Forward Analysis
    oos_passed: bool = False  # 样本外（Out-of-Sample）

    @property
    def all_passed(self) -> bool:
        """3阶段全通过才允许上线"""
        return self.is_passed and self.wfa_passed and self.oos_passed


@dataclass
class BacktestResultData:
    """回测结果可视化数据模型"""
    backtest_id: str = ""
    strategy_id: str = ""
    net_value_curve: list[float] = field(default_factory=list)
    drawdown_curve: list[float] = field(default_factory=list)  # 负数
    timestamps: list[str] = field(default_factory=list)
    metrics: BacktestMetrics = field(default_factory=BacktestMetrics)
    gate_status: BacktestGateStatus = field(default_factory=BacktestGateStatus)
    overfitting_flag: bool = False


def fetch_backtest_results(
    backtest_result: Any,
    nav_series: Optional[list[float]] = None,
    drawdown_series: Optional[list[float]] = None,
    timestamps: Optional[list[str]] = None,
    metrics: Optional[BacktestMetrics] = None,
    gate_status: Optional[BacktestGateStatus] = None,
    sortino: float = 0.0,
    ic: float = 0.0,
    ir: float = 0.0,
) -> BacktestResultData:
    """从 D_BACKTEST BacktestResult 提取可视化数据

    蓝图 §16.7.1: 输入 BacktestResult(CTR-P1-016, 11必填字段)
    BacktestResult 11必填字段: annual_return/end_date/idempotency_key/max_drawdown/
        sharpe_ratio/start_date/strategy_id/timestamp/total_return/trades_count/win_rate

    Args:
        backtest_result: BacktestResult 实例（依赖注入，禁止直接 import D_BACKTEST 业务层）
        nav_series: 净值曲线序列（可选，BacktestResult 不含曲线，需外部传入）
        drawdown_series: 回撤曲线序列（负数）
        timestamps: 时间戳序列
        metrics: 绩效指标（可选，未传则从 BacktestResult 派生）
        gate_status: 3阶段门控状态（可选，未传则默认全 False）
        sortino/ic/ir: BacktestResult 不含这些字段，需外部传入

    Returns:
        BacktestResultData
    """
    br = backtest_result
    backtest_id = getattr(br, "idempotency_key", "") or ""
    strategy_id = getattr(br, "strategy_id", "") or ""

    if metrics is None:
        metrics = BacktestMetrics(
            sharpe=float(getattr(br, "sharpe_ratio", 0.0) or 0.0),
            sortino=float(sortino),
            max_drawdown=float(getattr(br, "max_drawdown", 0.0) or 0.0),
            ic=float(ic),
            ir=float(ir),
            win_rate=float(getattr(br, "win_rate", 0.0) or 0.0),
            annual_return=float(getattr(br, "annual_return", 0.0) or 0.0),
        )

    if gate_status is None:
        gate_status = BacktestGateStatus()

    nav = list(nav_series) if nav_series else []
    dd = list(drawdown_series) if drawdown_series else []
    ts = [str(t) for t in timestamps] if timestamps else []

    return BacktestResultData(
        backtest_id=backtest_id,
        strategy_id=strategy_id,
        net_value_curve=nav,
        drawdown_curve=dd,
        timestamps=ts,
        metrics=metrics,
        gate_status=gate_status,
        overfitting_flag=bool(getattr(br, "overfitting_flag", False)),
    )


def _metric_card(label: str, value: str, color: str = "#333") -> Any:
    """生成单个指标卡片（Panel Card 或 dict）"""
    if pn is None:
        return {"label": label, "value": value, "color": color}
    return pn.pane.Markdown(
        f"**{label}**\n\n## {value}",
        styles={"color": color, "text-align": "center", "padding": "8px",
                "border": "1px solid #e0e0e0", "border-radius": "4px"},
    )


def _gate_indicator(label: str, passed: bool) -> Any:
    """生成门控状态指示器（绿色=PASS / 红色=FAIL）"""
    status = "PASS" if passed else "FAIL"
    color = "#28a745" if passed else "#dc3545"
    if pn is None:
        return {"label": label, "status": status, "color": color}
    return pn.pane.Markdown(
        f"**{label}**\n\n## {status}",
        styles={"color": color, "text-align": "center", "padding": "8px",
                "border": f"2px solid {color}", "border-radius": "4px"},
    )


def render_backtest_results(data: BacktestResultData) -> dict[str, Any]:
    """Panel+HoloViz 渲染回测结果（v3.0.0, #ARCH-047）

    布局:
      - 顶部: 关键指标卡片(Sharpe/Sortino/MaxDD/IC/IR/胜率/年化)
      - 中部: 净值曲线(HoloViews)+回撤曲线(plotly_resampler)
      - 底部: 3阶段门控状态(IS→WFA→OOS, 绿色=通过/红色=未通过)

    callback仅编排: 图表生成委托 ChartFactory.make_equity/make_drawdown.
    测试环境(无 panel)仅返回 dict payload，便于断言。
    """
    # payload 始终返回（测试断言用）
    payload: dict[str, Any] = {
        "backtest_id": data.backtest_id,
        "strategy_id": data.strategy_id,
        "metrics": {
            "sharpe": round(data.metrics.sharpe, 4),
            "sortino": round(data.metrics.sortino, 4),
            "max_drawdown": round(data.metrics.max_drawdown, 4),
            "ic": round(data.metrics.ic, 4),
            "ir": round(data.metrics.ir, 4),
            "win_rate": round(data.metrics.win_rate, 4),
            "annual_return": round(data.metrics.annual_return, 4),
        },
        "gate_status": {
            "is_passed": data.gate_status.is_passed,
            "wfa_passed": data.gate_status.wfa_passed,
            "oos_passed": data.gate_status.oos_passed,
            "all_passed": data.gate_status.all_passed,
        },
        "overfitting_flag": data.overfitting_flag,
        "net_value_points": len(data.net_value_curve),
        "drawdown_points": len(data.drawdown_curve),
        "renderer": "panel" if pn is not None else "dict",
    }

    if pn is None:
        return payload

    # ===== 顶部：关键指标卡片 =====
    m = data.metrics
    metric_cards = [
        _metric_card("Sharpe (修正)", f"{m.sharpe:.3f}"),
        _metric_card("Sortino", f"{m.sortino:.3f}"),
        _metric_card("Max Drawdown", f"{m.max_drawdown:.2%}", "#dc3545"),
        _metric_card("Win Rate", f"{m.win_rate:.2%}"),
        _metric_card("IC", f"{m.ic:.3f}"),
        _metric_card("IR", f"{m.ir:.3f}"),
        _metric_card("Annual Return", f"{m.annual_return:.2%}", "#28a745"),
    ]
    metrics_row = pn.Row(*metric_cards, sizing_mode="stretch_width")

    # 过拟合警告
    overfitting_alert = None
    if data.overfitting_flag:
        overfitting_alert = pn.pane.Alert(
            "⚠ 过拟合警告 (overfitting_flag=True)：样本外Sharpe<70%样本内，建议否决上线",
            alert_type="danger",
        )

    # ===== 中部：净值+回撤图表（ChartFactory 工厂方法）=====
    charts: list[Any] = []
    if data.net_value_curve:
        try:
            equity_fig = make_equity(
                net_value_curve=data.net_value_curve,
                timestamps=data.timestamps,
                title="Net Value (NAV)",
            )
            charts.append(equity_fig)
        except ChartFactoryError:
            pass  # 数据为空时跳过

    if data.drawdown_curve:
        try:
            dd_fig = make_drawdown(
                drawdown_curve=data.drawdown_curve,
                timestamps=data.timestamps,
                title="Drawdown",
            )
            charts.append(dd_fig)
        except ChartFactoryError:
            pass

    charts_col = pn.Column(*charts, sizing_mode="stretch_width") if charts else None

    # ===== 底部：3阶段门控状态 =====
    gs = data.gate_status
    gate_indicators = [
        _gate_indicator("IS (样本内)", gs.is_passed),
        _gate_indicator("WFA (Walk-Forward)", gs.wfa_passed),
        _gate_indicator("OOS (样本外)", gs.oos_passed),
    ]
    gate_row = pn.Row(*gate_indicators, sizing_mode="stretch_width")

    gate_summary = pn.pane.Alert(
        "3阶段全通过，允许上线" if gs.all_passed else "存在未通过阶段，禁止上线",
        alert_type="success" if gs.all_passed else "warning",
    )

    # ===== 组装最终布局 =====
    layout_items = [
        pn.pane.Markdown(f"## 回测结果: {data.strategy_id} ({data.backtest_id})"),
        pn.pane.Markdown("### 关键指标 (Key Metrics)"),
        metrics_row,
    ]
    if overfitting_alert is not None:
        layout_items.append(overfitting_alert)
    if charts_col is not None:
        layout_items.append(pn.pane.Markdown("### 净值曲线 + 回撤 (NAV & Drawdown)"))
        layout_items.append(charts_col)
    layout_items.append(pn.pane.Markdown("### 3阶段决策门控 (IS → WFA → OOS)"))
    layout_items.append(gate_row)
    layout_items.append(gate_summary)

    layout = pn.Column(*layout_items, sizing_mode="stretch_width")
    payload["_layout"] = layout
    return payload


__all__ = [
    "BacktestMetrics",
    "BacktestGateStatus",
    "BacktestResultData",
    "fetch_backtest_results",
    "render_backtest_results",
]
