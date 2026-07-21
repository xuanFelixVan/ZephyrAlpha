# [A_test] module_id: MOD-GOV_ce_cache_invalidation | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.cache_invalidation
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
    from zephyr.shared.io.cache_invalidation import CacheInvalidationManager, CacheVersion
except Exception as _exc:
    pytest.skip(f"cannot import cache_invalidation: {_exc}", allow_module_level=True)


class TestCacheInvalidationManager:
    def test_set_version_stores_and_returns(self):
        mgr = CacheInvalidationManager()
        cv = mgr.set_version("ke-001", 3)
        assert isinstance(cv, CacheVersion)
        assert cv.key == "ke-001"
        assert cv.version == 3
        assert cv.invalidated_at != ""

    def test_check_staleness_stale(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("ke-001", 5)
        assert mgr.check_staleness("ke-001", 3) is True

    def test_check_staleness_fresh(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("ke-001", 3)
        assert mgr.check_staleness("ke-001", 3) is False

    def test_check_staleness_client_newer(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("ke-001", 2)
        assert mgr.check_staleness("ke-001", 5) is False

    def test_check_staleness_unknown_key(self):
        mgr = CacheInvalidationManager()
        assert mgr.check_staleness("unknown", 1) is False

    def test_set_version_overwrites(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("ke-001", 1)
        cv2 = mgr.set_version("ke-001", 5)
        assert cv2.version == 5
        assert mgr.check_staleness("ke-001", 3) is True

    def test_multiple_keys_independent(self):
        mgr = CacheInvalidationManager()
        mgr.set_version("a", 10)
        mgr.set_version("b", 1)
        assert mgr.check_staleness("a", 5) is True
        assert mgr.check_staleness("b", 5) is False
