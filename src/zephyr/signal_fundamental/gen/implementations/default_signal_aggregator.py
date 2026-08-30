# [BLUEPRINT] MOD-L03-001 | docs/03_modules/_domain_signal/blueprint.md
# [MODULE] zephyr.signal_fundamental.gen.implementations.default_signal_aggregator
# [DOMAIN] D_FUNDAMENTAL_SIGNAL
# [DEPENDENCIES] zephyr.signal_fundamental.gen.aggregator_base; zephyr.shared.contracts.factor_signal; zephyr.shared.contracts.synthesized_signal
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/signal/test_default_signal_aggregator.py
# [A_module] module_id=MOD-L03-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: signal
# category: signal_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_SIGNAL — Default Signal Aggregator

信号聚合器具体实现。多因子信号（FactorSignal）-> 合成信号（SynthesizedSignal）。

CTR 契约：
  消费者 — CTR-002 (FactorSignal) ← D_FACTOR
  生产者 — CTR-P1-015 (SynthesizedSignal) -> D_RISK, D_PORTFOLIO_CORE

SSoT: cross_layer_contracts.yaml -> CTR-002 + CTR-P1-015
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Final

from zephyr.shared.contracts.factor_signal import FactorSignal
from zephyr.shared.contracts.synthesized_signal import SynthesizedSignal
from zephyr.signal_fundamental.gen.aggregator_base import SignalAggregatorBase

_logger = logging.getLogger(__name__)

__aggregator_id__ = "default-signal-aggregator"


@dataclass(frozen=True)
class PortfolioSignalEntry:
    """组合级信号条目（单标的，CAND-SIG-005）。

    Attributes:
        symbol: 标的代码
        weight: 归一化权重（同批 entries Σ=1）
        direction: 合成信号方向（组合级只纳入 LONG 候选，A股无做空）
        signal_value: 合成信号值（[-3,3]）
        confidence: 合成置信度
        trigger_conditions: 触发条件明细（贡献因子+权重，"factor_id:w=..." 升序）
        idempotency_key: 条目幂等键（父键-标的派生）
    """

    symbol: str
    weight: float
    direction: str
    signal_value: float
    confidence: float
    trigger_conditions: tuple[str, ...]
    idempotency_key: str


@dataclass(frozen=True)
class PortfolioSignalOutput:
    """组合级聚合输出（标的清单+归一化权重+触发条件明细，CAND-SIG-005）。

    Attributes:
        entries: 入选标的条目（按 symbol 升序，确定性）
        total_weight: 权重合计（归一化后=1.0；空组合=0.0）
        degraded_symbols: 降级（有效因子不足/无信号）被剔除的标的
        timestamp: 组合时间戳（取入选信号 as_of_timestamp 最大值，PIT 一致）
        idempotency_key: 组合级幂等键
    """

    entries: tuple[PortfolioSignalEntry, ...]
    total_weight: float
    degraded_symbols: tuple[str, ...]
    timestamp: datetime
    idempotency_key: str


class DefaultSignalAggregator(SignalAggregatorBase):
    """默认信号聚合器——等权聚合 + 信号强度缩放"""

    __aggregator_id__ = __aggregator_id__

    def __init__(
        self,
        aggregation_method: str = "equal_weight",
        min_factors_required: int = 2,
        min_confidence: float = 0.3,
    ):
        self._method = aggregation_method
        self._min_factors = min_factors_required
        self._min_confidence = min_confidence

    def aggregate(
        self,
        factor_signals: list[FactorSignal],
        symbol: str,
        idempotency_key: str,
    ) -> SynthesizedSignal:
        t0 = time.perf_counter()

        if not factor_signals:
            return self._empty_signal(symbol, idempotency_key, t0)

        valid = [s for s in factor_signals if s.is_valid and (s.confidence or 1.0) >= self._min_confidence]
        if len(valid) < self._min_factors:
            _logger.warning("Insufficient valid factors: %d/%d for symbol=%s", len(valid), len(factor_signals), symbol)
            # PIT 一致性：降级路径仍须用因子信号时间戳，禁止 wall-clock（回测时会注入未来信息）
            return self._empty_signal(symbol, idempotency_key, t0, as_of_date=factor_signals[0].as_of_date)

        if self._method == "equal_weight":
            signal_value, contributions, confidence = self._equal_weight(valid)
        elif self._method == "confidence_weight":
            signal_value, contributions, confidence = self._confidence_weight(valid)
        elif self._method == "ic_weight":
            signal_value, contributions, confidence = self._ic_weight(valid)
        else:
            signal_value, contributions, confidence = self._equal_weight(valid)

        signal_value = self.normalize_signal(signal_value)
        direction = "LONG" if signal_value > 0 else "SHORT" if signal_value < 0 else "NEUTRAL"
        generation_latency_ms = int((time.perf_counter() - t0) * 1000)

        return SynthesizedSignal(
            signal_id=f"syn-{symbol}-{uuid.uuid4().hex[:8]}",
            symbol=symbol,
            # PIT 一致性：as_of_timestamp 须取自因子信号 as_of_date，禁止 wall-clock（回测时 datetime.now 会注入未来信息）
            as_of_timestamp=valid[0].as_of_date,
            signal_value=signal_value,
            signal_direction=direction,
            confidence=confidence,
            generation_latency_ms=generation_latency_ms,
            idempotency_key=idempotency_key,
            regime="normal",
            suggested_position_pct=abs(signal_value) / 10.0,
            # 基类契约：contributing_factors 必须记录每个因子的权重（下游归因分析）
            contributing_factors={c["factor_id"]: c["weight"] for c in contributions},
        )

    # ── 组合级输出（CAND-SIG-005：标的清单+归一化权重+触发条件明细）──

    def aggregate_portfolio(
        self,
        signals_by_symbol: dict[str, list[FactorSignal]],
        idempotency_key: str,
    ) -> PortfolioSignalOutput:
        """组合级聚合：多标的因子信号 → 标的清单 + 归一化权重 + 触发条件明细。

        流程：逐标的调 aggregate() 单标的聚合 → 剔除降级/非正向信号（A股无做空，
        组合级只纳入 LONG 候选）→ 原始分 = |signal_value| × confidence →
        归一化权重（Σ=1）。权重非正（零信号）标的同样剔除。

        Args:
            signals_by_symbol: {symbol: [FactorSignal]}（CTR-002 因子信号分组）
            idempotency_key: 组合级幂等键（条目键按 父键-symbol 派生）

        Returns:
            PortfolioSignalOutput（entries 按 symbol 升序，确定性）
        """
        included: list[tuple[str, SynthesizedSignal, float]] = []
        degraded: list[str] = []

        for symbol in sorted(signals_by_symbol):
            sig = self.aggregate(
                signals_by_symbol[symbol],
                symbol,
                f"{idempotency_key}-{symbol}",
            )
            if sig.is_degraded:
                degraded.append(symbol)
                continue
            if sig.signal_value <= 0:
                continue  # NEUTRAL/SHORT 不入组合清单（A股无做空）
            included.append((symbol, sig, abs(sig.signal_value) * sig.confidence))

        if not included:
            return PortfolioSignalOutput(
                entries=(),
                total_weight=0.0,
                degraded_symbols=tuple(degraded),
                timestamp=datetime.now(UTC),
                idempotency_key=idempotency_key,
            )

        total_score = sum(score for _, _, score in included)
        entries = tuple(
            PortfolioSignalEntry(
                symbol=symbol,
                weight=(score / total_score) if total_score > 0 else 0.0,
                direction=sig.signal_direction,
                signal_value=sig.signal_value,
                confidence=sig.confidence,
                trigger_conditions=tuple(
                    f"{fid}:w={w:.4f}" for fid, w in sorted(sig.contributing_factors.items())
                ),
                idempotency_key=sig.idempotency_key,
            )
            for symbol, sig, score in included
        )
        timestamp = max(sig.as_of_timestamp for _, sig, _ in included)
        _logger.info(
            "Portfolio aggregation: symbols=%d degraded=%d total_weight=%.4f",
            len(entries),
            len(degraded),
            sum(e.weight for e in entries),
        )
        return PortfolioSignalOutput(
            entries=entries,
            total_weight=sum(e.weight for e in entries),
            degraded_symbols=tuple(degraded),
            timestamp=timestamp,
            idempotency_key=idempotency_key,
        )

    def _equal_weight(self, signals: list[FactorSignal]) -> tuple[float, list[dict], float]:
        n = len(signals)
        raw = sum(s.normalized_value or s.raw_value for s in signals) / n
        contributions = [{"factor_id": s.factor_id, "weight": 1.0 / n, "raw_value": s.raw_value} for s in signals]
        confidence = sum(s.confidence or 1.0 for s in signals) / n
        return raw, contributions, confidence

    def _confidence_weight(self, signals: list[FactorSignal]) -> tuple[float, list[dict], float]:
        confidences = [s.confidence or 1.0 for s in signals]
        total_conf = sum(confidences)
        if total_conf == 0:
            return 0.0, [], 0.0
        weights = [c / total_conf for c in confidences]
        raw = sum((s.normalized_value or s.raw_value) * w for s, w in zip(signals, weights, strict=False))
        contributions = [
            {"factor_id": s.factor_id, "weight": w, "raw_value": s.raw_value}
            for s, w in zip(signals, weights, strict=False)
        ]
        avg_conf = total_conf / len(signals)
        return raw, contributions, avg_conf

    def _ic_weight(self, signals: list[FactorSignal]) -> tuple[float, list[dict], float]:
        return self._equal_weight(signals)

    def _empty_signal(
        self, symbol: str, idempotency_key: str, t0: float, as_of_date: datetime | None = None
    ) -> SynthesizedSignal:
        return SynthesizedSignal(
            signal_id=f"syn-empty-{symbol}-{uuid.uuid4().hex[:8]}",
            symbol=symbol,
            # PIT 一致性：优先用因子信号时间戳；无因子信号时回退 wall-clock（仅实时路径）
            as_of_timestamp=as_of_date if as_of_date is not None else datetime.now(UTC),
            signal_value=0.0,
            signal_direction="NEUTRAL",
            confidence=0.0,
            generation_latency_ms=int((time.perf_counter() - t0) * 1000),
            idempotency_key=idempotency_key,
            regime="normal",
            suggested_position_pct=0.0,
            contributing_factors={},
            is_degraded=True,
        )


__all__: Final = ["DefaultSignalAggregator", "PortfolioSignalEntry", "PortfolioSignalOutput"]
