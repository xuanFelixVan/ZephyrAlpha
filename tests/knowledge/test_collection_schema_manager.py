# [BLUEPRINT] MOD-KNW-010 | docs/03_modules/_domain_knowledge/collection_schema_manager/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-010 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_collection_schema_manager
# [TESTS] src/zephyr/knowledge/collection_schema_manager.py
"""MOD-KNW-010 单元测试：collection_schema_manager Collection模式管理器。

蓝图验收（B13-04346/CAND-KNW-012，A3 D-AUTONOMY-187）：
8 Collection schema 版本注册（严格递增）+ 迁移脚本注册/执行编排
（注入 runner，dry-run 先行）+ 破坏性变更检测（字段删除/类型变更 →
CI 报告 + 拒绝注册除非 force）。runner/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.knowledge.collection_schema_manager",
    reason="collection_schema_manager not importable",
)

from zephyr.knowledge.collection_schema_manager import (  # noqa: E402
    CollectionName,
    CollectionSchemaError,
    CollectionSchemaManager,
    FieldDef,
    FieldType,
    Migration,
    MigrationKind,
    MigrationState,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)

_V1_FIELDS = (
    FieldDef(name="doc_id", field_type=FieldType.STRING, required=True),
    FieldDef(name="embedding", field_type=FieldType.JSON),
    FieldDef(name="created_at", field_type=FieldType.STRING),
)


def _mgr(runner=None) -> CollectionSchemaManager:
    return CollectionSchemaManager(clock=lambda: _T0, migration_runner=runner)


def _migration(mid: str = "mig-1", frm: int = 1, to: int = 2) -> Migration:
    return Migration(
        migration_id=mid,
        collection=CollectionName.KNOWLEDGE,
        from_version=frm,
        to_version=to,
        kind=MigrationKind.REBUILD_VECTORS,
        params={"model": "bge-m3"},
    )


# ──────────────────────────────────────────────────────────────────────────────
# schema 版本注册
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterSchema:
    def test_register_first_version(self) -> None:
        mgr = _mgr()
        schema = mgr.register_schema(CollectionName.KNOWLEDGE, 1, _V1_FIELDS)
        assert schema.collection is CollectionName.KNOWLEDGE
        assert schema.version == 1
        assert schema.registered_at == _T0
        assert len(schema.fields) == 3

    def test_register_sequential_versions(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.DECISIONS, 1, _V1_FIELDS)
        mgr.register_schema(
            CollectionName.DECISIONS, 2, _V1_FIELDS + (FieldDef(name="rationale", field_type=FieldType.STRING),)
        )
        assert mgr.list_versions(CollectionName.DECISIONS) == (1, 2)

    def test_skip_version_raises(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.RULES, 1, _V1_FIELDS)
        with pytest.raises(CollectionSchemaError):
            mgr.register_schema(CollectionName.RULES, 3, _V1_FIELDS)

    def test_first_version_must_be_one(self) -> None:
        mgr = _mgr()
        with pytest.raises(CollectionSchemaError):
            mgr.register_schema(CollectionName.RULES, 2, _V1_FIELDS)

    def test_duplicate_version_raises(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.LESSONS, 1, _V1_FIELDS)
        with pytest.raises(CollectionSchemaError):
            mgr.register_schema(CollectionName.LESSONS, 1, _V1_FIELDS)

    def test_unknown_collection_raises(self) -> None:
        mgr = _mgr()
        with pytest.raises(CollectionSchemaError):
            mgr.register_schema("vector_store", 1, _V1_FIELDS)  # type: ignore[arg-type]

    def test_empty_fields_raises(self) -> None:
        mgr = _mgr()
        with pytest.raises(CollectionSchemaError):
            mgr.register_schema(CollectionName.KNOWLEDGE, 1, ())

    def test_duplicate_field_name_raises(self) -> None:
        mgr = _mgr()
        with pytest.raises(CollectionSchemaError):
            mgr.register_schema(
                CollectionName.KNOWLEDGE,
                1,
                (
                    FieldDef(name="a", field_type=FieldType.STRING),
                    FieldDef(name="a", field_type=FieldType.INTEGER),
                ),
            )

    def test_invalid_field_type_raises(self) -> None:
        mgr = _mgr()
        with pytest.raises(CollectionSchemaError):
            mgr.register_schema(
                CollectionName.KNOWLEDGE,
                1,
                (
                    FieldDef(name="a", field_type="blob"),  # type: ignore[arg-type]
                ),
            )

    def test_get_schema_latest_and_pinned(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.BLUEPRINTS, 1, _V1_FIELDS)
        mgr.register_schema(
            CollectionName.BLUEPRINTS, 2, _V1_FIELDS + (FieldDef(name="owner", field_type=FieldType.STRING),)
        )
        assert mgr.get_schema(CollectionName.BLUEPRINTS).version == 2
        assert mgr.get_schema(CollectionName.BLUEPRINTS, 1).version == 1

    def test_get_schema_unknown_raises(self) -> None:
        mgr = _mgr()
        with pytest.raises(CollectionSchemaError):
            mgr.get_schema(CollectionName.KNOWLEDGE)
        mgr.register_schema(CollectionName.KNOWLEDGE, 1, _V1_FIELDS)
        with pytest.raises(CollectionSchemaError):
            mgr.get_schema(CollectionName.KNOWLEDGE, 9)


# ──────────────────────────────────────────────────────────────────────────────
# 破坏性变更检测（CI 报告 + force 门禁）
# ──────────────────────────────────────────────────────────────────────────────


class TestBreakingChanges:
    def test_field_removed_rejected_unless_force(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.KNOWLEDGE, 1, _V1_FIELDS)
        with pytest.raises(CollectionSchemaError):
            mgr.register_schema(CollectionName.KNOWLEDGE, 2, _V1_FIELDS[:2])  # 删 created_at
        assert mgr.list_versions(CollectionName.KNOWLEDGE) == (1,)  # 未注册

    def test_field_type_changed_rejected_unless_force(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.KNOWLEDGE, 1, _V1_FIELDS)
        mutated = (
            FieldDef(name="doc_id", field_type=FieldType.STRING, required=True),
            FieldDef(name="embedding", field_type=FieldType.STRING),  # json→str 类型变更
            FieldDef(name="created_at", field_type=FieldType.STRING),
        )
        with pytest.raises(CollectionSchemaError):
            mgr.register_schema(CollectionName.KNOWLEDGE, 2, mutated)

    def test_force_registers_breaking_schema(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.KNOWLEDGE, 1, _V1_FIELDS)
        schema = mgr.register_schema(CollectionName.KNOWLEDGE, 2, _V1_FIELDS[:2], force=True)
        assert schema.version == 2
        assert mgr.list_versions(CollectionName.KNOWLEDGE) == (1, 2)

    def test_additive_change_not_breaking(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.KNOWLEDGE, 1, _V1_FIELDS)
        schema = mgr.register_schema(
            CollectionName.KNOWLEDGE, 2, _V1_FIELDS + (FieldDef(name="tags", field_type=FieldType.STRING_LIST),)
        )
        assert schema.version == 2  # 新增字段非破坏性，无需 force

    def test_detect_breaking_changes(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.DECISIONS, 1, _V1_FIELDS)
        mutated = (
            FieldDef(name="doc_id", field_type=FieldType.INTEGER, required=True),  # 类型变更
            FieldDef(name="embedding", field_type=FieldType.JSON),
        )  # 删 created_at
        mgr.register_schema(CollectionName.DECISIONS, 2, mutated, force=True)
        changes = mgr.detect_breaking_changes(CollectionName.DECISIONS, 1, 2)
        kinds = {(c.field, c.kind) for c in changes}
        assert kinds == {("doc_id", "type_changed"), ("created_at", "removed")}

    def test_detect_invalid_range_raises(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.DECISIONS, 1, _V1_FIELDS)
        with pytest.raises(CollectionSchemaError):
            mgr.detect_breaking_changes(CollectionName.DECISIONS, 1, 1)

    def test_ci_report_collects_breaking_log(self) -> None:
        mgr = _mgr()
        mgr.register_schema(CollectionName.KNOWLEDGE, 1, _V1_FIELDS)
        with pytest.raises(CollectionSchemaError):
            mgr.register_schema(CollectionName.KNOWLEDGE, 2, _V1_FIELDS[:2])  # 拒绝也留痕
        mgr.register_schema(CollectionName.KNOWLEDGE, 2, _V1_FIELDS[:2], force=True)
        report = mgr.ci_report()
        assert report["breaking_change_count"] == 2  # 拒绝 + force 各留痕一条
        assert all(c["collection"] == "knowledge" for c in report["breaking_changes"])
        assert report["breaking_changes"][0]["kind"] == "removed"
        assert len(report["collections"]) == 8


# ──────────────────────────────────────────────────────────────────────────────
# 迁移脚本注册与执行编排（dry-run 先行）
# ──────────────────────────────────────────────────────────────────────────────


class TestMigration:
    def _ready(self, runner=None) -> CollectionSchemaManager:
        mgr = _mgr(runner)
        mgr.register_schema(CollectionName.KNOWLEDGE, 1, _V1_FIELDS)
        mgr.register_schema(
            CollectionName.KNOWLEDGE, 2, _V1_FIELDS + (FieldDef(name="chunk_no", field_type=FieldType.INTEGER),)
        )
        return mgr

    def test_register_migration_ok(self) -> None:
        mgr = self._ready()
        mgr.register_migration(_migration())
        assert mgr.migration_status("mig-1") is MigrationState.REGISTERED

    def test_register_migration_unknown_version_raises(self) -> None:
        mgr = self._ready()
        with pytest.raises(CollectionSchemaError):
            mgr.register_migration(_migration(to=9))

    def test_register_migration_bad_range_raises(self) -> None:
        mgr = self._ready()
        with pytest.raises(CollectionSchemaError):
            mgr.register_migration(_migration(frm=2, to=2))

    def test_register_migration_duplicate_raises(self) -> None:
        mgr = self._ready()
        mgr.register_migration(_migration())
        with pytest.raises(CollectionSchemaError):
            mgr.register_migration(_migration())

    def test_dry_run_then_apply(self) -> None:
        calls: list[tuple[str, bool]] = []

        def _runner(mig: Migration, dry_run: bool) -> None:
            calls.append((mig.migration_id, dry_run))

        mgr = self._ready(_runner)
        mgr.register_migration(_migration())
        assert mgr.dry_run_migration("mig-1") is MigrationState.DRY_RUN_PASSED
        assert mgr.apply_migration("mig-1") is MigrationState.APPLIED
        assert calls == [("mig-1", True), ("mig-1", False)]  # dry-run 先行

    def test_apply_without_dry_run_raises(self) -> None:
        mgr = self._ready(lambda m, d: None)
        mgr.register_migration(_migration())
        with pytest.raises(CollectionSchemaError):
            mgr.apply_migration("mig-1")

    def test_runner_not_injected_fail_closed(self) -> None:
        mgr = self._ready()
        mgr.register_migration(_migration())
        with pytest.raises(CollectionSchemaError):
            mgr.dry_run_migration("mig-1")

    def test_runner_failure_wrapped(self) -> None:
        def _boom(mig: Migration, dry_run: bool) -> None:
            raise RuntimeError("向量重建失败")

        mgr = self._ready(_boom)
        mgr.register_migration(_migration())
        with pytest.raises(CollectionSchemaError):
            mgr.dry_run_migration("mig-1")
        assert mgr.migration_status("mig-1") is MigrationState.REGISTERED  # 未前进

    def test_dry_run_and_apply_idempotent(self) -> None:
        calls: list[bool] = []
        mgr = self._ready(lambda m, d: calls.append(d))
        mgr.register_migration(_migration())
        mgr.dry_run_migration("mig-1")
        mgr.dry_run_migration("mig-1")  # 幂等不重复执行
        mgr.apply_migration("mig-1")
        mgr.apply_migration("mig-1")  # 幂等
        assert calls == [True, False]

    def test_dry_run_after_apply_raises(self) -> None:
        mgr = self._ready(lambda m, d: None)
        mgr.register_migration(_migration())
        mgr.dry_run_migration("mig-1")
        mgr.apply_migration("mig-1")
        with pytest.raises(CollectionSchemaError):
            mgr.dry_run_migration("mig-1")

    def test_unknown_migration_raises(self) -> None:
        mgr = self._ready(lambda m, d: None)
        with pytest.raises(CollectionSchemaError):
            mgr.migration_status("ghost")
