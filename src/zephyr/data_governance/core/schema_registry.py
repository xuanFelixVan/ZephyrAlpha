# [BLUEPRINT] MOD-DATA_GOV-001 | docs/03_modules/_domain_data_governance/blueprint.md
# [MODULE] zephyr.data_governance.core.schema_registry
# [DOMAIN] D_DATA_GOV
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 表名唯一; 列名在表内唯一; 注册幂等(重复注册更新)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未注册表->KeyError; 列不存在->KeyError
# [TESTS] tests/data_governance/test_schema_registry.py
# [TTL] permanent
"""D-DATA-GOV Schema Registry——表结构注册与查询。

提供内存级的 Schema 注册服务，记录表名、列名、类型、描述。
与 data/table_registry.py 互补：table_registry 管理品类→表名映射，
schema_registry 管理表名→列结构映射。

用法：
    reg = ManagedSchemaRegistry()
    reg.register("market.kline_daily", [
        ColumnSchema("trade_date", "Date", "交易日期"),
        ColumnSchema("symbol", "String", "标的代码"),
    ])
    schema = reg.get_schema("market.kline_daily")
    assert reg.has_column("market.kline_daily", "symbol")
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ColumnSchema:
    """列结构定义。

    Attributes:
        name: 列名
        dtype: 数据类型 (如 "String", "Float64", "Date")
        description: 列描述
        nullable: 是否允许 NULL
    """

    name: str
    dtype: str
    description: str = ""
    nullable: bool = True


@dataclass
class TableSchema:
    """表结构定义。

    Attributes:
        table_name: 全限定表名 (如 "market.kline_daily")
        columns: 列定义列表
        description: 表描述
    """

    table_name: str
    columns: list[ColumnSchema] = field(default_factory=list)
    description: str = ""


class ManagedSchemaRegistry:
    """Schema 注册表——内存级表结构管理。

    提供注册、查询、校验功能。注册幂等（重复注册同一表名会更新）。
    # class-name-alias: 与 shared/schema/schema_registry.py SchemaRegistry 区分（data_governance 域管理器）
    """

    def __init__(self) -> None:
        self._schemas: dict[str, TableSchema] = {}

    def register(
        self,
        table_name: str,
        columns: list[ColumnSchema],
        description: str = "",
    ) -> TableSchema:
        """注册或更新表结构。

        Args:
            table_name: 全限定表名
            columns: 列定义列表
            description: 表描述

        Returns:
            注册的 TableSchema
        """
        schema = TableSchema(table_name, list(columns), description)
        self._schemas[table_name] = schema
        return schema

    def get_schema(self, table_name: str) -> TableSchema:
        """获取表结构。未注册抛 KeyError。"""
        if table_name not in self._schemas:
            raise KeyError(f"表 '{table_name}' 未在 ManagedSchemaRegistry 注册")
        return self._schemas[table_name]

    def list_tables(self) -> list[str]:
        """返回所有已注册表名。"""
        return list(self._schemas.keys())

    def has_table(self, table_name: str) -> bool:
        """判断表是否已注册。"""
        return table_name in self._schemas

    def has_column(self, table_name: str, column_name: str) -> bool:
        """判断表中是否存在指定列。"""
        schema = self._schemas.get(table_name)
        if schema is None:
            return False
        return any(col.name == column_name for col in schema.columns)

    def get_column(
        self, table_name: str, column_name: str
    ) -> Optional[ColumnSchema]:
        """获取列定义。不存在返回 None。"""
        schema = self._schemas.get(table_name)
        if schema is None:
            return None
        for col in schema.columns:
            if col.name == column_name:
                return col
        return None

    def remove(self, table_name: str) -> bool:
        """移除表注册。返回是否成功。"""
        if table_name not in self._schemas:
            return False
        del self._schemas[table_name]
        return True
