# [BLUEPRINT] MOD-SIG-036 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md §2.1
# [MODULE] zephyr.signal_ashare.market_state_sensor
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] (待 regime_change_detector / next_day_8state_forecast / 下游风控节流层)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] trend_score ∈ [-1,1]; vol_percentile ∈ [0,1]; confidence ∈ [0,1]; 9 网格单状态输出; 纯函数计算与 DB 加载隔离
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯函数输入长度不足 → ValueError; loader 查询为空/失败 → MarketStateDataError
# [TESTS] tests/signal_ashare/test_market_state_sensor.py
# [A_module] module_id=MOD-SIG-036 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 指数日 K 收盘序列 closes（默认 000300 沪深300，loader 走 market_index_kline 真源表）
# A1: trend_score = 0.5×tanh(ret20/0.10) + 0.5×tanh((ma20/ma60−1)/0.05) ∈ [-1,1]
# A2: vol_percentile = 近 20 日已实现波动率（日收益 std×√252）在 trailing 250 日滚动波动率中的分位 ∈ [0,1]
# A3: 3×3 规则映射: trend≥0.2 BULL / ≤−0.2 BEAR / 其间 NEUTRAL; vol_pct<1/3 LOW / >2/3 HIGH / 其间 MEDIUM
# A4: confidence = 阈值边际（距最近分类边界的归一化距离）× 样本充足因子 ∈ [0,1]
# O1: MarketStateSnapshot（9 网格状态 + 趋势/波动分解 + 置信度，供下游风控节流消费）
# [/ALGO_FLOW]
"""
市场状态传感器（10 号 regime spec §2.1 结构探测器规则版，MOD-SIG-036）。

规则驱动的 3×3 市场状态分类：趋势方向（Bull/Neutral/Bear）× 波动率水平
（Low/Medium/High）→ 9 网格状态单值输出 + 分解得分 + 置信度。

定位红线（宪章 §3 约束三 + 10 号 spec §1.2）：本模块是市场级风险节流的状态
感知层——只回答"现在市场处于什么状态、把握多大"，输出状态/得分/置信度供下
游风控节流消费，**不输出任何择时买卖信号**。与 regime/ HMM 4 态检测器
（MOD-REGIME-001，模型驱动）的关系：本模块是规则驱动的轻量传感器（可解释、
无拟合、无过拟合风险），两者输入同源（指数价量）可交叉验证。

阈值（trend ±0.2、vol 1/3-2/3 分位、tanh 缩放 0.10/0.05）为初拟，待实盘标定。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: closes 参数
#   fields: 参数 closes，类型注解 Sequence[float]
#   code: market_state_sensor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: short_window 参数
#   fields: 参数 short_window，类型注解 int
#   code: market_state_sensor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: long_window 参数
#   fields: 参数 long_window，类型注解 int
#   code: market_state_sensor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: returns 参数
#   fields: 参数 returns，类型注解 Sequence[float]
#   code: market_state_sensor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① compute_trend_score
#   name_en: compute_trend_score
#   intro: 趋势得分 ∈ [-1, 1]：20 日收益与 MA20/MA60 偏离的等权 tanh 合成。
#   desc: 趋势得分 ∈ [-1, 1]：20 日收益与 MA20/MA60 偏离的等权 tanh 合成。 Args: closes: 收盘序列（升序），长度 ≥ long_window +…；源码 L253-L278
#   inputs: closes short_window long_window
#   outputs: float
# - id: A2
#   name_zh: ② compute_vol_percentile
#   name_en: compute_vol_percentile
#   intro: 已实现波动率分位 ∈ (0, 1]：近 vol_window 日波动率在 trailing 窗口中的排名。
#   desc: 已实现波动率分位 ∈ (0, 1]：近 vol_window 日波动率在 trailing 窗口中的排名。 波动率 = 日收益总体标准差 × √252（年化）。分位 = trai…；源码 L281-L305
#   inputs: returns vol_window lookback
#   outputs: float
# - id: A3
#   name_zh: ③ classify_trend
#   name_en: classify_trend
#   intro: 趋势得分 → 3 分类（≥bull_min BULL / ≤bear_max BEAR / 其间 NEUTRAL）。
#   desc: 趋势得分 → 3 分类（≥bull_min BULL / ≤bear_max BEAR / 其间 NEUTRAL）。；源码 L308-L318
#   inputs: trend_score bull_min bear_max
#   outputs: TrendDirection
# - id: A4
#   name_zh: ④ classify_volatility
#   name_en: classify_volatility
#   intro: 波动率分位 → 3 分类（<low_max LOW / >high_min HIGH / 边界等值落 MEDIUM）。
#   desc: 波动率分位 → 3 分类（<low_max LOW / >high_min HIGH / 边界等值落 MEDIUM）。；源码 L321-L331
#   inputs: vol_percentile low_max high_min
#   outputs: VolatilityLevel
# - id: A5
#   name_zh: ⑤ classify_market_state
#   name_en: classify_market_state
#   intro: 趋势 × 波动率 → 9 网格状态单值输出。
#   desc: 趋势 × 波动率 → 9 网格状态单值输出。；源码 L334-L339
#   inputs: trend vol
#   outputs: MarketGridState
# - id: A6
#   name_zh: ⑥ sense_market_state
#   name_en: sense_market_state
#   intro: 核心纯函数：收盘序列 → 市场状态快照。
#   desc: 核心纯函数：收盘序列 → 市场状态快照。 confidence 合成（初拟）：趋势/波动各自距最近分类边界的归一化边际均值 × 样本充足因子（min(1, n/(2×min_hi…；源码 L342-L384
#   inputs: closes config
#   outputs: MarketStateSnapshot
# - id: A7
#   name_zh: ⑦ MarketStateSensor
#   name_en: MarketStateSensor
#   intro: 市场状态传感器（DB 加载层薄封装，计算全部委托纯函数）。
#   desc: 市场状态传感器（DB 加载层薄封装，计算全部委托纯函数）。 DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV）， regis…；公共方法（定义序）: load_in…
#   inputs: registry query_fn config
#   outputs: 返回值
#   （注：A7 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 regime_change_detector / next_day_8state_forecast / 下游风控节流层)
# - id: O2
#   name_zh: TrendDirection
#   name_en: TrendDirection
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 regime_change_detector / next_day_8state_forecast / 下游风控节流层)
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
# A6 --> A7
# A7 --> O1
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_logger = logging.getLogger(__name__)

__all__: Final = [
    "MarketGridState",
    "MarketStateConfig",
    "MarketStateDataError",
    "MarketStateSensor",
    "MarketStateSnapshot",
    "TrendDirection",
    "VolatilityLevel",
    "classify_market_state",
    "classify_trend",
    "classify_volatility",
    "compute_trend_score",
    "compute_vol_percentile",
    "sense_market_state",
]

#: 默认市场代理指数（沪深300，与 regime/ 检测器同一代理）
DEFAULT_MARKET_SYMBOL: Final = "000300"

#: 趋势得分 tanh 缩放常数（20 日收益 10% / 均线偏离 5% 为"明确趋势"参考点，初拟）
_TREND_RET_SCALE: Final = 0.10
_TREND_MA_SCALE: Final = 0.05

#: 状态网格映射表（3×3）
_GRID_STATE: Final = {
    ("BULL", "LOW"): "BULL_LOW",
    ("BULL", "MEDIUM"): "BULL_MEDIUM",
    ("BULL", "HIGH"): "BULL_HIGH",
    ("NEUTRAL", "LOW"): "NEUTRAL_LOW",
    ("NEUTRAL", "MEDIUM"): "NEUTRAL_MEDIUM",
    ("NEUTRAL", "HIGH"): "NEUTRAL_HIGH",
    ("BEAR", "LOW"): "BEAR_LOW",
    ("BEAR", "MEDIUM"): "BEAR_MEDIUM",
    ("BEAR", "HIGH"): "BEAR_HIGH",
}

# SQL 模板常量（_SQL_* 前缀约定，与 ch_reader/overnight_boundary_reviser 一致）
_SQL_INDEX_KLINE = (
    "SELECT trade_date, close FROM {table} FINAL "
    "WHERE symbol = '{symbol}' "
    "AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY trade_date"
)


class MarketStateDataError(Exception):
    """市场状态数据加载失败（loader 查询为空/解析失败）。"""


class TrendDirection(str, Enum):
    """趋势方向 3 分类"""

    BULL = "BULL"  # 上涨趋势
    NEUTRAL = "NEUTRAL"  # 无方向
    BEAR = "BEAR"  # 下跌趋势


class VolatilityLevel(str, Enum):
    """波动率水平 3 分类"""

    LOW = "LOW"  # 低波动
    MEDIUM = "MEDIUM"  # 中波动
    HIGH = "HIGH"  # 高波动


class MarketGridState(str, Enum):
    """市场状态 3×3 网格（趋势 × 波动率，10 号 spec §3.1 基础 9 态）"""

    BULL_LOW = "BULL_LOW"  # 温和上涨低波动——最佳趋势跟踪期
    BULL_MEDIUM = "BULL_MEDIUM"  # 上涨趋势中波动——正常趋势期
    BULL_HIGH = "BULL_HIGH"  # 急涨急跌——方向对但波动大
    NEUTRAL_LOW = "NEUTRAL_LOW"  # 无方向低波动——震荡磨底
    NEUTRAL_MEDIUM = "NEUTRAL_MEDIUM"  # 无方向中波动——典型震荡市
    NEUTRAL_HIGH = "NEUTRAL_HIGH"  # 无方向高波动——混沌期
    BEAR_LOW = "BEAR_LOW"  # 温和下跌低波动——阴跌期
    BEAR_MEDIUM = "BEAR_MEDIUM"  # 下跌趋势中波动——正常下跌期
    BEAR_HIGH = "BEAR_HIGH"  # 暴跌高波动——恐慌期


@dataclass(frozen=True)
class MarketStateConfig:
    """市场状态传感器配置（阈值为初拟，待实盘标定）。"""

    short_window: int = 20  # 短期趋势窗口（交易日）
    long_window: int = 60  # 长期趋势窗口（交易日）
    vol_window: int = 20  # 已实现波动率窗口
    vol_lookback: int = 250  # 波动率分位回看窗口
    trend_bull_min: float = 0.2  # 趋势得分 ≥ 此值判 BULL
    trend_bear_max: float = -0.2  # 趋势得分 ≤ 此值判 BEAR
    vol_low_max: float = 1.0 / 3.0  # 波动率分位 < 此值判 LOW
    vol_high_min: float = 2.0 / 3.0  # 波动率分位 > 此值判 HIGH
    min_history: int = 60  # 最少输入交易日数


@dataclass(frozen=True)
class MarketStateSnapshot:
    """市场状态快照（输出契约：状态 + 分解得分 + 置信度，非买卖信号）。"""

    state: MarketGridState  # 9 网格单状态
    trend_direction: TrendDirection
    vol_level: VolatilityLevel
    trend_score: float  # ∈ [-1, 1]
    vol_percentile: float  # ∈ [0, 1]
    confidence: float  # ∈ [0, 1]
    n_days: int  # 输入序列长度


def compute_trend_score(
    closes: Sequence[float],
    short_window: int = 20,
    long_window: int = 60,
) -> float:
    """趋势得分 ∈ [-1, 1]：20 日收益与 MA20/MA60 偏离的等权 tanh 合成。

    Args:
        closes: 收盘序列（升序），长度 ≥ long_window + 1。
        short_window: 短期窗口（ret20 与 MA20）。
        long_window: 长期窗口（MA60）。

    Returns:
        trend_score = 0.5×tanh(ret_short/0.10) + 0.5×tanh((ma_short/ma_long−1)/0.05)。

    Raises:
        ValueError: 输入长度不足 long_window + 1。
    """
    if len(closes) < long_window + 1:
        raise ValueError(f"closes 长度 {len(closes)} 不足 long_window+1={long_window + 1}")
    ret_short = closes[-1] / closes[-1 - short_window] - 1.0
    ma_short = statistics.fmean(closes[-short_window:])
    ma_long = statistics.fmean(closes[-long_window:])
    ma_gap = ma_short / ma_long - 1.0 if ma_long > 0 else 0.0
    score = 0.5 * math.tanh(ret_short / _TREND_RET_SCALE) + 0.5 * math.tanh(ma_gap / _TREND_MA_SCALE)
    return max(-1.0, min(1.0, score))


def compute_vol_percentile(
    returns: Sequence[float],
    vol_window: int = 20,
    lookback: int = 250,
) -> float:
    """已实现波动率分位 ∈ (0, 1]：近 vol_window 日波动率在 trailing 窗口中的排名。

    波动率 = 日收益总体标准差 × √252（年化）。分位 = trailing 窗口内
    ≤ 当前波动率的样本占比（等值并入，常数序列分位为 1.0）。

    Args:
        returns: 日收益序列（升序），长度 ≥ vol_window + 1。
        vol_window: 波动率计算窗口。
        lookback: 分位回看窗口（超出实际样本时取全部）。

    Raises:
        ValueError: 输入长度不足 vol_window + 1。
    """
    if len(returns) < vol_window + 1:
        raise ValueError(f"returns 长度 {len(returns)} 不足 vol_window+1={vol_window + 1}")
    annualize = math.sqrt(252.0)
    vols = [statistics.pstdev(returns[i - vol_window : i]) * annualize for i in range(vol_window, len(returns) + 1)]
    current = vols[-1]
    trailing = vols[-lookback:]
    return sum(1 for v in trailing if v <= current) / len(trailing)


def classify_trend(
    trend_score: float,
    bull_min: float = 0.2,
    bear_max: float = -0.2,
) -> TrendDirection:
    """趋势得分 → 3 分类（≥bull_min BULL / ≤bear_max BEAR / 其间 NEUTRAL）。"""
    if trend_score >= bull_min:
        return TrendDirection.BULL
    if trend_score <= bear_max:
        return TrendDirection.BEAR
    return TrendDirection.NEUTRAL


def classify_volatility(
    vol_percentile: float,
    low_max: float = 1.0 / 3.0,
    high_min: float = 2.0 / 3.0,
) -> VolatilityLevel:
    """波动率分位 → 3 分类（<low_max LOW / >high_min HIGH / 边界等值落 MEDIUM）。"""
    if vol_percentile < low_max:
        return VolatilityLevel.LOW
    if vol_percentile > high_min:
        return VolatilityLevel.HIGH
    return VolatilityLevel.MEDIUM


def classify_market_state(
    trend: TrendDirection,
    vol: VolatilityLevel,
) -> MarketGridState:
    """趋势 × 波动率 → 9 网格状态单值输出。"""
    return MarketGridState(_GRID_STATE[(trend.value, vol.value)])


def sense_market_state(
    closes: Sequence[float],
    config: MarketStateConfig | None = None,
) -> MarketStateSnapshot:
    """核心纯函数：收盘序列 → 市场状态快照。

    confidence 合成（初拟）：趋势/波动各自距最近分类边界的归一化边际均值
    × 样本充足因子（min(1, n/(2×min_history))）。边际越大分类越确定。

    Raises:
        ValueError: 输入长度不足 config.min_history（或波动率窗口 +1）。
    """
    cfg = config or MarketStateConfig()
    n = len(closes)
    if n < cfg.min_history:
        raise ValueError(f"closes 长度 {n} 不足 min_history={cfg.min_history}")

    trend_score = compute_trend_score(closes, cfg.short_window, cfg.long_window)
    returns = [closes[i] / closes[i - 1] - 1.0 for i in range(1, n)]
    vol_pct = compute_vol_percentile(returns, cfg.vol_window, cfg.vol_lookback)

    trend = classify_trend(trend_score, cfg.trend_bull_min, cfg.trend_bear_max)
    vol = classify_volatility(vol_pct, cfg.vol_low_max, cfg.vol_high_min)
    state = classify_market_state(trend, vol)

    trend_margin = min(abs(trend_score - cfg.trend_bull_min), abs(trend_score - cfg.trend_bear_max)) / max(
        cfg.trend_bull_min, 1e-9
    )
    vol_span = cfg.vol_high_min - cfg.vol_low_max
    vol_margin = min(abs(vol_pct - cfg.vol_low_max), abs(vol_pct - cfg.vol_high_min)) / max(vol_span, 1e-9)
    margin_factor = max(0.0, min(1.0, 0.5 * (min(trend_margin, 1.0) + min(vol_margin, 1.0))))
    sample_factor = min(1.0, n / (2.0 * cfg.min_history))
    confidence = margin_factor * sample_factor

    return MarketStateSnapshot(
        state=state,
        trend_direction=trend,
        vol_level=vol,
        trend_score=trend_score,
        vol_percentile=vol_pct,
        confidence=confidence,
        n_days=n,
    )


class MarketStateSensor:
    """市场状态传感器（DB 加载层薄封装，计算全部委托纯函数）。

    DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV），
    registry 默认 get_registry()（表名经 TableRegistry 派生，禁止硬编码）。
    测试注入假 query_fn 即可全链验证，不触真实 ClickHouse。
    """

    def __init__(
        self,
        registry: object = None,
        query_fn: Callable[..., str] | None = None,
        config: MarketStateConfig | None = None,
    ) -> None:
        self._registry = registry
        self._query_fn = query_fn
        self._config = config or MarketStateConfig()

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

    def load_index_closes(
        self,
        symbol: str = DEFAULT_MARKET_SYMBOL,
        start: str = "2010-01-01",
        end: str = "2099-12-31",
    ) -> list[float]:
        """从 market_index_kline 加载指数收盘序列（升序）。

        Raises:
            MarketStateDataError: 查询为空或无可解析行。
        """
        sql = _SQL_INDEX_KLINE.format(table=self._resolve_table(), symbol=symbol, start=start, end=end)
        tsv = self._resolve_query_fn()(sql)
        closes: list[float] = []
        for line in (tsv or "").strip().split("\n"):
            parts = line.rstrip("\r").split("\t")
            if len(parts) >= 2:
                try:
                    closes.append(float(parts[1]))
                except ValueError:
                    _logger.warning("market_state_sensor 跳过不可解析行: %s", line[:80])
        if not closes:
            raise MarketStateDataError(f"market_index_kline 查询为空: symbol={symbol}, [{start}, {end}]")
        return closes

    def sense(
        self,
        symbol: str = DEFAULT_MARKET_SYMBOL,
        start: str = "2010-01-01",
        end: str = "2099-12-31",
    ) -> MarketStateSnapshot:
        """加载指数日 K 并输出市场状态快照（计算委托 sense_market_state）。"""
        closes = self.load_index_closes(symbol, start, end)
        return sense_market_state(closes, self._config)
