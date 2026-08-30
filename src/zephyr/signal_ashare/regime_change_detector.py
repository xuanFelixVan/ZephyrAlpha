# [BLUEPRINT] MOD-SIG-039 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/10_regime_detector_spec.md §2.1
# [MODULE] zephyr.signal_ashare.regime_change_detector
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] (待 BM-BUY-02 买卖流体制切换预警 / 下游风控节流层)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] switch_probability ∈ [0,1]; confidence ∈ [0,1]; cusum_level ∈ [0,1]; TRIGGERED 时 candidate 非 None; 纯函数计算与 DB 加载隔离
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 纯函数输入长度不足 → ValueError; loader 查询为空/失败 → RegimeChangeDataError
# [TESTS] tests/signal_ashare/test_regime_change_detector.py
# [A_module] module_id=MOD-SIG-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 指数日 K 收盘序列 closes（默认 000300，loader 走 market_index_kline 真源表）
# A1: 牛熊规则判定: 收盘价 < MA60 或自 250 日峰值回撤 ≥20% → BEAR，否则 BULL
# A2: 双侧 CUSUM 变点统计: 去均值收益累积偏差（allowance=0.5σ），按 σ√n 归一
# A3: 切换状态机: 尾部连续同态天数 k ≤ confirm_days → TRIGGERED(候选待确认);
#     k > confirm_days → CONFIRMED(体制更新); 无翻转但 CUSUM 超 watch_band → WATCH 预警
# A4: 切换概率: STABLE 0.05+0.20×cusum / WATCH 0.15+0.25×cusum /
#     TRIGGERED 0.35+0.45×k/confirm_days / CONFIRMED 0.90（对应 spec §4 触发→确认概率爬升）
# O1: RegimeChangeSnapshot（当前体制 + 切换相位 + 切换概率 + 置信度，供下游风控节流消费）
# [/ALGO_FLOW]
"""
regime 变更检测器（10 号 regime spec §2.1 BM-BUY-02-A-1-d，MOD-SIG-039）。

牛/熊 2 态体制 + 变点预警的规则实现：盯着市场脾气会不会变——趋势转震荡、
牛转熊的切换点提前预警。spec 原文为"牛/熊 2 态（HMM+变点）"，本模块按施工
纪律取规则判定优先：牛熊分界用"MA60 + 峰值回撤 20%"经典规则（可解释、无拟
合），变点用双侧 CUSUM（去均值累积偏差，allowance=0.5σ 过滤噪声漂移），切
换确认用"触发→确认→失败"状态机（对应 spec §4 转换五要素的概率爬升语义）。

定位红线：输出是体制状态 + 切换相位 + 切换概率 + 置信度，供下游风控节流
（Shrinkage/budget）消费——**不输出择时买卖信号**，与情绪周期（sleeve 内
alpha 择时）正交。

参数（MA60、回撤 20%、confirm 3 天、CUSUM 阈值 2.0、watch_band 0.75）为初拟，
待实盘标定。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: closes 参数
#   fields: 参数 closes，类型注解 Sequence[float]
#   code: regime_change_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: ma_window 参数
#   fields: 参数 ma_window，类型注解 int
#   code: regime_change_detector.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: drawdown_threshold 参数
#   fields: 参数 drawdown_threshold，类型注解 float
#   code: regime_change_detector.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: peak_window 参数
#   fields: 参数 peak_window，类型注解 int
#   code: regime_change_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① classify_regime
#   name_en: classify_regime
#   intro: 牛熊规则判定：收盘价 < MA 或自峰值回撤 ≥ 阈值 → BEAR，否则 BULL。
#   desc: 牛熊规则判定：收盘价 < MA 或自峰值回撤 ≥ 阈值 → BEAR，否则 BULL。 Args: closes: 收盘序列（升序），长度 ≥ ma_window。 ma_win…；源码 L215-L239
#   inputs: closes ma_window drawdown_threshold peak_window
#   outputs: MarketRegime
# - id: A2
#   name_zh: ② build_regime_series
#   name_en: build_regime_series
#   intro: 逐日重建最近 days 天的牛熊体制序列（升序，供切换状态机消费）。
#   desc: 逐日重建最近 days 天的牛熊体制序列（升序，供切换状态机消费）。；源码 L242-L255
#   inputs: closes days ma_window drawdown_threshold peak_window
#   outputs: list[MarketRegime]
# - id: A3
#   name_zh: ③ cusum_level
#   name_en: cusum_level
#   intro: 双侧 CUSUM 变点统计量（σ√n 归一，allowance=0.5σ 过滤噪声漂移）。
#   desc: 双侧 CUSUM 变点统计量（σ√n 归一，allowance=0.5σ 过滤噪声漂移）。 检测窗口内收益均值的漂移：去均值累积偏差的最大值按 σ√n 归一。 恒定收益（无漂移）…；源码 L258-L283
#   inputs: returns
#   outputs: float
# - id: A4
#   name_zh: ④ detect_regime_change
#   name_en: detect_regime_change
#   intro: 核心纯函数：收盘序列 → regime 变更快照（切换状态机 + CUSUM 预警）。
#   desc: 核心纯函数：收盘序列 → regime 变更快照（切换状态机 + CUSUM 预警）。 状态机：尾部连续同态天数 k；前一不同态为已确认体制。 - 无翻转（整窗同态）→ STAB…；源码 L286-L355
#   inputs: closes config
#   outputs: RegimeChangeSnapshot
# - id: A5
#   name_zh: ⑤ RegimeChangeDetector
#   name_en: RegimeChangeDetector
#   intro: regime 变更检测器（DB 加载层薄封装，计算全部委托纯函数）。
#   desc: regime 变更检测器（DB 加载层薄封装，计算全部委托纯函数）。 DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV），…；公共方法（定义序）: load_ind…
#   inputs: registry query_fn config
#   outputs: 返回值
#   （注：A5 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: MarketRegime
#   name_en: MarketRegime
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 BM-BUY-02 买卖流体制切换预警 / 下游风控节流层)
# - id: O2
#   name_zh: list[MarketRegime]
#   name_en: list[MarketRegime]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 BM-BUY-02 买卖流体制切换预警 / 下游风控节流层)
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
# A5 --> O1
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
    "ChangePhase",
    "MarketRegime",
    "RegimeChangeConfig",
    "RegimeChangeDataError",
    "RegimeChangeDetector",
    "RegimeChangeSnapshot",
    "build_regime_series",
    "classify_regime",
    "cusum_level",
    "detect_regime_change",
]

#: 默认市场代理指数（沪深300）
DEFAULT_MARKET_SYMBOL: Final = "000300"

#: 切换概率标定常数（初拟，对应 spec §4 触发 45%→确认 70%+ 的概率爬升语义）
_PROB_STABLE_BASE: Final = 0.05
_PROB_STABLE_CUSUM: Final = 0.20
_PROB_WATCH_BASE: Final = 0.15
_PROB_WATCH_CUSUM: Final = 0.25
_PROB_TRIGGERED_BASE: Final = 0.35
_PROB_TRIGGERED_PER_DAY: Final = 0.45
_PROB_CONFIRMED: Final = 0.90

# SQL 模板常量（_SQL_* 前缀约定）
_SQL_INDEX_KLINE = (
    "SELECT trade_date, close FROM {table} FINAL "
    "WHERE symbol = '{symbol}' "
    "AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "ORDER BY trade_date"
)


class RegimeChangeDataError(Exception):
    """regime 变更检测数据加载失败（loader 查询为空/解析失败）。"""


class MarketRegime(str, Enum):
    """牛/熊 2 态体制（BM-BUY-02-A-1-d）"""

    BULL = "BULL"  # 牛市体制：价格位于 MA60 上方且峰值回撤 <20%
    BEAR = "BEAR"  # 熊市体制：价格跌破 MA60 或峰值回撤 ≥20%


class ChangePhase(str, Enum):
    """体制切换相位（触发→确认状态机）"""

    STABLE = "STABLE"  # 体制稳定，无切换迹象
    WATCH = "WATCH"  # 预警：未翻转但 CUSUM 压力逼近阈值
    TRIGGERED = "TRIGGERED"  # 触发：新体制候选出现，待持续确认
    CONFIRMED = "CONFIRMED"  # 确认：新体制持续超过确认窗，体制更新


@dataclass(frozen=True)
class RegimeChangeConfig:
    """regime 变更检测配置（参数为初拟，待实盘标定）。"""

    ma_window: int = 60  # 牛熊分界均线窗口（交易日）
    peak_window: int = 250  # 峰值回看窗口
    drawdown_threshold: float = 0.20  # 牛熊分界回撤（经典 20% 线）
    confirm_days: int = 3  # 切换确认所需持续天数
    cusum_threshold: float = 2.0  # CUSUM 归一统计量报警阈值
    watch_band: float = 0.75  # CUSUM 压力占比 ≥ 此值时 STABLE→WATCH
    min_history: int = 60  # 状态机回看天数（同时是最少输入要求的一部分）


@dataclass(frozen=True)
class RegimeChangeSnapshot:
    """regime 变更快照（输出契约：体制 + 相位 + 概率 + 置信度，非买卖信号）。"""

    regime: MarketRegime  # 当前已确认体制
    phase: ChangePhase  # 切换相位
    candidate: MarketRegime | None  # 待确认的新体制候选（TRIGGERED 时非 None）
    switch_probability: float  # 切换概率 ∈ [0, 1]
    days_in_candidate: int  # 候选态已连续天数（非 TRIGGERED 为 0）
    cusum_level: float  # CUSUM 压力占比 min(1, level/threshold) ∈ [0, 1]
    confidence: float  # ∈ [0, 1]
    n_days: int  # 输入序列长度


def classify_regime(
    closes: Sequence[float],
    ma_window: int = 60,
    drawdown_threshold: float = 0.20,
    peak_window: int = 250,
) -> MarketRegime:
    """牛熊规则判定：收盘价 < MA 或自峰值回撤 ≥ 阈值 → BEAR，否则 BULL。

    Args:
        closes: 收盘序列（升序），长度 ≥ ma_window。
        ma_window: 牛熊分界均线窗口。
        drawdown_threshold: 峰值回撤阈值（经典 20% 牛熊线）。
        peak_window: 峰值回看窗口（超出序列长度时取全部）。

    Raises:
        ValueError: 输入长度不足 ma_window。
    """
    if len(closes) < ma_window:
        raise ValueError(f"closes 长度 {len(closes)} 不足 ma_window={ma_window}")
    ma = statistics.fmean(closes[-ma_window:])
    peak = max(closes[-peak_window:])
    drawdown = 1.0 - closes[-1] / peak if peak > 0 else 0.0
    if closes[-1] < ma or drawdown >= drawdown_threshold:
        return MarketRegime.BEAR
    return MarketRegime.BULL


def build_regime_series(
    closes: Sequence[float],
    days: int = 60,
    ma_window: int = 60,
    drawdown_threshold: float = 0.20,
    peak_window: int = 250,
) -> list[MarketRegime]:
    """逐日重建最近 days 天的牛熊体制序列（升序，供切换状态机消费）。"""
    n = len(closes)
    if n < ma_window + days:
        raise ValueError(f"closes 长度 {n} 不足 ma_window+days={ma_window + days}")
    return [
        classify_regime(closes[: n - days + j + 1], ma_window, drawdown_threshold, peak_window) for j in range(days)
    ]


def cusum_level(returns: Sequence[float]) -> float:
    """双侧 CUSUM 变点统计量（σ√n 归一，allowance=0.5σ 过滤噪声漂移）。

    检测窗口内收益均值的漂移：去均值累积偏差的最大值按 σ√n 归一。
    恒定收益（无漂移）→ 0；窗口内发生持续方向漂移 → 显著 >1。

    Args:
        returns: 日收益序列（升序）。空序列或零波动 → 0.0。
    """
    n = len(returns)
    if n == 0:
        return 0.0
    mean = statistics.fmean(returns)
    sigma = statistics.pstdev(returns)
    if sigma <= 0:
        return 0.0
    allowance = 0.5 * sigma
    s_pos = 0.0
    s_neg = 0.0
    best = 0.0
    for r in returns:
        dev = r - mean
        s_pos = max(0.0, s_pos + dev - allowance)
        s_neg = min(0.0, s_neg + dev + allowance)
        best = max(best, s_pos, -s_neg)
    return best / (sigma * math.sqrt(n))


def detect_regime_change(
    closes: Sequence[float],
    config: RegimeChangeConfig | None = None,
) -> RegimeChangeSnapshot:
    """核心纯函数：收盘序列 → regime 变更快照（切换状态机 + CUSUM 预警）。

    状态机：尾部连续同态天数 k；前一不同态为已确认体制。
      - 无翻转（整窗同态）→ STABLE；CUSUM 压力 ≥ watch_band 时升级 WATCH。
      - k ≤ confirm_days → TRIGGERED（体制仍为旧态，candidate=新态候选）。
      - k > confirm_days → CONFIRMED（体制更新为新态）。

    Raises:
        ValueError: 输入长度不足 ma_window + min_history。
    """
    cfg = config or RegimeChangeConfig()
    n = len(closes)
    if n < cfg.ma_window + cfg.min_history:
        raise ValueError(f"closes 长度 {n} 不足 ma_window+min_history={cfg.ma_window + cfg.min_history}")

    series = build_regime_series(closes, cfg.min_history, cfg.ma_window, cfg.drawdown_threshold, cfg.peak_window)
    raw_today = series[-1]
    k = 1
    while k < len(series) and series[-1 - k] == raw_today:
        k += 1
    prev = series[-1 - k] if k < len(series) else raw_today

    returns = [closes[i] / closes[i - 1] - 1.0 for i in range(1, n)]
    level = cusum_level(returns[-cfg.min_history :])
    cusum_ratio = min(1.0, level / cfg.cusum_threshold) if cfg.cusum_threshold > 0 else 0.0

    if prev == raw_today:
        # 整窗同态：无翻转
        regime = raw_today
        candidate = None
        days = 0
        if cusum_ratio >= cfg.watch_band:
            phase = ChangePhase.WATCH
            probability = _PROB_WATCH_BASE + _PROB_WATCH_CUSUM * cusum_ratio
        else:
            phase = ChangePhase.STABLE
            probability = _PROB_STABLE_BASE + _PROB_STABLE_CUSUM * cusum_ratio
    elif k > cfg.confirm_days:
        regime = raw_today
        candidate = None
        days = 0
        phase = ChangePhase.CONFIRMED
        probability = _PROB_CONFIRMED
    else:
        regime = prev
        candidate = raw_today
        days = k
        phase = ChangePhase.TRIGGERED
        probability = _PROB_TRIGGERED_BASE + _PROB_TRIGGERED_PER_DAY * k / cfg.confirm_days

    # 置信度：样本充足因子 × 边界证据因子（现价距 MA 边界的归一化距离，5% 为满分）
    ma = statistics.fmean(closes[-cfg.ma_window :])
    evidence = min(1.0, abs(closes[-1] / ma - 1.0) / 0.05) if ma > 0 else 0.0
    sample_factor = min(1.0, n / (2.0 * (cfg.ma_window + cfg.min_history)))
    confidence = sample_factor * (0.4 + 0.6 * evidence)

    return RegimeChangeSnapshot(
        regime=regime,
        phase=phase,
        candidate=candidate,
        switch_probability=max(0.0, min(1.0, probability)),
        days_in_candidate=days,
        cusum_level=cusum_ratio,
        confidence=max(0.0, min(1.0, confidence)),
        n_days=n,
    )


class RegimeChangeDetector:
    """regime 变更检测器（DB 加载层薄封装，计算全部委托纯函数）。

    DB 依赖注入：query_fn 默认走项目既有 data 层 ch_reader.query（TSV），
    registry 默认 get_registry()（表名经 TableRegistry 派生，禁止硬编码）。
    """

    def __init__(
        self,
        registry: object = None,
        query_fn: Callable[..., str] | None = None,
        config: RegimeChangeConfig | None = None,
    ) -> None:
        self._registry = registry
        self._query_fn = query_fn
        self._config = config or RegimeChangeConfig()

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
            RegimeChangeDataError: 查询为空或无可解析行。
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
                    _logger.warning("regime_change_detector 跳过不可解析行: %s", line[:80])
        if not closes:
            raise RegimeChangeDataError(f"market_index_kline 查询为空: symbol={symbol}, [{start}, {end}]")
        return closes

    def detect(
        self,
        symbol: str = DEFAULT_MARKET_SYMBOL,
        start: str = "2010-01-01",
        end: str = "2099-12-31",
    ) -> RegimeChangeSnapshot:
        """加载指数日 K 并输出 regime 变更快照（计算委托 detect_regime_change）。"""
        closes = self.load_index_closes(symbol, start, end)
        return detect_regime_change(closes, self._config)
