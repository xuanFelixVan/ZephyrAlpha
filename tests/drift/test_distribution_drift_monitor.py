# [BLUEPRINT] MOD-FBL-001 | docs/03_modules/_domain_fbl_detectors/distribution_drift_monitor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FBL-001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.drift.test_distribution_drift_monitor
# [TESTS] src/zephyr/feedback_loop/detectors/drift/distribution_drift_monitor.py
"""MOD-FBL-001 单元测试：distribution_drift_monitor 三路分布漂移监控器。

蓝图验收（B10-01824/CAND-FBLDETEC-001，A1 §29.5）：
PSI/KL/MDD 三度量已知答案 + feature/concept/label 三路独立阈值 +
差异化响应矩阵（feature critical→DEGRADE，concept/label critical→RETRAIN）。
全部内存构造分布样本，不触网不触库。
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip(
    "zephyr.feedback_loop.detectors.drift.distribution_drift_monitor",
    reason="distribution_drift_monitor not importable",
)

from zephyr.feedback_loop.detectors.drift.distribution_drift_monitor import (  # noqa: E402
    ChannelThresholds,
    DistributionDriftError,
    DistributionDriftMonitor,
    DriftChannel,
    DriftResponse,
    DriftSeverity,
    kl_divergence,
    mdd,
    psi,
)

_REF = np.linspace(-2.0, 2.0, 200)  # 确定性参照分布
_SAME = _REF.copy()
_SHIFTED = _REF + 3.0  # 大幅平移 → 分布显著漂移


# ──────────────────────────────────────────────────────────────────────────────
# 三度量已知答案
# ──────────────────────────────────────────────────────────────────────────────


class TestMetrics:
    def test_psi_identical_near_zero(self) -> None:
        assert psi(_REF, _SAME) == pytest.approx(0.0, abs=1e-6)

    def test_psi_shifted_large(self) -> None:
        assert psi(_REF, _SHIFTED) > 1.0

    def test_kl_identical_near_zero(self) -> None:
        assert kl_divergence(_REF, _SAME) == pytest.approx(0.0, abs=1e-6)

    def test_kl_shifted_positive(self) -> None:
        assert kl_divergence(_REF, _SHIFTED) > 1.0

    def test_mdd_identical_zero(self) -> None:
        assert mdd(_REF, _SAME) == pytest.approx(0.0, abs=1e-9)

    def test_mdd_shifted_equals_standardized_mean_gap(self) -> None:
        # 平移 3.0，参照 σ≈1.16 → 标准化距离 ≈ 3/σ > 2
        assert mdd(_REF, _SHIFTED) > 2.0

    def test_invalid_inputs_fail_closed(self) -> None:
        with pytest.raises(DistributionDriftError):
            psi(np.array([]), _SAME)
        with pytest.raises(DistributionDriftError):
            psi(_REF, np.array([1.0, np.nan]))
        with pytest.raises(DistributionDriftError):
            kl_divergence(_REF, _SAME, buckets=1)
        with pytest.raises(DistributionDriftError):
            mdd(np.array([1.0]), np.array([1.0]))  # 不足 min_samples


# ──────────────────────────────────────────────────────────────────────────────
# 三路独立阈值 + 响应矩阵
# ──────────────────────────────────────────────────────────────────────────────


class TestChannelsAndResponse:
    def test_no_drift_when_identical(self) -> None:
        mon = DistributionDriftMonitor()
        rep = mon.check_feature(_REF, _SAME)
        assert rep.drift_detected is False
        assert rep.severity == DriftSeverity.NONE
        assert rep.response == DriftResponse.NONE
        assert set(rep.metric_values) == {"psi", "kl", "mdd"}

    def test_feature_critical_degrade(self) -> None:
        mon = DistributionDriftMonitor()
        rep = mon.check_feature(_REF, _SHIFTED)
        assert rep.drift_detected is True
        assert rep.severity == DriftSeverity.CRITICAL
        assert rep.response == DriftResponse.DEGRADE  # 特征路 critical→降级

    def test_concept_critical_retrain(self) -> None:
        mon = DistributionDriftMonitor()
        rep = mon.check_concept(_REF, _SHIFTED)
        assert rep.response == DriftResponse.RETRAIN  # 概念路 critical→重训

    def test_label_critical_retrain(self) -> None:
        mon = DistributionDriftMonitor()
        rep = mon.check_label(_REF, _SHIFTED)
        assert rep.response == DriftResponse.RETRAIN  # 标签路 critical→重训

    def test_warn_level_alert(self) -> None:
        # 微调阈值使同一偏移只越 warn 不越 critical
        mon = DistributionDriftMonitor(
            thresholds={
                DriftChannel.FEATURE: ChannelThresholds(
                    psi_warn=0.01,
                    psi_critical=999.0,
                    kl_warn=0.01,
                    kl_critical=999.0,
                    mdd_warn=0.01,
                    mdd_critical=999.0,
                ),
            }
        )
        rep = mon.check_feature(_REF, _SHIFTED)
        assert rep.drift_detected is True
        assert rep.severity == DriftSeverity.WARN
        assert rep.response == DriftResponse.ALERT

    def test_channels_have_independent_thresholds(self) -> None:
        # concept 路阈值极宽 → 同输入 concept 不报警而 feature 报警
        mon = DistributionDriftMonitor(
            thresholds={
                DriftChannel.CONCEPT: ChannelThresholds(
                    psi_warn=999.0,
                    psi_critical=1000.0,
                    kl_warn=999.0,
                    kl_critical=1000.0,
                    mdd_warn=999.0,
                    mdd_critical=1000.0,
                ),
            }
        )
        assert mon.check_feature(_REF, _SHIFTED).drift_detected is True
        assert mon.check_concept(_REF, _SHIFTED).drift_detected is False

    def test_custom_response_matrix_override(self) -> None:
        mon = DistributionDriftMonitor(
            response_matrix={
                (DriftChannel.FEATURE, DriftSeverity.CRITICAL): DriftResponse.RETRAIN,
            }
        )
        rep = mon.check_feature(_REF, _SHIFTED)
        assert rep.response == DriftResponse.RETRAIN

    def test_check_dispatch_by_channel(self) -> None:
        mon = DistributionDriftMonitor()
        rep = mon.check(DriftChannel.LABEL, _REF, _SHIFTED)
        assert rep.channel == DriftChannel.LABEL
        assert rep.response == DriftResponse.RETRAIN

    def test_check_invalid_inputs_fail_closed(self) -> None:
        mon = DistributionDriftMonitor()
        with pytest.raises(DistributionDriftError):
            mon.check_feature(np.array([]), _SAME)
        with pytest.raises(DistributionDriftError):
            mon.check_concept(_REF, np.array([1.0, np.inf]))
