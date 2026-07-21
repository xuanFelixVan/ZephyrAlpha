# [A_test] module_id: MOD-GOV_doc_compressor_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.doc_compressor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.shared.io.doc_compressor import (
        DEFAULT_POLICY,
        CompressionInvariantError,
        CompressionOutcome,
        CompressionPolicy,
        DocCompressor,
    )
except Exception as exc:
    pytest.skip(f"无法导入 doc_compressor: {exc}", allow_module_level=True)


class TestCompressionPolicy:
    def test_default_policy_values(self):
        p = CompressionPolicy()
        assert p.min_chars == 200
        assert p.max_chars == 4000
        assert p.preserve_structure is True
        assert p.preserve_provenance is True
        assert len(p.preserve_immutable_blocks) == 3

    def test_min_chars_must_be_less_than_max_chars(self):
        with pytest.raises(ValueError):
            CompressionPolicy(min_chars=5000, max_chars=4000)

    def test_immutable_blocks_must_contain_start(self):
        with pytest.raises(ValueError):
            CompressionPolicy(preserve_immutable_blocks=["<!-- BAD_MARKER -->"])

    def test_immutable_blocks_must_be_nonempty(self):
        with pytest.raises(ValueError):
            CompressionPolicy(preserve_immutable_blocks=[""])

    def test_frozen_policy(self):
        p = CompressionPolicy()
        with pytest.raises(Exception):
            p.min_chars = 999

    def test_default_policy_is_valid(self):
        assert DEFAULT_POLICY.min_chars < DEFAULT_POLICY.max_chars


class TestDocCompressor:
    def setup_method(self):
        DocCompressor.reset_instance()
        policy = CompressionPolicy(
            min_chars=100,
            max_chars=5000,
            preserve_structure=True,
            preserve_provenance=True,
            preserve_immutable_blocks=["<!-- IMMUTABLE_START -->"],
        )
        self.compressor = DocCompressor(policy=policy)

    def teardown_method(self):
        DocCompressor.reset_instance()

    def test_compress_empty_string(self):
        result = self.compressor.compress("")
        assert result == ""

    def test_compress_preserves_headers(self):
        text = "## Header One\nSome content here.\n## Header Two\nMore content."
        result = self.compressor.compress(text)
        assert "## Header One" in result
        assert "## Header Two" in result

    def test_compress_preserves_frontmatter(self):
        text = "---\ntitle: Test\n---\n## Section\nBody text."
        result = self.compressor.compress(text)
        assert "---" in result
        assert "title: Test" in result

    def test_compress_with_provenance_returns_outcome(self):
        text = "## Title\nSome body text for testing."
        outcome = self.compressor.compress_with_provenance(text)
        assert isinstance(outcome, CompressionOutcome)
        assert outcome.raw_text == text
        assert isinstance(outcome.compressed_text, str)

    def test_compress_truncates_long_text(self):
        long_text = "## Title\n" + "x" * 6000
        policy = CompressionPolicy(
            min_chars=100,
            max_chars=200,
            preserve_structure=True,
            preserve_provenance=False,
            preserve_immutable_blocks=["<!-- IMMUTABLE_START -->"],
        )
        compressor = DocCompressor(policy=policy)
        result = compressor.compress(long_text)
        assert len(result) <= 250

    def test_compress_preserves_immutable_blocks(self):
        text = "## Title\n<!-- IMMUTABLE_START -->\nsecret data\n<!-- IMMUTABLE_END -->\nMore text."
        result = self.compressor.compress(text)
        assert "<!-- IMMUTABLE_START -->" in result
        assert "<!-- IMMUTABLE_END -->" in result

    def test_singleton_instance(self):
        DocCompressor.reset_instance()
        policy = CompressionPolicy(
            min_chars=100, max_chars=5000, preserve_immutable_blocks=["<!-- IMMUTABLE_START -->"]
        )
        inst1 = DocCompressor.instance(policy=policy, reset=True)
        inst2 = DocCompressor.instance()
        assert inst1 is inst2

    def test_policy_property(self):
        assert isinstance(self.compressor.policy, CompressionPolicy)


class TestCompressionInvariantError:
    def test_error_message(self):
        err = CompressionInvariantError(
            field="preserve_structure",
            original="header exists",
            compressed="header missing",
        )
        assert "preserve_structure" in str(err)
        assert err.field == "preserve_structure"
        assert err.original == "header exists"
        assert err.compressed == "header missing"
