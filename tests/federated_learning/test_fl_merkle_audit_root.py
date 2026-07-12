# [A_test] module_id: SRC-TST-0972 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_merkle_audit_root
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.gates.merkle_audit_root
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_merkle_audit_root.py
# [TTL] task_bound

from zephyr.feedback_loop.gates.merkle_audit_root import MerkleAuditRoot


class TestMerkleAuditRootInstantiation:
    def test_default_construction(self):
        mar = MerkleAuditRoot()
        assert mar.root_hash == ""


class TestCompute:
    def test_compute_returns_hex_string(self):
        mar = MerkleAuditRoot()
        result = mar.compute(["entry1", "entry2"])
        assert isinstance(result, str)
        assert len(result) == 64

    def test_compute_deterministic(self):
        mar = MerkleAuditRoot()
        entries = ["a", "b", "c"]
        assert mar.compute(entries) == mar.compute(entries)

    def test_compute_different_entries_different_hash(self):
        mar = MerkleAuditRoot()
        h1 = mar.compute(["entry1"])
        h2 = mar.compute(["entry2"])
        assert h1 != h2

    def test_compute_order_matters(self):
        mar = MerkleAuditRoot()
        h1 = mar.compute(["a", "b"])
        h2 = mar.compute(["b", "a"])
        assert h1 != h2


class TestBoundaries:
    def test_compute_empty_list(self):
        mar = MerkleAuditRoot()
        result = mar.compute([])
        assert isinstance(result, str)
        assert len(result) == 64

    def test_compute_single_entry(self):
        mar = MerkleAuditRoot()
        result = mar.compute(["only_entry"])
        assert isinstance(result, str)
        assert len(result) == 64
