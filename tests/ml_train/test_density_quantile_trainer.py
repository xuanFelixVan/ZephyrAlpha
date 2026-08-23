# [BLUEPRINT] ML-DENSITY-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-ML_test_density_quantile_trainer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_density_quantile_trainer
# [TESTS] src/zephyr/ml_train/implementations/density_quantile_trainer.py
# [TTL] task_bound
"""GAP-F-34 密度预测主路线 MVP（ML-DENSITY-001 轻量密度头）toy 断言。

合成小数据（异方差噪声）跑通 训练→评估→晋升片段→分位数序列输出 全链；
禁真训练大模型、禁实盘生效（B-009）。
"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.ml_train.implementations.density_quantile_trainer import (
    DensityQuantileConfig,
    DensityQuantileTrainer,
    DensityTrainError,
)


def _toy_dataset(n: int = 240, seed: int = 7) -> tuple[np.ndarray, np.ndarray]:
    """y = 2*x0 - x1 + 异方差噪声（|x0| 越大噪声越大）。"""
    rng = np.random.default_rng(seed)
    x = rng.normal(size=(n, 3))
    noise = rng.normal(size=n) * (0.1 + np.abs(x[:, 0]))
    y = 2.0 * x[:, 0] - x[:, 1] + noise
    return x, y


class TestTrainValidateFlow:
    def test_train_returns_pinball_metrics(self):
        x, y = _toy_dataset()
        trainer = DensityQuantileTrainer()
        metrics = trainer.train({"X": x, "feature_names": ["a", "b", "c"]}, y, idempotency_key="t-1")
        assert metrics["train_pinball_mean"] >= 0.0
        assert metrics["n_train"] == float(len(y))

    def test_validate_coverage_and_pinball(self):
        x, y = _toy_dataset()
        trainer = DensityQuantileTrainer()
        trainer.train({"X": x}, y, idempotency_key="t-2")
        out = trainer.validate({"X": x}, y)
        assert 0.0 <= out["coverage_10_90"] <= 1.0
        assert out["coverage_10_90"] > 0.3  # toy 数据下应有基本覆盖
        assert out["pinball_mean"] >= 0.0
        assert out["n"] == float(len(y))

    def test_train_too_few_samples_raises(self):
        x, y = _toy_dataset(n=10)
        trainer = DensityQuantileTrainer(DensityQuantileConfig(min_train_samples=30))
        with pytest.raises(DensityTrainError, match="样本不足"):
            trainer.train({"X": x}, y, idempotency_key="t-3")

    def test_train_missing_x_raises(self):
        trainer = DensityQuantileTrainer()
        with pytest.raises(DensityTrainError, match="features"):
            trainer.train({}, np.zeros(50), idempotency_key="t-4")


class TestQuantileSeriesInterface:
    """供 GAP-F-01 情景概率分布消费的分位数序列接口。"""

    def test_predict_quantiles_shape_and_keys(self):
        x, y = _toy_dataset()
        trainer = DensityQuantileTrainer()
        trainer.train({"X": x}, y, idempotency_key="t-5")
        qs = trainer.predict_quantiles(x[:5])
        assert set(qs.keys()) == {0.1, 0.25, 0.5, 0.75, 0.9}
        for arr in qs.values():
            assert arr.shape == (5,)

    def test_predict_quantiles_monotonic(self):
        """分位数序列单调不交叉（q10 <= q25 <= q50 <= q75 <= q90）。"""
        x, y = _toy_dataset()
        trainer = DensityQuantileTrainer()
        trainer.train({"X": x}, y, idempotency_key="t-6")
        qs = trainer.predict_quantiles(x[:50])
        ordered = [qs[q] for q in sorted(qs)]
        for lower, upper in zip(ordered, ordered[1:]):
            assert np.all(lower <= upper + 1e-9)

    def test_predict_before_train_raises(self):
        trainer = DensityQuantileTrainer()
        with pytest.raises(DensityTrainError, match="未训练"):
            trainer.predict_quantiles(np.zeros((3, 3)))


class TestRegistryPromotionStub:
    def test_build_registry_entry_is_candidate_draft(self):
        x, y = _toy_dataset()
        trainer = DensityQuantileTrainer()
        trainer.train({"X": x}, y, idempotency_key="t-7")
        entry = trainer.build_registry_entry(metrics={"pinball_mean": 0.5})
        assert entry["model_id"] == "ML-DENSITY-001"
        assert entry["promotion_stage"] == "candidate"  # 晋升桩：永不直改注册表，草稿恒 candidate
        assert entry["model_type"] == "density_prediction"
        assert entry["code_path"].endswith("density_quantile_trainer.py")

    def test_build_registry_entry_before_train_raises(self):
        trainer = DensityQuantileTrainer()
        with pytest.raises(DensityTrainError, match="未训练"):
            trainer.build_registry_entry(metrics={})
