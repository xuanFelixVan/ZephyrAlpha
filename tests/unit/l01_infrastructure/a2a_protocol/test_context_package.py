"""测试: Context Package"""

import pytest
from zephyr.l01_infrastructure.a2a_protocol.layer2_communication.context_package import ContextPackage


class TestContextPackage:
    def test_create_context(self):
        ctx = ContextPackage(task_id="a2a-task-x", source_agent="agent-x")
        assert ctx.task_id == "a2a-task-x"

    def test_add_blueprint(self):
        ctx = ContextPackage(task_id="a2a-task-x", source_agent="agent-x")
        ctx.add_blueprint("bp1", "blueprint content")
        assert "bp1" in ctx.blueprints

    def test_to_dict(self):
        ctx = ContextPackage(task_id="a2a-task-x", source_agent="agent-x")
        d = ctx.to_dict()
        assert d["task_id"] == "a2a-task-x"
        assert d["blueprint_count"] == 0
