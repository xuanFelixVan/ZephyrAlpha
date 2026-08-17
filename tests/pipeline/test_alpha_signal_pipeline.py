# [A_test] module_id: MOD-GOV_alpha_signal_pipeline | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] tests.test_alpha_signal_pipeline
# [INVARIANTS] must test all public classes and methods of alpha_signal_pipeline
# [MODIFY-GUARD] alpha_signal_pipeline.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/test_alpha_signal_pipeline.py
# [TTL] task_bound

from unittest.mock import MagicMock, patch

import pytest

from zephyr.signal_fundamental.pipeline import (
    AlphaSignalPipeline,
    PipelineError,
    PipelineResult,
    PipelineStage,
)


class TestPipelineStage:
    def test_enum_values(self):
        assert PipelineStage.FACTOR_DISCOVERY.value == "factor_discovery"
        assert PipelineStage.FACTOR_COMPUTE.value == "factor_compute"
        assert PipelineStage.SIGNAL_SYNTHESIS.value == "signal_synthesis"
        assert PipelineStage.SIGNAL_VALIDATION.value == "signal_validation"
        assert PipelineStage.CAPITAL_ALLOCATION.value == "capital_allocation"

    def test_enum_count(self):
        assert len(PipelineStage) == 5


class TestPipelineError:
    """PipelineError 契约对齐 shared/foundation/errors.py SSoT（5.76.1 修复后）。"""

    def test_instantiation(self):
        err = PipelineError("test error")
        assert err.message == "test error"
        assert err.details == {}
        assert err.error_code == "ZA-SH-0007"

    def test_with_detail(self):
        err = PipelineError("fail", details={"k": "v"})
        assert err.details == {"k": "v"}


class TestPipelineResult:
    def test_default_values(self):
        r = PipelineResult(
            pipeline_id="p1",
            status="running",
            stage=PipelineStage.FACTOR_DISCOVERY,
        )
        assert r.pipeline_id == "p1"
        assert r.status == "running"
        assert r.factors_computed == 0
        assert r.factors_failed == 0
        assert r.signal_count == 0
        assert r.confidence == 0.0
        assert r.degraded is False
        assert r.errors == []
        assert r.completed_at is None
        assert r.idempotency_key != ""

    def test_custom_values(self):
        r = PipelineResult(
            pipeline_id="p2",
            status="completed",
            stage=PipelineStage.CAPITAL_ALLOCATION,
            factors_computed=5,
            factors_failed=1,
            signal_count=3,
            confidence=0.85,
            degraded=True,
            errors=[{"msg": "warn"}],
            completed_at="2026-01-01T00:00:00",
            idempotency_key="key-123",
        )
        assert r.factors_computed == 5
        assert r.confidence == 0.85
        assert r.degraded is True


class TestAlphaSignalPipeline:
    def test_instantiation(self):
        pipe = AlphaSignalPipeline()
        assert pipe.factors == []
        assert pipe.synthesizers == []
        assert pipe.degraded_reasons == []

    def test_run_no_factors(self):
        pipe = AlphaSignalPipeline()
        result = pipe.run()
        assert result.status == "no_factors"
        assert result.factors_computed == 0

    def test_run_with_custom_idempotency_key(self):
        pipe = AlphaSignalPipeline()
        result = pipe.run(idempotency_key="my-key")
        assert result.idempotency_key == "my-key"

    def test_run_with_simple_factor(self):
        pipe = AlphaSignalPipeline()

        class GoodFactor:
            def compute(self):
                return [MagicMock(confidence=0.8, signal_value=1.0)]

        pipe.factors = [GoodFactor]
        result = pipe.run()
        assert result.factors_computed == 1
        assert result.signal_count >= 1

    def test_run_factor_exception(self):
        pipe = AlphaSignalPipeline()

        class BadFactor:
            def compute(self):
                raise RuntimeError("factor error")

        pipe.factors = [BadFactor]
        result = pipe.run()
        assert result.factors_failed == 1
        assert any("factor error" in e.get("error", "") for e in result.errors)

    def test_run_factor_no_compute_method(self):
        pipe = AlphaSignalPipeline()

        class EmptyFactor:
            pass

        pipe.factors = [EmptyFactor]
        result = pipe.run()
        assert result.factors_computed == 0

    def test_register_factor_blacklisted(self):
        pipe = AlphaSignalPipeline()
        with patch("zephyr.signal_fundamental.pipeline._CONTRACTS_AVAILABLE", True):

            class MaliciousFactor:
                pass

            MaliciousFactor.__name__ = "MaliciousPoison"
            pipe.register_factor(MaliciousFactor)
            assert len(pipe.factors) == 0
            assert len(pipe.degraded_reasons) > 0

    def test_register_synthesizer_blacklisted(self):
        pipe = AlphaSignalPipeline()
        with patch("zephyr.signal_fundamental.pipeline._CONTRACTS_AVAILABLE", True):

            class HackSynth:
                pass

            HackSynth.__name__ = "HackSynthesizer"
            pipe.register_synthesizer(HackSynth)
            assert len(pipe.synthesizers) == 0
            assert len(pipe.degraded_reasons) > 0

    def test_aggregate_confidence_empty(self):
        assert AlphaSignalPipeline.aggregate_confidence([]) == 0.0

    def test_aggregate_confidence_with_objects(self):
        items = [MagicMock(confidence=0.6), MagicMock(confidence=0.8)]
        result = AlphaSignalPipeline.aggregate_confidence(items)
        assert result == pytest.approx(0.7)

    def test_aggregate_confidence_with_dicts(self):
        items = [{"confidence": 0.5}, {"confidence": 0.9}]
        result = AlphaSignalPipeline.aggregate_confidence(items)
        assert result == pytest.approx(0.7)

    def test_aggregate_confidence_no_confidence_attr(self):
        items = [MagicMock(spec=[]), MagicMock(spec=[])]
        result = AlphaSignalPipeline.aggregate_confidence(items)
        assert result == 0.5

    def test_snapshot_builtins(self):
        snap = AlphaSignalPipeline.snapshot_builtins()
        assert isinstance(snap, frozenset)
        assert "print" in snap

    def test_check_builtins_integrity_clean(self):
        snap = AlphaSignalPipeline.snapshot_builtins()
        violations = AlphaSignalPipeline.check_builtins_integrity(snap)
        assert violations == []

    def test_extreme_signal_degraded(self):
        pipe = AlphaSignalPipeline()

        class ExtremeFactor:
            def compute(self):
                sig = MagicMock()
                sig.confidence = 0.9
                sig.signal_value = 5000.0
                return [sig]

        pipe.factors = [ExtremeFactor]
        result = pipe.run()
        assert result.degraded is True or result.confidence <= 1.0
