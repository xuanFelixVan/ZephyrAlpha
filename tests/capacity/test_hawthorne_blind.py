# [A_test] module_id: SRC-TST-1091 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_hawthorne_blind
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_hawthorne_blind.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip("zephyr.ops.capacity_assurance.hawthorne_blind", reason="hawthorne_blind not available")
HawthorneBlind = mod.HawthorneBlind


class TestHawthorneBlind:
    def test_instantiation(self):
        hb = HawthorneBlind()
        assert len(hb._visible_rules) == 0

    def test_add_rule(self):
        hb = HawthorneBlind()
        hb.add_rule("cpu_usage", "visible")
        hb.add_rule("memory_usage", "hidden")
        assert hb._visible_rules["cpu_usage"] == "visible"
        assert hb._visible_rules["memory_usage"] == "hidden"

    def test_filter_visible(self):
        hb = HawthorneBlind()
        hb.add_rule("cpu_usage", "visible")
        result = hb.filter_for_ai({"cpu_usage": 85.5, "memory_usage": 70.0})
        assert result == {"cpu_usage": 85.5}

    def test_filter_aggregated(self):
        hb = HawthorneBlind()
        hb.add_rule("latency", "aggregated")
        result = hb.filter_for_ai({"latency": 150})
        assert "agg_latency" in result
        assert result["agg_latency"] == "NORMAL"

    def test_filter_hidden(self):
        hb = HawthorneBlind()
        hb.add_rule("secret_key", "hidden")
        result = hb.filter_for_ai({"secret_key": "abc123"})
        assert "secret_key" not in result

    def test_filter_default_hidden(self):
        hb = HawthorneBlind()
        result = hb.filter_for_ai({"unknown_metric": 42})
        assert "unknown_metric" not in result

    def test_filter_empty_metrics(self):
        hb = HawthorneBlind()
        result = hb.filter_for_ai({})
        assert result == {}

    def test_filter_aggregated_non_numeric(self):
        hb = HawthorneBlind()
        hb.add_rule("status", "aggregated")
        result = hb.filter_for_ai({"status": "running"})
        assert result["agg_status"] == "running"
