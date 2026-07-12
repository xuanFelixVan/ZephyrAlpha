# [A_test] module_id: SRC-TST-1713 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_synthetic_anomaly_generator
# [INVARIANTS] generate returns list[dict] with length=count; each dict has pattern and id
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_synthetic_anomaly_generator.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.synthetic_anomaly_generator import (
    SyntheticAnomalyGenerator,
)


class TestSyntheticAnomalyGeneratorInstantiation:
    def test_instantiation(self):
        obj = SyntheticAnomalyGenerator()
        assert obj is not None


class TestSyntheticAnomalyGeneratorGenerate:
    def test_generate_returns_list(self):
        obj = SyntheticAnomalyGenerator()
        result = obj.generate("spike", 3)
        assert isinstance(result, list)

    def test_generate_correct_count(self):
        obj = SyntheticAnomalyGenerator()
        result = obj.generate("spike", 5)
        assert len(result) == 5

    def test_generate_zero_count(self):
        obj = SyntheticAnomalyGenerator()
        result = obj.generate("spike", 0)
        assert result == []

    def test_generate_each_item_has_pattern(self):
        obj = SyntheticAnomalyGenerator()
        result = obj.generate("drift", 3)
        for item in result:
            assert item["pattern"] == "drift"

    def test_generate_each_item_has_id(self):
        obj = SyntheticAnomalyGenerator()
        result = obj.generate("noise", 4)
        ids = [item["id"] for item in result]
        assert ids == [0, 1, 2, 3]

    def test_generate_large_count(self):
        obj = SyntheticAnomalyGenerator()
        result = obj.generate("burst", 100)
        assert len(result) == 100

    def test_generate_empty_pattern(self):
        obj = SyntheticAnomalyGenerator()
        result = obj.generate("", 2)
        assert len(result) == 2
        assert result[0]["pattern"] == ""

    def test_generate_ids_sequential(self):
        obj = SyntheticAnomalyGenerator()
        result = obj.generate("test", 3)
        assert result[0]["id"] == 0
        assert result[1]["id"] == 1
        assert result[2]["id"] == 2
