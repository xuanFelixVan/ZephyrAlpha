# [BLUEPRINT] MOD-ML-010 | docs/03_modules/_domain_machine_learning_train/qnn_two_stage/blueprint.md | §4.5.1-A2
# [TTL] permanent
# [A_test] module_id: MOD-ML-010 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_qnn_two_stage
# [TESTS] src/zephyr/ml_train/implementations/qnn_two_stage.py
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""TwoStageQnn (MOD-ML-010) 测试套件。

覆盖: 两阶段训练链/缩放头拟合与degraded回退/retrain_stage2冻结Stage1/分位数单调性/validate指标/晋升草稿恒candidate/输入校验。
"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.ml_train.implementations.qnn_two_stage import (
    TwoStageQnn,
    TwoStageQnnConfig,
    TwoStageQnnError,
)


def _toy_dataset(n: int = 200, seed: int = 7) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """y = 2*x0 - x1 + 噪声; 2 symbols。"""
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n, 3))
    noise = rng.normal(size=n) * 0.1
    y = 2.0 * x[:, 0] - x[:, 1] + noise
    symbol_ids = np.array(["A"] * (n // 2) + ["B"] * (n - n // 2))
    return x, y, symbol_ids


# ── 两阶段训练链 ─────────────────────────────────────────────────────────────


class TestTwoStageTrain:
    def test_train_returns_metrics(self):
        x, y, sym = _toy_dataset()
        qnn = TwoStageQnn()
        metrics = qnn.train({"X": x, "symbol_ids": sym}, y, idempotency_key="t-1")
        assert metrics["train_pinball_mean"] >= 0.0
        assert metrics["n_train"] == float(len(y))
        assert metrics["n_symbols"] == 2.0

    def test_stage1_frozen_after_train(self):
        x, y, sym = _toy_dataset()
        qnn = TwoStageQnn()
        qnn.train({"X": x, "symbol_ids": sym}, y, idempotency_key="t-2")
        stage1_before = qnn._stage1_models[0.5]
        qnn.retrain_stage2({"X": x, "symbol_ids": sym}, y)
        assert qnn._stage1_models[0.5] is stage1_before  # Stage1 未变

    def test_predict_quantiles_monotone(self):
        x, y, sym = _toy_dataset()
        qnn = TwoStageQnn()
        qnn.train({"X": x, "symbol_ids": sym}, y, idempotency_key="t-3")
        qs = qnn.predict_quantiles(x, sym)
        sorted_qs = sorted(qs)
        for i in range(len(sorted_qs) - 1):
            lower = qs[sorted_qs[i]]
            upper = qs[sorted_qs[i + 1]]
            assert np.all(lower <= upper + 1e-9)


# ── Stage2 缩放头 ────────────────────────────────────────────────────────────


class TestStage2Scaling:
    def test_degraded_when_few_symbol_samples(self):
        rng = np.random.default_rng(7)
        x = rng.normal(size=(40, 3))
        y = 2.0 * x[:, 0] - x[:, 1] + rng.normal(size=40) * 0.1
        sym = np.array(["A"] * 35 + ["B"] * 5)  # B 只有 5 样本 < min_symbol_samples=20
        cfg = TwoStageQnnConfig(min_symbol_samples=20)
        qnn = TwoStageQnn(cfg)
        qnn.train({"X": x, "symbol_ids": sym}, y, idempotency_key="t-4")
        a, b = qnn._symbol_scaling["B"]
        assert (a, b) == (1.0, 0.0)  # degraded

    def test_scaling_fitted_when_enough_samples(self):
        x, y, sym = _toy_dataset(n=200)
        cfg = TwoStageQnnConfig(min_symbol_samples=20)
        qnn = TwoStageQnn(cfg)
        qnn.train({"X": x, "symbol_ids": sym}, y, idempotency_key="t-5")
        a_a, b_a = qnn._symbol_scaling["A"]
        a_b, b_b = qnn._symbol_scaling["B"]
        # 两 symbol 均应有拟合值 (非 degraded 1,0)
        assert (a_a, b_a) != (1.0, 0.0)
        assert (a_b, b_b) != (1.0, 0.0)


# ── validate ────────────────────────────────────────────────────────────────


class TestValidate:
    def test_validate_metrics(self):
        x, y, sym = _toy_dataset()
        qnn = TwoStageQnn()
        qnn.train({"X": x, "symbol_ids": sym}, y, idempotency_key="t-6")
        out = qnn.validate({"X": x, "symbol_ids": sym}, y)
        assert 0.0 <= out["coverage_10_90"] <= 1.0
        assert out["coverage_10_90"] > 0.3
        assert out["pinball_mean"] >= 0.0


# ── 晋升草稿 ─────────────────────────────────────────────────────────────────


class TestRegistryEntry:
    def test_candidate_draft(self):
        x, y, sym = _toy_dataset()
        qnn = TwoStageQnn()
        metrics = qnn.train({"X": x, "symbol_ids": sym}, y, idempotency_key="t-7")
        entry = qnn.build_registry_entry(metrics)
        assert entry["promotion_stage"] == "candidate"
        assert entry["status"] == "candidate"
        assert entry["serving_mode"] == "none"
        assert entry["model_id"] == "ML-QNN2S-001"


# ── 输入校验 ─────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_missing_x(self):
        qnn = TwoStageQnn()
        with pytest.raises(TwoStageQnnError, match="X.*缺失"):
            qnn.train({"symbol_ids": np.array(["A"])}, np.array([1.0]), idempotency_key="t-8")

    def test_missing_symbol_ids(self):
        qnn = TwoStageQnn()
        with pytest.raises(TwoStageQnnError, match="symbol_ids.*缺失"):
            qnn.train({"X": np.array([[1.0]])}, np.array([1.0]), idempotency_key="t-9")

    def test_mismatched_lengths(self):
        qnn = TwoStageQnn()
        with pytest.raises(TwoStageQnnError, match="长度不齐"):
            qnn.train({"X": np.array([[1.0]]), "symbol_ids": np.array(["A", "B"])}, np.array([1.0]), idempotency_key="t-10")

    def test_predict_before_train(self):
        qnn = TwoStageQnn()
        with pytest.raises(TwoStageQnnError, match="模型未训练"):
            qnn.predict_quantiles(np.array([[1.0]]), np.array(["A"]))
