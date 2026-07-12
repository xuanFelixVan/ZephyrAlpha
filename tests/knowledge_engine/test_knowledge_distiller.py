# [A_test] module_id: SRC-TST-1194 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_knowledge_distiller
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_knowledge_distiller.py
# [TTL] task_bound

import pytest

from zephyr.gov_kb.knowledge_distiller import (
    DistillationResult,
    KnowledgeDistiller,
)


class TestDistillationResult:
    def test_instantiation_defaults(self):
        dr = DistillationResult(representative_ke_id="KE-001")
        assert dr.representative_ke_id == "KE-001"
        assert dr.superseded_ke_ids == []
        assert dr.cluster_size == 0

    def test_instantiation_custom(self):
        dr = DistillationResult(
            representative_ke_id="KE-REP",
            superseded_ke_ids=["KE-002", "KE-003"],
            cluster_size=3,
        )
        assert dr.superseded_ke_ids == ["KE-002", "KE-003"]
        assert dr.cluster_size == 3

    def test_missing_required_field_raises(self):
        with pytest.raises(TypeError):
            DistillationResult()


class TestKnowledgeDistiller:
    def test_instantiation(self):
        kd = KnowledgeDistiller()
        assert kd is not None

    def test_distill_single_entry(self):
        kd = KnowledgeDistiller()
        entries = [("KE-001", "content1")]
        results = kd.distill(entries)
        assert len(results) >= 1
        assert results[0].cluster_size == 1
        assert results[0].superseded_ke_ids == []

    def test_distill_multiple_entries(self):
        kd = KnowledgeDistiller()
        entries = [("KE-001", "content1"), ("KE-002", "content2"), ("KE-003", "content3")]
        results = kd.distill(entries)
        assert len(results) >= 1
        assert results[0].cluster_size == 3
        assert "KE-002" in results[0].superseded_ke_ids
        assert "KE-003" in results[0].superseded_ke_ids

    def test_distill_returns_distillation_result(self):
        kd = KnowledgeDistiller()
        entries = [("KE-001", "content1")]
        results = kd.distill(entries)
        assert all(isinstance(r, DistillationResult) for r in results)

    def test_distill_representative_ke_id(self):
        kd = KnowledgeDistiller()
        entries = [("KE-001", "content1"), ("KE-002", "content2")]
        results = kd.distill(entries)
        assert results[0].representative_ke_id == "KE-REP-001"
