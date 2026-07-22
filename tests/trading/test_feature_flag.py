# [A_test] module_id: MOD-GOV_feature_flag | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] tests.test_feature_flag
# [INVARIANTS] is_enabled 未注册时按 default 返回或抛 FlagNotFoundError; set 创建 flag+审计条目
# [MODIFY-GUARD] src/zephyr/shared/foundation/flags.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] set/is_enabled/get_all 对已注册 flag 永不抛异常
# [TESTS] tests/trading/test_feature_flag.py
# [TTL] task_bound

# 5.38.1/5.38.7 治本：orchestrator/governance/feature_flag.py 已删除，
# 能力收敛至 canonical 真源 zephyr.shared.foundation.flags（D_SHARED 层）。
# 本测试从旧 FeatureFlagManager API 迁移到 canonical FlagRegistry API。

from __future__ import annotations

import json

import pytest

from zephyr.shared.foundation.flags import (
    FeatureFlag,
    FlagNotFoundError,
    FlagRegistry,
    FlagState,
)


class TestFeatureFlagModel:
    def test_default_values(self):
        flag = FeatureFlag(key="CT-TEST")
        assert flag.key == "CT-TEST"
        assert flag.state == FlagState.ALWAYS_OFF
        assert flag.description == ""

    def test_custom_values(self):
        flag = FeatureFlag(key="CT-X", state=FlagState.ALWAYS_ON, description="test flag")
        assert flag.is_enabled() is True
        assert flag.description == "test flag"


class TestFlagRegistryInstantiation:
    def test_empty_flags_on_init(self):
        registry = FlagRegistry()
        assert registry._flags == {}

    def test_empty_audit_on_init(self):
        registry = FlagRegistry()
        assert registry._audit == []


class TestSet:
    def test_set_returns_feature_flag(self):
        registry = FlagRegistry()
        flag = registry.set("CT-TEST", True)
        assert isinstance(flag, FeatureFlag)
        assert flag.key == "CT-TEST"
        assert flag.state == FlagState.ALWAYS_ON

    def test_set_stores_flag(self):
        registry = FlagRegistry()
        registry.set("CT-A", True, "desc A")
        assert "CT-A" in registry._flags
        assert registry._flags["CT-A"].is_enabled() is True
        assert registry._flags["CT-A"].description == "desc A"

    def test_set_appends_audit(self):
        registry = FlagRegistry()
        registry.set("CT-B", False, "audit test")
        assert len(registry._audit) == 1
        assert registry._audit[0]["key"] == "CT-B"
        assert registry._audit[0]["state"] == FlagState.ALWAYS_OFF.value

    def test_set_overwrites_existing(self):
        registry = FlagRegistry()
        registry.set("CT-C", True)
        registry.set("CT-C", False)
        assert registry._flags["CT-C"].is_enabled() is False
        assert len(registry._audit) == 2


class TestIsEnabled:
    def test_unknown_flag_raises_without_default(self):
        registry = FlagRegistry()
        with pytest.raises(FlagNotFoundError):
            registry.is_enabled("UNKNOWN")

    def test_unknown_flag_returns_default(self):
        registry = FlagRegistry()
        assert registry.is_enabled("UNKNOWN", default=True) is True
        assert registry.is_enabled("UNKNOWN", default=False) is False

    def test_enabled_flag_returns_true(self):
        registry = FlagRegistry()
        registry.set("CT-ON", True)
        assert registry.is_enabled("CT-ON") is True

    def test_disabled_flag_returns_false(self):
        registry = FlagRegistry()
        registry.set("CT-OFF", False)
        assert registry.is_enabled("CT-OFF") is False


class TestGetAll:
    def test_empty_registry_returns_empty(self):
        registry = FlagRegistry()
        assert registry.get_all() == {}

    def test_returns_enabled_mapping(self):
        registry = FlagRegistry()
        registry.set("CT-X", True)
        registry.set("CT-Y", False)
        result = registry.get_all()
        assert result == {"CT-X": True, "CT-Y": False}


class TestAuditPersistence:
    """5.38.6：审计轨迹持久化 JSONL（tmp_path 隔离，不写生产路径）。"""

    def test_audit_written_to_jsonl(self, tmp_path):
        audit_file = tmp_path / "feature_flags.jsonl"
        registry = FlagRegistry(audit_path=audit_file)
        registry.set("CT-PERSIST", True, "persist test")
        registry.unregister("CT-PERSIST")

        lines = audit_file.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        first = json.loads(lines[0])
        assert first["action"] == "register"
        assert first["key"] == "CT-PERSIST"
        assert first["state"] == FlagState.ALWAYS_ON.value
        assert "timestamp" in first
        second = json.loads(lines[1])
        assert second["action"] == "unregister"
        assert second["key"] == "CT-PERSIST"

    def test_no_persistence_by_default(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        registry = FlagRegistry()
        registry.set("CT-NOPERSIST", True)
        assert not (tmp_path / "data").exists()

    def test_audit_failure_does_not_raise(self, tmp_path):
        bad_path = tmp_path / "nonexistent_dir_x" / "\0bad" / "audit.jsonl"
        registry = FlagRegistry(audit_path=bad_path)
        flag = registry.set("CT-RESILIENT", True)
        assert flag.is_enabled() is True
        assert len(registry._audit) == 1


class TestLoadFlagsFromYaml:
    """5.38.4：flags.yaml 加载到 FlagRegistry。"""

    def test_loads_top_level_flags(self, tmp_path):
        from zephyr.shared.foundation.flags import load_flags_from_yaml

        yaml_file = tmp_path / "flags.yaml"
        yaml_file.write_text(
            "flags:\n"
            "  auto_bootstrap:\n"
            "    enabled: true\n"
            '    description: "自动注入遥测hooks"\n'
            "  archive:\n"
            "    enabled: false\n"
            '    description: "遥测数据归档"\n',
            encoding="utf-8",
        )
        registry = FlagRegistry()
        count = load_flags_from_yaml(yaml_file, registry=registry)
        assert count == 2
        assert registry.is_enabled("auto_bootstrap") is True
        assert registry.is_enabled("archive") is False

    def test_missing_yaml_returns_zero(self, tmp_path):
        from zephyr.shared.foundation.flags import load_flags_from_yaml

        registry = FlagRegistry()
        assert load_flags_from_yaml(tmp_path / "nope.yaml", registry=registry) == 0

    def test_real_config_flags_yaml_loads(self):
        from zephyr.shared.foundation.flags import load_flags_from_yaml
        from zephyr.shared.io.paths import REPO_ROOT

        registry = FlagRegistry()
        count = load_flags_from_yaml(REPO_ROOT / "config" / "flags.yaml", registry=registry)
        assert count >= 9  # metrics/logs/traces/ai_behavior/archive/health/alerts/schema_validation/auto_bootstrap/...
        assert registry.is_enabled("auto_bootstrap") is True


class TestBoundary:
    def test_set_empty_key(self):
        registry = FlagRegistry()
        flag = registry.set("", True)
        assert flag.key == ""
        assert registry.is_enabled("") is True

    def test_set_empty_description(self):
        registry = FlagRegistry()
        flag = registry.set("CT-Z", True, "")
        assert flag.description == ""

    def test_multiple_sets_accumulate_audit(self):
        registry = FlagRegistry()
        for i in range(5):
            registry.set(f"CT-{i}", True)
        assert len(registry._audit) == 5
