# [A_test] module_id: MOD-GOV_skill_workflow | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_workflow
# [INVARIANTS] define rejects cycles; topological_order length == skills length for valid DAG
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_skill_workflow.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_workflow import SkillWorkflow


class TestSkillWorkflowInstantiation:
    def test_init(self):
        wf = SkillWorkflow()
        assert wf.workflows == {}
        assert wf.executions == {}


class TestDefine:
    def setup_method(self):
        self.wf = SkillWorkflow()

    def test_define_simple_workflow(self):
        result = self.wf.define("wf1", ["a", "b", "c"])
        assert result["status"] == "defined"
        assert result["topological_order"] == ["a", "b", "c"]

    def test_define_with_dependencies(self):
        result = self.wf.define("wf2", ["a", "b", "c"], dependencies={"b": ["a"], "c": ["b"]})
        assert result["status"] == "defined"
        assert result["topological_order"] == ["a", "b", "c"]

    def test_define_with_parallel_groups(self):
        result = self.wf.define(
            "wf3",
            ["a", "b", "c"],
            parallel_groups=[["a", "b"], ["c"]],
        )
        assert result["status"] == "defined"
        assert result["parallel_levels"] == [["a", "b"], ["c"]]

    def test_define_detects_cycle(self):
        result = self.wf.define(
            "wf_cycle",
            ["a", "b", "c"],
            dependencies={"a": ["c"], "c": ["b"], "b": ["a"]},
        )
        assert result["status"] == "invalid"
        assert result["error"] == "dependency_cycle_detected"

    def test_define_empty_skills_list(self):
        result = self.wf.define("wf_empty", [])
        assert result["status"] == "defined"
        assert result["skill_count"] == 0

    def test_define_single_skill(self):
        result = self.wf.define("wf_single", ["only_skill"])
        assert result["status"] == "defined"
        assert result["topological_order"] == ["only_skill"]

    def test_define_parallelism(self):
        result = self.wf.define(
            "wf_para",
            ["a", "b", "c", "d"],
            parallel_groups=[["a", "b", "c"], ["d"]],
        )
        assert result["parallelism"] == 3

    def test_define_stores_workflow(self):
        self.wf.define("wf_stored", ["x", "y"])
        assert "wf_stored" in self.wf.workflows

    def test_define_with_partial_dependencies(self):
        result = self.wf.define(
            "wf_partial",
            ["a", "b", "c"],
            dependencies={"c": ["a"]},
        )
        assert result["status"] == "defined"
        assert "a" in result["topological_order"]
        assert result["topological_order"].index("a") < result["topological_order"].index("c")


class TestExecute:
    def setup_method(self):
        self.wf = SkillWorkflow()

    def test_execute_nonexistent_workflow(self):
        result = self.wf.execute("no_such_wf")
        assert result["status"] == "not_found"

    def test_execute_defined_workflow(self):
        self.wf.define("wf_exec", ["a", "b"])
        result = self.wf.execute("wf_exec")
        assert result["workflow_id"] == "wf_exec"
        assert result["skill_count"] == 2

    def test_execute_stores_execution_record(self):
        self.wf.define("wf_rec", ["a"])
        self.wf.execute("wf_rec")
        assert len(self.wf.executions) > 0

    def test_execute_with_context(self):
        self.wf.define("wf_ctx", ["a"])
        result = self.wf.execute("wf_ctx", context={"key": "value"})
        assert result["workflow_id"] == "wf_ctx"

    def test_execute_empty_workflow(self):
        self.wf.define("wf_empty_exec", [])
        result = self.wf.execute("wf_empty_exec")
        assert result["skill_count"] == 0
