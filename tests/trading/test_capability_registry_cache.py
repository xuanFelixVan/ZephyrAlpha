# [A_test] module_id: MOD-GOV_capability_registry_cache | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §16.3
# [MODULE] tests.trading.test_capability_registry
# [INVARIANTS] 缓存写失效无脏读;TTL<=0 永不命中
# [MODIFY-GUARD] src/zephyr/trading/capability_registry.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] cache_stats 返回 hits/misses/hit_rate/size/ttl_seconds
# [TESTS] tests/trading/test_capability_registry.py
# [TTL] task_bound

"""CapabilityRegistry 内存缓存 + 读写锁专项（蓝图 §16.3 步骤 1 / GAP-006 配套）。

验收口径（04号文 Phase 0 步骤 0.2）：缓存命中率 >95%。
"""

from __future__ import annotations

import threading

from zephyr.trading.capability_card import CapabilityCard, CapabilityCategory
from zephyr.trading.capability_registry import CapabilityRegistry


def _make_card(
    capability_id: str = "test-card",
    name: str = "Test Card",
    category: CapabilityCategory = CapabilityCategory.INFRA,
    description: str = "A test card",
    tags: list[str] | None = None,
    status: str = "ACTIVE",
) -> CapabilityCard:
    return CapabilityCard(
        capability_id=capability_id,
        name=name,
        category=category,
        description=description,
        tags=tags or [],
        status=status,
    )


class TestQueryCache:
    def test_repeated_reads_hit_cache(self):
        reg = CapabilityRegistry()
        reg.register(_make_card("c1", tags=["gpu"]))
        reg.get("c1")  # 首次 miss 回填
        for _ in range(99):
            assert reg.get("c1") is not None
        stats = reg.cache_stats()
        assert stats["hits"] == 99
        assert stats["misses"] == 1
        assert stats["hit_rate"] >= 0.95

    def test_hit_rate_acceptance_over_95_percent(self):
        """04号文验收口径：重复读场景命中率 >95%（含 discover/list_all/find_by_tags/count）。"""
        reg = CapabilityRegistry()
        reg.register(_make_card("c1", name="Embedding Router", tags=["gpu", "embedding"]))
        reads = (
            [lambda: reg.get("c1")]
            + [lambda: reg.list_all()]
            + [lambda: reg.discover("embedding")]
            + [lambda: reg.find_by_tags(["gpu"])]
            + [lambda: reg.count()]
        )
        for fn in reads:  # 首轮全部 miss 回填
            fn()
        for _ in range(40):  # 200 次重复读全 hit
            for fn in reads:
                fn()
        stats = reg.cache_stats()
        assert stats["hit_rate"] > 0.95

    def test_cache_result_consistent(self):
        reg = CapabilityRegistry()
        card = _make_card("c1", name="Embedding Router", tags=["gpu"])
        reg.register(card)
        assert reg.get("c1") is card
        assert reg.get("c1") is card  # 命中返回同一对象
        assert reg.discover("embedding") == [card]
        assert reg.find_by_tags(["GPU"]) == [card]
        assert reg.count() == 1

    def test_register_invalidates_cache(self):
        reg = CapabilityRegistry()
        reg.register(_make_card("c1"))
        assert reg.count() == 1  # miss 回填
        assert reg.count() == 1  # hit
        reg.register(_make_card("c2"))
        assert reg.count() == 2  # 版本失效 → miss 后看到新值
        stats = reg.cache_stats()
        assert stats["misses"] == 2

    def test_unregister_invalidates_cache(self):
        reg = CapabilityRegistry()
        reg.register(_make_card("c1"))
        assert reg.get("c1") is not None  # miss 回填
        assert reg.get("c1") is not None  # hit
        reg.unregister("c1")
        assert reg.get("c1") is None  # 失效后无脏读
        reg.register(_make_card("c1"))
        assert reg.get("c1") is not None

    def test_duplicate_register_does_not_bump_version(self):
        reg = CapabilityRegistry()
        reg.register(_make_card("c1"))
        reg.get("c1")
        reg.register(_make_card("c1"))  # 重复注册：无状态变化，不失效缓存
        reg.get("c1")
        stats = reg.cache_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_ttl_zero_never_hits(self):
        reg = CapabilityRegistry(cache_ttl_seconds=0.0)
        reg.register(_make_card("c1"))
        for _ in range(5):
            reg.get("c1")
        stats = reg.cache_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 5

    def test_health_check_all_cached(self):
        reg = CapabilityRegistry()
        reg.register(_make_card("c1", status="ACTIVE"))
        assert reg.health_check_all() == {"c1": True}
        assert reg.health_check_all() == {"c1": True}
        stats = reg.cache_stats()
        assert stats["hits"] == 1

    def test_cache_stats_schema(self):
        reg = CapabilityRegistry()
        stats = reg.cache_stats()
        assert set(stats) == {"hits", "misses", "hit_rate", "size", "ttl_seconds"}
        assert stats["hits"] == 0
        assert stats["hit_rate"] == 0.0


class TestReadWriteLock:
    def test_concurrent_reads_no_error(self):
        """读路径并发：8 线程 × 50 次混合读，结果一致且无异常。"""
        reg = CapabilityRegistry()
        for i in range(10):
            reg.register(_make_card(f"c{i}", name=f"Card {i}", tags=["t"]))
        errors: list[Exception] = []

        def _reader() -> None:
            try:
                for _ in range(50):
                    assert len(reg.list_all()) == 10
                    assert reg.count() == 10
                    assert reg.get("c3") is not None
                    assert len(reg.discover("card")) == 10
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        threads = [threading.Thread(target=_reader) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []

    def test_concurrent_read_write_consistent(self):
        """写并发下读者看到旧快照或新快照（最终一致），绝不抛异常/读到中间态。"""
        reg = CapabilityRegistry()
        reg.register(_make_card("c0"))
        errors: list[Exception] = []
        stop = threading.Event()

        def _reader() -> None:
            try:
                while not stop.is_set():
                    assert 1 <= reg.count() <= 20
                    assert 1 <= len(reg.list_all()) <= 20
            except Exception as e:  # noqa: BLE001
                errors.append(e)

        readers = [threading.Thread(target=_reader) for _ in range(4)]
        for t in readers:
            t.start()
        for i in range(1, 20):
            reg.register(_make_card(f"c{i}"))
        stop.set()
        for t in readers:
            t.join()
        assert errors == []
        assert reg.count() == 20
