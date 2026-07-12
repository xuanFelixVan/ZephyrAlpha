# [A_test] module_id: SRC-TST-1171 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_migration_gate
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_kb.kb_gate_task import _GATE_SEQ, build_kb_gate_eval_task
from zephyr.governance.rule_enforcement.task_types import Task, TaskNamespace, TaskStatus


class TestBuildKbGateEvalTask:
    def test_build_g1_task(self, tmp_path):
        deliverable = tmp_path / "g1_result.md"
        deliverable.write_text("G1 output", encoding="utf-8")
        task = build_kb_gate_eval_task(gate_id="G1", title="G1 Ingest Gate", deliverable=deliverable)
        assert isinstance(task, Task)
        assert task.task_id == "KBG-9101"
        assert task.namespace == TaskNamespace.KBG
        assert task.seq == 9101
        assert task.title == "G1 Ingest Gate"
        assert task.status == TaskStatus.IN_PROGRESS
        assert str(deliverable) in task.deliverables

    def test_build_g4_task(self, tmp_path):
        deliverable = tmp_path / "g4_result.md"
        deliverable.write_text("G4 output", encoding="utf-8")
        task = build_kb_gate_eval_task(gate_id="G4", title="G4 Activate Gate", deliverable=deliverable)
        assert task.task_id == "KBG-9104"
        assert task.title == "G4 Activate Gate"

    def test_build_all_gates(self, tmp_path):
        for gate_id, (expected_ns, expected_seq) in _GATE_SEQ.items():
            deliverable = tmp_path / f"{gate_id}_result.md"
            deliverable.write_text(f"{gate_id} output", encoding="utf-8")
            task = build_kb_gate_eval_task(gate_id=gate_id, title=f"{gate_id} Gate", deliverable=deliverable)
            assert task.namespace == expected_ns
            assert task.seq == expected_seq
            assert task.task_id == f"{expected_ns.value}-{expected_seq}"

    def test_task_has_required_fields(self, tmp_path):
        deliverable = tmp_path / "test.md"
        deliverable.write_text("test", encoding="utf-8")
        task = build_kb_gate_eval_task(gate_id="G1", title="Test", deliverable=deliverable)
        assert task.phase == 2
        assert task.safety_level == "M"
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_invalid_gate_id_raises(self, tmp_path):
        deliverable = tmp_path / "test.md"
        deliverable.write_text("test", encoding="utf-8")
        with pytest.raises(KeyError):
            build_kb_gate_eval_task(gate_id="G9", title="Invalid", deliverable=deliverable)
