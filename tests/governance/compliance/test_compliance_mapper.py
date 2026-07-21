# [A_test] module_id: MOD-GOV_compliance_mapper | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §

# [MODULE] tests.test_compliance_mapper

# [INVARIANTS] 合规映射必须同步法律变更;blocked操作必须同步确认

# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md

# [CONSUMERS] pytest

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 测试异常必须包含 context 和 rule_id

# [TESTS] tests/test_compliance_mapper.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.compliance_gate_a6.compliance_mapper import COMPLIANCE_MAP, ComplianceMapper


class TestComplianceMapperInstantiation:
    def test_creates_instance(self):
        mapper = ComplianceMapper()
        assert mapper is not None

    def test_instance_has_check_method(self):
        mapper = ComplianceMapper()
        assert callable(getattr(mapper, "check", None))

    def test_instance_has_requires_escalation_method(self):
        mapper = ComplianceMapper()
        assert callable(getattr(mapper, "requires_escalation", None))


class TestCheck:
    def test_known_operation_modify_financial_data(self):
        mapper = ComplianceMapper()
        result = mapper.check("modify_financial_data")
        assert result == {"sox": True, "gdpr": False, "mifid": True}

    def test_known_operation_access_personal_data(self):
        mapper = ComplianceMapper()
        result = mapper.check("access_personal_data")
        assert result == {"sox": False, "gdpr": True, "mifid": False}

    def test_known_operation_execute_trade(self):
        mapper = ComplianceMapper()
        result = mapper.check("execute_trade")
        assert result == {"sox": True, "gdpr": False, "mifid": True}

    def test_known_operation_delete_audit_log(self):
        mapper = ComplianceMapper()
        result = mapper.check("delete_audit_log")
        assert result == {"sox": True, "gdpr": False, "mifid": True}

    def test_unknown_operation_returns_all_false(self):
        mapper = ComplianceMapper()
        result = mapper.check("nonexistent_operation")
        assert result == {"sox": False, "gdpr": False, "mifid": False}

    def test_empty_string_returns_all_false(self):
        mapper = ComplianceMapper()
        result = mapper.check("")
        assert result == {"sox": False, "gdpr": False, "mifid": False}

    def test_none_input_returns_all_false(self):
        mapper = ComplianceMapper()
        result = mapper.check(None)
        assert result == {"sox": False, "gdpr": False, "mifid": False}

    def test_result_is_dict_with_three_keys(self):
        mapper = ComplianceMapper()
        result = mapper.check("modify_financial_data")
        assert set(result.keys()) == {"sox", "gdpr", "mifid"}

    def test_result_values_are_bool(self):
        mapper = ComplianceMapper()
        result = mapper.check("modify_financial_data")
        for v in result.values():
            assert isinstance(v, bool)


class TestRequiresEscalation:
    def test_sox_operation_requires_escalation(self):
        mapper = ComplianceMapper()
        assert mapper.requires_escalation("modify_financial_data") is True

    def test_gdpr_operation_requires_escalation(self):
        mapper = ComplianceMapper()
        assert mapper.requires_escalation("access_personal_data") is True

    def test_unknown_operation_no_escalation(self):
        mapper = ComplianceMapper()
        assert mapper.requires_escalation("nonexistent_operation") is False

    def test_empty_string_no_escalation(self):
        mapper = ComplianceMapper()
        assert mapper.requires_escalation("") is False

    def test_none_input_no_escalation(self):
        mapper = ComplianceMapper()
        assert mapper.requires_escalation(None) is False

    def test_all_regulation_operation_requires_escalation(self):
        mapper = ComplianceMapper()
        assert mapper.requires_escalation("delete_audit_log") is True


class TestComplianceMapConsistency:
    def test_compliance_map_has_four_entries(self):
        assert len(COMPLIANCE_MAP) == 4

    def test_all_entries_have_three_regulations(self):
        for op, regs in COMPLIANCE_MAP.items():
            assert set(regs.keys()) == {"sox", "gdpr", "mifid"}, f"operation {op} missing regulation keys"

    def test_all_regulation_values_are_bool(self):
        for op, regs in COMPLIANCE_MAP.items():
            for reg, val in regs.items():
                assert isinstance(val, bool), f"operation {op} regulation {reg} value is not bool"

    def test_check_matches_compliance_map(self):
        mapper = ComplianceMapper()
        for op, expected in COMPLIANCE_MAP.items():
            assert mapper.check(op) == expected
