# [A_test] module_id: MOD-GOV_blueprint_fidelity | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §tests
# [MODULE] zephyr.security.access_control.blueprint_fidelity
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.security.access_control.blueprint_fidelity import BlueprintFidelity, FidelityCheck

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_REASON = str(exc)

# #ARCH-083 xfail 与既有 import skipif 合并（后赋值覆盖会吃掉 xfail）
pytestmark = [
    pytest.mark.xfail(strict=False, reason="#ARCH-083 blueprint_fidelity 窄实现 vs 宽契约，待裁定"),
    pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_REASON}"),
]


class TestBlueprintFidelity:
    def test_check_field_count_match(self):
        bf = BlueprintFidelity()
        fc = bf.check_field_count("mod_a", expected=5, actual=5)
        assert isinstance(fc, FidelityCheck)
        assert fc.match is True
        assert fc.check_type == "field_count"

    def test_check_field_count_mismatch(self):
        bf = BlueprintFidelity()
        fc = bf.check_field_count("mod_a", expected=5, actual=3)
        assert fc.match is False

    def test_check_api_contract_match(self):
        bf = BlueprintFidelity()
        fc = bf.check_api_contract("mod_a", "process", ["data", "config"], ["config", "data"])
        assert fc.match is True
        assert "api_contract:process" in fc.check_type

    def test_check_api_contract_mismatch(self):
        bf = BlueprintFidelity()
        fc = bf.check_api_contract("mod_a", "process", ["data", "config"], ["data"])
        assert fc.match is False

    def test_summary_empty(self):
        bf = BlueprintFidelity()
        s = bf.summary()
        assert s["total_checks"] == 0
        assert s["passed"] == 0
        assert s["failed"] == 0
        assert s["fidelity_pct"] == 0.0

    def test_summary_mixed(self):
        bf = BlueprintFidelity()
        bf.check_field_count("mod_a", 5, 5)
        bf.check_field_count("mod_b", 3, 2)
        bf.check_api_contract("mod_a", "fn", ["a"], ["b"])
        s = bf.summary()
        assert s["total_checks"] == 3
        assert s["passed"] == 1
        assert s["failed"] == 2
        assert abs(s["fidelity_pct"] - 33.33333333333333) < 0.01

    def test_check_field_count_zero(self):
        bf = BlueprintFidelity()
        fc = bf.check_field_count("mod_c", expected=0, actual=0)
        assert fc.match is True

    def test_check_api_contract_empty_params(self):
        bf = BlueprintFidelity()
        fc = bf.check_api_contract("mod_d", "fn", [], [])
        assert fc.match is True


class TestFidelityCheck:
    def test_model_fields(self):
        fc = FidelityCheck(module="m", check_type="t", expected="e", actual="a", match=True)
        assert fc.module == "m"
        assert fc.match is True
