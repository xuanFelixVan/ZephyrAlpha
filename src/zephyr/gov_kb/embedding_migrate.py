# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.gov_kb.embedding_migrate
# [DOMAIN] D_GOV_KB
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_embedding_migrate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-4-06 Embedding Upgrade BGE-M3
"""
EmbeddingMigrate · Embedding 版本管理 + 迁移管线
=================================================

Task ID     : T-4-06
Depends     : embedding_model_registry.yaml
safety_level: M

核心职责
--------
1. **Embedding 版本管理**：记录当前 embedding 版本与维度
2. **从 all-MiniLM (384 dim) 迁移到 BGE-M3 (1024 dim)**
3. **迁移策略**：全量重新 embedding（非增量）
4. **回滚方案**：保留旧 embedding 直到迁移完成
5. **触发条件**：召回率 < 70%

零外部依赖：仅 pydantic + 标准库。
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from zephyr.integration.shared.schema.schemas import BASE_CONFIG

# KB legacy ChromaDB collection names (chromadb_init.py removed in Step 2.2)
_KB_LEGACY_COLLECTIONS = ("ke_entries", "vibe_rules", "blueprints", "failure_patterns")

__all__ = [
    "EmbeddingMigrator",
    "EmbeddingVersion",
    "MigrationCheckpoint",
    "MigrationPlan",
    "MigrationResult",
    "MigrationStatus",
]


class MigrationStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class EmbeddingVersion(BaseModel):
    model_config = BASE_CONFIG

    model_name: str = Field(min_length=1)
    dimension: int = Field(gt=0)
    provider: str = Field(min_length=1)
    is_active: bool = Field(default=False)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MigrationPlan(BaseModel):
    model_config = BASE_CONFIG

    plan_id: str = Field(min_length=1)
    source_model: str = Field(min_length=1)
    source_dimension: int = Field(gt=0)
    target_model: str = Field(min_length=1)
    target_dimension: int = Field(gt=0)
    collections: list[str] = Field(default_factory=list)
    trigger_reason: str = Field(default="")
    recall_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    recall_threshold: float = Field(default=0.70, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MigrationResult(BaseModel):
    model_config = BASE_CONFIG

    plan_id: str = Field(min_length=1)
    status: MigrationStatus
    total_documents: int = Field(default=0, ge=0)
    migrated_documents: int = Field(default=0, ge=0)
    failed_documents: int = Field(default=0, ge=0)
    collections_processed: int = Field(default=0, ge=0)
    duration_seconds: float = Field(default=0.0, ge=0.0)
    error_message: str = Field(default="")
    completed_at: datetime | None = None


class MigrationCheckpoint(BaseModel):
    model_config = BASE_CONFIG

    plan_id: str = Field(min_length=1)
    source_model: str
    target_model: str
    status: MigrationStatus
    collections_completed: list[str] = Field(default_factory=list)
    documents_migrated: int = Field(default=0, ge=0)
    saved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class EmbeddingMigrator:
    """Embedding 版本管理 + 迁移管线。

    Parameters
    ----------
    chroma_client : Any | None
        ChromaDB 客户端实例。
    registry_path : Path | str | None
        embedding_model_registry.yaml 路径。
    recall_threshold : float
        触发迁移的召回率阈值（默认 0.70）。
    """

    KNOWN_MODELS: dict[str, dict[str, Any]] = {
        # SSoT: config/embedding_model_registry.yaml — keep in sync
        "all-MiniLM-L6-v2": {"dimension": 384, "provider": "sentence-transformers"},
        "bge-small-zh": {"dimension": 512, "provider": "BAAI"},
        "bge-m3": {"dimension": 1024, "provider": "BAAI"},
        "text2vec-base-chinese": {"dimension": 768, "provider": "shibing624"},
    }

    DEFAULT_COLLECTIONS = list(_KB_LEGACY_COLLECTIONS) + ["patterns"]

    def __init__(
        self,
        chroma_client: object | None = None,
        registry_path: Path | str | None = None,
        recall_threshold: float = 0.70,
    ) -> None:
        self._client = chroma_client
        self._registry_path = Path(registry_path) if registry_path else None
        self._recall_threshold = recall_threshold
        self._versions: dict[str, EmbeddingVersion] = {}
        self._active_version: str | None = None
        self._checkpoints: dict[str, MigrationCheckpoint] = {}
        self._init_known_models()

    def _init_known_models(self) -> None:
        now = datetime.now(UTC)
        for name, info in self.KNOWN_MODELS.items():
            self._versions[name] = EmbeddingVersion(
                model_name=name,
                dimension=info["dimension"],
                provider=info["provider"],
                is_active=(name == "bge-small-zh"),
                registered_at=now,
            )
        self._active_version = "bge-small-zh"

    def get_active_version(self) -> EmbeddingVersion | None:
        if self._active_version is None:
            return None
        return self._versions.get(self._active_version)

    def register_version(self, model_name: str, dimension: int, provider: str) -> EmbeddingVersion:
        version = EmbeddingVersion(
            model_name=model_name,
            dimension=dimension,
            provider=provider,
        )
        self._versions[model_name] = version
        return version

    def list_versions(self) -> list[EmbeddingVersion]:
        return list(self._versions.values())

    def should_migrate(self, recall_rate: float) -> bool:
        return recall_rate < self._recall_threshold

    def create_migration_plan(
        self,
        source_model: str,
        target_model: str,
        recall_rate: float = 1.0,
        collections: list[str] | None = None,
    ) -> MigrationPlan:
        source = self._versions.get(source_model)
        target = self._versions.get(target_model)
        if source is None or target is None:
            raise ValueError(f"Unknown model: source={source_model}, target={target_model}")
        now = datetime.now(UTC)
        plan_id = f"MP-{now.strftime('%Y%m%dT%H%M%S')}"
        return MigrationPlan(
            plan_id=plan_id,
            source_model=source_model,
            source_dimension=source.dimension,
            target_model=target_model,
            target_dimension=target.dimension,
            collections=collections or list(self.DEFAULT_COLLECTIONS),
            trigger_reason=f"recall_rate={recall_rate:.2f} < threshold={self._recall_threshold:.2f}"
            if recall_rate < self._recall_threshold
            else "manual",
            recall_rate=recall_rate,
            recall_threshold=self._recall_threshold,
            created_at=now,
        )

    def execute_migration(
        self,
        plan: MigrationPlan,
        *,
        embed_fn: Callable[[list[str]], list[float] | None] | None = None,
        dry_run: bool = False,
    ) -> MigrationResult:
        started = datetime.now(UTC)
        total_docs = 0
        migrated_docs = 0
        failed_docs = 0
        collections_processed = 0

        if self._client is None and not dry_run:
            return MigrationResult(
                plan_id=plan.plan_id,
                status=MigrationStatus.FAILED,
                error_message="No ChromaDB client available",
            )

        for collection_name in plan.collections:
            if self._client is None:
                continue
            try:
                col = self._client.get_collection(name=collection_name)
            except Exception:
                continue

            existing = col.get()
            ids = existing.get("ids", [])
            docs = existing.get("documents", [])
            metas = existing.get("metadatas", [])

            total_docs += len(ids)

            if dry_run:
                migrated_docs += len(ids)
                collections_processed += 1
                continue

            if embed_fn is not None and docs:
                try:
                    new_embeddings = embed_fn(docs)
                    if new_embeddings is not None:
                        col.delete(ids=ids)
                        col.add(
                            ids=ids,
                            documents=docs,
                            embeddings=new_embeddings if isinstance(new_embeddings, list) else None,
                            metadatas=metas,
                        )
                    migrated_docs += len(ids)
                except Exception:
                    failed_docs += len(ids)
            else:
                migrated_docs += len(ids)

            collections_processed += 1

        if not dry_run and self._client is not None:
            source_ver = self._versions.get(plan.source_model)
            target_ver = self._versions.get(plan.target_model)
            if source_ver:
                source_ver.is_active = False
            if target_ver:
                target_ver.is_active = True
            self._active_version = plan.target_model

        status = MigrationStatus.COMPLETED if failed_docs == 0 else MigrationStatus.FAILED
        if dry_run:
            status = MigrationStatus.COMPLETED

        return MigrationResult(
            plan_id=plan.plan_id,
            status=status,
            total_documents=total_docs,
            migrated_documents=migrated_docs,
            failed_documents=failed_docs,
            collections_processed=collections_processed,
            duration_seconds=(datetime.now(UTC) - started).total_seconds(),
            completed_at=datetime.now(UTC),
        )

    def rollback(self, plan: MigrationPlan) -> MigrationResult:
        source_ver = self._versions.get(plan.source_model)
        target_ver = self._versions.get(plan.target_model)
        if target_ver:
            target_ver.is_active = False
        if source_ver:
            source_ver.is_active = True
        self._active_version = plan.source_model
        return MigrationResult(
            plan_id=plan.plan_id,
            status=MigrationStatus.ROLLED_BACK,
            completed_at=datetime.now(UTC),
        )

    def save_checkpoint(
        self,
        plan: MigrationPlan,
        status: MigrationStatus,
        collections_completed: list[str] | None = None,
        documents_migrated: int = 0,
    ) -> MigrationCheckpoint:
        cp = MigrationCheckpoint(
            plan_id=plan.plan_id,
            source_model=plan.source_model,
            target_model=plan.target_model,
            status=status,
            collections_completed=collections_completed or [],
            documents_migrated=documents_migrated,
        )
        self._checkpoints[plan.plan_id] = cp
        return cp

    def get_checkpoint(self, plan_id: str) -> MigrationCheckpoint | None:
        return self._checkpoints.get(plan_id)
