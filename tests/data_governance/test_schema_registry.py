# [BLUEPRINT] MOD-DATA_GOV-001 | (auto-injected by S4 reconciler) | §D-DATA-GOV
# [TTL] permanent
# [A_test] module_id: MOD-DATA_GOV-001 | layer=test | stability=volatile | safety=L
# [MODULE] tests.data_governance.test_schema_registry
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/data_governance/test_schema_registry.py
# [TTL] task_bound
"""D-DATA-GOV Schema Registry 测试。"""

from __future__ import annotations

import pytest

from zephyr.data_governance.core.schema_registry import (
    ColumnSchema,
    ManagedSchemaRegistry,
    TableSchema,
)


def _make_columns() -> list[ColumnSchema]:
    return [
        ColumnSchema("trade_date", "Date", "交易日期", nullable=False),
        ColumnSchema("symbol", "String", "标的代码", nullable=False),
        ColumnSchema("close", "Float64", "收盘价"),
    ]


class TestRegisterAndGet:
    def test_register_and_get(self):
        reg = ManagedSchemaRegistry()
        reg.register("market.kline_daily", _make_columns(), "日K线")
        schema = reg.get_schema("market.kline_daily")
        assert isinstance(schema, TableSchema)
        assert schema.table_name == "market.kline_daily"
        assert len(schema.columns) == 3
        assert schema.description == "日K线"

    def test_register_idempotent_updates(self):
        reg = ManagedSchemaRegistry()
        reg.register("t1", _make_columns(), "旧描述")
        reg.register("t1", _make_columns()[:2], "新描述")
        schema = reg.get_schema("t1")
        assert len(schema.columns) == 2
        assert schema.description == "新描述"

    def test_get_unregistered_raises(self):
        reg = ManagedSchemaRegistry()
        with pytest.raises(KeyError, match="未在 ManagedSchemaRegistry 注册"):
            reg.get_schema("unknown")


class TestListAndCheck:
    def test_list_tables_empty(self):
        reg = ManagedSchemaRegistry()
        assert reg.list_tables() == []

    def test_list_tables(self):
        reg = ManagedSchemaRegistry()
        reg.register("t1", _make_columns())
        reg.register("t2", _make_columns())
        assert set(reg.list_tables()) == {"t1", "t2"}

    def test_has_table(self):
        reg = ManagedSchemaRegistry()
        reg.register("t1", _make_columns())
        assert reg.has_table("t1") is True
        assert reg.has_table("unknown") is False

    def test_has_column(self):
        reg = ManagedSchemaRegistry()
        reg.register("t1", _make_columns())
        assert reg.has_column("t1", "symbol") is True
        assert reg.has_column("t1", "volume") is False
        assert reg.has_column("unknown", "symbol") is False

    def test_get_column(self):
        reg = ManagedSchemaRegistry()
        reg.register("t1", _make_columns())
        col = reg.get_column("t1", "close")
        assert col is not None
        assert col.dtype == "Float64"
        assert col.description == "收盘价"

    def test_get_column_not_found(self):
        reg = ManagedSchemaRegistry()
        reg.register("t1", _make_columns())
        assert reg.get_column("t1", "volume") is None
        assert reg.get_column("unknown", "close") is None


class TestRemove:
    def test_remove_existing(self):
        reg = ManagedSchemaRegistry()
        reg.register("t1", _make_columns())
        assert reg.remove("t1") is True
        assert reg.has_table("t1") is False

    def test_remove_nonexistent(self):
        reg = ManagedSchemaRegistry()
        assert reg.remove("unknown") is False
