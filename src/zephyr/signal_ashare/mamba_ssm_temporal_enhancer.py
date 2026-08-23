# [BLUEPRINT] MOD-SIG-051 | docs/03_modules/MOD-SIG-051/
# [MODULE] zephyr.signal_ashare.mamba_ssm_temporal_enhancer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy
# [CONSUMERS] （远期：信号层时序特征增强消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 未 fit 时 enhance 一律 fail-closed（ValueError）；不引 torch/mamba_ssm 依赖——真模型属 B-007 人工闸门；输出形状恒等于输入形状
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空输入/非有限值/维度不符/非法 smoothing/未训练 enhance → ValueError
# [TESTS] tests/signal_ashare/test_mamba_ssm_temporal_enhancer.py
# [A_module] module_id=MOD-SIG-051 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Mamba-SSM 时序增强器（MOD-SIG-051）——接口契约 + 轻量占位实现。

Mamba/SSM 属远期候选（10 号 memo §9.15.3：⭐ 低，Phase 5+ 评估，过度工程风险
与可解释性冲突已登记）。本模块只立接口契约：enhance 签名/输入校验/未训练
fail-closed。**不引 torch/mamba_ssm 依赖**——真模型属 B-007 人工闸门。

占位增强路径：fit 学 z-score 统计（mean/std，std=0 列安全处理），enhance 输出
标准化 + EMA 平滑序列，形状恒等于输入。
"""

from __future__ import annotations

from typing import Final

import numpy as np

__all__: Final = ["MambaSsmTemporalEnhancer"]

_EPS: Final[float] = 1e-12


class MambaSsmTemporalEnhancer:
    """Mamba-SSM 时序增强器骨架（z-score + EMA 占位）。"""

    def __init__(self, *, smoothing: float = 0.3) -> None:
        if not 0.0 < smoothing <= 1.0:
            raise ValueError(f"smoothing 必须 ∈ (0,1]: {smoothing}")
        self._smoothing = smoothing
        self._mean: np.ndarray | None = None
        self._std: np.ndarray | None = None

    @property
    def is_fitted(self) -> bool:
        return self._mean is not None

    def fit(self, features: np.ndarray) -> None:
        """拟合标准化统计。空输入/非有限值 → ValueError。"""
        x = np.asarray(features, dtype=float)
        if x.size == 0:
            raise ValueError("输入特征为空")
        if x.ndim == 1:
            x = x.reshape(-1, 1)
        if not np.all(np.isfinite(x)):
            raise ValueError("输入特征含非有限值")
        self._mean = x.mean(axis=0)
        self._std = x.std(axis=0)

    def enhance(self, features: np.ndarray) -> np.ndarray:
        """增强（标准化 + EMA 平滑）。未训练 fail-closed；形状恒等于输入。"""
        if not self.is_fitted:
            raise ValueError("模型未训练——enhance fail-closed")
        x = np.asarray(features, dtype=float)
        if x.size == 0:
            raise ValueError("输入特征为空")
        squeeze = x.ndim == 1
        if squeeze:
            x = x.reshape(-1, 1)
        if not np.all(np.isfinite(x)):
            raise ValueError("输入特征含非有限值")
        if x.shape[1] != self._mean.shape[0]:
            raise ValueError(f"特征维度不符: fit={self._mean.shape[0]} vs enhance={x.shape[1]}")

        z = (x - self._mean) / np.where(self._std > _EPS, self._std, 1.0)
        alpha = self._smoothing
        out = np.empty_like(z)
        out[0] = z[0]
        for i in range(1, len(z)):
            out[i] = alpha * z[i] + (1.0 - alpha) * out[i - 1]
        return out.ravel() if squeeze else out
