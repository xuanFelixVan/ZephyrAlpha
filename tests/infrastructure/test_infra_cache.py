# [A_test] module_id: MOD-GOV_infra_cache | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_infra_cache

# [INVARIANTS] TTL过期自动驱逐;LRU超容量驱逐;stats准确

# [MODIFY-GUARD] cache.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] CacheError

# [TESTS] pytest tests/test_infra_cache.py -q
# [TTL] task_bound

import asyncio
import time

from zephyr.shared.infra.cache import (
    CacheError,
    CacheStats,
    MemoryCache,
    cache_key,
)


class TestCacheStats:
    def test_defaults(self):
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.hit_rate == 0.0

    def test_hit_rate(self):
        stats = CacheStats(hits=7, misses=3)
        assert abs(stats.hit_rate - 0.7) < 0.01

    def test_zero_total_hit_rate(self):
        stats = CacheStats(hits=0, misses=0)
        assert stats.hit_rate == 0.0


class TestMemoryCache:
    def test_set_and_get(self):
        cache = MemoryCache(max_size=100, default_ttl_seconds=60)
        asyncio.get_event_loop().run_until_complete(cache.set("key1", "value1"))
        result = asyncio.get_event_loop().run_until_complete(cache.get("key1"))
        assert result == "value1"

    def test_get_missing_returns_none(self):
        cache = MemoryCache()
        result = asyncio.get_event_loop().run_until_complete(cache.get("missing"))
        assert result is None

    def test_delete(self):
        cache = MemoryCache()
        asyncio.get_event_loop().run_until_complete(cache.set("key1", "val"))
        deleted = asyncio.get_event_loop().run_until_complete(cache.delete("key1"))
        assert deleted is True
        result = asyncio.get_event_loop().run_until_complete(cache.get("key1"))
        assert result is None

    def test_delete_nonexistent(self):
        cache = MemoryCache()
        deleted = asyncio.get_event_loop().run_until_complete(cache.delete("nope"))
        assert deleted is False

    def test_clear(self):
        cache = MemoryCache()
        asyncio.get_event_loop().run_until_complete(cache.set("a", 1))
        asyncio.get_event_loop().run_until_complete(cache.set("b", 2))
        asyncio.get_event_loop().run_until_complete(cache.clear())
        r1 = asyncio.get_event_loop().run_until_complete(cache.get("a"))
        r2 = asyncio.get_event_loop().run_until_complete(cache.get("b"))
        assert r1 is None
        assert r2 is None

    def test_ttl_expiry(self):
        cache = MemoryCache(max_size=100, default_ttl_seconds=1)
        asyncio.get_event_loop().run_until_complete(cache.set("short", "data", ttl_seconds=0))
        time.sleep(0.05)
        result = asyncio.get_event_loop().run_until_complete(cache.get("short"))
        assert result is None

    def test_lru_eviction(self):
        cache = MemoryCache(max_size=3, default_ttl_seconds=60)
        asyncio.get_event_loop().run_until_complete(cache.set("a", 1))
        asyncio.get_event_loop().run_until_complete(cache.set("b", 2))
        asyncio.get_event_loop().run_until_complete(cache.set("c", 3))
        asyncio.get_event_loop().run_until_complete(cache.set("d", 4))
        stats = cache.stats()
        assert stats.size <= 3

    def test_stats_tracking(self):
        cache = MemoryCache()
        asyncio.get_event_loop().run_until_complete(cache.set("k", "v"))
        asyncio.get_event_loop().run_until_complete(cache.get("k"))
        asyncio.get_event_loop().run_until_complete(cache.get("miss"))
        stats = cache.stats()
        assert stats.hits == 1
        assert stats.misses == 1

    def test_overwrite_key(self):
        cache = MemoryCache()
        asyncio.get_event_loop().run_until_complete(cache.set("k", "old"))
        asyncio.get_event_loop().run_until_complete(cache.set("k", "new"))
        result = asyncio.get_event_loop().run_until_complete(cache.get("k"))
        assert result == "new"


class TestCacheKey:
    def test_joins_parts(self):
        assert cache_key("llm", "chat", "model") == "llm:chat:model"

    def test_single_part(self):
        assert cache_key("solo") == "solo"

    def test_empty(self):
        assert cache_key() == ""


class TestCacheError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = CacheError("fail")
        assert isinstance(err, ZephyrBaseError)
