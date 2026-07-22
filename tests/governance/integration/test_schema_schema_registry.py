# [A_test] module_id: MOD-GOV_schema_schema_registry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_schema_schema_registry

# [INVARIANTS] 重复注册同版本抛SchemaRegistryError;latest返回最高版本;compatible_versions_for同MAJOR

# [MODIFY-GUARD] schema_registry.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] SchemaRegistryError

# [TESTS] pytest tests/test_schema_schema_registry.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.schema.schema_registry import (
    SchemaEntry,
    SchemaRegistry,
    SchemaRegistryError,
    SchemaVersion,
    get_schema_registry,
)


def _make_entry(name: str, version: str, major: int, minor: int, **kwargs):
    return SchemaEntry(
        schema_name=name,
        version=version,
        major_version=major,
        minor_version=minor,
        module_id="MOD-INF-016",
        description=f"{name} v{version}",
        added_in="0.1.0",
        **kwargs,
    )


class TestSchemaVersion:
    def test_members(self):
        assert SchemaVersion.V1_0.value == "1.0"
        assert SchemaVersion.V2_0.value == "2.0"


class TestSchemaEntry:
    def test_creation(self):
        entry = _make_entry("Task", "0.5.0", 0, 5)
        assert entry.schema_name == "Task"
        assert entry.version == "0.5.0"
        assert entry.breaking is False
        assert entry.supersedes is None

    def test_frozen(self):
        entry = _make_entry("Task", "0.5.0", 0, 5)
        with pytest.raises(AttributeError):
            entry.version = "0.6.0"


class TestSchemaRegistry:
    @pytest.fixture(autouse=True)
    def _fresh_registry(self):
        reg = SchemaRegistry()
        yield reg

    def test_register_and_get(self, _fresh_registry):
        reg = _fresh_registry
        entry = _make_entry("Task", "0.5.0", 0, 5)
        reg.register(entry)
        result = reg.get("Task", "0.5.0")
        assert result.schema_name == "Task"

    def test_register_duplicate_raises(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_make_entry("Task", "0.5.0", 0, 5))
        with pytest.raises(SchemaRegistryError, match="already registered"):
            reg.register(_make_entry("Task", "0.5.0", 0, 5))

    def test_get_missing_schema_raises(self, _fresh_registry):
        reg = _fresh_registry
        with pytest.raises(SchemaRegistryError, match="not found"):
            reg.get("Missing", "0.1.0")

    def test_get_missing_version_raises(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_make_entry("Task", "0.5.0", 0, 5))
        with pytest.raises(SchemaRegistryError, match="not found"):
            reg.get("Task", "9.9.9")

    def test_latest(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_make_entry("Task", "0.5.0", 0, 5))
        reg.register(_make_entry("Task", "0.7.0", 0, 7))
        reg.register(_make_entry("Task", "0.6.0", 0, 6))
        result = reg.latest("Task")
        assert result.version == "0.7.0"

    def test_latest_nonexistent(self, _fresh_registry):
        reg = _fresh_registry
        assert reg.latest("Missing") is None

    def test_versions_sorted(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_make_entry("Task", "0.7.0", 0, 7))
        reg.register(_make_entry("Task", "0.5.0", 0, 5))
        versions = reg.versions("Task")
        assert [v.version for v in versions] == ["0.5.0", "0.7.0"]

    def test_versions_empty(self, _fresh_registry):
        reg = _fresh_registry
        assert reg.versions("Missing") == []

    def test_compatible_versions_for(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_make_entry("Task", "0.5.0", 0, 5))
        reg.register(_make_entry("Task", "0.6.0", 0, 6))
        reg.register(_make_entry("Task", "1.0.0", 1, 0))
        compat = reg.compatible_versions_for("0.6.0", "Task")
        versions = [e.version for e in compat]
        assert "0.6.0" in versions
        assert "1.0.0" not in versions

    def test_check_register_compatible_same_major(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_make_entry("Task", "0.5.0", 0, 5))
        assert reg.check_register_compatible(_make_entry("Task", "0.6.0", 0, 6)) is True

    def test_check_register_compatible_different_major_raises(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_make_entry("Task", "0.5.0", 0, 5))
        with pytest.raises(SchemaRegistryError, match="major version change"):
            reg.check_register_compatible(_make_entry("Task", "1.0.0", 1, 0))

    def test_schema_count(self, _fresh_registry):
        reg = _fresh_registry
        assert reg.schema_count == 0
        reg.register(_make_entry("Task", "0.5.0", 0, 5))
        assert reg.schema_count == 1

    def test_list_schemas(self, _fresh_registry):
        reg = _fresh_registry
        reg.register(_make_entry("Task", "0.5.0", 0, 5))
        reg.register(_make_entry("Audit", "0.1.0", 0, 1))
        assert reg.list_schemas() == ["Audit", "Task"]


class TestGetSchemaRegistry:
    def test_returns_registry(self):
        reg = get_schema_registry()
        assert isinstance(reg, SchemaRegistry)


class TestSchemaRegistryError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = SchemaRegistryError("fail", details={"schema": "X"})
        assert isinstance(err, ZephyrBaseError)
