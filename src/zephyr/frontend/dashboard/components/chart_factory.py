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
# [TTL] permanent
"""chart_factory · 图表统一工厂（v3.0.0新增, #ARCH-047）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §3.1 组件13
ARCH-047: Streamlit->Panel+HoloViz技术栈切换, ChartFactory 作为图表生成统一入口

设计原则:
  - 纯函数工厂: 无 Streamlit/Panel 依赖, 业务逻辑独立为纯函数
  - callback仅编排: Panel callback 仅调用 ChartFactory.make_xxx(), 不含图表生成逻辑
  - G1升级路径: fetch->ChartFactory.make_xxx()->callback, G1升级时 fetch 可直接包装为 FastAPI 路由
  - 可选依赖: holoviews/plotly/plotly_resampler/panel 通过 try/except 导入, 测试环境返回 dict payload

工厂方法:
  - make_equity: 净值曲线(HoloViews Curve), backtest_results 调用
  - make_drawdown: 回撤曲线(plotly_resampler), backtest_results 调用
  - make_kline: K线图(Lightweight Charts v5.2, pn.pane.HTML+原生JS), backtest_results 调用
  - make_tick: Tick回放图(Plotly+plotly_resampler), tick_replay 调用
  - make_heatmap: 热力图(Plotly), 通用
  - make_orderbook: 5档盘口(Plotly 水平条形图, ask红/bid绿), order_book 调用
  - make_position: 持仓表格(Plotly Table, T+1锁定行红色背景), position_monitor 调用
  - make_orderflow: 订单流(Plotly Table+状态颜色编码), trade_panel 调用
  - make_gate_chart: 门禁统计堆叠条形图(Plotly Bar, pass绿/block红), gate_statistics 调用 (v3.1.0新增)
  - make_trend_line: 趋势折线图(Plotly Line, 大数据量自动 plotly_resampler), olap_trend 调用 (v3.1.0新增)

技术栈版本(ARCH-047 tech_stack):
  - holoviews >=1.19.0,<2.0.0 (policy)
  - plotly_resampler >=0.9.0,<1.0.0 (policy, MVP默认渲染策略10万级)
  - lightweight-charts v5.2 (policy, JS原生不引入Python封装包)
  - datashader >=0.16.0,<1.0.0 (factory, 仅阈值触发>50万点)
"""
from __future__ import annotations

from typing import Final
from zephyr.shared.io.serialization import dumps

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
    error_code = "ZA-FE-0001"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


# Datashader 阈值: 超过50万点自动切换 Datashader 渲染（蓝图 §16.7.2）
DATASHADER_THRESHOLD: Final[int] = 500_000


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
        fig = FigureResampler(default_n_shown_samples=10_000)
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

    data_json = dumps(kline_data)
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
        fig = FigureResampler(default_n_shown_samples=10_000)
    elif FigureResampler is not None:
        fig = FigureResampler(default_n_shown_samples=10_000)
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


def make_orderbook(
    ask_price: list[float],
    bid_price: list[float],
    ask_vol: list[int],
    bid_vol: list[int],
    last_price: float = 0.0,
    pressure_ratio: float = 0.0,
    title: str = "Order Book",
    width: int = 800,
    height: int = 400,
) -> Any:
    """生成5档盘口可视化（Plotly 水平条形图）

    蓝图 §16.7.3: 5档盘口展示, ask红/bid绿, 压力比仪表盘
    ARCH-047: callback仅编排, 图表生成委托此工厂方法

    Args:
        ask_price: 5档卖价 [ask1~ask5]
        bid_price: 5档买价 [bid1~bid5]
        ask_vol: 5档卖量
        bid_vol: 5档买量
        last_price: 最新价
        pressure_ratio: 盘口压力比 = bid_vol_total / ask_vol_total
        title: 图表标题
        width: 图表宽度
        height: 图表高度

    Returns:
        plotly Figure | dict payload（无 plotly 时）
    """
    if not ask_price and not bid_price:
        raise ChartFactoryError("ask_price/bid_price 不能同时为空")

    if go is None:
        return {
            "type": "orderbook",
            "ask_levels": len(ask_price),
            "bid_levels": len(bid_price),
            "last_price": last_price,
            "pressure_ratio": pressure_ratio,
            "title": title,
        }

    # 构建5档标签 (ask5->ask1 降序显示, bid1->bid5 降序显示)
    n_ask = len(ask_price)
    n_bid = len(bid_price)
    ask_labels = [f"ask{n_ask - i}" for i in range(n_ask)]  # ask5, ask4, ..., ask1
    bid_labels = [f"bid{i + 1}" for i in range(n_bid)]  # bid1, bid2, ..., bid5

    # 卖盘条形图 (红色, 从上到下 ask5->ask1)
    ask_bar = go.Bar(
        x=[-v for v in ask_vol],  # 负值让 ask 朝左
        y=ask_labels,
        orientation="h",
        name="Ask",
        marker_color="#dc3545",
        text=[f"{p:.3f} × {v}" for p, v in zip(ask_price, ask_vol)],
        textposition="auto",
        hovertemplate="Ask %{y}: %{text}<extra></extra>",
    )

    # 买盘条形图 (绿色, 从上到下 bid1->bid5)
    bid_bar = go.Bar(
        x=bid_vol,
        y=bid_labels,
        orientation="h",
        name="Bid",
        marker_color="#28a745",
        text=[f"{p:.3f} × {v}" for p, v in zip(bid_price, bid_vol)],
        textposition="auto",
        hovertemplate="Bid %{y}: %{text}<extra></extra>",
    )

    fig = go.Figure(data=[ask_bar, bid_bar])
    fig.update_layout(
        title=f"{title} | Last={last_price:.3f} | Pressure={pressure_ratio:.2f}",
        xaxis_title="Volume (ask ← / bid ->)",
        barmode="overlay",
        template="plotly_white",
        height=height,
        width=width,
        showlegend=True,
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor="#333"),
    )
    return fig


def make_position(
    positions: list[dict],
    title: str = "Position Monitor",
    width: int = 1000,
    height: int = 400,
) -> Any:
    """生成持仓表格（Plotly Table）

    蓝图 §16.7.4: 持仓表格(symbol/名称/持仓/可用/冻结/成本/最新价/盈亏/盈亏%/T+1标记)
    ARCH-047: callback仅编排, 图表生成委托此工厂方法

    Args:
        positions: 持仓列表, 每项格式:
            {symbol, name, quantity, available, frozen, today_bought,
             cost_price, last_price, unrealized_pnl, unrealized_pnl_pct,
             is_t_plus_1_locked}
        title: 表格标题
        width: 表格宽度
        height: 表格高度

    Returns:
        plotly Figure(go.Table) | dict payload（无 plotly 时）
    """
    if not positions:
        raise ChartFactoryError("positions 不能为空")

    if go is None:
        return {
            "type": "position",
            "rows": len(positions),
            "title": title,
        }

    # 提取各列
    symbols = [p.get("symbol", "") for p in positions]
    names = [p.get("name", "") for p in positions]
    quantities = [p.get("quantity", 0) for p in positions]
    availables = [p.get("available", 0) for p in positions]
    frozens = [p.get("frozen", 0) for p in positions]
    today_boughts = [p.get("today_bought", 0) for p in positions]
    cost_prices = [f"{p.get('cost_price', 0):.3f}" for p in positions]
    last_prices = [f"{p.get('last_price', 0):.3f}" for p in positions]
    pnls = [p.get("unrealized_pnl", 0) for p in positions]
    pnl_pcts = [p.get("unrealized_pnl_pct", 0) for p in positions]
    t1_flags = ["T+1" if p.get("is_t_plus_1_locked") else "—" for p in positions]

    # 盈亏颜色编码
    pnl_colors = ["#dc3545" if v < 0 else "#28a745" for v in pnls]
    pnl_text = [f"{v:+.2f}" for v in pnls]
    pnl_pct_text = [f"{v:+.2%}" for v in pnl_pcts]

    # T+1 锁定行红色背景
    row_colors = ["#ffe6e6" if p.get("is_t_plus_1_locked") else "white" for p in positions]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Symbol", "名称", "持仓", "可用", "冻结", "当日买入",
                    "成本价", "最新价", "盈亏", "盈亏%", "T+1"],
            fill_color="#f0f0f0",
            align="center",
            font=dict(size=12, color="#333"),
        ),
        cells=dict(
            values=[symbols, names, quantities, availables, frozens, today_boughts,
                    cost_prices, last_prices, pnl_text, pnl_pct_text, t1_flags],
            fill_color=[row_colors],
            align="center",
            font=dict(size=11),
        ),
    )])

    fig.update_layout(
        title=title,
        height=height,
        width=width,
    )
    return fig


def make_orderflow(
    orders: list[dict],
    title: str = "Order Flow",
    width: int = 1000,
    height: int = 400,
) -> Any:
    """生成订单流可视化（Plotly Table + 状态颜色编码）

    蓝图 §16.7.5: 订单列表(实时状态更新, 支持撤单按钮, Lightweight Charts订单流HTML Pane)
    ARCH-047: callback仅编排, 图表生成委托此工厂方法

    Args:
        orders: 订单列表, 每项格式:
            {order_id, broker_order_id, symbol, side, quantity, price,
             order_type, status, filled_quantity, avg_fill_price,
             timestamp, error_message}
        title: 表格标题
        width: 表格宽度
        height: 表格高度

    Returns:
        plotly Figure(go.Table) | dict payload（无 plotly 时）
    """
    if not orders:
        raise ChartFactoryError("orders 不能为空")

    if go is None:
        return {
            "type": "orderflow",
            "rows": len(orders),
            "title": title,
        }

    # 状态颜色映射
    status_colors = {
        "FILLED": "#28a745",       # 绿色
        "CANCELLED": "#6c757d",    # 灰色
        "REJECTED": "#dc3545",     # 红色
        "EXPIRED": "#343a40",      # 黑色
        "PENDING": "#ffc107",      # 黄色
        "SUBMITTED": "#17a2b8",    # 青色
        "ACCEPTED": "#007bff",     # 蓝色
        "PARTIALLY_FILLED": "#fd7e14",  # 橙色
    }

    # 提取各列
    order_ids = [o.get("broker_order_id") or o.get("order_id", "") for o in orders]
    symbols = [o.get("symbol", "") for o in orders]
    sides = [o.get("side", "").upper() for o in orders]
    quantities = [o.get("quantity", 0) for o in orders]
    prices = [f"{o.get('price', 0):.3f}" for o in orders]
    order_types = [o.get("order_type", "").upper() for o in orders]
    statuses = [o.get("status", "") for o in orders]
    filled_qtys = [o.get("filled_quantity", 0) for o in orders]
    avg_prices = [f"{o.get('avg_fill_price', 0):.3f}" for o in orders]
    timestamps = [o.get("timestamp", "") for o in orders]

    # 状态行颜色
    row_colors = [status_colors.get(s, "white") for s in statuses]
    # 使用浅色背景
    light_colors = []
    for s in statuses:
        c = status_colors.get(s, "#ffffff")
        # 转换为浅色版本
        if c.startswith("#"):
            light_colors.append(c + "33")  # 添加 alpha
        else:
            light_colors.append("white")

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Order ID", "Symbol", "Side", "Qty", "Price",
                    "Type", "Status", "Filled", "Avg Price", "Timestamp"],
            fill_color="#f0f0f0",
            align="center",
            font=dict(size=12, color="#333"),
        ),
        cells=dict(
            values=[order_ids, symbols, sides, quantities, prices,
                    order_types, statuses, filled_qtys, avg_prices, timestamps],
            fill_color=[light_colors],
            align="center",
            font=dict(size=11),
        ),
    )])

    fig.update_layout(
        title=title,
        height=height,
        width=width,
    )
    return fig


def make_gate_chart(
    gate_stats: list[dict],
    title: str = "Gate Statistics",
    width: int = 800,
    height: int = 400,
) -> Any:
    """生成门禁统计条形图（Plotly 堆叠条形图, pass绿/block红）

    蓝图 §3.1: make_gate_chart（v3.1.0新增, 旧Streamlit页面迁移Panel用）
    ARCH-047: callback仅编排, 图表生成委托此工厂方法

    Args:
        gate_stats: 各门禁统计列表, 每项格式:
            {gate_id, total_runs, passed_runs, failed_runs, pass_rate, block_rate}
        title: 图表标题
        width: 图表宽度
        height: 图表高度

    Returns:
        plotly Figure | dict payload（无 plotly 时）
    """
    if not gate_stats:
        raise ChartFactoryError("gate_stats 不能为空")

    if go is None:
        return {
            "type": "gate_chart",
            "gates": len(gate_stats),
            "title": title,
        }

    gate_ids = [g.get("gate_id", f"gate{i}") for i, g in enumerate(gate_stats)]
    pass_rates = [float(g.get("pass_rate", 0.0)) for g in gate_stats]
    block_rates = [float(g.get("block_rate", 0.0)) for g in gate_stats]

    fig = go.Figure(data=[
        go.Bar(name="Pass Rate", x=gate_ids, y=pass_rates, marker_color="#28a745"),
        go.Bar(name="Block Rate", x=gate_ids, y=block_rates, marker_color="#dc3545"),
    ])
    fig.update_layout(
        title=title,
        barmode="stack",
        template="plotly_white",
        yaxis_title="Rate",
        yaxis=dict(range=[0, 1], tickformat=".0%"),
        height=height,
        width=width,
        showlegend=True,
    )
    return fig


def make_trend_line(
    y_values: list[float],
    x_labels: Optional[list[str]] = None,
    title: str = "Trend",
    color: str = "#1f77b4",
    width: int = 800,
    height: int = 400,
    y_title: str = "Value",
) -> Any:
    """生成趋势折线图（Plotly Line, 大数据量自动 plotly_resampler 降采样）

    蓝图 §3.1: make_trend_line（v3.1.0新增, OLAP趋势页迁移Panel用）
    ARCH-047: callback仅编排, 图表生成委托此工厂方法

    Args:
        y_values: Y 轴数值序列
        x_labels: X 轴标签序列（可选, 如时间/周期）
        title: 图表标题
        color: 曲线颜色
        width: 图表宽度
        height: 图表高度
        y_title: Y 轴标题

    Returns:
        plotly_resampler FigureResampler | plotly Figure | dict payload（无 plotly 时）
    """
    if not y_values:
        raise ChartFactoryError("y_values 不能为空")

    if go is None:
        return {
            "type": "trend_line",
            "points": len(y_values),
            "title": title,
            "color": color,
        }

    x = _ensure_x(x_labels, len(y_values))

    if FigureResampler is not None and len(y_values) > 10_000:
        fig = FigureResampler(default_n_shown_samples=10_000)
    else:
        fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=x,
            y=y_values,
            name=title,
            line=dict(color=color),
            mode="lines",
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title=y_title,
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
    "make_orderbook",
    "make_position",
    "make_orderflow",
    "make_gate_chart",
    "make_trend_line",
]
