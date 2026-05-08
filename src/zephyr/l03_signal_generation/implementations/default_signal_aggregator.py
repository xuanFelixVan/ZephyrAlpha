# ---
# layer: l03_signal_generation
# category: signal_implementation
# status: active
# created: "2026-05-05"
# ---

"""L03 — Default Signal Aggregator

信号聚合器具体实现。多因子信号（FactorSignal）→ 合成信号（SynthesizedSignal）。

CTR 契约：
  消费者 — CTR-002 (FactorSignal) ← L02
  生产者 — CTR-P1-015 (SynthesizedSignal) → L04, L05

SSoT: cross-layer-contracts.yaml → CTR-002 + CTR-P1-015
"""
from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from zephyr.l03_signal_generation.aggregator_base import SignalAggregatorBase
from zephyr.shared.contracts.market.factor_signal import FactorSignal
from zephyr.shared.contracts.market.synthesized_signal import SynthesizedSignal

_logger = logging.getLogger(__name__)

__aggregator_id__ = "default-signal-aggregator"


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
            return self._empty_signal(symbol, idempotency_key, t0)

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
            as_of_timestamp=datetime.now(timezone.utc),
            signal_value=signal_value,
            signal_direction=direction,
            confidence=confidence,
            generation_latency_ms=generation_latency_ms,
            idempotency_key=idempotency_key,
            regime="normal",
            suggested_position_pct=abs(signal_value) / 10.0,
            contributing_factors={},
        )

    def _equal_weight(self, signals: list[FactorSignal]) -> tuple[float, list[dict], float]:
        n = len(signals)
        raw = sum(s.normalized_value or s.raw_value for s in signals) / n
        contributions = [
            {"factor_id": s.factor_id, "weight": 1.0 / n, "raw_value": s.raw_value}
            for s in signals
        ]
        confidence = sum(s.confidence or 1.0 for s in signals) / n
        return raw, contributions, confidence

    def _confidence_weight(self, signals: list[FactorSignal]) -> tuple[float, list[dict], float]:
        confidences = [s.confidence or 1.0 for s in signals]
        total_conf = sum(confidences)
        if total_conf == 0:
            return 0.0, [], 0.0
        weights = [c / total_conf for c in confidences]
        raw = sum(
            (s.normalized_value or s.raw_value) * w for s, w in zip(signals, weights)
        )
        contributions = [
            {"factor_id": s.factor_id, "weight": w, "raw_value": s.raw_value}
            for s, w in zip(signals, weights)
        ]
        avg_conf = total_conf / len(signals)
        return raw, contributions, avg_conf

    def _ic_weight(self, signals: list[FactorSignal]) -> tuple[float, list[dict], float]:
        return self._equal_weight(signals)

    def _empty_signal(self, symbol: str, idempotency_key: str, t0: float) -> SynthesizedSignal:
        return SynthesizedSignal(
            signal_id=f"syn-empty-{symbol}-{uuid.uuid4().hex[:8]}",
            symbol=symbol,
            as_of_timestamp=datetime.now(timezone.utc),
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


__all__ = ["DefaultSignalAggregator"]
