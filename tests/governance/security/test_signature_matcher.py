# [A_test] module_id: SRC-TST-1598 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_signature_matcher
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_signature_matcher.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_code_quality.code_dedup.signature_matcher import (
    SignatureMatch,
    SignatureMatcher,
)


class TestSignatureMatch:
    def test_default_values(self):
        sm = SignatureMatch(fingerprint="abc123")
        assert sm.fingerprint == "abc123"
        assert sm.existing == []
        assert sm.confidence == 0.0
        assert sm.level == "LOW"
        assert sm.method == "signature_collision"

    def test_custom_values(self):
        sm = SignatureMatch(
            fingerprint="def456",
            existing=["a.py::foo", "b.py::bar"],
            confidence=0.95,
            level="CRITICAL",
        )
        assert len(sm.existing) == 2
        assert sm.level == "CRITICAL"


class TestSignatureMatcher:
    def test_instantiation(self):
        sm = SignatureMatcher()
        assert sm._index == {}

    def test_compute_fingerprint_no_return(self):
        sm = SignatureMatcher()
        fp = sm.compute_fingerprint(["int", "str"])
        assert len(fp) == 12
        assert isinstance(fp, str)

    def test_compute_fingerprint_with_return(self):
        sm = SignatureMatcher()
        fp = sm.compute_fingerprint(["int", "str"], "bool")
        assert len(fp) == 12

    def test_compute_fingerprint_deterministic(self):
        sm = SignatureMatcher()
        fp1 = sm.compute_fingerprint(["int", "str"], "bool")
        fp2 = sm.compute_fingerprint(["int", "str"], "bool")
        assert fp1 == fp2

    def test_compute_fingerprint_order_independent(self):
        sm = SignatureMatcher()
        fp1 = sm.compute_fingerprint(["int", "str"])
        fp2 = sm.compute_fingerprint(["str", "int"])
        assert fp1 == fp2

    def test_compute_fingerprint_empty_params(self):
        sm = SignatureMatcher()
        fp = sm.compute_fingerprint([])
        assert len(fp) == 12

    def test_build_index_and_match(self):
        sm = SignatureMatcher()
        entries = [
            {"signature_fingerprint": "abc123", "file": "a.py", "name": "foo"},
            {"signature_fingerprint": "abc123", "file": "b.py", "name": "bar"},
            {"signature_fingerprint": "def456", "file": "c.py", "name": "baz"},
        ]
        sm.build_index(entries)
        result = sm.match("abc123", "src/shared/a.py")
        assert result is not None
        assert len(result.existing) == 2
        assert result.level == "CRITICAL"

    def test_match_no_collision(self):
        sm = SignatureMatcher()
        sm.build_index([{"signature_fingerprint": "abc123", "file": "a.py", "name": "foo"}])
        result = sm.match("zzz999", "some/path.py")
        assert result is None

    def test_match_path_classification_tests(self):
        sm = SignatureMatcher()
        sm.build_index([{"signature_fingerprint": "abc123", "file": "a.py", "name": "foo"}])
        result = sm.match("abc123", "tests/test_foo.py")
        assert result is not None
        assert result.level == "LOW"

    def test_match_path_classification_default(self):
        sm = SignatureMatcher()
        sm.build_index([{"signature_fingerprint": "abc123", "file": "a.py", "name": "foo"}])
        result = sm.match("abc123", "src/utils/helper.py")
        assert result is not None
        assert result.level == "MEDIUM"

    def test_match_bulk(self):
        sm = SignatureMatcher()
        sm.build_index(
            [
                {"signature_fingerprint": "abc123", "file": "a.py", "name": "foo"},
                {"signature_fingerprint": "def456", "file": "b.py", "name": "bar"},
            ]
        )
        results = sm.match_bulk([("abc123", "a.py"), ("def456", "b.py"), ("zzz", "c.py")])
        assert len(results) == 2

    def test_match_bulk_empty(self):
        sm = SignatureMatcher()
        results = sm.match_bulk([])
        assert results == []

    def test_extract_signature_valid(self):
        src = "def foo(x: int, y: str) -> bool:\n    return True\n"
        params, ret = SignatureMatcher.extract_signature(src)
        assert "int" in params
        assert "str" in params
        assert ret == "bool"

    def test_extract_signature_no_annotations(self):
        src = "def foo(x, y):\n    pass\n"
        params, ret = SignatureMatcher.extract_signature(src)
        assert all(p == "Any" for p in params)
        assert ret == ""

    def test_extract_signature_syntax_error(self):
        src = "def broken(:\n"
        params, ret = SignatureMatcher.extract_signature(src)
        assert params == []
        assert ret == ""

    def test_extract_signature_empty(self):
        params, ret = SignatureMatcher.extract_signature("")
        assert params == []
        assert ret == ""

    def test_build_index_clears_previous(self):
        sm = SignatureMatcher()
        sm.build_index([{"signature_fingerprint": "abc", "file": "a.py", "name": "foo"}])
        assert sm.match("abc", "a.py") is not None
        sm.build_index([])
        assert sm.match("abc", "a.py") is None

    def test_classify_path_core(self):
        assert SignatureMatcher._classify_path("src/core/engine.py") == "HIGH"
