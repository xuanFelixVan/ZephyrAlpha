# [A_test] module_id: SRC-TST-0961 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_federated_security
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.federated_security
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_federated_security.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.federated_security import FederatedSecurity


class TestFederatedSecurityInstantiation:
    def test_default_construction(self):
        fs = FederatedSecurity()
        assert fs.trusted_peers == set()


class TestVerifyPeer:
    def test_verify_trusted_peer(self):
        fs = FederatedSecurity(trusted_peers={"peer-1", "peer-2"})
        assert fs.verify_peer("peer-1") is True

    def test_verify_untrusted_peer(self):
        fs = FederatedSecurity(trusted_peers={"peer-1"})
        assert fs.verify_peer("peer-unknown") is False

    def test_verify_empty_peers(self):
        fs = FederatedSecurity()
        assert fs.verify_peer("any-peer") is False


class TestBoundaries:
    def test_verify_empty_string_peer(self):
        fs = FederatedSecurity(trusted_peers={""})
        assert fs.verify_peer("") is True

    def test_verify_none_peer_returns_false(self):
        fs = FederatedSecurity(trusted_peers={"peer-1"})
        assert fs.verify_peer(None) is False
