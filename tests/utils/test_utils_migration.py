# [A_test] module_id: MOD-GOV_utils_migration | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_utils_migration

# [INVARIANTS] migrate_task幂等;MigrationError路径不存在时抛出;latest_schema_version一致

# [MODIFY-GUARD] migration.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] MigrationError

# [TESTS] pytest tests/test_utils_migration.py -q
# [TTL] task_bound

import pytest

# 治本：从真源导入（非 shim）。shim zephyr.shared.foundation.migration 用 import * 仅 re-export 公共符号，
# 私有 _find_path/_register_bidirectional 未被重新导出。真源在 utils/migration.py。
from zephyr.shared.utils.migration import (
    MIGRATIONS,
    MigrationError,
    _find_path,
    _register_bidirectional,
    downgrade_task,
    latest_schema_version,
    migrate_task,
)


@pytest.fixture(autouse=True)
def _clean_migrations():
    original = dict(MIGRATIONS)
    MIGRATIONS.clear()
    yield
    MIGRATIONS.clear()
    MIGRATIONS.update(original)


def _upgrade_1_0_to_1_1(data):
    data = dict(data)
    data["schema_version"] = "1.1.0"
    data.setdefault("new_field", "default")
    return data


def _downgrade_1_1_to_1_0(data):
    data = dict(data)
    data["schema_version"] = "1.0.0"
    data.pop("new_field", None)
    return data


def _upgrade_1_1_to_2_0(data):
    data = dict(data)
    data["schema_version"] = "2.0.0"
    data.setdefault("v2_field", True)
    return data


def _downgrade_2_0_to_1_1(data):
    data = dict(data)
    data["schema_version"] = "1.1.0"
    data.pop("v2_field", None)
    return data


class TestLatestSchemaVersion:
    def test_returns_string(self):
        result = latest_schema_version()
        assert isinstance(result, str)
        assert "." in result


class TestRegisterBidirectional:
    def test_registers_both_directions(self):
        _register_bidirectional("1.0.0", "1.1.0", _upgrade_1_0_to_1_1, _downgrade_1_1_to_1_0)
        assert "1.1.0" in MIGRATIONS["1.0.0"]
        assert "1.0.0" in MIGRATIONS["1.1.0"]


class TestFindPath:
    def test_same_version_returns_empty(self):
        _register_bidirectional("1.0.0", "1.1.0", _upgrade_1_0_to_1_1, _downgrade_1_1_to_1_0)
        result = _find_path("1.0.0", "1.0.0")
        assert result == []

    def test_direct_path(self):
        _register_bidirectional("1.0.0", "1.1.0", _upgrade_1_0_to_1_1, _downgrade_1_1_to_1_0)
        result = _find_path("1.0.0", "1.1.0")
        assert result == ["1.1.0"]

    def test_no_path_returns_empty(self):
        result = _find_path("1.0.0", "9.9.9")
        assert result == []

    def test_multi_hop_path(self):
        _register_bidirectional("1.0.0", "1.1.0", _upgrade_1_0_to_1_1, _downgrade_1_1_to_1_0)
        _register_bidirectional("1.1.0", "2.0.0", _upgrade_1_1_to_2_0, _downgrade_2_0_to_1_1)
        result = _find_path("1.0.0", "2.0.0")
        assert result == ["1.1.0", "2.0.0"]


class TestMigrateTask:
    def test_same_version_idempotent(self):
        data = {"task_id": "T-001", "schema_version": "1.0.0"}
        result = migrate_task(data)
        assert result["schema_version"] == "1.0.0"

    def test_single_step_upgrade(self):
        _register_bidirectional("1.0.0", "1.1.0", _upgrade_1_0_to_1_1, _downgrade_1_1_to_1_0)
        data = {"task_id": "T-001", "schema_version": "1.0.0"}
        result = migrate_task(data, to_version="1.1.0")
        assert result["schema_version"] == "1.1.0"
        assert result["new_field"] == "default"

    def test_multi_step_upgrade(self):
        _register_bidirectional("1.0.0", "1.1.0", _upgrade_1_0_to_1_1, _downgrade_1_1_to_1_0)
        _register_bidirectional("1.1.0", "2.0.0", _upgrade_1_1_to_2_0, _downgrade_2_0_to_1_1)
        data = {"task_id": "T-001", "schema_version": "1.0.0"}
        result = migrate_task(data, to_version="2.0.0")
        assert result["schema_version"] == "2.0.0"
        assert result["new_field"] == "default"
        assert result["v2_field"] is True

    def test_no_path_raises(self):
        data = {"task_id": "T-001", "schema_version": "1.0.0"}
        with pytest.raises(MigrationError, match="找不到"):
            migrate_task(data, to_version="9.9.9")

    def test_does_not_mutate_original(self):
        _register_bidirectional("1.0.0", "1.1.0", _upgrade_1_0_to_1_1, _downgrade_1_1_to_1_0)
        data = {"task_id": "T-001", "schema_version": "1.0.0"}
        migrate_task(data, to_version="1.1.0")
        assert data["schema_version"] == "1.0.0"

    def test_default_schema_version(self):
        data = {"task_id": "T-001"}
        result = migrate_task(data)
        assert "schema_version" in result


class TestDowngradeTask:
    def test_downgrade(self):
        _register_bidirectional("1.0.0", "1.1.0", _upgrade_1_0_to_1_1, _downgrade_1_1_to_1_0)
        data = {"task_id": "T-001", "schema_version": "1.1.0", "new_field": "val"}
        result = downgrade_task(data, to_version="1.0.0")
        assert result["schema_version"] == "1.0.0"
        assert "new_field" not in result
