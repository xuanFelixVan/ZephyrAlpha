# [A_test] module_id: SRC-TST-0899 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_federated_security
# [INVARIANTS] Peer verification must be deterministic
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound


from zephyr.feedback_loop.gates.federated_security import FederatedSecurity


class TestFederatedSecurityInstantiation:
    def test_default_empty_peers(self):
        fs = FederatedSecurity()
        assert fs.trusted_peers == set()

    def test_custom_trusted_peers(self):
        fs = FederatedSecurity(trusted_peers={"peer-1", "peer-2"})
        assert len(fs.trusted_peers) == 2


class TestVerifyPeer:
    def test_trusted_peer_returns_true(self):
        fs = FederatedSecurity(trusted_peers={"peer-1"})
        assert fs.verify_peer("peer-1") is True

    def test_untrusted_peer_returns_false(self):
        fs = FederatedSecurity(trusted_peers={"peer-1"})
        assert fs.verify_peer("peer-unknown") is False

    def test_empty_trusted_set(self):
        fs = FederatedSecurity()
        assert fs.verify_peer("any-peer") is False

    def test_empty_string_peer(self):
        fs = FederatedSecurity(trusted_peers={""})
        assert fs.verify_peer("") is True

    def test_multiple_trusted_peers(self):
        fs = FederatedSecurity(trusted_peers={"a", "b", "c"})
        assert fs.verify_peer("b") is True
        assert fs.verify_peer("d") is False
