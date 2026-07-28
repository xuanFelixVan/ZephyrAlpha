# [A_test] module_id: MOD-GOV_skill_contract | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_contract
# [INVARIANTS] SkillContract.validate_contracts must detect missing/short contracts
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 = all pass; exit != 0 = regression
# [TESTS] tests/test_skill_contract.py
# [TTL] task_bound


from zephyr.autonomy_core.skills.skill_contract import SkillContract


class TestSkillContractInstantiation:
    def test_class_has_contract_types(self):
        assert "input_schema" in SkillContract._CONTRACT_TYPES
        assert "output_schema" in SkillContract._CONTRACT_TYPES
        assert "side_effects" in SkillContract._CONTRACT_TYPES
        assert "dependencies" in SkillContract._CONTRACT_TYPES

    def test_contract_types_count(self):
        assert len(SkillContract._CONTRACT_TYPES) == 4


class TestParseContracts:
    def test_parse_input_schema(self):
        body = "输入：\nname: str\nage: int\n\nOther text"
        result = SkillContract.parse_contracts(body)
        assert "input_schema" in result
        assert "name" in result["input_schema"]

    def test_parse_output_schema(self):
        body = "输出：\nresult: dict\nstatus: str\n\nOther"
        result = SkillContract.parse_contracts(body)
        assert "output_schema" in result

    def test_parse_side_effects(self):
        body = "副作用：\nWrites to database\nSends email\n\nOther"
        result = SkillContract.parse_contracts(body)
        assert "side_effects" in result

    def test_parse_dependencies(self):
        body = "依赖：\nzephyr.shared\nzephyr.knowledge.kb\n\nOther"
        result = SkillContract.parse_contracts(body)
        assert "dependencies" in result

    def test_parse_english_keywords(self):
        body = "input:\nname: str\n\noutput:\nresult: dict\n\nside_effects:\nNone\n\ndependencies:\nos, sys"
        result = SkillContract.parse_contracts(body)
        assert "input_schema" in result
        assert "output_schema" in result
        assert "side_effects" in result
        assert "dependencies" in result

    def test_parse_empty_body(self):
        result = SkillContract.parse_contracts("")
        assert result == {}

    def test_parse_no_matching_sections(self):
        result = SkillContract.parse_contracts("Just some random text\nwith no contract sections")
        assert result == {}

    def test_parse_truncates_long_content(self):
        long_content = "x" * 600
        body = f"输入：\n{long_content}\n\nEnd"
        result = SkillContract.parse_contracts(body)
        if "input_schema" in result:
            assert len(result["input_schema"]) <= 500


class TestValidateContracts:
    def test_valid_contracts_with_body(self):
        body = "输入：\nname: str - the user name\nage: int - the user age\n\n输出：\nresult: dict - the processed result\nstatus: str - the status code"
        result = SkillContract.validate_contracts("test-skill", body=body)
        assert result["skill_id"] == "test-skill"
        assert result["contracts_valid"] is True
        assert result["violations"] == []

    def test_missing_input_schema_warning(self):
        body = "输出：\nresult: dict - the processed result\nstatus: str - the status code"
        result = SkillContract.validate_contracts("test-skill", body=body)
        assert result["contracts_valid"] is False
        missing_types = [v["contract"] for v in result["violations"]]
        assert "input_schema" in missing_types

    def test_missing_output_schema_high_severity(self):
        body = "输入：\nname: str - the user name\nage: int - the user age"
        result = SkillContract.validate_contracts("test-skill", body=body)
        output_violations = [v for v in result["violations"] if v["contract"] == "output_schema"]
        assert len(output_violations) == 1
        assert output_violations[0]["severity"] == "high"

    def test_contract_too_short(self):
        body = "输入：\nshort\n\n输出：\nalso short"
        result = SkillContract.validate_contracts("test-skill", body=body)
        short_violations = [v for v in result["violations"] if v["type"] == "contract_too_short"]
        assert len(short_violations) >= 1

    def test_none_body_load_failure(self):
        result = SkillContract.validate_contracts("nonexistent-skill", body=None)
        assert result["contracts_valid"] is False
        assert "error" in result
        assert result["error"] == "load_failed"

    def test_empty_body(self):
        result = SkillContract.validate_contracts("test-skill", body="")
        assert result["contracts_valid"] is False
        assert len(result["violations"]) >= 2

    def test_contracts_found_and_missing(self):
        body = "输入：\nname: str - the user name\n\n副作用：\nNone - no side effects at all here"
        result = SkillContract.validate_contracts("test-skill", body=body)
        assert "input_schema" in result["contracts_found"]
        assert "side_effects" in result["contracts_found"]
        assert "output_schema" in result["contracts_missing"]

    def test_no_critical_severity_means_not_blocked(self):
        body = "输入：\nshort\n\n输出：\nalso short"
        result = SkillContract.validate_contracts("test-skill", body=body)
        has_critical = any(v.get("severity") == "critical" for v in result["violations"])
        assert has_critical is False

    def test_full_contract_all_types(self):
        body = "输入：\nname: str - the user name\nage: int - the user age\n\n输出：\nresult: dict - the processed result\nstatus: str - the status code\n\n副作用：\nWrites to database - persists user data\nSends email - notifies admin\n\n依赖：\nzephyr.shared - common utilities\nzephyr.knowledge.kb - knowledge base access"
        result = SkillContract.validate_contracts("test-skill", body=body)
        assert len(result["contracts_found"]) == 4
        assert len(result["contracts_missing"]) == 0
