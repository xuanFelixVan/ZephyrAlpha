# [BLUEPRINT] MOD-ML-004 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-ML_test_gray_release_shadow_deployer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_gray_release_shadow_deployer
# [TESTS] src/zephyr/ml_train/gray_release_shadow_deployer.py
# [TTL] task_bound
"""MOD-ML-004 灰度/影子部署 toy 断言（影子只记录不生效）。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.ml_train.gray_release_shadow_deployer import (
    GrayReleaseShadowDeployer,
    ShadowDeployError,
)


def _preds(n: int = 30) -> np.ndarray:
    return np.random.default_rng(2).normal(size=n)


class TestShadowDeployment:
    def test_deploy_creates_shadow_session(self):
        dep = GrayReleaseShadowDeployer()
        sess = dep.deploy_shadow("ML-DENSITY-001", shadow_ratio=0.2)
        assert sess.model_id == "ML-DENSITY-001"
        assert sess.shadow_ratio == 0.2
        assert sess.active is True

    def test_shadow_ratio_bounds(self):
        dep = GrayReleaseShadowDeployer()
        with pytest.raises(ShadowDeployError, match="shadow_ratio"):
            dep.deploy_shadow("m1", shadow_ratio=1.5)
        with pytest.raises(ShadowDeployError, match="shadow_ratio"):
            dep.deploy_shadow("m1", shadow_ratio=0.0)

    def test_duplicate_shadow_rejected(self):
        dep = GrayReleaseShadowDeployer()
        dep.deploy_shadow("m1", shadow_ratio=0.1)
        with pytest.raises(ShadowDeployError, match="已在影子部署"):
            dep.deploy_shadow("m1", shadow_ratio=0.1)


class TestShadowRecording:
    def test_record_predictions_only_observes(self):
        """影子只记录不生效：记录的预测永不进入生效面。"""
        dep = GrayReleaseShadowDeployer()
        dep.deploy_shadow("m1", shadow_ratio=0.5)
        result = dep.record_shadow_predictions("m1", _preds())
        assert result["recorded"] == 30
        assert result["effective"] is False  # 红线：影子不生效

    def test_record_unknown_model_raises(self):
        dep = GrayReleaseShadowDeployer()
        with pytest.raises(ShadowDeployError, match="未影子部署"):
            dep.record_shadow_predictions("ghost", _preds(5))

    def test_shadow_report_aggregates(self):
        dep = GrayReleaseShadowDeployer()
        dep.deploy_shadow("m1", shadow_ratio=0.3)
        dep.record_shadow_predictions("m1", _preds(10))
        dep.record_shadow_predictions("m1", _preds(20))
        rep = dep.shadow_report("m1")
        assert rep["total_records"] == 30
        assert rep["batches"] == 2
        assert "mean" in rep and "std" in rep

    def test_retire_shadow(self):
        dep = GrayReleaseShadowDeployer()
        dep.deploy_shadow("m1", shadow_ratio=0.1)
        sess = dep.retire_shadow("m1")
        assert sess.active is False
        with pytest.raises(ShadowDeployError, match="未影子部署"):
            dep.record_shadow_predictions("m1", _preds(3))
