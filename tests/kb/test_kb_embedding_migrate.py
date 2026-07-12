# [A_test] module_id: SRC-TST-1162 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_embedding_migrate
# [INVARIANTS] EmbeddingMigrator manages version lifecycle; migration plan requires known models
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_kb.embedding_migrate import (
    EmbeddingMigrator,
    EmbeddingVersion,
    MigrationPlan,
    MigrationResult,
    MigrationStatus,
)


class TestMigrationStatus:
    def test_enum_values(self):
        assert MigrationStatus.NOT_STARTED.value == "NOT_STARTED"
        assert MigrationStatus.IN_PROGRESS.value == "IN_PROGRESS"
        assert MigrationStatus.COMPLETED.value == "COMPLETED"
        assert MigrationStatus.FAILED.value == "FAILED"
        assert MigrationStatus.ROLLED_BACK.value == "ROLLED_BACK"


class TestEmbeddingVersion:
    def test_valid_version(self):
        v = EmbeddingVersion(model_name="bge-m3", dimension=1024, provider="BAAI")
        assert v.model_name == "bge-m3"
        assert v.dimension == 1024
        assert v.provider == "BAAI"
        assert v.is_active is False

    def test_invalid_empty_model_name(self):
        with pytest.raises(Exception):
            EmbeddingVersion(model_name="", dimension=1024, provider="BAAI")

    def test_invalid_zero_dimension(self):
        with pytest.raises(Exception):
            EmbeddingVersion(model_name="test", dimension=0, provider="BAAI")


class TestMigrationPlan:
    def test_valid_plan(self):
        p = MigrationPlan(
            plan_id="MP-001",
            source_model="all-MiniLM-L6-v2",
            source_dimension=384,
            target_model="bge-m3",
            target_dimension=1024,
        )
        assert p.plan_id == "MP-001"
        assert p.recall_threshold == 0.70

    def test_invalid_empty_plan_id(self):
        with pytest.raises(Exception):
            MigrationPlan(
                plan_id="",
                source_model="a",
                source_dimension=384,
                target_model="b",
                target_dimension=1024,
            )


class TestMigrationResult:
    def test_default_values(self):
        r = MigrationResult(plan_id="MP-001", status=MigrationStatus.COMPLETED)
        assert r.total_documents == 0
        assert r.migrated_documents == 0
        assert r.failed_documents == 0
        assert r.duration_seconds == 0.0
        assert r.error_message == ""


class TestEmbeddingMigrator:
    def test_init_loads_known_models(self):
        m = EmbeddingMigrator()
        versions = m.list_versions()
        assert len(versions) >= 4
        model_names = [v.model_name for v in versions]
        assert "bge-m3" in model_names
        assert "all-MiniLM-L6-v2" in model_names

    def test_get_active_version(self):
        m = EmbeddingMigrator()
        active = m.get_active_version()
        assert active is not None
        assert active.model_name == "bge-small-zh"
        assert active.is_active is True

    def test_register_version(self):
        m = EmbeddingMigrator()
        v = m.register_version("custom-model", 512, "custom")
        assert v.model_name == "custom-model"
        assert v.dimension == 512
        versions = m.list_versions()
        assert any(x.model_name == "custom-model" for x in versions)

    def test_should_migrate_below_threshold(self):
        m = EmbeddingMigrator(recall_threshold=0.70)
        assert m.should_migrate(0.50) is True

    def test_should_migrate_above_threshold(self):
        m = EmbeddingMigrator(recall_threshold=0.70)
        assert m.should_migrate(0.80) is False

    def test_create_migration_plan(self):
        m = EmbeddingMigrator()
        plan = m.create_migration_plan(
            source_model="all-MiniLM-L6-v2",
            target_model="bge-m3",
            recall_rate=0.50,
        )
        assert plan.source_model == "all-MiniLM-L6-v2"
        assert plan.target_model == "bge-m3"
        assert plan.source_dimension == 384
        assert plan.target_dimension == 1024
        assert "recall_rate=0.50" in plan.trigger_reason

    def test_create_migration_plan_unknown_model(self):
        m = EmbeddingMigrator()
        with pytest.raises(ValueError, match="Unknown model"):
            m.create_migration_plan(source_model="unknown-a", target_model="unknown-b")

    def test_execute_migration_dry_run(self):
        m = EmbeddingMigrator()
        plan = m.create_migration_plan(
            source_model="all-MiniLM-L6-v2",
            target_model="bge-m3",
            recall_rate=0.50,
        )
        result = m.execute_migration(plan, dry_run=True)
        assert result.status == MigrationStatus.COMPLETED

    def test_execute_migration_no_client(self):
        m = EmbeddingMigrator()
        plan = m.create_migration_plan(
            source_model="all-MiniLM-L6-v2",
            target_model="bge-m3",
            recall_rate=0.50,
        )
        result = m.execute_migration(plan, dry_run=False)
        assert result.status == MigrationStatus.FAILED
        assert "No ChromaDB client" in result.error_message

    def test_rollback(self):
        m = EmbeddingMigrator()
        plan = m.create_migration_plan(
            source_model="all-MiniLM-L6-v2",
            target_model="bge-m3",
            recall_rate=0.50,
        )
        result = m.rollback(plan)
        assert result.status == MigrationStatus.ROLLED_BACK
        active = m.get_active_version()
        assert active is not None
        assert active.model_name == "all-MiniLM-L6-v2"

    def test_save_and_get_checkpoint(self):
        m = EmbeddingMigrator()
        plan = m.create_migration_plan(
            source_model="all-MiniLM-L6-v2",
            target_model="bge-m3",
            recall_rate=0.50,
        )
        cp = m.save_checkpoint(plan, MigrationStatus.IN_PROGRESS, ["ke_entries"], 100)
        assert cp.plan_id == plan.plan_id
        assert cp.status == MigrationStatus.IN_PROGRESS
        assert "ke_entries" in cp.collections_completed
        retrieved = m.get_checkpoint(plan.plan_id)
        assert retrieved is not None
        assert retrieved.documents_migrated == 100

    def test_get_checkpoint_nonexistent(self):
        m = EmbeddingMigrator()
        assert m.get_checkpoint("nonexistent") is None
