# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.chart_factory
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] holoviews; plotly; plotly_resampler; panel
# [CONSUMERS] zephyr.frontend.dashboard.components.backtest_results; tick_replay; order_book; position_monitor; trade_panel
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ChartFactoryError
# [TESTS]
# [A_module] module_id=MOD-L08-001-chart_factory | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""chart_factory · 图表统一工厂（v3.0.0新增, #ARCH-047）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §3.1 组件13
ARCH-047: Streamlit→Panel+HoloViz技术栈切换, ChartFactory 作为图表生成统一入口

设计原则:
  - 纯函数工厂: 无 Streamlit/Panel 依赖, 业务逻辑独立为纯函数
  - callback仅编排: Panel callback 仅调用 ChartFactory.make_xxx(), 不含图表生成逻辑
  - G1升级路径: fetch→ChartFactory.make_xxx()→callback, G1升级时 fetch 可直接包装为 FastAPI 路由
  - 可选依赖: holoviews/plotly/plotly_resampler/panel 通过 try/except 导入, 测试环境返回 dict payload

工厂方法:
  - make_equity: 净值曲线(HoloViews Curve), backtest_results 调用
  - make_drawdown: 回撤曲线(plotly_resampler), backtest_results 调用
  - make_kline: K线图(Lightweight Charts v5.2, pn.pane.HTML+原生JS), backtest_results 调用
  - make_tick: Tick回放图(Plotly+plotly_resampler), tick_replay 调用
  - make_heatmap: 热力图(Plotly), 通用

技术栈版本(ARCH-047 tech_stack):
  - holoviews >=1.19.0,<2.0.0 (GOV-P1)
  - plotly_resampler >=0.9.0,<1.0.0 (GOV-P1, MVP默认渲染策略10万级)
  - lightweight-charts v5.2 (GOV-P1, JS原生不引入Python封装包)
  - datashader >=0.16.0,<1.0.0 (GOV-P2, 仅阈值触发>50万点)
"""
from __future__ import annotations

import json
from typing import Any, Optional

try:
    import holoviews as hv
except ImportError:  # 测试环境无 holoviews
    hv = None

try:
    import plotly.graph_objects as go
except ImportError:  # 测试环境无 plotly
    go = None

try:
    from plotly_resampler import FigureResampler
except ImportError:  # 测试环境无 plotly_resampler
    FigureResampler = None

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None


class ChartFactoryError(Exception):
    """图表工厂错误"""


# Datashader 阈值: 超过50万点自动切换 Datashader 渲染（蓝图 §16.7.2）
DATASHADER_THRESHOLD = 500_000


def _ensure_x(x: Optional[list], length: int) -> list:
    """生成 X 轴序列：若 x 为空或长度不匹配，用 range(length) 兜底"""
    if x and len(x) == length:
        return list(x)
    return list(range(length))


def make_equity(
    net_value_curve: list[float],
    timestamps: Optional[list] = None,
    title: str = "Net Value",
    color: str = "#1f77b4",
    width: int = 800,
    height: int = 400,
) -> Any:
    """生成净值曲线图（HoloViews Curve）

    蓝图 §16.7.1: HoloViews(净值曲线)
    ARCH-047 tech_stack: holoviews >=1.19.0

    Args:
        net_value_curve: 净值曲线序列
        timestamps: 时间戳序列（可选，长度需与 net_value_curve 一致）
        title: 图表标题
        color: 曲线颜色
        width: 图表宽度
        height: 图表高度

    Returns:
        HoloViews Curve 对象（有 hv 时）| dict payload（无 hv 时，测试环境）
    """
    if not net_value_curve:
        raise ChartFactoryError("net_value_curve 不能为空")

    if hv is None:
        return {
            "type": "equity",
            "points": len(net_value_curve),
            "title": title,
            "color": color,
        }

    x = _ensure_x(timestamps, len(net_value_curve))
    curve = hv.Curve((x, net_value_curve), label="NAV")
    curve = curve.opts(
        title=title,
        xlabel="Time",
        ylabel="Net Value",
        color=color,
        width=width,
        height=height,
        tools=["hover"],
    )
    return curve


def make_drawdown(
    drawdown_curve: list[float],
    timestamps: Optional[list] = None,
    title: str = "Drawdown",
    color: str = "#d62728",
    width: int = 800,
    height: int = 300,
) -> Any:
    """生成回撤曲线图（plotly_resampler）

    蓝图 §16.7.1: plotly_resampler(回撤)
    ARCH-047 tech_stack: plotly_resampler >=0.9.0（MVP默认渲染策略，10万级降采样）

    Args:
        drawdown_curve: 回撤曲线序列（负数）
        timestamps: 时间戳序列（可选）
        title: 图表标题
        color: 填充颜色
        width: 图表宽度
        height: 图表高度

    Returns:
        plotly_resampler FigureResampler | plotly Figure | dict payload（无 plotly 时）
    """
    if not drawdown_curve:
        raise ChartFactoryError("drawdown_curve 不能为空")

    if go is None:
        return {
            "type": "drawdown",
            "points": len(drawdown_curve),
            "title": title,
            "color": color,
        }

    x = _ensure_x(timestamps, len(drawdown_curve))

    # 优先使用 FigureResampler（大数据降采样），降级为普通 go.Figure
    if FigureResampler is not None:
        fig = FigureResampler(default_n_ticks=10_000)
    else:
        fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=drawdown_curve,
            name="Drawdown",
            fill="tozeroy",
            line=dict(color=color),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Drawdown",
        template="plotly_white",
        height=height,
        width=width,
    )
    return fig


def make_kline(
    kline_data: list[dict],
    title: str = "K-Line",
    height: int = 400,
) -> Any:
    """生成K线图（Lightweight Charts v5.2, pn.pane.HTML+原生JS）

    蓝图 §16.7.1: Lightweight Charts(K线, HTML Pane+原生JS), 不依赖Python封装包
    ARCH-047 tech_stack: lightweight-charts v5.2（JS原生, pn.pane.HTML集成）

    Args:
        kline_data: K线数据列表, 每项格式 {time, open, high, low, close}
            time: ISO 字符串或 UNIX 时间戳（秒）
            open/high/low/close: 价格
        title: 图表标题
        height: 图表高度

    Returns:
        panel.pane.HTML 对象（有 pn 时）| dict payload（无 pn 时, 含 html 字段）
    """
    if not kline_data:
        raise ChartFactoryError("kline_data 不能为空")

    # 校验数据格式
    required_keys = {"time", "open", "high", "low", "close"}
    for i, k in enumerate(kline_data):
        missing = required_keys - set(k.keys())
        if missing:
            raise ChartFactoryError(f"kline_data[{i}] 缺少字段: {missing}")

    data_json = json.dumps(kline_data, default=str)
    chart_id = f"kline-{id(kline_data) & 0xFFFFFF:x}"

    html = f"""
<div id="{chart_id}" style="width:100%;height:{height}px;"></div>
<script src="https://unpkg.com/lightweight-charts@5.2/dist/lightweight-charts.standalone.production.js"></script>
<script>
(function() {{
    var container = document.getElementById('{chart_id}');
    if (!container || typeof LightweightCharts === 'undefined') return;
    var chart = LightweightCharts.createChart(container, {{
        width: '100%',
        height: {height},
        layout: {{ background: {{ type: 'solid', color: '#ffffff' }}, textColor: '#333' }},
        grid: {{
            vertLines: {{ color: 'rgba(197, 203, 206, 0.3)' }},
            horzLines: {{ color: 'rgba(197, 203, 206, 0.3)' }},
        }},
    }});
    var candleSeries = chart.addCandlestickSeries();
    candleSeries.setData({data_json});
    chart.timeScale().fitContent();
}})();
</script>
"""

    if pn is not None:
        return pn.pane.HTML(html, height=height + 20)

    return {
        "type": "kline",
        "html": html,
        "points": len(kline_data),
        "title": title,
    }


def make_tick(
    tick_data: list[float],
    timestamps: Optional[list] = None,
    title: str = "Tick Replay",
    color: str = "#1f77b4",
    width: int = 800,
    height: int = 400,
) -> Any:
    """生成Tick回放图（Plotly+plotly_resampler, Datashader阈值触发）

    蓝图 §16.7.2: Plotly+plotly_resampler默认 / Datashader阈值触发(>50万点)
    渲染策略: MVP全用Plotly+plotly_resampler(10万级降采样), Datashader仅阈值触发(>50万点百万级渲染)

    Args:
        tick_data: Tick 价格序列
        timestamps: 时间戳序列（可选）
        title: 图表标题
        color: 曲线颜色
        width: 图表宽度
        height: 图表高度

    Returns:
        plotly_resampler FigureResampler | plotly Figure | dict payload（无 plotly 时）
    """
    if not tick_data:
        raise ChartFactoryError("tick_data 不能为空")

    if go is None:
        return {
            "type": "tick",
            "points": len(tick_data),
            "title": title,
            "color": color,
            "datashader_triggered": len(tick_data) > DATASHADER_THRESHOLD,
        }

    x = _ensure_x(timestamps, len(tick_data))
    use_datashader = len(tick_data) > DATASHADER_THRESHOLD

    # 大数据量优先用 FigureResampler（内置降采样，Datashader 风格渲染）
    if use_datashader and FigureResampler is not None:
        fig = FigureResampler(default_n_ticks=10_000)
    elif FigureResampler is not None:
        fig = FigureResampler(default_n_ticks=10_000)
    else:
        fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=tick_data,
            name="Tick",
            line=dict(color=color),
            mode="lines",
        )
    )
    fig.update_layout(
        title=f"{title}{' (Datashader)' if use_datashader else ''}",
        xaxis_title="Time",
        yaxis_title="Price",
        template="plotly_white",
        height=height,
        width=width,
    )
    return fig


def make_heatmap(
    data: list[list[float]],
    x_labels: Optional[list[str]] = None,
    y_labels: Optional[list[str]] = None,
    title: str = "Heatmap",
    colorscale: str = "RdYlGn",
    width: int = 800,
    height: int = 400,
) -> Any:
    """生成热力图（Plotly Heatmap）

    蓝图 §3.1: make_heatmap（通用热力图工厂）

    Args:
        data: 二维数据矩阵 z[row][col]
        x_labels: X 轴标签列表
        y_labels: Y 轴标签列表
        title: 图表标题
        colorscale: 颜色刻度（RdYlGn/Blues/Viridis 等）
        width: 图表宽度
        height: 图表高度

    Returns:
        plotly Figure | dict payload（无 plotly 时）
    """
    if not data or not data[0]:
        raise ChartFactoryError("data 不能为空且必须为非空二维矩阵")

    if go is None:
        return {
            "type": "heatmap",
            "rows": len(data),
            "cols": len(data[0]) if data else 0,
            "title": title,
            "colorscale": colorscale,
        }

    fig = go.Figure(
        data=go.Heatmap(
            z=data,
            x=x_labels,
            y=y_labels,
            colorscale=colorscale,
        )
    )
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=height,
        width=width,
    )
    return fig


__all__ = [
    "ChartFactoryError",
    "DATASHADER_THRESHOLD",
    "make_equity",
    "make_drawdown",
    "make_kline",
    "make_tick",
    "make_heatmap",
]
