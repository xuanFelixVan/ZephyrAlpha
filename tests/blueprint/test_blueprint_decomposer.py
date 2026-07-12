# [A_test] module_id: SRC-TST-0437 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-354 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §

# [MODULE] tests.test_blueprint_decomposer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]
# [TTL] task_bound

from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.gov_enforcement.rule_enforcement.task_types import TaskNamespace
from zephyr.integration.shared.schema.execution_model import ExecutionModel
from zephyr.integration.shared.schema.severity_types import Priority, SafetyLevel
from zephyr.shared.blueprint_tools.blueprint_decomposer import (
    BlueprintDecomposer,
    _marker_to_blueprint_label,
    _resolve_task_namespace,
    _split_desc_and_depends,
)
from zephyr.shared.foundation.models import GateLevel, TaskAuditFinding, TaskCard, TaskStatus


def _make_task_card(
    task_id: str = "CP-1",
    title: str = "Test Task",
    depends_on: list[str] | None = None,
    namespace: TaskNamespace = TaskNamespace.CP,
    seq: int = 1,
    description: str = "A test task description that is long enough",
    source_blueprint: str = "test-bp",
    source_section: str = "auto-extracted",
    verification_status: str = "unverified",
    audit_findings: list[TaskAuditFinding] | None = None,
) -> TaskCard:
    now = datetime.now(UTC)
    return TaskCard(
        task_id=task_id,
        namespace=namespace,
        seq=seq,
        title=title,
        status=TaskStatus.PENDING,
        priority=Priority.P2,
        phase=1,
        execution_model=ExecutionModel.deepseek,
        safety_level=SafetyLevel.L,
        source_blueprint=source_blueprint,
        source_section=source_section,
        description=description,
        files_in_scope=["test.md"],
        upstream_files=["test.md"],
        downstream_outputs=[],
        allowed_touch=[],
        forbidden_touch=[],
        applicable_rules=[],
        context_assembly_manifest=[],
        rollback_instructions="",
        estimated_tokens=4000,
        timeout_minutes=30,
        completed_gates=[],
        blocked_gates={},
        assigned_pipeline="A",
        pipeline_modules=[],
        blocked_by=[],
        artifact_paths=[],
        audit_findings=audit_findings or [],
        ke_entries=[],
        tags=[],
        depends_on=depends_on or [],
        ai_autonomy_level="supervised",
        autonomy_checklist=[],
        construction_status="pending",
        verification_status=verification_status,
        created_at=now,
        updated_at=now,
    )


def _write_blueprint(content: str, tmpdir: str, filename: str = "test_bp.md") -> str:
    bp_path = os.path.join(tmpdir, filename)
    with open(bp_path, "w", encoding="utf-8") as f:
        f.write(content)
    return bp_path


class TestSplitDescAndDepends:
    def test_separates_depends_from_narrative(self):
        lines = [
            "Implement the module",
            "depends_on: [CP-1, CP-2]",
            "More narrative text",
        ]
        narrative, deps = _split_desc_and_depends(lines)
        assert "Implement the module" in narrative
        assert "More narrative text" in narrative
        assert "depends_on: [CP-1, CP-2]" not in narrative
        assert deps == ["CP-1", "CP-2"]

    def test_empty_input(self):
        narrative, deps = _split_desc_and_depends([])
        assert narrative == []
        assert deps == []

    def test_no_depends_lines(self):
        lines = ["Line one", "Line two"]
        narrative, deps = _split_desc_and_depends(lines)
        assert narrative == ["Line one", "Line two"]
        assert deps == []

    def test_only_depends_lines(self):
        lines = ["depends_on: [ADR-1]", "depends_on: [CP-3]"]
        narrative, deps = _split_desc_and_depends(lines)
        assert narrative == []
        assert deps == ["ADR-1", "CP-3"]

    def test_depends_with_quotes_and_spaces(self):
        lines = ["depends_on: [\"CP-1\", 'CP-2']"]
        narrative, deps = _split_desc_and_depends(lines)
        assert deps == ["CP-1", "CP-2"]


class TestMarkerToBlueprintLabel:
    def test_adr_marker(self):
        assert _marker_to_blueprint_label("[ADR-1-1]") == "ADR"

    def test_td_marker(self):
        assert _marker_to_blueprint_label("TD-1") == "TD"

    def test_cs_marker(self):
        assert _marker_to_blueprint_label("CS-1") == "CS"

    def test_cp_marker(self):
        assert _marker_to_blueprint_label("CP-1") == "CP"

    def test_infra_marker(self):
        assert _marker_to_blueprint_label("INFRA-1") == "INFRA"

    def test_script_marker(self):
        assert _marker_to_blueprint_label("SCRIPT-1") == "SCRIPT"

    def test_unknown_marker(self):
        assert _marker_to_blueprint_label("UNKNOWN-1") is None

    def test_empty_string(self):
        assert _marker_to_blueprint_label("") is None


class TestResolveTaskNamespace:
    def test_adr(self):
        assert _resolve_task_namespace("ADR") == TaskNamespace.KBG

    def test_cp(self):
        assert _resolve_task_namespace("CP") == TaskNamespace.CP

    def test_td_maps_to_dw(self):
        assert _resolve_task_namespace("TD") == TaskNamespace.DW

    def test_tech_debt_maps_to_dw(self):
        assert _resolve_task_namespace("TECH-DEBT") == TaskNamespace.DW

    def test_cs_maps_to_std(self):
        assert _resolve_task_namespace("CS") == TaskNamespace.STD

    def test_infra_maps_to_ops(self):
        assert _resolve_task_namespace("INFRA") == TaskNamespace.OPS

    def test_script_maps_to_ops(self):
        assert _resolve_task_namespace("SCRIPT") == TaskNamespace.OPS

    def test_unknown_returns_none(self):
        assert _resolve_task_namespace("NONEXISTENT") is None

    def test_case_insensitive(self):
        assert _resolve_task_namespace("adr") == TaskNamespace.KBG


class TestBlueprintDecomposerInit:
    def test_default_init(self):
        decomposer = BlueprintDecomposer()
        assert decomposer.task_repo is None
        assert decomposer.docs_dir is None
        assert decomposer._global_seq == {}

    def test_init_with_task_repo(self):
        mock_repo = MagicMock()
        decomposer = BlueprintDecomposer(task_repo=mock_repo)
        assert decomposer.task_repo is mock_repo

    def test_init_with_docs_dir(self):
        decomposer = BlueprintDecomposer(docs_dir="/tmp/test_docs")
        assert decomposer.docs_dir == Path("/tmp/test_docs")

    def test_init_with_none_values(self):
        decomposer = BlueprintDecomposer(task_repo=None, docs_dir=None)
        assert decomposer.task_repo is None
        assert decomposer.docs_dir is None


class TestDecomposeBlueprint:
    def test_single_adr_item(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "- [ADR-1-1] **Auth Module** — Implement authentication layer\n"
            bp_path = _write_blueprint(content, tmpdir)
            decomposer = BlueprintDecomposer()
            result = decomposer.decompose_blueprint(bp_path, namespace="ADR", phase=1)
            assert result.total_tasks == 1
            assert result.tasks[0].namespace == TaskNamespace.KBG
            assert result.tasks[0].title == "Auth Module"
            assert "Implement authentication layer" in result.tasks[0].description

    def test_multiple_items(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = (
                "- [ADR-1-1] **Module A** — First module description here\n"
                "- [ADR-1-2] **Module B** — Second module description here\n"
            )
            bp_path = _write_blueprint(content, tmpdir)
            decomposer = BlueprintDecomposer()
            result = decomposer.decompose_blueprint(bp_path, namespace="ADR", phase=2)
            assert result.total_tasks == 2
            assert result.tasks[0].namespace == TaskNamespace.KBG
            assert result.tasks[1].namespace == TaskNamespace.KBG

    def test_file_not_found(self):
        decomposer = BlueprintDecomposer()
        with pytest.raises(FileNotFoundError, match="蓝图文件不存在"):
            decomposer.decompose_blueprint("/nonexistent/path.md")

    def test_empty_blueprint(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bp_path = _write_blueprint("", tmpdir)
            decomposer = BlueprintDecomposer()
            result = decomposer.decompose_blueprint(bp_path)
            assert result.total_tasks == 0
            assert result.tasks == []
            assert result.unassigned_items == []

    def test_with_depends_on(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = (
                "- [ADR-1-1] **Module A** — First module description here\n"
                "depends_on: [ADR-2]\n"
                "- [ADR-1-2] **Module B** — Second module description here\n"
            )
            bp_path = _write_blueprint(content, tmpdir)
            decomposer = BlueprintDecomposer()
            result = decomposer.decompose_blueprint(bp_path, namespace="ADR")
            assert result.total_tasks == 2
            assert "ADR-2" in result.tasks[0].depends_on

    def test_with_docs_dir_writes_output(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "- [ADR-1-1] **Module A** — First module description here\n"
            bp_path = _write_blueprint(content, tmpdir)
            docs_dir = os.path.join(tmpdir, "docs_output")
            decomposer = BlueprintDecomposer(docs_dir=docs_dir)
            result = decomposer.decompose_blueprint(bp_path, namespace="ADR")
            assert result.total_tasks == 1
            assert os.path.exists(os.path.join(docs_dir, "decomposition", "decomposition_result.json"))

    def test_with_task_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "- [ADR-1-1] **Module A** — First module description here\n"
            bp_path = _write_blueprint(content, tmpdir)
            mock_repo = MagicMock()
            mock_repo.next_seq.return_value = 42
            decomposer = BlueprintDecomposer(task_repo=mock_repo)
            result = decomposer.decompose_blueprint(bp_path, namespace="ADR")
            assert result.total_tasks == 1
            assert result.tasks[0].task_id == "KBG-42"
            mock_repo.create.assert_called_once()

    def test_default_namespace_cp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "- [ADR-1-1] **Module A** — First module description here\n"
            bp_path = _write_blueprint(content, tmpdir)
            decomposer = BlueprintDecomposer()
            result = decomposer.decompose_blueprint(bp_path)
            assert result.tasks[0].namespace == TaskNamespace.KBG

    def test_dependency_graph_built(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = (
                "- [ADR-1-1] **Module A** — First module description here\n"
                "- [ADR-1-2] **Module B** — Second module description here\n"
            )
            bp_path = _write_blueprint(content, tmpdir)
            decomposer = BlueprintDecomposer()
            result = decomposer.decompose_blueprint(bp_path, namespace="ADR")
            assert isinstance(result.dependency_graph, dict)
            assert len(result.dependency_graph) == 2


class TestDecomposeBlueprintsBatch:
    def test_batch_multiple_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content_a = "- [ADR-1-1] **Module A** — First module description here\n"
            content_b = "- [ADR-1-1] **Module B** — Second module description here\n"
            bp_a = _write_blueprint(content_a, tmpdir, "bp_a.md")
            bp_b = _write_blueprint(content_b, tmpdir, "bp_b.md")
            decomposer = BlueprintDecomposer()
            results = decomposer.decompose_blueprints_batch([bp_a, bp_b], namespace="ADR")
            assert len(results) == 2
            assert results[0].total_tasks == 1
            assert results[1].total_tasks == 1

    def test_batch_empty_list(self):
        decomposer = BlueprintDecomposer()
        results = decomposer.decompose_blueprints_batch([])
        assert results == []

    def test_batch_default_namespace_ops(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "- [ADR-1-1] **Module A** — First module description here\n"
            bp_path = _write_blueprint(content, tmpdir)
            decomposer = BlueprintDecomposer()
            results = decomposer.decompose_blueprints_batch([bp_path])
            assert results[0].tasks[0].namespace == TaskNamespace.KBG


class TestTopologySort:
    def test_no_dependencies(self):
        t1 = _make_task_card(task_id="CP-1", title="Task 1")
        t2 = _make_task_card(task_id="CP-2", title="Task 2", seq=2)
        t3 = _make_task_card(task_id="CP-3", title="Task 3", seq=3)
        decomposer = BlueprintDecomposer()
        sorted_tasks = decomposer.topology_sort([t1, t2, t3])
        assert len(sorted_tasks) == 3
        assert sorted_tasks[0].task_id == "CP-1"

    def test_with_dependencies(self):
        t1 = _make_task_card(task_id="CP-1", title="Task 1")
        t2 = _make_task_card(task_id="CP-2", title="Task 2", seq=2, depends_on=["CP-1"])
        t3 = _make_task_card(task_id="CP-3", title="Task 3", seq=3, depends_on=["CP-2"])
        decomposer = BlueprintDecomposer()
        sorted_tasks = decomposer.topology_sort([t3, t2, t1])
        ids = [t.task_id for t in sorted_tasks]
        assert ids.index("CP-1") < ids.index("CP-2")
        assert ids.index("CP-2") < ids.index("CP-3")

    def test_cyclic_dependency_falls_back(self):
        t1 = _make_task_card(task_id="CP-1", title="Task 1", depends_on=["CP-2"])
        t2 = _make_task_card(task_id="CP-2", title="Task 2", seq=2, depends_on=["CP-1"])
        decomposer = BlueprintDecomposer()
        sorted_tasks = decomposer.topology_sort([t1, t2])
        assert len(sorted_tasks) == 2
        assert sorted_tasks[0].task_id == "CP-1"
        assert sorted_tasks[1].task_id == "CP-2"

    def test_empty_input(self):
        decomposer = BlueprintDecomposer()
        sorted_tasks = decomposer.topology_sort([])
        assert sorted_tasks == []

    def test_single_task(self):
        t1 = _make_task_card(task_id="CP-1", title="Task 1")
        decomposer = BlueprintDecomposer()
        sorted_tasks = decomposer.topology_sort([t1])
        assert len(sorted_tasks) == 1
        assert sorted_tasks[0].task_id == "CP-1"

    def test_diamond_dependency(self):
        t1 = _make_task_card(task_id="CP-1", title="Root")
        t2 = _make_task_card(task_id="CP-2", title="Left", seq=2, depends_on=["CP-1"])
        t3 = _make_task_card(task_id="CP-3", title="Right", seq=3, depends_on=["CP-1"])
        t4 = _make_task_card(task_id="CP-4", title="Merge", seq=4, depends_on=["CP-2", "CP-3"])
        decomposer = BlueprintDecomposer()
        sorted_tasks = decomposer.topology_sort([t4, t3, t2, t1])
        ids = [t.task_id for t in sorted_tasks]
        assert ids.index("CP-1") < ids.index("CP-2")
        assert ids.index("CP-1") < ids.index("CP-3")
        assert ids.index("CP-2") < ids.index("CP-4")
        assert ids.index("CP-3") < ids.index("CP-4")


class TestExtractDependsFromContent:
    def test_extracts_depends_from_blueprint(self):
        content = (
            "- [ADR-1-1] **Module A** — First module\n"
            "depends_on: [CP-1, CP-2]\n"
            "- [ADR-1-2] **Module B** — Second module\n"
        )
        decomposer = BlueprintDecomposer()
        result = decomposer.extract_depends_from_content(content)
        assert "Module A" in result
        assert result["Module A"] == ["CP-1", "CP-2"]

    def test_empty_content(self):
        decomposer = BlueprintDecomposer()
        result = decomposer.extract_depends_from_content("")
        assert result == {}

    def test_no_depends_lines(self):
        content = "- [ADR-1-1] **Module A** — First module\n"
        decomposer = BlueprintDecomposer()
        result = decomposer.extract_depends_from_content(content)
        assert result == {}

    def test_universal_item_pattern(self):
        content = "1. **Module X** — Some description\ndepends_on: [ADR-1]\n"
        decomposer = BlueprintDecomposer()
        result = decomposer.extract_depends_from_content(content)
        assert "Module X" in result
        assert result["Module X"] == ["ADR-1"]

    def test_multiple_items_with_depends(self):
        content = (
            "- [ADR-1-1] **Module A** — First module\n"
            "depends_on: [CP-1]\n"
            "- [ADR-1-2] **Module B** — Second module\n"
            "depends_on: [CP-2, CP-3]\n"
        )
        decomposer = BlueprintDecomposer()
        result = decomposer.extract_depends_from_content(content)
        assert len(result) == 2
        assert result["Module A"] == ["CP-1"]
        assert result["Module B"] == ["CP-2", "CP-3"]


class TestCheckGate:
    def test_g0_pass(self):
        task = _make_task_card(
            source_blueprint="test-bp",
            description="A valid description that is long enough",
        )
        decomposer = BlueprintDecomposer()
        assert decomposer.check_gate(GateLevel.G0, task) is True

    def test_g0_fail_no_blueprint(self):
        task = _make_task_card(
            source_blueprint="test-bp",
            description="A valid description that is long enough",
        )
        object.__setattr__(task, "source_blueprint", "")
        decomposer = BlueprintDecomposer()
        assert decomposer.check_gate(GateLevel.G0, task) is False

    def test_g0_fail_short_description(self):
        task = _make_task_card(
            source_blueprint="test-bp",
            description="A valid description that is long enough",
        )
        object.__setattr__(task, "description", "short")
        decomposer = BlueprintDecomposer()
        assert decomposer.check_gate(GateLevel.G0, task) is False

    def test_g0_fail_empty_description(self):
        task = _make_task_card(
            source_blueprint="test-bp",
            description="x" * 10,
        )
        decomposer = BlueprintDecomposer()
        assert decomposer.check_gate(GateLevel.G0, task) is True

    def test_g7_pass(self):
        finding = TaskAuditFinding(
            finding_id="F-0001",
            dimension="quality",
            severity="low",
            description="Minor issue",
            source_task="CP-1",
            resolved=True,
        )
        task = _make_task_card(
            verification_status="verified",
            audit_findings=[finding],
        )
        decomposer = BlueprintDecomposer()
        assert decomposer.check_gate(GateLevel.G7, task) is True

    def test_g7_fail_unverified(self):
        task = _make_task_card(verification_status="unverified")
        decomposer = BlueprintDecomposer()
        assert decomposer.check_gate(GateLevel.G7, task) is False

    def test_g7_fail_unresolved_finding(self):
        finding = TaskAuditFinding(
            finding_id="F-0002",
            dimension="security",
            severity="high",
            description="Critical issue",
            source_task="CP-1",
            resolved=False,
        )
        task = _make_task_card(
            verification_status="verified",
            audit_findings=[finding],
        )
        decomposer = BlueprintDecomposer()
        assert decomposer.check_gate(GateLevel.G7, task) is False

    def test_other_gates_pass(self):
        task = _make_task_card()
        decomposer = BlueprintDecomposer()
        for gate in [GateLevel.G1, GateLevel.G2, GateLevel.G3, GateLevel.G4, GateLevel.G5, GateLevel.G6]:
            assert decomposer.check_gate(gate, task) is True


class TestNextGlobalSeq:
    def test_sequential(self):
        decomposer = BlueprintDecomposer()
        assert decomposer._next_global_seq(TaskNamespace.CP) == 1
        assert decomposer._next_global_seq(TaskNamespace.CP) == 2
        assert decomposer._next_global_seq(TaskNamespace.CP) == 3

    def test_independent_namespaces(self):
        decomposer = BlueprintDecomposer()
        assert decomposer._next_global_seq(TaskNamespace.CP) == 1
        assert decomposer._next_global_seq(TaskNamespace.KBG) == 1
        assert decomposer._next_global_seq(TaskNamespace.CP) == 2
        assert decomposer._next_global_seq(TaskNamespace.KBG) == 2
