# [A_test] module_id: SRC-TST-1806 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable | error_contract=ImportError→skip
from __future__ import annotations

# [A_test] module_id=T-GEN_test_work_orchestrator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md | §
# [MODULE] tests.test_work_orchestrator
# [INVARIANTS] WorkOrchestrator依赖CapabilityRegistry;测试使用mock;DAG加载使用tmp_path
# [MODIFY-GUARD] src/zephyr/runtime/work_orchestrator.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] submit返回str;complete_item更新状态;acquire_slot返回bool
# [TESTS] tests/test_work_orchestrator.py
# [TTL] task_bound
from pathlib import Path
from unittest.mock import MagicMock

import yaml

from zephyr.trading.work_dag import WorkDAG, WorkEdge, WorkItem, WorkNode
from zephyr.trading.work_orchestrator import WorkOrchestrator


def _make_registry():
    return MagicMock()


class TestWorkOrchestratorInit:
    def test_default_slots(self):
        wo = WorkOrchestrator(_make_registry())
        assert wo._slots == {"trae": 1, "local": 3, "api": 2}

    def test_custom_slots(self):
        wo = WorkOrchestrator(_make_registry(), max_parallel_l1=2, max_parallel_l2=5, max_parallel_l3=3)
        assert wo._slots == {"trae": 2, "local": 5, "api": 3}


class TestRegisterDag:
    def test_register_and_get(self):
        wo = WorkOrchestrator(_make_registry())
        dag = WorkDAG(dag_id="d1", name="Test")
        wo.register_dag(dag)
        assert wo.get_dag("d1") == dag

    def test_get_missing_dag(self):
        wo = WorkOrchestrator(_make_registry())
        assert wo.get_dag("missing") is None

    def test_list_dags(self):
        wo = WorkOrchestrator(_make_registry())
        wo.register_dag(WorkDAG(dag_id="d1"))
        wo.register_dag(WorkDAG(dag_id="d2"))
        dags = wo.list_dags()
        assert len(dags) == 2


class TestLoadDags:
    def test_load_from_dir(self, tmp_path: Path):
        dag_dir = tmp_path / "dags"
        dag_dir.mkdir()
        dag_data = {"dag_id": "loaded-1", "name": "Loaded", "nodes": [], "edges": []}
        (dag_dir / "test.yaml").write_text(yaml.dump(dag_data, allow_unicode=True), encoding="utf-8")
        wo = WorkOrchestrator(_make_registry(), dag_dir=dag_dir)
        count = wo.load_dags()
        assert count == 1
        assert wo.get_dag("loaded-1") is not None

    def test_load_no_dir(self):
        wo = WorkOrchestrator(_make_registry(), dag_dir=Path("/nonexistent"))
        assert wo.load_dags() == 0

    def test_load_none_dir(self):
        wo = WorkOrchestrator(_make_registry(), dag_dir=None)
        assert wo.load_dags() == 0

    def test_load_invalid_yaml_skipped(self, tmp_path: Path):
        dag_dir = tmp_path / "dags"
        dag_dir.mkdir()
        (dag_dir / "bad.yaml").write_text("not: valid: yaml: {{{", encoding="utf-8")
        (dag_dir / "good.yaml").write_text(
            yaml.dump({"dag_id": "good-1", "nodes": [], "edges": []}, allow_unicode=True), encoding="utf-8"
        )
        wo = WorkOrchestrator(_make_registry(), dag_dir=dag_dir)
        count = wo.load_dags()
        assert count == 1


class TestSubmit:
    def test_submit_assigns_id(self):
        wo = WorkOrchestrator(_make_registry())
        item = WorkItem(item_id="", capability_id="cap-1")
        iid = wo.submit(item)
        assert iid.startswith("WI-")

    def test_submit_preserves_id(self):
        wo = WorkOrchestrator(_make_registry())
        item = WorkItem(item_id="CUSTOM-1", capability_id="cap-1")
        iid = wo.submit(item)
        assert iid == "CUSTOM-1"

    def test_submit_sets_created_at(self):
        wo = WorkOrchestrator(_make_registry())
        item = WorkItem(item_id="wi-1", capability_id="cap-1", created_at="")
        wo.submit(item)
        assert item.created_at != ""

    def test_submit_no_deps_sets_ready(self):
        wo = WorkOrchestrator(_make_registry())
        item = WorkItem(item_id="wi-1", capability_id="cap-1")
        wo.submit(item)
        assert item.status == "READY"

    def test_submit_with_deps_stays_pending(self):
        wo = WorkOrchestrator(_make_registry())
        item = WorkItem(item_id="wi-1", capability_id="cap-1", depends_on=["wi-0"])
        wo.submit(item)
        assert item.status == "PENDING"


class TestSubmitDag:
    def test_submit_dag_creates_items(self):
        wo = WorkOrchestrator(_make_registry())
        dag = WorkDAG(
            dag_id="d1",
            nodes=[
                WorkNode(node_id="n1", capability_id="cap-1"),
                WorkNode(node_id="n2", capability_id="cap-2"),
            ],
            edges=[WorkEdge(from_node="n1", to_node="n2")],
        )
        wo.register_dag(dag)
        result = wo.submit_dag("d1")
        assert result == "d1"

    def test_submit_missing_dag(self):
        wo = WorkOrchestrator(_make_registry())
        result = wo.submit_dag("missing")
        assert result == ""


class TestScheduleNext:
    def test_schedule_returns_ready_items(self):
        wo = WorkOrchestrator(_make_registry())
        wo.submit(WorkItem(item_id="wi-1", capability_id="cap-1", priority="P1"))
        wo.submit(WorkItem(item_id="wi-2", capability_id="cap-2", priority="P0"))
        ready = wo.schedule_next()
        assert len(ready) == 2
        assert ready[0].priority == "P0"

    def test_schedule_empty(self):
        wo = WorkOrchestrator(_make_registry())
        assert wo.schedule_next() == []


class TestSlotManagement:
    def test_acquire_and_release(self):
        wo = WorkOrchestrator(_make_registry())
        assert wo.acquire_slot("local") is True
        assert wo.available_slots("local") == 2
        wo.release_slot("local")
        assert wo.available_slots("local") == 3

    def test_acquire_exhausted(self):
        wo = WorkOrchestrator(_make_registry(), max_parallel_l2=1)
        assert wo.acquire_slot("local") is True
        assert wo.acquire_slot("local") is False

    def test_release_never_below_zero(self):
        wo = WorkOrchestrator(_make_registry())
        wo.release_slot("local")
        assert wo._slots_used["local"] == 0


class TestCompleteItem:
    def test_complete_success(self):
        wo = WorkOrchestrator(_make_registry())
        item = WorkItem(item_id="wi-1", capability_id="cap-1", layer="local")
        wo.submit(item)
        wo.complete_item("wi-1", result={"ok": True})
        assert wo.status("wi-1") == "COMPLETED"
        assert item.result == {"ok": True}

    def test_complete_failure(self):
        wo = WorkOrchestrator(_make_registry())
        item = WorkItem(item_id="wi-1", capability_id="cap-1", layer="local")
        wo.submit(item)
        wo.complete_item("wi-1", error="something went wrong")
        assert wo.status("wi-1") == "FAILED"
        assert item.error == "something went wrong"

    def test_complete_missing_item(self):
        wo = WorkOrchestrator(_make_registry())
        wo.complete_item("nonexistent")

    def test_complete_unblocks_dependents(self):
        wo = WorkOrchestrator(_make_registry())
        parent = WorkItem(item_id="wi-1", capability_id="cap-1", layer="local")
        child = WorkItem(item_id="wi-2", capability_id="cap-2", layer="local", depends_on=["wi-1"])
        wo.submit(parent)
        wo.submit(child)
        assert wo.status("wi-2") == "PENDING"
        wo.complete_item("wi-1", result={"done": True})
        assert wo.status("wi-2") == "READY"


class TestStatus:
    def test_status_of_submitted_item(self):
        wo = WorkOrchestrator(_make_registry())
        wo.submit(WorkItem(item_id="wi-1", capability_id="cap-1"))
        assert wo.status("wi-1") == "READY"

    def test_status_missing(self):
        wo = WorkOrchestrator(_make_registry())
        assert wo.status("missing") is None


class TestPendingCount:
    def test_pending_count(self):
        wo = WorkOrchestrator(_make_registry())
        wo.submit(WorkItem(item_id="wi-1", capability_id="cap-1", layer="local"))
        wo.submit(WorkItem(item_id="wi-2", capability_id="cap-2", layer="api"))
        counts = wo.pending_count()
        assert counts["local"] == 1
        assert counts["api"] == 1

    def test_pending_count_empty(self):
        wo = WorkOrchestrator(_make_registry())
        counts = wo.pending_count()
        assert counts == {"trae": 0, "local": 0, "api": 0}


class TestRunningCount:
    def test_running_count(self):
        wo = WorkOrchestrator(_make_registry())
        counts = wo.running_count()
        assert counts == {"trae": 0, "local": 0, "api": 0}


class TestResolveLayerAndPriority:
    def test_resolve_layer(self):
        wo = WorkOrchestrator(_make_registry())
        item = WorkItem(item_id="wi-1", capability_id="cap-1", layer="api")
        assert wo.resolve_layer(item) == "api"

    def test_resolve_priority(self):
        wo = WorkOrchestrator(_make_registry())
        item = WorkItem(item_id="wi-1", capability_id="cap-1", priority="P0")
        assert wo.resolve_priority(item) == "P0"
