# [A_test] module_id: SRC-TST-0874 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_ewc_kb_review
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.ewc_kb_review
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_ewc_kb_review.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.ewc_kb_review import EWCKBReview


class TestEWCKBReviewInstantiation:
    def test_default_instantiation(self):
        obj = EWCKBReview()
        assert obj is not None
        assert obj.importance_weights == {}

    def test_custom_weights(self):
        obj = EWCKBReview(importance_weights={"param_a": 0.8})
        assert obj.importance_weights == {"param_a": 0.8}

    def test_is_dataclass(self):
        obj = EWCKBReview()
        assert hasattr(obj, "__dataclass_fields__")


class TestEWCKBReviewProtect:
    def test_protect_new_param(self):
        ewc = EWCKBReview()
        ewc.protect(param="weight_1", importance=0.9)
        assert ewc.importance_weights["weight_1"] == pytest.approx(0.9)

    def test_protect_multiple_params(self):
        ewc = EWCKBReview()
        ewc.protect(param="w1", importance=0.5)
        ewc.protect(param="w2", importance=0.8)
        assert len(ewc.importance_weights) == 2
        assert ewc.importance_weights["w1"] == pytest.approx(0.5)
        assert ewc.importance_weights["w2"] == pytest.approx(0.8)

    def test_protect_overwrites_existing(self):
        ewc = EWCKBReview()
        ewc.protect(param="w1", importance=0.5)
        ewc.protect(param="w1", importance=0.9)
        assert ewc.importance_weights["w1"] == pytest.approx(0.9)

    def test_protect_returns_none(self):
        ewc = EWCKBReview()
        result = ewc.protect(param="w1", importance=0.5)
        assert result is None


class TestEWCKBReviewBoundaries:
    def test_zero_importance(self):
        ewc = EWCKBReview()
        ewc.protect(param="w_zero", importance=0.0)
        assert ewc.importance_weights["w_zero"] == pytest.approx(0.0)

    def test_negative_importance(self):
        ewc = EWCKBReview()
        ewc.protect(param="w_neg", importance=-0.5)
        assert ewc.importance_weights["w_neg"] == pytest.approx(-0.5)

    def test_very_high_importance(self):
        ewc = EWCKBReview()
        ewc.protect(param="w_high", importance=1000.0)
        assert ewc.importance_weights["w_high"] == pytest.approx(1000.0)

    def test_empty_param_name(self):
        ewc = EWCKBReview()
        ewc.protect(param="", importance=0.5)
        assert "" in ewc.importance_weights
