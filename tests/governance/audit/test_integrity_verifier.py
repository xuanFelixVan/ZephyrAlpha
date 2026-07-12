# [A_test] module_id: SRC-TST-1140 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_integrity_verifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_integrity_verifier.py -q
# [TTL] task_bound

from __future__ import annotations

import hashlib

from zephyr.gov_audit.integrity_verifier import IntegrityVerifier


class TestIntegrityVerifierInstantiation:
    def test_creates_instance_with_empty_hashes(self):
        verifier = IntegrityVerifier()
        assert verifier._hashes == {}

    def test_hashes_attribute_is_dict(self):
        verifier = IntegrityVerifier()
        assert isinstance(verifier._hashes, dict)


class TestRegisterHash:
    def test_register_hash_stores_sha256(self):
        verifier = IntegrityVerifier()
        content = "hello world"
        expected = hashlib.sha256(content.encode()).hexdigest()
        verifier.register_hash("file.py", content)
        assert verifier._hashes["file.py"] == expected

    def test_register_hash_overwrites_previous(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("file.py", "v1")
        verifier.register_hash("file.py", "v2")
        expected = hashlib.sha256(b"v2").hexdigest()
        assert verifier._hashes["file.py"] == expected

    def test_register_hash_multiple_files(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("a.py", "alpha")
        verifier.register_hash("b.py", "beta")
        assert len(verifier._hashes) == 2
        assert "a.py" in verifier._hashes
        assert "b.py" in verifier._hashes

    def test_register_hash_empty_content(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("empty.py", "")
        expected = hashlib.sha256(b"").hexdigest()
        assert verifier._hashes["empty.py"] == expected

    def test_register_hash_unicode_content(self):
        verifier = IntegrityVerifier()
        content = "中文内容 🚀"
        expected = hashlib.sha256(content.encode()).hexdigest()
        verifier.register_hash("unicode.py", content)
        assert verifier._hashes["unicode.py"] == expected


class TestVerify:
    def test_verify_returns_true_when_content_matches(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("file.py", "original")
        assert verifier.verify("file.py", "original") is True

    def test_verify_returns_false_when_content_differs(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("file.py", "original")
        assert verifier.verify("file.py", "modified") is False

    def test_verify_returns_true_for_unregistered_filepath(self):
        verifier = IntegrityVerifier()
        assert verifier.verify("unknown.py", "anything") is True

    def test_verify_returns_false_for_tampered_content(self):
        verifier = IntegrityVerifier()
        original = "line1\nline2\nline3"
        verifier.register_hash("data.yaml", original)
        tampered = "line1\nTAMPERED\nline3"
        assert verifier.verify("data.yaml", tampered) is False

    def test_verify_handles_empty_string(self):
        verifier = IntegrityVerifier()
        verifier.register_hash("empty.py", "")
        assert verifier.verify("empty.py", "") is True
        assert verifier.verify("empty.py", "x") is False

    def test_verify_handles_unicode(self):
        verifier = IntegrityVerifier()
        content = "日本語テスト"
        verifier.register_hash("jp.py", content)
        assert verifier.verify("jp.py", content) is True
        assert verifier.verify("jp.py", "別の内容") is False


class TestDiffFiles:
    def test_diff_files_detects_added_lines(self):
        verifier = IntegrityVerifier()
        old = "line1\nline2"
        new = "line1\nline2\nline3"
        diffs = verifier.diff_files("f.py", old, new)
        assert any("+line3" in d for d in diffs)

    def test_diff_files_detects_removed_lines(self):
        verifier = IntegrityVerifier()
        old = "line1\nline2\nline3"
        new = "line1\nline3"
        diffs = verifier.diff_files("f.py", old, new)
        assert any("-line2" in d for d in diffs)

    def test_diff_files_no_changes(self):
        verifier = IntegrityVerifier()
        content = "line1\nline2"
        diffs = verifier.diff_files("f.py", content, content)
        assert diffs == []

    def test_diff_files_caps_at_50(self):
        verifier = IntegrityVerifier()
        old_lines = [f"old{i}" for i in range(100)]
        new_lines = [f"new{i}" for i in range(100)]
        old = "\n".join(old_lines)
        new = "\n".join(new_lines)
        diffs = verifier.diff_files("f.py", old, new)
        assert len(diffs) == 50

    def test_diff_files_empty_old_content(self):
        verifier = IntegrityVerifier()
        new = "line1\nline2"
        diffs = verifier.diff_files("f.py", "", new)
        assert all(d.startswith("+") for d in diffs)

    def test_diff_files_empty_new_content(self):
        verifier = IntegrityVerifier()
        old = "line1\nline2"
        diffs = verifier.diff_files("f.py", old, "")
        assert all(d.startswith("-") for d in diffs)

    def test_diff_files_mixed_additions_and_removals(self):
        verifier = IntegrityVerifier()
        old = "alpha\nbeta\ngamma"
        new = "alpha\ndelta\ngamma"
        diffs = verifier.diff_files("f.py", old, new)
        added = [d for d in diffs if d.startswith("+")]
        removed = [d for d in diffs if d.startswith("-")]
        assert len(added) >= 1
        assert len(removed) >= 1
