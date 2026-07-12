# [A_test] module_id: SRC-TST-0932 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_api_version_contract
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.actors.api_version_contract
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_api_version_contract.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.actors.api_version_contract import APIVersionContract, VersionStatus


class TestAPIVersionContractInstantiation:
    def test_creates_with_defaults(self):
        contract = APIVersionContract(api_name="test_api", version="v1", sunset_date="2099-01-01")
        assert contract.api_name == "test_api"
        assert contract.version == "v1"
        assert contract.status == VersionStatus.ACTIVE

    def test_creates_with_custom_params(self):
        contract = APIVersionContract(
            api_name="my_api",
            version="v2",
            sunset_date="2025-06-01",
            replacement_version="v3",
            status=VersionStatus.DEPRECATED,
            deprecation_notice_days=60,
        )
        assert contract.status == VersionStatus.DEPRECATED
        assert contract.deprecation_notice_days == 60


class TestCheckSunset:
    def test_returns_false_before_sunset(self):
        contract = APIVersionContract(api_name="a", version="v1", sunset_date="2099-12-31")
        assert contract.check_sunset(today="2026-01-01") is False

    def test_returns_true_on_sunset_date(self):
        contract = APIVersionContract(api_name="a", version="v1", sunset_date="2026-01-01")
        assert contract.check_sunset(today="2026-01-01") is True

    def test_returns_true_after_sunset(self):
        contract = APIVersionContract(api_name="a", version="v1", sunset_date="2025-01-01")
        assert contract.check_sunset(today="2026-01-01") is True


class TestDaysUntilSunset:
    def test_positive_days_before_sunset(self):
        contract = APIVersionContract(api_name="a", version="v1", sunset_date="2099-12-31")
        days = contract.days_until_sunset()
        assert days > 0

    def test_negative_days_after_sunset(self):
        contract = APIVersionContract(api_name="a", version="v1", sunset_date="2020-01-01")
        days = contract.days_until_sunset()
        assert days < 0
