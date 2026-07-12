# [A_test] module_id: SRC-TST-0324 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_api_version_contract
# [INVARIANTS] sunset_date format YYYY-MM-DD; check_sunset returns bool
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.actors.api_version_contract import (
    APIVersionContract,
    VersionStatus,
)


class TestVersionStatus:
    def test_enum_values(self):
        assert VersionStatus.ACTIVE == "ACTIVE"
        assert VersionStatus.DEPRECATED == "DEPRECATED"
        assert VersionStatus.SUNSET == "SUNSET"


class TestAPIVersionContractInstantiation:
    def test_default_construction(self):
        contract = APIVersionContract(api_name="test_api", version="v1", sunset_date="2026-12-31")
        assert contract.api_name == "test_api"
        assert contract.version == "v1"
        assert contract.sunset_date == "2026-12-31"
        assert contract.replacement_version == ""
        assert contract.status == VersionStatus.ACTIVE
        assert contract.deprecation_notice_days == 90

    def test_custom_fields(self):
        contract = APIVersionContract(
            api_name="my_api",
            version="v2",
            sunset_date="2026-06-01",
            replacement_version="v3",
            status=VersionStatus.DEPRECATED,
            deprecation_notice_days=30,
        )
        assert contract.replacement_version == "v3"
        assert contract.status == VersionStatus.DEPRECATED
        assert contract.deprecation_notice_days == 30


class TestCheckSunset:
    def test_before_sunset_returns_false(self):
        contract = APIVersionContract(api_name="api", version="v1", sunset_date="2099-01-01")
        assert contract.check_sunset(today="2026-01-01") is False

    def test_on_sunset_returns_true(self):
        contract = APIVersionContract(api_name="api", version="v1", sunset_date="2026-05-22")
        assert contract.check_sunset(today="2026-05-22") is True

    def test_after_sunset_returns_true(self):
        contract = APIVersionContract(api_name="api", version="v1", sunset_date="2020-01-01")
        assert contract.check_sunset(today="2026-01-01") is True

    def test_today_defaults_to_current_date(self):
        contract = APIVersionContract(api_name="api", version="v1", sunset_date="2020-01-01")
        assert contract.check_sunset() is True


class TestDaysUntilSunset:
    def test_future_sunset_positive(self):
        contract = APIVersionContract(api_name="api", version="v1", sunset_date="2099-12-31")
        assert contract.days_until_sunset() > 0

    def test_past_sunset_negative(self):
        contract = APIVersionContract(api_name="api", version="v1", sunset_date="2020-01-01")
        assert contract.days_until_sunset() < 0


class TestBoundaryCases:
    def test_invalid_sunset_date_raises(self):
        contract = APIVersionContract(api_name="api", version="v1", sunset_date="not-a-date")
        with pytest.raises(ValueError):
            contract.check_sunset()

    def test_invalid_today_raises(self):
        contract = APIVersionContract(api_name="api", version="v1", sunset_date="2026-12-31")
        with pytest.raises(ValueError):
            contract.check_sunset(today="bad-date")
