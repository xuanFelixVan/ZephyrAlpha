# [A_test] module_id: MOD-GOV_blueprint_reconciler | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_blueprint_reconciler
# [INVARIANTS] must test all public classes and methods of blueprint_reconciler
# [MODIFY-GUARD] blueprint_reconciler.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/test_blueprint_reconciler.py
# [TTL] task_bound

from zephyr.governance.architecture_governance.blueprint_reconciler import BlueprintReconciler


class TestBlueprintReconciler:
    def test_instantiation(self):
        r = BlueprintReconciler()
        assert r is not None

    def test_verify_module_consistent(self):
        r = BlueprintReconciler()
        result = r.verify_module(
            blueprint_specs={"files": ["a.py", "b.py"]},
            implementation_files=["a.py", "b.py"],
        )
        assert result["consistent"] is True
        assert result["missing"] == []
        assert result["extra"] == []

    def test_verify_module_missing_files(self):
        r = BlueprintReconciler()
        result = r.verify_module(
            blueprint_specs={"files": ["a.py", "b.py", "c.py"]},
            implementation_files=["a.py"],
        )
        assert result["consistent"] is False
        assert "b.py" in result["missing"]
        assert "c.py" in result["missing"]

    def test_verify_module_extra_files(self):
        r = BlueprintReconciler()
        result = r.verify_module(
            blueprint_specs={"files": ["a.py"]},
            implementation_files=["a.py", "extra.py"],
        )
        assert result["consistent"] is True
        assert "extra.py" in result["extra"]

    def test_verify_module_empty_specs(self):
        r = BlueprintReconciler()
        result = r.verify_module(
            blueprint_specs={},
            implementation_files=["a.py"],
        )
        assert result["consistent"] is True
        assert result["missing"] == []
        assert "a.py" in result["extra"]

    def test_verify_module_empty_implementation(self):
        r = BlueprintReconciler()
        result = r.verify_module(
            blueprint_specs={"files": ["a.py"]},
            implementation_files=[],
        )
        assert result["consistent"] is False
        assert "a.py" in result["missing"]

    def test_verify_module_both_empty(self):
        r = BlueprintReconciler()
        result = r.verify_module(
            blueprint_specs={"files": []},
            implementation_files=[],
        )
        assert result["consistent"] is True
        assert result["missing"] == []
        assert result["extra"] == []

    def test_verify_module_no_files_key(self):
        r = BlueprintReconciler()
        result = r.verify_module(
            blueprint_specs={"other_key": "value"},
            implementation_files=["a.py"],
        )
        assert result["consistent"] is True
