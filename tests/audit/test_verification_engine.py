# [A_test] module_id: SRC-TST-1784 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_verification_engine
# [INVARIANTS] Verdict thresholds: delta<-0.01=HARMFUL; |delta|<0.01=INEFFECTIVE; else=EFFECTIVE
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_verification_engine.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.verification_engine import (
    Verdict,
    VerificationEngine,
    VerificationResult,
)


class TestVerificationEngineInstantiation:
    def test_default_construction(self):
        engine = VerificationEngine()
        assert engine is not None

    def test_is_dataclass(self):
        engine = VerificationEngine()
        assert hasattr(engine, "verify")


class TestVerify:
    def test_effective_positive_delta(self):
        engine = VerificationEngine()
        result = engine.verify("anom-1", pre_value=1.0, post_value=2.0, timestamp=100.0)
        assert isinstance(result, VerificationResult)
        assert result.verdict == Verdict.EFFECTIVE
        assert result.delta == pytest.approx(1.0)
        assert result.anomaly_id == "anom-1"

    def test_harmful_negative_delta(self):
        engine = VerificationEngine()
        result = engine.verify("anom-2", pre_value=5.0, post_value=3.0, timestamp=200.0)
        assert result.verdict == Verdict.HARMFUL
        assert result.delta == pytest.approx(-2.0)

    def test_ineffective_tiny_delta(self):
        engine = VerificationEngine()
        result = engine.verify("anom-3", pre_value=1.0, post_value=1.005, timestamp=300.0)
        assert result.verdict == Verdict.INEFFECTIVE
        assert abs(result.delta) < 0.01

    def test_ineffective_zero_delta(self):
        engine = VerificationEngine()
        result = engine.verify("anom-4", pre_value=10.0, post_value=10.0, timestamp=400.0)
        assert result.verdict == Verdict.INEFFECTIVE
        assert result.delta == pytest.approx(0.0)

    def test_boundary_harmful_threshold(self):
        engine = VerificationEngine()
        result = engine.verify("anom-5", pre_value=1.0, post_value=0.98, timestamp=500.0)
        assert result.verdict == Verdict.HARMFUL
        assert result.delta == pytest.approx(-0.02)

    def test_boundary_ineffective_threshold(self):
        engine = VerificationEngine()
        result = engine.verify("anom-6", pre_value=1.0, post_value=1.009, timestamp=600.0)
        assert result.verdict == Verdict.INEFFECTIVE

    def test_negative_pre_value(self):
        engine = VerificationEngine()
        result = engine.verify("anom-7", pre_value=-5.0, post_value=-3.0, timestamp=700.0)
        assert result.verdict == Verdict.EFFECTIVE
        assert result.delta == pytest.approx(2.0)

    def test_zero_values(self):
        engine = VerificationEngine()
        result = engine.verify("anom-8", pre_value=0.0, post_value=0.0, timestamp=800.0)
        assert result.verdict == Verdict.INEFFECTIVE
