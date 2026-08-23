# [BLUEPRINT] MOD-ML-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-ML_test_gap_f35_skeletons | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_gap_f35_candidate_skeletons
# [TESTS] src/zephyr/ml_train/implementations/limit_up_classifier.py; src/zephyr/ml_train/implementations/seat_pattern_classifier.py; src/zephyr/ml_train/services/sentiment_sft_entry.py
# [TTL] task_bound
"""GAP-F-35 ML 外围三候选骨架 toy 断言（禁真训练——只验管线骨架+数据接口位）。

三候选：舆情情感 SFT 训练入口桩（ML-SFT-001）/ 打板涨停分类器（ML-CLS-001）/
席位形态分类器（ML-CLS-002）。骨架语义：数据接口校验可用、train() 一律抛
CandidateTrainDisabledError（ZA-MLT-0003），真训练待 Owner 批准（B-007）。
"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.ml_train.implementations.limit_up_classifier import (
    LIMIT_UP_FEATURES,
    LimitUpClassifierSkeleton,
)
from zephyr.ml_train.implementations.seat_pattern_classifier import (
    SEAT_FEATURES,
    SeatPatternClassifierSkeleton,
)
from zephyr.ml_train.services.sentiment_sft_entry import (
    CandidateTrainDisabledError,
    SFTEntryConfig,
    run_sentiment_sft_training_entry,
)


class TestLimitUpClassifierSkeleton:
    def test_feature_schema_declared(self):
        assert "seal_ratio" in LIMIT_UP_FEATURES
        assert "first_seal_minutes" in LIMIT_UP_FEATURES

    def test_validate_features_ok(self):
        skel = LimitUpClassifierSkeleton()
        x = {name: np.zeros(10) for name in LIMIT_UP_FEATURES}
        assert skel.check_feature_interface({"X": x}) is True

    def test_validate_features_missing_raises(self):
        skel = LimitUpClassifierSkeleton()
        with pytest.raises(ValueError, match="seal_ratio"):
            skel.check_feature_interface({"X": {"other": np.zeros(5)}})

    def test_train_disabled(self):
        skel = LimitUpClassifierSkeleton()
        x = {name: np.zeros(10) for name in LIMIT_UP_FEATURES}
        with pytest.raises(CandidateTrainDisabledError) as exc:
            skel.train({"X": x}, np.zeros(10), idempotency_key="k")
        assert exc.value.error_code == "ZA-MLT-0003"


class TestSeatPatternClassifierSkeleton:
    def test_feature_schema_declared(self):
        assert "seat_net_buy_ratio" in SEAT_FEATURES
        assert "top_seat_count" in SEAT_FEATURES

    def test_validate_features_ok(self):
        skel = SeatPatternClassifierSkeleton()
        x = {name: np.zeros(8) for name in SEAT_FEATURES}
        assert skel.check_feature_interface({"X": x}) is True

    def test_train_disabled(self):
        skel = SeatPatternClassifierSkeleton()
        x = {name: np.zeros(8) for name in SEAT_FEATURES}
        with pytest.raises(CandidateTrainDisabledError) as exc:
            skel.train({"X": x}, np.zeros(8), idempotency_key="k")
        assert exc.value.error_code == "ZA-MLT-0003"


class TestSentimentSFTEntry:
    def test_entry_dry_run_returns_plan(self):
        samples = [{"title": "t", "content": "c", "sentiment": "positive", "score": 0.8}]
        plan = run_sentiment_sft_training_entry(samples, config=SFTEntryConfig(dry_run=True))
        assert plan["status"] == "dry_run"
        assert plan["n_samples"] == 1
        assert plan["model_id"] == "ML-SFT-001"

    def test_entry_rejects_empty_samples(self):
        with pytest.raises(ValueError, match="samples"):
            run_sentiment_sft_training_entry([], config=SFTEntryConfig(dry_run=True))

    def test_entry_real_train_disabled(self):
        """禁真训练：dry_run=False 走真训练必须抛 ZA-MLT-0003（B-007 人工闸门）。"""
        samples = [{"title": "t", "content": "c", "sentiment": "neutral", "score": 0.5}]
        with pytest.raises(CandidateTrainDisabledError) as exc:
            run_sentiment_sft_training_entry(samples, config=SFTEntryConfig(dry_run=False))
        assert exc.value.error_code == "ZA-MLT-0003"
