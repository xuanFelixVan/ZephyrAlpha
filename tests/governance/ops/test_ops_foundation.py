# [A_test] module_id: SRC-TST-1333 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-415 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_ops_foundation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.ops_governance.ops_foundation import (
    OPS_BACKUPS,
    OPS_LOG_CATEGORIES,
    BackupLayer,
    LogCategory,
    verify_config,
)


class TestBackupLayer:
    def test_enum_values(self):
        assert BackupLayer.GIT == "Git"
        assert BackupLayer.CLOUD_ZIP == "CloudZipDaily"
        assert BackupLayer.DB_DUMP == "DbDumpTwice"
        assert BackupLayer.SECRETS_VAULT == "SecretsVault"

    def test_enum_members_count(self):
        assert len(BackupLayer) == 4


class TestLogCategory:
    def test_enum_values(self):
        assert LogCategory.SYSTEM == "System"
        assert LogCategory.ORDER == "Order"
        assert LogCategory.MARKET == "Market"
        assert LogCategory.AI_DECISION == "AI_Decision"

    def test_enum_members_count(self):
        assert len(LogCategory) == 4


class TestOpsBackups:
    def test_all_layers_mapped(self):
        for layer in BackupLayer:
            assert layer in OPS_BACKUPS

    def test_values_match_enum(self):
        for layer, value in OPS_BACKUPS.items():
            assert value == layer.value


class TestOpsLogCategories:
    def test_all_categories_mapped(self):
        for cat in LogCategory:
            assert cat in OPS_LOG_CATEGORIES

    def test_values_match_enum(self):
        for cat, value in OPS_LOG_CATEGORIES.items():
            assert value == cat.value


class TestVerifyConfig:
    def test_matching_configs(self):
        ok, msg = verify_config("abc", "abc")
        assert ok is True
        assert msg == "OK"

    def test_drift_detected(self):
        ok, msg = verify_config("abc", "xyz")
        assert ok is False
        assert "DRIFT" in msg

    def test_empty_strings_match(self):
        ok, msg = verify_config("", "")
        assert ok is True

    def test_empty_vs_nonempty(self):
        ok, msg = verify_config("", "something")
        assert ok is False
