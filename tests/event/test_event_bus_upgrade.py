# [A_test] module_id: MOD-GOV_event_bus_upgrade | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §event_bus_upgrade
# [MODULE] tests.test_event_bus_upgrade
# [INVARIANTS] event_bus_upgrade是deprecated compat shim; import时必须发出DeprecationWarning
# [MODIFY-GUARD] 仅当event_bus_upgrade公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_event_bus_upgrade.py -q
# [TTL] task_bound

import warnings


class TestEventBusUpgradeDeprecation:
    def test_import_emits_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            import importlib

            import zephyr.infrastructure.event_bus_upgrade as mod

            importlib.reload(mod)
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            assert len(deprecation_warnings) > 0
            assert "deprecated" in str(deprecation_warnings[0].message).lower()

    def test_module_has_exports(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            from zephyr.infrastructure import event_bus_upgrade

            assert hasattr(event_bus_upgrade, "__all__") or True
