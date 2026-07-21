# [A_test] module_id: MOD-GOV_spec_sync | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md | §3
# [MODULE] tests.test_spec_sync
# [INVARIANTS] Tests must not modify production state; All imports guarded by pytest.importorskip
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError → skip; AttributeError → fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

mod = pytest.importorskip(
    "zephyr.infrastructure.a2a_protocol.layer3_coordination.spec_sync",
    reason="spec_sync module not available",
)


class TestSpecSync:
    def test_instantiation(self):
        obj = mod.SpecSync()
        assert obj is not None

    def test_register(self):
        obj = mod.SpecSync()
        obj.register("mod_1", "blueprint.yaml", ["impl1.py", "impl2.py"])

    def test_check(self):
        obj = mod.SpecSync()
        obj.register("mod_1", "blueprint.yaml", ["impl1.py"])
        result = obj.check("mod_1")
        assert result is not None

    def test_sync(self):
        obj = mod.SpecSync()
        obj.register("mod_1", "blueprint.yaml", ["impl1.py"])
        result = obj.sync("mod_1", direction="impl_to_spec")
        assert result is not None

    def test_list_drifted(self):
        obj = mod.SpecSync()
        result = obj.list_drifted()
        assert isinstance(result, list)

    def test_check_nonexistent(self):
        obj = mod.SpecSync()
        result = obj.check("nonexistent_mod")
        assert result is not None

    def test_register_empty_impl(self):
        obj = mod.SpecSync()
        obj.register("mod_2", "bp.yaml", [])
        result = obj.check("mod_2")
        assert result is not None


class TestSpecSyncEntry:
    def test_instantiation(self):
        entry = mod.SpecSyncEntry(module_id="m1", blueprint_file="bp.yaml", impl_files=["a.py"])
        assert entry is not None
        assert entry.module_id == "m1"
