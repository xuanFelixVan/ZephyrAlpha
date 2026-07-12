# [A_test] module_id: SRC-TST-1012 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_fle_chaos_engineering
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_fle_chaos_engineering.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.detectors.chaos_engineering import ChaosEngineering


class TestChaosEngineeringInstantiation:
    def test_default_construction(self):
        ce = ChaosEngineering()
        assert ce.experiments == []

    def test_with_initial_experiments(self):
        ce = ChaosEngineering(experiments=[{"name": "kill_db"}])
        assert len(ce.experiments) == 1


class TestInject:
    def test_inject_single_experiment(self):
        ce = ChaosEngineering()
        ce.inject({"name": "kill_db", "target": "postgres"})
        assert len(ce.experiments) == 1
        assert ce.experiments[0]["name"] == "kill_db"

    def test_inject_multiple_experiments(self):
        ce = ChaosEngineering()
        ce.inject({"name": "kill_db"})
        ce.inject({"name": "cpu_stress"})
        assert len(ce.experiments) == 2

    def test_inject_empty_dict(self):
        ce = ChaosEngineering()
        ce.inject({})
        assert len(ce.experiments) == 1
        assert ce.experiments[0] == {}

    def test_inject_preserves_order(self):
        ce = ChaosEngineering()
        ce.inject({"name": "first"})
        ce.inject({"name": "second"})
        ce.inject({"name": "third"})
        assert [e["name"] for e in ce.experiments] == ["first", "second", "third"]

    def test_inject_with_nested_data(self):
        ce = ChaosEngineering()
        ce.inject({"name": "network_partition", "config": {"duration": 60, "targets": ["a", "b"]}})
        assert ce.experiments[0]["config"]["duration"] == 60

    def test_independent_instances(self):
        a = ChaosEngineering()
        b = ChaosEngineering()
        a.inject({"name": "test"})
        assert b.experiments == []
