# [A_test] module_id: SRC-TST-1330 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_online_feature_importance
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.online_feature_importance
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_online_feature_importance.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.online_feature_importance import OnlineFeatureImportance


class TestOnlineFeatureImportanceInstantiation:
    def test_default_instantiation(self):
        obj = OnlineFeatureImportance()
        assert obj is not None
        assert obj.scores == {}

    def test_custom_scores(self):
        obj = OnlineFeatureImportance(scores={"feat_a": 0.7})
        assert obj.scores["feat_a"] == pytest.approx(0.7)

    def test_is_dataclass(self):
        obj = OnlineFeatureImportance()
        assert hasattr(obj, "__dataclass_fields__")


class TestOnlineFeatureImportanceUpdate:
    def test_update_new_feature(self):
        ofi = OnlineFeatureImportance()
        ofi.update(feature="cpu_usage", importance=0.85)
        assert ofi.scores["cpu_usage"] == pytest.approx(0.85)

    def test_update_multiple_features(self):
        ofi = OnlineFeatureImportance()
        ofi.update(feature="cpu_usage", importance=0.8)
        ofi.update(feature="memory", importance=0.6)
        assert len(ofi.scores) == 2

    def test_update_overwrites_existing(self):
        ofi = OnlineFeatureImportance()
        ofi.update(feature="cpu_usage", importance=0.5)
        ofi.update(feature="cpu_usage", importance=0.9)
        assert ofi.scores["cpu_usage"] == pytest.approx(0.9)

    def test_update_returns_none(self):
        ofi = OnlineFeatureImportance()
        result = ofi.update(feature="f1", importance=0.5)
        assert result is None


class TestOnlineFeatureImportanceBoundaries:
    def test_zero_importance(self):
        ofi = OnlineFeatureImportance()
        ofi.update(feature="unused", importance=0.0)
        assert ofi.scores["unused"] == pytest.approx(0.0)

    def test_negative_importance(self):
        ofi = OnlineFeatureImportance()
        ofi.update(feature="harmful", importance=-0.3)
        assert ofi.scores["harmful"] == pytest.approx(-0.3)

    def test_importance_above_one(self):
        ofi = OnlineFeatureImportance()
        ofi.update(feature="dominant", importance=5.0)
        assert ofi.scores["dominant"] == pytest.approx(5.0)

    def test_empty_feature_name(self):
        ofi = OnlineFeatureImportance()
        ofi.update(feature="", importance=0.5)
        assert "" in ofi.scores

    def test_many_features(self):
        ofi = OnlineFeatureImportance()
        for i in range(200):
            ofi.update(feature=f"feat_{i}", importance=float(i) / 200)
        assert len(ofi.scores) == 200
