# [A_test] module_id: SRC-TST-1596 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md | §
# [MODULE] tests.test_shared_lifecycle_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
from zephyr.gov_code_quality.code_dedup.shared_lifecycle_manager import (
    LifecycleStage,
    SharedLifecycleManager,
)


class TestSharedLifecycleManager:
    def test_instantiation_default(self):
        mgr = SharedLifecycleManager()
        assert mgr is not None

    def test_instantiation_with_path(self, tmp_path):
        mgr = SharedLifecycleManager(lifecycle_path=str(tmp_path / "lifecycle.yaml"))
        assert mgr is not None

    def test_register_active(self):
        mgr = SharedLifecycleManager()
        result = mgr.register_active("func_a", "module_a", caller_count=3)
        assert result is not None

    def test_transition(self):
        mgr = SharedLifecycleManager()
        mgr.register_active("func_a", "module_a", caller_count=3)
        result = mgr.transition("func_a", "module_a", LifecycleStage.DEPRECATED, reason="obsolete")
        assert result is not None

    def test_get_active_functions(self):
        mgr = SharedLifecycleManager()
        result = mgr.get_active_functions()
        assert isinstance(result, list)

    def test_get_deprecated_functions(self):
        mgr = SharedLifecycleManager()
        result = mgr.get_deprecated_functions()
        assert isinstance(result, list)

    def test_get_graveyard(self):
        mgr = SharedLifecycleManager()
        result = mgr.get_graveyard()
        assert isinstance(result, list)

    def test_generate_migration(self):
        mgr = SharedLifecycleManager()
        result = mgr.generate_migration("old_func", "old_mod", "new_func", "new_mod", reason="rename")
        assert result is not None

    def test_remove_from_shadow_manifest(self):
        mgr = SharedLifecycleManager()
        result = mgr.remove_from_shadow_manifest("func_a", "module_a")
        assert result is not None
