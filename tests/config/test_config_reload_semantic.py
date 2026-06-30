# [A_test] module_id: SRC-TST-0571 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_config_reload_semantic
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_config_reload_semantic.py
# [TTL] task_bound

import os
import time

import pytest

mod = pytest.importorskip(
    "zephyr.trading.feedback_loop.capacity_assurance.config_reload_semantic", reason="config_reload_semantic not available"
)
ConfigReloadSemantic = mod.ConfigReloadSemantic


class TestConfigReloadSemantic:
    def test_instantiation(self):
        crs = ConfigReloadSemantic()
        assert len(crs._watched) == 0

    def test_watch_existing_file(self, tmp_path):
        crs = ConfigReloadSemantic()
        f = tmp_path / "config.yaml"
        f.write_text("key: value", encoding="utf-8")
        crs.watch(str(f))
        assert str(f) in crs._watched

    def test_watch_nonexistent_file(self):
        crs = ConfigReloadSemantic()
        crs.watch("/nonexistent/file.yaml")
        assert "/nonexistent/file.yaml" not in crs._watched

    def test_check_and_reload_no_change(self, tmp_path):
        crs = ConfigReloadSemantic()
        f = tmp_path / "config.yaml"
        f.write_text("key: value", encoding="utf-8")
        crs.watch(str(f))
        reloaded = crs.check_and_reload()
        assert reloaded == []

    def test_check_and_reload_with_change(self, tmp_path):
        crs = ConfigReloadSemantic()
        f = tmp_path / "config.yaml"
        f.write_text("key: value", encoding="utf-8")
        crs.watch(str(f))
        time.sleep(0.1)
        f.write_text("key: new_value", encoding="utf-8")
        os.utime(str(f), (time.time() + 1, time.time() + 1))
        reloaded = crs.check_and_reload()
        assert str(f) in reloaded

    def test_watch_with_callback(self, tmp_path):
        crs = ConfigReloadSemantic()
        f = tmp_path / "config.yaml"
        f.write_text("key: value", encoding="utf-8")
        callback_results = []
        crs.watch(str(f), callback=lambda path: callback_results.append(path))
        time.sleep(0.1)
        f.write_text("key: new_value", encoding="utf-8")
        os.utime(str(f), (time.time() + 1, time.time() + 1))
        crs.check_and_reload()
        assert len(callback_results) == 1
