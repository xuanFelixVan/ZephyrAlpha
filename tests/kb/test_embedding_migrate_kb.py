# [A_test] module_id: SRC-TST-1900 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-519 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.kb.test_embedding_migrate
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for embedding_migrate.py (T-4-06)
==============================================
覆盖：Embedding 版本管理、迁移管线、回滚、触发条件。

最少测试：10 条。
"""


from typing import Any

import pytest

from zephyr.gov_kb.embedding_migrate import (
    EmbeddingMigrator,
    MigrationStatus,
)


class TestEmbeddingVersion:
    def test_known_models_initialized(self) -> None:
        migrator = EmbeddingMigrator()
        versions = migrator.list_versions()
        names = {v.model_name for v in versions}
        assert "bge-small-zh" in names
        assert "bge-m3" in names

    def test_default_active_is_bge_small_zh(self) -> None:
        migrator = EmbeddingMigrator()
        active = migrator.get_active_version()
        assert active is not None
        assert active.model_name == "bge-small-zh"
        assert active.dimension == 512
        assert active.is_active is True

    def test_register_new_version(self) -> None:
        migrator = EmbeddingMigrator()
        ver = migrator.register_version("custom-model", 256, "custom")
        assert ver.model_name == "custom-model"
        assert ver.dimension == 256
        assert ver in migrator.list_versions()


class TestShouldMigrate:
    def test_below_threshold_triggers(self) -> None:
        migrator = EmbeddingMigrator(recall_threshold=0.70)
        assert migrator.should_migrate(0.65) is True

    def test_above_threshold_no_migrate(self) -> None:
        migrator = EmbeddingMigrator(recall_threshold=0.70)
        assert migrator.should_migrate(0.75) is False

    def test_at_threshold_no_migrate(self) -> None:
        migrator = EmbeddingMigrator(recall_threshold=0.70)
        assert migrator.should_migrate(0.70) is False


class TestMigrationPlan:
    def test_create_plan(self) -> None:
        migrator = EmbeddingMigrator()
        plan = migrator.create_migration_plan(
            source_model="bge-small-zh",
            target_model="bge-m3",
            recall_rate=0.65,
        )
        assert plan.source_model == "bge-small-zh"
        assert plan.target_model == "bge-m3"
        assert plan.source_dimension == 512
        assert plan.target_dimension == 1024
        assert plan.recall_rate == 0.65

    def test_create_plan_unknown_model_raises(self) -> None:
        migrator = EmbeddingMigrator()
        with pytest.raises(ValueError):
            migrator.create_migration_plan(
                source_model="unknown-model",
                target_model="bge-m3",
            )


class TestExecuteMigration:
    def test_dry_run_no_client(self) -> None:
        migrator = EmbeddingMigrator()
        plan = migrator.create_migration_plan("bge-small-zh", "bge-m3")
        result = migrator.execute_migration(plan, dry_run=True)
        assert result.status == MigrationStatus.COMPLETED
        assert result.migrated_documents == 0

    def test_no_client_fails(self) -> None:
        migrator = EmbeddingMigrator()
        plan = migrator.create_migration_plan("bge-small-zh", "bge-m3")
        result = migrator.execute_migration(plan, dry_run=False)
        assert result.status == MigrationStatus.FAILED

    def test_migration_with_mock_client(self) -> None:
        class FakeCollection:
            def __init__(self) -> None:
                self._ids: list[str] = ["id1", "id2"]
                self._docs: list[str] = ["doc1", "doc2"]
                self._metas: list[dict[str, Any]] = [{}, {}]

            def get(self, **kwargs: Any) -> dict[str, Any]:
                return {"ids": self._ids, "documents": self._docs, "metadatas": self._metas}

            def delete(self, ids: list[str]) -> None:
                pass

            def add(self, **kwargs: Any) -> None:
                pass

        class FakeClient:
            def get_collection(self, name: str) -> FakeCollection:
                return FakeCollection()

        migrator = EmbeddingMigrator(chroma_client=FakeClient())
        plan = migrator.create_migration_plan("bge-small-zh", "bge-m3")
        result = migrator.execute_migration(plan, dry_run=False)
        assert result.status == MigrationStatus.COMPLETED
        assert result.total_documents > 0
        assert result.migrated_documents > 0

    def test_migration_updates_active_version(self) -> None:
        class FakeClient:
            def get_collection(self, name: str) -> Any:
                class FC:
                    def get(self, **kw: Any) -> dict[str, Any]:
                        return {"ids": [], "documents": [], "metadatas": []}

                return FC()

        migrator = EmbeddingMigrator(chroma_client=FakeClient())
        plan = migrator.create_migration_plan("bge-small-zh", "bge-m3")
        migrator.execute_migration(plan, dry_run=False)
        active = migrator.get_active_version()
        assert active is not None
        assert active.model_name == "bge-m3"


class TestRollback:
    def test_rollback_restores_source(self) -> None:
        migrator = EmbeddingMigrator()
        plan = migrator.create_migration_plan("bge-small-zh", "bge-m3")
        result = migrator.rollback(plan)
        assert result.status == MigrationStatus.ROLLED_BACK
        active = migrator.get_active_version()
        assert active is not None
        assert active.model_name == "bge-small-zh"


class TestCheckpoint:
    def test_save_and_get_checkpoint(self) -> None:
        migrator = EmbeddingMigrator()
        plan = migrator.create_migration_plan("bge-small-zh", "bge-m3")
        cp = migrator.save_checkpoint(plan, MigrationStatus.IN_PROGRESS, ["ke_entries"], 10)
        assert cp.plan_id == plan.plan_id
        assert cp.status == MigrationStatus.IN_PROGRESS
        got = migrator.get_checkpoint(plan.plan_id)
        assert got is not None
        assert got.documents_migrated == 10
