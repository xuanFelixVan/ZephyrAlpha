# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.backtest_results
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.backtest.core.engine_base
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
"""backtest_results · 回测结果可视化组件（v2.2.0新增）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §16.7.1
数据源: D_BACKTEST BacktestResult(CTR-P1-016, 11必填字段)
渲染依赖: plotly(图表) + streamlit(布局)

布局:
  - 顶部: 关键指标卡片(Sharpe/Sortino/MaxDD/IC/IR/胜率/年化)
  - 中部: 净值曲线+回撤曲线(plotly双轴图)
  - 底部: 3阶段门控状态(IS→WFA→OOS, 绿色=通过/红色=未通过)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

try:
    import streamlit as st
except ImportError:  # 测试环境无 streamlit
    st = None

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:  # 测试环境无 plotly
    go = None
    make_subplots = None


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


def render_backtest_results(data: BacktestResultData) -> dict[str, Any]:
    """Streamlit 渲染回测结果

    布局:
      - 顶部: 关键指标卡片(Sharpe/Sortino/MaxDD/IC/IR/胜率/年化)
      - 中部: 净值曲线+回撤曲线(plotly双轴图)
      - 底部: 3阶段门控状态(IS→WFA→OOS)

    测试环境(无 streamlit/plotly)仅返回 dict，便于断言。
    """
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
    }

    if st is None or go is None:
        return payload

    # 顶部：关键指标卡片
    st.subheader("关键指标 (Key Metrics)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sharpe (修正)", f"{data.metrics.sharpe:.3f}")
    col2.metric("Sortino", f"{data.metrics.sortino:.3f}")
    col3.metric("Max Drawdown", f"{data.metrics.max_drawdown:.2%}")
    col4.metric("Win Rate", f"{data.metrics.win_rate:.2%}")

    col5, col6, col7, _ = st.columns(4)
    col5.metric("IC", f"{data.metrics.ic:.3f}")
    col6.metric("IR", f"{data.metrics.ir:.3f}")
    col7.metric("Annual Return", f"{data.metrics.annual_return:.2%}")

    if data.overfitting_flag:
        st.error("⚠ 过拟合警告 (overfitting_flag=True)：样本外Sharpe<70%样本内，建议否决上线")

    # 中部：净值+回撤双轴图
    if data.net_value_curve:
        st.subheader("净值曲线 + 回撤 (NAV & Drawdown)")
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.08,
            row_heights=[0.7, 0.3],
            subplot_titles=("Net Value", "Drawdown"),
        )
        x = data.timestamps if len(data.timestamps) == len(data.net_value_curve) else list(range(len(data.net_value_curve)))
        fig.add_trace(
            go.Scatter(x=x, y=data.net_value_curve, name="NAV", line=dict(color="#1f77b4")),
            row=1, col=1,
        )
        if data.drawdown_curve:
            dd_x = data.timestamps if len(data.timestamps) == len(data.drawdown_curve) else list(range(len(data.drawdown_curve)))
            fig.add_trace(
                go.Scatter(x=dd_x, y=data.drawdown_curve, name="Drawdown", fill="tozeroy", line=dict(color="#d62728")),
                row=2, col=1,
            )
        fig.update_layout(height=520, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    # 底部：3阶段门控状态
    st.subheader("3阶段决策门控 (IS → WFA → OOS)")
    gc1, gc2, gc3 = st.columns(3)
    gc1.metric("IS (样本内)", "PASS" if data.gate_status.is_passed else "FAIL")
    gc2.metric("WFA (Walk-Forward)", "PASS" if data.gate_status.wfa_passed else "FAIL")
    gc3.metric("OOS (样本外)", "PASS" if data.gate_status.oos_passed else "FAIL")
    if data.gate_status.all_passed:
        st.success("3阶段全通过，允许上线")
    else:
        st.warning("存在未通过阶段，禁止上线")

    return payload


__all__ = [
    "BacktestMetrics",
    "BacktestGateStatus",
    "BacktestResultData",
    "fetch_backtest_results",
    "render_backtest_results",
]
