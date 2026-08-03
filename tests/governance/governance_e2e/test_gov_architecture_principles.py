# [A_test] module_id: MOD-GOV_gov_architecture_principles | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-386 | docs/03_modules/_domain_governance/blueprint.md | §test
# [MODULE] tests.test_gov_architecture_principles
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] ArchPrinciple枚举稳定;IRON_LAW_DEFS完整
# [MODIFY-GUARD] src/zephyr/governance/architecture_principles.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/test_gov_architecture_principles.py
# [TTL] task_bound

from __future__ import annotations

import pytest

ap_mod = pytest.importorskip("zephyr.governance.architecture_principles")
ArchPrinciple = ap_mod.ArchPrinciple
BlueprintIronLaw = ap_mod.BlueprintIronLaw
PRINCIPLE_DEFS = ap_mod.PRINCIPLE_DEFS
IRON_LAW_DEFS = ap_mod.IRON_LAW_DEFS
princpled_check = ap_mod.princpled_check
get_principle_by_kb_ref = ap_mod.get_principle_by_kb_ref
validate_against_principles = ap_mod.validate_against_principles


class TestArchPrinciple:
    def test_all_values(self):
        assert ArchPrinciple.P1_SSOT.value == "P1_SSOT"
        assert ArchPrinciple.P2_YAML_SCHEMA.value == "P2_YAML_SCHEMA"
        assert ArchPrinciple.P3_DUAL_AI.value == "P3_DUAL_AI"
        assert ArchPrinciple.P4_OCP.value == "P4_OCP"
        assert ArchPrinciple.P5_BLUEPRINT_FIRST.value == "P5_BLUEPRINT_FIRST"

    def test_member_count(self):
        assert len(ArchPrinciple) == 5

    def test_is_str_enum(self):
        assert isinstance(ArchPrinciple.P1_SSOT, str)


class TestBlueprintIronLaw:
    def test_all_values(self):
        assert BlueprintIronLaw.IL1_FLAT_TOP.value == "IL1_FLAT_TOP"
        assert BlueprintIronLaw.IL2_BOOTSTRAP_LINK.value == "IL2_BOOTSTRAP_LINK"
        assert BlueprintIronLaw.IL3_AUDITABLE_CHANGE.value == "IL3_AUDITABLE_CHANGE"
        assert BlueprintIronLaw.IL4_EQUIVALENCE.value == "IL4_EQUIVALENCE"
        assert BlueprintIronLaw.IL5_SOURCE_OF_TRUTH.value == "IL5_SOURCE_OF_TRUTH"

    def test_member_count(self):
        assert len(BlueprintIronLaw) == 5

    def test_is_str_enum(self):
        assert isinstance(BlueprintIronLaw.IL1_FLAT_TOP, str)


class TestPrincipleDefs:
    def test_all_principles_have_defs(self):
        for p in ArchPrinciple:
            assert p in PRINCIPLE_DEFS, f"Missing PRINCIPLE_DEFS for {p}"

    def test_each_def_has_label(self):
        for p, d in PRINCIPLE_DEFS.items():
            assert "label" in d, f"Missing 'label' for {p}"

    def test_each_def_has_statement(self):
        for p, d in PRINCIPLE_DEFS.items():
            assert "statement" in d, f"Missing 'statement' for {p}"

    def test_each_def_has_kb_ref(self):
        for p, d in PRINCIPLE_DEFS.items():
            assert "kb_ref" in d, f"Missing 'kb_ref' for {p}"


class TestIronLawDefs:
    def test_all_iron_laws_have_defs(self):
        for il in BlueprintIronLaw:
            assert il in IRON_LAW_DEFS, f"Missing IRON_LAW_DEFS for {il}"

    def test_each_def_is_nonempty_string(self):
        for il, desc in IRON_LAW_DEFS.items():
            assert isinstance(desc, str) and len(desc) > 0, f"Empty def for {il}"


class TestPrincpledCheckDecorator:
    def test_decorator_preserves_function(self):
        @princpled_check(ArchPrinciple.P1_SSOT)
        def sample_func():
            return 42

        assert sample_func() == 42

    def test_decorator_sets_principles_attr(self):
        @princpled_check(ArchPrinciple.P1_SSOT, ArchPrinciple.P4_OCP)
        def sample_func():
            return 0

        assert hasattr(sample_func, "_zephyr_principles")
        assert ArchPrinciple.P1_SSOT in sample_func._zephyr_principles
        assert ArchPrinciple.P4_OCP in sample_func._zephyr_principles

    def test_decorator_with_no_principles(self):
        @princpled_check()
        def sample_func():
            return 1

        assert sample_func() == 1
        assert sample_func._zephyr_principles == []

    def test_decorator_preserves_function_name(self):
        @princpled_check(ArchPrinciple.P1_SSOT)
        def my_named_func():
            return 0

        assert my_named_func.__name__ == "my_named_func"


class TestGetPrincipleByKbRef:
    def test_known_ref(self):
        result = get_principle_by_kb_ref("KBG-0001")
        assert result == ArchPrinciple.P1_SSOT

    def test_unknown_ref_returns_none(self):
        result = get_principle_by_kb_ref("NONEXISTENT")
        assert result is None

    def test_empty_string_returns_none(self):
        result = get_principle_by_kb_ref("")
        assert result is None


class TestValidateAgainstPrinciples:
    def test_no_violations_returns_true(self):
        assert validate_against_principles([]) is True

    def test_with_violations_returns_false(self):
        assert validate_against_principles(["violation1"]) is False

    def test_multiple_violations_returns_false(self):
        assert validate_against_principles(["v1", "v2", "v3"]) is False
