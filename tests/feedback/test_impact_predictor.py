# [A_test] module_id: SRC-TST-1109 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_impact_predictor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.diagnosis.impact_predictor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_impact_predictor.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.diagnosis.impact_predictor import ImpactPredictor


class TestImpactPredictorInstantiation:
    def test_default_instantiation(self):
        pred = ImpactPredictor()
        assert pred is not None

    def test_is_dataclass(self):
        pred = ImpactPredictor()
        assert hasattr(pred, "__dataclass_fields__")


class TestPredict:
    def test_predict_empty_scope(self):
        pred = ImpactPredictor()
        result = pred.predict("restart_service", [])
        assert result == {}

    def test_predict_single_scope(self):
        pred = ImpactPredictor()
        result = pred.predict("restart_service", ["db"])
        assert "db" in result
        assert isinstance(result["db"], float)

    def test_predict_multiple_scopes(self):
        pred = ImpactPredictor()
        result = pred.predict("restart_service", ["db", "cache", "queue"])
        assert len(result) == 3
        assert "db" in result
        assert "cache" in result
        assert "queue" in result

    def test_predict_returns_zero_by_default(self):
        pred = ImpactPredictor()
        result = pred.predict("any_action", ["scope_a", "scope_b"])
        for scope, impact in result.items():
            assert impact == 0.0

    def test_predict_scope_keys_match_input(self):
        pred = ImpactPredictor()
        scopes = ["alpha", "beta", "gamma"]
        result = pred.predict("action", scopes)
        assert set(result.keys()) == set(scopes)

    def test_predict_empty_action(self):
        pred = ImpactPredictor()
        result = pred.predict("", ["scope1"])
        assert "scope1" in result

    def test_predict_values_are_float(self):
        pred = ImpactPredictor()
        result = pred.predict("action", ["s1", "s2"])
        for v in result.values():
            assert isinstance(v, float)
