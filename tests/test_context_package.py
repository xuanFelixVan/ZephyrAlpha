# [A_test] module_id: SRC-TST-0601 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain-infra_ops/a2a-protocol/blueprint.md | §
# [MODULE] tests.test_context_package
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_context_package.py

from zephyr.governance.context_package import ContextPackage


class TestContextPackage:
    def test_create(self):
        cp = ContextPackage(task_id="task-1", source_agent="agent-a")
        assert cp.task_id == "task-1"
        assert cp.source_agent == "agent-a"
        assert cp.blueprints == {}
        assert cp.decisions == []
        assert cp.session_state == {}
        assert cp.locks_held == []

    def test_add_blueprint(self):
        cp = ContextPackage(task_id="task-1", source_agent="agent-a")
        cp.add_blueprint("mod-inf-025", "blueprint content here")
        assert "mod-inf-025" in cp.blueprints
        assert cp.blueprints["mod-inf-025"] == "blueprint content here"

    def test_add_decision(self):
        cp = ContextPackage(task_id="task-1", source_agent="agent-a")
        cp.add_decision("dec-001", {"choice": "approve"})
        assert len(cp.decisions) == 1
        assert cp.decisions[0]["id"] == "dec-001"
        assert cp.decisions[0]["data"] == {"choice": "approve"}

    def test_set_session_state(self):
        cp = ContextPackage(task_id="task-1", source_agent="agent-a")
        state = {"phase": "construction", "step": 3}
        cp.set_session_state(state)
        assert cp.session_state == state

    def test_to_dict(self):
        cp = ContextPackage(task_id="task-1", source_agent="agent-a")
        cp.add_blueprint("bp1", "content")
        cp.add_decision("d1", {"x": 1})
        cp.set_session_state({"key": "val"})
        d = cp.to_dict()
        assert d["task_id"] == "task-1"
        assert d["source_agent"] == "agent-a"
        assert d["blueprint_count"] == 1
        assert d["decision_count"] == 1
        assert d["session_state_keys"] == ["key"]

    def test_empty_to_dict(self):
        cp = ContextPackage(task_id="task-2", source_agent="agent-b")
        d = cp.to_dict()
        assert d["blueprint_count"] == 0
        assert d["decision_count"] == 0
        assert d["session_state_keys"] == []

    def test_add_multiple_blueprints(self):
        cp = ContextPackage(task_id="task-1", source_agent="agent-a")
        cp.add_blueprint("bp1", "c1")
        cp.add_blueprint("bp2", "c2")
        assert len(cp.blueprints) == 2
