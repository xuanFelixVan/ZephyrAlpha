# [A_test] module_id: SRC-TST-1930 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-549 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.resource_optimization.test_io_cache
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
test_io_cache.py - FileCache unit tests
========================================

TASK-INF-0140 Phase 2 verification.
"""


import json
import time

import pytest

from zephyr.shared.io.io_cache import FileCache


class TestFileCacheBasic:
    def test_miss_on_empty(self, tmp_path):
        cache = FileCache()
        assert cache.get(str(tmp_path / "nonexistent.yaml")) is None

    def test_get_or_load_yaml(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("key: value\nlist:\n  - a\n  - b\n", encoding="utf-8")
        cache = FileCache()
        result = cache.get_or_load(str(f))
        assert result == {"key": "value", "list": ["a", "b"]}

    def test_get_or_load_json(self, tmp_path):
        f = tmp_path / "test.json"
        f.write_text(json.dumps({"x": 1}), encoding="utf-8")
        cache = FileCache()
        result = cache.get_or_load(str(f))
        assert result == {"x": 1}

    def test_hit_on_second_get(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("a: 1\n", encoding="utf-8")
        cache = FileCache()
        cache.get_or_load(str(f))
        result = cache.get(str(f))
        assert result == {"a": 1}
        stats = cache.get_stats()
        assert stats.hit_count == 1
        assert stats.miss_count == 1

    def test_invalidate_on_mtime_change(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("a: 1\n", encoding="utf-8")
        cache = FileCache()
        cache.get_or_load(str(f))
        time.sleep(0.05)
        f.write_text("a: 2\n", encoding="utf-8")
        result = cache.get(str(f))
        assert result is None

    def test_manual_invalidate(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("a: 1\n", encoding="utf-8")
        cache = FileCache()
        cache.get_or_load(str(f))
        assert cache.invalidate(str(f)) is True
        assert cache.get(str(f)) is None

    def test_invalidate_nonexistent(self, tmp_path):
        cache = FileCache()
        assert cache.invalidate(str(tmp_path / "nope.yaml")) is False


class TestFileCacheLRU:
    def test_eviction_at_max_entries(self, tmp_path):
        cache = FileCache(max_entries=3)
        for i in range(5):
            f = tmp_path / f"f{i}.yaml"
            f.write_text(f"val: {i}\n", encoding="utf-8")
            cache.get_or_load(str(f))
        stats = cache.get_stats()
        assert stats.total_entries == 3
        assert stats.evictions == 2

    def test_lru_order(self, tmp_path):
        cache = FileCache(max_entries=3)
        files = []
        for i in range(3):
            f = tmp_path / f"f{i}.yaml"
            f.write_text(f"val: {i}\n", encoding="utf-8")
            cache.get_or_load(str(f))
            files.append(f)
        cache.get(str(files[0]))
        f4 = tmp_path / "f4.yaml"
        f4.write_text("val: 4\n", encoding="utf-8")
        cache.get_or_load(str(f4))
        assert cache.get(str(files[0])) is not None
        assert cache.get(str(files[1])) is None


class TestFileCacheWarm:
    def test_warm_multiple_files(self, tmp_path):
        files = []
        for i in range(3):
            f = tmp_path / f"w{i}.yaml"
            f.write_text(f"v: {i}\n", encoding="utf-8")
            files.append(str(f))
        cache = FileCache()
        loaded = cache.warm(files)
        assert loaded == 3
        stats = cache.get_stats()
        assert stats.total_entries == 3

    def test_warm_skips_nonexistent(self, tmp_path):
        cache = FileCache()
        loaded = cache.warm([str(tmp_path / "nope.yaml")])
        assert loaded == 0


class TestFileCacheStats:
    def test_stats_empty(self):
        cache = FileCache()
        stats = cache.get_stats()
        assert stats.total_entries == 0
        assert stats.hit_count == 0
        assert stats.miss_count == 0
        assert stats.hit_rate == 0.0
        assert stats.memory_usage_mb == 0.0
        assert stats.evictions == 0

    def test_hit_rate_calculation(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("a: 1\n", encoding="utf-8")
        cache = FileCache()
        cache.get_or_load(str(f))
        cache.get(str(f))
        cache.get(str(f))
        stats = cache.get_stats()
        assert stats.hit_rate == pytest.approx(2.0 / 3.0, abs=0.01)


class TestFileCacheClear:
    def test_clear_resets_all(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("a: 1\n", encoding="utf-8")
        cache = FileCache()
        cache.get_or_load(str(f))
        cache.clear()
        stats = cache.get_stats()
        assert stats.total_entries == 0
        assert stats.hit_count == 0
