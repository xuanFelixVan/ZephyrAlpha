# [A_test] module_id: MOD-GOV_lazy_loader_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-402 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_lazy_loader
# [INVARIANTS] LazyModuleRegistry is per-instance; thread-safe
# [MODIFY-GUARD] lazy_loader.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] KeyError on unregistered; RuntimeError on not-yet-loaded; re-raises on import failure
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.shared.lifecycle.lazy_loader import LazyModuleRegistry, ModuleEntry


class TestModuleEntry:
    def test_defaults(self):
        entry = ModuleEntry(name="m1", import_path="os.path")
        assert entry.name == "m1"
        assert entry.import_path == "os.path"
        assert entry.is_core is False
        assert entry.loaded is False
        assert entry.module is None
        assert entry.load_time_s == 0.0
        assert entry.loaded_at == 0.0

    def test_custom(self):
        entry = ModuleEntry(
            name="m2",
            import_path="json",
            is_core=True,
            loaded=True,
            module=None,
            load_time_s=0.5,
        )
        assert entry.is_core is True
        assert entry.loaded is True
        assert entry.load_time_s == 0.5


class TestLazyModuleRegistryInit:
    def test_default(self):
        reg = LazyModuleRegistry()
        assert reg.list_entries() == []

    def test_with_core_modules(self):
        reg = LazyModuleRegistry(core_modules=["os", "json"])
        reg.register("os", "os")
        reg.register("json", "json")
        reg.register("sys", "sys")
        entries = reg.list_entries()
        core_names = [e.name for e in entries if e.is_core]
        assert "os" in core_names
        assert "json" in core_names
        assert "sys" not in core_names


class TestLazyModuleRegistryRegister:
    def test_register(self):
        reg = LazyModuleRegistry()
        reg.register("os", "os")
        assert reg.is_registered("os") is True

    def test_register_overwrite(self):
        reg = LazyModuleRegistry()
        reg.register("m1", "os")
        reg.register("m1", "json")
        assert reg.is_registered("m1") is True

    def test_register_core_flag(self):
        reg = LazyModuleRegistry(core_modules=["os"])
        reg.register("os", "os")
        entries = reg.list_entries()
        os_entry = [e for e in entries if e.name == "os"][0]
        assert os_entry.is_core is True

    def test_register_explicit_core(self):
        reg = LazyModuleRegistry()
        reg.register("m1", "json", is_core=True)
        entries = reg.list_entries()
        assert entries[0].is_core is True


class TestLazyModuleRegistryLoad:
    def test_load_success(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        mod = reg.load("json")
        import json as expected

        assert mod is expected
        assert reg.is_loaded("json") is True

    def test_load_already_loaded(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        mod1 = reg.load("json")
        mod2 = reg.load("json")
        assert mod1 is mod2

    def test_load_unregistered_raises_keyerror(self):
        reg = LazyModuleRegistry()
        with pytest.raises(KeyError, match="not registered"):
            reg.load("nonexistent")

    def test_load_bad_import_raises(self):
        reg = LazyModuleRegistry()
        reg.register("bad", "nonexistent.module.xyz")
        with pytest.raises(ModuleNotFoundError):
            reg.load("bad")

    def test_load_records_timing(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        reg.load("json")
        entries = reg.list_entries()
        json_entry = [e for e in entries if e.name == "json"][0]
        assert json_entry.load_time_s >= 0
        assert json_entry.loaded_at > 0


class TestLazyModuleRegistryGet:
    def test_get_loaded(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        reg.load("json")
        mod = reg.get("json")
        import json as expected

        assert mod is expected

    def test_get_unregistered_raises_keyerror(self):
        reg = LazyModuleRegistry()
        with pytest.raises(KeyError, match="not registered"):
            reg.get("nope")

    def test_get_not_yet_loaded_raises_runtimeerror(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        with pytest.raises(RuntimeError, match="not yet loaded"):
            reg.get("json")


class TestLazyModuleRegistryIsLoaded:
    def test_not_registered(self):
        reg = LazyModuleRegistry()
        assert reg.is_loaded("nope") is False

    def test_registered_not_loaded(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        assert reg.is_loaded("json") is False

    def test_loaded(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        reg.load("json")
        assert reg.is_loaded("json") is True


class TestLazyModuleRegistryUnload:
    def test_unload_success(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        reg.load("json")
        result = reg.unload("json")
        assert result is True
        assert reg.is_loaded("json") is False

    def test_unload_not_loaded(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        result = reg.unload("json")
        assert result is False

    def test_unload_not_registered(self):
        reg = LazyModuleRegistry()
        result = reg.unload("nope")
        assert result is False

    def test_unload_clears_module(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        reg.load("json")
        reg.unload("json")
        with pytest.raises(RuntimeError):
            reg.get("json")


class TestLazyModuleRegistryLoadCoreModules:
    def test_load_core_modules(self):
        reg = LazyModuleRegistry(core_modules=["json", "os"])
        reg.register("json", "json")
        reg.register("os", "os")
        reg.register("sys", "sys")
        loaded = reg.load_core_modules()
        assert loaded == 2
        assert reg.is_loaded("json") is True
        assert reg.is_loaded("os") is True
        assert reg.is_loaded("sys") is False

    def test_load_core_modules_no_core(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        loaded = reg.load_core_modules()
        assert loaded == 0

    def test_load_core_modules_failure_continues(self):
        reg = LazyModuleRegistry(core_modules=["json", "bad_module"])
        reg.register("json", "json")
        reg.register("bad_module", "nonexistent.module.xyz")
        loaded = reg.load_core_modules()
        assert loaded == 1


class TestLazyModuleRegistryStats:
    def test_empty_stats(self):
        reg = LazyModuleRegistry()
        stats = reg.stats()
        assert stats["total_registered"] == 0
        assert stats["total_loaded"] == 0
        assert stats["core_modules"] == 0
        assert stats["lazy_modules"] == 0
        assert stats["pending"] == 0

    def test_stats_after_register_and_load(self):
        reg = LazyModuleRegistry(core_modules=["json"])
        reg.register("json", "json")
        reg.register("sys", "sys")
        reg.load("json")
        stats = reg.stats()
        assert stats["total_registered"] == 2
        assert stats["total_loaded"] == 1
        assert stats["core_modules"] == 1
        assert stats["lazy_modules"] == 1
        assert stats["pending"] == 1


class TestLazyModuleRegistryListEntries:
    def test_empty(self):
        reg = LazyModuleRegistry()
        assert reg.list_entries() == []

    def test_returns_entries(self):
        reg = LazyModuleRegistry()
        reg.register("json", "json")
        reg.register("os", "os")
        entries = reg.list_entries()
        assert len(entries) == 2
        names = {e.name for e in entries}
        assert names == {"json", "os"}
