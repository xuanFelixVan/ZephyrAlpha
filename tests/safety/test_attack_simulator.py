# [A_test] module_id: SRC-TST-0341 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_attack_simulator
# [INVARIANTS] scenarios is list[dict]
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_attack_simulator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.verifiers.attack_simulator import AttackSimulator


class TestAttackSimulatorInstantiation:
    def test_default_construction(self):
        asim = AttackSimulator()
        assert asim.scenarios == []

    def test_custom_scenarios(self):
        scenarios = [{"name": "metric_injection", "severity": "high"}]
        asim = AttackSimulator(scenarios=scenarios)
        assert len(asim.scenarios) == 1
        assert asim.scenarios[0]["name"] == "metric_injection"


class TestScenariosAttribute:
    def test_add_scenario(self):
        asim = AttackSimulator()
        asim.scenarios.append({"name": "s1", "type": "injection"})
        assert len(asim.scenarios) == 1

    def test_multiple_scenarios(self):
        scenarios = [{"name": f"attack-{i}"} for i in range(5)]
        asim = AttackSimulator(scenarios=scenarios)
        assert len(asim.scenarios) == 5

    def test_empty_scenario_dict(self):
        asim = AttackSimulator(scenarios=[{}])
        assert len(asim.scenarios) == 1

    def test_scenarios_mutable_default(self):
        asim1 = AttackSimulator()
        asim2 = AttackSimulator()
        asim1.scenarios.append({"name": "x"})
        assert len(asim2.scenarios) == 0
