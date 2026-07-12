# [A_test] module_id: SRC-TST-1393 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_pre_apply_integrity_gate
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
import hashlib

from zephyr.gov_code_quality.code_dedup.pre_apply_integrity_gate import PreApplyIntegrityGate


class TestPreApplyIntegrityGate:
    def test_instantiation(self):
        gate = PreApplyIntegrityGate()
        assert gate is not None

    def test_verify_returns_tuple(self, tmp_path):
        gate = PreApplyIntegrityGate()
        f = tmp_path / "test.py"
        f.write_text("x = 1", encoding="utf-8")
        expected = hashlib.sha256(b"x = 1").hexdigest()
        result = gate.verify(str(f), expected)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is True
        assert result[1] == "SHA256_OK"

    def test_verify_mismatch(self, tmp_path):
        gate = PreApplyIntegrityGate()
        f = tmp_path / "test.py"
        f.write_text("x = 1", encoding="utf-8")
        result = gate.verify(str(f), "wrong_hash")
        assert result[0] is False
        assert "SHA_MISMATCH" in result[1]

    def test_verify_nonexistent_file(self):
        gate = PreApplyIntegrityGate()
        result = gate.verify("nonexistent.py", "abc123")
        assert result[0] is False
        assert "FILE_NOT_FOUND" in result[1]
