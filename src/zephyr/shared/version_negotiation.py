"""
共享 Schema 版本协商器（Version Negotiation — CTR-VER-001）

依据：MOD-MASTER-001 蓝图 §三 + CTR-VER-001
为 3 个共享 Schema（TaskCard/Finding/KE）实现版本协商机制。

规则：
1. forward-compat：新增可选字段——双版本过渡期
2. backward-compat：删除字段→@deprecated→2 MAJOR 版本后移除
3. BREAKING 变更→2 版本过渡期
4. 运行时协商：min(producer_version, consumer_max_supported)
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SchemaName(str, Enum):
    TASKCARD = "TaskCard"
    FINDING = "Finding"
    KE = "KnowledgeEntry"


class ChangeType(str, Enum):
    ADD_OPTIONAL = "add_optional"
    ADD_REQUIRED = "add_required"
    REMOVE_FIELD = "remove_field"
    TYPE_CHANGE = "type_change"
    RENAME_FIELD = "rename_field"


class VersionSegment(BaseModel):
    major: int
    minor: int
    patch: int

    @classmethod
    def parse(cls, version_str: str) -> VersionSegment:
        parts = version_str.replace("v", "").split(".")
        return cls(
            major=int(parts[0]),
            minor=int(parts[1]) if len(parts) > 1 else 0,
            patch=int(parts[2]) if len(parts) > 2 else 0,
        )

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    def __ge__(self, other: VersionSegment) -> bool:
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)

    def __gt__(self, other: VersionSegment) -> bool:
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)


class DeprecationRecord(BaseModel):
    schema_name: SchemaName
    field_name: str
    deprecated_in: str
    removal_target: str
    reason: str = ""
    migration_guide: str = ""


class NegotiationResult(BaseModel):
    schema_name: SchemaName
    producer_version: str
    consumer_max_supported: str
    negotiated_version: str
    degraded: bool = False
    warnings: list[str] = Field(default_factory=list)


class VersionNegotiator:
    DEPRECATION_GRACE_MAJOR: int = 2

    def __init__(self):
        self._deprecations: list[DeprecationRecord] = []

    def register_deprecation(
        self,
        schema_name: SchemaName,
        field_name: str,
        current_version: str,
        reason: str = "",
    ) -> DeprecationRecord:
        current = VersionSegment.parse(current_version)
        removal_major = current.major + self.DEPRECATION_GRACE_MAJOR
        removal = VersionSegment(major=removal_major, minor=0, patch=0)

        record = DeprecationRecord(
            schema_name=schema_name,
            field_name=field_name,
            deprecated_in=current_version,
            removal_target=str(removal),
            reason=reason,
            migration_guide=f"字段 '{field_name}' 将于 {removal} 移除，请迁移至替代字段",
        )
        self._deprecations.append(record)
        return record

    def get_deprecations(self, schema_name: SchemaName | None = None) -> list[DeprecationRecord]:
        if schema_name is None:
            return list(self._deprecations)
        return [d for d in self._deprecations if d.schema_name == schema_name]

    def is_deprecated(
        self,
        schema_name: SchemaName,
        field_name: str,
        current_version: str,
    ) -> bool:
        current = VersionSegment.parse(current_version)
        for d in self._deprecations:
            if d.schema_name == schema_name and d.field_name == field_name:
                target = VersionSegment.parse(d.removal_target)
                if current >= target:
                    return True
        return False

    def negotiate(
        self,
        schema_name: SchemaName,
        producer_version: str,
        consumer_max_supported: str,
    ) -> NegotiationResult:
        prod = VersionSegment.parse(producer_version)
        cons = VersionSegment.parse(consumer_max_supported)

        if cons >= prod:
            return NegotiationResult(
                schema_name=schema_name,
                producer_version=producer_version,
                consumer_max_supported=consumer_max_supported,
                negotiated_version=producer_version,
                degraded=False,
            )

        warnings: list[str] = []
        if cons.major < prod.major:
            warnings.append(
                f"消费者不支持 MAJOR {prod.major}，降级至 {consumer_max_supported}"
            )

        return NegotiationResult(
            schema_name=schema_name,
            producer_version=producer_version,
            consumer_max_supported=consumer_max_supported,
            negotiated_version=consumer_max_supported,
            degraded=True,
            warnings=warnings,
        )

    def check_breaking_change(
        self,
        change_type: ChangeType,
        current_version: str,
    ) -> bool:
        if change_type in (ChangeType.REMOVE_FIELD, ChangeType.TYPE_CHANGE, ChangeType.RENAME_FIELD):
            return True
        if change_type == ChangeType.ADD_REQUIRED:
            return True
        return False

    def required_transition_versions(self, change_type: ChangeType) -> int:
        if change_type in (ChangeType.REMOVE_FIELD, ChangeType.TYPE_CHANGE):
            return 2
        if change_type == ChangeType.ADD_REQUIRED:
            return 1
        return 0
