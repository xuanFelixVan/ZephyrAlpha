# [A_test] module_id: SRC-TST-1184 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-399 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_ke_structurer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_ke_structurer.py
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.shared.knowledge.ke_structurer import KeStructuredOutput, KEStructurer, KEType, KnowledgeEntry


class TestKEType:
    def test_enum_values(self):
        assert KEType.INSIGHT.value == "insight"
        assert KEType.PROCEDURE.value == "procedure"
        assert KEType.PATTERN.value == "pattern"
        assert KEType.FAILURE.value == "failure"
        assert KEType.HEURISTIC.value == "heuristic"

    def test_enum_from_string(self):
        assert KEType("insight") == KEType.INSIGHT
        assert KEType("procedure") == KEType.PROCEDURE

    def test_enum_invalid_raises(self):
        with pytest.raises(ValueError):
            KEType("nonexistent")


class TestKnowledgeEntry:
    def test_creation_with_defaults(self):
        entry = KnowledgeEntry(
            ke_id="KE-1",
            task_id="T-1",
            ke_type=KEType.INSIGHT,
            content_snippet="test",
            source_file="f.py",
            priority="P2",
            created_at="2026-01-01T00:00:00Z",
        )
        assert entry.tags == []

    def test_creation_with_tags(self):
        entry = KnowledgeEntry(
            ke_id="KE-2",
            task_id="T-1",
            ke_type=KEType.PATTERN,
            content_snippet="snippet",
            source_file="g.py",
            priority="P1",
            created_at="2026-01-01T00:00:00Z",
            tags=["alpha", "beta"],
        )
        assert entry.tags == ["alpha", "beta"]


class TestKeStructuredOutput:
    def test_creation(self):
        output = KeStructuredOutput(entries=[], total=0, by_type={}, timestamp_utc="2026-01-01")
        assert output.entries == []
        assert output.total == 0
        assert output.by_type == {}


class TestKEStructurerInit:
    def test_init_default_data_dir(self):
        s = KEStructurer()
        assert s._data_dir == Path("data/knowledge")

    def test_init_custom_data_dir(self, tmp_path):
        s = KEStructurer(data_dir=tmp_path)
        assert s._data_dir == tmp_path


class TestKEStructurerStructureTaskKE:
    def test_with_existing_ke_entries(self):
        s = KEStructurer()
        task_card = {
            "task_id": "TASK-1",
            "ke_entries": [
                {
                    "ke_id": "KE-TASK-1-1",
                    "ke_type": "insight",
                    "content_snippet": "learned something",
                    "source_file": "a.py",
                    "priority": "P1",
                    "tags": ["core"],
                },
                {
                    "ke_id": "KE-TASK-1-2",
                    "ke_type": "failure",
                    "content_snippet": "bug found",
                    "source_file": "b.py",
                    "priority": "P0",
                    "tags": [],
                },
            ],
        }
        entries = s.structure_task_ke(task_card)
        assert len(entries) == 2
        assert entries[0].ke_id == "KE-TASK-1-1"
        assert entries[0].ke_type == KEType.INSIGHT
        assert entries[1].ke_type == KEType.FAILURE

    def test_with_description_no_ke_entries(self):
        s = KEStructurer()
        task_card = {
            "task_id": "TASK-2",
            "description": "Implement feature X",
        }
        entries = s.structure_task_ke(task_card)
        assert len(entries) == 1
        assert entries[0].ke_id == "KE-TASK-2-001"
        assert entries[0].ke_type == KEType.INSIGHT
        assert entries[0].content_snippet == "Implement feature X"
        assert entries[0].tags == ["task_description"]

    def test_with_empty_card(self):
        s = KEStructurer()
        entries = s.structure_task_ke({})
        assert entries == []

    def test_with_empty_ke_entries_list(self):
        s = KEStructurer()
        task_card = {
            "task_id": "TASK-3",
            "ke_entries": [],
            "description": "Some desc",
        }
        entries = s.structure_task_ke(task_card)
        assert len(entries) == 1
        assert entries[0].content_snippet == "Some desc"

    def test_ke_entry_missing_fields_use_defaults(self):
        s = KEStructurer()
        task_card = {
            "task_id": "TASK-4",
            "ke_entries": [{}],
        }
        entries = s.structure_task_ke(task_card)
        assert len(entries) == 1
        assert entries[0].ke_id == "KE-TASK-4-1"
        assert entries[0].ke_type == KEType.INSIGHT
        assert entries[0].content_snippet == ""
        assert entries[0].priority == "P2"
        assert entries[0].tags == []

    def test_description_truncated_to_500(self):
        s = KEStructurer()
        long_desc = "x" * 600
        task_card = {
            "task_id": "TASK-5",
            "description": long_desc,
        }
        entries = s.structure_task_ke(task_card)
        assert len(entries[0].content_snippet) == 500

    def test_created_at_is_iso_format(self):
        s = KEStructurer()
        task_card = {
            "task_id": "TASK-6",
            "description": "test",
        }
        entries = s.structure_task_ke(task_card)
        assert "T" in entries[0].created_at


class TestKEStructurerSaveAndGet:
    def test_save_and_get_by_type(self, tmp_path):
        s = KEStructurer(data_dir=tmp_path)
        entries = [
            KnowledgeEntry(
                ke_id="KE-1",
                task_id="T-1",
                ke_type=KEType.INSIGHT,
                content_snippet="insight text",
                source_file="a.py",
                priority="P2",
                created_at="2026-01-01T00:00:00Z",
                tags=["t1"],
            ),
            KnowledgeEntry(
                ke_id="KE-2",
                task_id="T-1",
                ke_type=KEType.FAILURE,
                content_snippet="failure text",
                source_file="b.py",
                priority="P0",
                created_at="2026-01-01T00:00:00Z",
                tags=[],
            ),
        ]
        s.save_entries(entries)
        insights = s.get_by_type(KEType.INSIGHT)
        assert len(insights) == 1
        assert insights[0].ke_id == "KE-1"
        failures = s.get_by_type(KEType.FAILURE)
        assert len(failures) == 1
        assert failures[0].ke_id == "KE-2"

    def test_get_by_type_no_file(self, tmp_path):
        s = KEStructurer(data_dir=tmp_path)
        results = s.get_by_type(KEType.INSIGHT)
        assert results == []

    def test_save_creates_directory(self, tmp_path):
        nested = tmp_path / "sub" / "dir"
        s = KEStructurer(data_dir=nested)
        entries = [
            KnowledgeEntry(
                ke_id="KE-1",
                task_id="T-1",
                ke_type=KEType.INSIGHT,
                content_snippet="test",
                source_file="a.py",
                priority="P2",
                created_at="2026-01-01T00:00:00Z",
            ),
        ]
        s.save_entries(entries)
        assert nested.exists()

    def test_save_appends_to_existing(self, tmp_path):
        s = KEStructurer(data_dir=tmp_path)
        entry1 = KnowledgeEntry(
            ke_id="KE-1",
            task_id="T-1",
            ke_type=KEType.INSIGHT,
            content_snippet="first",
            source_file="a.py",
            priority="P2",
            created_at="2026-01-01T00:00:00Z",
        )
        entry2 = KnowledgeEntry(
            ke_id="KE-2",
            task_id="T-2",
            ke_type=KEType.INSIGHT,
            content_snippet="second",
            source_file="b.py",
            priority="P1",
            created_at="2026-01-01T00:00:00Z",
        )
        s.save_entries([entry1])
        s.save_entries([entry2])
        results = s.get_by_type(KEType.INSIGHT)
        assert len(results) == 2

    def test_save_empty_entries(self, tmp_path):
        s = KEStructurer(data_dir=tmp_path)
        s.save_entries([])
        assert not s._entries_path.exists()

    def test_get_by_type_with_corrupt_file(self, tmp_path):
        s = KEStructurer(data_dir=tmp_path)
        s._data_dir.mkdir(parents=True, exist_ok=True)
        with open(s._entries_path, "w", encoding="utf-8") as f:
            f.write("not valid json\n")
        results = s.get_by_type(KEType.INSIGHT)
        assert results == []

    def test_saved_jsonl_format(self, tmp_path):
        s = KEStructurer(data_dir=tmp_path)
        entries = [
            KnowledgeEntry(
                ke_id="KE-1",
                task_id="T-1",
                ke_type=KEType.INSIGHT,
                content_snippet="test",
                source_file="a.py",
                priority="P2",
                created_at="2026-01-01T00:00:00Z",
                tags=["x"],
            ),
        ]
        s.save_entries(entries)
        lines = s._entries_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["ke_id"] == "KE-1"
        assert data["ke_type"] == "insight"
        assert data["tags"] == ["x"]
