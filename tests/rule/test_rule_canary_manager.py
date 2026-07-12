# [A_test] module_id: SRC-TST-1493 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rule_canary_manager
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_rule_canary_manager.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_canary_manager import RuleCanaryManager


class TestRuleCanaryManagerInit:
    def test_default_canary_weight(self):
        mgr = RuleCanaryManager()
        assert mgr._canary_weight == 0.01

    def test_default_baseline_metrics_empty(self):
        mgr = RuleCanaryManager()
        assert mgr._baseline_metrics == {}

    def test_default_canary_metrics_empty(self):
        mgr = RuleCanaryManager()
        assert mgr._canary_metrics == {}


class TestSetBaseline:
    def test_sets_baseline_metrics(self):
        mgr = RuleCanaryManager()
        mgr.set_baseline({"false_positive_rate": 0.05, "accuracy": 0.95})
        assert mgr._baseline_metrics["false_positive_rate"] == 0.05
        assert mgr._baseline_metrics["accuracy"] == 0.95

    def test_overwrites_previous_baseline(self):
        mgr = RuleCanaryManager()
        mgr.set_baseline({"false_positive_rate": 0.05})
        mgr.set_baseline({"false_positive_rate": 0.03})
        assert mgr._baseline_metrics["false_positive_rate"] == 0.03


class TestSetCanaryMetrics:
    def test_sets_canary_metrics(self):
        mgr = RuleCanaryManager()
        mgr.set_canary_metrics({"false_positive_rate": 0.10, "latency_ms": 200})
        assert mgr._canary_metrics["false_positive_rate"] == 0.10
        assert mgr._canary_metrics["latency_ms"] == 200

    def test_overwrites_previous_canary_metrics(self):
        mgr = RuleCanaryManager()
        mgr.set_canary_metrics({"false_positive_rate": 0.10})
        mgr.set_canary_metrics({"false_positive_rate": 0.02})
        assert mgr._canary_metrics["false_positive_rate"] == 0.02


class TestShouldRollback:
    def test_no_rollback_when_canary_better(self):
        mgr = RuleCanaryManager()
        mgr.set_baseline({"false_positive_rate": 0.10})
        mgr.set_canary_metrics({"false_positive_rate": 0.05})
        assert mgr.should_rollback() is False

    def test_no_rollback_when_canary_slightly_worse(self):
        mgr = RuleCanaryManager()
        mgr.set_baseline({"false_positive_rate": 0.10})
        mgr.set_canary_metrics({"false_positive_rate": 0.19})
        assert mgr.should_rollback() is False

    def test_rollback_when_canary_double_baseline(self):
        mgr = RuleCanaryManager()
        mgr.set_baseline({"false_positive_rate": 0.10})
        mgr.set_canary_metrics({"false_positive_rate": 0.21})
        assert mgr.should_rollback() is True

    def test_rollback_at_exact_2x_boundary(self):
        mgr = RuleCanaryManager()
        mgr.set_baseline({"false_positive_rate": 0.10})
        mgr.set_canary_metrics({"false_positive_rate": 0.20})
        assert mgr.should_rollback() is False

    def test_no_rollback_when_no_metrics_set(self):
        mgr = RuleCanaryManager()
        assert mgr.should_rollback() is False

    def test_no_rollback_when_only_baseline_set(self):
        mgr = RuleCanaryManager()
        mgr.set_baseline({"false_positive_rate": 0.10})
        assert mgr.should_rollback() is False

    def test_rollback_when_only_canary_set_and_baseline_zero(self):
        mgr = RuleCanaryManager()
        mgr.set_canary_metrics({"false_positive_rate": 0.50})
        assert mgr.should_rollback() is True


class TestPromote:
    def test_promote_sets_weight_to_one(self):
        mgr = RuleCanaryManager()
        assert mgr._canary_weight == 0.01
        mgr.promote()
        assert mgr._canary_weight == 1.0

    def test_promote_idempotent(self):
        mgr = RuleCanaryManager()
        mgr.promote()
        mgr.promote()
        assert mgr._canary_weight == 1.0


class TestRuleCanaryManagerBoundary:
    def test_zero_baseline_false_positive_rate(self):
        mgr = RuleCanaryManager()
        mgr.set_baseline({"false_positive_rate": 0.0})
        mgr.set_canary_metrics({"false_positive_rate": 0.01})
        assert mgr.should_rollback() is True

    def test_very_high_canary_false_positive_rate(self):
        mgr = RuleCanaryManager()
        mgr.set_baseline({"false_positive_rate": 0.01})
        mgr.set_canary_metrics({"false_positive_rate": 0.99})
        assert mgr.should_rollback() is True

    def test_metrics_with_extra_keys_ignored(self):
        mgr = RuleCanaryManager()
        mgr.set_baseline({"false_positive_rate": 0.05, "extra_key": 42})
        mgr.set_canary_metrics({"false_positive_rate": 0.06, "other_key": 99})
        assert mgr.should_rollback() is False
