# [A_test] module_id: SRC-TST-0511 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_chaos_engineering
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.detectors.chaos_engineering
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_chaos_engineering.py
# [TTL] task_bound

from zephyr.feedback_loop.detectors.chaos_engineering import ChaosEngineering


class TestChaosEngineeringInstantiation:
    def test_default_instantiation(self):
        ce = ChaosEngineering()
        assert ce.experiments == []

    def test_custom_experiments(self):
        exps = [{"name": "kill_db", "target": "postgres"}]
        ce = ChaosEngineering(experiments=exps)
        assert len(ce.experiments) == 1
        assert ce.experiments[0]["name"] == "kill_db"

    def test_empty_experiments_list(self):
        ce = ChaosEngineering(experiments=[])
        assert ce.experiments == []


class TestChaosEngineeringInject:
    def test_inject_single_experiment(self):
        ce = ChaosEngineering()
        ce.inject({"name": "latency_spike", "delay_ms": 500})
        assert len(ce.experiments) == 1
        assert ce.experiments[0]["delay_ms"] == 500

    def test_inject_multiple_experiments(self):
        ce = ChaosEngineering()
        ce.inject({"name": "exp_a"})
        ce.inject({"name": "exp_b"})
        ce.inject({"name": "exp_c"})
        assert len(ce.experiments) == 3

    def test_inject_preserves_order(self):
        ce = ChaosEngineering()
        ce.inject({"name": "first"})
        ce.inject({"name": "second"})
        assert ce.experiments[0]["name"] == "first"
        assert ce.experiments[1]["name"] == "second"

    def test_inject_empty_dict(self):
        ce = ChaosEngineering()
        ce.inject({})
        assert len(ce.experiments) == 1
        assert ce.experiments[0] == {}

    def test_inject_complex_experiment(self):
        ce = ChaosEngineering()
        exp = {"name": "network_partition", "targets": ["svc_a", "svc_b"], "duration_s": 60, "probability": 0.1}
        ce.inject(exp)
        assert ce.experiments[0]["targets"] == ["svc_a", "svc_b"]
        assert ce.experiments[0]["probability"] == 0.1

    def test_inject_does_not_overwrite_existing(self):
        ce = ChaosEngineering(experiments=[{"name": "existing"}])
        ce.inject({"name": "new"})
        assert len(ce.experiments) == 2
