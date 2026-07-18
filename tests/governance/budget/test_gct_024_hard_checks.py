# [A_test] module_id: SRC-TST-0132 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-289 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.governance.test_gct_024_hard_checks
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from pathlib import Path

import yaml

from zephyr.governance.ops_governance.budget_engine import BudgetEngine


class TestGCT024HardChecks:
    """GCT-024 硬检查：验证 BudgetEngine 实例化、三维覆盖、策略文件存在"""

    def test_budget_engine_pre_flight_self_test(self):
        be = BudgetEngine()
        r = be.pre_flight_check("gct024-check", 1000, 0.1)
        assert r.decision.name == "ALLOW"

    def test_three_dimension_coverage(self):
        be = BudgetEngine()
        assert len(be._policies) == 3

    def test_policy_file_exists_and_parsable(self):
        policy_path = Path("config/budget_policy.yaml")
        assert policy_path.exists(), f"Missing: {policy_path}"
        with open(policy_path, encoding="utf-8") as f:
            p = yaml.safe_load(f)
        assert p["budget_levels"]["session_level"]["hard_limit"] == 12000

    def test_escalation_bridge_importable(self):
        from zephyr.governance.bridges.alerts import BudgetAlert
        from zephyr.governance.ops_governance.budget_handler import on_budget_alert

        a = BudgetAlert(alert_id="B001")
        r = on_budget_alert(a)
        assert r is not None

    def test_rbac_bridge_importable(self):
        from zephyr.governance.agent_spec.rbac_bridge import BudgetRBACBridge

        b = BudgetRBACBridge()
        r = b.check_budget("a1", 500, 1000)
        assert r["action"] == "ALLOW"

    def test_burn_rate_monitor_normal(self):
        from zephyr.governance.financial_governance.budget_enforcement import BurnRateMonitor

        bm = BurnRateMonitor()
        bm.record_consumption(100)
        bm.compute_burn_rates(1_000_000)
        assert bm.get_severity().name == "NORMAL"
