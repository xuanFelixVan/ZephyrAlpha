# [BLUEPRINT] MOD-SIG-041 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/90_methodology_open_questions.md §22.4
# [MODULE] zephyr.signal_ashare.market_lifecycle_phase
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] (待 下游风控节流层：冬季禁抄底 / 秋季强制离场约束消费)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] confidence ∈ [0,1]; nh 比率 ∈ [0,1]; 4 季节单值输出; 纯函数计算与 DB 加载隔离
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯函数输入长度不足 → ValueError; loader 查询为空/失败 → MarketLifecycleDataError
# [TESTS] tests/signal_ashare/test_market_lifecycle_phase.py
# [A_module] module_id=MOD-SIG-041 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 板块日 K（kline_sector）→ 新高占比序列 nh（当日收盘创 trailing 250 日新高的板块占比）
# I2: 可选指数收盘序列 closes（000300，指数趋势一致性校验，loader 走 market_index_kline）
# A1: 水位: 慢线 MA20(nh) ≥ 0.10 → 高位; 趋势: 快线 MA5(nh) > 慢线 → 上行（严格大于，不升即滞涨）
# A2: 2×2 季节映射: 低+升 SPRING / 高+升 SUMMER / 高+降 AUTUMN / 低+降 WINTER
# A3: 季节约束: WINTER → forbid_bottom_fishing（冬季禁抄底）; AUTUMN → force_exit（秋季强制离场）
# A4: confidence = 样本因子 × (0.4+0.6×边际) ± 指数一致性调整（±0.1，clip [0,1]）
# O1: LifecyclePhaseSnapshot（季节 + 约束 + 持续天数 + 置信度，供下游风控节流消费）
# [/ALGO_FLOW]
"""市场生命周期相位（90 号 §22.4 BM-SEL-10，MOD-SIG-041）。

盘后判定行情生命周期春夏秋冬 4 阶段：输入=板块新高占比趋势（周月频低频
overlay），输出=季节标签 + 季节约束（冬季禁抄底 / 秋季强制离场），供下游风
控节流消费。

2×2 规则分类（新高占比水位 × 趋势）：
  - SPRING 春：低位回升（慢线 <10% 且快线上穿）——筑底孕育
  - SUMMER 夏：高位上行（慢线 ≥10% 且快线在慢线上方）——主升扩张
  - AUTUMN 秋：高位回落/滞涨（慢线 ≥10% 且快线不高于慢线）——高位派发
  - WINTER 冬：低位下行（慢线 <10% 且快线不高于慢线）——低迷阴跌

三者边界消歧（90 号 §22.4 真源）：情绪周期（28 号，sleeve 内 alpha 择时，日频
游资数据）/ regime（10 号，市场级风险节流，日频价量 4 态 HMM）/ 本模块（生命
周期，周月频新高占比，季节级禁为约束）——输入源、时间尺度、消费方式均不同，
不是同一物的三种说法。输出是状态/约束/置信度，**非择时买卖信号**。

阈值（高低水位 0.10、快慢线 5/20、指数 MA60）为初拟，待实盘标定。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping, Sequence

_logger = logging.getLogger(__name__)

__all__: Final = [
    "LifecyclePhaseConfig",
    "LifecyclePhaseSnapshot",
    "LifecycleSeason",
    "MarketLifecycleDataError",
    "MarketLifecyclePhaseSensor",
    "SeasonConstraint",
    "classify_season",
    "compute_nh_ratio_series",
    "detect_lifecycle_phase",
    "moving_average",
    "season_constraint",
]

#: 默认市场代理指数（沪深300）
DEFAULT_MARKET_SYMBOL: Final = "000300"

#: 指数一致性调整的置信度加减幅度（初拟）
_INDEX_AGREE_BONUS: Final = 0.1

# SQL 模板常量（_SQL_* 前缀约定）
_SQL_SECTOR_KLINE = (
    "SELECT code, trade_date, close FROM {table} FINAL "
    "WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY code, trade_date"
)
_SQL_INDEX_KLINE = (
    "SELECT trade_date, close FROM {table} FINAL "
    "WHERE symbol = '{symbol}' "
    "AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY trade_date"
)


class MarketLifecycleDataError(Exception):
    """市场生命周期数据加载失败（loader 查询为空/解析失败）。"""


class LifecycleSeason(str, Enum):
    """行情生命周期 4 季节（BM-SEL-10）"""

    SPRING = "SPRING"  # 春：低位复苏（新高占比低位回升）
    SUMMER = "SUMMER"  # 夏：主升扩张（新高占比高位上行）
    AUTUMN = "AUTUMN"  # 秋：高位派发（新高占比高位回落/滞涨）
    WINTER = "WINTER"  # 冬：低迷阴跌（新高占比低位下行）


@dataclass(frozen=True)
class SeasonConstraint:
    """季节约束（供下游风控节流消费的禁为标志）。"""

    forbid_bottom_fishing: bool  # 冬季禁抄底
    force_exit: bool  # 秋季强制离场


@dataclass(frozen=True)
class LifecyclePhaseConfig:
    """市场生命周期配置（阈值为初拟，待实盘标定）。"""

    fast_window: int = 5  # 新高占比快线窗口（约 1 周）
    slow_window: int = 20  # 新高占比慢线窗口（约 1 月）
    high_threshold: float = 0.10  # 高低水位分界（10% 板块创新高）
    index_ma_window: int = 60  # 指数趋势校验均线窗口
    min_history: int = 25  # 最少输入交易日数（slow_window + fast_window）


@dataclass(frozen=True)
class LifecyclePhaseSnapshot:
    """市场生命周期快照（输出契约：季节 + 约束 + 置信度，非买卖信号）。"""

    season: LifecycleSeason
    nh_fast: float  # 新高占比快线值
    nh_slow: float  # 新高占比慢线值
    days_in_season: int  # 当前季节已连续天数（可判定窗口内）
    constraint: SeasonConstraint
    confidence: float  # ∈ [0, 1]
    n_days: int  # 输入序列长度


def moving_average(values: Sequence[float], window: int) -> float:
    """末尾 window 项简单移动平均（window 超出长度时取全部）。"""
    tail = values[-window:] if window > 0 else values
    return sum(tail) / len(tail) if tail else 0.0


def classify_season(is_high: bool, is_rising: bool) -> LifecycleSeason:
    """2×2 季节映射：水位（高/低）× 趋势（升/降）→ 春夏秋冬。"""
    if is_high:
        return LifecycleSeason.SUMMER if is_rising else LifecycleSeason.AUTUMN
    return LifecycleSeason.SPRING if is_rising else LifecycleSeason.WINTER


def season_constraint(season: LifecycleSeason) -> SeasonConstraint:
    """季节 → 禁为约束（冬季禁抄底 / 秋季强制离场，90 号 §22.4）。"""
    return SeasonConstraint(
        forbid_bottom_fishing=season == LifecycleSeason.WINTER,
        force_exit=season == LifecycleSeason.AUTUMN,
    )


def compute_nh_ratio_series(
    rows: Iterable[tuple[str, str, float]],
    high_window: int = 250,
) -> list[tuple[str, float]]:
    """板块日 K 行 → 每日新高占比序列（(code, trade_date, close) 升序输入）。

    新高定义：当日收盘 ≥ 该板块 trailing high_window 日（含当日）最高收盘。
    占比 = 当日创新高板块数 / 当日有数据板块数。返回 (日期, 占比) 按日期升序。
    """
    by_code: dict[str, list[tuple[str, float]]] = {}
    for code, date, close in rows:
        by_code.setdefault(code, []).append((date, close))
    # 每板块: 日期 → 是否新高
    nh_flag: dict[str, dict[str, bool]] = {}
    for code, series in by_code.items():
        flags: dict[str, bool] = {}
        for i, (date, close) in enumerate(series):
            start = max(0, i - high_window + 1)
            window_max = max(c for _, c in series[start : i + 1])
            flags[date] = close >= window_max
        nh_flag[code] = flags
    all_dates = sorted({date for series in by_code.values() for date, _ in series})
    out: list[tuple[str, float]] = []
    for date in all_dates:
        present = [code for code in by_code if date in nh_flag[code]]
        if present:
            hits = sum(1 for code in present if nh_flag[code][date])
            out.append((date, hits / len(present)))
    return out


def detect_lifecycle_phase(
    nh_ratios: Sequence[float],
    closes: Sequence[float] | None = None,
    config: LifecyclePhaseConfig | None = None,
) -> LifecyclePhaseSnapshot:
    """核心纯函数：新高占比序列（+可选指数收盘）→ 生命周期相位快照。

    趋势判定：快线 > 慢线（严格大于——高位不升即滞涨判秋，低位躺平判冬）。
    指数一致性（closes 提供时）：多方季（春/夏）应立于指数 MA 上方，空方季
    （秋/冬）应位于下方，一致置信度 +0.1，背离 −0.1。

    Raises:
        ValueError: 输入长度不足 config.min_history。
    """
    cfg = config or LifecyclePhaseConfig()
    n = len(nh_ratios)
    if n < cfg.min_history:
        raise ValueError(f"nh_ratios 长度 {n} 不足 min_history={cfg.min_history}")

    nh_fast = moving_average(nh_ratios, cfg.fast_window)
    nh_slow = moving_average(nh_ratios, cfg.slow_window)
    is_high = nh_slow >= cfg.high_threshold
    is_rising = nh_fast > nh_slow
    season = classify_season(is_high, is_rising)

    # 持续天数：逐日重建可判定窗口内的季节序列，取尾部同季连续段
    days_in_season = 0
    for i in range(cfg.slow_window - 1, n):
        slow_i = moving_average(nh_ratios[: i + 1], cfg.slow_window)
        fast_i = moving_average(nh_ratios[: i + 1], cfg.fast_window)
        season_i = classify_season(slow_i >= cfg.high_threshold, fast_i > slow_i)
        if season_i == season:
            days_in_season += 1
        else:
            days_in_season = 0

    # 置信度：水位/趋势边际 + 样本充足 + 指数一致性调整
    level_margin = min(1.0, abs(nh_slow - cfg.high_threshold) / max(cfg.high_threshold, 1e-9))
    trend_margin = min(1.0, abs(nh_fast - nh_slow) / max(cfg.high_threshold, 1e-9))
    base = 0.5 * level_margin + 0.5 * trend_margin
    sample_factor = min(1.0, n / (2.0 * cfg.min_history))
    confidence = sample_factor * (0.4 + 0.6 * base)
    if closes:
        ma = moving_average(closes, cfg.index_ma_window)
        index_above = closes[-1] >= ma
        bullish_season = season in (LifecycleSeason.SPRING, LifecycleSeason.SUMMER)
        agreement = index_above == bullish_season
        confidence += _INDEX_AGREE_BONUS if agreement else -_INDEX_AGREE_BONUS
    confidence = max(0.0, min(1.0, confidence))

    return LifecyclePhaseSnapshot(
        season=season,
        nh_fast=nh_fast,
        nh_slow=nh_slow,
        days_in_season=days_in_season,
        constraint=season_constraint(season),
        confidence=confidence,
        n_days=n,
    )


class MarketLifecyclePhaseSensor:
    """市场生命周期相位传感器（DB 加载层薄封装，计算全部委托纯函数）。

    DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV），
    registry 默认 get_registry()（表名经 TableRegistry 派生，禁止硬编码）。
    真源表：market_sector_kline（板块日 K → 新高占比）+ market_index_kline
    （指数趋势一致性校验）。
    """

    def __init__(
        self,
        registry: object = None,
        query_fn: Callable[..., str] | None = None,
        config: LifecyclePhaseConfig | None = None,
    ) -> None:
        self._registry = registry
        self._query_fn = query_fn
        self._config = config or LifecyclePhaseConfig()

    def _resolve_query_fn(self) -> Callable[..., str]:
        if self._query_fn is not None:
            return self._query_fn
        from zephyr.data import ch_reader  # 延迟导入，保持纯函数路径零 DB 依赖

        return ch_reader.query

    def _resolve_table(self, category_id: str) -> str:
        registry = self._registry
        if registry is None:
            from zephyr.data.table_registry import get_registry

            registry = get_registry()
        return registry.table(category_id)

    def load_nh_ratio_series(self, start: str, end: str) -> list[float]:
        """从 kline_sector 加载板块日 K 并计算新高占比序列（日期升序）。

        Raises:
            MarketLifecycleDataError: 查询为空或无可解析行。
        """
        sql = _SQL_SECTOR_KLINE.format(
            table=self._resolve_table("market_sector_kline"), start=start, end=end
        )
        tsv = self._resolve_query_fn()(sql)
        rows: list[tuple[str, str, float]] = []
        for line in (tsv or "").strip().split("\n"):
            parts = line.rstrip("\r").split("\t")
            if len(parts) >= 3:
                try:
                    rows.append((parts[0], parts[1], float(parts[2])))
                except ValueError:
                    _logger.warning("market_lifecycle_phase 跳过不可解析行: %s", line[:80])
        if not rows:
            raise MarketLifecycleDataError(
                f"market_sector_kline 查询为空: [{start}, {end}]"
            )
        series = compute_nh_ratio_series(rows)
        if not series:
            raise MarketLifecycleDataError(
                f"market_sector_kline 新高占比序列为空: [{start}, {end}]"
            )
        return [ratio for _, ratio in series]

    def load_index_closes(
        self,
        symbol: str = DEFAULT_MARKET_SYMBOL,
        start: str = "2010-01-01",
        end: str = "2099-12-31",
    ) -> list[float]:
        """从 market_index_kline 加载指数收盘序列（升序，指数一致性校验用）。"""
        sql = _SQL_INDEX_KLINE.format(
            table=self._resolve_table("market_index_kline"), symbol=symbol, start=start, end=end
        )
        tsv = self._resolve_query_fn()(sql)
        closes: list[float] = []
        for line in (tsv or "").strip().split("\n"):
            parts = line.rstrip("\r").split("\t")
            if len(parts) >= 2:
                try:
                    closes.append(float(parts[1]))
                except ValueError:
                    _logger.warning("market_lifecycle_phase 跳过不可解析行: %s", line[:80])
        if not closes:
            raise MarketLifecycleDataError(
                f"market_index_kline 查询为空: symbol={symbol}, [{start}, {end}]"
            )
        return closes

    def sense(
        self,
        symbol: str = DEFAULT_MARKET_SYMBOL,
        start: str = "2010-01-01",
        end: str = "2099-12-31",
    ) -> LifecyclePhaseSnapshot:
        """加载板块/指数日 K 并输出生命周期相位快照（计算委托纯函数链）。"""
        nh_ratios = self.load_nh_ratio_series(start, end)
        closes = self.load_index_closes(symbol, start, end)
        return detect_lifecycle_phase(nh_ratios, closes, self._config)
