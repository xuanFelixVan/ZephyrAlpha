# [A_test] module_id: MOD-GOV_api_lifecycle | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-348 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_api_lifecycle
# [INVARIANTS] REJECTED status must include rejection_reason; deprecate_api sets DEPRECATED state
# [MODIFY-GUARD] Changes must sync with api_lifecycle.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_api_lifecycle.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from zephyr.governance.lifecycle_governance.api_lifecycle import (
    APIEndpoint,
    APIState,
    DeprecationNotice,
    deprecate_api,
    remove_api,
)


class TestAPIState:
    def test_enum_values(self):
        assert APIState.ACTIVE.value == "Active"
        assert APIState.DEPRECATED.value == "Deprecated"
        assert APIState.REMOVED.value == "Removed"

    def test_enum_count(self):
        assert len(APIState) == 3


class TestDeprecationNotice:
    def test_creation(self):
        notice = DeprecationNotice(
            api_name="test-api",
            deprecated_at=datetime.now(UTC).isoformat(),
            removal_at=(datetime.now(UTC) + timedelta(days=90)).isoformat(),
        )
        assert notice.api_name == "test-api"
        assert notice.grace_period_days == 90

    def test_days_until_removal_positive(self):
        future = datetime.now(UTC) + timedelta(days=45)
        notice = DeprecationNotice(
            api_name="test",
            deprecated_at=datetime.now(UTC).isoformat(),
            removal_at=future.isoformat(),
            grace_period_days=90,
        )
        assert notice.days_until_removal > 0

    def test_days_until_removal_expired(self):
        past = datetime.now(UTC) - timedelta(days=200)
        notice = DeprecationNotice(
            api_name="test",
            deprecated_at=past.isoformat(),
            removal_at=(past + timedelta(days=90)).isoformat(),
            grace_period_days=90,
        )
        assert notice.days_until_removal == 0

    def test_expired_property(self):
        past = datetime.now(UTC) - timedelta(days=200)
        notice = DeprecationNotice(
            api_name="test",
            deprecated_at=past.isoformat(),
            removal_at=(past + timedelta(days=90)).isoformat(),
            grace_period_days=90,
        )
        assert notice.expired is True

    def test_not_expired_property(self):
        notice = DeprecationNotice(
            api_name="test",
            deprecated_at=datetime.now(UTC).isoformat(),
            removal_at=(datetime.now(UTC) + timedelta(days=90)).isoformat(),
            grace_period_days=90,
        )
        assert notice.expired is False

    def test_invalid_date_returns_zero(self):
        notice = DeprecationNotice(
            api_name="test",
            deprecated_at="not-a-date",
            removal_at="also-not-a-date",
        )
        assert notice.days_until_removal == 0


class TestAPIEndpoint:
    def test_creation_default_active(self):
        ep = APIEndpoint(name="my-api", version="1.0")
        assert ep.state == APIState.ACTIVE
        assert ep.deprecation is None

    def test_creation_with_state(self):
        ep = APIEndpoint(name="old-api", version="0.9", state=APIState.DEPRECATED)
        assert ep.state == APIState.DEPRECATED


class TestDeprecateApi:
    def test_deprecate_sets_state(self):
        ep = APIEndpoint(name="my-api", version="1.0")
        notice = deprecate_api(ep, migration_guide="Use v2")
        assert ep.state == APIState.DEPRECATED
        assert ep.deprecation is not None
        assert notice.migration_guide == "Use v2"

    def test_deprecate_notice_fields(self):
        ep = APIEndpoint(name="test", version="1.0")
        notice = deprecate_api(ep, grace_period_days=30)
        assert notice.api_name == "test"
        assert notice.grace_period_days == 30

    def test_deprecate_default_grace_period(self):
        ep = APIEndpoint(name="test", version="1.0")
        notice = deprecate_api(ep)
        assert notice.grace_period_days == 90


class TestRemoveApi:
    def test_remove_sets_state(self):
        ep = APIEndpoint(name="old-api", version="0.1")
        remove_api(ep)
        assert ep.state == APIState.REMOVED
        assert ep.sunset_date is not None

    def test_remove_sets_sunset_date(self):
        ep = APIEndpoint(name="old-api", version="0.1")
        remove_api(ep)
        assert ep.sunset_date is not None
        assert len(ep.sunset_date) > 0
