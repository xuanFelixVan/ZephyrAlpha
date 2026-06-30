# [A_test] module_id: SRC-TST-0590 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_context_engine_support
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_context_engine_support.py
# [TTL] task_bound


import zephyr.autonomy_core.support as support_pkg


class TestSupportPackageImport:
    def test_package_importable(self):
        assert support_pkg is not None

    def test_all_exports(self):
        expected = {"architecture_context_loader", "doc_compressor", "prompt_registry", "system_snapshot"}
        assert set(support_pkg.__all__) == expected

    def test_submodule_importable_architecture(self):
        from zephyr.autonomy_core.support import architecture_context_loader

        assert architecture_context_loader is not None

    def test_submodule_importable_doc_compressor(self):
        from zephyr.autonomy_core.support import doc_compressor

        assert doc_compressor is not None

    def test_submodule_importable_prompt_registry(self):
        from zephyr.autonomy_core.support import prompt_registry

        assert prompt_registry is not None

    def test_submodule_importable_system_snapshot(self):
        from zephyr.autonomy_core.support import system_snapshot

        assert system_snapshot is not None
