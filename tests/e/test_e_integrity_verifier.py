# [A_test] module_id: SRC-TST-0811 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_integrity_verifier
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

from zephyr.gov_audit.integrity_verifier import IntegrityVerifier


class TestIntegrityVerifierInit:
    def test_default_state(self):
        verifier = IntegrityVerifier()
        assert verifier._hashes == {}


class TestIntegrityVerifierRegisterHash:
    def test_register_stores_hash(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("/path/to/file.py", "content")
        assert "/path/to/file.py" in verifier._hashes
        assert len(verifier._hashes["/path/to/file.py"]) == 64

    def test_register_multiple_files(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("a.py", "a")
        verifier.register_hash("b.py", "b")
        assert len(verifier._hashes) == 2

    def test_register_overwrites(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("f.py", "old")
        old_hash = verifier._hashes["f.py"]
        verifier.register_hash("f.py", "new")
        assert verifier._hashes["f.py"] != old_hash


class TestIntegrityVerifierVerify:
    def test_unregistered_file_passes(self):
        verifier = IntegrityVerifier()
        assert verifier.verify("f.py", "any") is True

    def test_identical_content_passes(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("f.py", "same")
        assert verifier.verify("f.py", "same") is True

    def test_different_content_fails(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("f.py", "original")
        assert verifier.verify("f.py", "modified") is False


class TestIntegrityVerifierDiffFiles:
    def test_empty_diff(self):
        verifier = IntegrityVerifier()
        diffs = verifier.diff_files("f.py", "line1\nline2", "line1\nline2")
        assert diffs == []

    def test_added_lines(self):
        verifier = IntegrityVerifier()
        diffs = verifier.diff_files("f.py", "line1", "line1\nline2")
        assert "+line2" in diffs

    def test_removed_lines(self):
        verifier = IntegrityVerifier()
        diffs = verifier.diff_files("f.py", "line1\nline2", "line1")
        assert "-line2" in diffs

    def test_both_added_and_removed(self):
        verifier = IntegrityVerifier()
        diffs = verifier.diff_files("f.py", "line1\nline2", "line1\nline3")
        assert "-line2" in diffs
        assert "+line3" in diffs

    def test_truncated_at_50(self):
        verifier = IntegrityVerifier()
        old_lines = "\n".join(f"old{i}" for i in range(100))
        new_lines = "\n".join(f"new{i}" for i in range(100))
        diffs = verifier.diff_files("f.py", old_lines, new_lines)
        assert len(diffs) == 50
