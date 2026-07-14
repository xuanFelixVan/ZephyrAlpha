# [A_test] module_id: SRC-TST-0697 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md
# [MODULE] tests.test_data_lifecycle
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/data_lifecycle.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip
# [TESTS] python -m pytest tests/test_data_lifecycle.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.data_governance.data_lifecycle import (
    ARCHIVE_AFTER_YEARS,
    GDPR_PII_FIELDS,
    PURGE_AFTER_YEARS,
    DataStage,
    forget_pii,
)


class TestDataStage:
    def test_enum_values(self):
        assert DataStage.CREATE.value == "Create"
        assert DataStage.STORE.value == "Store"
        assert DataStage.USE.value == "Use"
        assert DataStage.ARCHIVE.value == "Archive"
        assert DataStage.PURGE.value == "Purge"

    def test_enum_is_str(self):
        for stage in DataStage:
            assert isinstance(stage.value, str)

    def test_enum_members_count(self):
        assert len(DataStage) == 5

    def test_enum_access_by_name(self):
        assert DataStage["CREATE"] is DataStage.CREATE
        assert DataStage["PURGE"] is DataStage.PURGE

    def test_enum_iteration(self):
        members = list(DataStage)
        assert len(members) == 5
        assert DataStage.CREATE in members


class TestConstants:
    def test_archive_after_years(self):
        assert isinstance(ARCHIVE_AFTER_YEARS, int)
        assert ARCHIVE_AFTER_YEARS > 0

    def test_purge_after_years(self):
        assert isinstance(PURGE_AFTER_YEARS, int)
        assert PURGE_AFTER_YEARS > ARCHIVE_AFTER_YEARS

    def test_gdpr_pii_fields(self):
        assert isinstance(GDPR_PII_FIELDS, list)
        assert len(GDPR_PII_FIELDS) > 0
        for field in GDPR_PII_FIELDS:
            assert isinstance(field, str)
            assert len(field) > 0


class TestForgetPii:
    def test_returns_dict(self):
        result = forget_pii()
        assert isinstance(result, dict)

    def test_action_key(self):
        result = forget_pii()
        assert "action" in result
        assert result["action"] == "permanent_delete"

    def test_cert_key(self):
        result = forget_pii()
        assert "cert" in result
        assert isinstance(result["cert"], str)
        assert len(result["cert"]) > 0

    def test_result_has_expected_keys(self):
        result = forget_pii()
        assert set(result.keys()) == {"action", "cert"}
