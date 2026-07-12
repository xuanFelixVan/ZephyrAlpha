# [A_test] module_id: SRC-TST-1259 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_merkle_audit
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_merkle_audit.py -q
# [TTL] task_bound

import hashlib
import json

from zephyr.gov_audit.merkle_audit import MerkleAudit, MerkleTree


class TestMerkleTreeInstantiation:
    def test_creates_instance_with_empty_leaves(self):
        tree = MerkleTree()
        assert isinstance(tree, MerkleTree)
        assert tree._leaves == []


class TestMerkleTreeAddEvent:
    def test_add_event_appends_sha256_leaf(self):
        tree = MerkleTree()
        event = {"action": "escalate", "rule_id": "R-001"}
        tree.add_event(event)
        assert len(tree._leaves) == 1
        expected = hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()
        assert tree._leaves[0] == expected

    def test_add_multiple_events(self):
        tree = MerkleTree()
        tree.add_event({"a": 1})
        tree.add_event({"b": 2})
        tree.add_event({"c": 3})
        assert len(tree._leaves) == 3


class TestMerkleTreeRootHash:
    def test_root_hash_empty_tree(self):
        tree = MerkleTree()
        assert tree.root_hash() == "empty"

    def test_root_hash_single_leaf(self):
        tree = MerkleTree()
        tree.add_event({"x": 1})
        root = tree.root_hash()
        assert isinstance(root, str)
        assert len(root) > 0
        assert root != "empty"

    def test_root_hash_multiple_leaves(self):
        tree = MerkleTree()
        tree.add_event({"a": 1})
        tree.add_event({"b": 2})
        root = tree.root_hash()
        assert isinstance(root, str)
        assert len(root) == 64

    def test_root_hash_changes_after_add(self):
        tree = MerkleTree()
        tree.add_event({"a": 1})
        root1 = tree.root_hash()
        tree.add_event({"b": 2})
        root2 = tree.root_hash()
        assert root1 != root2


class TestMerkleAuditInstantiation:
    def test_creates_instance(self):
        audit = MerkleAudit()
        assert isinstance(audit, MerkleAudit)
        assert isinstance(audit._tree, MerkleTree)


class TestMerkleAuditRecord:
    def test_record_returns_root_hash(self):
        audit = MerkleAudit()
        result = audit.record({"event": "test"})
        assert isinstance(result, str)
        assert result != "empty"

    def test_record_multiple_events(self):
        audit = MerkleAudit()
        r1 = audit.record({"event": "first"})
        r2 = audit.record({"event": "second"})
        assert r1 != r2


class TestMerkleAuditGetRoot:
    def test_get_root_empty(self):
        audit = MerkleAudit()
        assert audit.get_root() == "empty"

    def test_get_root_after_record(self):
        audit = MerkleAudit()
        audit.record({"event": "test"})
        root = audit.get_root()
        assert root != "empty"

    def test_get_root_matches_record_return(self):
        audit = MerkleAudit()
        returned = audit.record({"event": "test"})
        assert audit.get_root() == returned


class TestBoundary:
    def test_large_event_dict(self):
        tree = MerkleTree()
        event = {f"key_{i}": i for i in range(1000)}
        tree.add_event(event)
        root = tree.root_hash()
        assert isinstance(root, str)
        assert len(root) == 64

    def test_nested_event_dict(self):
        tree = MerkleTree()
        event = {"outer": {"inner": {"deep": "value"}}}
        tree.add_event(event)
        root = tree.root_hash()
        assert isinstance(root, str)
        assert len(root) == 64

    def test_event_with_unicode_values(self):
        tree = MerkleTree()
        event = {"action": "升级", "详情": "模型版本突变"}
        tree.add_event(event)
        root = tree.root_hash()
        assert isinstance(root, str)
        assert len(root) == 64
