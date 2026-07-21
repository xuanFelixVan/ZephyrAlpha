# [A_test] module_id: MOD-GOV_ba_data_lifecycle | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md
# [MODULE] tests.test_ba_data_lifecycle
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_ba_data_lifecycle.py
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
    def test_all_stages_exist(self):
        assert DataStage.CREATE == "Create"
        assert DataStage.STORE == "Store"
        assert DataStage.USE == "Use"
        assert DataStage.ARCHIVE == "Archive"
        assert DataStage.PURGE == "Purge"

    def test_is_str_enum(self):
        assert isinstance(DataStage.CREATE, str)

    def test_stage_count(self):
        assert len(DataStage) == 5


class TestConstants:
    def test_archive_after_years(self):
        assert ARCHIVE_AFTER_YEARS == 7
        assert isinstance(ARCHIVE_AFTER_YEARS, int)

    def test_purge_after_years(self):
        assert PURGE_AFTER_YEARS == 15
        assert isinstance(PURGE_AFTER_YEARS, int)

    def test_purge_after_greater_than_archive(self):
        assert PURGE_AFTER_YEARS > ARCHIVE_AFTER_YEARS

    def test_gdpr_pii_fields(self):
        assert "user" in GDPR_PII_FIELDS
        assert "payment" in GDPR_PII_FIELDS
        assert "email" in GDPR_PII_FIELDS
        assert len(GDPR_PII_FIELDS) == 3


class TestForgetPii:
    def test_returns_dict(self):
        result = forget_pii()
        assert isinstance(result, dict)

    def test_action_is_permanent_delete(self):
        result = forget_pii()
        assert result["action"] == "permanent_delete"

    def test_cert_provided(self):
        result = forget_pii()
        assert result["cert"] == "provided"

    def test_has_two_keys(self):
        result = forget_pii()
        assert len(result) == 2
