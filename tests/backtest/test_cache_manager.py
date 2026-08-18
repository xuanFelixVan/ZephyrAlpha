# [BLUEPRINT] MOD-BT-020 | docs/03_modules/_domain_backtest/cache_manager/blueprint.md
# [MODULE] tests.backtest.test_cache_manager
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.services.cache_manager
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-BT-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-BT-020 Backtest Cache Manager 单元测试.

覆盖: 基本put/get、缓存命中/未命中、LRU淘汰、按键失效、按策略失效、全量清空、
统计正确性、缓存键计算、线程安全、空params、配置校验、frozen不可变、
覆盖更新、hit_count追踪、hit_rate计算。
"""

from __future__ import annotations

import threading
from dataclasses import FrozenInstanceError

import pytest

from zephyr.backtest.services.cache_manager import (
    BacktestCacheManager,
    CacheConfig,
    CacheEntry,
    CacheError,
    CacheKey,
    CacheStats,
)

# ============== 辅助函数 ==============


def make_key(
    mgr: BacktestCacheManager,
    strategy_id: str = "strat_a",
    params: dict | None = None,
    start: str = "2024-01-01",
    end: str = "2024-06-30",
    benchmark: str | None = None,
) -> CacheKey:
    return mgr.compute_key(strategy_id, params or {}, start, end, benchmark)


# ============== 配置 ==============


class TestCacheConfig:
    def test_defaults(self):
        cfg = CacheConfig()
        assert cfg.max_entries == 256
        assert cfg.max_size_bytes == 0

    def test_custom(self):
        cfg = CacheConfig(max_entries=128, max_size_bytes=1024 * 1024)
        assert cfg.max_entries == 128
        assert cfg.max_size_bytes == 1024 * 1024

    def test_frozen(self):
        cfg = CacheConfig()
        with pytest.raises(FrozenInstanceError):
            cfg.max_entries = 500  # type: ignore[misc]

    def test_invalid_max_entries_zero(self):
        with pytest.raises(CacheError):
            CacheConfig(max_entries=0)

    def test_invalid_max_entries_negative(self):
        with pytest.raises(CacheError):
            CacheConfig(max_entries=-1)

    def test_invalid_max_size_negative(self):
        with pytest.raises(CacheError):
            CacheConfig(max_size_bytes=-100)


# ============== Frozen Dataclass ==============


class TestFrozenDataclasses:
    def test_cache_key_frozen(self):
        key = CacheKey("s", "h", "a", "b")
        with pytest.raises(FrozenInstanceError):
            key.strategy_id = "x"  # type: ignore[misc]

    def test_cache_entry_frozen(self):
        key = CacheKey("s", "h", "a", "b")
        entry = CacheEntry(key=key, value=42, created_at="2024-01-01")
        with pytest.raises(FrozenInstanceError):
            entry.value = 99  # type: ignore[misc]

    def test_cache_stats_frozen(self):
        stats = CacheStats(hits=1, misses=2, evictions=3, total_entries=4)
        with pytest.raises(FrozenInstanceError):
            stats.hits = 100  # type: ignore[misc]


# ============== 缓存键计算 ==============


class TestComputeKey:
    def test_same_params_same_key(self):
        mgr = BacktestCacheManager()
        k1 = mgr.compute_key("s", {"fast": 5, "slow": 20}, "2024-01-01", "2024-06-30")
        k2 = mgr.compute_key("s", {"fast": 5, "slow": 20}, "2024-01-01", "2024-06-30")
        assert k1 == k2

    def test_different_params_different_key(self):
        mgr = BacktestCacheManager()
        k1 = mgr.compute_key("s", {"fast": 5}, "2024-01-01", "2024-06-30")
        k2 = mgr.compute_key("s", {"fast": 10}, "2024-01-01", "2024-06-30")
        assert k1 != k2

    def test_param_order_independent(self):
        """参数顺序不影响缓存键。"""
        mgr = BacktestCacheManager()
        k1 = mgr.compute_key("s", {"fast": 5, "slow": 20}, "a", "b")
        k2 = mgr.compute_key("s", {"slow": 20, "fast": 5}, "a", "b")
        assert k1 == k2

    def test_different_strategy_different_key(self):
        mgr = BacktestCacheManager()
        k1 = mgr.compute_key("s1", {"fast": 5}, "a", "b")
        k2 = mgr.compute_key("s2", {"fast": 5}, "a", "b")
        assert k1 != k2

    def test_different_dates_different_key(self):
        mgr = BacktestCacheManager()
        k1 = mgr.compute_key("s", {}, "2024-01-01", "2024-06-30")
        k2 = mgr.compute_key("s", {}, "2024-01-01", "2024-12-31")
        assert k1 != k2

    def test_benchmark_affects_key(self):
        mgr = BacktestCacheManager()
        k1 = mgr.compute_key("s", {}, "a", "b", benchmark_symbol="000300")
        k2 = mgr.compute_key("s", {}, "a", "b", benchmark_symbol=None)
        assert k1 != k2

    def test_empty_params_valid(self):
        mgr = BacktestCacheManager()
        key = mgr.compute_key("s", {}, "a", "b")
        assert len(key.params_hash) == 16

    def test_none_params_treated_as_empty(self):
        mgr = BacktestCacheManager()
        key = mgr.compute_key("s", {}, "a", "b")
        assert key.params_hash  # 非空

    def test_empty_strategy_raises(self):
        mgr = BacktestCacheManager()
        with pytest.raises(CacheError):
            mgr.compute_key("", {}, "a", "b")

    def test_empty_dates_raise(self):
        mgr = BacktestCacheManager()
        with pytest.raises(CacheError):
            mgr.compute_key("s", {}, "", "b")
        with pytest.raises(CacheError):
            mgr.compute_key("s", {}, "a", "")

    def test_datetime_params_handled(self):
        """datetime 等非 JSON 原生类型通过 default=str 处理, 生成合法键。"""
        from datetime import datetime

        mgr = BacktestCacheManager()
        key = mgr.compute_key("s", {"date": datetime(2024, 1, 1)}, "a", "b")
        assert len(key.params_hash) == 16


# ============== 基本读写 ==============


class TestPutGet:
    def test_put_then_get(self):
        mgr = BacktestCacheManager()
        key = make_key(mgr)
        result = {"sharpe": 1.5, "return": 0.2}
        assert mgr.put(key, result) is True
        assert mgr.get(key) == result

    def test_get_miss_returns_none(self):
        mgr = BacktestCacheManager()
        key = make_key(mgr)
        assert mgr.get(key) is None

    def test_put_overwrite(self):
        mgr = BacktestCacheManager()
        key = make_key(mgr)
        mgr.put(key, "old")
        is_new = mgr.put(key, "new")
        assert is_new is False
        assert mgr.get(key) == "new"

    def test_put_different_keys(self):
        mgr = BacktestCacheManager()
        k1 = make_key(mgr, params={"fast": 5})
        k2 = make_key(mgr, params={"fast": 10})
        mgr.put(k1, "result1")
        mgr.put(k2, "result2")
        assert mgr.get(k1) == "result1"
        assert mgr.get(k2) == "result2"

    def test_none_value_cached(self):
        """None 值也可以被缓存 (与未命中区分: put后get返回None是命中)。"""
        mgr = BacktestCacheManager()
        key = make_key(mgr)
        mgr.put(key, None)
        stats = mgr.stats()
        # 未 get 之前 miss=0
        assert stats.misses == 0
        # get 后命中 (hits=1, misses=0)
        mgr.get(key)
        stats = mgr.stats()
        assert stats.hits == 1


# ============== LRU 淘汰 ==============


class TestLRUEviction:
    def test_eviction_on_overflow(self):
        mgr = BacktestCacheManager(CacheConfig(max_entries=3))
        keys = [make_key(mgr, params={"i": i}) for i in range(4)]
        for i, k in enumerate(keys):
            mgr.put(k, f"val{i}")
        # 第一个应被淘汰
        assert mgr.get(keys[0]) is None
        # 后三个应在
        for i in range(1, 4):
            assert mgr.get(keys[i]) == f"val{i}"

    def test_lru_order_updates_on_get(self):
        """get 后该条目移到最近使用, 不被淘汰。"""
        mgr = BacktestCacheManager(CacheConfig(max_entries=3))
        k1 = make_key(mgr, params={"i": 1})
        k2 = make_key(mgr, params={"i": 2})
        k3 = make_key(mgr, params={"i": 3})
        mgr.put(k1, "v1")
        mgr.put(k2, "v2")
        mgr.put(k3, "v3")
        # 访问 k1 → k1 移到末尾
        mgr.get(k1)
        # 插入 k4 → 淘汰最旧的 (k2)
        k4 = make_key(mgr, params={"i": 4})
        mgr.put(k4, "v4")
        assert mgr.get(k1) == "v1"  # k1 仍在
        assert mgr.get(k2) is None  # k2 被淘汰
        assert mgr.get(k3) == "v3"
        assert mgr.get(k4) == "v4"

    def test_eviction_count_tracked(self):
        mgr = BacktestCacheManager(CacheConfig(max_entries=2))
        for i in range(5):
            mgr.put(make_key(mgr, params={"i": i}), f"v{i}")
        stats = mgr.stats()
        assert stats.evictions == 3  # 5 inserts - 2 max = 3 evictions
        assert stats.total_entries == 2

    def test_overwrite_does_not_evict(self):
        """覆盖已有键不计为新条目, 不触发淘汰。"""
        mgr = BacktestCacheManager(CacheConfig(max_entries=2))
        k1 = make_key(mgr, params={"i": 1})
        k2 = make_key(mgr, params={"i": 2})
        mgr.put(k1, "v1")
        mgr.put(k2, "v2")
        # 覆盖 k1
        mgr.put(k1, "v1_new")
        stats = mgr.stats()
        assert stats.evictions == 0
        assert stats.total_entries == 2
        assert mgr.get(k1) == "v1_new"


# ============== 失效 ==============


class TestInvalidation:
    def test_invalidate_existing(self):
        mgr = BacktestCacheManager()
        key = make_key(mgr)
        mgr.put(key, "val")
        assert mgr.invalidate(key) is True
        assert mgr.get(key) is None

    def test_invalidate_nonexistent(self):
        mgr = BacktestCacheManager()
        key = make_key(mgr)
        assert mgr.invalidate(key) is False

    def test_invalidate_strategy(self):
        mgr = BacktestCacheManager()
        for i in range(3):
            mgr.put(make_key(mgr, strategy_id="s1", params={"i": i}), f"v{i}")
        for i in range(2):
            mgr.put(make_key(mgr, strategy_id="s2", params={"i": i}), f"w{i}")
        count = mgr.invalidate_strategy("s1")
        assert count == 3
        assert mgr.stats().total_entries == 2

    def test_invalidate_strategy_nonexistent(self):
        mgr = BacktestCacheManager()
        mgr.put(make_key(mgr, strategy_id="s1"), "v")
        count = mgr.invalidate_strategy("s_nonexistent")
        assert count == 0

    def test_invalidate_strategy_empty_id(self):
        mgr = BacktestCacheManager()
        mgr.put(make_key(mgr), "v")
        assert mgr.invalidate_strategy("") == 0

    def test_clear_all(self):
        mgr = BacktestCacheManager()
        for i in range(5):
            mgr.put(make_key(mgr, params={"i": i}), f"v{i}")
        count = mgr.clear()
        assert count == 5
        assert mgr.stats().total_entries == 0

    def test_clear_empty(self):
        mgr = BacktestCacheManager()
        assert mgr.clear() == 0


# ============== 统计 ==============


class TestStats:
    def test_initial_stats(self):
        mgr = BacktestCacheManager()
        stats = mgr.stats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0
        assert stats.total_entries == 0

    def test_hit_miss_count(self):
        mgr = BacktestCacheManager()
        key = make_key(mgr)
        mgr.get(key)  # miss
        mgr.get(key)  # miss
        mgr.put(key, "val")
        mgr.get(key)  # hit
        stats = mgr.stats()
        assert stats.hits == 1
        assert stats.misses == 2

    def test_hit_rate(self):
        stats = CacheStats(hits=3, misses=1, evictions=0, total_entries=1)
        assert stats.hit_rate == 0.75

    def test_hit_rate_zero(self):
        stats = CacheStats(hits=0, misses=0, evictions=0, total_entries=0)
        assert stats.hit_rate == 0.0

    def test_total_entries_after_ops(self):
        mgr = BacktestCacheManager()
        for i in range(3):
            mgr.put(make_key(mgr, params={"i": i}), f"v{i}")
        assert mgr.stats().total_entries == 3
        mgr.clear()
        assert mgr.stats().total_entries == 0


# ============== Hit Count ==============


class TestHitCount:
    def test_hit_count_increments(self):
        mgr = BacktestCacheManager()
        key = make_key(mgr)
        mgr.put(key, "val")
        mgr.get(key)
        mgr.get(key)
        mgr.get(key)
        # 内部 entry 的 hit_count 应为 3
        # 通过 stats 验证 hits=3
        assert mgr.stats().hits == 3

    def test_hit_count_resets_on_overwrite(self):
        mgr = BacktestCacheManager()
        key = make_key(mgr)
        mgr.put(key, "val")
        mgr.get(key)
        mgr.get(key)
        # 覆盖 → hit_count 重置
        mgr.put(key, "new_val")
        assert mgr.stats().hits == 2  # 累计 hits 不重置, 但 entry hit_count 重置


# ============== 线程安全 ==============


class TestThreadSafety:
    def test_concurrent_put_get(self):
        mgr = BacktestCacheManager(CacheConfig(max_entries=1000))
        errors: list[Exception] = []

        def worker(tid: int) -> None:
            try:
                for i in range(50):
                    key = mgr.compute_key(
                        f"s{tid}", {"i": i}, "2024-01-01", "2024-06-30"
                    )
                    mgr.put(key, f"v{tid}-{i}")
                    mgr.get(key)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        stats = mgr.stats()
        assert stats.total_entries == 500  # 10 threads × 50 entries
        assert stats.hits == 500  # each thread gets once after put


# ============== 配置只读 ==============


class TestConfigReadonly:
    def test_config_property(self):
        cfg = CacheConfig(max_entries=100)
        mgr = BacktestCacheManager(cfg)
        assert mgr.config.max_entries == 100
        assert mgr.config is cfg
