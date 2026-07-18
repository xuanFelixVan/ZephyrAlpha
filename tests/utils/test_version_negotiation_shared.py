# [A_test] module_id: SRC-TST-1960 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-577 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_version_negotiation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/version_negotiation.py
====================================================
覆盖矩阵：
  SchemaName / ChangeType：
    - 枚举值完整性 × 2
  VersionSegment：
    - parse 标准格式 × 2
    - str 格式化 × 1
    - 比较运算符 >= / > × 4
    - parse 单段版本号 × 1
  DeprecationRecord：
    - 构造 × 1
  NegotiationResult：
    - 构造 × 1
    - 降级标志 × 1
  VersionNegotiator：
    - register_deprecation × 2
    - get_deprecations 全部 / 按 schema × 2
    - is_deprecated × 3
    - negotiate 消费端支持 ≥ 产出端 × 1
    - negotiate 消费端 MAJOR 落后 × 1
    - negotiate 消费端 MINOR 落后 × 1
    - check_breaking_change × 3
    - required_transition_versions × 3

Safety: HIGH（版本协商是 Schema 演进安全的根基）
"""

from zephyr.shared.versioning.version_negotiation import (
    ChangeType,
    DeprecationRecord,
    NegotiationResult,
    SchemaName,
    VersionNegotiator,
    VersionSegment,
)


class TestEnums:
    def test_schema_names(self):
        values = {s.value for s in SchemaName}
        assert "TaskCard" in values
        assert "Finding" in values
        assert "KnowledgeEntry" in values
        assert len(values) == 3

    def test_change_types(self):
        values = {c.value for c in ChangeType}
        assert "add_optional" in values
        assert "add_required" in values
        assert "remove_field" in values
        assert "type_change" in values
        assert "rename_field" in values


class TestVersionSegment:
    def test_parse_full_semver(self):
        v = VersionSegment.parse("v2.1.3")
        assert v.major == 2
        assert v.minor == 1
        assert v.patch == 3

    def test_parse_without_v_prefix(self):
        v = VersionSegment.parse("3.0.0")
        assert v.major == 3

    def test_str_representation(self):
        v = VersionSegment.parse("v1.5.2")
        assert str(v) == "v1.5.2"

    def test_greater_equal_major(self):
        v1 = VersionSegment.parse("v2.0.0")
        v2 = VersionSegment.parse("v1.9.9")
        assert v1 >= v2
        assert v1 > v2

    def test_equal(self):
        v1 = VersionSegment.parse("v1.2.3")
        v2 = VersionSegment.parse("v1.2.3")
        assert v1 >= v2
        assert not (v1 > v2)

    def test_greater_equal_minor(self):
        v1 = VersionSegment.parse("v1.5.0")
        v2 = VersionSegment.parse("v1.4.9")
        assert v1 >= v2

    def test_less_than(self):
        v1 = VersionSegment.parse("v1.0.0")
        v2 = VersionSegment.parse("v2.0.0")
        assert not (v1 >= v2)
        assert not (v1 > v2)

    def test_parse_partial_version(self):
        v = VersionSegment.parse("v1")
        assert v.major == 1
        assert v.minor == 0
        assert v.patch == 0


class TestDeprecationRecord:
    def test_construction(self):
        rec = DeprecationRecord(
            schema_name=SchemaName.TASKCARD,
            field_name="old_field",
            deprecated_in="v1.0.0",
            removal_target="v3.0.0",
            reason="replaced by new_field",
            migration_guide="Use new_field instead",
        )
        assert rec.schema_name == SchemaName.TASKCARD
        assert rec.field_name == "old_field"


class TestNegotiationResult:
    def test_construction(self):
        result = NegotiationResult(
            schema_name=SchemaName.TASKCARD,
            producer_version="v2.0.0",
            consumer_max_supported="v1.5.0",
            negotiated_version="v1.5.0",
            degraded=True,
            warnings=["Consumer MAJOR behind"],
        )
        assert result.negotiated_version == "v1.5.0"
        assert result.degraded is True
        assert len(result.warnings) == 1


class TestVersionNegotiator:
    def test_register_deprecation(self):
        negotiator = VersionNegotiator()
        rec = negotiator.register_deprecation(
            SchemaName.TASKCARD,
            "old_field",
            "v1.0.0",
            "replaced",
        )
        assert rec.schema_name == SchemaName.TASKCARD
        assert rec.field_name == "old_field"
        removal = VersionSegment.parse(rec.removal_target)
        current = VersionSegment.parse("v1.0.0")
        assert removal.major == current.major + 2

    def test_register_multiple_deprecations(self):
        negotiator = VersionNegotiator()
        negotiator.register_deprecation(SchemaName.TASKCARD, "f1", "v1.0.0")
        negotiator.register_deprecation(SchemaName.FINDING, "f2", "v1.0.0")
        assert len(negotiator._deprecations) == 2

    def test_get_all_deprecations(self):
        negotiator = VersionNegotiator()
        negotiator.register_deprecation(SchemaName.TASKCARD, "x", "v1.0.0")
        assert len(negotiator.get_deprecations()) == 1
        assert len(negotiator.get_deprecations()) == 1

    def test_get_deprecations_by_schema(self):
        negotiator = VersionNegotiator()
        negotiator.register_deprecation(SchemaName.TASKCARD, "f1", "v1.0.0")
        negotiator.register_deprecation(SchemaName.FINDING, "f2", "v1.0.0")
        finding_deps = negotiator.get_deprecations(SchemaName.FINDING)
        assert len(finding_deps) == 1
        assert finding_deps[0].field_name == "f2"

    def test_is_deprecated_before_removal(self):
        negotiator = VersionNegotiator()
        negotiator.register_deprecation(
            SchemaName.TASKCARD,
            "old_field",
            "v1.0.0",
        )
        assert not negotiator.is_deprecated(
            SchemaName.TASKCARD,
            "old_field",
            "v2.9.9",
        )

    def test_is_deprecated_at_removal(self):
        negotiator = VersionNegotiator()
        negotiator.register_deprecation(
            SchemaName.TASKCARD,
            "old_field",
            "v1.0.0",
        )
        removal = VersionSegment(major=3, minor=0, patch=0)
        assert negotiator.is_deprecated(
            SchemaName.TASKCARD,
            "old_field",
            str(removal),
        )

    def test_is_deprecated_unknown_field(self):
        negotiator = VersionNegotiator()
        assert not negotiator.is_deprecated(
            SchemaName.TASKCARD,
            "nonexistent",
            "v5.0.0",
        )

    def test_negotiate_consumer_supports(self):
        negotiator = VersionNegotiator()
        result = negotiator.negotiate(
            SchemaName.TASKCARD,
            "v1.0.0",
            "v2.0.0",
        )
        assert result.negotiated_version == "v1.0.0"
        assert result.degraded is False

    def test_negotiate_consumer_equal(self):
        negotiator = VersionNegotiator()
        result = negotiator.negotiate(
            SchemaName.TASKCARD,
            "v1.5.0",
            "v1.5.0",
        )
        assert result.negotiated_version == "v1.5.0"
        assert result.degraded is False

    def test_negotiate_consumer_major_behind(self):
        negotiator = VersionNegotiator()
        result = negotiator.negotiate(
            SchemaName.TASKCARD,
            "v3.0.0",
            "v2.9.0",
        )
        assert result.negotiated_version == "v2.9.0"
        assert result.degraded is True
        assert len(result.warnings) > 0

    def test_negotiate_consumer_minor_behind(self):
        negotiator = VersionNegotiator()
        result = negotiator.negotiate(
            SchemaName.FINDING,
            "v2.3.0",
            "v2.1.0",
        )
        assert result.negotiated_version == "v2.1.0"
        assert result.degraded is True

    def test_check_breaking_remove_field(self):
        negotiator = VersionNegotiator()
        assert (
            negotiator.check_breaking_change(
                ChangeType.REMOVE_FIELD,
                "v1.0.0",
            )
            is True
        )

    def test_check_breaking_add_required(self):
        negotiator = VersionNegotiator()
        assert (
            negotiator.check_breaking_change(
                ChangeType.ADD_REQUIRED,
                "v1.0.0",
            )
            is True
        )

    def test_check_not_breaking_add_optional(self):
        negotiator = VersionNegotiator()
        assert (
            negotiator.check_breaking_change(
                ChangeType.ADD_OPTIONAL,
                "v1.0.0",
            )
            is False
        )

    def test_required_transition_remove_field(self):
        negotiator = VersionNegotiator()
        assert negotiator.required_transition_versions(ChangeType.REMOVE_FIELD) == 2

    def test_required_transition_add_required(self):
        negotiator = VersionNegotiator()
        assert negotiator.required_transition_versions(ChangeType.ADD_REQUIRED) == 1

    def test_required_transition_add_optional(self):
        negotiator = VersionNegotiator()
        assert negotiator.required_transition_versions(ChangeType.ADD_OPTIONAL) == 0
