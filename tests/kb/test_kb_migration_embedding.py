# [A_test] module_id: SRC-TST-1170 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_migration_embedding
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

from zephyr.gov_kb.embedding_migrate import (
    EmbeddingMigrator,
    EmbeddingVersion,
    MigrationCheckpoint,
    MigrationPlan,
    MigrationResult,
    MigrationStatus,
)


class TestMigrationStatus:
    def test_enum_values(self):
        assert MigrationStatus.NOT_STARTED == "NOT_STARTED"
        assert MigrationStatus.IN_PROGRESS == "IN_PROGRESS"
        assert MigrationStatus.COMPLETED == "COMPLETED"
        assert MigrationStatus.FAILED == "FAILED"
        assert MigrationStatus.ROLLED_BACK == "ROLLED_BACK"


class TestEmbeddingVersion:
    def test_create_valid(self):
        ev = EmbeddingVersion(model_name="bge-m3", dimension=1024, provider="BAAI")
        assert ev.model_name == "bge-m3"
        assert ev.dimension == 1024
        assert ev.provider == "BAAI"
        assert ev.is_active is False

    def test_empty_model_name_rejected(self):
        with pytest.raises(Exception):
            EmbeddingVersion(model_name="", dimension=1024, provider="BAAI")

    def test_zero_dimension_rejected(self):
        with pytest.raises(Exception):
            EmbeddingVersion(model_name="test", dimension=0, provider="BAAI")

    def test_negative_dimension_rejected(self):
        with pytest.raises(Exception):
            EmbeddingVersion(model_name="test", dimension=-1, provider="BAAI")


class TestMigrationPlan:
    def test_create_valid(self):
        plan = MigrationPlan(
            plan_id="MP-001",
            source_model="all-MiniLM-L6-v2",
            source_dimension=384,
            target_model="bge-m3",
            target_dimension=1024,
        )
        assert plan.plan_id == "MP-001"
        assert plan.source_model == "all-MiniLM-L6-v2"

    def test_empty_plan_id_rejected(self):
        with pytest.raises(Exception):
            MigrationPlan(
                plan_id="",
                source_model="a",
                source_dimension=384,
                target_model="b",
                target_dimension=1024,
            )

    def test_recall_rate_bounds(self):
        plan = MigrationPlan(
            plan_id="MP-002",
            source_model="a",
            source_dimension=384,
            target_model="b",
            target_dimension=1024,
            recall_rate=0.5,
        )
        assert plan.recall_rate == 0.5

    def test_recall_rate_out_of_bounds(self):
        with pytest.raises(Exception):
            MigrationPlan(
                plan_id="MP-003",
                source_model="a",
                source_dimension=384,
                target_model="b",
                target_dimension=1024,
                recall_rate=1.5,
            )


class TestMigrationResult:
    def test_create_completed(self):
        mr = MigrationResult(
            plan_id="MP-001",
            status=MigrationStatus.COMPLETED,
            total_documents=100,
            migrated_documents=100,
        )
        assert mr.status == MigrationStatus.COMPLETED
        assert mr.failed_documents == 0

    def test_negative_documents_rejected(self):
        with pytest.raises(Exception):
            MigrationResult(
                plan_id="MP-001",
                status=MigrationStatus.FAILED,
                total_documents=-1,
            )


class TestMigrationCheckpoint:
    def test_create(self):
        cp = MigrationCheckpoint(
            plan_id="MP-001",
            source_model="a",
            target_model="b",
            status=MigrationStatus.IN_PROGRESS,
            collections_completed=["ke_entries"],
            documents_migrated=50,
        )
        assert cp.plan_id == "MP-001"
        assert cp.collections_completed == ["ke_entries"]


class TestEmbeddingMigrator:
    def test_init_loads_known_models(self):
        migrator = EmbeddingMigrator()
        versions = migrator.list_versions()
        assert len(versions) >= 4
        names = [v.model_name for v in versions]
        assert "bge-m3" in names
        assert "all-MiniLM-L6-v2" in names

    def test_get_active_version(self):
        migrator = EmbeddingMigrator()
        active = migrator.get_active_version()
        assert active is not None
        assert active.model_name == "bge-small-zh"
        assert active.is_active is True

    def test_register_version(self):
        migrator = EmbeddingMigrator()
        new_ver = migrator.register_version("custom-model", 256, "test_provider")
        assert new_ver.model_name == "custom-model"
        assert new_ver.dimension == 256
        assert new_ver in migrator.list_versions()

    def test_should_migrate_below_threshold(self):
        migrator = EmbeddingMigrator(recall_threshold=0.70)
        assert migrator.should_migrate(0.5) is True

    def test_should_migrate_above_threshold(self):
        migrator = EmbeddingMigrator(recall_threshold=0.70)
        assert migrator.should_migrate(0.8) is False

    def test_should_migrate_at_threshold(self):
        migrator = EmbeddingMigrator(recall_threshold=0.70)
        assert migrator.should_migrate(0.70) is False

    def test_create_migration_plan(self):
        migrator = EmbeddingMigrator()
        plan = migrator.create_migration_plan(
            source_model="all-MiniLM-L6-v2",
            target_model="bge-m3",
            recall_rate=0.5,
        )
        assert plan.source_model == "all-MiniLM-L6-v2"
        assert plan.target_model == "bge-m3"
        assert plan.source_dimension == 384
        assert plan.target_dimension == 1024
        assert "recall_rate" in plan.trigger_reason

    def test_create_migration_plan_unknown_model(self):
        migrator = EmbeddingMigrator()
        with pytest.raises(ValueError, match="Unknown model"):
            migrator.create_migration_plan(
                source_model="nonexistent",
                target_model="bge-m3",
            )

    def test_execute_migration_dry_run(self):
        migrator = EmbeddingMigrator()
        plan = migrator.create_migration_plan(
            source_model="all-MiniLM-L6-v2",
            target_model="bge-m3",
            recall_rate=0.5,
        )
        result = migrator.execute_migration(plan, dry_run=True)
        assert result.status == MigrationStatus.COMPLETED

    def test_execute_migration_no_client(self):
        migrator = EmbeddingMigrator(chroma_client=None)
        plan = migrator.create_migration_plan(
            source_model="all-MiniLM-L6-v2",
            target_model="bge-m3",
        )
        result = migrator.execute_migration(plan)
        assert result.status == MigrationStatus.FAILED
        assert "No ChromaDB client" in result.error_message

    def test_rollback(self):
        migrator = EmbeddingMigrator()
        plan = migrator.create_migration_plan(
            source_model="all-MiniLM-L6-v2",
            target_model="bge-m3",
        )
        result = migrator.rollback(plan)
        assert result.status == MigrationStatus.ROLLED_BACK
        active = migrator.get_active_version()
        assert active.model_name == "all-MiniLM-L6-v2"

    def test_save_and_get_checkpoint(self):
        migrator = EmbeddingMigrator()
        plan = migrator.create_migration_plan(
            source_model="all-MiniLM-L6-v2",
            target_model="bge-m3",
        )
        cp = migrator.save_checkpoint(
            plan,
            status=MigrationStatus.IN_PROGRESS,
            collections_completed=["ke_entries"],
            documents_migrated=10,
        )
        assert cp.collections_completed == ["ke_entries"]
        retrieved = migrator.get_checkpoint(plan.plan_id)
        assert retrieved is not None
        assert retrieved.documents_migrated == 10

    def test_get_checkpoint_nonexistent(self):
        migrator = EmbeddingMigrator()
        assert migrator.get_checkpoint("nonexistent") is None
