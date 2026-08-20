# [BLUEPRINT] MOD-MKT-006 | docs/03_modules/_domain_mkt_data/raw_data_cache/blueprint.md
# [MODULE] tests.market_data.raw_data_cache.test_raw_data_cache
# [DOMAIN] D_MKT_DATA
# [DEPENDENCIES] zephyr.market_data.raw_data_cache
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-MKT-006 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-MKT-006 Raw Data Cache 单元测试.

覆盖: put/get 读写、LRU 淘汰、TTL 过期、范围查询、哈希校验、
线程安全、统计信息、边界值(空 symbol/date 拒绝/容量超限淘汰/覆盖更新).
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timedelta, timezone

import pytest

from zephyr.market_data.raw_data_cache import (
    CacheConfig,
    CacheEntry,
    CacheError,
    CacheKey,
    EvictionPolicy,
    RawDataCache,
)

# ============== CacheKey ==============


class TestCacheKey:
    def test_create(self):
        key = CacheKey("600000.SH", "2026-08-01")
        assert key.symbol == "600000.SH"
        assert key.date == "2026-08-01"

    def test_empty_symbol_rejected(self):
        with pytest.raises(CacheError, match="symbol"):
            CacheKey("", "2026-08-01")

    def test_empty_date_rejected(self):
        with pytest.raises(CacheError, match="date"):
            CacheKey("600000.SH", "")

    def test_frozen(self):
        key = CacheKey("600000.SH", "2026-08-01")
        with pytest.raises(Exception):
            key.symbol = "other"  # type: ignore[misc]

    def test_equality(self):
        assert CacheKey("A", "1") == CacheKey("A", "1")
        assert CacheKey("A", "1") != CacheKey("A", "2")
        assert CacheKey("A", "1") != CacheKey("B", "1")


# ============== put / get 基本读写 ==============


class TestPutGet:
    def test_put_returns_entry(self):
        cache = RawDataCache()
        entry = cache.put("600000.SH", "2026-08-01", b"raw", "tushare")
        assert isinstance(entry, CacheEntry)
        assert entry.key == CacheKey("600000.SH", "2026-08-01")
        assert entry.source_vendor == "tushare"
        assert entry.raw_payload == b"raw"
        assert entry.payload_size == 3
        assert len(entry.content_hash) == 16

    def test_get_hit(self):
        cache = RawDataCache()
        cache.put("600000.SH", "2026-08-01", b"raw", "tushare")
        entry = cache.get("600000.SH", "2026-08-01")
        assert entry is not None
        assert entry.raw_payload == b"raw"

    def test_get_miss(self):
        cache = RawDataCache()
        assert cache.get("600000.SH", "2026-08-01") is None

    def test_overwrite_updates_payload(self):
        cache = RawDataCache()
        cache.put("600000.SH", "2026-08-01", b"old", "tushare")
        cache.put("600000.SH", "2026-08-01", b"new long payload", "tushare")
        entry = cache.get("600000.SH", "2026-08-01")
        assert entry is not None
        assert entry.raw_payload == b"new long payload"
        assert entry.payload_size == 16  # len("new long payload")
        assert cache.stats.total_entries == 1

    def test_bytearray_payload_accepted(self):
        cache = RawDataCache()
        entry = cache.put("A", "2026-01-01", bytearray(b"data"), "v")
        assert entry.raw_payload == b"data"

    def test_non_bytes_payload_rejected(self):
        cache = RawDataCache()
        with pytest.raises(CacheError, match="bytes"):
            cache.put("A", "2026-01-01", "string", "v")  # type: ignore[arg-type]

    def test_empty_symbol_rejected(self):
        cache = RawDataCache()
        with pytest.raises(CacheError, match="symbol"):
            cache.put("", "2026-08-01", b"raw", "tushare")

    def test_empty_date_rejected(self):
        cache = RawDataCache()
        with pytest.raises(CacheError, match="date"):
            cache.put("600000.SH", "", b"raw", "tushare")

    def test_empty_vendor_rejected(self):
        cache = RawDataCache()
        with pytest.raises(CacheError, match="source_vendor"):
            cache.put("600000.SH", "2026-08-01", b"raw", "")

    def test_empty_payload_allowed(self):
        cache = RawDataCache()
        entry = cache.put("A", "2026-01-01", b"", "v")
        assert entry.payload_size == 0
        got = cache.get("A", "2026-01-01")
        assert got is not None
        assert got.raw_payload == b""


# ============== 哈希校验 ==============


class TestContentHash:
    def test_same_payload_same_hash(self):
        cache = RawDataCache()
        e1 = cache.put("A", "2026-01-01", b"hello", "v")
        e2 = cache.put("B", "2026-01-01", b"hello", "v")
        assert e1.content_hash == e2.content_hash

    def test_different_payload_different_hash(self):
        cache = RawDataCache()
        e1 = cache.put("A", "2026-01-01", b"hello", "v")
        e2 = cache.put("B", "2026-01-01", b"world", "v")
        assert e1.content_hash != e2.content_hash

    def test_hash_is_16_chars(self):
        cache = RawDataCache()
        entry = cache.put("A", "2026-01-01", b"data", "v")
        assert len(entry.content_hash) == 16


# ============== LRU 淘汰 ==============


class TestLRUEviction:
    def test_lru_evicts_oldest(self):
        cache = RawDataCache(CacheConfig(max_size=2, ttl_seconds=None))
        cache.put("A", "2026-01-01", b"1", "v")
        cache.put("B", "2026-01-01", b"2", "v")
        # 访问 A, 使 B 成为最久未访问
        cache.get("A", "2026-01-01")
        # 写入 C, 应淘汰 B
        cache.put("C", "2026-01-01", b"3", "v")
        assert cache.get("A", "2026-01-01") is not None
        assert cache.get("B", "2026-01-01") is None
        assert cache.get("C", "2026-01-01") is not None
        assert cache.stats.total_entries == 2

    def test_lru_eviction_count(self):
        cache = RawDataCache(CacheConfig(max_size=1, ttl_seconds=None))
        cache.put("A", "2026-01-01", b"1", "v")
        cache.put("B", "2026-01-01", b"2", "v")  # 淘汰 A
        assert cache.stats.eviction_count == 1

    def test_ttl_only_policy_no_capacity_eviction(self):
        cache = RawDataCache(CacheConfig(max_size=1, ttl_seconds=None, policy=EvictionPolicy.TTL))
        cache.put("A", "2026-01-01", b"1", "v")
        cache.put("B", "2026-01-01", b"2", "v")
        # TTL 策略不做容量淘汰, 两条都在
        assert cache.stats.total_entries == 2


# ============== TTL 过期 ==============


class TestTTLExpiry:
    def test_expired_entry_returns_none(self):
        cache = RawDataCache()
        # ttl=0 立即过期
        cache.put("A", "2026-01-01", b"1", "v", ttl_seconds=0)
        # 等待过期
        time.sleep(0.01)
        assert cache.get("A", "2026-01-01") is None

    def test_ttl_override(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=999))
        cache.put("A", "2026-01-01", b"1", "v", ttl_seconds=0)
        time.sleep(0.01)
        assert cache.get("A", "2026-01-01") is None

    def test_no_ttl_never_expires(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        cache.put("A", "2026-01-01", b"1", "v")
        assert cache.get("A", "2026-01-01") is not None

    def test_evict_expired_active(self):
        cache = RawDataCache()
        cache.put("A", "2026-01-01", b"1", "v", ttl_seconds=0)
        cache.put("B", "2026-01-01", b"2", "v", ttl_seconds=999)
        time.sleep(0.01)
        evicted = cache.evict_expired()
        assert evicted == 1
        assert cache.get("A", "2026-01-01") is None
        assert cache.get("B", "2026-01-01") is not None

    def test_is_expired_property(self):
        cache = RawDataCache()
        entry = cache.put("A", "2026-01-01", b"1", "v", ttl_seconds=0)
        assert entry.expires_at is not None
        time.sleep(0.01)
        assert entry.is_expired is True

    def test_no_ttl_expires_at_none(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        entry = cache.put("A", "2026-01-01", b"1", "v")
        assert entry.expires_at is None
        assert entry.is_expired is False


# ============== 范围查询 ==============


class TestQuery:
    def test_query_range(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        for d in ["2026-08-01", "2026-08-02", "2026-08-03", "2026-08-04"]:
            cache.put("600000.SH", d, d.encode(), "v")
        results = cache.query("600000.SH", "2026-08-02", "2026-08-03")
        assert len(results) == 2
        assert results[0].key.date == "2026-08-02"
        assert results[1].key.date == "2026-08-03"

    def test_query_skips_other_symbols(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        cache.put("A", "2026-01-01", b"1", "v")
        cache.put("B", "2026-01-01", b"2", "v")
        results = cache.query("A", "2026-01-01", "2026-01-01")
        assert len(results) == 1
        assert results[0].key.symbol == "A"

    def test_query_skips_expired(self):
        cache = RawDataCache()
        cache.put("A", "2026-01-01", b"1", "v", ttl_seconds=0)
        cache.put("A", "2026-01-02", b"2", "v", ttl_seconds=999)
        time.sleep(0.01)
        results = cache.query("A", "2026-01-01", "2026-01-02")
        assert len(results) == 1
        assert results[0].key.date == "2026-01-02"

    def test_query_empty_range(self):
        cache = RawDataCache()
        assert cache.query("A", "2026-01-01", "2026-01-05") == []

    def test_query_sorted_by_date(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        # 乱序写入
        cache.put("A", "2026-08-03", b"3", "v")
        cache.put("A", "2026-08-01", b"1", "v")
        cache.put("A", "2026-08-02", b"2", "v")
        results = cache.query("A", "2026-08-01", "2026-08-03")
        dates = [e.key.date for e in results]
        assert dates == ["2026-08-01", "2026-08-02", "2026-08-03"]


# ============== exists / clear ==============


class TestExistsClear:
    def test_exists_true(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        cache.put("A", "2026-01-01", b"1", "v")
        assert cache.exists("A", "2026-01-01") is True

    def test_exists_false(self):
        cache = RawDataCache()
        assert cache.exists("A", "2026-01-01") is False

    def test_exists_expired_false(self):
        cache = RawDataCache()
        cache.put("A", "2026-01-01", b"1", "v", ttl_seconds=0)
        time.sleep(0.01)
        assert cache.exists("A", "2026-01-01") is False

    def test_clear(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        cache.put("A", "2026-01-01", b"1", "v")
        cache.put("B", "2026-01-01", b"2", "v")
        count = cache.clear()
        assert count == 2
        assert cache.stats.total_entries == 0
        assert cache.stats.total_size_bytes == 0

    def test_clear_empty(self):
        cache = RawDataCache()
        assert cache.clear() == 0


# ============== 统计 ==============


class TestStats:
    def test_hit_miss_count(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        cache.put("A", "2026-01-01", b"1", "v")
        cache.get("A", "2026-01-01")  # hit
        cache.get("B", "2026-01-01")  # miss
        stats = cache.stats
        assert stats.hit_count == 1
        assert stats.miss_count == 1

    def test_hit_rate(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        cache.put("A", "2026-01-01", b"1", "v")
        cache.get("A", "2026-01-01")  # hit
        cache.get("A", "2026-01-01")  # hit
        cache.get("B", "2026-01-01")  # miss
        stats = cache.stats
        assert stats.hit_rate == pytest.approx(2 / 3)

    def test_hit_rate_zero_when_empty(self):
        cache = RawDataCache()
        assert cache.stats.hit_rate == 0.0

    def test_total_size_bytes(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        cache.put("A", "2026-01-01", b"12345", "v")
        assert cache.stats.total_size_bytes == 5


# ============== 线程安全 ==============


class TestThreadSafety:
    def test_concurrent_put_get(self):
        cache = RawDataCache(CacheConfig(max_size=500, ttl_seconds=None))
        errors: list[Exception] = []

        def writer(start: int) -> None:
            try:
                for i in range(start, start + 100):
                    cache.put(f"S{i}", "2026-01-01", b"data", "v")
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        def reader() -> None:
            try:
                for i in range(200):
                    cache.get(f"S{i}", "2026-01-01")
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        threads = [
            threading.Thread(target=writer, args=(0,)),
            threading.Thread(target=writer, args=(100,)),
            threading.Thread(target=reader),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        # 200 次写入, max_size=500, 全部应保留
        assert cache.stats.total_entries == 200

    def test_concurrent_clear_safe(self):
        cache = RawDataCache(CacheConfig(ttl_seconds=None))
        for i in range(50):
            cache.put(f"S{i}", "2026-01-01", b"x", "v")

        errors: list[Exception] = []

        def clearer() -> None:
            try:
                cache.clear()
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        def getter() -> None:
            try:
                for i in range(50):
                    cache.get(f"S{i}", "2026-01-01")
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        threads = [threading.Thread(target=clearer), threading.Thread(target=getter)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
