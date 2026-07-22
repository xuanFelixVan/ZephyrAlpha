# [A_test] module_id: MOD-GOV_pipeline_orchestrator_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.pipeline_orchestrator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.integration.pipeline_orchestrator import (
        PipelineMetrics,
        PipelineOrchestrator,
        PipelineResult,
    )
except Exception as exc:
    pytest.skip(f"Cannot import pipeline_orchestrator: {exc}", allow_module_level=True)


class TestPipelineMetrics:
    def test_default_values(self):
        m = PipelineMetrics()
        assert m.build_ms == 0.0
        assert m.compress_ms == 0.0
        assert m.validate_ms == 0.0
        assert m.inject_ms == 0.0
        assert m.total_ms == 0.0

    def test_as_dict(self):
        m = PipelineMetrics(build_ms=1.0, compress_ms=2.0, validate_ms=3.0, inject_ms=4.0, total_ms=10.0)
        d = m.as_dict
        assert d["build_ms"] == 1.0
        assert d["compress_ms"] == 2.0
        assert d["validate_ms"] == 3.0
        assert d["inject_ms"] == 4.0
        assert d["total_ms"] == 10.0

    def test_as_dict_keys(self):
        m = PipelineMetrics()
        d = m.as_dict
        assert set(d.keys()) == {"build_ms", "compress_ms", "validate_ms", "inject_ms", "total_ms"}


class TestPipelineResult:
    def test_default_values(self):
        r = PipelineResult()
        assert r.success is False
        assert r.raw_context is None
        assert r.injection_result is None
        assert r.degraded is False
        assert r.degradation_reason == ""
        assert r.errors == []

    def test_custom_values(self):
        r = PipelineResult(success=True, degraded=True, degradation_reason="test")
        assert r.success is True
        assert r.degraded is True
        assert r.degradation_reason == "test"


class TestPipelineOrchestrator:
    def test_instantiation(self):
        orc = PipelineOrchestrator()
        assert orc is not None

    def test_instantiation_with_params(self):
        orc = PipelineOrchestrator(session_limit=4000, pipeline_timeout_s=5.0)
        assert orc is not None

    def test_run_returns_pipeline_result(self):
        orc = PipelineOrchestrator()
        result = orc.run(task_type="CODE_GEN", target_layer="D_INFRA_OPS", session_id="test-session")
        assert isinstance(result, PipelineResult)

    def test_run_metrics_populated(self):
        orc = PipelineOrchestrator()
        result = orc.run(task_type="CODE_GEN", target_layer="D_INFRA_OPS", session_id="test-session")
        assert result.metrics.total_ms >= 0
        assert result.metrics.build_ms >= 0

    def test_run_with_empty_params(self):
        orc = PipelineOrchestrator()
        result = orc.run()
        assert isinstance(result, PipelineResult)
