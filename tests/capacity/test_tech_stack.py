# [A_test] module_id: SRC-TST-1729 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_tech_stack
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_tech_stack.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip("zephyr.feedback_loop.capacity_assurance.tech_stack", reason="tech_stack not available")
TechStackValidator = mod.TechStackValidator
ComponentStatus = mod.ComponentStatus


class TestComponentStatus:
    def test_instantiation(self):
        cs = ComponentStatus(dd_id="DD-1", component="test", available=True)
        assert cs.dd_id == "DD-1"
        assert cs.available is True
        assert cs.details == ""
        assert cs.suggestion == ""

    def test_with_details_and_suggestion(self):
        cs = ComponentStatus(
            dd_id="DD-2", component="test2", available=False, details="missing", suggestion="install it"
        )
        assert cs.available is False
        assert cs.details == "missing"
        assert cs.suggestion == "install it"


class TestTechStackValidator:
    def test_instantiation_with_nonexistent_manifest(self, tmp_path):
        manifest = str(tmp_path / "nonexistent.yaml")
        validator = TechStackValidator(manifest_path=manifest)
        assert len(validator.decisions) == 16

    def test_validate_returns_results(self, tmp_path):
        manifest = str(tmp_path / "nonexistent.yaml")
        validator = TechStackValidator(manifest_path=manifest)
        results = validator.validate()
        assert len(results) == 16
        for r in results:
            assert isinstance(r, ComponentStatus)

    def test_check_pydantic_v2(self, tmp_path):
        manifest = str(tmp_path / "nonexistent.yaml")
        validator = TechStackValidator(manifest_path=manifest)
        result = validator.inspect_pydantic_v2()
        assert isinstance(result, ComponentStatus)
        assert result.dd_id == "DD-1"

    def test_check_sqlite(self, tmp_path):
        manifest = str(tmp_path / "nonexistent.yaml")
        validator = TechStackValidator(manifest_path=manifest)
        result = validator.inspect_sqlite()
        assert result.available is True

    def test_check_pytest(self, tmp_path):
        manifest = str(tmp_path / "nonexistent.yaml")
        validator = TechStackValidator(manifest_path=manifest)
        result = validator.inspect_pytest()
        assert result.available is True

    def test_report_generates_string(self, tmp_path):
        manifest = str(tmp_path / "nonexistent.yaml")
        validator = TechStackValidator(manifest_path=manifest)
        report = validator.report()
        assert isinstance(report, str)
        assert "ZephyrAlpha" in report or "总计" in report

    def test_default_decisions_count(self, tmp_path):
        manifest = str(tmp_path / "nonexistent.yaml")
        validator = TechStackValidator(manifest_path=manifest)
        assert len(validator._default_decisions()) == 16

    def test_validate_on_startup(self, tmp_path):
        manifest = str(tmp_path / "nonexistent.yaml")
        result = mod.validate_on_startup(manifest_path=manifest)
        assert isinstance(result, bool)
