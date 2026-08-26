# [BLUEPRINT] MOD-SIG-116 | docs/03_modules/_domain_signal/wyckoff_secondary_test/blueprint.md
# [MODULE] zephyr.signal_ashare.wyckoff_secondary_test
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；k线序列/时钟全注入，不 import zephyr 内部件）
# [CONSUMERS] 运行时装配批（统一注入点装配：Wyckoff 信号层 / 延续-反转判定消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 结构词表闭合(markup|markdown|range)；判定词表闭合(continuation|reversal|neutral)；ST缩量确认=回踩均量<前波段均量×阈值且价格未破前低(markdown对称)；回调38.2%/61.8%历史概率表仅统计全horizon可见样本；同输入必同输出（确定性）
# [MODIFY-GUARD] docs/03_modules/_domain_signal/wyckoff_secondary_test/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] WyckoffStError(占位 ZA-SIG-UNREGISTERED-WYCKOFF-ST)——非法k线/非法配置/样本不足/非有限读数时抛
# [TESTS] tests/signal_ashare/test_wyckoff_secondary_test.py
# [A_module] module_id=MOD-SIG-116 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""WyckoffSecondaryTest — Wyckoff 二次测试模型（MOD-SIG-116）。

B10-01372（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-036，A1 模块18）：
Wyckoff ST 缩量确认（回踩均量 < 前波段均量 × 阈值）+ Markup/Markdown
识别（higher high / higher low vs lower high / lower low 结构判定）+
回调 38.2%/61.8% 历史概率表（滚动统计注入 k 线序列）+ 动量延续 vs 反转
判定输出。

纯内存/DI 设计：k 线序列由调用方注入，时钟注入；不触网、不触盘、
无 subprocess。同输入必同输出。非法输入 Fail-Closed 抛 WyckoffStError。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "KBar",
    "RetracementProbTable",
    "StructurePhase",
    "StVerdict",
    "WyckoffStConfig",
    "WyckoffStError",
    "WyckoffStReport",
    "WyckoffSecondaryTest",
]

_FIB_382: Final = 0.382
_FIB_618: Final = 0.618


class WyckoffStError(Exception):
    """Wyckoff 二次测试输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-WYCKOFF-ST。
    """


class StructurePhase(str, Enum):
    """Wyckoff 结构相位（词表闭合）。"""

    MARKUP = "markup"
    MARKDOWN = "markdown"
    RANGE = "range"


class StVerdict(str, Enum):
    """二次测试判定（词表闭合）。"""

    CONTINUATION = "continuation"
    REVERSAL = "reversal"
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class KBar:
    """单根 K 线（frozen；high≥low、价格为正、量非负、全有限）。"""

    ts: datetime.datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        for name in ("open", "high", "low", "close", "volume"):
            v = getattr(self, name)
            if isinstance(v, bool) or not math.isfinite(v):
                raise WyckoffStError(f"KBar.{name} 非有限数: {v!r}")
        if self.high < self.low:
            raise WyckoffStError(f"KBar.high({self.high}) < low({self.low})")
        if self.open <= 0 or self.high <= 0 or self.low <= 0 or self.close <= 0:
            raise WyckoffStError("KBar 价格必须为正")
        if self.volume < 0:
            raise WyckoffStError(f"KBar.volume 不可为负: {self.volume}")


@dataclass(frozen=True)
class WyckoffStConfig:
    """二次测试配置（frozen）。"""

    pivot_order: int = 2
    min_bars: int = 12
    st_volume_threshold: float = 0.85
    fib_tolerance: float = 0.05
    prob_horizon: int = 10

    def __post_init__(self) -> None:
        if isinstance(self.pivot_order, bool) or self.pivot_order < 1:
            raise WyckoffStError(f"pivot_order 必须 ≥1: {self.pivot_order!r}")
        if isinstance(self.min_bars, bool) or self.min_bars < 2 * self.pivot_order + 3:
            raise WyckoffStError(
                f"min_bars 必须 ≥ 2*pivot_order+3: {self.min_bars!r}"
            )
        if not math.isfinite(self.st_volume_threshold) or self.st_volume_threshold <= 0:
            raise WyckoffStError(f"st_volume_threshold 必须为正有限: {self.st_volume_threshold!r}")
        if not math.isfinite(self.fib_tolerance) or not (0 < self.fib_tolerance <= 0.25):
            raise WyckoffStError(f"fib_tolerance 须在 (0, 0.25]: {self.fib_tolerance!r}")
        if isinstance(self.prob_horizon, bool) or self.prob_horizon < 1:
            raise WyckoffStError(f"prob_horizon 必须 ≥1: {self.prob_horizon!r}")


@dataclass(frozen=True)
class RetracementProbTable:
    """回调 38.2%/61.8% 历史概率表（滚动统计注入 k 线序列）。

    仅统计「入场后 horizon 根 k 线全部可见」的样本；无样本时概率为 0.0。
    """

    samples_382: int
    continuations_382: int
    samples_618: int
    continuations_618: int

    @property
    def prob_382(self) -> float:
        """38.2% 区延续概率（无样本 0.0）。"""
        if self.samples_382 <= 0:
            return 0.0
        return self.continuations_382 / self.samples_382

    @property
    def prob_618(self) -> float:
        """61.8% 区延续概率（无样本 0.0）。"""
        if self.samples_618 <= 0:
            return 0.0
        return self.continuations_618 / self.samples_618


@dataclass(frozen=True)
class WyckoffStReport:
    """二次测试报告（frozen）。score ∈ [-1, 1]：正=多头延续/空转多，负=空头延续/多转空。"""

    phase: StructurePhase
    st_confirmed: bool
    volume_ratio: float | None
    retracement_ratio: float | None
    prob_table: RetracementProbTable
    verdict: StVerdict
    score: float
    reason: str
    generated_at: datetime.datetime


def _avg(values: Sequence[float]) -> float:
    return sum(values) / len(values)


class WyckoffSecondaryTest:
    """Wyckoff 二次测试模型（结构判定 + ST 缩量确认 + 概率表 + 延续/反转）。"""

    def __init__(
        self,
        *,
        config: WyckoffStConfig | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._config = config or WyckoffStConfig()
        self._clock = clock or datetime.datetime.now

    # ── 内部：摆点检测 ────────────────────────────────────────────────────

    def _pivots(
        self, bars: Sequence[KBar]
    ) -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
        """严格大于/小于两侧 order 根的摆点（确定性顺序）。"""
        order = self._config.pivot_order
        highs: list[tuple[int, float]] = []
        lows: list[tuple[int, float]] = []
        n = len(bars)
        for i in range(order, n - order):
            h = bars[i].high
            if all(h > bars[j].high for j in range(i - order, i)) and all(
                h > bars[j].high for j in range(i + 1, i + order + 1)
            ):
                highs.append((i, h))
            lo = bars[i].low
            if all(lo < bars[j].low for j in range(i - order, i)) and all(
                lo < bars[j].low for j in range(i + 1, i + order + 1)
            ):
                lows.append((i, lo))
        return highs, lows

    # ── 内部：结构判定 ────────────────────────────────────────────────────

    @staticmethod
    def _structure(
        highs: list[tuple[int, float]], lows: list[tuple[int, float]]
    ) -> StructurePhase:
        if len(highs) < 2 or len(lows) < 2:
            return StructurePhase.RANGE
        hh = highs[-1][1] > highs[-2][1]
        hl = lows[-1][1] > lows[-2][1]
        if hh and hl:
            return StructurePhase.MARKUP
        if (not hh) and (not hl):
            return StructurePhase.MARKDOWN
        return StructurePhase.RANGE

    # ── 内部：历史概率表（滚动统计注入序列） ──────────────────────────────

    def _probability_table(
        self,
        bars: Sequence[KBar],
        highs: list[tuple[int, float]],
        lows: list[tuple[int, float]],
    ) -> RetracementProbTable:
        tol = self._config.fib_tolerance
        horizon = self._config.prob_horizon
        pivots = sorted(
            [(i, p, "H") for i, p in highs] + [(i, p, "L") for i, p in lows]
        )
        s382 = c382 = s618 = c618 = 0
        n = len(bars)
        for a, b in zip(pivots, pivots[1:]):
            _i_a, p_a, t_a = a
            i_b, p_b, t_b = b
            if t_a == t_b:
                continue
            up = t_a == "L"  # L->H 上升腿；H->L 下降腿
            span = (p_b - p_a) if up else (p_a - p_b)
            if span <= 0:
                continue
            seen382 = seen618 = False
            for k in range(i_b + 1, n):
                if seen382 and seen618:
                    break
                r = ((p_b - bars[k].close) / span) if up else ((bars[k].close - p_b) / span)
                end = k + 1 + horizon
                if end > n:
                    continue  # horizon 不全可见的样本不计
                if up:
                    cont = any(bars[m].close > p_b for m in range(k + 1, end))
                else:
                    cont = any(bars[m].close < p_b for m in range(k + 1, end))
                if not seen382 and abs(r - _FIB_382) <= tol:
                    seen382 = True
                    s382 += 1
                    c382 += int(cont)
                if not seen618 and abs(r - _FIB_618) <= tol:
                    seen618 = True
                    s618 += 1
                    c618 += int(cont)
        return RetracementProbTable(
            samples_382=s382, continuations_382=c382,
            samples_618=s618, continuations_618=c618,
        )

    # ── 主入口 ────────────────────────────────────────────────────────────

    def analyze(self, bars: Sequence[KBar]) -> WyckoffStReport:
        """分析注入 k 线序列（按给定时间序），输出二次测试报告。"""
        bars = tuple(bars)
        if not bars:
            raise WyckoffStError("k线序列为空")
        for b in bars:
            if not isinstance(b, KBar):
                raise WyckoffStError(f"非 KBar 元素: {type(b)!r}")
        if len(bars) < self._config.min_bars:
            raise WyckoffStError(
                f"k线样本不足: {len(bars)} < min_bars={self._config.min_bars}"
            )

        highs, lows = self._pivots(bars)
        phase = self._structure(highs, lows)
        table = self._probability_table(bars, highs, lows)
        close = bars[-1].close
        thr = self._config.st_volume_threshold
        tol = self._config.fib_tolerance

        volume_ratio: float | None = None
        retracement: float | None = None
        st_confirmed = False
        verdict = StVerdict.NEUTRAL
        score = 0.0
        reason = "结构不明（range），不判定"

        leg: tuple[float, float] | None = None  # (swing_low, swing_high)
        pullback: tuple[KBar, ...] = ()
        impulse: tuple[KBar, ...] = ()

        if phase is StructurePhase.MARKUP:
            hi_idx, hi_p = highs[-1]
            prior_lows = [(i, p) for i, p in lows if i < hi_idx]
            if prior_lows:
                lo_idx, lo_p = prior_lows[-1]
                leg = (lo_p, hi_p)
                impulse = tuple(bars[lo_idx:hi_idx + 1])
                pullback = tuple(bars[hi_idx + 1:])
        elif phase is StructurePhase.MARKDOWN:
            lo_idx, lo_p = lows[-1]
            prior_highs = [(i, p) for i, p in highs if i < lo_idx]
            if prior_highs:
                hi_idx, hi_p = prior_highs[-1]
                leg = (lo_p, hi_p)
                impulse = tuple(bars[hi_idx:lo_idx + 1])
                pullback = tuple(bars[lo_idx + 1:])

        if phase is not StructurePhase.RANGE and leg is None:
            phase = StructurePhase.RANGE
            reason = "摆点不足以成腿，降级 range"

        if leg is not None:
            lo_p, hi_p = leg
            span = hi_p - lo_p
            if span <= 0:
                raise WyckoffStError(f"摆点区间非法: low={lo_p} high={hi_p}")
            if pullback:
                avg_imp = _avg([b.volume for b in impulse])
                avg_pull = _avg([b.volume for b in pullback])
                if avg_imp > 0:
                    volume_ratio = avg_pull / avg_imp
            if phase is StructurePhase.MARKUP:
                retracement = (hi_p - close) / span
                st_confirmed = (
                    volume_ratio is not None
                    and volume_ratio < thr
                    and close >= lo_p
                )
                if retracement > 1.0:
                    verdict = StVerdict.REVERSAL
                    reason = "跌破前波段低点，延续失败（反转）"
                elif st_confirmed and retracement <= _FIB_618 + tol:
                    verdict = StVerdict.CONTINUATION
                    reason = "ST缩量确认+回调守住61.8%区，动量延续"
                elif (not st_confirmed) and retracement >= _FIB_618 - tol:
                    verdict = StVerdict.REVERSAL
                    reason = "放量深调（≥61.8%），反转风险"
                else:
                    reason = "回踩量能/深度未达判定阈值"
            else:  # MARKDOWN
                retracement = (close - lo_p) / span
                st_confirmed = (
                    volume_ratio is not None
                    and volume_ratio < thr
                    and close <= hi_p
                )
                if retracement > 1.0:
                    verdict = StVerdict.REVERSAL
                    reason = "反弹破前波段高点，下跌延续失败（反转）"
                elif st_confirmed and retracement <= _FIB_618 + tol:
                    verdict = StVerdict.CONTINUATION
                    reason = "反抽缩量确认+未越61.8%区，下跌延续"
                elif (not st_confirmed) and retracement >= _FIB_618 - tol:
                    verdict = StVerdict.REVERSAL
                    reason = "放量深反抽（≥61.8%），反转风险"
                else:
                    reason = "反抽量能/深度未达判定阈值"

            if verdict is not StVerdict.NEUTRAL and retracement is not None:
                if retracement <= 0.5:
                    p = table.prob_382 if table.samples_382 > 0 else 0.5
                else:
                    p = table.prob_618 if table.samples_618 > 0 else 0.5
                bullish = (
                    (phase is StructurePhase.MARKUP and verdict is StVerdict.CONTINUATION)
                    or (phase is StructurePhase.MARKDOWN and verdict is StVerdict.REVERSAL)
                )
                score = p if bullish else -p

        report = WyckoffStReport(
            phase=phase,
            st_confirmed=st_confirmed,
            volume_ratio=volume_ratio,
            retracement_ratio=retracement,
            prob_table=table,
            verdict=verdict,
            score=score,
            reason=reason,
            generated_at=self._clock(),
        )
        _log.debug(
            "Wyckoff ST: phase=%s verdict=%s r=%s vr=%s",
            phase.value, verdict.value, retracement, volume_ratio,
        )
        return report
