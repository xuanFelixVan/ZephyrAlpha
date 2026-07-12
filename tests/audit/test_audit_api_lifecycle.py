# [A_test] module_id: SRC-TST-0343 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_audit_api_lifecycle
# [INVARIANTS] APIState transitions; DeprecationNotice expiry logic
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass; exit non-zero on fail
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from zephyr.gov_audit.api_lifecycle import (
    APIEndpoint,
    APIState,
    DeprecationNotice,
    deprecate_api,
    remove_api,
)


class TestAPIState:
    def test_enum_values(self):
        assert APIState.ACTIVE == "Active"
        assert APIState.DEPRECATED == "Deprecated"
        assert APIState.REMOVED == "Removed"


class TestDeprecationNotice:
    def test_days_until_removal_future(self):
        notice = DeprecationNotice(
            api_name="test_api",
            deprecated_at=datetime.now(UTC).isoformat(),
            removal_at=(datetime.now(UTC) + timedelta(days=30)).isoformat(),
            grace_period_days=90,
        )
        assert notice.days_until_removal > 0

    def test_days_until_removal_expired(self):
        notice = DeprecationNotice(
            api_name="test_api",
            deprecated_at="2020-01-01T00:00:00+00:00",
            removal_at="2020-04-01T00:00:00+00:00",
            grace_period_days=90,
        )
        assert notice.days_until_removal == 0

    def test_expired_property(self):
        notice = DeprecationNotice(
            api_name="test_api",
            deprecated_at="2020-01-01T00:00:00+00:00",
            removal_at="2020-04-01T00:00:00+00:00",
            grace_period_days=90,
        )
        assert notice.expired is True

    def test_not_expired_property(self):
        notice = DeprecationNotice(
            api_name="test_api",
            deprecated_at=datetime.now(UTC).isoformat(),
            removal_at=(datetime.now(UTC) + timedelta(days=90)).isoformat(),
            grace_period_days=90,
        )
        assert notice.expired is False

    def test_days_until_removal_invalid_date(self):
        notice = DeprecationNotice(
            api_name="test_api",
            deprecated_at="not-a-date",
            removal_at="not-a-date",
        )
        assert notice.days_until_removal == 0


class TestAPIEndpoint:
    def test_default_state_is_active(self):
        ep = APIEndpoint(name="test", version="1.0")
        assert ep.state == APIState.ACTIVE
        assert ep.deprecation is None

    def test_with_deprecation(self):
        notice = DeprecationNotice(
            api_name="test",
            deprecated_at=datetime.now(UTC).isoformat(),
            removal_at=(datetime.now(UTC) + timedelta(days=90)).isoformat(),
        )
        ep = APIEndpoint(name="test", version="1.0", deprecation=notice)
        assert ep.deprecation is not None


class TestDeprecateApi:
    def test_deprecate_sets_state(self):
        ep = APIEndpoint(name="my_api", version="2.0")
        notice = deprecate_api(ep, migration_guide="Use new_api instead")
        assert ep.state == APIState.DEPRECATED
        assert ep.deprecation is not None
        assert ep.deprecation.migration_guide == "Use new_api instead"

    def test_deprecate_custom_grace_period(self):
        ep = APIEndpoint(name="my_api", version="2.0")
        notice = deprecate_api(ep, grace_period_days=30)
        assert notice.grace_period_days == 30
        assert ep.deprecation.grace_period_days == 30


class TestRemoveApi:
    def test_remove_sets_state_and_sunset(self):
        ep = APIEndpoint(name="old_api", version="1.0")
        remove_api(ep)
        assert ep.state == APIState.REMOVED
        assert ep.sunset_date is not None
