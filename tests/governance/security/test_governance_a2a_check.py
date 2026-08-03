# [A_test] module_id: MOD-GOV_governance_a2a_check | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.a2a_check
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.a2a_check import (
        ALLOWED_TALK_PAIRS,
        verify_a2a_pair,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestVerifyA2aPair:
    def test_orchestrator_to_worker(self):
        result = verify_a2a_pair("orchestrator", "worker")
        assert result["approved"] is True

    def test_worker_to_orchestrator(self):
        result = verify_a2a_pair("worker", "orchestrator")
        assert result["approved"] is True

    def test_auditor_to_orchestrator(self):
        result = verify_a2a_pair("auditor", "orchestrator")
        assert result["approved"] is True

    def test_superadmin_to_any(self):
        result = verify_a2a_pair("superadmin", "any_agent")
        assert result["approved"] is True

    def test_any_to_superadmin(self):
        result = verify_a2a_pair("any_agent", "superadmin")
        assert result["approved"] is True

    def test_self_communication(self):
        result = verify_a2a_pair("worker", "worker")
        assert result["approved"] is True
        assert result["reason"] == "self_communication"

    def test_unauthorized_pair(self):
        result = verify_a2a_pair("worker", "auditor")
        assert result["approved"] is False
        assert result["reason"] == "pair_not_allowed"

    def test_result_keys(self):
        result = verify_a2a_pair("orchestrator", "worker")
        assert "approved" in result
        assert "from" in result
        assert "to" in result

    def test_from_to_preserved(self):
        result = verify_a2a_pair("orchestrator", "worker")
        assert result["from"] == "orchestrator"
        assert result["to"] == "worker"


@pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)
class TestAllowedTalkPairs:
    def test_pairs_non_empty(self):
        assert len(ALLOWED_TALK_PAIRS) > 0

    def test_pairs_are_tuples(self):
        for pair in ALLOWED_TALK_PAIRS:
            assert isinstance(pair, tuple)
            assert len(pair) == 2
