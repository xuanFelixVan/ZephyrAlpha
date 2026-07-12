# [A_test] module_id: SRC-TST-0827 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_embedding_version_lock
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_embedding_version_lock.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.gov_kb.embedding_version_lock import EmbeddingVersionInfo, EmbeddingVersionLock


class TestEmbeddingVersionInfo:
    def test_instantiation_with_all_fields(self):
        evi = EmbeddingVersionInfo(
            model_name="test-model",
            model_version="2.0.0",
            ke_count=100,
            needs_regression_test=True,
        )
        assert evi.model_name == "test-model"
        assert evi.model_version == "2.0.0"
        assert evi.ke_count == 100
        assert evi.needs_regression_test is True

    def test_instantiation_defaults(self):
        evi = EmbeddingVersionInfo(model_name="m", model_version="1.0", ke_count=0, needs_regression_test=False)
        assert evi.ke_count == 0
        assert evi.needs_regression_test is False

    def test_equality(self):
        a = EmbeddingVersionInfo(model_name="x", model_version="1", ke_count=0, needs_regression_test=False)
        b = EmbeddingVersionInfo(model_name="x", model_version="1", ke_count=0, needs_regression_test=False)
        assert a == b


class TestEmbeddingVersionLock:
    def test_instantiation(self):
        evl = EmbeddingVersionLock()
        assert evl is not None

    def test_get_version_returns_embedding_version_info(self):
        evl = EmbeddingVersionLock()
        result = evl.get_version()
        assert isinstance(result, EmbeddingVersionInfo)

    def test_get_version_model_name(self):
        evl = EmbeddingVersionLock()
        result = evl.get_version()
        assert result.model_name == "all-MiniLM-L6-v2"

    def test_get_version_model_version(self):
        evl = EmbeddingVersionLock()
        result = evl.get_version()
        assert result.model_version == "1.0.0"

    def test_get_version_ke_count_is_zero(self):
        evl = EmbeddingVersionLock()
        result = evl.get_version()
        assert result.ke_count == 0

    def test_get_version_needs_regression_test_is_false(self):
        evl = EmbeddingVersionLock()
        result = evl.get_version()
        assert result.needs_regression_test is False

    def test_detect_change_same_model_same_version_returns_false(self):
        evl = EmbeddingVersionLock()
        assert evl.detect_change("all-MiniLM-L6-v2", "1.0.0") is False

    def test_detect_change_different_model_returns_true(self):
        evl = EmbeddingVersionLock()
        assert evl.detect_change("text-embedding-ada-002", "1.0.0") is True

    def test_detect_change_different_version_returns_true(self):
        evl = EmbeddingVersionLock()
        assert evl.detect_change("all-MiniLM-L6-v2", "2.0.0") is True

    def test_detect_change_both_different_returns_true(self):
        evl = EmbeddingVersionLock()
        assert evl.detect_change("other-model", "3.0.0") is True

    def test_detect_change_empty_model_returns_true(self):
        evl = EmbeddingVersionLock()
        assert evl.detect_change("", "1.0.0") is True

    def test_detect_change_empty_version_returns_true(self):
        evl = EmbeddingVersionLock()
        assert evl.detect_change("all-MiniLM-L6-v2", "") is True
