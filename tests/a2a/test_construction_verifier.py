# [A_test] module_id: MOD-GOV_construction_verifier | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_construction_verifier
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.construction_verifier",
    reason="construction_verifier module not available",
)


class TestConstructionVerifier:
    def test_instantiation(self):
        obj = mod.ConstructionVerifier()
        assert obj is not None

    def test_verify(self):
        obj = mod.ConstructionVerifier()
        result = obj.verify("task_1", output={"status": "done"})
        assert isinstance(result, dict)

    def test_verify_warn_only(self):
        obj = mod.ConstructionVerifier()
        result = obj.verify("task_1", output={"status": "done"}, _warn_only=True)
        assert isinstance(result, dict)

    def test_verify_empty_output(self):
        obj = mod.ConstructionVerifier()
        result = obj.verify("task_1", output={})
        assert isinstance(result, dict)


class TestVerifierResult:
    def test_instantiation(self):
        result = mod.VerifierResult(passed=True)
        assert result is not None
        assert result.passed is True

    def test_instantiation_failed(self):
        result = mod.VerifierResult(passed=False)
        assert result.passed is False


class TestStubAnalysis:
    def test_instantiation(self):
        analysis = mod.StubAnalysis(
            file_name="test.py", line_count=10, class_count=1, method_count=2, is_empty_stub=False
        )
        assert analysis is not None
        assert analysis.file_name == "test.py"
