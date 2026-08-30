# [BLUEPRINT] MOD-SIG-120 | docs/03_modules/_domain_signal/intraday_size_style/blueprint.md
# [MODULE] zephyr.signal_ashare.intraday_size_style
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（统计核心纯内存；clock 全注入）
# [CONSUMERS] 运行时装配批（统一注入点装配：大小盘收益序列 / 分时价量接入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Size 差序列等长对齐; 风格持续=尾端同号连计数>阈值(默认5)判定; 首/次半小时滚动 Pearson ∈ [-1,1] 零方差降级 0; VWAP 总成交量>0 否则 Fail-Closed; ADX ∈ [0,100]; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/intraday_size_style/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] IntradaySizeStyleError(占位 ZA-SIG-UNREGISTERED-INTRADAY-SIZE-STYLE)——空序列/长度不齐/非有限值/负成交量/零总量/窗口或参数越界时抛
# [TESTS] tests/signal_ashare/test_intraday_size_style.py
# [A_module] module_id=MOD-SIG-120 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
IntradaySizeStyle — 分时微结构与大小盘风格（MOD-SIG-120）。

B10-01385（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-040，A1 模块45）：
Size 因子（大盘-小盘收益差序列）+ 风格持续性统计（同向 >5 天判定）+
前半小时动量预测后半小时（Gao 2018 日内动量：首 30min 收益与次 30min 收益
滚动相关 + 信号输出）+ VWAP 偏差 + 分时 ADX 辅助。

查重分工（蓝图 §0）：market_cap_tier=市值分层静态分类（本件=层间收益差
时序与日内动量，不做分层）；intraday_volume_orderflow=分时量价订单流
（本件取首/次半小时收益对做 Gao 式动量，零交集）；t0_point_analyzer=
T0 买卖点（本件仅风格/动量统计信号，不产买卖点）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: intraday_size_style.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① IntradaySizeStyle
#   name_en: IntradaySizeStyle
#   intro: 分时微结构与大小盘风格统计件（纯内存，时钟注入）。
#   desc: 分时微结构与大小盘风格统计件（纯内存，时钟注入）。 Args: clock: 时钟注入（测试可控）；缺省系统时钟。；公共方法（定义序）: size_factor_series, style_persistence, i…
#   inputs: clock
#   outputs: 返回值
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: IntradaySizeStyle
#   downstream: 运行时装配批（统一注入点装配：大小盘收益序列 / 分时价量接入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "IntradayMomentumSignal",
    "IntradaySizeStyle",
    "IntradaySizeStyleError",
    "SizeStyleAssessment",
    "StylePersistence",
]

#: 风格持续性默认最小同向天数（同向 >5 天判定为持续）
_DEFAULT_PERSISTENCE_DAYS: Final = 5
#: 日内动量默认滚动窗口（交易日数）
_DEFAULT_MOMENTUM_WINDOW: Final = 20
#: 日内动量默认相关阈值
_DEFAULT_CORR_THRESHOLD: Final = 0.5
#: 分时 ADX 默认周期
_DEFAULT_ADX_PERIOD: Final = 14


class IntradaySizeStyleError(Exception):
    """分时微结构与大小盘风格输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-INTRADAY-SIZE-STYLE。
    """


@dataclass(frozen=True)
class StylePersistence:
    """风格持续性（Size 差序列尾端同号连计）。"""

    direction: int  # +1 大盘强 / -1 小盘强 / 0 无方向（尾端为 0）
    streak_days: int  # 尾端同号连续天数
    is_persistent: bool  # streak_days > min_days（默认 5，严格大于）


@dataclass(frozen=True)
class IntradayMomentumSignal:
    """Gao 2018 日内动量：首 30min 收益 → 次 30min 收益滚动相关信号。"""

    correlation: float  # 滚动 Pearson ∈ [-1,1]；窗口未就绪/零方差降级 0.0
    window_ready: bool  # 样本数达到滚动窗口
    signal: int  # +1 看多 / -1 看空 / 0 无信号


@dataclass(frozen=True)
class SizeStyleAssessment:
    """分时微结构与大小盘风格综合评估输出（frozen）。"""

    size_diff_latest: float  # 最新 Size 因子值（大盘-小盘收益差）
    persistence: StylePersistence
    momentum: IntradayMomentumSignal
    vwap_deviation: float  # (最新价 - VWAP) / VWAP
    adx: float  # 分时 ADX ∈ [0,100]
    assessed_at: datetime.datetime


def _as_finite_series(name: str, values: Sequence[float], *, min_len: int = 1) -> tuple[float, ...]:
    """序列校验：长度下限 + 全部有限值，非法 Fail-Closed。"""
    try:
        seq = tuple(float(v) for v in values)
    except (TypeError, ValueError) as exc:
        raise IntradaySizeStyleError(f"{name} 含非数值元素: {exc}") from exc
    if len(seq) < min_len:
        raise IntradaySizeStyleError(f"{name} 长度 {len(seq)} < 下限 {min_len}")
    for v in seq:
        if not math.isfinite(v):
            raise IntradaySizeStyleError(f"{name} 含非有限值: {v!r}")
    return seq


def _sign(x: float) -> int:
    """符号函数：>0 → +1；<0 → -1；==0 → 0。"""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> float:
    """Pearson 相关系数；零方差降级 0.0（确定性）。"""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=False))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0.0 or vy == 0.0:
        return 0.0
    return cov / math.sqrt(vx * vy)


class IntradaySizeStyle:
    """分时微结构与大小盘风格统计件（纯内存，时钟注入）。

    Args:
        clock: 时钟注入（测试可控）；缺省系统时钟。
    """

    def __init__(self, *, clock: Callable[[], datetime.datetime] | None = None) -> None:
        self._clock = clock or datetime.datetime.now

    # ── Size 因子 ────────────────────────────────────────────────────────

    def size_factor_series(
        self,
        large_returns: Sequence[float],
        small_returns: Sequence[float],
    ) -> tuple[float, ...]:
        """Size 因子序列 = 大盘收益 - 小盘收益（逐日对齐）。"""
        large = _as_finite_series("large_returns", large_returns)
        small = _as_finite_series("small_returns", small_returns)
        if len(large) != len(small):
            raise IntradaySizeStyleError(f"大小盘收益序列长度不齐: {len(large)} vs {len(small)}")
        return tuple(l - s for l, s in zip(large, small, strict=False))

    # ── 风格持续性 ────────────────────────────────────────────────────────

    def style_persistence(
        self,
        size_diffs: Sequence[float],
        *,
        min_days: int = _DEFAULT_PERSISTENCE_DAYS,
    ) -> StylePersistence:
        """风格持续性：Size 差序列尾端同号连计数，> min_days 判定持续。"""
        if min_days < 1:
            raise IntradaySizeStyleError(f"min_days 非法: {min_days!r}（须 >= 1）")
        diffs = _as_finite_series("size_diffs", size_diffs)
        direction = _sign(diffs[-1])
        streak = 0
        for v in reversed(diffs):
            if _sign(v) != direction:
                break
            streak += 1
        if direction == 0:
            streak = 0  # 尾端为 0 视为无方向不持续
        return StylePersistence(
            direction=direction,
            streak_days=streak,
            is_persistent=streak > min_days,
        )

    # ── 日内动量（Gao 2018）──────────────────────────────────────────────

    def intraday_momentum_signal(
        self,
        first_half_returns: Sequence[float],
        second_half_returns: Sequence[float],
        *,
        window: int = _DEFAULT_MOMENTUM_WINDOW,
        corr_threshold: float = _DEFAULT_CORR_THRESHOLD,
    ) -> IntradayMomentumSignal:
        """首 30min 收益预测次 30min 收益：滚动相关 + 信号输出。

        相关 >= 阈值 → 信号取最新首半小时收益符号；否则 0。
        样本不足窗口 → window_ready=False 降级（correlation=0.0, signal=0）。
        """
        if window < 2:
            raise IntradaySizeStyleError(f"window 非法: {window!r}（须 >= 2）")
        if not 0.0 < corr_threshold <= 1.0:
            raise IntradaySizeStyleError(f"corr_threshold 非法: {corr_threshold!r}（须 ∈ (0,1]）")
        first = _as_finite_series("first_half_returns", first_half_returns)
        second = _as_finite_series("second_half_returns", second_half_returns)
        if len(first) != len(second):
            raise IntradaySizeStyleError(f"首/次半小时收益序列长度不齐: {len(first)} vs {len(second)}")
        if len(first) < window:
            _log.debug("日内动量窗口未就绪: %d < %d（降级）", len(first), window)
            return IntradayMomentumSignal(correlation=0.0, window_ready=False, signal=0)
        corr = _pearson(first[-window:], second[-window:])
        signal = _sign(first[-1]) if corr >= corr_threshold else 0
        return IntradayMomentumSignal(correlation=corr, window_ready=True, signal=signal)

    # ── VWAP 偏差 ────────────────────────────────────────────────────────

    def vwap_deviation(
        self,
        prices: Sequence[float],
        volumes: Sequence[float],
    ) -> float:
        """VWAP 偏差 = (最新价 - VWAP) / VWAP（总量为 0 Fail-Closed）。"""
        px = _as_finite_series("prices", prices)
        vol = _as_finite_series("volumes", volumes)
        if len(px) != len(vol):
            raise IntradaySizeStyleError(f"价量序列长度不齐: {len(px)} vs {len(vol)}")
        for p in px:
            if p <= 0.0:
                raise IntradaySizeStyleError(f"价格非正: {p!r}")
        for v in vol:
            if v < 0.0:
                raise IntradaySizeStyleError(f"成交量为负: {v!r}")
        total_vol = sum(vol)
        if total_vol <= 0.0:
            raise IntradaySizeStyleError("总成交量为 0（VWAP 无定义，Fail-Closed）")
        vwap = sum(p * v for p, v in zip(px, vol, strict=False)) / total_vol
        return (px[-1] - vwap) / vwap

    # ── 分时 ADX ─────────────────────────────────────────────────────────

    def intraday_adx(
        self,
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        *,
        period: int = _DEFAULT_ADX_PERIOD,
    ) -> float:
        """分时 ADX（简化 Wilder：周期滚动和 + DX 均值），∈ [0,100]。"""
        if period < 2:
            raise IntradaySizeStyleError(f"period 非法: {period!r}（须 >= 2）")
        hi = _as_finite_series("highs", highs)
        lo = _as_finite_series("lows", lows)
        cl = _as_finite_series("closes", closes)
        if not (len(hi) == len(lo) == len(cl)):
            raise IntradaySizeStyleError(f"高低收序列长度不齐: {len(hi)}/{len(lo)}/{len(cl)}")
        n = len(cl)
        if n < period + 1:
            raise IntradaySizeStyleError(f"样本 {n} 不足（ADX 需 period+1={period + 1}，Fail-Closed）")
        for h, l in zip(hi, lo, strict=False):
            if h < l:
                raise IntradaySizeStyleError(f"最高价 < 最低价: high={h!r} low={l!r}")

        trs: list[float] = []
        plus_dm: list[float] = []
        minus_dm: list[float] = []
        for i in range(1, n):
            up = hi[i] - hi[i - 1]
            down = lo[i - 1] - lo[i]
            plus_dm.append(up if (up > down and up > 0.0) else 0.0)
            minus_dm.append(down if (down > up and down > 0.0) else 0.0)
            trs.append(
                max(
                    hi[i] - lo[i],
                    abs(hi[i] - cl[i - 1]),
                    abs(lo[i] - cl[i - 1]),
                )
            )
        dx_values: list[float] = []
        for end in range(period, len(trs) + 1):
            atr = sum(trs[end - period : end])
            if atr == 0.0:
                dx_values.append(0.0)
                continue
            pdi = 100.0 * sum(plus_dm[end - period : end]) / atr
            mdi = 100.0 * sum(minus_dm[end - period : end]) / atr
            denom = pdi + mdi
            dx = 0.0 if denom == 0.0 else 100.0 * abs(pdi - mdi) / denom
            dx_values.append(dx)
        return sum(dx_values) / len(dx_values)

    # ── 综合评估 ──────────────────────────────────────────────────────────

    def assess(
        self,
        *,
        large_returns: Sequence[float],
        small_returns: Sequence[float],
        first_half_returns: Sequence[float],
        second_half_returns: Sequence[float],
        prices: Sequence[float],
        volumes: Sequence[float],
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        momentum_window: int = _DEFAULT_MOMENTUM_WINDOW,
        corr_threshold: float = _DEFAULT_CORR_THRESHOLD,
        adx_period: int = _DEFAULT_ADX_PERIOD,
        persistence_days: int = _DEFAULT_PERSISTENCE_DAYS,
    ) -> SizeStyleAssessment:
        """五因子综合评估（确定性聚合；时钟注入留痕）。"""
        diffs = self.size_factor_series(large_returns, small_returns)
        persistence = self.style_persistence(diffs, min_days=persistence_days)
        momentum = self.intraday_momentum_signal(
            first_half_returns,
            second_half_returns,
            window=momentum_window,
            corr_threshold=corr_threshold,
        )
        dev = self.vwap_deviation(prices, volumes)
        adx = self.intraday_adx(highs, lows, closes, period=adx_period)
        return SizeStyleAssessment(
            size_diff_latest=diffs[-1],
            persistence=persistence,
            momentum=momentum,
            vwap_deviation=dev,
            adx=adx,
            assessed_at=self._clock(),
        )
