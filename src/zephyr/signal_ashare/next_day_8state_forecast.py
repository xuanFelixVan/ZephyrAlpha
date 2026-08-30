# [BLUEPRINT] MOD-SIG-037 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md §2.1
# [MODULE] zephyr.signal_ashare.next_day_8state_forecast
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] (待 BM-BUY-01 多情景对策 / 下游风控节流层信号权重修正)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] probabilities 八态 Σ=1.0; top_probability ∈ [0,1]; confidence ∈ [0,1]; 纯函数计算与 DB 加载隔离
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯函数输入长度不足/前收非正 → ValueError; loader 查询为空/失败 → NextDayForecastDataError
# [TESTS] tests/signal_ashare/test_next_day_8state_forecast.py
# [A_module] module_id=MOD-SIG-037 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 指数日 K OHLC 序列（默认 000300，loader 走 market_index_kline 真源表）
# A1: 单日 8 态分类: 振幅≥3% → VIOLENT; |涨跌幅|≤0.3% → FLAT_CLOSE;
#     缺口>+0.5% 高开 / <-0.5% 低开 / 其间平开 × 收≥开高走 / 收<开低走 → 6 网格态
# A2: 一阶马尔可夫转移矩阵: 历史状态转移频次 + Laplace(α=1) 平滑 → 8×8 行归一矩阵
# A3: 平稳分布修正: 幂迭代求 π，预测分布 = (1−blend)×经验行 + blend×π（防稀有态过拟合）
# A4: confidence = top_probability × 支持度因子 min(1, 当前态出发转移数/30)
# O1: NextDayForecast（8 态概率分布 + 众数态 + 置信度，供下游风控节流/权重修正）
# [/ALGO_FLOW]
"""
次日 8 状态预测（交易决策架构 9.2 八态叠加模型，BM-SEL-04，MOD-SIG-037）。

8 态 = 高开高走/高开低走/低开高走/低开低走/平开高走/平开低走/震荡收平/剧烈
震荡，输出次日走势的 8 态概率分布（ΣP=1.0）。引擎为一阶马尔可夫链：历史状
态转移频次估计转移矩阵（Laplace 平滑）+ 平稳分布修正（幂迭代 π 按 blend 混
入经验行，防稀有态过拟合）。

边界声明（90 号 §7 裁定）：八态"点预测"已裁定暂缓（52-53% 天花板实证+T+1
兑现悖论）——本模块**只输出概率分布与置信度，不出点位、不出买卖信号**，供
下游风控节流与信号权重修正消费（与 44 号"只出档位概率不出点位"一致）。

阈值（平开 ±0.5%、收平 ±0.3%、剧烈震荡振幅 3%、blend 0.2）为初拟，待实盘标定。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: bar 参数
#   fields: 参数 bar，类型注解 DailyBar
#   code: next_day_8state_forecast.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: prev_close 参数
#   fields: 参数 prev_close，类型注解 float
#   code: next_day_8state_forecast.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: gap_threshold 参数
#   fields: 参数 gap_threshold（无注解）
#   code: next_day_8state_forecast.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: flat_threshold 参数
#   fields: 参数 flat_threshold（无注解）
#   code: next_day_8state_forecast.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① classify_daily_state
#   name_en: classify_daily_state
#   intro: 单日 K 线 → 8 态分类（优先级：剧烈震荡 > 震荡收平 > 缺口×方向网格）。
#   desc: 单日 K 线 → 8 态分类（优先级：剧烈震荡 > 震荡收平 > 缺口×方向网格）。 Args: bar: 当日 K 线（OHLC）。 prev_close: 前收盘价（必须为正…；源码 L220-L254
#   inputs: bar prev_close gap_threshold flat_threshold violent_amplitude
#   outputs: NextDayState
# - id: A2
#   name_zh: ② build_state_series
#   name_en: build_state_series
#   intro: K 线序列 → 8 态序列（首根无前收跳过，输出长度 = len(bars) − 1）。
#   desc: K 线序列 → 8 态序列（首根无前收跳过，输出长度 = len(bars) − 1）。；源码 L257-L274
#   inputs: bars config
#   outputs: list[NextDayState]
# - id: A3
#   name_zh: ③ estimate_transition_matrix
#   name_en: estimate_transition_matrix
#   intro: 历史状态转移频次 + Laplace 平滑 → 8×8 行归一转移矩阵。
#   desc: 历史状态转移频次 + Laplace 平滑 → 8×8 行归一转移矩阵。 laplace_alpha=0 时无平滑，无出发转移的行保持全零（由 forecast 兜底均匀分布）。；源码 L277-L292
#   inputs: states laplace_alpha
#   outputs: list[list[float]]
# - id: A4
#   name_zh: ④ stationary_distribution
#   name_en: stationary_distribution
#   intro: 幂迭代求马尔可夫链平稳分布 π（π = π×M，每步归一化兜底零行）。
#   desc: 幂迭代求马尔可夫链平稳分布 π（π = π×M，每步归一化兜底零行）。；源码 L295-L320
#   inputs: matrix max_iter tol
#   outputs: list[float]
# - id: A5
#   name_zh: ⑤ forecast_next_day
#   name_en: forecast_next_day
#   intro: 核心纯函数：8 态历史序列 → 次日 8 态概率分布预测。
#   desc: 核心纯函数：8 态历史序列 → 次日 8 态概率分布预测。 预测分布 = (1−blend)×经验转移行 + blend×平稳分布，再归一化； 经验行全零（当前态无出发转移且无平…；源码 L323-L368
#   inputs: states config
#   outputs: NextDayForecast
# - id: A6
#   name_zh: ⑥ NextDay8StateForecaster
#   name_en: NextDay8StateForecaster
#   intro: 次日 8 态预测器（DB 加载层薄封装，计算全部委托纯函数）。
#   desc: 次日 8 态预测器（DB 加载层薄封装，计算全部委托纯函数）。 DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV）， reg…；公共方法（定义序）: load_in…
#   inputs: registry query_fn config
#   outputs: 返回值
#   （注：A6 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: NextDayState
#   name_en: NextDayState
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 BM-BUY-01 多情景对策 / 下游风控节流层信号权重修正)
# - id: O2
#   name_zh: list[NextDayState]
#   name_en: list[NextDayState]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 BM-BUY-01 多情景对策 / 下游风控节流层信号权重修正)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_logger = logging.getLogger(__name__)

__all__: Final = [
    "DailyBar",
    "ForecastConfig",
    "NextDay8StateForecaster",
    "NextDayForecast",
    "NextDayForecastDataError",
    "NextDayState",
    "build_state_series",
    "classify_daily_state",
    "estimate_transition_matrix",
    "forecast_next_day",
    "stationary_distribution",
]

#: 默认市场代理指数（沪深300）
DEFAULT_MARKET_SYMBOL: Final = "000300"

# SQL 模板常量（_SQL_* 前缀约定）
_SQL_INDEX_KLINE = (
    "SELECT trade_date, open, high, low, close FROM {table} FINAL "
    "WHERE symbol = '{symbol}' "
    "AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY trade_date"
)


class NextDayForecastDataError(Exception):
    """次日 8 态预测数据加载失败（loader 查询为空/解析失败）。"""


class NextDayState(str, Enum):
    """次日走势 8 态（交易决策架构 9.2）"""

    GAP_UP_UP = "GAP_UP_UP"  # 高开高走
    GAP_UP_DOWN = "GAP_UP_DOWN"  # 高开低走
    GAP_DOWN_UP = "GAP_DOWN_UP"  # 低开高走
    GAP_DOWN_DOWN = "GAP_DOWN_DOWN"  # 低开低走
    FLAT_UP = "FLAT_UP"  # 平开高走
    FLAT_DOWN = "FLAT_DOWN"  # 平开低走
    FLAT_CLOSE = "FLAT_CLOSE"  # 震荡收平
    VIOLENT = "VIOLENT"  # 剧烈震荡


#: 状态 → 矩阵下标（Enum 定义序即矩阵行序）
_STATE_INDEX: Final = {s: i for i, s in enumerate(NextDayState)}
_N_STATES: Final = len(NextDayState)


@dataclass(frozen=True)
class DailyBar:
    """单日 K 线（OHLC）。"""

    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class ForecastConfig:
    """次日 8 态预测配置（阈值为初拟，待实盘标定）。"""

    gap_threshold: float = 0.005  # 平开带宽：|开盘缺口| ≤ 0.5% 算平开
    flat_threshold: float = 0.003  # 收平带宽：|收盘涨跌幅| ≤ 0.3% 算震荡收平
    violent_amplitude: float = 0.03  # 剧烈震荡：日内振幅 ≥ 3%
    laplace_alpha: float = 1.0  # 转移计数 Laplace 平滑强度
    stationary_blend: float = 0.2  # 平稳分布混入比例（防稀有态过拟合）
    support_full: int = 30  # 当前态出发转移数达到此值时支持度因子为 1
    min_history: int = 30  # 最少状态序列长度


@dataclass(frozen=True)
class NextDayForecast:
    """次日 8 态预测（输出契约：概率分布 + 置信度，非点位/买卖信号）。"""

    current_state: NextDayState  # 当日（最新）状态
    probabilities: dict[NextDayState, float]  # 次日 8 态概率分布，Σ=1
    top_state: NextDayState  # 众数态（概率最大）
    top_probability: float  # 众数态概率 ∈ [0, 1]
    confidence: float  # ∈ [0, 1]
    n_transitions: int  # 估计所用转移样本数


def classify_daily_state(
    bar: DailyBar,
    prev_close: float,
    *,
    gap_threshold: float = 0.005,
    flat_threshold: float = 0.003,
    violent_amplitude: float = 0.03,
) -> NextDayState:
    """单日 K 线 → 8 态分类（优先级：剧烈震荡 > 震荡收平 > 缺口×方向网格）。

    Args:
        bar: 当日 K 线（OHLC）。
        prev_close: 前收盘价（必须为正）。
        gap_threshold: 平开带宽（|缺口| ≤ 此值算平开）。
        flat_threshold: 收平带宽（|涨跌幅| ≤ 此值算震荡收平）。
        violent_amplitude: 剧烈震荡振幅阈值（(high−low)/prev_close）。

    Raises:
        ValueError: prev_close ≤ 0。
    """
    if prev_close <= 0:
        raise ValueError(f"prev_close 必须为正: {prev_close}")
    amplitude = (bar.high - bar.low) / prev_close
    if amplitude >= violent_amplitude:
        return NextDayState.VIOLENT
    daily_ret = bar.close / prev_close - 1.0
    if abs(daily_ret) <= flat_threshold:
        return NextDayState.FLAT_CLOSE
    gap = bar.open / prev_close - 1.0
    walk_up = bar.close >= bar.open
    if gap > gap_threshold:
        return NextDayState.GAP_UP_UP if walk_up else NextDayState.GAP_UP_DOWN
    if gap < -gap_threshold:
        return NextDayState.GAP_DOWN_UP if walk_up else NextDayState.GAP_DOWN_DOWN
    return NextDayState.FLAT_UP if walk_up else NextDayState.FLAT_DOWN


def build_state_series(
    bars: Sequence[DailyBar],
    config: ForecastConfig | None = None,
) -> list[NextDayState]:
    """K 线序列 → 8 态序列（首根无前收跳过，输出长度 = len(bars) − 1）。"""
    cfg = config or ForecastConfig()
    states: list[NextDayState] = []
    for i in range(1, len(bars)):
        states.append(
            classify_daily_state(
                bars[i],
                bars[i - 1].close,
                gap_threshold=cfg.gap_threshold,
                flat_threshold=cfg.flat_threshold,
                violent_amplitude=cfg.violent_amplitude,
            )
        )
    return states


def estimate_transition_matrix(
    states: Sequence[NextDayState],
    laplace_alpha: float = 1.0,
) -> list[list[float]]:
    """历史状态转移频次 + Laplace 平滑 → 8×8 行归一转移矩阵。

    laplace_alpha=0 时无平滑，无出发转移的行保持全零（由 forecast 兜底均匀分布）。
    """
    counts = [[laplace_alpha] * _N_STATES for _ in range(_N_STATES)]
    for i in range(len(states) - 1):
        counts[_STATE_INDEX[states[i]]][_STATE_INDEX[states[i + 1]]] += 1.0
    matrix: list[list[float]] = []
    for row in counts:
        total = sum(row)
        matrix.append([c / total for c in row] if total > 0 else [0.0] * _N_STATES)
    return matrix


def stationary_distribution(
    matrix: Sequence[Sequence[float]],
    max_iter: int = 1000,
    tol: float = 1e-12,
) -> list[float]:
    """幂迭代求马尔可夫链平稳分布 π（π = π×M，每步归一化兜底零行）。"""
    n = len(matrix)
    dist = [1.0 / n] * n
    for _ in range(max_iter):
        nxt = [0.0] * n
        for i in range(n):
            di = dist[i]
            if di == 0.0:
                continue
            row = matrix[i]
            for j in range(n):
                nxt[j] += di * row[j]
        total = sum(nxt)
        if total <= 0:
            break
        nxt = [v / total for v in nxt]
        if max(abs(nxt[i] - dist[i]) for i in range(n)) < tol:
            dist = nxt
            break
        dist = nxt
    return dist


def forecast_next_day(
    states: Sequence[NextDayState],
    config: ForecastConfig | None = None,
) -> NextDayForecast:
    """核心纯函数：8 态历史序列 → 次日 8 态概率分布预测。

    预测分布 = (1−blend)×经验转移行 + blend×平稳分布，再归一化；
    经验行全零（当前态无出发转移且无平滑）时兜底为平稳分布。

    Raises:
        ValueError: 状态序列长度不足 config.min_history。
    """
    cfg = config or ForecastConfig()
    if len(states) < cfg.min_history:
        raise ValueError(f"states 长度 {len(states)} 不足 min_history={cfg.min_history}")

    matrix = estimate_transition_matrix(states, cfg.laplace_alpha)
    stationary = stationary_distribution(matrix)
    current = states[-1]
    row = matrix[_STATE_INDEX[current]]

    blend = max(0.0, min(1.0, cfg.stationary_blend))
    probs = [(1.0 - blend) * row[j] + blend * stationary[j] for j in range(_N_STATES)]
    total = sum(probs)
    if total <= 0:
        probs = list(stationary)
        total = sum(probs)
    probs = [p / total for p in probs]

    probabilities = {s: probs[_STATE_INDEX[s]] for s in NextDayState}
    top_state = max(probabilities, key=lambda s: probabilities[s])
    top_probability = probabilities[top_state]

    # 支持度：当前态出发的历史转移数 → 支持度因子（满 support_full 记 1）
    support = sum(1 for i in range(len(states) - 1) if states[i] == current)
    support_factor = min(1.0, support / cfg.support_full) if cfg.support_full > 0 else 1.0
    confidence = top_probability * support_factor

    return NextDayForecast(
        current_state=current,
        probabilities=probabilities,
        top_state=top_state,
        top_probability=top_probability,
        confidence=max(0.0, min(1.0, confidence)),
        n_transitions=len(states) - 1,
    )


class NextDay8StateForecaster:
    """次日 8 态预测器（DB 加载层薄封装，计算全部委托纯函数）。

    DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV），
    registry 默认 get_registry()（表名经 TableRegistry 派生，禁止硬编码）。
    """

    def __init__(
        self,
        registry: object = None,
        query_fn: Callable[..., str] | None = None,
        config: ForecastConfig | None = None,
    ) -> None:
        self._registry = registry
        self._query_fn = query_fn
        self._config = config or ForecastConfig()

    def _resolve_query_fn(self) -> Callable[..., str]:
        if self._query_fn is not None:
            return self._query_fn
        from zephyr.data import ch_reader  # 延迟导入，保持纯函数路径零 DB 依赖

        return ch_reader.query

    def _resolve_table(self) -> str:
        registry = self._registry
        if registry is None:
            from zephyr.data.table_registry import get_registry

            registry = get_registry()
        return registry.table("market_index_kline")

    def load_index_bars(
        self,
        symbol: str = DEFAULT_MARKET_SYMBOL,
        start: str = "2010-01-01",
        end: str = "2099-12-31",
    ) -> list[DailyBar]:
        """从 market_index_kline 加载指数日 K OHLC（升序）。

        Raises:
            NextDayForecastDataError: 查询为空或无可解析行。
        """
        sql = _SQL_INDEX_KLINE.format(table=self._resolve_table(), symbol=symbol, start=start, end=end)
        tsv = self._resolve_query_fn()(sql)
        bars: list[DailyBar] = []
        for line in (tsv or "").strip().split("\n"):
            parts = line.rstrip("\r").split("\t")
            if len(parts) >= 5:
                try:
                    bars.append(
                        DailyBar(
                            open=float(parts[1]),
                            high=float(parts[2]),
                            low=float(parts[3]),
                            close=float(parts[4]),
                        )
                    )
                except ValueError:
                    _logger.warning("next_day_8state_forecast 跳过不可解析行: %s", line[:80])
        if not bars:
            raise NextDayForecastDataError(f"market_index_kline 查询为空: symbol={symbol}, [{start}, {end}]")
        return bars

    def forecast(
        self,
        symbol: str = DEFAULT_MARKET_SYMBOL,
        start: str = "2010-01-01",
        end: str = "2099-12-31",
    ) -> NextDayForecast:
        """加载指数日 K 并输出次日 8 态预测（计算委托纯函数链）。"""
        bars = self.load_index_bars(symbol, start, end)
        states = build_state_series(bars, self._config)
        return forecast_next_day(states, self._config)
