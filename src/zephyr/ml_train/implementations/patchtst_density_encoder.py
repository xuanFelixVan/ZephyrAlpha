# [BLUEPRINT] MOD-ML-011 | docs/03_modules/_domain_machine_learning_train/patchtst_density_encoder/blueprint.md
# [MODULE] zephyr.ml_train.implementations.patchtst_density_encoder
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] numpy
# [CONSUMERS] MOD-ML-DENSITY(密度头消费) ; MOD-ML-010(QNN Stage1前置特征)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 输入(n,L,C)三维; patchify patch_len=16 stride=8通道独立; SVD top-d_proj投影确定性; query=拟合集embedding均值; softmax注意力权重和=1; transform需先fit; B-009 testing封顶
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] PatchtstEncoderError(ZA-MLT-0013)
# [TESTS] tests/ml_train/test_patchtst_density_encoder.py
# [A_module] module_id=MOD-ML-011 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 时序特征 x
#   fields: (n, lookback, n_channels) 三维张量, 默认60天×60因子
# - id: I2
#   name: PatchtstEncoderConfig
#   fields: patch_len=16, stride=8, d_proj=16, min_samples=8
# 层: 算法
# - id: A1
#   name_zh: ① patchify
#   name_en: patchify
#   intro: 每通道切patch(通道独立)
# - id: A2
#   name_zh: ② SVD patch embedding
#   name_en: svd_embedding
#   intro: 全样本patch合并SVD取top-d_proj主成分
# - id: A3
#   name_zh: ③ 注意力池化
#   name_en: attention_pool
#   intro: query=均值embedding, softmax加权patch维→每通道d维向量
# 层: 输出
# - id: O1
#   name_zh: PatchtstFeatures
#   name_en: PatchtstFeatures
#   intro: channel_embeddings(n,C,d)+pooled(n,d)作密度预测前置特征
#   downstream: MOD-ML-DENSITY密度头; MOD-ML-010 QNN Stage1 ([CONSUMERS] 头)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1

"""PatchTST 密度前置特征编码器 (MOD-ML-011, B10-01831 §29.7)。

Transformer 时序架构密度预测增强：PatchTST 单家族落地，作 QNN Stage1
前置特征提取器（Phase2 路线）。

查重分工 (W-P1-20 铁律⑤探查——时序特征编码器缺口,双路线互补非竞争):
  - mamba_ssm_temporal_enhancer (MOD-SIG-051): 信号域 Mamba 单家族;
    本件=PatchTST 编码器, 家族不同/域不同;
  - density_quantile_trainer (MOD-ML-DENSITY): 消费扁平特征矩阵;
    本件=前置特征编码器, 非预测器;
  - qnn_two_stage (MOD-ML-010): 两阶段 QNN (训练架构);
    本件=Stage1 前置特征提取器 (TSV §29.7 Phase2 原文)。

torch 仅在可选 ml-train extra → numpy MVP (patchify+通道独立+SVD+注意力池化)。

依据: construction_backlog_dig.tsv B10-01831 + CAND-MLT-015
SSoT: docs/03_modules/_domain_machine_learning_train/patchtst_density_encoder/blueprint.md
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Final

import numpy as np

_log = logging.getLogger(__name__)

__all__: Final[list[str]] = [
    "PatchtstEncoderConfig",
    "PatchtstFeatures",
    "PatchtstDensityEncoder",
    "PatchtstEncoderError",
]


class PatchtstEncoderError(Exception):
    """PatchTST 编码器训练/转换失败。"""

    error_code = "ZA-MLT-0013"  # 待登记, 建议 ZA-MLT-0004


@dataclass(frozen=True)
class PatchtstEncoderConfig:
    """PatchTST 编码器配置。"""

    patch_len: int = 16
    stride: int = 8
    d_proj: int = 16
    min_samples: int = 8

    def __post_init__(self) -> None:
        if self.patch_len <= 0:
            raise PatchtstEncoderError(f"patch_len must be > 0, got {self.patch_len}")
        if self.stride <= 0:
            raise PatchtstEncoderError(f"stride must be > 0, got {self.stride}")
        if self.d_proj <= 0:
            raise PatchtstEncoderError(f"d_proj must be > 0, got {self.d_proj}")
        if self.min_samples <= 0:
            raise PatchtstEncoderError(f"min_samples must be > 0, got {self.min_samples}")


@dataclass(frozen=True)
class PatchtstFeatures:
    """PatchTST 编码器输出。"""

    channel_embeddings: np.ndarray  # (n, C, d_proj)
    pooled: np.ndarray  # (n, d_proj)
    n_patches: int


class PatchtstDensityEncoder:
    """PatchTST 密度前置特征编码器。

    输入 (n, lookback, n_channels) 时序 → 输出密度预测前置特征。
    """

    def __init__(self, config: PatchtstEncoderConfig | None = None) -> None:
        self.config = config or PatchtstEncoderConfig()
        self._projection: np.ndarray | None = None  # (patch_len, d_proj)
        self._query: np.ndarray | None = None  # (d_proj,)
        self._n_channels: int | None = None

    def fit(self, x: np.ndarray) -> dict[str, float]:
        """拟合投影矩阵与 query 向量。

        Args:
            x: (n, lookback, n_channels) 时序张量

        Returns:
            拟合指标
        """
        arr = self._validate_input(x)
        n, lookback, n_channels = arr.shape
        if n < self.config.min_samples:
            raise PatchtstEncoderError(f"样本不足: n={n} < min={self.config.min_samples}")

        patches = self._patchify(arr)  # (n, C, P, patch_len)
        n_patches = patches.shape[2]
        flat = patches.reshape(-1, self.config.patch_len)  # (n*C*P, patch_len)

        # SVD 投影 (top-d_proj 主成分)
        _, _, vt = np.linalg.svd(flat, full_matrices=False)
        d_proj = min(self.config.d_proj, vt.shape[0])
        self._projection = vt[:d_proj].T  # (patch_len, d_proj)

        # query = 拟合集 embedding 均值
        embeddings = flat @ self._projection  # (n*C*P, d_proj)
        self._query = np.mean(embeddings, axis=0)  # (d_proj,)

        self._n_channels = n_channels
        metrics = {
            "n_samples": float(n),
            "n_channels": float(n_channels),
            "n_patches": float(n_patches),
            "d_proj": float(d_proj),
        }
        _log.info("PatchTST编码器拟合完成: metrics=%s", metrics)
        return metrics

    def transform(self, x: np.ndarray) -> PatchtstFeatures:
        """转换时序 → 密度预测前置特征。"""
        if self._projection is None or self._query is None:
            raise PatchtstEncoderError("未拟合, 先调 fit()")
        arr = self._validate_input(x)
        n, lookback, n_channels = arr.shape
        if self._n_channels is not None and n_channels != self._n_channels:
            raise PatchtstEncoderError(
                f"n_channels 不匹配: 拟合={self._n_channels} 实得={n_channels}"
            )

        patches = self._patchify(arr)  # (n, C, P, patch_len)
        n_patches = patches.shape[2]
        flat = patches.reshape(-1, self.config.patch_len)
        embeddings = flat @ self._projection  # (n*C*P, d_proj)
        embeddings = embeddings.reshape(n, n_channels, n_patches, -1)  # (n, C, P, d)

        # 注意力池化: softmax(embedding·query/√d) 对 patch 维加权
        scale = np.sqrt(embeddings.shape[-1])
        scores = np.einsum("ncpd,d->ncp", embeddings, self._query) / scale  # (n, C, P)
        # softmax over P
        scores_max = np.max(scores, axis=-1, keepdims=True)
        exp_scores = np.exp(scores - scores_max)
        attn = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)  # (n, C, P)

        channel_embeddings = np.einsum("ncp,ncpd->ncd", attn, embeddings)  # (n, C, d)
        pooled = np.mean(channel_embeddings, axis=1)  # (n, d)

        return PatchtstFeatures(
            channel_embeddings=channel_embeddings,
            pooled=pooled,
            n_patches=n_patches,
        )

    # ── 内部 ────────────────────────────────────────────────

    def _validate_input(self, x: np.ndarray) -> np.ndarray:
        arr = np.asarray(x, dtype=float)
        if arr.ndim != 3:
            raise PatchtstEncoderError(f"输入需三维 (n, L, C), 实得 ndim={arr.ndim}")
        if arr.shape[1] < self.config.patch_len:
            raise PatchtstEncoderError(
                f"lookback={arr.shape[1]} < patch_len={self.config.patch_len}"
            )
        return arr

    def _patchify(self, x: np.ndarray) -> np.ndarray:
        """切 patch: (n, L, C) → (n, C, P, patch_len), 通道独立。"""
        n, lookback, n_channels = x.shape
        pl = self.config.patch_len
        stride = self.config.stride
        # 计算 patch 数: floor((L - pl) / stride) + 1
        n_patches = (lookback - pl) // stride + 1
        patches = np.zeros((n, n_channels, n_patches, pl))
        for p in range(n_patches):
            start = p * stride
            patches[:, :, p, :] = x[:, start:start + pl, :].transpose(0, 2, 1)
        return patches