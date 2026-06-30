# [A_test] module_id: SRC-TST-0930 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_alert_router
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.observability.feedback_loop.actors.alert_router
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_alert_router.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.ops.actors.alert_router import AlertRouter


class TestAlertRouterInstantiation:
    def test_creates_with_defaults(self):
        router = AlertRouter()
        assert router is not None


class TestRoute:
    def test_critical_severity_routes_to_pagerduty(self):
        router = AlertRouter()
        assert router.route(9) == "PAGERDUTY"

    def test_high_severity_routes_to_slack(self):
        router = AlertRouter()
        assert router.route(5) == "SLACK"
        assert router.route(7) == "SLACK"

    def test_low_severity_routes_to_email(self):
        router = AlertRouter()
        assert router.route(1) == "EMAIL"
        assert router.route(4) == "EMAIL"

    def test_boundary_severity_eight(self):
        router = AlertRouter()
        assert router.route(8) == "PAGERDUTY"

    def test_boundary_severity_zero(self):
        router = AlertRouter()
        assert router.route(0) == "EMAIL"

    def test_boundary_negative_severity(self):
        router = AlertRouter()
        assert router.route(-1) == "EMAIL"
