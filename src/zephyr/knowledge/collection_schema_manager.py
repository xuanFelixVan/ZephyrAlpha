# [BLUEPRINT] MOD-KNW-010 | docs/03_modules/_domain_knowledge/collection_schema_manager/blueprint.md
# [MODULE] zephyr.knowledge.collection_schema_manager
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（管理核心纯内存；迁移 runner/时钟 全注入）
# [CONSUMERS] 运行时装配批（8 Collection schema 注册 / 迁移编排 / CI 破坏性变更报告）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Collection 词表闭合(8); schema 版本按 collection 严格递增(+1); 字段名同版本内唯一; 破坏性变更(字段删除/类型变更)拒绝注册除非 force; 迁移须 dry-run 先行再 apply; 迁移执行强制经注入 runner(未注入 Fail-Closed); 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/collection_schema_manager/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CollectionSchemaError(占位 ZA-KNW-UNREGISTERED-COLLECTION-SCHEMA)——未知Collection/非法版本/字段非法/破坏性变更未force/迁移非法或未dry-run/runner缺失时抛
# [TESTS] tests/knowledge/test_collection_schema_manager.py
# [A_module] module_id=MOD-KNW-010 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
CollectionSchemaManager — Collection 模式管理器（MOD-KNW-010）。

B13-04346（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-012，A3 D-AUTONOMY-187）：
8 大 Collection schema **版本注册**（schema_id/version/字段定义 dict）+
迁移脚本**注册与执行编排**（向量重建/元数据回填，执行经注入 runner，
dry-run 先行）+ **破坏性变更检测**（字段删除/类型变更 → CI 报告 +
拒绝应用除非 force 标记）。

查重分工（蓝图 §0）：vector_memory/collection_schemas=8 Collection 静态配
置声明（本件=其版本演进与迁移编排，不改静态声明）；kb_engine=按 Collection
做 CRUD（本件不管条目数据）；跨 Collection 查询沿用 kb_engine/检索层语义
（本件只保证 schema 演进不破坏查询契约）。纯内存/DI，不触网不起子进程。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: collection_schema_manager.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: migration_runner 参数
#   fields: 参数 migration_runner（无注解）
#   code: collection_schema_manager.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CollectionSchemaManager
#   name_en: CollectionSchemaManager
#   intro: 8 Collection schema 版本注册 + 迁移编排 + 破坏性变更检测件。
#   desc: 8 Collection schema 版本注册 + 迁移编排 + 破坏性变更检测件。；公共方法（定义序）: register_schema, get_schema, list_versions, detect_bre…
#   inputs: clock migration_runner
#   outputs: 返回值
#   （注：A1 之后另有 9 个公共定义未列入（含 9 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（10 定义）
#   name_en: public defs
#   intro: CollectionSchemaManager
#   downstream: 运行时装配批（8 Collection schema 注册 / 迁移编排 / CI 破坏性变更报告）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "BreakingChange",
    "CollectionName",
    "CollectionSchemaError",
    "CollectionSchemaManager",
    "FieldDef",
    "FieldType",
    "Migration",
    "MigrationKind",
    "MigrationState",
    "SchemaVersion",
]


class CollectionSchemaError(Exception):
    """Collection schema 输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-COLLECTION-SCHEMA。
    """


class CollectionName(str, Enum):
    """8 大 Collection（词表闭合，与 vector_memory 静态声明对齐）。"""

    DECISIONS = "decisions"
    CODE_CONTEXT = "code_context"
    LESSONS = "lessons"
    KNOWLEDGE = "knowledge"
    RULES = "rules"
    BLUEPRINTS = "blueprints"
    SESSION_SNAPSHOTS = "session_snapshots"
    EXECUTION_TRACES = "execution_traces"


class FieldType(str, Enum):
    """schema 字段类型（词表闭合）。"""

    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    JSON = "json"
    STRING_LIST = "list[str]"


class MigrationKind(str, Enum):
    """迁移脚本类型（词表闭合）。"""

    REBUILD_VECTORS = "rebuild_vectors"
    BACKFILL_METADATA = "backfill_metadata"


class MigrationState(str, Enum):
    """迁移编排状态机：REGISTERED → DRY_RUN_PASSED → APPLIED。"""

    REGISTERED = "registered"
    DRY_RUN_PASSED = "dry_run_passed"
    APPLIED = "applied"


@dataclass(frozen=True)
class FieldDef:
    """schema 字段定义（frozen）。"""

    name: str
    field_type: FieldType
    required: bool = False
    description: str = ""


@dataclass(frozen=True)
class SchemaVersion:
    """单 Collection 单版本 schema（frozen）。"""

    collection: CollectionName
    version: int
    fields: tuple[FieldDef, ...]
    registered_at: datetime.datetime


@dataclass(frozen=True)
class BreakingChange:
    """破坏性变更（CI 报告载荷）。"""

    collection: CollectionName
    field: str
    kind: str  # "removed" | "type_changed"
    from_type: FieldType | None
    to_type: FieldType | None


@dataclass(frozen=True)
class Migration:
    """迁移脚本（注册载体，frozen）。"""

    migration_id: str
    collection: CollectionName
    from_version: int
    to_version: int
    kind: MigrationKind
    params: Mapping[str, str] = field(default_factory=dict)


#: 迁移 runner 签名：runner(migration, dry_run) -> None（异常即失败）
MigrationRunner = Callable[[Migration, bool], None]


def _validate_collection(collection: CollectionName) -> CollectionName:
    if not isinstance(collection, CollectionName):
        raise CollectionSchemaError(f"未知 Collection: {collection!r}（词表闭合 8 大）")
    return collection


def _validate_fields(fields: Sequence[FieldDef]) -> tuple[FieldDef, ...]:
    if not fields:
        raise CollectionSchemaError("字段定义为空")
    out = tuple(fields)
    names: set[str] = set()
    for f in out:
        if not isinstance(f, FieldDef):
            raise CollectionSchemaError(f"非法字段定义: {f!r}（须为 FieldDef）")
        if not f.name:
            raise CollectionSchemaError("字段名为空")
        if not isinstance(f.field_type, FieldType):
            raise CollectionSchemaError(f"字段 {f.name!r} 类型非法: {f.field_type!r}")
        if f.name in names:
            raise CollectionSchemaError(f"字段名重复: {f.name!r}")
        names.add(f.name)
    return out


def _diff_breaking(
    collection: CollectionName,
    old: tuple[FieldDef, ...],
    new: tuple[FieldDef, ...],
) -> tuple[BreakingChange, ...]:
    old_map = {f.name: f for f in old}
    new_map = {f.name: f for f in new}
    changes: list[BreakingChange] = []
    for name in sorted(old_map.keys() - new_map.keys()):
        changes.append(
            BreakingChange(
                collection=collection,
                field=name,
                kind="removed",
                from_type=old_map[name].field_type,
                to_type=None,
            )
        )
    for name in sorted(old_map.keys() & new_map.keys()):
        if old_map[name].field_type is not new_map[name].field_type:
            changes.append(
                BreakingChange(
                    collection=collection,
                    field=name,
                    kind="type_changed",
                    from_type=old_map[name].field_type,
                    to_type=new_map[name].field_type,
                )
            )
    return tuple(changes)


class CollectionSchemaManager:
    """8 Collection schema 版本注册 + 迁移编排 + 破坏性变更检测件。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        migration_runner: MigrationRunner | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._runner = migration_runner
        self._schemas: dict[CollectionName, dict[int, SchemaVersion]] = {}
        self._migrations: dict[str, tuple[Migration, MigrationState]] = {}
        self._breaking_log: list[BreakingChange] = []

    # ── schema 版本注册 ────────────────────────────────────────────────────

    def register_schema(
        self,
        collection: CollectionName,
        version: int,
        fields: Sequence[FieldDef],
        *,
        force: bool = False,
    ) -> SchemaVersion:
        """注册新版本：版本严格 +1 递增；破坏性变更拒绝除非 force。"""
        _validate_collection(collection)
        if not isinstance(version, int) or version < 1:
            raise CollectionSchemaError(f"非法版本号: {version!r}")
        field_tuple = _validate_fields(fields)
        versions = self._schemas.setdefault(collection, {})
        if version in versions:
            raise CollectionSchemaError(f"schema 重复注册: {collection.value} v{version}")
        latest = max(versions) if versions else 0
        if version != latest + 1:
            raise CollectionSchemaError(f"版本须严格递增: {collection.value} 当前最新 v{latest}，拒绝注册 v{version}")
        if latest:
            changes = _diff_breaking(collection, versions[latest].fields, field_tuple)
            if changes:
                self._breaking_log.extend(changes)
                if not force:
                    raise CollectionSchemaError(
                        f"破坏性变更拒绝注册（须 force 标记）: {collection.value} v{version} "
                        + ", ".join(f"{c.field}:{c.kind}" for c in changes)
                    )
                _log.warning(
                    "force 注册破坏性 schema: %s v%s (%s)",
                    collection.value,
                    version,
                    ", ".join(f"{c.field}:{c.kind}" for c in changes),
                )
        schema = SchemaVersion(
            collection=collection,
            version=version,
            fields=field_tuple,
            registered_at=self._clock(),
        )
        versions[version] = schema
        return schema

    def get_schema(self, collection: CollectionName, version: int | None = None) -> SchemaVersion:
        """取 schema（version=None → 最新；未知 → Fail-Closed）。"""
        _validate_collection(collection)
        versions = self._schemas.get(collection) or {}
        if not versions:
            raise CollectionSchemaError(f"Collection {collection.value} 无已注册 schema")
        pick = max(versions) if version is None else version
        schema = versions.get(pick)
        if schema is None:
            raise CollectionSchemaError(f"未知 schema: {collection.value} v{pick}")
        return schema

    def list_versions(self, collection: CollectionName) -> tuple[int, ...]:
        """版本序列（确定性升序）。"""
        _validate_collection(collection)
        return tuple(sorted((self._schemas.get(collection) or {}).keys()))

    # ── 破坏性变更检测（CI 报告） ───────────────────────────────────────────

    def detect_breaking_changes(
        self,
        collection: CollectionName,
        from_version: int,
        to_version: int,
    ) -> tuple[BreakingChange, ...]:
        """两版本间破坏性变更（字段删除/类型变更；确定性排序）。"""
        old = self.get_schema(collection, from_version)
        new = self.get_schema(collection, to_version)
        if from_version >= to_version:
            raise CollectionSchemaError(f"版本区间非法: v{from_version} -> v{to_version}（须 from < to）")
        return _diff_breaking(collection, old.fields, new.fields)

    def ci_report(self) -> dict:
        """CI 报告（全量破坏性变更留痕；确定性排序）。"""
        changes = sorted(
            self._breaking_log,
            key=lambda c: (c.collection.value, c.field, c.kind),
        )
        return {
            "breaking_change_count": len(changes),
            "breaking_changes": [
                {
                    "collection": c.collection.value,
                    "field": c.field,
                    "kind": c.kind,
                    "from_type": c.from_type.value if c.from_type else None,
                    "to_type": c.to_type.value if c.to_type else None,
                }
                for c in changes
            ],
            "collections": [c.value for c in CollectionName],
        }

    # ── 迁移脚本注册与执行编排 ──────────────────────────────────────────────

    def register_migration(self, migration: Migration) -> None:
        """注册迁移：from<to 且两版本均已注册；重复 id → Fail-Closed。"""
        if not isinstance(migration, Migration):
            raise CollectionSchemaError(f"非法迁移: {migration!r}（须为 Migration）")
        if not migration.migration_id:
            raise CollectionSchemaError("migration_id 为空")
        _validate_collection(migration.collection)
        if not isinstance(migration.kind, MigrationKind):
            raise CollectionSchemaError(f"非法迁移类型: {migration.kind!r}")
        if migration.from_version >= migration.to_version:
            raise CollectionSchemaError(f"迁移版本区间非法: v{migration.from_version} -> v{migration.to_version}")
        self.get_schema(migration.collection, migration.from_version)
        self.get_schema(migration.collection, migration.to_version)
        if migration.migration_id in self._migrations:
            raise CollectionSchemaError(f"migration_id 重复: {migration.migration_id!r}")
        self._migrations[migration.migration_id] = (migration, MigrationState.REGISTERED)

    def _migration(self, migration_id: str) -> tuple[Migration, MigrationState]:
        entry = self._migrations.get(migration_id)
        if entry is None:
            raise CollectionSchemaError(f"未知迁移: {migration_id!r}")
        return entry

    def _run(self, migration: Migration, dry_run: bool) -> None:
        if self._runner is None:
            raise CollectionSchemaError("migration_runner 未注入（迁移执行强制经注入 runner）")
        try:
            self._runner(migration, dry_run)
        except CollectionSchemaError:
            raise
        except Exception as exc:  # noqa: BLE001 — runner 失败 Fail-Closed 包装
            raise CollectionSchemaError(
                f"迁移 {'dry-run' if dry_run else 'apply'} 执行失败: {migration.migration_id}: {exc}"
            ) from exc

    def dry_run_migration(self, migration_id: str) -> MigrationState:
        """dry-run 先行：REGISTERED → DRY_RUN_PASSED（重复 dry-run 幂等）。"""
        migration, state = self._migration(migration_id)
        if state is MigrationState.APPLIED:
            raise CollectionSchemaError(f"迁移已应用，禁止再 dry-run: {migration_id!r}")
        if state is MigrationState.DRY_RUN_PASSED:
            return state
        self._run(migration, True)
        self._migrations[migration_id] = (migration, MigrationState.DRY_RUN_PASSED)
        return MigrationState.DRY_RUN_PASSED

    def apply_migration(self, migration_id: str) -> MigrationState:
        """apply：须 dry-run 先行（DRY_RUN_PASSED → APPLIED；幂等）。"""
        migration, state = self._migration(migration_id)
        if state is MigrationState.APPLIED:
            return state
        if state is not MigrationState.DRY_RUN_PASSED:
            raise CollectionSchemaError(f"迁移须 dry-run 先行: {migration_id!r} 当前 {state.value}")
        self._run(migration, False)
        self._migrations[migration_id] = (migration, MigrationState.APPLIED)
        return MigrationState.APPLIED

    def migration_status(self, migration_id: str) -> MigrationState:
        """迁移状态查询（未知 → Fail-Closed）。"""
        return self._migration(migration_id)[1]
