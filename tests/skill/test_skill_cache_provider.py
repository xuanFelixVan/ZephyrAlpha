# [A_test] module_id: MOD-GOV_skill_cache_provider | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_cache_provider
# [INVARIANTS] get returns None for missing keys; set+get roundtrips; invalidate removes key
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] configure returns dict with backend info
# [TESTS] tests/test_skill_cache_provider.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.autonomy_core.skills.skill_cache_provider import SkillCacheProvider


class TestSkillCacheProviderInstantiation:
    def test_default_memory_backend(self):
        cache = SkillCacheProvider()
        assert cache.backend_name == "memory"

    def test_disk_backend(self):
        cache = SkillCacheProvider(backend="disk")
        assert cache.backend_name == "disk"

    def test_invalid_backend_falls_back_to_memory(self):
        cache = SkillCacheProvider(backend="nonexistent")
        assert cache.backend_name == "memory"


class TestSkillCacheProviderConfigure:
    def test_configure_memory(self):
        cache = SkillCacheProvider()
        result = cache.configure("memory")
        assert result["backend"] == "memory"
        assert result["requested"] == "memory"

    def test_configure_disk(self):
        cache = SkillCacheProvider()
        result = cache.configure("disk")
        assert result["backend"] == "disk"

    def test_configure_invalid_falls_back(self):
        cache = SkillCacheProvider()
        result = cache.configure("redis")
        assert result["backend"] == "memory"
        assert result["available"] is False

    def test_configure_case_insensitive(self):
        cache = SkillCacheProvider()
        result = cache.configure("  MEMORY  ")
        assert result["backend"] == "memory"

    def test_configure_returns_dict(self):
        cache = SkillCacheProvider()
        result = cache.configure("memory")
        assert "backend" in result
        assert "requested" in result
        assert "available" in result


class TestSkillCacheProviderMemoryOps:
    def setup_method(self):
        self.cache = SkillCacheProvider(backend="memory")

    def test_set_and_get(self):
        self.cache.set("key1", "value1")
        assert self.cache.get("key1") == "value1"

    def test_get_missing_key(self):
        assert self.cache.get("nonexistent") is None

    def test_set_overwrite(self):
        self.cache.set("key1", "value1")
        self.cache.set("key1", "value2")
        assert self.cache.get("key1") == "value2"

    def test_invalidate(self):
        self.cache.set("key1", "value1")
        self.cache.invalidate("key1")
        assert self.cache.get("key1") is None

    def test_invalidate_missing_key(self):
        self.cache.invalidate("nonexistent")

    def test_clear(self):
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.clear()
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None

    def test_set_various_types(self):
        self.cache.set("str", "hello")
        self.cache.set("int", 42)
        self.cache.set("list", [1, 2, 3])
        self.cache.set("dict", {"a": 1})
        self.cache.set("none_val", None)
        assert self.cache.get("str") == "hello"
        assert self.cache.get("int") == 42
        assert self.cache.get("list") == [1, 2, 3]
        assert self.cache.get("dict") == {"a": 1}
        assert self.cache.get("none_val") is None

    def test_lru_eviction(self):
        cache = SkillCacheProvider(backend="memory")
        cache._SkillCacheProvider__backend.max = 3
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")
        cache.set("k4", "v4")
        assert cache.get("k1") is None
        assert cache.get("k4") == "v4"


class TestSkillCacheProviderDiskOps:
    def setup_method(self):
        self.cache = SkillCacheProvider(backend="disk")

    def teardown_method(self):
        for key in ["dkey1", "dkey2", "d_str", "d_int", "d_list", "dk1", "dk2"]:
            self.cache.invalidate(key)

    def test_set_and_get(self):
        self.cache.set("dkey1", "dvalue1")
        assert self.cache.get("dkey1") == "dvalue1"

    def test_get_missing_key(self):
        assert self.cache.get("nonexistent_disk") is None

    def test_invalidate(self):
        self.cache.set("dkey2", "dvalue2")
        self.cache.invalidate("dkey2")
        assert self.cache.get("dkey2") is None

    def test_set_various_types(self):
        self.cache.set("d_str", "hello")
        self.cache.set("d_int", 42)
        self.cache.set("d_list", [1, 2, 3])
        assert self.cache.get("d_str") == "hello"
        assert self.cache.get("d_int") == 42
        assert self.cache.get("d_list") == [1, 2, 3]

    def test_clear_raises_on_disk(self):
        self.cache.set("dk1", "dv1")
        with pytest.raises(AttributeError):
            self.cache.clear()


class TestSkillCacheProviderBackendSwitch:
    def test_switch_memory_to_disk(self):
        cache = SkillCacheProvider(backend="memory")
        cache.set("mk", "mv")
        cache.configure("disk")
        assert cache.backend_name == "disk"
        assert cache.get("mk") is None

    def test_switch_disk_to_memory(self):
        cache = SkillCacheProvider(backend="disk")
        cache.set("dk", "dv")
        cache.configure("memory")
        assert cache.backend_name == "memory"
        assert cache.get("dk") is None
        cache.clear()
