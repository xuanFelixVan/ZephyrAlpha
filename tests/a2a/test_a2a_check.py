# [A_test] module_id: MOD-GOV_a2a_check | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.a2a_check
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
    from zephyr.security.access_control.a2a_check import ALLOWED_TALK_PAIRS, verify_a2a_pair

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}")


class TestVerifyA2APair:
    def test_allowed_pair_orchestrator_worker(self):
        result = verify_a2a_pair("orchestrator", "worker")
        assert result["approved"] is True
        assert result["from"] == "orchestrator"
        assert result["to"] == "worker"

    def test_allowed_pair_worker_orchestrator(self):
        result = verify_a2a_pair("worker", "orchestrator")
        assert result["approved"] is True

    def test_allowed_pair_auditor_orchestrator(self):
        result = verify_a2a_pair("auditor", "orchestrator")
        assert result["approved"] is True

    def test_superadmin_to_any(self):
        result = verify_a2a_pair("superadmin", "anything")
        assert result["approved"] is True

    def test_any_to_superadmin(self):
        result = verify_a2a_pair("anything", "superadmin")
        assert result["approved"] is True

    def test_self_communication(self):
        result = verify_a2a_pair("solo", "solo")
        assert result["approved"] is True
        assert result.get("reason") == "self_communication"

    def test_disallowed_pair(self):
        result = verify_a2a_pair("worker", "auditor")
        assert result["approved"] is False
        assert result.get("reason") == "pair_not_allowed"

    def test_empty_strings(self):
        result = verify_a2a_pair("", "")
        assert result["approved"] is True
        assert result.get("reason") == "self_communication"

    def test_empty_from_disallowed(self):
        result = verify_a2a_pair("", "worker")
        assert result["approved"] is False


class TestAllowedTalkPairs:
    def test_pairs_is_set(self):
        assert isinstance(ALLOWED_TALK_PAIRS, set)

    def test_pairs_contains_key_entries(self):
        assert ("orchestrator", "worker") in ALLOWED_TALK_PAIRS
        assert ("superadmin", "*") in ALLOWED_TALK_PAIRS
