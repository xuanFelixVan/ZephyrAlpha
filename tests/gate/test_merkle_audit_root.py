# [A_test] module_id: SRC-TST-1260 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §
# [MODULE] tests.test_merkle_audit_root
# [INVARIANTS] Merkle hash must be deterministic for same input
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

import hashlib

from zephyr.feedback_loop.gates.merkle_audit_root import MerkleAuditRoot


class TestMerkleAuditRootInstantiation:
    def test_default_root_hash(self):
        mar = MerkleAuditRoot()
        assert mar.root_hash == ""

    def test_custom_root_hash(self):
        mar = MerkleAuditRoot(root_hash="abc123")
        assert mar.root_hash == "abc123"


class TestCompute:
    def test_compute_returns_sha256_hex(self):
        mar = MerkleAuditRoot()
        entries = ["entry1", "entry2"]
        expected = hashlib.sha256("|".join(entries).encode()).hexdigest()
        assert mar.compute(entries) == expected

    def test_compute_deterministic(self):
        mar = MerkleAuditRoot()
        entries = ["a", "b", "c"]
        assert mar.compute(entries) == mar.compute(entries)

    def test_compute_different_entries_different_hash(self):
        mar = MerkleAuditRoot()
        hash1 = mar.compute(["a"])
        hash2 = mar.compute(["b"])
        assert hash1 != hash2

    def test_compute_empty_list(self):
        mar = MerkleAuditRoot()
        result = mar.compute([])
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_compute_single_entry(self):
        mar = MerkleAuditRoot()
        result = mar.compute(["only"])
        expected = hashlib.sha256(b"only").hexdigest()
        assert result == expected

    def test_compute_order_matters(self):
        mar = MerkleAuditRoot()
        hash1 = mar.compute(["a", "b"])
        hash2 = mar.compute(["b", "a"])
        assert hash1 != hash2
