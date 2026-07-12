# [A_test] module_id: SRC-TST-0813 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §8
# [MODULE] tests.test_e_merkle_audit
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_audit.merkle_audit import MerkleAudit, MerkleTree


class TestMerkleTree:
    def test_empty_tree_root_is_empty(self):
        mt = MerkleTree()
        assert mt.root_hash() == "empty"

    def test_add_event_produces_hash(self):
        mt = MerkleTree()
        mt.add_event({"type": "test", "id": 1})
        root = mt.root_hash()
        assert root != "empty"
        assert len(root) == 64

    def test_add_multiple_events(self):
        mt = MerkleTree()
        mt.add_event({"type": "a"})
        root1 = mt.root_hash()
        mt.add_event({"type": "b"})
        root2 = mt.root_hash()
        assert root1 != root2


class TestMerkleAudit:
    def test_record_returns_hash(self):
        ma = MerkleAudit()
        h = ma.record({"event": "test"})
        assert len(h) == 64

    def test_get_root_before_record(self):
        ma = MerkleAudit()
        assert ma.get_root() == "empty"

    def test_record_updates_root(self):
        ma = MerkleAudit()
        ma.record({"event": "test"})
        assert ma.get_root() != "empty"

    def test_multiple_records(self):
        ma = MerkleAudit()
        ma.record({"event": "e1"})
        ma.record({"event": "e2"})
        r = ma.get_root()
        assert len(r) == 64
