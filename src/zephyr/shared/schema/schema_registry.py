# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.schema.schema_registry
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.__version__; zephyr.shared.foundation.errors
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
# [A_module] module_id=MOD-SHR_schema_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

import threading
from typing import Self

"""
schema_registry.py —— Schema 版本编目与查询（Phase 10 新增 | 盲点 B25 修复）

痛点修复：migration.py 能迁移 Task，但没有集中式 schema 版本目录——
  1. 消费者不知道当前有哪些 schema、各是什么版本
  2. 无法查询 "schema X 的最新兼容版本是什么"
  3. 新增 schema 时无人知晓——注册表是社区驱动的（靠人记得去 migration.py 加）

设计对标：
  - Confluent Schema Registry（Avro / JSON Schema + 版本化 + 兼容性检查）
  - AWS Glue Schema Registry（集中式 schema catalog）
  - Apicurio Registry（Open-source schema registry）

设计原则：
  - 集中式编目——所有版本化数据结构的 SSoT
  - 版本查询——给定 schema_name → 当前最新版本 + 所有版本链
  - 兼容性检查——新增版本必须通过兼容性规则（同 MAJOR 追加字段 / 不同 MAJOR 拒绝）

AI 施工约定：
  - 任何新增 versioned schema MUST 在 SchemaRegistry 登记
  - 消费者 MUST 在启动时通过 SchemaRegistry 查询兼容版本

SSoT: MOD-INF-016 §2.22 shared-schema-registry
Version: 0.1.0
"""


from dataclasses import dataclass, field
from enum import Enum, unique

from zephyr.shared.__version__ import version_compatible
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "SchemaEntry",
    "SchemaRegistry",
    "SchemaRegistryError",
    "SchemaVersion",
    "get_schema_registry",
]


class SchemaRegistryError(ZephyrBaseError):
    """Schema Registry 操作失败——schema 不存在、版本冲突、兼容性违规。"""
    error_code = "ZA-SH-0017"


@unique
class SchemaVersion(str, Enum):
    V1_0 = "1.0"
    V1_1 = "1.1"
    V1_2 = "1.2"
    V2_0 = "2.0"


@dataclass(frozen=True)
class SchemaEntry:
    """单个 schema 的版本化条目。"""

    schema_name: str
    version: str
    major_version: int
    minor_version: int
    module_id: str
    description: str
    added_in: str
    breaking: bool = False
    supersedes: str | None = None
    fields: dict[str, str] = field(default_factory=dict)


class SchemaRegistry:
    """集中式 Schema 编目——查询版本、兼容性检查。

    对标 Confluent Schema Registry 的 REST API（GET /schemas/{name}/versions）。

    Usage::

        reg = get_schema_registry()
        latest = reg.latest("Task")
        print(latest.version)  # "0.7.0"
        compatible = reg.compatible_versions_for("0.7.0", "Task")
    """

    def __init__(self) -> None:
        self._schemas: dict[str, dict[str, SchemaEntry]] = {}

    def register(self, entry: SchemaEntry) -> None:
        name = entry.schema_name
        if name not in self._schemas:
            self._schemas[name] = {}

        if entry.version in self._schemas[name]:
            raise SchemaRegistryError(
                f"schema '{name}' version '{entry.version}' already registered",
                details={"schema_name": name, "version": entry.version},
            )

        self._schemas[name][entry.version] = entry

    def get(self, schema_name: str, version: str) -> SchemaEntry:
        versions = self._schemas.get(schema_name)
        if versions is None:
            raise SchemaRegistryError(
                f"schema '{schema_name}' not found in registry",
                details={"schema_name": schema_name},
            )
        entry = versions.get(version)
        if entry is None:
            raise SchemaRegistryError(
                f"schema '{schema_name}' version '{version}' not found",
                details={"schema_name": schema_name, "version": version},
            )
        return entry

    def latest(self, schema_name: str) -> SchemaEntry | None:
        versions = self._schemas.get(schema_name)
        if versions is None:
            return None

        from zephyr.shared.__version__ import _parse_semver

        return max(versions.values(), key=lambda e: _parse_semver(e.version))

    def versions(self, schema_name: str) -> list[SchemaEntry]:
        versions = self._schemas.get(schema_name)
        if versions is None:
            return []

        from zephyr.shared.__version__ import _parse_semver

        return sorted(versions.values(), key=lambda e: _parse_semver(e.version))

    def compatible_versions_for(self, consumer_version: str, schema_name: str) -> list[SchemaEntry]:
        """查找与 consumer_version 兼容的所有 schema 版本。

        cross_layer_contracts.yaml VER-R1：同 MAJOR MUST 前后兼容。

        Args:
            consumer_version: 消费者当前版本（如 "0.7.0"）。
            schema_name: schema 名称。

        Returns:
            兼容的 SchemaEntry 列表（包含 consumer_version 本身）。
        """
        all_versions = self.versions(schema_name)
        return [e for e in all_versions if version_compatible(e.version, consumer_version)]

    def check_register_compatible(self, entry: SchemaEntry) -> bool:
        """注册新版本前检查兼容性。"""
        existing = self._schemas.get(entry.schema_name, {})
        for existing_entry in existing.values():
            if existing_entry.major_version != entry.major_version:
                raise SchemaRegistryError(
                    f"major version change from {existing_entry.major_version} to {entry.major_version} "
                    f"for schema '{entry.schema_name}' is not backward-compatible",
                    details={
                        "schema_name": entry.schema_name,
                        "old_major": existing_entry.major_version,
                        "new_major": entry.major_version,
                    },
                )
        return True

    @property
    def schema_count(self) -> int:
        return len(self._schemas)

    def list_schemas(self) -> list[str]:
        return sorted(self._schemas.keys())


_global_schema_registry: SchemaRegistry | None = None
_global_schema_registry_lock = threading.Lock()


def get_schema_registry() -> SchemaRegistry:
    global _global_schema_registry
    if _global_schema_registry is None:
        with _global_schema_registry_lock:
            if _global_schema_registry is None:
                _global_schema_registry = SchemaRegistry()
    return _global_schema_registry
