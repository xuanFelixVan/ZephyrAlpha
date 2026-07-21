# [A_test] module_id: MOD-GOV_cache_invalidation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_cache_invalidation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_cache_invalidation.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.shared.io.cache_invalidation import (
    CacheInvalidationManager,
    CacheVersion,
)


class TestCacheVersion:
    def test_fields_assigned(self):
        cv = CacheVersion(key="k1", version=3, invalidated_at="2026-05-23T00:00:00+00:00")
        assert cv.key == "k1"
        assert cv.version == 3
        assert cv.invalidated_at == "2026-05-23T00:00:00+00:00"

    def test_version_is_int(self):
        cv = CacheVersion(key="k", version=1, invalidated_at="")
        assert isinstance(cv.version, int)


class TestCacheInvalidationManagerInstantiation:
    def test_can_create_manager(self):
        mgr = CacheInvalidationManager()
        assert mgr is not None

    def test_has_set_version_method(self):
        mgr = CacheInvalidationManager()
        assert callable(getattr(mgr, "set_version", None))

    def test_has_check_staleness_method(self):
        mgr = CacheInvalidationManager()
        assert callable(getattr(mgr, "check_staleness", None))


class TestCacheInvalidationManagerSetVersion:
    def test_set_version_returns_cache_version(self):
        mgr = CacheInvalidationManager()
        cv = mgr.set_version("key1", 5)
        assert isinstance(cv, CacheVersion)
        assert cv.key == "key1"
        assert cv.version == 5

    def test_set_version_populates_invalidated_at(self):
        mgr = CacheInvalidationManager()
        cv = mgr.set_version("key1", 1)
        assert cv.invalidated_at != ""
        assert "T" in cv.invalidated_at

    def test_set_version_overwrites_previous(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("key1", 1)
        cv = mgr.set_version("key1", 2)
        assert cv.version == 2


class TestCacheInvalidationManagerCheckStaleness:
    def test_stale_when_server_version_higher(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("k", 5)
        assert mgr.check_staleness("k", 3) is True

    def test_not_stale_when_versions_equal(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("k", 5)
        assert mgr.check_staleness("k", 5) is False

    def test_not_stale_when_client_version_higher(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("k", 2)
        assert mgr.check_staleness("k", 10) is False

    def test_unknown_key_returns_false(self):
        mgr = CacheInvalidationManager()
        assert mgr.check_staleness("nonexistent", 0) is False

    def test_version_zero_server_and_zero_client(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("k", 0)
        assert mgr.check_staleness("k", 0) is False

    def test_version_zero_server_and_negative_client(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("k", 0)
        assert mgr.check_staleness("k", -1) is True
