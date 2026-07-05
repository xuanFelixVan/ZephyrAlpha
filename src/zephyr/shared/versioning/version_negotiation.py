# [BLUEPRINT] SRC-192 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.shared.versioning.version_negotiation
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] tests
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_version_negotiation.py
# [A_module] module_id=MOD-INT_version_negotiation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from functools import total_ordering


class SchemaName(Enum):
    TASKCARD = "TaskCard"
    FINDING = "Finding"
    KNOWLEDGE_ENTRY = "KnowledgeEntry"


class ChangeType(Enum):
    ADD_OPTIONAL = "add_optional"
    ADD_REQUIRED = "add_required"
    REMOVE_FIELD = "remove_field"
    TYPE_CHANGE = "type_change"
    RENAME_FIELD = "rename_field"


@total_ordering
@dataclass(frozen=True)
class VersionSegment:
    major: int = 0
    minor: int = 0
    patch: int = 0

    @classmethod
    def parse(cls, version_str: str) -> VersionSegment:
        s = version_str.lstrip("v")
        parts = s.split(".")
        major = int(parts[0]) if len(parts) > 0 and parts[0] else 0
        minor = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        patch = int(parts[2]) if len(parts) > 2 and parts[2] else 0
        return cls(major=major, minor=minor, patch=patch)

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, VersionSegment):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, VersionSegment):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch))


@dataclass
class DeprecationRecord:
    schema_name: SchemaName
    field_name: str
    deprecated_in: str
    removal_target: str = ""
    reason: str = ""
    migration_guide: str = ""


@dataclass
class NegotiationResult:
    schema_name: SchemaName
    producer_version: str
    consumer_max_supported: str
    negotiated_version: str
    degraded: bool = False
    warnings: list[str] = field(default_factory=list)


class VersionNegotiator:
    def __init__(self) -> None:
        self._deprecations: list[DeprecationRecord] = []

    def register_deprecation(
        self,
        schema_name: SchemaName,
        field_name: str,
        deprecated_in: str,
        reason: str = "",
        migration_guide: str = "",
    ) -> DeprecationRecord:
        dep_ver = VersionSegment.parse(deprecated_in)
        removal = VersionSegment(major=dep_ver.major + 2, minor=0, patch=0)
        rec = DeprecationRecord(
            schema_name=schema_name,
            field_name=field_name,
            deprecated_in=deprecated_in,
            removal_target=str(removal),
            reason=reason,
            migration_guide=migration_guide,
        )
        self._deprecations.append(rec)
        return rec

    def get_deprecations(self, schema_name: SchemaName | None = None) -> list[DeprecationRecord]:
        if schema_name is None:
            return list(self._deprecations)
        return [d for d in self._deprecations if d.schema_name == schema_name]

    def is_deprecated(self, schema_name: SchemaName, field_name: str, current_version: str) -> bool:
        for dep in self._deprecations:
            if dep.schema_name == schema_name and dep.field_name == field_name:
                removal = VersionSegment.parse(dep.removal_target)
                current = VersionSegment.parse(current_version)
                if current >= removal:
                    return True
        return False

    def negotiate(
        self,
        schema_name: SchemaName,
        producer_version: str,
        consumer_max_supported: str,
    ) -> NegotiationResult:
        producer = VersionSegment.parse(producer_version)
        consumer = VersionSegment.parse(consumer_max_supported)
        warnings: list[str] = []
        degraded = False

        if consumer >= producer:
            return NegotiationResult(
                schema_name=schema_name,
                producer_version=producer_version,
                consumer_max_supported=consumer_max_supported,
                negotiated_version=producer_version,
                degraded=False,
            )

        degraded = True
        if consumer.major < producer.major:
            warnings.append("Consumer MAJOR behind")
        elif consumer.minor < producer.minor:
            warnings.append("Consumer MINOR behind")

        return NegotiationResult(
            schema_name=schema_name,
            producer_version=producer_version,
            consumer_max_supported=consumer_max_supported,
            negotiated_version=consumer_max_supported,
            degraded=degraded,
            warnings=warnings,
        )

    def check_breaking_change(self, change_type: ChangeType, version: str) -> bool:
        return change_type in (
            ChangeType.REMOVE_FIELD,
            ChangeType.ADD_REQUIRED,
            ChangeType.TYPE_CHANGE,
            ChangeType.RENAME_FIELD,
        )

    def required_transition_versions(self, change_type: ChangeType) -> int:
        mapping: dict[ChangeType, int] = {
            ChangeType.REMOVE_FIELD: 2,
            ChangeType.ADD_REQUIRED: 1,
            ChangeType.ADD_OPTIONAL: 0,
            ChangeType.TYPE_CHANGE: 2,
            ChangeType.RENAME_FIELD: 2,
        }
        return mapping.get(change_type, 0)


__all__ = [
    "ChangeType",
    "DeprecationRecord",
    "NegotiationResult",
    "SchemaName",
    "VersionNegotiator",
    "VersionSegment",
]
