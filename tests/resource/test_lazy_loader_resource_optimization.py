# [A_test] module_id: SRC-TST-1931 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-550 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.resource_optimization.test_lazy_loader
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
test_lazy_loader.py - LazyModuleRegistry unit tests
====================================================

TASK-INF-0142 Phase 4 verification.
"""


import pytest

from zephyr.shared.lifecycle.lazy_loader import LazyModuleRegistry


class TestLazyModuleRegistryBasic:
    def test_register_and_load(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        mod = reg.load("json")
        assert mod is not None
        assert hasattr(mod, "dumps")

    def test_is_loaded(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        assert reg.is_loaded("json") is False
        reg.load("json")
        assert reg.is_loaded("json") is True

    def test_is_registered(self):
        reg = LazyModuleRegistry()
        assert reg.is_registered("json") is False
        reg.register("json", "json")
        assert reg.is_registered("json") is True

    def test_load_twice_returns_same(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        m1 = reg.load("json")
        m2 = reg.load("json")
        assert m1 is m2

    def test_load_nonexistent_raises(self):
        reg = LazyModuleRegistry()
        with pytest.raises(KeyError):
            reg.load("nope")

    def test_get_before_load_raises(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        with pytest.raises(RuntimeError):
            reg.get("json")

    def test_get_after_load(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        reg.load("json")
        mod = reg.get("json")
        assert mod is not None


class TestLazyModuleRegistryCore:
    def test_core_modules_auto_flag(self):
        reg = LazyModuleRegistry(core_modules=["json", "os"])
        reg.register("json", "json")
        reg.register("os", "os")
        reg.register("yaml", "yaml", is_core=False)
        entries = reg.list_entries()
        json_entry = next(e for e in entries if e.name == "json")
        os_entry = next(e for e in entries if e.name == "os")
        yaml_entry = next(e for e in entries if e.name == "yaml")
        assert json_entry.is_core is True
        assert os_entry.is_core is True
        assert yaml_entry.is_core is False

    def test_load_core_modules(self):
        reg = LazyModuleRegistry(core_modules=["json"])
        reg.register("json", "json")
        reg.register("os", "os")
        loaded = reg.load_core_modules()
        assert loaded == 1
        assert reg.is_loaded("json") is True
        assert reg.is_loaded("os") is False


class TestLazyModuleRegistryUnload:
    def test_unload(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        reg.load("json")
        assert reg.unload("json") is True
        assert reg.is_loaded("json") is False

    def test_unload_not_loaded(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        assert reg.unload("json") is False


class TestLazyModuleRegistryStats:
    def test_stats_empty(self):
        reg = LazyModuleRegistry()
        stats = reg.stats()
        assert stats["total_registered"] == 0
        assert stats["total_loaded"] == 0

    def test_stats_after_register(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json", is_core=True)
        reg.register("os", "os")
        stats = reg.stats()
        assert stats["total_registered"] == 2
        assert stats["core_modules"] == 1
        assert stats["lazy_modules"] == 1
        assert stats["pending"] == 2

    def test_stats_after_load(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        reg.load("json")
        stats = reg.stats()
        assert stats["total_loaded"] == 1
        assert stats["pending"] == 0


class TestLazyModuleRegistryBadImport:
    def test_bad_import_path_raises(self):
        reg = LazyModuleRegistry()
        reg.register("bad", "nonexistent.module.xyz")
        with pytest.raises(ModuleNotFoundError):
            reg.load("bad")
