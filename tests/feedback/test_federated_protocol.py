# [A_test] module_id: SRC-TST-0898 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_federated_protocol
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_federated_protocol.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.verifiers.federated_protocol import FederatedProtocol


class TestFederatedProtocolInstantiation:
    def test_default_construction(self):
        fp = FederatedProtocol()
        assert fp.instance_id == ""
        assert fp.peers == []

    def test_custom_construction(self):
        fp = FederatedProtocol(instance_id="fle-1", peers=["fle-2", "fle-3"])
        assert fp.instance_id == "fle-1"
        assert len(fp.peers) == 2

    def test_empty_instance_id(self):
        fp = FederatedProtocol(instance_id="")
        assert fp.instance_id == ""

    def test_empty_peers(self):
        fp = FederatedProtocol(peers=[])
        assert fp.peers == []

    def test_peers_mutable_default(self):
        fp1 = FederatedProtocol()
        fp2 = FederatedProtocol()
        fp1.peers.append("fle-x")
        assert "fle-x" not in fp2.peers
