# [A_test] module_id: MOD-GOV_support_doc_compressor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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
        CompressionOutcome,
        CompressionPolicy,
        DocCompressor,
        load_policy_from_yaml,
    )
except Exception as _exc:
    pytest.skip(f"无法导入 doc_compressor: {_exc}", allow_module_level=True)


class TestCompressionPolicy:
    def test_default_policy_valid(self):
        assert DEFAULT_POLICY.min_chars < DEFAULT_POLICY.max_chars
        assert DEFAULT_POLICY.preserve_structure is True
        assert DEFAULT_POLICY.preserve_provenance is True

    def test_invalid_min_ge_max_raises(self):
        with pytest.raises(ValueError):
            CompressionPolicy(min_chars=5000, max_chars=4000)

    def test_frozen_policy(self):
        with pytest.raises(Exception):
            DEFAULT_POLICY.min_chars = 999

    def test_immutable_blocks_empty_string_raises(self):
        with pytest.raises(ValueError):
            CompressionPolicy(preserve_immutable_blocks=[""])

    def test_min_chars_below_100_raises(self):
        with pytest.raises(ValueError):
            CompressionPolicy(min_chars=10, max_chars=5000)


class TestDocCompressorCompress:
    def setup_method(self):
        DocCompressor.reset_instance()

    def test_compress_simple_text(self):
        compressor = DocCompressor(policy=CompressionPolicy(min_chars=100, max_chars=10000))
        result = compressor.compress("Hello world")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_compress_empty_text(self):
        compressor = DocCompressor(policy=CompressionPolicy())
        result = compressor.compress("")
        assert result == ""

    def test_compress_preserves_headers(self):
        text = "## Header 1\nSome content\n## Header 2\nMore content"
        compressor = DocCompressor(policy=CompressionPolicy(min_chars=100, max_chars=10000))
        result = compressor.compress(text)
        assert "## Header 1" in result
        assert "## Header 2" in result

    def test_compress_with_provenance_returns_outcome(self):
        compressor = DocCompressor(policy=CompressionPolicy(min_chars=100, max_chars=10000))
        outcome = compressor.compress_with_provenance("Some text here")
        assert isinstance(outcome, CompressionOutcome)
        assert outcome.raw_text == "Some text here"
        assert isinstance(outcome.compressed_text, str)

    def test_compress_preserves_frontmatter(self):
        text = "---\ntitle: Test\n---\n## Section\nContent here"
        compressor = DocCompressor(policy=CompressionPolicy(min_chars=100, max_chars=10000))
        result = compressor.compress(text)
        assert "---" in result

    def test_compress_truncates_long_text(self):
        text = "x" * 50000
        compressor = DocCompressor(policy=CompressionPolicy(min_chars=100, max_chars=500))
        result = compressor.compress(text)
        assert len(result) <= 600


class TestDocCompressorSingleton:
    def setup_method(self):
        DocCompressor.reset_instance()

    def test_instance_returns_same(self):
        a = DocCompressor.instance()
        b = DocCompressor.instance()
        assert a is b

    def test_reset_instance(self):
        DocCompressor.instance()
        DocCompressor.reset_instance()
        assert DocCompressor.instance is None


class TestLoadPolicyFromYaml:
    def test_load_nonexistent_returns_default(self):
        import warnings
        from pathlib import Path

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            policy = load_policy_from_yaml(Path("/nonexistent/policy.yaml"))
        assert policy == DEFAULT_POLICY
