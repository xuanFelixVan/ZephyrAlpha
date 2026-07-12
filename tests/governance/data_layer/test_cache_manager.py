# [A_test] module_id: SRC-TST-0480 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_cache_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.cache_manager import (
    CacheManager,
    FunctionCache,
)


class TestCacheManager:
    def test_instantiation_default(self):
        cm = CacheManager()
        assert cm is not None

    def test_instantiation_with_path(self, tmp_path):
        cm = CacheManager(cache_path=str(tmp_path / "cache.json"))
        assert cm is not None

    def test_load_returns_function_cache(self, tmp_path):
        cm = CacheManager(cache_path=str(tmp_path / "cache.json"))
        result = cm.load()
        assert isinstance(result, FunctionCache)

    def test_save_and_load(self, tmp_path):
        path = str(tmp_path / "cache.json")
        cm = CacheManager(cache_path=path)
        cm.save()
        result = cm.load()
        assert isinstance(result, FunctionCache)

    def test_get_by_id_not_found(self, tmp_path):
        cm = CacheManager(cache_path=str(tmp_path / "cache.json"))
        result = cm.get_by_id("nonexistent")
        assert result is None

    def test_get_by_signature_not_found(self, tmp_path):
        cm = CacheManager(cache_path=str(tmp_path / "cache.json"))
        result = cm.get_by_signature("nonexistent")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_cache_property(self, tmp_path):
        cm = CacheManager(cache_path=str(tmp_path / "cache.json"))
        result = cm.cache
        assert result is None or isinstance(result, FunctionCache)
