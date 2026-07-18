# [A_test] module_id: SRC-TST-2088 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-705 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_version_negotiation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""版本协商器单元测试——forward-compat + deprecation 流程验证。"""

from __future__ import annotations

import pytest

from zephyr.shared.versioning.version_negotiation import (
    ChangeType,
    SchemaName,
    VersionNegotiator,
    VersionSegment,
)


@pytest.fixture
def negotiator():
    return VersionNegotiator()


class TestVersionSegment:
    def test_parse_simple(self):
        v = VersionSegment.parse("v1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_parse_no_v_prefix(self):
        v = VersionSegment.parse("2.0.0")
        assert v.major == 2

    def test_comparison(self):
        assert VersionSegment.parse("v2.0.0") > VersionSegment.parse("v1.9.9")
        assert VersionSegment.parse("v1.0.1") > VersionSegment.parse("v1.0.0")

    def test_equals(self):
        assert VersionSegment.parse("v1.0.0").major == VersionSegment.parse("v1.0.0").major


class TestDeprecation:
    def test_register_deprecation(self, negotiator):
        record = negotiator.register_deprecation(SchemaName.TASKCARD, "old_field", "v1.0.0", reason="已废弃")
        assert record.deprecated_in == "v1.0.0"
        assert record.removal_target == "v3.0.0"

    def test_is_deprecated_before_removal(self, negotiator):
        negotiator.register_deprecation(SchemaName.TASKCARD, "old_field", "v1.0.0")
        assert not negotiator.is_deprecated(SchemaName.TASKCARD, "old_field", "v2.0.0")

    def test_is_deprecated_after_removal(self, negotiator):
        negotiator.register_deprecation(SchemaName.TASKCARD, "old_field", "v1.0.0")
        assert negotiator.is_deprecated(SchemaName.TASKCARD, "old_field", "v3.0.0")

    def test_filter_by_schema(self, negotiator):
        negotiator.register_deprecation(SchemaName.TASKCARD, "a", "v1.0.0")
        negotiator.register_deprecation(SchemaName.FINDING, "b", "v1.0.0")
        taskcard_deps = negotiator.get_deprecations(SchemaName.TASKCARD)
        assert len(taskcard_deps) == 1
        assert taskcard_deps[0].field_name == "a"


class TestNegotiate:
    def test_consumer_supports_producer_version(self, negotiator):
        result = negotiator.negotiate(SchemaName.TASKCARD, "v1.0.0", "v2.0.0")
        assert result.negotiated_version == "v1.0.0"
        assert not result.degraded

    def test_consumer_behind_producer(self, negotiator):
        result = negotiator.negotiate(SchemaName.TASKCARD, "v2.0.0", "v1.0.0")
        assert result.degraded
        assert result.negotiated_version == "v1.0.0"

    def test_consumer_same_version(self, negotiator):
        result = negotiator.negotiate(SchemaName.TASKCARD, "v1.5.0", "v1.5.0")
        assert not result.degraded


class TestBreakingChange:
    def test_type_change_is_breaking(self, negotiator):
        assert negotiator.check_breaking_change(ChangeType.TYPE_CHANGE, "v1.0.0")

    def test_add_optional_not_breaking(self, negotiator):
        assert not negotiator.check_breaking_change(ChangeType.ADD_OPTIONAL, "v1.0.0")

    def test_required_transition_2_for_type_change(self, negotiator):
        assert negotiator.required_transition_versions(ChangeType.TYPE_CHANGE) == 2
