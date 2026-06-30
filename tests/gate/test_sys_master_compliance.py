# [A_test] module_id: SRC-TST-1885 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-505 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.gates.test_sys_master_compliance
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

from __future__ import annotations

import sys
from unittest.mock import patch

SYS_MASTER = "zephyr.governance.rule_enforcement.sys_master_compliance"


class TestBlueprintExistence:
    def test_return_type(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_blueprint_existence

        results = check_blueprint_existence()
        assert isinstance(results, list)
        assert len(results) == 2
        for r in results:
            assert r["check_id"] == "SYS-C00"
            assert r["label"].endswith("blueprint_exists")
            assert r["status"] in ("PASS", "FAIL")
            assert "detail" in r


class TestColdStartIntegration:
    def test_project_rules_missing(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_cold_start_integration

        with patch(f"{SYS_MASTER}.PROJECT_RULES") as mock_path:
            mock_path.exists.return_value = False
            results = check_cold_start_integration()
            assert results[0]["status"] == "FAIL"
            assert "MISSING" in results[0]["detail"]

    def test_cold_start_referenced(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_cold_start_integration

        with patch(f"{SYS_MASTER}.PROJECT_RULES") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = (
                "STEP 1 ─ registry\n"
                "STEP 1.5 ─ SYS-MASTER-001 §0 — AI agent cold start first stop\n"
                "STEP 2 ─ project_rules\n"
                "STEP 3 ─ session continuity\n"
                "STEP 4 ─ phase manager\n"
                "STEP 4.5 ─ asset index\n"
                "STEP 5 ─ locate registry\n"
            )
            results = check_cold_start_integration()
            assert results[0]["status"] == "PASS"


class TestDependsOnIntegrity:
    def test_mod_master_present(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_depends_on_integrity

        raw_yaml = "depends_on:\n  - target: MOD-MASTER-001\n    type: reference\n"
        mock_data = {"depends_on": [{"target": "MOD-MASTER-001", "type": "reference"}]}
        with patch(f"{SYS_MASTER}.extract_frontmatter", return_value=mock_data):
            results = check_depends_on_integrity()
            assert results[0]["status"] == "PASS"

    def test_mod_master_missing(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_depends_on_integrity

        with patch(f"{SYS_MASTER}.extract_frontmatter", return_value={"depends_on": []}):
            results = check_depends_on_integrity()
            assert results[0]["status"] == "FAIL"


class TestConstructionProgressConsistency:
    def test_all_match(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_construction_progress_consistency

        fm_sys = {"construction_progress": "completed"}
        fm_mod = {"construction_progress": "phase_1_complete"}
        bp_data = {
            "blueprints": [
                {"module_id": "SYS-MASTER-001", "construction_progress": "completed"},
                {"module_id": "MOD-MASTER-001", "construction_progress": "phase_1_complete"},
            ]
        }
        mod_data = {
            "modules": [
                {"module_id": "SYS-MASTER-001", "construction_plan": {"status": "completed"}},
                {"module_id": "MOD-MASTER-001", "construction_plan": {"status": "phase_1_complete"}},
            ]
        }

        with patch(f"{SYS_MASTER}.extract_frontmatter", side_effect=[fm_sys, fm_mod]):
            with patch(f"{SYS_MASTER}.yaml.safe_load") as mock_load:
                mock_load.side_effect = [bp_data, mod_data, bp_data, mod_data]
                results = check_construction_progress_consistency()
                assert len(results) == 2
                assert all(r["status"] == "PASS" for r in results)

    def test_mismatch(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_construction_progress_consistency

        fm_sys = {"construction_progress": "completed"}
        fm_mod = {"construction_progress": "phase_1_complete"}
        bp_drifted = {
            "blueprints": [
                {"module_id": "SYS-MASTER-001", "construction_progress": "not_started"},
                {"module_id": "MOD-MASTER-001", "construction_progress": "phase_1_complete"},
            ]
        }
        mod_data = {
            "modules": [
                {"module_id": "SYS-MASTER-001", "construction_plan": {"status": "not_started"}},
                {"module_id": "MOD-MASTER-001", "construction_plan": {"status": "phase_1_complete"}},
            ]
        }

        with patch(f"{SYS_MASTER}.extract_frontmatter", side_effect=[fm_sys, fm_mod]):
            with patch(f"{SYS_MASTER}.yaml.safe_load") as mock_load:
                mock_load.side_effect = [bp_drifted, mod_data, bp_drifted, mod_data]
                results = check_construction_progress_consistency()
                assert len(results) == 2
                assert results[0]["status"] == "FAIL"
                assert results[1]["status"] == "PASS"


class TestAiRulesCount:
    def test_76_rules(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_ai_rules_count

        ai_role = " ".join([f"({i}) rule {i}" for i in range(1, 77)])
        with patch(f"{SYS_MASTER}.extract_frontmatter", return_value={"ai_role_instruction": ai_role}):
            results = check_ai_rules_count()
            assert results[0]["status"] == "PASS"

    def test_less_than_76(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_ai_rules_count

        ai_role = " ".join([f"({i}) rule {i}" for i in range(1, 50)])
        with patch(f"{SYS_MASTER}.extract_frontmatter", return_value={"ai_role_instruction": ai_role}):
            results = check_ai_rules_count()
            assert results[0]["status"] == "FAIL"


class TestGateRegistryEntry:
    def test_entry_present(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_gate_registry_entry

        with patch(f"{SYS_MASTER}.GATE_REGISTRY") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = "SYS-MASTER-CMP: active"
            results = check_gate_registry_entry()
            assert results[0]["status"] == "PASS"

    def test_entry_missing(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import check_gate_registry_entry

        with patch(f"{SYS_MASTER}.GATE_REGISTRY") as mock_path:
            mock_path.exists.return_value = True
            mock_path.read_text.return_value = "G1: active\nG2: active"
            results = check_gate_registry_entry()
            assert results[0]["status"] == "FAIL"


class TestMainFunction:
    def test_main_returns_0_when_all_pass(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import main

        all_pass = [
            {"check_id": "X", "label": "a", "status": "PASS", "detail": "ok"},
            {"check_id": "X", "label": "b", "status": "PASS", "detail": "ok"},
        ]
        with patch(f"{SYS_MASTER}.check_blueprint_existence", return_value=all_pass):
            with patch(f"{SYS_MASTER}.check_cold_start_integration", return_value=all_pass):
                with patch(f"{SYS_MASTER}.check_depends_on_integrity", return_value=all_pass):
                    with patch(f"{SYS_MASTER}.check_construction_progress_consistency", return_value=all_pass):
                        with patch(f"{SYS_MASTER}.check_ai_rules_count", return_value=all_pass):
                            with patch(f"{SYS_MASTER}.check_gate_registry_entry", return_value=all_pass):
                                with patch(f"{SYS_MASTER}.check_crosscheck_script", return_value=all_pass):
                                    assert main() == 0

    def test_main_returns_1_when_any_fail(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import main

        one_fail = [{"check_id": "X", "label": "a", "status": "FAIL", "detail": "bad"}]
        with patch(f"{SYS_MASTER}.check_blueprint_existence", return_value=one_fail):
            with patch(f"{SYS_MASTER}.check_cold_start_integration", return_value=[]):
                with patch(f"{SYS_MASTER}.check_depends_on_integrity", return_value=[]):
                    with patch(f"{SYS_MASTER}.check_construction_progress_consistency", return_value=[]):
                        with patch(f"{SYS_MASTER}.check_ai_rules_count", return_value=[]):
                            with patch(f"{SYS_MASTER}.check_gate_registry_entry", return_value=[]):
                                with patch(f"{SYS_MASTER}.check_crosscheck_script", return_value=[]):
                                    assert main() == 1

    def test_main_json_flag(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import main

        all_pass = [{"check_id": "X", "label": "a", "status": "PASS", "detail": "ok"}]
        with patch.object(sys, "argv", ["prog", "--json"]):
            with patch(f"{SYS_MASTER}.check_blueprint_existence", return_value=all_pass):
                with patch(f"{SYS_MASTER}.check_cold_start_integration", return_value=all_pass):
                    with patch(f"{SYS_MASTER}.check_depends_on_integrity", return_value=all_pass):
                        with patch(f"{SYS_MASTER}.check_construction_progress_consistency", return_value=all_pass):
                            with patch(f"{SYS_MASTER}.check_ai_rules_count", return_value=all_pass):
                                with patch(f"{SYS_MASTER}.check_gate_registry_entry", return_value=all_pass):
                                    with patch(f"{SYS_MASTER}.check_crosscheck_script", return_value=all_pass):
                                        assert main() == 0


class TestIntegrationRealFileSystem:
    def test_all_checks_pass_on_real_system(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import (
            check_ai_rules_count,
            check_blueprint_existence,
            check_cold_start_integration,
            check_construction_progress_consistency,
            check_crosscheck_script,
            check_depends_on_integrity,
            check_gate_registry_entry,
        )

        for fn in [
            check_blueprint_existence,
            check_cold_start_integration,
            check_depends_on_integrity,
            check_construction_progress_consistency,
            check_ai_rules_count,
            check_gate_registry_entry,
            check_crosscheck_script,
        ]:
            for r in fn():
                assert r["status"] in ("PASS", "WARN"), f"FAILED: {r}"

    def test_main_exit_zero(self):
        from zephyr.governance.rule_enforcement.sys_master_compliance import main

        assert main() == 0
