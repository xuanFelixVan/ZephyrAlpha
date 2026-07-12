# [A_test] module_id: SRC-TST-1496 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_rule_shadow_runner
# [INVARIANTS] 影子模式统计必须准确;假阳性率必须<10%
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_rule_shadow_runner.py
# [TTL] task_bound

import time

from zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_shadow_runner import RuleShadowRunner


class TestRuleShadowRunnerInit:
    def test_instantiation(self):
        rsr = RuleShadowRunner()
        assert rsr._shadow_rules == {}


class TestDeployShadow:
    def test_deploy_single_rule(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        assert "RULE-001" in rsr._shadow_rules
        assert rsr._shadow_rules["RULE-001"]["rule"] == {"action": "block"}

    def test_deploy_with_default_shadow_days(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        assert rsr._shadow_rules["RULE-001"]["shadow_days"] == 3

    def test_deploy_with_custom_shadow_days(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"}, shadow_days=7)
        assert rsr._shadow_rules["RULE-001"]["shadow_days"] == 7

    def test_deploy_records_timestamp(self):
        rsr = RuleShadowRunner()
        before = time.time()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        after = time.time()
        assert before <= rsr._shadow_rules["RULE-001"]["deployed_at"] <= after

    def test_deploy_initializes_empty_decisions(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        assert rsr._shadow_rules["RULE-001"]["decisions"] == []

    def test_deploy_multiple_rules(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        rsr.deploy_shadow("RULE-002", {"action": "warn"})
        assert len(rsr._shadow_rules) == 2

    def test_redeploy_overwrites(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        rsr.deploy_shadow("RULE-001", {"action": "warn"})
        assert rsr._shadow_rules["RULE-001"]["rule"] == {"action": "warn"}
        assert rsr._shadow_rules["RULE-001"]["decisions"] == []


class TestRecordShadowDecision:
    def test_record_single_decision(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        rsr.record_shadow_decision("RULE-001", "op_a", "low", "high")
        assert len(rsr._shadow_rules["RULE-001"]["decisions"]) == 1
        assert rsr._shadow_rules["RULE-001"]["decisions"][0] == {"op": "op_a", "old": "low", "new": "high"}

    def test_record_multiple_decisions(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        rsr.record_shadow_decision("RULE-001", "op_a", "low", "high")
        rsr.record_shadow_decision("RULE-001", "op_b", "low", "low")
        assert len(rsr._shadow_rules["RULE-001"]["decisions"]) == 2

    def test_record_for_undeployed_rule_ignored(self):
        rsr = RuleShadowRunner()
        rsr.record_shadow_decision("RULE-999", "op_a", "low", "high")
        assert "RULE-999" not in rsr._shadow_rules


class TestDiff:
    def test_diff_no_changes(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        rsr.record_shadow_decision("RULE-001", "op_a", "low", "low")
        result = rsr.diff("RULE-001")
        assert result["total"] == 1
        assert result["changes"] == 0

    def test_diff_with_changes(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        rsr.record_shadow_decision("RULE-001", "op_a", "low", "high")
        result = rsr.diff("RULE-001")
        assert result["total"] == 1
        assert result["changes"] == 1

    def test_diff_mixed_decisions(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        rsr.record_shadow_decision("RULE-001", "op_a", "low", "high")
        rsr.record_shadow_decision("RULE-001", "op_b", "low", "low")
        rsr.record_shadow_decision("RULE-001", "op_c", "med", "high")
        result = rsr.diff("RULE-001")
        assert result["total"] == 3
        assert result["changes"] == 2

    def test_diff_no_decisions(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        result = rsr.diff("RULE-001")
        assert result["total"] == 0
        assert result["changes"] == 0

    def test_diff_unknown_rule(self):
        rsr = RuleShadowRunner()
        result = rsr.diff("RULE-999")
        assert result == {}

    def test_diff_includes_rule_id(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        result = rsr.diff("RULE-001")
        assert result["rule_id"] == "RULE-001"


class TestPromote:
    def test_promote_existing_rule(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        assert rsr.promote("RULE-001") is True

    def test_promote_nonexistent_rule(self):
        rsr = RuleShadowRunner()
        assert rsr.promote("RULE-999") is False

    def test_promote_after_record(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"})
        rsr.record_shadow_decision("RULE-001", "op_a", "low", "high")
        assert rsr.promote("RULE-001") is True


class TestBoundary:
    def test_empty_rule_def(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {})
        assert rsr._shadow_rules["RULE-001"]["rule"] == {}

    def test_complex_rule_def(self):
        rsr = RuleShadowRunner()
        rule_def = {"action": "block", "conditions": [{"field": "amount", "op": ">", "value": 1000}]}
        rsr.deploy_shadow("RULE-001", rule_def)
        assert rsr._shadow_rules["RULE-001"]["rule"]["conditions"][0]["value"] == 1000

    def test_zero_shadow_days(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("RULE-001", {"action": "block"}, shadow_days=0)
        assert rsr._shadow_rules["RULE-001"]["shadow_days"] == 0

    def test_unicode_rule_id(self):
        rsr = RuleShadowRunner()
        rsr.deploy_shadow("规则-001", {"action": "block"})
        assert rsr.promote("规则-001") is True
