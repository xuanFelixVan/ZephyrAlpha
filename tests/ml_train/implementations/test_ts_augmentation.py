# [BLUEPRINT] MOD-ML-015 | docs/03_modules/_domain_machine_learning_train/ts_augmentation/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-ML-015 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_train.implementations.test_ts_augmentation
# [TESTS] src/zephyr/ml_train/implementations/ts_augmentation.py
"""MOD-ML-015 单元测试：ts_augmentation 金融时序数据增强库。

蓝图验收（B1-00639/CAND-MLT-019，C2 95；canonical 承接 MLT-023/026）：
五法（时间扭曲 ε∈[-0.3,0.3]/幅度缩放波动率≤P99 钳制/切换点切片混合/
Jittering/Permutation，随机源注入）+ synthetic=True + 权重 0.5 + KS 质量门
注入（未注入/不过 Fail-Closed）+ 混入≤30% 硬约束。随机源/KS 全内存替身。
"""

from __future__ import annotations

import random

import pytest

pytest.importorskip(
    "zephyr.ml_train.implementations.ts_augmentation",
    reason="ts_augmentation not importable",
)

from zephyr.ml_train.implementations.ts_augmentation import (  # noqa: E402
    AugmentedSample,
    MAX_MIX_RATIO,
    SYNTHETIC_TRAIN_WEIGHT,
    TsAugmentError,
    TsAugmentor,
)

_SERIES = [100.0, 101.0, 100.5, 102.0, 103.0, 102.5, 104.0, 105.0, 104.5, 106.0]
_SERIES_B = [200.0, 201.0, 200.5, 202.0, 203.0, 202.5, 204.0, 205.0, 204.5, 206.0]


def _augmentor(ks_ok: bool = True, seed: int = 7) -> TsAugmentor:
    return TsAugmentor(rng=random.Random(seed), ks_tester=lambda o, a: ks_ok)


# ──────────────────────────────────────────────────────────────────────────────
# 时间扭曲
# ──────────────────────────────────────────────────────────────────────────────


class TestTimeWarp:
    def test_ok_preserves_length(self) -> None:
        sample = _augmentor().time_warp(_SERIES, epsilon=0.2)
        assert len(sample.values) == len(_SERIES)
        assert sample.method == "time_warp"
        assert sample.synthetic is True
        assert sample.train_weight == SYNTHETIC_TRAIN_WEIGHT

    def test_epsilon_zero_identity(self) -> None:
        sample = _augmentor().time_warp(_SERIES, epsilon=0.0)
        assert sample.values == pytest.approx(_SERIES)

    def test_epsilon_out_of_bound_rejected(self) -> None:
        with pytest.raises(TsAugmentError):
            _augmentor().time_warp(_SERIES, epsilon=0.31)
        with pytest.raises(TsAugmentError):
            _augmentor().time_warp(_SERIES, epsilon=-0.31)

    def test_random_epsilon_deterministic_with_seed(self) -> None:
        s1 = _augmentor(seed=3).time_warp(_SERIES)
        s2 = _augmentor(seed=3).time_warp(_SERIES)
        assert s1.values == s2.values
        assert -0.3 <= s1.meta["epsilon"] <= 0.3


# ──────────────────────────────────────────────────────────────────────────────
# 幅度缩放（波动率≤P99 钳制）
# ──────────────────────────────────────────────────────────────────────────────


class TestAmplitudeScale:
    def test_scale_down_no_clamp(self) -> None:
        sample = _augmentor().amplitude_scale(_SERIES, c=0.8)
        assert sample.values == pytest.approx([v * 0.8 for v in _SERIES])
        assert sample.meta["clamped"] is False

    def test_scale_up_clamped_by_p99(self) -> None:
        # history == series 时 P99 < max|diff|，c=1.5 必钳制
        sample = _augmentor().amplitude_scale(_SERIES, c=1.5)
        assert sample.meta["clamped"] is True
        assert sample.meta["c"] < 1.5

    def test_wide_history_no_clamp(self) -> None:
        wide_history = [0.0, 1000.0, -1000.0, 500.0] * 10  # 极大波动历史
        sample = _augmentor().amplitude_scale(_SERIES, c=1.4, history=wide_history)
        assert sample.meta["clamped"] is False
        assert sample.values == pytest.approx([v * 1.4 for v in _SERIES])

    def test_c_out_of_bound_rejected(self) -> None:
        with pytest.raises(TsAugmentError):
            _augmentor().amplitude_scale(_SERIES, c=0.4)
        with pytest.raises(TsAugmentError):
            _augmentor().amplitude_scale(_SERIES, c=1.6)

    def test_random_c_deterministic_with_seed(self) -> None:
        s1 = _augmentor(seed=5).amplitude_scale(_SERIES)
        s2 = _augmentor(seed=5).amplitude_scale(_SERIES)
        assert s1.values == s2.values


# ──────────────────────────────────────────────────────────────────────────────
# 切片混合（拼接点须切换点）
# ──────────────────────────────────────────────────────────────────────────────


class TestSliceMix:
    def test_ok_at_switch_point(self) -> None:
        sample = _augmentor().slice_mix(_SERIES, _SERIES_B, cut_index=4, switch_points=[2, 4, 7])
        assert sample.values == tuple(_SERIES[:4] + _SERIES_B[4:])
        assert sample.meta["cut_index"] == 4

    def test_non_switch_point_rejected(self) -> None:
        with pytest.raises(TsAugmentError):
            _augmentor().slice_mix(_SERIES, _SERIES_B, cut_index=5, switch_points=[2, 4, 7])

    def test_length_mismatch_rejected(self) -> None:
        with pytest.raises(TsAugmentError):
            _augmentor().slice_mix(_SERIES, _SERIES_B[:6], cut_index=4, switch_points=[4])

    def test_boundary_cut_rejected(self) -> None:
        with pytest.raises(TsAugmentError):
            _augmentor().slice_mix(_SERIES, _SERIES_B, cut_index=0, switch_points=[0])


# ──────────────────────────────────────────────────────────────────────────────
# Jittering / Permutation
# ──────────────────────────────────────────────────────────────────────────────


class TestJitterPermutation:
    def test_jitter_deterministic_with_seed(self) -> None:
        s1 = _augmentor(seed=11).jitter(_SERIES, sigma=0.5)
        s2 = _augmentor(seed=11).jitter(_SERIES, sigma=0.5)
        assert s1.values == s2.values
        assert s1.values != tuple(_SERIES)  # 确实加了噪声

    def test_jitter_sigma_nonpositive_rejected(self) -> None:
        with pytest.raises(TsAugmentError):
            _augmentor().jitter(_SERIES, sigma=0.0)
        with pytest.raises(TsAugmentError):
            _augmentor().jitter(_SERIES, sigma=-0.1)

    def test_permutation_preserves_multiset(self) -> None:
        sample = _augmentor(seed=13).permutation(_SERIES, n_segments=3)
        assert sorted(sample.values) == sorted(_SERIES)
        assert len(sample.values) == len(_SERIES)

    def test_permutation_n_segments_out_of_bound_rejected(self) -> None:
        with pytest.raises(TsAugmentError):
            _augmentor().permutation(_SERIES, n_segments=1)
        with pytest.raises(TsAugmentError):
            _augmentor().permutation(_SERIES, n_segments=len(_SERIES) + 1)

    def test_series_too_short_rejected(self) -> None:
        with pytest.raises(TsAugmentError):
            _augmentor().jitter([1.0], sigma=0.1)


# ──────────────────────────────────────────────────────────────────────────────
# KS 质量门（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestKsGate:
    def test_ks_tester_not_injected_fail_closed(self) -> None:
        augmentor = TsAugmentor(rng=random.Random(0))
        with pytest.raises(TsAugmentError):
            augmentor.jitter(_SERIES, sigma=0.1)

    def test_ks_reject_blocks_sample(self) -> None:
        with pytest.raises(TsAugmentError):
            _augmentor(ks_ok=False).jitter(_SERIES, sigma=0.1)

    def test_ks_exception_treated_as_reject(self) -> None:
        def _boom(o, a):
            raise RuntimeError("ks 崩溃")

        augmentor = TsAugmentor(rng=random.Random(0), ks_tester=_boom)
        with pytest.raises(TsAugmentError):
            augmentor.jitter(_SERIES, sigma=0.1)


# ──────────────────────────────────────────────────────────────────────────────
# 混入 ≤30% 硬约束
# ──────────────────────────────────────────────────────────────────────────────


class TestMixBatch:
    def _aug_samples(self, n: int) -> list[AugmentedSample]:
        augmentor = _augmentor()
        return [augmentor.jitter(_SERIES, sigma=0.1) for _ in range(n)]

    def test_mix_within_limit(self) -> None:
        originals = [object() for _ in range(7)]
        batch = _augmentor().mix_batch(originals, self._aug_samples(3))  # 3/10 = 30%
        assert len(batch) == 10

    def test_mix_over_limit_rejected(self) -> None:
        originals = [object() for _ in range(6)]
        with pytest.raises(TsAugmentError):
            _augmentor().mix_batch(originals, self._aug_samples(3))  # 3/9 > 30%

    def test_mix_empty_batch_rejected(self) -> None:
        with pytest.raises(TsAugmentError):
            _augmentor().mix_batch([], [])

    def test_mix_rejects_non_synthetic(self) -> None:
        bad = AugmentedSample(values=(1.0, 2.0), method="jitter", synthetic=False)
        with pytest.raises(TsAugmentError):
            _augmentor().mix_batch([object() for _ in range(7)], [bad])

    def test_mix_rejects_wrong_weight(self) -> None:
        bad = AugmentedSample(values=(1.0, 2.0), method="jitter", train_weight=1.0)
        with pytest.raises(TsAugmentError):
            _augmentor().mix_batch([object() for _ in range(7)], [bad])

    def test_max_mix_ratio_constant(self) -> None:
        assert MAX_MIX_RATIO == 0.30
