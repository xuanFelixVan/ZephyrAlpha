# [BLUEPRINT] MOD-SIG-038 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/90_methodology_open_questions.md §22.3
# [MODULE] zephyr.signal_ashare.cross_market_conduction_sensor
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] (待 下游风控节流层 / 全量或板块重算触发器)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] correlation ∈ [-1,1]; confidence ∈ [0,1]; total_predicted_impact ∈ [-impact_clip, +impact_clip]; 纯函数计算与 DB 加载隔离
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯函数输入样本不足 → 返回 None（降级友好）; loader 查询为空/失败 → CrossMarketConductionDataError
# [TESTS] tests/signal_ashare/test_cross_market_conduction_sensor.py
# [A_module] module_id=MOD-SIG-038 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 外盘指数日收益（us_index: SPX/DJI/IXIC）+ A 股指数日收益（market_index_kline: 000300）
# A1: 日历对齐: 外盘 t 日收益 → A 股其后首个交易日（bisect 取最新先于当日的外盘日期）
# A2: 领先滞后相关: lag ∈ [0..2] 取 |corr| 最大者（lag0=隔夜传导当日生效，lag≥1=延续效应）
# A3: 传导系数 beta = cov(外盘, A股@best_lag)/var(外盘)（简版 Granger 思路的回归斜率）
# A4: 异动分档: |shock|<1% NONE / [1%,2%) MILD / ≥2% SEVERE; 影响预测 = Σ beta×shock（clip ±5%）
# O1: ConductionSnapshot（分市场传导系数+影响预测 + 总影响 + 最重异动档 + 置信度）
# [/ALGO_FLOW]
"""
跨市场传导传感器（90 号 §22.3 BM-SEL-06，MOD-SIG-038）。

美股/港股等外盘指数异动到达时，用领先滞后相关 + 回归斜率（简版 Granger
思路）估计"外盘 → A 股"的传导系数，量化预测对 A 股的影响幅度：美股一异动，
立刻算出对 A 股的传导系数和影响幅度，供下游风控节流与全量/板块重算触发消费。

边界消歧（90 号 §22.3）：36 号 BS-005 跨市场传导是风控前兆监控（防守触发器，
已 production）；本模块是传导幅度量化层（系数 + 幅度预测），两者消费同一外围
行情输入但产出正交。输出是系数/幅度/置信度，**不构成买卖信号**。

口径说明：A 股 T+1 下外盘隔夜冲击首日反映在开仓价中，本模块不做"抢跑"式预
测；lead_lag=0 表示隔夜传导当日生效（对齐后主口径），lag≥1 为延续效应。

参数（相关显著性 0.3、min_samples 60、异动分档 1%/2%、clip ±5%）为初拟，待实
盘标定。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: x 参数
#   fields: 参数 x，类型注解 Sequence[float]
#   code: cross_market_conduction_sensor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: y 参数
#   fields: 参数 y，类型注解 Sequence[float]
#   code: cross_market_conduction_sensor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: ashare 参数
#   fields: 参数 ashare，类型注解 Mapping[str, float]
#   code: cross_market_conduction_sensor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: foreign 参数
#   fields: 参数 foreign，类型注解 Mapping[str, float]
#   code: cross_market_conduction_sensor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① pearson_corr
#   name_en: pearson_corr
#   intro: 皮尔逊相关（零方差/样本不足 → 0.0）。
#   desc: 皮尔逊相关（零方差/样本不足 → 0.0）。；源码 L250-L263
#   inputs: x y
#   outputs: float
# - id: A2
#   name_zh: ② align_foreign_to_ashare
#   name_en: align_foreign_to_ashare
#   intro: 外盘收益对齐到 A 股日历：A 股当日 ← 最新早于当日的外盘日期收益。
#   desc: 外盘收益对齐到 A 股日历：A 股当日 ← 最新早于当日的外盘日期收益。 隔夜传导口径：美股 t 日收盘（北京时间次日凌晨）影响 A 股 t+1 交易日。 无先于此日期的外盘数据…；源码 L266-L289
#   inputs: ashare foreign
#   outputs: tuple[list[float], list[float]]
# - id: A3
#   name_zh: ③ lead_lag_correlation
#   name_en: lead_lag_correlation
#   intro: 领先滞后相关：corr(foreign[i], ashare[i+lag])，lag ≥ 0。
#   desc: 领先滞后相关：corr(foreign[i], ashare[i+lag])，lag ≥ 0。；源码 L292-L304
#   inputs: foreign ashare lag
#   outputs: float
# - id: A4
#   name_zh: ④ estimate_conduction
#   name_en: estimate_conduction
#   intro: 单市场传导估计：lag 扫描取 |corr| 最大，回归斜率为传导系数 beta。
#   desc: 单市场传导估计：lag 扫描取 |corr| 最大，回归斜率为传导系数 beta。 Args: foreign_returns: 已对齐的外盘收益序列。 ashare_retur…；源码 L307-L360
#   inputs: foreign_returns ashare_returns config symbol
#   outputs: MarketConduction | None
# - id: A5
#   name_zh: ⑤ classify_shock
#   name_en: classify_shock
#   intro: 外盘异动分档：|shock| <1% NONE / [1%, 2%) MILD / ≥2% SEVERE（边界取重档）。
#   desc: 外盘异动分档：|shock| <1% NONE / [1%, 2%) MILD / ≥2% SEVERE（边界取重档）。；源码 L363-L374
#   inputs: shock mild_threshold severe_threshold
#   outputs: ShockLevel
# - id: A6
#   name_zh: ⑥ sense_cross_market_conduction
#   name_en: sense_cross_market_conduction
#   intro: 核心纯函数：多市场传导感知 → 总影响预测快照。
#   desc: 核心纯函数：多市场传导感知 → 总影响预测快照。 单市场样本不足时剔除该市场（降级友好）；全部不足 → 空 markets + 零影响。 影响预测 = Σ beta × late…；源码 L377-L416
#   inputs: foreign_series config
#   outputs: ConductionSnapshot
# - id: A7
#   name_zh: ⑦ CrossMarketConductionSensor
#   name_en: CrossMarketConductionSensor
#   intro: 跨市场传导传感器（DB 加载层薄封装，计算全部委托纯函数）。
#   desc: 跨市场传导传感器（DB 加载层薄封装，计算全部委托纯函数）。 DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV）， regi…；公共方法（定义序）: sense；源…
#   inputs: registry query_fn config foreign_codes
#   outputs: 返回值
#   （注：A7 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 下游风控节流层 / 全量或板块重算触发器)
# - id: O2
#   name_zh: tuple[list[float], list[float]]
#   name_en: tuple[list[float], list[float]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 下游风控节流层 / 全量或板块重算触发器)
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

import bisect
import logging
from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ConductionConfig",
    "ConductionSnapshot",
    "CrossMarketConductionDataError",
    "CrossMarketConductionSensor",
    "ForeignMarketSeries",
    "MarketConduction",
    "ShockLevel",
    "align_foreign_to_ashare",
    "classify_shock",
    "estimate_conduction",
    "lead_lag_correlation",
    "pearson_corr",
    "sense_cross_market_conduction",
]

#: 默认市场代理指数（沪深300）
DEFAULT_MARKET_SYMBOL: Final = "000300"

#: 默认外盘指数代码（us_index 表 index_code：标普/道琼/纳指，ETF 替代真实指数）
DEFAULT_FOREIGN_CODES: Final = ("SPX", "DJI", "IXIC")

#: 相关显著性参考值（|corr| 达到此值置信度记满分，初拟）
_CORR_SIGNIFICANT: Final = 0.3

#: 异动严重度排序（取最重档用）
_SHOCK_RANK: Final = {"NONE": 0, "MILD": 1, "SEVERE": 2}

# SQL 模板常量（_SQL_* 前缀约定）
_SQL_US_INDEX = (
    "SELECT trade_date, index_code, close FROM {table} FINAL "
    "WHERE index_code IN ({codes}) "
    "AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY index_code, trade_date"
)
_SQL_INDEX_KLINE = (
    "SELECT trade_date, close FROM {table} FINAL "
    "WHERE symbol = '{symbol}' "
    "AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY trade_date"
)


class CrossMarketConductionDataError(Exception):
    """跨市场传导数据加载失败（loader 查询为空/解析失败）。"""


class ShockLevel(str, Enum):
    """外盘异动分档"""

    NONE = "NONE"  # 无异动（|shock| < 1%）
    MILD = "MILD"  # 轻微异动（1% ≤ |shock| < 2%）
    SEVERE = "SEVERE"  # 剧烈异动（|shock| ≥ 2%）


@dataclass(frozen=True)
class ConductionConfig:
    """跨市场传导配置（参数为初拟，待实盘标定）。"""

    window: int = 250  # 相关/回归估计窗口（对齐后样本）
    max_lag: int = 2  # 领先滞后扫描最大 lag（交易日）
    min_samples: int = 60  # 单市场最少样本数（不足则该市场降级跳过）
    mild_threshold: float = 0.01  # 轻微异动下限
    severe_threshold: float = 0.02  # 剧烈异动下限
    impact_clip: float = 0.05  # 总影响预测绝对值上限


@dataclass(frozen=True)
class ForeignMarketSeries:
    """单个外围市场的输入（returns 与 ashare_returns 已逐日对齐）。"""

    symbol: str  # 外盘指数代码
    returns: tuple[float, ...]  # 对齐后的外盘日收益序列
    ashare_returns: tuple[float, ...]  # 对齐后的 A 股日收益序列（同长度）
    latest_shock: float  # 最新一期外盘收益（最新隔夜冲击）


@dataclass(frozen=True)
class MarketConduction:
    """单市场传导估计（系数 + 当前冲击的影响预测）。"""

    foreign_symbol: str
    lead_lag: int  # 传导生效滞后天数（0=隔夜当日生效）
    correlation: float  # 领先滞后相关 ∈ [-1, 1]
    beta: float  # 传导系数（回归斜率）
    n_samples: int  # 估计样本数
    confidence: float  # ∈ [0, 1]
    latest_shock: float = 0.0  # 最新冲击
    predicted_impact: float = 0.0  # 影响预测 = beta × latest_shock
    shock_level: ShockLevel = ShockLevel.NONE


@dataclass(frozen=True)
class ConductionSnapshot:
    """跨市场传导快照（输出契约：系数/幅度/置信度，非买卖信号）。"""

    markets: tuple[MarketConduction, ...]  # 分市场传导估计（样本不足的市场已剔除）
    total_predicted_impact: float  # 总影响预测 ∈ [-impact_clip, +impact_clip]
    worst_shock_level: ShockLevel  # 各市场中最重异动档
    confidence: float  # 各市场置信度均值 ∈ [0, 1]


def pearson_corr(x: Sequence[float], y: Sequence[float]) -> float:
    """皮尔逊相关（零方差/样本不足 → 0.0）。"""
    n = min(len(x), len(y))
    if n < 2:
        return 0.0
    xs, ys = x[:n], y[:n]
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    vx = sum((v - mx) ** 2 for v in xs)
    vy = sum((v - my) ** 2 for v in ys)
    if vx <= 0 or vy <= 0:
        return 0.0
    return cov / (vx * vy) ** 0.5


def align_foreign_to_ashare(
    ashare: Mapping[str, float],
    foreign: Mapping[str, float],
) -> tuple[list[float], list[float]]:
    """外盘收益对齐到 A 股日历：A 股当日 ← 最新早于当日的外盘日期收益。

    隔夜传导口径：美股 t 日收盘（北京时间次日凌晨）影响 A 股 t+1 交易日。
    无先于此日期的外盘数据时，该 A 股日期剔除（两序列同步缩短）。

    Args:
        ashare: {A股交易日: 收益}。foreign: {外盘交易日: 收益}。日期为 ISO 字符串。

    Returns:
        (对齐外盘收益, 对齐 A 股收益)，长度一致。
    """
    foreign_dates = sorted(foreign)
    out_f: list[float] = []
    out_a: list[float] = []
    for d in sorted(ashare):
        idx = bisect.bisect_left(foreign_dates, d) - 1
        if idx >= 0:
            out_f.append(foreign[foreign_dates[idx]])
            out_a.append(ashare[d])
    return out_f, out_a


def lead_lag_correlation(
    foreign: Sequence[float],
    ashare: Sequence[float],
    lag: int,
) -> float:
    """领先滞后相关：corr(foreign[i], ashare[i+lag])，lag ≥ 0。"""
    n = min(len(foreign), len(ashare)) - lag
    if n < 2:
        return 0.0
    return pearson_corr(
        [foreign[i] for i in range(n)],
        [ashare[i + lag] for i in range(n)],
    )


def estimate_conduction(
    foreign_returns: Sequence[float],
    ashare_returns: Sequence[float],
    config: ConductionConfig | None = None,
    symbol: str = "",
) -> MarketConduction | None:
    """单市场传导估计：lag 扫描取 |corr| 最大，回归斜率为传导系数 beta。

    Args:
        foreign_returns: 已对齐的外盘收益序列。
        ashare_returns: 已对齐的 A 股收益序列（同长度口径）。
        config: 配置。symbol: 外盘指数代码（仅用于输出标注）。

    Returns:
        MarketConduction；样本不足 min_samples 或外盘零波动 → None（降级友好）。
    """
    cfg = config or ConductionConfig()
    n = min(len(foreign_returns), len(ashare_returns))
    if n < cfg.min_samples:
        return None
    foreign = list(foreign_returns)[-cfg.window :]
    ashare = list(ashare_returns)[-cfg.window :]

    best_lag = 0
    best_corr = 0.0
    for lag in range(cfg.max_lag + 1):
        c = lead_lag_correlation(foreign, ashare, lag)
        if abs(c) > abs(best_corr):
            best_lag = lag
            best_corr = c

    pairs_n = min(len(foreign), len(ashare)) - best_lag
    f_seg = foreign[:pairs_n]
    a_seg = ashare[best_lag : best_lag + pairs_n]
    mf = sum(f_seg) / pairs_n
    var_f = sum((v - mf) ** 2 for v in f_seg)
    if var_f <= 0:
        return None
    ma = sum(a_seg) / pairs_n
    cov = sum((f_seg[i] - mf) * (a_seg[i] - ma) for i in range(pairs_n))
    beta = cov / var_f

    sample_factor = min(1.0, n / cfg.window)
    corr_factor = min(1.0, abs(best_corr) / _CORR_SIGNIFICANT)
    confidence = sample_factor * corr_factor

    return MarketConduction(
        foreign_symbol=symbol,
        lead_lag=best_lag,
        correlation=best_corr,
        beta=beta,
        n_samples=n,
        confidence=max(0.0, min(1.0, confidence)),
    )


def classify_shock(
    shock: float,
    mild_threshold: float = 0.01,
    severe_threshold: float = 0.02,
) -> ShockLevel:
    """外盘异动分档：|shock| <1% NONE / [1%, 2%) MILD / ≥2% SEVERE（边界取重档）。"""
    magnitude = abs(shock)
    if magnitude >= severe_threshold:
        return ShockLevel.SEVERE
    if magnitude >= mild_threshold:
        return ShockLevel.MILD
    return ShockLevel.NONE


def sense_cross_market_conduction(
    foreign_series: Sequence[ForeignMarketSeries],
    config: ConductionConfig | None = None,
) -> ConductionSnapshot:
    """核心纯函数：多市场传导感知 → 总影响预测快照。

    单市场样本不足时剔除该市场（降级友好）；全部不足 → 空 markets + 零影响。
    影响预测 = Σ beta × latest_shock，按 impact_clip 截断。
    """
    cfg = config or ConductionConfig()
    markets: list[MarketConduction] = []
    for fs in foreign_series:
        est = estimate_conduction(fs.returns, fs.ashare_returns, cfg, fs.symbol)
        if est is None:
            _logger.warning("cross_market_conduction 样本不足，剔除市场: %s", fs.symbol)
            continue
        impact = est.beta * fs.latest_shock
        markets.append(
            replace(
                est,
                latest_shock=fs.latest_shock,
                predicted_impact=impact,
                shock_level=classify_shock(fs.latest_shock, cfg.mild_threshold, cfg.severe_threshold),
            )
        )

    total = sum(m.predicted_impact for m in markets)
    total = max(-cfg.impact_clip, min(cfg.impact_clip, total))
    worst = ShockLevel.NONE
    for m in markets:
        if _SHOCK_RANK[m.shock_level.value] > _SHOCK_RANK[worst.value]:
            worst = m.shock_level
    confidence = sum(m.confidence for m in markets) / len(markets) if markets else 0.0

    return ConductionSnapshot(
        markets=tuple(markets),
        total_predicted_impact=total,
        worst_shock_level=worst,
        confidence=max(0.0, min(1.0, confidence)),
    )


class CrossMarketConductionSensor:
    """跨市场传导传感器（DB 加载层薄封装，计算全部委托纯函数）。

    DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV），
    registry 默认 get_registry()（表名经 TableRegistry 派生，禁止硬编码）。
    真源表：market_us_index（外盘指数日 K）+ market_index_kline（A 股指数日 K）。
    """

    def __init__(
        self,
        registry: object = None,
        query_fn: Callable[..., str] | None = None,
        config: ConductionConfig | None = None,
        foreign_codes: Sequence[str] = DEFAULT_FOREIGN_CODES,
    ) -> None:
        self._registry = registry
        self._query_fn = query_fn
        self._config = config or ConductionConfig()
        self._foreign_codes = tuple(foreign_codes)

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

    @staticmethod
    def _closes_to_returns(date_close: list[tuple[str, float]]) -> dict[str, float]:
        """(日期, 收盘) 升序序列 → {日期: 日收益}（首日无前收跳过）。"""
        returns: dict[str, float] = {}
        for i in range(1, len(date_close)):
            prev = date_close[i - 1][1]
            if prev > 0:
                returns[date_close[i][0]] = date_close[i][1] / prev - 1.0
        return returns

    def _load_ashare_returns(self, symbol: str, start: str, end: str) -> dict[str, float]:
        sql = _SQL_INDEX_KLINE.format(
            table=self._resolve_table("market_index_kline"), symbol=symbol, start=start, end=end
        )
        tsv = self._resolve_query_fn()(sql)
        rows: list[tuple[str, float]] = []
        for line in (tsv or "").strip().split("\n"):
            parts = line.rstrip("\r").split("\t")
            if len(parts) >= 2:
                try:
                    rows.append((parts[0], float(parts[1])))
                except ValueError:
                    _logger.warning("cross_market_conduction 跳过不可解析行: %s", line[:80])
        if not rows:
            raise CrossMarketConductionDataError(f"market_index_kline 查询为空: symbol={symbol}, [{start}, {end}]")
        return self._closes_to_returns(rows)

    def _load_foreign_returns(self, start: str, end: str) -> dict[str, dict[str, float]]:
        sql = _SQL_US_INDEX.format(
            table=self._resolve_table("market_us_index"),
            codes=", ".join(f"'{c}'" for c in self._foreign_codes),
            start=start,
            end=end,
        )
        tsv = self._resolve_query_fn()(sql)
        by_code: dict[str, list[tuple[str, float]]] = {}
        for line in (tsv or "").strip().split("\n"):
            parts = line.rstrip("\r").split("\t")
            if len(parts) >= 3:
                try:
                    by_code.setdefault(parts[1], []).append((parts[0], float(parts[2])))
                except ValueError:
                    _logger.warning("cross_market_conduction 跳过不可解析行: %s", line[:80])
        if not by_code:
            raise CrossMarketConductionDataError(
                f"market_us_index 查询为空: codes={self._foreign_codes}, [{start}, {end}]"
            )
        return {code: self._closes_to_returns(rows) for code, rows in by_code.items()}

    def sense(
        self,
        symbol: str = DEFAULT_MARKET_SYMBOL,
        start: str = "2010-01-01",
        end: str = "2099-12-31",
    ) -> ConductionSnapshot:
        """加载外盘 + A 股指数日 K，输出跨市场传导快照（计算委托纯函数链）。"""
        ashare = self._load_ashare_returns(symbol, start, end)
        foreign = self._load_foreign_returns(start, end)
        series: list[ForeignMarketSeries] = []
        for code, f_map in sorted(foreign.items()):
            f_aligned, a_aligned = align_foreign_to_ashare(ashare, f_map)
            if not f_aligned:
                _logger.warning("cross_market_conduction 对齐后为空，剔除市场: %s", code)
                continue
            latest_date = max(f_map)
            series.append(
                ForeignMarketSeries(
                    symbol=code,
                    returns=tuple(f_aligned),
                    ashare_returns=tuple(a_aligned),
                    latest_shock=f_map[latest_date],
                )
            )
        return sense_cross_market_conduction(series, self._config)
