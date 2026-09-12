# [A_test] module_id: MOD-GOV_architecture_principles | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md
# [MODULE] tests.test_architecture_principles
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_architecture_principles.py -q
# [TTL] task_bound

from __future__ import annotations

import logging

from zephyr.governance.architecture_governance.architecture_principles import (
    IRON_LAW_DEFS,
    PRINCIPLE_DEFS,
    ArchPrinciple,
    BlueprintIronLaw,
    get_principle_by_kb_ref,
    princpled_check,
    validate_against_principles,
)


class TestArchPrincipleInstantiation:
    def test_enum_has_five_members(self):
        assert len(ArchPrinciple) == 5

    def test_p1_ssot_value(self):
        assert ArchPrinciple.P1_SSOT.value == "P1_SSOT"

    def test_p2_yaml_schema_value(self):
        assert ArchPrinciple.P2_YAML_SCHEMA.value == "P2_YAML_SCHEMA"

    def test_p3_dual_ai_value(self):
        assert ArchPrinciple.P3_DUAL_AI.value == "P3_DUAL_AI"

    def test_p4_ocp_value(self):
        assert ArchPrinciple.P4_OCP.value == "P4_OCP"

    def test_p5_blueprint_first_value(self):
        assert ArchPrinciple.P5_BLUEPRINT_FIRST.value == "P5_BLUEPRINT_FIRST"

    def test_is_str_enum(self):
        assert isinstance(ArchPrinciple.P1_SSOT, str)


class TestBlueprintIronLawInstantiation:
    def test_enum_has_five_members(self):
        assert len(BlueprintIronLaw) == 5

    def test_il1_value(self):
        assert BlueprintIronLaw.IL1_FLAT_TOP.value == "IL1_FLAT_TOP"

    def test_il2_value(self):
        assert BlueprintIronLaw.IL2_BOOTSTRAP_LINK.value == "IL2_BOOTSTRAP_LINK"

    def test_il3_value(self):
        assert BlueprintIronLaw.IL3_AUDITABLE_CHANGE.value == "IL3_AUDITABLE_CHANGE"

    def test_il4_value(self):
        assert BlueprintIronLaw.IL4_EQUIVALENCE.value == "IL4_EQUIVALENCE"

    def test_il5_value(self):
        assert BlueprintIronLaw.IL5_SOURCE_OF_TRUTH.value == "IL5_SOURCE_OF_TRUTH"

    def test_is_str_enum(self):
        assert isinstance(BlueprintIronLaw.IL1_FLAT_TOP, str)


class TestPrincipleDefs:
    def test_keys_match_arch_principle_enum(self):
        assert set(PRINCIPLE_DEFS.keys()) == set(ArchPrinciple)

    def test_each_def_has_label(self):
        for principle, definition in PRINCIPLE_DEFS.items():
            assert "label" in definition, f"Missing label for {principle}"

    def test_each_def_has_statement(self):
        for principle, definition in PRINCIPLE_DEFS.items():
            assert "statement" in definition, f"Missing statement for {principle}"

    def test_each_def_has_kb_ref(self):
        for principle, definition in PRINCIPLE_DEFS.items():
            assert "kb_ref" in definition, f"Missing kb_ref for {principle}"

    def test_each_label_non_empty(self):
        for principle, definition in PRINCIPLE_DEFS.items():
            assert len(definition["label"]) > 0, f"Empty label for {principle}"

    def test_each_statement_non_empty(self):
        for principle, definition in PRINCIPLE_DEFS.items():
            assert len(definition["statement"]) > 0, f"Empty statement for {principle}"

    def test_each_kb_ref_non_empty(self):
        for principle, definition in PRINCIPLE_DEFS.items():
            assert len(definition["kb_ref"]) > 0, f"Empty kb_ref for {principle}"

    def test_kb_refs_are_unique(self):
        refs = [d["kb_ref"] for d in PRINCIPLE_DEFS.values()]
        assert len(refs) == len(set(refs)), "Duplicate kb_ref values found"

    def test_p1_ssot_kb_ref(self):
        assert PRINCIPLE_DEFS[ArchPrinciple.P1_SSOT]["kb_ref"] == "ADR-0001"

    def test_p5_blueprint_first_kb_ref(self):
        assert PRINCIPLE_DEFS[ArchPrinciple.P5_BLUEPRINT_FIRST]["kb_ref"] == "G6"


class TestIronLawDefs:
    def test_keys_match_blueprint_iron_law_enum(self):
        assert set(IRON_LAW_DEFS.keys()) == set(BlueprintIronLaw)

    def test_all_descriptions_non_empty(self):
        for law, desc in IRON_LAW_DEFS.items():
            assert len(desc) > 0, f"Empty description for {law}"

    def test_all_descriptions_are_strings(self):
        for law, desc in IRON_LAW_DEFS.items():
            assert isinstance(desc, str), f"Non-string description for {law}"

    def test_il5_is_source_of_truth(self):
        assert "YAML" in IRON_LAW_DEFS[BlueprintIronLaw.IL5_SOURCE_OF_TRUTH]

    def test_il1_is_flat_top(self):
        assert (
            "单层" in IRON_LAW_DEFS[BlueprintIronLaw.IL1_FLAT_TOP]
            or "嵌套" in IRON_LAW_DEFS[BlueprintIronLaw.IL1_FLAT_TOP]
        )


class TestPrincpledCheck:
    def test_decorator_preserves_return_value(self):
        @princpled_check(ArchPrinciple.P1_SSOT)
        def my_func():
            return 42

        assert my_func() == 42

    def test_decorator_preserves_arguments(self):
        @princpled_check(ArchPrinciple.P4_OCP)
        def add(a, b):
            return a + b

        assert add(3, 4) == 7

    def test_decorator_sets_principles_attr(self):
        @princpled_check(ArchPrinciple.P1_SSOT, ArchPrinciple.P4_OCP)
        def my_func():
            return 0

        assert hasattr(my_func, "_zephyr_principles")
        assert my_func._zephyr_principles == [ArchPrinciple.P1_SSOT, ArchPrinciple.P4_OCP]

    def test_decorator_single_principle(self):
        @princpled_check(ArchPrinciple.P2_YAML_SCHEMA)
        def my_func():
            return "ok"

        assert my_func._zephyr_principles == [ArchPrinciple.P2_YAML_SCHEMA]

    def test_decorator_all_principles(self):
        @princpled_check(*ArchPrinciple)
        def my_func():
            return "all"

        assert len(my_func._zephyr_principles) == 5

    def test_decorator_preserves_function_name(self):
        @princpled_check(ArchPrinciple.P1_SSOT)
        def named_func():
            return 0

        assert named_func.__name__ == "named_func"

    def test_decorator_no_principles(self):
        @princpled_check()
        def my_func():
            return "empty"

        assert my_func._zephyr_principles == []
        assert my_func() == "empty"


class TestGetPrincipleByKbRef:
    def test_found_adr0001(self):
        result = get_principle_by_kb_ref("ADR-0001")
        assert result == ArchPrinciple.P1_SSOT

    def test_found_adr0002(self):
        result = get_principle_by_kb_ref("ADR-0002")
        assert result == ArchPrinciple.P2_YAML_SCHEMA

    def test_found_adr0003(self):
        result = get_principle_by_kb_ref("ADR-0003")
        assert result == ArchPrinciple.P3_DUAL_AI

    def test_found_adr0004(self):
        result = get_principle_by_kb_ref("ADR-0004")
        assert result == ArchPrinciple.P4_OCP

    def test_found_g6(self):
        result = get_principle_by_kb_ref("G6")
        assert result == ArchPrinciple.P5_BLUEPRINT_FIRST

    def test_not_found_returns_none(self):
        result = get_principle_by_kb_ref("NONEXISTENT")
        assert result is None

    def test_empty_string_returns_none(self):
        result = get_principle_by_kb_ref("")
        assert result is None

    def test_case_sensitive(self):
        result = get_principle_by_kb_ref("adr-0001")
        assert result is None

    def test_partial_match_returns_none(self):
        result = get_principle_by_kb_ref("KE-000")
        assert result is None


class TestValidateAgainstPrinciples:
    def test_no_violations_returns_true(self):
        assert validate_against_principles([]) is True

    def test_single_violation_returns_false(self):
        assert validate_against_principles(["violation 1"]) is False

    def test_multiple_violations_returns_false(self):
        assert validate_against_principles(["v1", "v2", "v3"]) is False

    def test_logs_warning_on_violation(self, caplog):
        with caplog.at_level(
            logging.WARNING, logger="zephyr.governance.architecture_governance.architecture_principles"
        ):
            validate_against_principles(["test violation"])
        assert len(caplog.records) >= 1
        assert "test violation" in caplog.text

    def test_no_log_on_no_violations(self, caplog):
        with caplog.at_level(
            logging.WARNING, logger="zephyr.governance.architecture_governance.architecture_principles"
        ):
            validate_against_principles([])
        assert len(caplog.records) == 0

    def test_logs_each_violation_separately(self, caplog):
        with caplog.at_level(
            logging.WARNING, logger="zephyr.governance.architecture_governance.architecture_principles"
        ):
            validate_against_principles(["v1", "v2"])
        assert len(caplog.records) == 2
