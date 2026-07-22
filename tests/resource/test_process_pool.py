# [A_test] module_id: MOD-GOV_process_pool | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-551 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.resource_optimization.test_process_pool
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
test_process_pool.py - MCPProcessPool unit tests
=================================================

TASK-INF-0142 Phase 4 verification.
"""


import sys
import time

from zephyr.shared.infra.process_pool import MCPProcessPool


class TestProcessPoolBasic:
    def setup_method(self):
        self._pools: list[MCPProcessPool] = []

    def teardown_method(self):
        for pool in self._pools:
            pool.terminate_all()

    def _make_pool(self, **kw) -> MCPProcessPool:
        pool = MCPProcessPool(**kw)
        self._pools.append(pool)
        return pool

    def test_empty_pool(self):
        pool = self._make_pool()
        stats = pool.get_stats()
        assert stats.active_processes == 0
        assert stats.max_processes == 30

    def test_create_process(self):
        pool = self._make_pool()
        entry = pool.get_or_create("echo-test", [sys.executable, "-c", "import time; time.sleep(60)"])
        assert entry is not None
        assert entry.is_alive
        stats = pool.get_stats()
        assert stats.active_processes == 1

    def test_reuse_process(self):
        pool = self._make_pool()
        entry1 = pool.get_or_create("reuse-test", [sys.executable, "-c", "import time; time.sleep(60)"])
        entry2 = pool.get_or_create("reuse-test")
        assert entry1 is entry2
        assert entry2.reuse_count == 1

    def test_max_processes_limit(self):
        pool = self._make_pool(max_processes=2)
        pool.get_or_create("p1", [sys.executable, "-c", "import time; time.sleep(60)"])
        pool.get_or_create("p2", [sys.executable, "-c", "import time; time.sleep(60)"])
        result = pool.get_or_create("p3", [sys.executable, "-c", "import time; time.sleep(60)"])
        assert result is None

    def test_terminate_process(self):
        pool = self._make_pool()
        pool.get_or_create("term-test", [sys.executable, "-c", "import time; time.sleep(60)"])
        assert pool.terminate("term-test") is True
        stats = pool.get_stats()
        assert stats.active_processes == 0

    def test_terminate_nonexistent(self):
        pool = self._make_pool()
        assert pool.terminate("nope") is False

    def test_terminate_all(self):
        pool = self._make_pool()
        pool.get_or_create("t1", [sys.executable, "-c", "import time; time.sleep(60)"])
        pool.get_or_create("t2", [sys.executable, "-c", "import time; time.sleep(60)"])
        count = pool.terminate_all()
        assert count == 2
        assert pool.get_stats().active_processes == 0


class TestProcessPoolZombie:
    def setup_method(self):
        self._pools: list[MCPProcessPool] = []

    def teardown_method(self):
        for pool in self._pools:
            pool.terminate_all()

    def _make_pool(self, **kw) -> MCPProcessPool:
        pool = MCPProcessPool(**kw)
        self._pools.append(pool)
        return pool

    def test_dead_process_detected(self):
        pool = self._make_pool()
        entry = pool.get_or_create("quick-die", [sys.executable, "-c", "pass"])
        time.sleep(1.0)
        assert not entry.is_alive
        reaped = pool._reap_zombies()
        assert reaped >= 1

    def test_get_or_create_replaces_dead(self):
        pool = self._make_pool()
        pool.get_or_create("replace-test", [sys.executable, "-c", "pass"])
        time.sleep(1.0)
        new_entry = pool.get_or_create("replace-test", [sys.executable, "-c", "import time; time.sleep(60)"])
        assert new_entry is not None
        assert new_entry.is_alive


class TestProcessPoolStats:
    def setup_method(self):
        self._pools: list[MCPProcessPool] = []

    def teardown_method(self):
        for pool in self._pools:
            pool.terminate_all()

    def _make_pool(self, **kw) -> MCPProcessPool:
        pool = MCPProcessPool(**kw)
        self._pools.append(pool)
        return pool

    def test_stats_with_active(self):
        pool = self._make_pool()
        pool.get_or_create("s1", [sys.executable, "-c", "import time; time.sleep(60)"])
        stats = pool.get_stats()
        assert stats.active_processes == 1
        assert stats.reuse_count == 0

    def test_reuse_count_increments(self):
        pool = self._make_pool()
        pool.get_or_create("r1", [sys.executable, "-c", "import time; time.sleep(60)"])
        pool.get_or_create("r1")
        pool.get_or_create("r1")
        stats = pool.get_stats()
        assert stats.reuse_count == 2
