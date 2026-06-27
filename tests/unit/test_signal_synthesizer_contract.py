# [A_test] module_id: SRC-TST-2065 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-682 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_signal_synthesizer_contract
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""SignalSynthesizerBase — FactorSignal 入参 / SynthesizedSignal 出站对齐。"""


import uuid
from datetime import UTC, datetime

from zephyr.signal_fundamental.synth.signal_synthesizer import SignalSynthesizerBase
from zephyr.trading.trading_contracts.market.factor_signal import FactorSignal
from zephyr.trading.trading_contracts.market.synthesized_signal import SynthesizedSignal


class _EqualWeightTestSynthesizer(SignalSynthesizerBase):
    """最小合成实现：等权平均 normalized_value / raw_value。"""

    __synthesizer_id__ = "unit-test-equal-weight"

    def synthesize(
        self,
        factor_signals: list[FactorSignal],
        symbol: str,
        as_of_timestamp: datetime,
        weights: dict[str, float] | None = None,
    ) -> SynthesizedSignal:
        if not factor_signals:
            return SynthesizedSignal(
                signal_id=f"empty-{uuid.uuid4().hex[:8]}",
                symbol=symbol,
                as_of_timestamp=as_of_timestamp,
                signal_value=0.0,
                signal_direction="NEUTRAL",
                confidence=0.0,
                generation_latency_ms=0,
                idempotency_key=self.default_idempotency_key(symbol, as_of_timestamp),
                is_degraded=True,
            )
        vals: list[float] = []
        contrib: dict[str, float] = {}
        wmap = weights or {}
        for fs in factor_signals:
            v = fs.normalized_value if fs.normalized_value is not None else fs.raw_value
            w = wmap.get(fs.factor_id, 1.0)
            vals.append(float(v) * w)
            contrib[fs.factor_id] = w
        raw = sum(vals) / max(len(vals), 1)
        signal_value = self.normalize_signal(raw)
        direction = self.direction_from_value(signal_value)
        conf = sum(fs.confidence for fs in factor_signals) / len(factor_signals)
        return SynthesizedSignal(
            signal_id=f"syn-{uuid.uuid4().hex[:8]}",
            symbol=symbol,
            as_of_timestamp=as_of_timestamp,
            signal_value=signal_value,
            signal_direction=direction,
            confidence=conf,
            contributing_factors=contrib,
            generation_latency_ms=1,
            idempotency_key=self.default_idempotency_key(symbol, as_of_timestamp),
            is_degraded=conf < 0.5,
        )


def test_signal_synthesizer_accepts_factor_signal_list() -> None:
    ts = datetime.now(UTC)
    fs = [
        FactorSignal(
            factor_id="a",
            symbol="600519",
            as_of_date=ts,
            raw_value=1.0,
            normalized_value=0.5,
            idempotency_key=str(uuid.uuid4()),
        ),
        FactorSignal(
            factor_id="b",
            symbol="600519",
            as_of_date=ts,
            raw_value=-1.0,
            normalized_value=-0.5,
            idempotency_key=str(uuid.uuid4()),
        ),
    ]
    synth = _EqualWeightTestSynthesizer()
    out = synth.synthesize(fs, "600519", ts)
    assert isinstance(out, SynthesizedSignal)
    assert out.symbol == "600519"
    assert -3.0 <= out.signal_value <= 3.0
    assert set(out.contributing_factors.keys()) == {"a", "b"}
