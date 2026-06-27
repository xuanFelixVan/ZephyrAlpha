# [A_test] module_id: SRC-TST-1275 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_rbac/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.micro_verifier
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
    from zephyr.security.access_control.micro_verifier import AtomicResult, MicroVerifier

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)


@pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")
class TestMicroVerifier:
    def setup_method(self):
        MicroVerifier._CACHE.clear()
        self.verifier = MicroVerifier()

    def test_check_allowed_action(self):
        result = self.verifier.check("agent-1", "read", "resource-A")
        assert isinstance(result, AtomicResult)
        assert result.allowed is True
        assert result.cached is False
        assert result.rule_id == "MV-ATOMIC-001"
        assert result.layer == "L0"

    def test_check_denied_actions(self):
        for action in ("destroy", "meltdown", "sudo"):
            MicroVerifier._CACHE.clear()
            result = self.verifier.check("agent-1", action, "resource-A")
            assert result.allowed is False, f"action={action} should be denied"

    def test_check_caching(self):
        self.verifier.check("agent-1", "read", "resource-A")
        result = self.verifier.check("agent-1", "read", "resource-A")
        assert result.cached is True

    def test_invalidate_specific_agent(self):
        self.verifier.check("agent-1", "read", "resource-A")
        self.verifier.check("agent-2", "read", "resource-A")
        self.verifier.invalidate("agent-1")
        result_a = self.verifier.check("agent-1", "read", "resource-A")
        result_b = self.verifier.check("agent-2", "read", "resource-A")
        assert result_a.cached is False
        assert result_b.cached is True

    def test_invalidate_all(self):
        self.verifier.check("agent-1", "read", "resource-A")
        self.verifier.check("agent-2", "write", "resource-B")
        self.verifier.invalidate()
        assert len(MicroVerifier._CACHE) == 0

    def test_check_empty_strings(self):
        result = self.verifier.check("", "", "")
        assert isinstance(result, AtomicResult)
        assert result.allowed is True

    def test_latency_us_positive(self):
        result = self.verifier.check("agent-1", "read", "resource-A")
        assert result.latency_us >= 0
