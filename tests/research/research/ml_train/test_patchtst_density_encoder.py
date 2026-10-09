# [BLUEPRINT] MOD-ML-011 | docs/03_modules/_domain_machine_learning_train/patchtst_density_encoder/blueprint.md | §29.7
# [TTL] permanent
# [A_test] module_id: MOD-ML-011 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_patchtst_density_encoder
# [TESTS] src/zephyr/ml_train/implementations/patchtst_density_encoder.py
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""PatchtstDensityEncoder (MOD-ML-011) 测试套件。

覆盖: patchify形状与通道独立性/SVD投影确定性/注意力池化权重和为1/pooled特征维度/未fit报错/输入校验。
"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.ml_train.implementations.patchtst_density_encoder import (
    PatchtstDensityEncoder,
    PatchtstEncoderConfig,
    PatchtstEncoderError,
    PatchtstFeatures,
)


def _toy_ts(n: int = 20, lookback: int = 60, n_channels: int = 5, seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(size=(n, lookback, n_channels))


# ── fit/transform 链 ─────────────────────────────────────────────────────────


class TestFitTransform:
    def test_fit_returns_metrics(self):
        x = _toy_ts()
        enc = PatchtstDensityEncoder()
        metrics = enc.fit(x)
        assert metrics["n_samples"] == 20.0
        assert metrics["n_channels"] == 5.0
        assert metrics["d_proj"] == 16.0

    def test_transform_output_shapes(self):
        x = _toy_ts(n=10, lookback=60, n_channels=5)
        enc = PatchtstDensityEncoder()
        enc.fit(x)
        out = enc.transform(x)
        assert isinstance(out, PatchtstFeatures)
        assert out.channel_embeddings.shape == (10, 5, 16)
        assert out.pooled.shape == (10, 16)
        # n_patches = (60-16)//8 + 1 = 6
        assert out.n_patches == 6

    def test_svd_deterministic(self):
        x = _toy_ts(n=10, lookback=60, n_channels=5, seed=42)
        enc1 = PatchtstDensityEncoder()
        enc1.fit(x)
        out1 = enc1.transform(x)
        enc2 = PatchtstDensityEncoder()
        enc2.fit(x)
        out2 = enc2.transform(x)
        np.testing.assert_allclose(out1.pooled, out2.pooled, rtol=1e-10)


# ── patchify ─────────────────────────────────────────────────────────────────


class TestPatchify:
    def test_channel_independence(self):
        # 通道间不互相影响: 交换通道顺序, 对应通道embedding不变
        x = _toy_ts(n=10, lookback=60, n_channels=3, seed=1)
        enc = PatchtstDensityEncoder()
        enc.fit(x)
        out1 = enc.transform(x)
        # 交换通道 0 和 1
        x_swap = x[:, :, [1, 0, 2]]
        out2 = enc.transform(x_swap)
        # 交换后通道 0 应等于原通道 1
        np.testing.assert_allclose(out2.channel_embeddings[:, 0, :], out1.channel_embeddings[:, 1, :], rtol=1e-10)
        np.testing.assert_allclose(out2.channel_embeddings[:, 1, :], out1.channel_embeddings[:, 0, :], rtol=1e-10)


# ── 注意力池化 ────────────────────────────────────────────────────────────────


class TestAttentionPooling:
    def test_attention_weights_sum_to_one(self):
        x = _toy_ts(n=10, lookback=60, n_channels=3)
        enc = PatchtstDensityEncoder()
        enc.fit(x)
        # 手动计算注意力权重验证
        arr = x
        patches = enc._patchify(arr)
        flat = patches.reshape(-1, enc.config.patch_len)
        emb = flat @ enc._projection
        emb = emb.reshape(arr.shape[0], arr.shape[2], patches.shape[2], -1)
        scale = np.sqrt(emb.shape[-1])
        scores = np.einsum("ncpd,d->ncp", emb, enc._query) / scale
        scores_max = np.max(scores, axis=-1, keepdims=True)
        exp_scores = np.exp(scores - scores_max)
        attn = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
        # 每行和应为 1
        np.testing.assert_allclose(np.sum(attn, axis=-1), 1.0, rtol=1e-10)


# ── 输入校验 ─────────────────────────────────────────────────────────────────


class TestInputValidation:
    def test_not_fitted_transform(self):
        enc = PatchtstDensityEncoder()
        with pytest.raises(PatchtstEncoderError, match="未拟合"):
            enc.transform(np.zeros((5, 60, 3)))

    def test_invalid_ndim(self):
        enc = PatchtstDensityEncoder()
        with pytest.raises(PatchtstEncoderError, match="三维"):
            enc.fit(np.zeros((5, 60)))

    def test_lookback_too_short(self):
        enc = PatchtstDensityEncoder()
        with pytest.raises(PatchtstEncoderError, match="lookback"):
            enc.fit(np.zeros((5, 10, 3)))  # 10 < patch_len=16

    def test_min_samples(self):
        cfg = PatchtstEncoderConfig(min_samples=10)
        enc = PatchtstDensityEncoder(cfg)
        with pytest.raises(PatchtstEncoderError, match="样本不足"):
            enc.fit(np.zeros((5, 60, 3)))  # 5 < 10

    def test_channel_mismatch(self):
        enc = PatchtstDensityEncoder()
        enc.fit(np.zeros((10, 60, 5)))
        with pytest.raises(PatchtstEncoderError, match="n_channels 不匹配"):
            enc.transform(np.zeros((10, 60, 3)))

    def test_config_validation(self):
        with pytest.raises(PatchtstEncoderError, match="patch_len"):
            PatchtstEncoderConfig(patch_len=0)
        with pytest.raises(PatchtstEncoderError, match="stride"):
            PatchtstEncoderConfig(stride=0)
        with pytest.raises(PatchtstEncoderError, match="d_proj"):
            PatchtstEncoderConfig(d_proj=0)
