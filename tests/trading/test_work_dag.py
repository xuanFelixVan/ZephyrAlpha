# [A_test] module_id: MOD-GOV_work_dag | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_work_dag
# [INVARIANTS] WorkDAG/WorkNode/WorkEdge/WorkItem是Pydantic模型;测试序列化+验证
# [MODIFY-GUARD] src/zephyr/runtime/work_dag.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] WorkNode需要node_id+capability_id;WorkDAG需要dag_id;WorkItem需要item_id+capability_id
# [TESTS] tests/test_work_dag.py
# [TTL] task_bound

from __future__ import annotations

import json

from zephyr.trading.work_dag import WorkDAG, WorkEdge, WorkItem, WorkNode


class TestWorkNode:
    def test_required_fields(self):
        node = WorkNode(node_id="n1", capability_id="cap-1")
        assert node.node_id == "n1"
        assert node.capability_id == "cap-1"
        assert node.work_type == ""
        assert node.params == {}
        assert node.layer_override is None
        assert node.priority_override is None

    def test_custom_fields(self):
        node = WorkNode(
            node_id="n2",
            capability_id="cap-2",
            work_type="inference",
            params={"key": "value"},
            layer_override="api",
            priority_override="P0",
        )
        assert node.work_type == "inference"
        assert node.params == {"key": "value"}
        assert node.layer_override == "api"
        assert node.priority_override == "P0"

    def test_serialization_roundtrip(self):
        node = WorkNode(node_id="n3", capability_id="cap-3", params={"x": "1"})
        data = json.loads(node.model_dump_json())
        restored = WorkNode(**data)
        assert restored.node_id == node.node_id
        assert restored.params == node.params

    def test_missing_required_field(self):
        try:
            WorkNode(node_id="n4")
            assert False, "Should have raised validation error"
        except Exception:
            pass


class TestWorkEdge:
    def test_default_condition(self):
        edge = WorkEdge(from_node="a", to_node="b")
        assert edge.condition == "success"

    def test_custom_condition(self):
        edge = WorkEdge(from_node="a", to_node="b", condition="failure")
        assert edge.condition == "failure"

    def test_serialization(self):
        edge = WorkEdge(from_node="x", to_node="y", condition="always")
        data = json.loads(edge.model_dump_json())
        assert data["from_node"] == "x"
        assert data["to_node"] == "y"
        assert data["condition"] == "always"


class TestWorkDAG:
    def test_required_fields(self):
        dag = WorkDAG(dag_id="dag-1")
        assert dag.dag_id == "dag-1"
        assert dag.name == ""
        assert dag.nodes == []
        assert dag.edges == []
        assert dag.default_layer == "local"
        assert dag.default_priority == "P1"
        assert dag.max_parallelism == 3
        assert dag.retry_on_failure == 2
        assert dag.timeout_minutes == 60

    def test_with_nodes_and_edges(self):
        n1 = WorkNode(node_id="n1", capability_id="cap-1")
        n2 = WorkNode(node_id="n2", capability_id="cap-2")
        e1 = WorkEdge(from_node="n1", to_node="n2")
        dag = WorkDAG(
            dag_id="dag-2",
            name="Test DAG",
            nodes=[n1, n2],
            edges=[e1],
        )
        assert len(dag.nodes) == 2
        assert len(dag.edges) == 1
        assert dag.edges[0].from_node == "n1"

    def test_serialization_roundtrip(self):
        dag = WorkDAG(
            dag_id="dag-3",
            name="Roundtrip",
            nodes=[WorkNode(node_id="n1", capability_id="cap-1")],
            edges=[WorkEdge(from_node="n1", to_node="n2")],
        )
        data = json.loads(dag.model_dump_json())
        restored = WorkDAG(**data)
        assert restored.dag_id == "dag-3"
        assert len(restored.nodes) == 1
        assert len(restored.edges) == 1

    def test_missing_dag_id(self):
        try:
            WorkDAG()
            assert False, "Should have raised validation error"
        except Exception:
            pass


class TestWorkItem:
    def test_required_fields(self):
        item = WorkItem(item_id="wi-1", capability_id="cap-1")
        assert item.item_id == "wi-1"
        assert item.capability_id == "cap-1"
        assert item.status == "PENDING"
        assert item.layer == "local"
        assert item.priority == "P1"
        assert item.depends_on == []
        assert item.result is None
        assert item.error is None

    def test_custom_fields(self):
        item = WorkItem(
            item_id="wi-2",
            capability_id="cap-2",
            dag_id="dag-1",
            node_id="n1",
            work_type="embedding",
            params={"model": "bge-m3"},
            layer="api",
            priority="P0",
            status="READY",
            depends_on=["wi-1"],
        )
        assert item.dag_id == "dag-1"
        assert item.layer == "api"
        assert item.priority == "P0"
        assert item.status == "READY"
        assert item.depends_on == ["wi-1"]

    def test_serialization_roundtrip(self):
        item = WorkItem(
            item_id="wi-3",
            capability_id="cap-3",
            params={"k": "v"},
            result={"output": "done"},
        )
        data = json.loads(item.model_dump_json())
        restored = WorkItem(**data)
        assert restored.item_id == "wi-3"
        assert restored.params == {"k": "v"}
        assert restored.result == {"output": "done"}

    def test_missing_required_fields(self):
        try:
            WorkItem(item_id="wi-4")
            assert False, "Should have raised validation error"
        except Exception:
            pass

    def test_empty_depends_on(self):
        item = WorkItem(item_id="wi-5", capability_id="cap-5")
        assert item.depends_on == []
