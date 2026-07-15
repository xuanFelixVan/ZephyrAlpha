# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.backtest_performance
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] panel; plotly; plotly_resampler; zephyr.frontend.dashboard.components.chart_factory
# [CONSUMERS] zephyr.frontend.dashboard.app_panel
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L08-001-backtest_performance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""backtest_performance · 掘金量化风格绩效分析可视化（v1.0.0, #ARCH-047）

参照掘金3客户端绩效分析 5 模块布局 + bt-visualizer 交互特性（hover/click/zoom）:
  Tab 1 绩效概览 Performance Overview  — 6 KPI + 收益图(3线) + 回撤图(2线) + 日收益率柱状图 + 16指标表
  Tab 2 持仓分析 Position Analysis      — 仓位分布堆叠图 + 每日快照表
  Tab 3 交易统计 Trade Statistics       — 28 指标网格 + 月度收益热力图
  Tab 4 每日明细 Daily Detail           — 日期选择 + 资金/持仓/委托三表下钻
  Tab 5 信号分析 Signal Analysis        — K线 + 买卖点打点 + 频度切换(bt-visualizer 风格)

数据源: BacktestPerformanceData (本模块定义, 含完整掘金字段)
交互: plotly hovertemplate(交易信息悬浮) + clickmode(点击下钻) + 双击重置
暗色主题: plotly custom template, 匹配 app_panel.py #2b2b2b 调色板

设计原则:
  - callback仅编排: 图表生成委托 plotly 原生, 布局委托 Panel
  - 中英双语: 所有 Tab 名/指标名/图表标题 中英并列
  - mock优先: 无真实 BacktestResult 注入时, 用 generate_demo_performance_data() 生成掘金风格示例
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:  # 测试环境无 plotly
    go = None
    make_subplots = None

try:
    from plotly_resampler import FigureResampler
except ImportError:
    FigureResampler = None


# ===== 暗色主题调色板 (匹配 app_panel.py) =====
_BG = "#2b2b2b"          # 深灰背景
_CARD_BG = "#383838"     # 卡片中灰
_INPUT_BG = "#1e1e1e"    # 输入框更深灰
_BORDER = "#555555"      # 灰边框
_TEXT = "#e0e0e0"        # 浅灰白文字
_TEXT_DIM = "#a0a0a0"    # 暗灰文字
_GREEN = "#26a69a"      # 涨/盈利 ( teal )
_RED = "#ef5350"        # 跌/亏损 ( red )
_BLUE = "#42a5f5"       # 策略收益
_ORANGE = "#ff9800"     # 超额收益
_PURPLE = "#ab47bc"     # 基准
_YELLOW = "#ffd54f"     # 高亮


def _dark_template() -> object:
    """创建 plotly 暗色主题 template (匹配 #2b2b2b 调色板)"""
    if go is None:
        return None
    return go.layout.Template(
        layout=go.Layout(
            paper_bgcolor=_BG,
            plot_bgcolor=_INPUT_BG,
            font=dict(color=_TEXT, size=12, family="Segoe UI, Arial, sans-serif"),
            title_font=dict(color=_TEXT, size=14),
            legend=dict(bgcolor=_CARD_BG, bordercolor=_BORDER, font=dict(color=_TEXT)),
            xaxis=dict(gridcolor=_BORDER, zerolinecolor=_BORDER, tickfont=dict(color=_TEXT_DIM)),
            yaxis=dict(gridcolor=_BORDER, zerolinecolor=_BORDER, tickfont=dict(color=_TEXT_DIM)),
            colorway=[_BLUE, _PURPLE, _ORANGE, _GREEN, _RED, _YELLOW],
            hoverlabel=dict(bgcolor=_CARD_BG, font=dict(color=_TEXT)),
            margin=dict(l=50, r=20, t=50, b=40),
        )
    )


_DARK_TEMPLATE = _dark_template() if go is not None else None


# ===== 数据模型 (参照掘金绩效分析字段定义) =====

@dataclass
class PerformanceMetrics:
    """16 绩效指标 (掘金绩效概览)"""
    initial_asset: float = 10_000_000.0   # 期初资产 (元)
    final_asset: float = 0.0              # 期末资产 (元)
    cumulative_pnl: float = 0.0           # 累计盈亏 (元)
    cumulative_fee: float = 0.0           # 累计手续费 (元)
    cumulative_return: float = 0.0        # 累计收益率 %
    benchmark_return: float = 0.0         # 基准收益率 %
    excess_return: float = 0.0            # 超额收益率 %
    annual_return: float = 0.0            # 年化收益率 %
    max_drawdown: float = 0.0             # 最大回撤 % (负数)
    annual_volatility: float = 0.0        # 年化波动率 %
    win_rate: float = 0.0                 # 胜率 %
    alpha: float = 0.0
    beta: float = 0.0
    sharpe: float = 0.0                   # 夏普比率
    sortino: float = 0.0                  # 索提诺比率
    calmar: float = 0.0                   # 卡玛比率
    information_ratio: float = 0.0        # 信息比率
    treynor: float = 0.0                  # 特雷诺比率
    risk_free_rate: float = 2.0           # 无风险利率 %
    trading_days: int = 0                 # 交易天数


@dataclass
class TradeStatistics:
    """28 交易统计指标 (掘金交易统计)"""
    trading_days: int = 0                    # 交易天数
    up_days: int = 0                         # 上涨天数
    down_days: int = 0                       # 下跌天数
    max_consecutive_up_days: int = 0          # 最大连续上涨天数
    max_consecutive_down_days: int = 0        # 最大连续下跌天数
    close_count: int = 0                     # 平仓次数
    profit_count: int = 0                    # 盈利次数
    loss_count: int = 0                     # 亏损次数
    daily_win_rate: float = 0.0              # 日胜率 %
    win_rate: float = 0.0                    # 胜率 %
    max_single_profit: float = 0.0           # 最大单次盈利 (元)
    avg_profit: float = 0.0                  # 平均单次盈利 (元)
    max_single_loss: float = 0.0             # 最大单次亏损 (元)
    avg_loss: float = 0.0                   # 平均单次亏损 (元)
    profit_loss_ratio: float = 0.0           # 盈亏比
    max_drawdown_duration: int = 0           # 最大回撤持续天数
    max_consecutive_drawdown: float = 0.0    # 最大连续回撤 %
    max_daily_drawdown: float = 0.0          # 最大日回撤 %
    max_weekly_drawdown: float = 0.0         # 最大周回撤 %
    max_monthly_drawdown: float = 0.0        # 最大月回撤 %
    max_drawdown_start: str = ""             # 最大回撤起始日
    max_drawdown_end: str = ""               # 最大回撤结束日
    max_no_new_high_days: int = 0            # 最长不创新高天数
    max_daily_gain: float = 0.0             # 单日最大上涨 %
    max_daily_loss: float = 0.0             # 单日最大下跌 %
    annual_turnover: float = 0.0            # 年换手率


@dataclass
class PerfTradeRecord:
    """交易记录 (信号分析用, 绩效分析专用模型)"""
    timestamp: str = ""
    symbol: str = ""
    side: str = ""        # buy / sell
    price: float = 0.0
    quantity: int = 0
    amount: float = 0.0
    fee: float = 0.0


@dataclass
class OHLCBar:
    """K线数据 (信号分析用)"""
    timestamp: str = ""
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: int = 0


@dataclass
class PerfPositionSnapshot:
    """持仓快照 (持仓分析/每日明细用, 绩效分析专用模型)"""
    date: str = ""
    symbol: str = ""
    side: str = ""          # long / short
    quantity: int = 0
    vwap: float = 0.0      # 持仓均价
    price: float = 0.0     # 当前价
    market_value: float = 0.0
    floating_pnl: float = 0.0


@dataclass
class DailyCapitalRow:
    """当日资金明细 (每日明细用)"""
    date: str = ""
    total_asset: float = 0.0
    cash_balance: float = 0.0
    position_value: float = 0.0
    floating_pnl: float = 0.0
    daily_pnl: float = 0.0
    buy_open_amount: float = 0.0
    buy_close_amount: float = 0.0
    sell_open_amount: float = 0.0
    sell_close_amount: float = 0.0
    fee: float = 0.0


@dataclass
class OrderRecord:
    """当日委托 (每日明细用)"""
    order_time: str = ""
    fill_time: str = ""
    symbol: str = ""
    name: str = ""
    side: str = ""
    price: float = 0.0
    quantity: int = 0
    filled_quantity: int = 0
    avg_fill_price: float = 0.0
    fee: float = 0.0
    status: str = ""


@dataclass
class BacktestPerformanceData:
    """回测绩效完整数据模型 (掘金风格)"""
    # 基本信息
    backtest_id: str = ""
    strategy_id: str = ""
    start_date: str = ""
    end_date: str = ""
    initial_asset: float = 10_000_000.0
    benchmark_symbol: str = "沪深300"

    # 时间序列 (掘金净值数据字段)
    timestamps: list[str] = field(default_factory=list)
    nav_curve: list[float] = field(default_factory=list)                # 单位净值
    strategy_yield: list[float] = field(default_factory=list)           # 累计收益率 %
    strategy_yield_daily: list[float] = field(default_factory=list)     # 每日收益率 %
    strategy_drawdown: list[float] = field(default_factory=list)        # 回撤 %
    benchmark_price: list[float] = field(default_factory=list)
    benchmark_yield: list[float] = field(default_factory=list)
    benchmark_yield_daily: list[float] = field(default_factory=list)
    benchmark_drawdown: list[float] = field(default_factory=list)

    # 交易 & 持仓 & K线
    trades: list[PerfTradeRecord] = field(default_factory=list)
    ohlc_daily: list[OHLCBar] = field(default_factory=list)
    positions: list[PerfPositionSnapshot] = field(default_factory=list)
    daily_capital: list[DailyCapitalRow] = field(default_factory=list)
    orders: list[OrderRecord] = field(default_factory=list)
    monthly_returns: list[list[float]] = field(default_factory=list)    # [year][month] %

    # 指标
    performance: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    trade_stats: TradeStatistics = field(default_factory=TradeStatistics)


# ===== Mock 数据生成器 (掘金风格示例) =====

# 裁定#217 Tier2 P3 Extract Method 重构（2026-07-15）
# 原 generate_demo_performance_data 308行 McCabe=34（13段顺序数据生成）。
# 治本：提取为 12 个模块级 helper（均 McCabe≤15），主函数简化为编排（McCabe≈1）。
# 行为等价：rng 调用顺序完全保留（daily_ret→benchmark→trades→ohlc→positions→daily_capital），
# 浮点运算 bit-identical（sum/mean 预计算不改变 IEEE754 结果）。

_DEMO_SYMBOLS = ["000001.SZ", "600000.SH", "000300.SH", "600519.SH", "000858.SZ"]


def _gen_trading_dates(start: datetime, end: datetime) -> list[datetime]:
    """生成交易日列表 (跳过周末)。"""
    dates: list[datetime] = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            dates.append(d)
        d += timedelta(days=1)
    return dates


def _gen_strategy_daily_ret(rng: random.Random, n: int) -> list[float]:
    """模拟策略日收益率 (AR(1) + noise + 大跌)。"""
    daily_ret: list[float] = []
    prev = 0.0
    for i in range(n):
        base = 0.0010
        ar = 0.15 * prev
        noise = rng.gauss(0, 0.013)
        r = base + ar + noise
        if i in (180, 181, 182, 350, 351):
            r -= 0.025
        daily_ret.append(r)
        prev = r
    return daily_ret


def _compute_nav_yield_drawdown(
    daily_ret: list[float], n: int,
) -> tuple[list[float], list[float], list[float], list[float]]:
    """计算累计净值、累计收益率%、每日收益率%、回撤%。"""
    nav = [1.0]
    for r in daily_ret:
        nav.append(nav[-1] * (1 + r))
    nav = nav[1:]
    if len(nav) != n:
        nav = nav[:n]
    strategy_yield = [(v - 1) * 100 for v in nav]
    strategy_yield_daily = [r * 100 for r in daily_ret]
    strategy_drawdown: list[float] = []
    peak = nav[0]
    for v in nav:
        peak = max(peak, v)
        strategy_drawdown.append((v / peak - 1) * 100)
    return nav, strategy_yield, strategy_yield_daily, strategy_drawdown


def _simulate_benchmark(
    rng: random.Random, n: int,
) -> tuple[list[float], list[float], list[float], list[float], list[float], list[float]]:
    """模拟基准 (沪深300)。返回 (bench_ret, bench_nav, price, yield, yield_daily, drawdown)。"""
    bench_ret: list[float] = []
    prev_b = 0.0
    for i in range(n):
        r = 0.0005 + 0.1 * prev_b + rng.gauss(0, 0.013)
        bench_ret.append(r)
        prev_b = r
    bench_nav = [1.0]
    for r in bench_ret:
        bench_nav.append(bench_nav[-1] * (1 + r))
    bench_nav = bench_nav[1:n+1] if len(bench_nav) >= n else bench_nav + [bench_nav[-1]] * (n - len(bench_nav))
    bench_nav = bench_nav[:n]
    benchmark_price = [3500 * v for v in bench_nav]
    benchmark_yield = [(v - 1) * 100 for v in bench_nav]
    benchmark_yield_daily = [r * 100 for r in bench_ret]
    benchmark_drawdown: list[float] = []
    bp = bench_nav[0]
    for v in bench_nav:
        bp = max(bp, v)
        benchmark_drawdown.append((v / bp - 1) * 100)
    return bench_ret, bench_nav, benchmark_price, benchmark_yield, benchmark_yield_daily, benchmark_drawdown


def _compute_perf_metrics(
    nav: list[float], daily_ret: list[float], bench_ret: list[float],
    bench_nav: list[float], n: int, max_dd: float,
) -> PerformanceMetrics:
    """计算绩效指标 (16指标, 参照掘金截图)。"""
    final_asset = 10_000_000.0 * nav[-1]
    cum_ret = (nav[-1] - 1) * 100
    bench_ret_total = (bench_nav[-1] - 1) * 100
    excess = cum_ret - bench_ret_total
    annual_ret = (nav[-1] ** (250.0 / n) - 1) * 100
    vol = math.sqrt(250) * (math.sqrt(sum(r ** 2 for r in daily_ret) / n - (sum(daily_ret) / n) ** 2)) * 100
    sharpe = (annual_ret - 2.0) / vol if vol > 0 else 0
    mean_dr = sum(daily_ret) / n
    mean_br = sum(bench_ret) / n
    cov = sum((daily_ret[i] - mean_dr) * (bench_ret[i] - mean_br) for i in range(n)) / n
    var_b = sum((r - mean_br) ** 2 for r in bench_ret) / n
    beta = cov / var_b if var_b > 0 else 1.0
    alpha = annual_ret - 2.0 - beta * (bench_ret_total * (250.0 / n) / 100 * 100 - 2.0)
    downside = [min(r, 0) for r in daily_ret]
    downside_vol = math.sqrt(250) * (math.sqrt(sum(r ** 2 for r in downside) / n)) * 100
    sortino = (annual_ret - 2.0) / downside_vol if downside_vol > 0 else 0
    calmar = annual_ret / abs(max_dd) if max_dd != 0 else 0
    excess_daily = [daily_ret[i] - bench_ret[i] for i in range(n)]
    excess_vol = math.sqrt(250) * (math.sqrt(sum(r ** 2 for r in excess_daily) / n - (sum(excess_daily) / n) ** 2)) * 100
    ir = (annual_ret - bench_ret_total) / excess_vol if excess_vol > 0 else 0
    treynor = (annual_ret - 2.0) / beta if beta != 0 else 0
    return PerformanceMetrics(
        initial_asset=10_000_000.0,
        final_asset=final_asset,
        cumulative_pnl=final_asset - 10_000_000.0,
        cumulative_fee=53_436.96,
        cumulative_return=cum_ret,
        benchmark_return=bench_ret_total,
        excess_return=excess,
        annual_return=annual_ret,
        max_drawdown=max_dd,
        annual_volatility=vol,
        win_rate=66.29,
        alpha=0.39,
        beta=beta,
        sharpe=sharpe,
        sortino=sortino,
        calmar=calmar,
        information_ratio=ir,
        treynor=treynor,
        risk_free_rate=2.0,
        trading_days=n,
    )


def _compute_trade_stats(
    daily_ret: list[float], strategy_yield_daily: list[float],
    n: int, max_dd: float,
) -> TradeStatistics:
    """计算交易统计 (28指标)。"""
    up_days = sum(1 for r in daily_ret if r > 0)
    down_days = sum(1 for r in daily_ret if r < 0)
    max_up = max_dn = cur_up = cur_dn = 0
    for r in daily_ret:
        if r > 0:
            cur_up += 1
            cur_dn = 0
        else:
            cur_dn += 1
            cur_up = 0
        max_up = max(max_up, cur_up)
        max_dn = max(max_dn, cur_dn)
    return TradeStatistics(
        trading_days=n,
        up_days=up_days,
        down_days=down_days,
        max_consecutive_up_days=max_up,
        max_consecutive_down_days=max_dn,
        close_count=120,
        profit_count=80,
        loss_count=40,
        daily_win_rate=up_days / n * 100,
        win_rate=66.29,
        max_single_profit=1_580_000.0,
        avg_profit=85_200.0,
        max_single_loss=-420_000.0,
        avg_loss=-48_500.0,
        profit_loss_ratio=1.76,
        max_drawdown_duration=42,
        max_consecutive_drawdown=max_dd,
        max_daily_drawdown=min(strategy_yield_daily),
        max_weekly_drawdown=-8.5,
        max_monthly_drawdown=-12.3,
        max_drawdown_start="2019-07-15",
        max_drawdown_end="2019-08-26",
        max_no_new_high_days=58,
        max_daily_gain=max(strategy_yield_daily),
        max_daily_loss=min(strategy_yield_daily),
        annual_turnover=12.5,
    )


def _gen_trades(rng: random.Random, dates: list[datetime], n: int) -> list[PerfTradeRecord]:
    """生成交易记录 (每4天一笔)。"""
    trades: list[PerfTradeRecord] = []
    for i in range(0, n, 4):
        dt = dates[i]
        side = "buy" if i % 8 == 0 else "sell"
        sym = _DEMO_SYMBOLS[i % len(_DEMO_SYMBOLS)]
        price = 10 + rng.random() * 50
        qty = 1000 + rng.randint(0, 5000)
        trades.append(PerfTradeRecord(
            timestamp=dt.strftime("%Y-%m-%d %H:%M:%S"),
            symbol=sym,
            side=side,
            price=round(price, 3),
            quantity=qty,
            amount=round(price * qty, 2),
            fee=round(price * qty * 0.0003, 2),
        ))
    return trades


def _gen_ohlc_daily(rng: random.Random, dates: list[datetime], daily_ret: list[float]) -> list[OHLCBar]:
    """生成K线数据 (日线, 用模拟的价格序列)。"""
    ohlc_daily: list[OHLCBar] = []
    base_price = 15.0
    for i, dt in enumerate(dates):
        op = base_price
        close = op * (1 + daily_ret[i])
        hi = max(op, close) * (1 + abs(rng.gauss(0, 0.005)))
        lo = min(op, close) * (1 - abs(rng.gauss(0, 0.005)))
        vol = rng.randint(500000, 5000000)
        ohlc_daily.append(OHLCBar(
            timestamp=dt.strftime("%Y-%m-%d"),
            open=round(op, 3),
            high=round(hi, 3),
            low=round(lo, 3),
            close=round(close, 3),
            volume=vol,
        ))
        base_price = close
    return ohlc_daily


def _gen_positions(rng: random.Random, dates: list[datetime], n: int) -> list[PerfPositionSnapshot]:
    """生成持仓快照 (每周一次, 3个标的)。"""
    positions: list[PerfPositionSnapshot] = []
    pos_symbols = _DEMO_SYMBOLS[:3]
    for i in range(0, n, 5):
        dt = dates[i]
        for sym in pos_symbols:
            qty = rng.randint(500, 10000)
            vwap = 10 + rng.random() * 40
            price = vwap * (1 + rng.gauss(0, 0.05))
            mv = price * qty
            fpnl = (price - vwap) * qty
            positions.append(PerfPositionSnapshot(
                date=dt.strftime("%Y-%m-%d"),
                symbol=sym,
                side="long",
                quantity=qty,
                vwap=round(vwap, 3),
                price=round(price, 3),
                market_value=round(mv, 2),
                floating_pnl=round(fpnl, 2),
            ))
    return positions


def _gen_daily_capital(
    rng: random.Random, dates: list[datetime], nav: list[float],
    daily_ret: list[float], n: int,
) -> list[DailyCapitalRow]:
    """生成每日资金 (每3天采样)。"""
    daily_capital: list[DailyCapitalRow] = []
    for i in range(0, n, 3):
        dt = dates[i]
        total = 10_000_000.0 * nav[i]
        pos_val = total * (0.3 + rng.random() * 0.4)
        cash = total - pos_val
        daily_capital.append(DailyCapitalRow(
            date=dt.strftime("%Y-%m-%d"),
            total_asset=round(total, 2),
            cash_balance=round(cash, 2),
            position_value=round(pos_val, 2),
            floating_pnl=round(pos_val * rng.gauss(0, 0.02), 2),
            daily_pnl=round(total * daily_ret[i], 2),
            buy_open_amount=round(rng.random() * 500000, 2) if i % 8 == 0 else 0,
            buy_close_amount=0,
            sell_open_amount=0,
            sell_close_amount=round(rng.random() * 500000, 2) if i % 8 == 4 else 0,
            fee=round(rng.random() * 2000, 2),
        ))
    return daily_capital


def _gen_orders(trades: list[PerfTradeRecord]) -> list[OrderRecord]:
    """生成委托记录 (前50笔)。"""
    orders: list[OrderRecord] = []
    for t in trades[:50]:
        orders.append(OrderRecord(
            order_time=t.timestamp,
            fill_time=t.timestamp,
            symbol=t.symbol,
            name=f"标的{t.symbol[:6]}",
            side=t.side,
            price=t.price,
            quantity=t.quantity,
            filled_quantity=t.quantity,
            avg_fill_price=t.price,
            fee=t.fee,
            status="FILLED",
        ))
    return orders


def _compute_monthly_returns(dates: list[datetime], daily_ret: list[float]) -> list[list[float]]:
    """计算月度收益矩阵 [2019, 2020] x [1-12月]。"""
    monthly_returns = [[0.0] * 12 for _ in range(2)]
    for i, dt in enumerate(dates):
        yr = dt.year - 2019
        mo = dt.month - 1
        if 0 <= yr < 2 and 0 <= mo < 12:
            monthly_returns[yr][mo] += daily_ret[i] * 100
    return monthly_returns


def generate_demo_performance_data() -> BacktestPerformanceData:
    """生成掘金风格示例回测数据 (2019-01-01 ~ 2020-12-31, 488交易日)

    参照掘金3截图:
      期初资产: 10,000,000.00  期末资产: 28,158,840.64
      累计收益率: 181.59%  年化收益率: 69.96%  最大回撤: -17.09%
      夏普比率: 12.40  交易天数: 488
    """
    rng = random.Random(42)  # 固定种子保证可复现
    start = datetime(2019, 1, 2)
    end = datetime(2020, 12, 31)
    dates = _gen_trading_dates(start, end)
    n = len(dates)
    timestamps = [dt.strftime('%Y-%m-%d') for dt in dates]
    daily_ret = _gen_strategy_daily_ret(rng, n)
    nav, strategy_yield, strategy_yield_daily, strategy_drawdown = _compute_nav_yield_drawdown(daily_ret, n)
    bench_ret, bench_nav, benchmark_price, benchmark_yield, benchmark_yield_daily, benchmark_drawdown = _simulate_benchmark(rng, n)
    max_dd = min(strategy_drawdown)
    perf = _compute_perf_metrics(nav, daily_ret, bench_ret, bench_nav, n, max_dd)
    trade_stats = _compute_trade_stats(daily_ret, strategy_yield_daily, n, max_dd)
    trades = _gen_trades(rng, dates, n)
    ohlc_daily = _gen_ohlc_daily(rng, dates, daily_ret)
    positions = _gen_positions(rng, dates, n)
    daily_capital = _gen_daily_capital(rng, dates, nav, daily_ret, n)
    orders = _gen_orders(trades)
    monthly_returns = _compute_monthly_returns(dates, daily_ret)
    return BacktestPerformanceData(
        backtest_id='demo-perf-001',
        strategy_id='行业轮动替换fundamental',
        start_date='2019-01-02',
        end_date='2020-12-31',
        initial_asset=10_000_000.0,
        benchmark_symbol='沪深300',
        timestamps=timestamps,
        nav_curve=nav,
        strategy_yield=strategy_yield,
        strategy_yield_daily=strategy_yield_daily,
        strategy_drawdown=strategy_drawdown,
        benchmark_price=benchmark_price,
        benchmark_yield=benchmark_yield,
        benchmark_yield_daily=benchmark_yield_daily,
        benchmark_drawdown=benchmark_drawdown,
        trades=trades,
        ohlc_daily=ohlc_daily,
        positions=positions,
        daily_capital=daily_capital,
        orders=orders,
        monthly_returns=monthly_returns,
        performance=perf,
        trade_stats=trade_stats,
    )


# ===== UI 辅助函数 =====

def _kpi_card(label_zh: str, label_en: str, value: str, color: str = _TEXT) -> object:
    """生成单个 KPI 卡片 (掘金风格: 标签 + 大号数值)"""
    if pn is None:
        return {"label_zh": label_zh, "label_en": label_en, "value": value, "color": color}
    return pn.Card(
        pn.pane.Markdown(
            f"<div style='text-align:center;'>"
            f"<div style='color:{_TEXT_DIM};font-size:12px;'>{label_zh}</div>"
            f"<div style='color:{_TEXT_DIM};font-size:11px;'>{label_en}</div>"
            f"<div style='color:{color};font-size:22px;font-weight:bold;margin-top:6px;'>{value}</div>"
            f"</div>",
            styles={"background": "transparent"},
        ),
        styles={
            "background": _CARD_BG,
            "border": f"1px solid {_BORDER}",
            "border-radius": "6px",
            "padding": "8px",
            "box-shadow": "none",
        },
        sizing_mode="stretch_width",
    )


def _section_header(title: str) -> object:
    """章节标题 (中英双语)"""
    if pn is None:
        return title
    return pn.pane.Markdown(
        f"#### {title}",
        styles={"color": _TEXT, "border-bottom": f"2px solid {_BORDER}", "padding-bottom": "4px"},
    )


def _fmt_money(v: float) -> str:
    """金额格式化 (万元/亿元)"""
    if abs(v) >= 1_0000_0000:
        return f"{v / 1_0000_0000:.2f}亿"
    if abs(v) >= 1_0000:
        return f"{v / 1_0000:.2f}万"
    return f"{v:.2f}"


def _fmt_pct(v: float, decimals: int = 2) -> str:
    return f"{v:.{decimals}f}%"


# ===== Tab 1: 绩效概览 =====

def _render_overview(data: BacktestPerformanceData) -> object:
    """Tab 1 绩效概览: 信息横幅 + 6 KPI + 收益图 + 回撤图 + 日收益率图 + 16指标表"""
    p = data.performance
    items: list[Any] = []

    # 信息横幅
    banner = pn.pane.HTML(
        f"<div style='background:{_CARD_BG};border:1px solid {_BORDER};border-radius:6px;"
        f"padding:10px 16px;color:{_TEXT};font-size:13px;'>"
        f"<b>回测时间 Backtest Period:</b> {data.start_date} ~ {data.end_date} &nbsp;|&nbsp; "
        f"<b>期初资金 Initial Capital:</b> ¥{p.initial_asset:,.2f} &nbsp;|&nbsp; "
        f"<b>基准 Benchmark:</b> {data.benchmark_symbol} &nbsp;|&nbsp; "
        f"<b>状态 Status:</b> <span style='color:{_GREEN};'>已完成 Completed</span> &nbsp;|&nbsp; "
        f"<b>交易天数 Trading Days:</b> {p.trading_days}"
        f"</div>",
        sizing_mode="stretch_width",
    )
    items.append(banner)

    # 6 KPI 卡片
    kpi_row1 = pn.Row(
        _kpi_card("累计收益率", "Cumulative Return", _fmt_pct(p.cumulative_return), _GREEN if p.cumulative_return >= 0 else _RED),
        _kpi_card("年化收益率", "Annual Return", _fmt_pct(p.annual_return), _GREEN if p.annual_return >= 0 else _RED),
        _kpi_card("最大回撤", "Max Drawdown", _fmt_pct(p.max_drawdown), _RED),
        _kpi_card("夏普比率", "Sharpe Ratio", f"{p.sharpe:.2f}", _BLUE),
        _kpi_card("胜率", "Win Rate", _fmt_pct(p.win_rate), _YELLOW),
        _kpi_card("盈亏比", "Profit/Loss Ratio", f"{data.trade_stats.profit_loss_ratio:.2f}", _ORANGE),
        sizing_mode="stretch_width",
    )
    items.append(kpi_row1)

    # 收益图 (3线: 策略收益/基准收益/超额收益)
    if go is not None and data.strategy_yield:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=data.timestamps, y=data.strategy_yield, name="策略收益 Strategy",
            line=dict(color=_BLUE, width=1.5),
            hovertemplate="日期: %{x}<br>收益: %{y:.2f}%<extra></extra>",
        ))
        fig1.add_trace(go.Scatter(
            x=data.timestamps, y=data.benchmark_yield, name="沪深300 Benchmark",
            line=dict(color=_PURPLE, width=1.5),
            hovertemplate="日期: %{x}<br>基准: %{y:.2f}%<extra></extra>",
        ))
        excess_line = [s - b for s, b in zip(data.strategy_yield, data.benchmark_yield)]
        fig1.add_trace(go.Scatter(
            x=data.timestamps, y=excess_line, name="超额收益 Excess",
            line=dict(color=_ORANGE, width=1.5, dash="dot"),
            hovertemplate="日期: %{x}<br>超额: %{y:.2f}%<extra></extra>",
        ))
        fig1.update_layout(
            title="收益图 Performance Chart",
            xaxis_title="时间 Time", yaxis_title="收益率 Yield (%)",
            template=_DARK_TEMPLATE, height=400,
            hovermode="x unified", legend=dict(orientation="h", y=-0.2),
            dragmode="zoom", clickmode="event+select",
        )
        items.append(pn.pane.Plotly(fig1, sizing_mode="stretch_width"))

    # 回撤图 (2线: 策略回撤/基准回撤, 填充)
    if go is not None and data.strategy_drawdown:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=data.timestamps, y=data.strategy_drawdown, name="策略回撤 Strategy DD",
            fill="tozeroy", line=dict(color=_RED, width=1),
            hovertemplate="日期: %{x}<br>回撤: %{y:.2f}%<extra></extra>",
        ))
        fig2.add_trace(go.Scatter(
            x=data.timestamps, y=data.benchmark_drawdown, name="沪深300回撤 Benchmark DD",
            fill="tozeroy", line=dict(color=_PURPLE, width=1),
            hovertemplate="日期: %{x}<br>基准回撤: %{y:.2f}%<extra></extra>",
        ))
        fig2.update_layout(
            title="回撤图 Drawdown Chart",
            xaxis_title="时间 Time", yaxis_title="回撤 Drawdown (%)",
            template=_DARK_TEMPLATE, height=300,
            hovermode="x unified", legend=dict(orientation="h", y=-0.2),
        )
        items.append(pn.pane.Plotly(fig2, sizing_mode="stretch_width"))

    # 日收益率柱状图 (策略 vs 基准, 并排)
    if go is not None and data.strategy_yield_daily:
        # 降采样: 超过500点用 FigureResampler
        if FigureResampler is not None and len(data.strategy_yield_daily) > 500:
            fig3 = FigureResampler(default_n_shown_samples=500)
        else:
            fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=data.timestamps, y=data.strategy_yield_daily, name="策略日收益率 Strategy",
            marker_color=[_GREEN if v >= 0 else _RED for v in data.strategy_yield_daily],
            opacity=0.7,
            hovertemplate="日期: %{x}<br>日收益: %{y:.2f}%<extra></extra>",
        ))
        fig3.add_trace(go.Scatter(
            x=data.timestamps, y=data.benchmark_yield_daily, name="沪深300日收益率 Benchmark",
            line=dict(color=_PURPLE, width=1),
            hovertemplate="日期: %{x}<br>基准日收益: %{y:.2f}%<extra></extra>",
        ))
        fig3.update_layout(
            title="日收益率 Daily Returns",
            xaxis_title="时间 Time", yaxis_title="日收益率 Daily Return (%)",
            template=_DARK_TEMPLATE, height=300,
            barmode="group", hovermode="x unified", legend=dict(orientation="h", y=-0.2),
        )
        items.append(pn.pane.Plotly(fig3, sizing_mode="stretch_width"))

    # 16 绩效指标表
    if go is not None:
        metrics_data = [
            ("期初资产 Initial Asset", f"¥{p.initial_asset:,.2f}"),
            ("期末资产 Final Asset", f"¥{p.final_asset:,.2f}"),
            ("累计盈亏 Cumulative PnL", f"¥{p.cumulative_pnl:,.2f}", _GREEN if p.cumulative_pnl >= 0 else _RED),
            ("累计手续费 Cumulative Fee", f"¥{p.cumulative_fee:,.2f}"),
            ("累计收益率 Cumulative Return", _fmt_pct(p.cumulative_return), _GREEN),
            ("基准收益率 Benchmark Return", _fmt_pct(p.benchmark_return)),
            ("超额收益率 Excess Return", _fmt_pct(p.excess_return), _ORANGE),
            ("年化收益率 Annual Return", _fmt_pct(p.annual_return), _GREEN),
            ("最大回撤 Max Drawdown", _fmt_pct(p.max_drawdown), _RED),
            ("年化波动率 Annual Volatility", _fmt_pct(p.annual_volatility)),
            ("胜率 Win Rate", _fmt_pct(p.win_rate)),
            ("Alpha", f"{p.alpha:.2f}"),
            ("Beta", f"{p.beta:.2f}"),
            ("夏普比率 Sharpe Ratio", f"{p.sharpe:.2f}", _BLUE),
            ("索提诺比率 Sortino Ratio", f"{p.sortino:.2f}"),
            ("卡玛比率 Calmar Ratio", f"{p.calmar:.2f}"),
            ("信息比率 Information Ratio", f"{p.information_ratio:.2f}"),
            ("特雷诺比率 Treynor Ratio", f"{p.treynor:.2f}"),
            ("无风险利率 Risk-Free Rate", _fmt_pct(p.risk_free_rate)),
            ("交易天数 Trading Days", f"{p.trading_days}"),
        ]
        # 双列布局
        half = (len(metrics_data) + 1) // 2
        col1_vals = [r[1] for r in metrics_data[:half]]
        col1_names = [r[0] for r in metrics_data[:half]]
        col2_vals = [r[1] for r in metrics_data[half:]]
        col2_names = [r[0] for r in metrics_data[half:]]

        fig4 = go.Figure(data=[go.Table(
            header=dict(
                values=["指标 Metric", "值 Value", "指标 Metric", "值 Value"],
                fill_color=_CARD_BG, font=dict(color=_TEXT, size=12),
                align="left", height=28,
            ),
            cells=dict(
                values=[col1_names, col1_vals, col2_names, col2_vals],
                fill_color=_INPUT_BG, font=dict(color=_TEXT, size=11),
                align="left", height=24,
            ),
        )])
        fig4.update_layout(template=_DARK_TEMPLATE, height=500, margin=dict(l=10, r=10, t=30, b=10))
        items.append(_section_header("绩效指标明细 Performance Metrics Detail"))
        items.append(pn.pane.Plotly(fig4, sizing_mode="stretch_width"))

    return pn.Column(*items, sizing_mode="stretch_width") if pn is not None else {"tab": "overview"}


# ===== Tab 2: 持仓分析 =====

def _render_positions(data: BacktestPerformanceData) -> object:
    """Tab 2 持仓分析: 仓位分布堆叠图 + 每日快照表"""
    items: list[Any] = []
    items.append(_section_header("仓位分布 Position Distribution"))

    if go is not None and data.positions:
        # 按日期聚合各标的持仓市值
        dates_map: dict[str, dict[str, float]] = {}
        for pos in data.positions:
            if pos.date not in dates_map:
                dates_map[pos.date] = {}
            dates_map[pos.date][pos.symbol] = pos.market_value

        sorted_dates = sorted(dates_map.keys())
        all_symbols = sorted({s for d in dates_map.values() for s in d.keys()})

        fig = go.Figure()
        for sym in all_symbols:
            vals = [dates_map[d].get(sym, 0) for d in sorted_dates]
            fig.add_trace(go.Scatter(
                x=sorted_dates, y=vals, name=sym, stackgroup="one",
                hovertemplate=f"{sym}<br>日期: %{{x}}<br>市值: ¥%{{y:,.0f}}<extra></extra>",
            ))
        fig.update_layout(
            title="仓位资金分布图 Position Value Distribution",
            xaxis_title="时间 Time", yaxis_title="持仓市值 Position Value (¥)",
            template=_DARK_TEMPLATE, height=400,
            hovermode="x unified", legend=dict(orientation="h", y=-0.2),
        )
        items.append(pn.pane.Plotly(fig, sizing_mode="stretch_width"))

    # 每日快照表
    items.append(_section_header("每日快照 Daily Snapshot"))
    if go is not None and data.positions:
        # 取最近20条
        recent = data.positions[-20:]
        fig2 = go.Figure(data=[go.Table(
            header=dict(
                values=["日期 Date", "代码 Symbol", "方向 Side", "数量 Qty",
                        "均价 VWAP", "当前价 Price", "市值 Market Value", "浮动盈亏 Float PnL"],
                fill_color=_CARD_BG, font=dict(color=_TEXT, size=12), align="center", height=28,
            ),
            cells=dict(
                values=[
                    [p.date for p in recent],
                    [p.symbol for p in recent],
                    [p.side for p in recent],
                    [p.quantity for p in recent],
                    [f"{p.vwap:.3f}" for p in recent],
                    [f"{p.price:.3f}" for p in recent],
                    [f"{p.market_value:,.0f}" for p in recent],
                    [f"{p.floating_pnl:+,.0f}" for p in recent],
                ],
                fill_color=_INPUT_BG, font=dict(color=_TEXT, size=11), align="center", height=22,
            ),
        )])
        fig2.update_layout(template=_DARK_TEMPLATE, height=500, margin=dict(l=10, r=10, t=30, b=10))
        items.append(pn.pane.Plotly(fig2, sizing_mode="stretch_width"))

    return pn.Column(*items, sizing_mode="stretch_width") if pn is not None else {"tab": "positions"}


# ===== Tab 3: 交易统计 =====

def _render_trade_stats(data: BacktestPerformanceData) -> object:
    """Tab 3 交易统计: 28指标网格 + 月度收益热力图"""
    items: list[Any] = []
    ts = data.trade_stats
    items.append(_section_header("交易统计指标 Trade Statistics (28 Metrics)"))

    # 28 指标网格 (用 KPI 卡片)
    metrics = [
        ("交易天数", "Trading Days", f"{ts.trading_days}"),
        ("上涨天数", "Up Days", f"{ts.up_days}", _GREEN),
        ("下跌天数", "Down Days", f"{ts.down_days}", _RED),
        ("最大连续上涨", "Max Consec Up", f"{ts.max_consecutive_up_days}天"),
        ("最大连续下跌", "Max Consec Down", f"{ts.max_consecutive_down_days}天"),
        ("平仓次数", "Close Count", f"{ts.close_count}"),
        ("盈利次数", "Profit Count", f"{ts.profit_count}", _GREEN),
        ("亏损次数", "Loss Count", f"{ts.loss_count}", _RED),
        ("日胜率", "Daily Win Rate", _fmt_pct(ts.daily_win_rate)),
        ("胜率", "Win Rate", _fmt_pct(ts.win_rate), _YELLOW),
        ("最大单次盈利", "Max Single Profit", f"¥{ts.max_single_profit:,.0f}", _GREEN),
        ("平均单次盈利", "Avg Profit", f"¥{ts.avg_profit:,.0f}", _GREEN),
        ("最大单次亏损", "Max Single Loss", f"¥{ts.max_single_loss:,.0f}", _RED),
        ("平均单次亏损", "Avg Loss", f"¥{ts.avg_loss:,.0f}", _RED),
        ("盈亏比", "P/L Ratio", f"{ts.profit_loss_ratio:.2f}", _ORANGE),
        ("最大回撤持续天数", "Max DD Duration", f"{ts.max_drawdown_duration}天"),
        ("最大连续回撤", "Max Consec DD", _fmt_pct(ts.max_consecutive_drawdown), _RED),
        ("最大日回撤", "Max Daily DD", _fmt_pct(ts.max_daily_drawdown), _RED),
        ("最大周回撤", "Max Weekly DD", _fmt_pct(ts.max_weekly_drawdown), _RED),
        ("最大月回撤", "Max Monthly DD", _fmt_pct(ts.max_monthly_drawdown), _RED),
        ("最大回撤起始", "DD Start", ts.max_drawdown_start),
        ("最大回撤结束", "DD End", ts.max_drawdown_end),
        ("最长不创新高", "Max No New High", f"{ts.max_no_new_high_days}天"),
        ("单日最大上涨", "Max Daily Gain", _fmt_pct(ts.max_daily_gain), _GREEN),
        ("单日最大下跌", "Max Daily Loss", _fmt_pct(ts.max_daily_loss), _RED),
        ("年换手率", "Annual Turnover", f"{ts.annual_turnover:.2f}"),
    ]

    # 每6个一行
    rows = []
    for i in range(0, len(metrics), 6):
        batch = metrics[i:i + 6]
        cards = []
        for m in batch:
            color = m[3] if len(m) > 3 else _TEXT
            cards.append(_kpi_card(m[0], m[1], m[2], color))
        rows.append(pn.Row(*cards, sizing_mode="stretch_width"))
    for r in rows:
        items.append(r)

    # 月度收益热力图
    items.append(_section_header("月度收益热力图 Monthly Returns Heatmap"))
    if go is not None and data.monthly_returns:
        years = [2019 + i for i in range(len(data.monthly_returns))]
        months = [f"{i+1}月\nJan" if i < 3 else f"{i+1}月" for i in range(12)]
        months_full = [f"{m}月\n{['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i]}" for i, m in enumerate(range(1, 13))]

        fig = go.Figure(data=go.Heatmap(
            z=data.monthly_returns,
            x=months_full,
            y=[str(y) for y in years],
            colorscale="RdYlGn",
            zmid=0,
            text=[[f"{v:.2f}%" for v in row] for row in data.monthly_returns],
            texttemplate="%{text}",
            textfont=dict(size=11),
            hovertemplate="年份: %{y}<br>月份: %{x}<br>收益: %{z:.2f}%<extra></extra>",
        ))
        fig.update_layout(
            title="月度收益率 Monthly Returns",
            xaxis_title="月份 Month", yaxis_title="年份 Year",
            template=_DARK_TEMPLATE, height=250,
        )
        items.append(pn.pane.Plotly(fig, sizing_mode="stretch_width"))

    return pn.Column(*items, sizing_mode="stretch_width") if pn is not None else {"tab": "trade_stats"}


# ===== Tab 4: 每日明细 =====

def _render_daily_detail(data: BacktestPerformanceData) -> object:
    """Tab 4 每日明细: 日期选择器 + 当日资金/持仓/委托三表"""
    items: list[Any] = []

    if pn is None:
        return {"tab": "daily_detail"}

    # 日期选择器
    available_dates = [dc.date for dc in data.daily_capital] if data.daily_capital else []
    default_date = available_dates[0] if available_dates else ""

    date_picker = pn.widgets.Select(
        name="选择日期 Select Date",
        options=available_dates,
        value=default_date,
        styles={"background": _INPUT_BG, "color": _TEXT},
        sizing_mode="stretch_width",
    )
    items.append(date_picker)

    # 动态表格容器
    tables_col = pn.Column(sizing_mode="stretch_width")

    def update_tables(event):
        """日期变更回调: 刷新三表"""
        sel = event.new if event else default_date
        tables_col.clear()
        if not sel:
            return

        # 当日资金
        cap = next((c for c in data.daily_capital if c.date == sel), None)
        if cap and go is not None:
            fig1 = go.Figure(data=[go.Table(
                header=dict(
                    values=["字段 Field", "值 Value"],
                    fill_color=_CARD_BG, font=dict(color=_TEXT, size=12), align="left", height=28,
                ),
                cells=dict(
                    values=[
                        ["日期 Date", "总资产 Total Asset", "资金余额 Cash Balance", "当日持仓 Position Value",
                         "浮动盈亏 Float PnL", "当日盈亏 Daily PnL", "买开金额 Buy Open", "买平金额 Buy Close",
                         "卖开金额 Sell Open", "卖平金额 Sell Close", "手续费 Fee"],
                        [cap.date, f"¥{cap.total_asset:,.2f}", f"¥{cap.cash_balance:,.2f}",
                         f"¥{cap.position_value:,.2f}", f"¥{cap.floating_pnl:+,.2f}",
                         f"¥{cap.daily_pnl:+,.2f}", f"¥{cap.buy_open_amount:,.2f}",
                         f"¥{cap.buy_close_amount:,.2f}", f"¥{cap.sell_open_amount:,.2f}",
                         f"¥{cap.sell_close_amount:,.2f}", f"¥{cap.fee:,.2f}"],
                    ],
                    fill_color=_INPUT_BG, font=dict(color=_TEXT, size=11), align="left", height=22,
                ),
            )])
            fig1.update_layout(template=_DARK_TEMPLATE, height=350, margin=dict(l=10, r=10, t=30, b=10))
            tables_col.append(_section_header(f"当日资金 Daily Capital ({sel})"))
            tables_col.append(pn.pane.Plotly(fig1, sizing_mode="stretch_width"))

        # 当日持仓
        day_positions = [p for p in data.positions if p.date == sel]
        if day_positions and go is not None:
            fig2 = go.Figure(data=[go.Table(
                header=dict(
                    values=["代码 Symbol", "方向 Side", "数量 Qty", "均价 VWAP",
                            "当前价 Price", "市值 Market Value", "浮动盈亏 Float PnL"],
                    fill_color=_CARD_BG, font=dict(color=_TEXT, size=12), align="center", height=28,
                ),
                cells=dict(
                    values=[
                        [p.symbol for p in day_positions],
                        [p.side for p in day_positions],
                        [p.quantity for p in day_positions],
                        [f"{p.vwap:.3f}" for p in day_positions],
                        [f"{p.price:.3f}" for p in day_positions],
                        [f"{p.market_value:,.0f}" for p in day_positions],
                        [f"{p.floating_pnl:+,.0f}" for p in day_positions],
                    ],
                    fill_color=_INPUT_BG, font=dict(color=_TEXT, size=11), align="center", height=22,
                ),
            )])
            fig2.update_layout(template=_DARK_TEMPLATE, height=200, margin=dict(l=10, r=10, t=30, b=10))
            tables_col.append(_section_header(f"当日持仓 Daily Positions ({sel})"))
            tables_col.append(pn.pane.Plotly(fig2, sizing_mode="stretch_width"))

        # 当日委托
        day_orders = [o for o in data.orders if o.order_time.startswith(sel)]
        if day_orders and go is not None:
            fig3 = go.Figure(data=[go.Table(
                header=dict(
                    values=["委托时间 Order Time", "代码 Symbol", "名称 Name", "方向 Side",
                            "价格 Price", "数量 Qty", "已成交 Filled", "均价 Avg Price",
                            "手续费 Fee", "状态 Status"],
                    fill_color=_CARD_BG, font=dict(color=_TEXT, size=12), align="center", height=28,
                ),
                cells=dict(
                    values=[
                        [o.order_time for o in day_orders],
                        [o.symbol for o in day_orders],
                        [o.name for o in day_orders],
                        [o.side for o in day_orders],
                        [f"{o.price:.3f}" for o in day_orders],
                        [o.quantity for o in day_orders],
                        [o.filled_quantity for o in day_orders],
                        [f"{o.avg_fill_price:.3f}" for o in day_orders],
                        [f"{o.fee:.2f}" for o in day_orders],
                        [o.status for o in day_orders],
                    ],
                    fill_color=_INPUT_BG, font=dict(color=_TEXT, size=11), align="center", height=22,
                ),
            )])
            fig3.update_layout(template=_DARK_TEMPLATE, height=250, margin=dict(l=10, r=10, t=30, b=10))
            tables_col.append(_section_header(f"当日委托 Daily Orders ({sel})"))
            tables_col.append(pn.pane.Plotly(fig3, sizing_mode="stretch_width"))

    date_picker.param.watch(update_tables, "value")
    update_tables(None)  # 初始加载

    items.append(tables_col)
    return pn.Column(*items, sizing_mode="stretch_width")


# ===== Tab 5: 信号分析 (bt-visualizer 风格) =====

def _render_signal_analysis(data: BacktestPerformanceData) -> object:
    """Tab 5 信号分析: K线 + 买卖点打点 + 频度切换 (bt-visualizer hover/click/zoom)"""
    items: list[Any] = []

    if pn is None or go is None:
        return {"tab": "signal"}

    # 频度选择
    freq_selector = pn.widgets.RadioButtonGroup(
        name="频度 Frequency",
        options=["日线 Daily", "60分钟 60min", "30分钟 30min", "15分钟 15min", "5分钟 5min", "1分钟 1min"],
        value="日线 Daily",
        button_type="default",
        styles={"background": _INPUT_BG},
    )
    items.append(freq_selector)

    # 标的选择 (从交易记录提取)
    symbols = sorted({t.symbol for t in data.trades})
    sym_selector = pn.widgets.Select(
        name="标的 Symbol",
        options=symbols if symbols else ["000001.SZ"],
        value=symbols[0] if symbols else "000001.SZ",
        styles={"background": _INPUT_BG, "color": _TEXT},
    )
    items.append(sym_selector)

    chart_col = pn.Column(sizing_mode="stretch_width")
    trade_table_col = pn.Column(sizing_mode="stretch_width")

    def render_kline(event=None):
        """渲染K线 + 买卖点 (bt-visualizer 风格)"""
        chart_col.clear()
        trade_table_col.clear()

        ohlc = data.ohlc_daily
        if not ohlc:
            chart_col.append(pn.pane.Markdown("*无K线数据 No OHLC data*"))
            return

        # 频度降采样 (模拟: 日线全量, 其他频度取前N条)
        freq = freq_selector.value
        if "60分钟" in freq:
            ohlc_show = ohlc[:200]
        elif "30分钟" in freq:
            ohlc_show = ohlc[:300]
        elif "15分钟" in freq:
            ohlc_show = ohlc[:400]
        elif "5分钟" in freq:
            ohlc_show = ohlc[:500]
        elif "1分钟" in freq:
            ohlc_show = ohlc[:600]
        else:
            ohlc_show = ohlc[:500]  # 日线取前500条避免卡顿

        ts_list = [b.timestamp for b in ohlc_show]

        # K线图
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.05, row_heights=[0.7, 0.3],
            subplot_titles=("K线 + 买卖信号 K-Line + Trade Signals", "成交量 Volume"),
        )

        fig.add_trace(go.Candlestick(
            x=ts_list,
            open=[b.open for b in ohlc_show],
            high=[b.high for b in ohlc_show],
            low=[b.low for b in ohlc_show],
            close=[b.close for b in ohlc_show],
            name="K线 K-Line",
            increasing_line_color=_GREEN, decreasing_line_color=_RED,
            increasing_fillcolor=_GREEN, decreasing_fillcolor=_RED,
            whiskerwidth=0.5,
        ), row=1, col=1)

        fig.add_trace(go.Bar(
            x=ts_list, y=[b.volume for b in ohlc_show],
            name="成交量 Volume",
            marker_color=[_GREEN if b.close >= b.open else _RED for b in ohlc_show],
            opacity=0.5,
        ), row=2, col=1)

        # 买卖点打点 (bt-visualizer 核心: hover 交易信息)
        buy_ts = [t.timestamp.split(" ")[0] for t in data.trades if t.side == "buy"]
        buy_pr = [t.price for t in data.trades if t.side == "buy"]
        buy_qty = [t.quantity for t in data.trades if t.side == "buy"]
        buy_amt = [t.amount for t in data.trades if t.side == "buy"]

        sell_ts = [t.timestamp.split(" ")[0] for t in data.trades if t.side == "sell"]
        sell_pr = [t.price for t in data.trades if t.side == "sell"]
        sell_qty = [t.quantity for t in data.trades if t.side == "sell"]
        sell_amt = [t.amount for t in data.trades if t.side == "sell"]

        # 过滤到K线显示范围内
        ts_set = set(ts_list)
        buy_filtered = [(t, p, q, a) for t, p, q, a in zip(buy_ts, buy_pr, buy_qty, buy_amt) if t in ts_set]
        sell_filtered = [(t, p, q, a) for t, p, q, a in zip(sell_ts, sell_pr, sell_qty, sell_amt) if t in ts_set]

        if buy_filtered:
            fig.add_trace(go.Scatter(
                x=[b[0] for b in buy_filtered],
                y=[b[1] for b in buy_filtered],
                mode="markers",
                marker=dict(symbol="triangle-up", size=12, color=_GREEN, line=dict(width=1, color=_TEXT)),
                name="买入 Buy",
                # bt-visualizer 风格: hover 显示完整交易信息
                hovertemplate="<b>买入 BUY</b><br>"
                              "日期: %{x}<br>"
                              "价格: %{y:.3f}<br>"
                              + "数量: " + ", ".join([f"{b[2]}" for b in buy_filtered]) + "<br>"
                              + "金额: ¥" + ", ".join([f"{b[3]:,.0f}" for b in buy_filtered]) + "<extra></extra>",
            ), row=1, col=1)

        if sell_filtered:
            fig.add_trace(go.Scatter(
                x=[s[0] for s in sell_filtered],
                y=[s[1] for s in sell_filtered],
                mode="markers",
                marker=dict(symbol="triangle-down", size=12, color=_RED, line=dict(width=1, color=_TEXT)),
                name="卖出 Sell",
                hovertemplate="<b>卖出 SELL</b><br>"
                              "日期: %{x}<br>"
                              "价格: %{y:.3f}<br>"
                              + "数量: " + ", ".join([f"{s[2]}" for s in sell_filtered]) + "<br>"
                              + "金额: ¥" + ", ".join([f"{s[3]:,.0f}" for s in sell_filtered]) + "<extra></extra>",
            ), row=1, col=1)

        # bt-visualizer 交互特性:
        #   - clickmode: 点击下钻
        #   - dragmode: 缩放
        #   - 双击重置 (plotly 原生)
        fig.update_layout(
            template=_DARK_TEMPLATE,
            height=600,
            xaxis_rangeslider_visible=False,  # 用单独 volume 子图替代
            hovermode="closest",
            clickmode="event+select",
            dragmode="zoom",
            legend=dict(orientation="h", y=-0.05),
            showlegend=True,
        )
        fig.update_yaxes(title_text="价格 Price", row=1, col=1)
        fig.update_yaxes(title_text="成交量 Vol", row=2, col=1)

        chart_col.append(pn.pane.Plotly(fig, sizing_mode="stretch_width", height=620))

        # 交易信号明细表
        recent_trades = data.trades[:30]
        fig2 = go.Figure(data=[go.Table(
            header=dict(
                values=["时间 Time", "代码 Symbol", "方向 Side", "价格 Price",
                        "数量 Qty", "金额 Amount", "手续费 Fee"],
                fill_color=_CARD_BG, font=dict(color=_TEXT, size=12), align="center", height=28,
            ),
            cells=dict(
                values=[
                    [t.timestamp for t in recent_trades],
                    [t.symbol for t in recent_trades],
                    [t.side for t in recent_trades],
                    [f"{t.price:.3f}" for t in recent_trades],
                    [t.quantity for t in recent_trades],
                    [f"{t.amount:,.0f}" for t in recent_trades],
                    [f"{t.fee:.2f}" for t in recent_trades],
                ],
                fill_color=_INPUT_BG, font=dict(color=_TEXT, size=11), align="center", height=22,
            ),
        )])
        fig2.update_layout(template=_DARK_TEMPLATE, height=400, margin=dict(l=10, r=10, t=30, b=10))
        trade_table_col.append(_section_header("交易信号明细 Trade Signal Detail"))
        trade_table_col.append(pn.pane.Plotly(fig2, sizing_mode="stretch_width"))

    freq_selector.param.watch(render_kline, "value")
    sym_selector.param.watch(render_kline, "value")
    render_kline()  # 初始渲染

    items.append(chart_col)
    items.append(trade_table_col)
    return pn.Column(*items, sizing_mode="stretch_width")


# ===== 主渲染函数 =====

def render_backtest_performance(data: BacktestPerformanceData) -> dict[str, Any]:
    """渲染掘金风格 5-Tab 绩效分析布局

    返回 dict (含 _layout 键, 供 app_panel.py 使用)
    """
    payload: dict[str, Any] = {
        "backtest_id": data.backtest_id,
        "strategy_id": data.strategy_id,
        "tabs": ["绩效概览", "持仓分析", "交易统计", "每日明细", "信号分析"],
        "renderer": "panel" if pn is not None else "dict",
    }

    if pn is None:
        return payload

    # 5 子 Tab (嵌套在 app_panel 的 "回测结果" Tab 内)
    sub_tabs = pn.Tabs(
        ("绩效概览 Performance Overview", _render_overview(data)),
        ("持仓分析 Position Analysis", _render_positions(data)),
        ("交易统计 Trade Statistics", _render_trade_stats(data)),
        ("每日明细 Daily Detail", _render_daily_detail(data)),
        ("信号分析 Signal Analysis", _render_signal_analysis(data)),
        tabs_location="above",
        sizing_mode="stretch_width",
    )

    # 策略标题
    header = pn.pane.HTML(
        f"<div style='background:{_CARD_BG};border:1px solid {_BORDER};border-radius:6px;"
        f"padding:12px 16px;margin-bottom:8px;'>"
        f"<span style='color:{_TEXT};font-size:16px;font-weight:bold;'>"
        f"📊 {data.strategy_id}</span>"
        f"<span style='color:{_TEXT_DIM};font-size:12px;margin-left:16px;'>"
        f"回测绩效分析 Backtest Performance Analysis | {data.backtest_id}"
        f"</span></div>",
        sizing_mode="stretch_width",
    )

    layout = pn.Column(header, sub_tabs, sizing_mode="stretch_width")
    payload["_layout"] = layout
    return payload


__all__ = [
    "PerformanceMetrics",
    "TradeStatistics",
    "PerfTradeRecord",
    "OHLCBar",
    "PerfPositionSnapshot",
    "DailyCapitalRow",
    "OrderRecord",
    "BacktestPerformanceData",
    "generate_demo_performance_data",
    "render_backtest_performance",
]
