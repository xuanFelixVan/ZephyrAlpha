# [A_test] module_id: SRC-TST-1166 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_gate_task
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] test_kb_gate_task.py
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.gov_kb.kb_gate_task import _GATE_SEQ, build_kb_gate_eval_task


class TestBuildKbGateEvalTask:
    def test_returns_task_card(self, tmp_path: Path):
        deliverable = tmp_path / "out.yaml"
        deliverable.write_text("test", encoding="utf-8")
        task = build_kb_gate_eval_task(gate_id="G1", title="Test G1", deliverable=deliverable)
        assert task.title == "Test G1"
        assert task.status.value == "IN_PROGRESS"
        assert str(deliverable) in task.deliverables

    def test_all_gate_ids(self, tmp_path: Path):
        deliverable = tmp_path / "out.yaml"
        deliverable.write_text("x", encoding="utf-8")
        for gid in ("G1", "G2", "G3", "G4", "G5"):
            task = build_kb_gate_eval_task(gate_id=gid, title=f"Gate {gid}", deliverable=deliverable)
            assert task.source_section == gid
            assert f"KB 门禁 {gid}" in task.description

    def test_invalid_gate_id_raises(self, tmp_path: Path):
        deliverable = tmp_path / "out.yaml"
        with pytest.raises(KeyError):
            build_kb_gate_eval_task(gate_id="G9", title="Bad", deliverable=deliverable)

    def test_task_id_format(self, tmp_path: Path):
        deliverable = tmp_path / "out.yaml"
        deliverable.write_text("x", encoding="utf-8")
        task = build_kb_gate_eval_task(gate_id="G1", title="T", deliverable=deliverable)
        ns, seq = _GATE_SEQ["G1"]
        assert task.task_id == f"{ns.value}-{seq}"

    def test_safety_level_is_m(self, tmp_path: Path):
        deliverable = tmp_path / "out.yaml"
        deliverable.write_text("x", encoding="utf-8")
        task = build_kb_gate_eval_task(gate_id="G3", title="T", deliverable=deliverable)
        assert task.safety_level.value == "M"

    def test_source_blueprint(self, tmp_path: Path):
        deliverable = tmp_path / "out.yaml"
        deliverable.write_text("x", encoding="utf-8")
        task = build_kb_gate_eval_task(gate_id="G2", title="T", deliverable=deliverable)
        assert task.source_blueprint == "KB-GATE"
