# [A_test] module_id: SRC-TST-1350 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_output_quality_gate
# [INVARIANTS] evaluate returns QualityVerdict; hard violations block
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_enforcement.rule_enforcement.output_quality_gate import (
    DEFAULT_RULES,
    OutputQualityGate,
    QualityRule,
    QualityVerdict,
)


class TestOutputQualityGate:
    def test_instantiation_defaults(self):
        gate = OutputQualityGate()
        assert len(gate._rules) > 0

    def test_instantiation_custom_rules(self):
        rules = [QualityRule(name="test", check_fn="len>0", threshold=0.5, severity="soft")]
        gate = OutputQualityGate(rules=rules)
        assert len(gate._rules) == 1

    def test_evaluate_good_output(self):
        gate = OutputQualityGate()
        verdict = gate.evaluate(
            output="This is a good quality output with diverse vocabulary and structure.",
            cost=0.001,
        )
        assert isinstance(verdict, QualityVerdict)
        assert verdict.passed is True
        assert verdict.should_block is False

    def test_evaluate_short_output(self):
        gate = OutputQualityGate()
        verdict = gate.evaluate(output="Hi", cost=0.001)
        assert len(verdict.violations) > 0

    def test_evaluate_placeholder_blocks(self):
        gate = OutputQualityGate()
        verdict = gate.evaluate(output="This output has a TODO placeholder in it.", cost=0.001)
        assert verdict.should_block is True
        assert verdict.passed is False

    def test_evaluate_fixme_blocks(self):
        gate = OutputQualityGate()
        verdict = gate.evaluate(output="FIXME: this needs fixing before shipping.", cost=0.001)
        assert verdict.should_block is True

    def test_evaluate_expensive_output(self):
        gate = OutputQualityGate()
        verdict = gate.evaluate(output="Short text", cost=10.0)
        assert len(verdict.violations) > 0

    def test_evaluate_repetitive_output(self):
        gate = OutputQualityGate()
        text = "word " * 100
        verdict = gate.evaluate(output=text, cost=0.001)
        assert verdict.score < 1.0

    def test_add_rule(self):
        gate = OutputQualityGate()
        initial_count = len(gate._rules)
        gate.add_rule(QualityRule(name="custom", check_fn="custom_check", threshold=0.9, severity="soft"))
        assert len(gate._rules) == initial_count + 1

    def test_score_range(self):
        gate = OutputQualityGate()
        verdict = gate.evaluate(output="A reasonable output with some content.", cost=0.001)
        assert 0.0 <= verdict.score <= 1.0

    def test_mismatched_brackets(self):
        gate = OutputQualityGate()
        verdict = gate.evaluate(output="This has { unmatched brackets ( and [.", cost=0.001)
        assert verdict.score < 1.0


class TestQualityRule:
    def test_creation(self):
        rule = QualityRule(name="test", check_fn="len>0", threshold=0.5, severity="soft")
        assert rule.name == "test"
        assert rule.threshold == 0.5

    def test_default_rules_exist(self):
        names = {r.name for r in DEFAULT_RULES}
        assert "min_length" in names
        assert "no_placeholder" in names


class TestBoundaryCases:
    def test_evaluate_empty_string(self):
        gate = OutputQualityGate()
        verdict = gate.evaluate(output="", cost=0.0)
        assert isinstance(verdict, QualityVerdict)
        assert len(verdict.violations) > 0

    def test_evaluate_zero_cost(self):
        gate = OutputQualityGate()
        verdict = gate.evaluate(output="A good output with zero cost.", cost=0.0)
        assert isinstance(verdict, QualityVerdict)

    def test_evaluate_very_long_output(self):
        gate = OutputQualityGate()
        text = "Unique word. " * 1000
        verdict = gate.evaluate(output=text, cost=0.01)
        assert verdict.passed is True
