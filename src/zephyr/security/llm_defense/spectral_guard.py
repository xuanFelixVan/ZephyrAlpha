# [BLUEPRINT] MOD-SECLLM-002 | docs/03_modules/_domain_security_llm/spectral_guard/blueprint.md
# [MODULE] zephyr.security.llm_defense.spectral_guard
# [DOMAIN] D_SECURITY_LLM
# [DEPENDENCIES] numpy（谱特征纯 numpy 实现；分模型双阈值表全注入，无时钟/副作用）
# [CONSUMERS] 运行时装配批（LLM 输出护栏装配点注入模型阈值表后调用判定）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 注意力矩阵视作动态图(对称化度-邻接 Laplacian); 谱特征=谱集中度/归一化谱熵(能量分散度); 幻觉评分∈[0,1]确定性; 分模型双阈值(warn/block)闭合; recall优先: SUSPECT 按阳性计; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_security_llm/spectral_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] SpectralGuardError(占位 ZA-SECLLM-UNREGISTERED-SPECTRAL-GUARD)——未注册模型/非方阵/空矩阵/负值或非有限元素/非法阈值表时抛
# [TESTS] tests/security/llm_defense/test_spectral_guard.py
# [A_module] module_id=MOD-SECLLM-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""SpectralGuard — Spectral 注意力谱幻觉检测器（MOD-SECLLM-002）。

B10-01868（AUD-DRAFT-001-DIGEST P2 波 P2-W15，CAND-SECLLM-001，A1
§29.24-7）：注意力矩阵视作**动态图** → Laplacian **谱能量特征**（度矩阵
− 邻接矩阵，对称化后 eigvalsh，谱集中度/归一化谱熵，纯 numpy 实现）+
**幻觉评分**（能量分散度 → 评分）+ **分模型阈值校准**（Qwen/DeepSeek 双
阈值表注入）+ **recall 优先**判定语义（SUSPECT 按阳性计，宁误报不漏报）。

查重分工（蓝图 §0）：sentinel_hallucination_detector=哨兵幻觉检测语义
（本件=注意力谱特征通路，不重建哨兵流水线）。
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Final, Mapping, Sequence

import numpy as np

_log = logging.getLogger(__name__)

__all__: Final = [
    "GuardResult",
    "SpectralFeatures",
    "SpectralGuard",
    "SpectralGuardError",
    "SpectralThresholds",
    "Verdict",
]


class SpectralGuardError(Exception):
    """Spectral 幻觉检测输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-SECLLM-UNREGISTERED-SPECTRAL-GUARD。
    """


class Verdict(str, Enum):
    """判定结论（词表闭合）。"""

    CLEAN = "clean"
    SUSPECT = "suspect"
    HALLUCINATED = "hallucinated"


@dataclass(frozen=True)
class SpectralThresholds:
    """分模型双阈值（warn 疑似线 / block 确认线，frozen）。"""

    warn: float
    block: float


@dataclass(frozen=True)
class SpectralFeatures:
    """Laplacian 谱能量特征（frozen）。"""

    size: int
    spectral_entropy: float
    concentration: float
    dispersion: float


@dataclass(frozen=True)
class GuardResult:
    """幻觉判定结果（frozen）。"""

    model: str
    score: float
    verdict: Verdict
    is_hallucination: bool
    features: SpectralFeatures


class SpectralGuard:
    """Spectral 注意力谱幻觉检测器（谱特征 + 双阈值 + recall 优先）。"""

    def __init__(
        self,
        *,
        thresholds: Mapping[str, SpectralThresholds],
        recall_first: bool = True,
    ) -> None:
        if not thresholds:
            raise SpectralGuardError("thresholds 为空（无分模型阈值表声明）")
        table: dict[str, SpectralThresholds] = {}
        for model, th in thresholds.items():
            if not model:
                raise SpectralGuardError("模型名为空")
            if not isinstance(th, SpectralThresholds):
                raise SpectralGuardError(f"模型 {model} 阈值类型非法")
            if not (0.0 <= th.warn <= th.block <= 1.0):
                raise SpectralGuardError(
                    f"模型 {model} 阈值非法（须 0<=warn<=block<=1）: "
                    f"warn={th.warn} block={th.block}"
                )
            table[model] = th
        self._thresholds = table
        self._recall_first = bool(recall_first)

    # ── 谱特征 ───────────────────────────────────────────────────────────

    @staticmethod
    def features(attention: Sequence[Sequence[float]]) -> SpectralFeatures:
        """注意力矩阵 → Laplacian 谱能量特征（度−邻接，纯 numpy）。

        对称化 A_sym=(A+Aᵀ)/2；L=D−A_sym；特征值升序；能量占比 p=λ/Σλ；
        谱熵 H=−Σp·ln p；dispersion=H/ln(n)（能量分散度，∈[0,1]）。
        """
        arr = np.asarray(attention, dtype=float)
        if arr.ndim != 2 or arr.shape[0] != arr.shape[1]:
            raise SpectralGuardError(f"注意力矩阵非方阵: shape={arr.shape!r}")
        n = arr.shape[0]
        if n == 0:
            raise SpectralGuardError("注意力矩阵为空")
        if not np.isfinite(arr).all():
            raise SpectralGuardError("注意力矩阵含非有限元素")
        if (arr < 0).any():
            raise SpectralGuardError("注意力矩阵含负值元素")

        sym = (arr + arr.T) / 2.0
        laplacian = np.diag(sym.sum(axis=1)) - sym
        eigvals = np.linalg.eigvalsh(laplacian)
        eigvals = np.clip(eigvals, 0.0, None)
        total = float(eigvals.sum())
        if total <= 0.0:
            # 零能量（如全零/单位注意力）：完全集中，无分散
            return SpectralFeatures(
                size=n, spectral_entropy=0.0, concentration=1.0, dispersion=0.0
            )
        p = eigvals / total
        positive = p[p > 0.0]
        entropy = float(-(positive * np.log(positive)).sum())
        dispersion = entropy / math.log(n) if n > 1 else 0.0
        return SpectralFeatures(
            size=n,
            spectral_entropy=entropy,
            concentration=float(p.max()),
            dispersion=dispersion,
        )

    # ── 幻觉判定 ─────────────────────────────────────────────────────────

    def evaluate(
        self, model: str, attention: Sequence[Sequence[float]]
    ) -> GuardResult:
        """幻觉评分 + 分模型双阈值判定（recall 优先）。"""
        th = self._thresholds.get(model)
        if th is None:
            raise SpectralGuardError(f"未注册模型: {model!r}（Fail-Closed）")
        feats = self.features(attention)
        score = feats.dispersion
        if score >= th.block:
            verdict = Verdict.HALLUCINATED
        elif score >= th.warn:
            verdict = Verdict.SUSPECT
        else:
            verdict = Verdict.CLEAN
        # recall 优先：SUSPECT 按阳性计（宁误报不漏报）
        is_hallucination = (
            verdict is Verdict.HALLUCINATED
            or (verdict is Verdict.SUSPECT and self._recall_first)
        )
        if is_hallucination:
            _log.warning(
                "Spectral 幻觉判定: model=%s score=%.4f verdict=%s",
                model, score, verdict.value,
            )
        return GuardResult(
            model=model,
            score=score,
            verdict=verdict,
            is_hallucination=is_hallucination,
            features=feats,
        )
