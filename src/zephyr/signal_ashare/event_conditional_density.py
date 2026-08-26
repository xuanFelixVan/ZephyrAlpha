# [BLUEPRINT] MOD-SIG-123 | docs/03_modules/_domain_signal/event_conditional_density/blueprint.md
# [MODULE] zephyr.signal_ashare.event_conditional_density
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（协议核心纯内存；clock/event_classifier 全注入）
# [CONSUMERS] 运行时装配批（盘后事件条件分布批处理 / 信号-风控下游密度输入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 事件类型词表闭合(earnings|policy|contract|restructuring|buyback|reduction|penalty); 直方图计数守恒(Σcount==n_samples，构造即校验); 事件桶样本<min_samples 回退全事件池 degraded=True; 盘后批次 ≤max_batch_symbols(100) 只护栏; NLP 事件分类回调未注入 Fail-Closed 不旁路; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_signal/event_conditional_density/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] EventCondDensityError(占位 ZA-SIG-UNREGISTERED-EVENT-COND-DENSITY)——未注册事件类型/空事件文本/NLP回调缺失或异常/非法收益值/空样本/批次越护栏/计数不守恒时抛
# [TESTS] tests/signal_ashare/test_event_conditional_density.py
# [A_module] module_id=MOD-SIG-123 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""EventConditionalDensity — 事件驱动条件分布预测（MOD-SIG-123）。

B10-01412（AUD-DRAFT-001-DIGEST P2 波 P2-W05，CAND-TESTB-043，A1 B3）：
以**事件类型作条件变量**扩展条件密度预测——按事件类型分桶历史事件前瞻
收益，产出**收益分布直方图 + 经验分位数**的事件条件分布；事件源经**注入
NLP 分类回调**接入（文本→闭合事件词表，未注入 Fail-Closed 不旁路）；
**盘后批处理**语义（单次 ≤100 只护栏）；**分布计数守恒校验**（Σ直方图
计数 == 样本数，破守恒 Fail-Closed）。

查重分工（蓝图 §0）：conditional_density_predictor（MOD-SIG-043）=波动率
分桶/regime 标签的收益率条件密度（本件=事件类型条件变量扩展，分桶降级
语义同构：桶样本不足回退全样本 degraded）；event_driven_screener=事件选
股（本件不做选股，只产分布）；causal_inference_engine=因果推断（零交集）。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Iterable, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "AfterCloseBatchReport",
    "EventCondDensityConfig",
    "EventCondDensityError",
    "EventConditionalDensity",
    "EventDensity",
    "EventType",
    "HistogramBin",
]

#: 默认经验分位数网格（P5~P95 五点，覆盖尾部/四分位/中位）
_DEFAULT_QUANTILES: Final = (0.05, 0.25, 0.50, 0.75, 0.95)


class EventCondDensityError(Exception):
    """事件条件分布输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SIG-UNREGISTERED-EVENT-COND-DENSITY。
    """


class EventType(str, Enum):
    """A股事件类型（词表闭合）。"""

    EARNINGS = "earnings"  # 业绩预告/披露
    POLICY = "policy"  # 政策事件
    CONTRACT = "contract"  # 重大合同
    RESTRUCTURING = "restructuring"  # 并购重组
    BUYBACK = "buyback"  # 回购增持
    REDUCTION = "reduction"  # 股东减持
    PENALTY = "penalty"  # 监管处罚/违规


@dataclass(frozen=True)
class EventCondDensityConfig:
    """事件条件分布配置（构造即校验，Fail-Closed）。

    Attributes:
        bin_count: 直方图分桶数（≥1）
        min_samples: 事件桶最小样本数（不足回退全事件池 degraded）
        max_batch_symbols: 盘后批处理只数护栏（≤100）
        quantiles: 经验分位数网格（(0,1) 开区间，严格递增）
    """

    bin_count: int = 10
    min_samples: int = 5
    max_batch_symbols: int = 100
    quantiles: tuple[float, ...] = _DEFAULT_QUANTILES

    def __post_init__(self) -> None:
        if self.bin_count < 1:
            raise EventCondDensityError(f"bin_count 须≥1，实得 {self.bin_count}")
        if self.min_samples < 1:
            raise EventCondDensityError(f"min_samples 须≥1，实得 {self.min_samples}")
        if self.max_batch_symbols < 1:
            raise EventCondDensityError(
                f"max_batch_symbols 须≥1，实得 {self.max_batch_symbols}"
            )
        if not self.quantiles:
            raise EventCondDensityError("quantiles 为空")
        for p in self.quantiles:
            if not 0.0 < p < 1.0:
                raise EventCondDensityError(f"分位水平越界: {p!r}（须∈(0,1) 开区间）")
        for prev, nxt in zip(self.quantiles, self.quantiles[1:]):
            if prev >= nxt:
                raise EventCondDensityError(f"quantiles 须严格递增: {self.quantiles!r}")


@dataclass(frozen=True)
class HistogramBin:
    """直方图单桶（[lower, upper)，末桶右闭）。"""

    lower: float
    upper: float
    count: int


@dataclass(frozen=True)
class EventDensity:
    """事件条件分布输出（直方图 + 分位数；构造后须经计数守恒校验）。"""

    event_type: EventType
    n_samples: int
    histogram: tuple[HistogramBin, ...]
    quantiles: dict[float, float] = field(default_factory=dict)
    degraded: bool = False  # True=事件桶样本不足，回退全事件池


@dataclass(frozen=True)
class AfterCloseBatchReport:
    """盘后批处理报告（≤100 只护栏内逐只事件条件密度）。"""

    generated_at: datetime.datetime
    n_symbols: int
    densities: dict[str, EventDensity] = field(default_factory=dict)


def _quantile(values: Sequence[float], p: float) -> float:
    """经验分位数（线性插值，numpy 'linear' 同口径；确定性）。"""
    s = sorted(values)
    n = len(s)
    if n == 1:
        return s[0]
    pos = (n - 1) * p
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return s[lo]
    frac = pos - lo
    return s[lo] * (1.0 - frac) + s[hi] * frac


def _histogram(values: Sequence[float], bin_count: int) -> tuple[HistogramBin, ...]:
    """等宽直方图（常数序列首桶收全部；末桶右闭收最大值；计数守恒）。"""
    lo = min(values)
    hi = max(values)
    counts = [0] * bin_count
    span = hi - lo
    if span < 1e-12:  # 常数序列：首桶收全部
        counts[0] = len(values)
        return tuple(HistogramBin(lower=lo, upper=lo, count=c) for c in counts)
    width = span / bin_count
    for v in values:
        idx = int((v - lo) / width)
        if idx >= bin_count:  # 末桶右闭（v == hi 恰好落右沿）
            idx = bin_count - 1
        counts[idx] += 1
    return tuple(
        HistogramBin(lower=lo + i * width, upper=lo + (i + 1) * width, count=counts[i])
        for i in range(bin_count)
    )


class EventConditionalDensity:
    """事件驱动条件分布预测器（事件分桶 + 直方图/分位数 + 盘后批护栏）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        event_classifier: Callable[[str], EventType | str] | None = None,
        config: EventCondDensityConfig | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._classifier = event_classifier
        self._cfg = config or EventCondDensityConfig()
        self._samples: dict[EventType, list[float]] = {t: [] for t in EventType}

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _coerce_type(raw: EventType | str) -> EventType:
        """事件类型收口（未注册词表 → Fail-Closed）。"""
        if isinstance(raw, EventType):
            return raw
        try:
            return EventType(str(raw))
        except ValueError:
            raise EventCondDensityError(
                f"未注册事件类型: {raw!r}（词表闭合）"
            ) from None

    @staticmethod
    def _check_return(value: float) -> float:
        """前瞻收益取值校验（须有限实数）。"""
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise EventCondDensityError(f"非法前瞻收益: {value!r}（须有限实数）")
        return float(value)

    def _build(
        self, event_type: EventType, values: Sequence[float], *, degraded: bool
    ) -> EventDensity:
        """构造事件条件分布（直方图 + 分位数 + 计数守恒校验）。"""
        density = EventDensity(
            event_type=event_type,
            n_samples=len(values),
            histogram=_histogram(values, self._cfg.bin_count),
            quantiles={p: _quantile(values, p) for p in self._cfg.quantiles},
            degraded=degraded,
        )
        self.validate_conservation(density)  # 分布校验：计数守恒
        return density

    @staticmethod
    def validate_conservation(density: EventDensity) -> None:
        """分布校验：Σ直方图计数 == n_samples（破守恒 Fail-Closed）。"""
        total = sum(b.count for b in density.histogram)
        if total != density.n_samples:
            raise EventCondDensityError(
                f"直方图计数不守恒: Σcount={total} != n_samples={density.n_samples}"
            )

    # ── 事件源注入（NLP 事件分类回调）────────────────────────────────────

    def classify_event(self, text: str) -> EventType:
        """事件文本 → 闭合事件类型（NLP 回调未注入 Fail-Closed 不旁路）。"""
        if not text or not text.strip():
            raise EventCondDensityError("事件文本为空")
        if self._classifier is None:
            raise EventCondDensityError(
                "event_classifier 未注入（事件源强制 NLP 分类回调，禁止旁路）"
            )
        try:
            raw = self._classifier(text)
        except EventCondDensityError:
            raise
        except Exception as exc:  # noqa: BLE001 — 回调异常统一收口 Fail-Closed
            _log.exception("event_classifier 分类异常")
            raise EventCondDensityError(f"NLP 事件分类回调异常: {exc!r}") from exc
        return self._coerce_type(raw)

    # ── 样本登记 ─────────────────────────────────────────────────────────

    def add_sample(self, event_type: EventType | str, forward_return: float) -> None:
        """登记单条事件前瞻收益样本（未注册类型/非法取值 Fail-Closed）。"""
        t = self._coerce_type(event_type)
        self._samples[t].append(self._check_return(forward_return))

    def add_samples(
        self, event_type: EventType | str, forward_returns: Iterable[float]
    ) -> None:
        """批量登记事件前瞻收益样本（空序列 Fail-Closed）。"""
        values = list(forward_returns)
        if not values:
            raise EventCondDensityError("收益样本为空")
        for v in values:
            self.add_sample(event_type, v)

    def bucket_size(self, event_type: EventType | str) -> int:
        """事件桶样本数查询。"""
        return len(self._samples[self._coerce_type(event_type)])

    # ── 分布预测 ─────────────────────────────────────────────────────────

    def density(self, event_type: EventType | str) -> EventDensity:
        """单事件类型条件分布（桶样本不足回退全事件池 degraded=True）。"""
        t = self._coerce_type(event_type)
        bucket = self._samples[t]
        if len(bucket) >= self._cfg.min_samples:
            return self._build(t, bucket, degraded=False)
        pooled = [v for src in EventType for v in self._samples[src]]  # 词表序确定
        if not pooled:
            raise EventCondDensityError(f"事件桶样本为空且全事件池为空: {t.value}")
        _log.info(
            "事件桶 %s 样本 %d < %d，回退全事件池（degraded）",
            t.value,
            len(bucket),
            self._cfg.min_samples,
        )
        return self._build(t, pooled, degraded=True)

    # ── 盘后批处理（≤100 只护栏）─────────────────────────────────────────

    def run_after_close_batch(
        self,
        symbol_samples: Mapping[str, tuple[EventType | str, Iterable[float]]],
    ) -> AfterCloseBatchReport:
        """盘后批处理：逐只产出事件条件密度（只数越护栏 Fail-Closed）。

        Args:
            symbol_samples: {symbol: (事件类型, 前瞻收益样本序列)}

        Raises:
            EventCondDensityError: 批次为空/超 max_batch_symbols 只/空 symbol/
                未注册事件类型/空样本/非法收益值。
        """
        if not symbol_samples:
            raise EventCondDensityError("盘后批次为空")
        n = len(symbol_samples)
        if n > self._cfg.max_batch_symbols:
            raise EventCondDensityError(
                f"盘后批次越护栏: {n} > {self._cfg.max_batch_symbols} 只"
            )
        prepared: dict[str, tuple[EventType, list[float]]] = {}
        for symbol, (raw_type, raw_returns) in symbol_samples.items():
            if not symbol or not symbol.strip():
                raise EventCondDensityError("symbol 为空")
            t = self._coerce_type(raw_type)
            values = [self._check_return(v) for v in raw_returns]
            if not values:
                raise EventCondDensityError(f"{symbol} 收益样本为空")
            prepared[symbol] = (t, values)
        pooled: list[float] = []  # 插入序确定
        for _, vals in prepared.values():
            pooled.extend(vals)
        densities = {
            symbol: self._build(
                t,
                vals if len(vals) >= self._cfg.min_samples else pooled,
                degraded=len(vals) < self._cfg.min_samples,
            )
            for symbol, (t, vals) in prepared.items()
        }
        return AfterCloseBatchReport(
            generated_at=self._clock(), n_symbols=n, densities=densities
        )
