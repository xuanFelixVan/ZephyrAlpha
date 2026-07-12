# [A_test] module_id: SRC-TST-0452 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §

# [MODULE] tests.test_breaking_change_detector

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] none

# [TESTS] pytest tests/test_breaking_change_detector.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_enforcement.rule_enforcement.breaking_change_detector import BreakingChangeDetector, ChangeType


class TestChangeType:
    def test_enum_values(self):
        assert ChangeType.FIELD_REMOVED.value == "field_removed"
        assert ChangeType.TYPE_CHANGED.value == "type_changed"
        assert ChangeType.FIELD_ADDED_OPTIONAL.value == "field_added_optional"
        assert ChangeType.FIELD_ADDED_REQUIRED.value == "field_added_required"
        assert ChangeType.FIELD_RENAMED.value == "field_renamed"

    def test_enum_count(self):
        assert len(ChangeType) == 5

    def test_enum_is_str(self):
        for ct in ChangeType:
            assert isinstance(ct, str)


class TestBreakingChangeDetectorInstantiation:
    def test_instantiation(self):
        detector = BreakingChangeDetector()
        assert detector is not None

    def test_breaking_changes_set_exists(self):
        detector = BreakingChangeDetector()
        assert hasattr(detector, "BREAKING_CHANGES")
        assert isinstance(detector.BREAKING_CHANGES, set)

    def test_breaking_changes_set_contents(self):
        detector = BreakingChangeDetector()
        assert ChangeType.FIELD_REMOVED in detector.BREAKING_CHANGES
        assert ChangeType.TYPE_CHANGED in detector.BREAKING_CHANGES
        assert ChangeType.FIELD_RENAMED in detector.BREAKING_CHANGES
        assert ChangeType.FIELD_ADDED_REQUIRED in detector.BREAKING_CHANGES

    def test_breaking_changes_set_excludes_optional(self):
        detector = BreakingChangeDetector()
        assert ChangeType.FIELD_ADDED_OPTIONAL not in detector.BREAKING_CHANGES

    def test_breaking_changes_set_size(self):
        detector = BreakingChangeDetector()
        assert len(detector.BREAKING_CHANGES) == 4


class TestIsBreaking:
    def test_field_removed_is_breaking(self):
        detector = BreakingChangeDetector()
        assert detector.is_breaking(ChangeType.FIELD_REMOVED) is True

    def test_type_changed_is_breaking(self):
        detector = BreakingChangeDetector()
        assert detector.is_breaking(ChangeType.TYPE_CHANGED) is True

    def test_field_renamed_is_breaking(self):
        detector = BreakingChangeDetector()
        assert detector.is_breaking(ChangeType.FIELD_RENAMED) is True

    def test_field_added_required_is_breaking(self):
        detector = BreakingChangeDetector()
        assert detector.is_breaking(ChangeType.FIELD_ADDED_REQUIRED) is True

    def test_field_added_optional_is_not_breaking(self):
        detector = BreakingChangeDetector()
        assert detector.is_breaking(ChangeType.FIELD_ADDED_OPTIONAL) is False

    def test_all_change_types_covered(self):
        detector = BreakingChangeDetector()
        for ct in ChangeType:
            result = detector.is_breaking(ct)
            assert isinstance(result, bool)


class TestDetect:
    def test_no_changes(self):
        detector = BreakingChangeDetector()
        schema = {"fields": {"name": "str", "age": "int"}}
        result = detector.detect(schema, schema)
        assert result == []

    def test_field_removed(self):
        detector = BreakingChangeDetector()
        old = {"fields": {"name": "str", "age": "int", "email": "str"}}
        new = {"fields": {"name": "str", "age": "int"}}
        result = detector.detect(old, new)
        assert len(result) == 1
        assert "FIELD_REMOVED: email" in result

    def test_multiple_fields_removed(self):
        detector = BreakingChangeDetector()
        old = {"fields": {"a": "int", "b": "str", "c": "float"}}
        new = {"fields": {}}
        result = detector.detect(old, new)
        assert len(result) == 3
        for f in ["a", "b", "c"]:
            assert f"FIELD_REMOVED: {f}" in result

    def test_type_changed(self):
        detector = BreakingChangeDetector()
        old = {"fields": {"name": "str"}}
        new = {"fields": {"name": "int"}}
        result = detector.detect(old, new)
        assert len(result) == 1
        assert "TYPE_CHANGED: name" in result

    def test_multiple_type_changes(self):
        detector = BreakingChangeDetector()
        old = {"fields": {"name": "str", "age": "int"}}
        new = {"fields": {"name": "bytes", "age": "float"}}
        result = detector.detect(old, new)
        assert len(result) == 2
        assert "TYPE_CHANGED: name" in result
        assert "TYPE_CHANGED: age" in result

    def test_field_removed_and_type_changed(self):
        detector = BreakingChangeDetector()
        old = {"fields": {"name": "str", "age": "int", "email": "str"}}
        new = {"fields": {"name": "bytes", "age": "int"}}
        result = detector.detect(old, new)
        assert len(result) == 2
        assert "FIELD_REMOVED: email" in result
        assert "TYPE_CHANGED: name" in result

    def test_field_added_not_reported(self):
        detector = BreakingChangeDetector()
        old = {"fields": {"name": "str"}}
        new = {"fields": {"name": "str", "email": "str"}}
        result = detector.detect(old, new)
        assert result == []

    def test_empty_old_schema(self):
        detector = BreakingChangeDetector()
        old = {}
        new = {"fields": {"name": "str"}}
        result = detector.detect(old, new)
        assert result == []

    def test_empty_new_schema(self):
        detector = BreakingChangeDetector()
        old = {"fields": {"name": "str"}}
        new = {}
        result = detector.detect(old, new)
        assert len(result) == 1
        assert "FIELD_REMOVED: name" in result

    def test_both_empty_schemas(self):
        detector = BreakingChangeDetector()
        result = detector.detect({}, {})
        assert result == []

    def test_both_empty_fields(self):
        detector = BreakingChangeDetector()
        result = detector.detect({"fields": {}}, {"fields": {}})
        assert result == []

    def test_none_old_schema_raises(self):
        detector = BreakingChangeDetector()
        with pytest.raises(AttributeError):
            detector.detect(None, {"fields": {}})

    def test_none_new_schema_raises(self):
        detector = BreakingChangeDetector()
        with pytest.raises(AttributeError):
            detector.detect({"fields": {}}, None)

    def test_both_none_schemas_raises(self):
        detector = BreakingChangeDetector()
        with pytest.raises(AttributeError):
            detector.detect(None, None)

    def test_same_type_not_reported(self):
        detector = BreakingChangeDetector()
        old = {"fields": {"name": "str"}}
        new = {"fields": {"name": "str"}}
        result = detector.detect(old, new)
        assert result == []

    def test_detect_returns_list(self):
        detector = BreakingChangeDetector()
        result = detector.detect({}, {})
        assert isinstance(result, list)

    def test_detect_returns_strings(self):
        detector = BreakingChangeDetector()
        old = {"fields": {"x": "int"}}
        new = {"fields": {}}
        result = detector.detect(old, new)
        for item in result:
            assert isinstance(item, str)
