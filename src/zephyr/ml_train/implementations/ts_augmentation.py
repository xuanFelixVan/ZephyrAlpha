# [BLUEPRINT] MOD-ML-015 | docs/03_modules/_domain_machine_learning_train/ts_augmentation/blueprint.md
# [MODULE] zephyr.ml_train.implementations.ts_augmentation
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] numpy（随机源/ks_tester 全注入；GAN/VAE 不建）
# [CONSUMERS] 运行时装配批（训练集增强混入统一注入点装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 五法词表闭合(time_warp/amplitude_scale/slice_mix/jitter/permutation); ε∈[-0.3,0.3] 硬校验; 幅度缩放 c∈[0.5,1.5] 且波动率≤历史P99(超限自动钳制); 切片混合拼接点须市场状态切换点; 增强样本 synthetic=True 且训练权重=0.5; KS 分布质量门强制(未注入/不过 Fail-Closed); 混入比例≤30% 硬约束; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_machine_learning_train/ts_augmentation/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] TsAugmentError(占位 ZA-MLT-UNREGISTERED-TS-AUGMENT)——序列过短/参数越界/拼接点非切换点/质量门未注入或不过/混入超30%时抛
# [TESTS] tests/ml_train/implementations/test_ts_augmentation.py
# [A_module] module_id=MOD-ML-015 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
TsAugmentor — 金融时序数据增强库（MOD-ML-015）。

B1-00639（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLT-019，C2 95；canonical
承接 MLT-023/026 归并）：**轻量五法**——时间扭曲（ε∈[-0.3,0.3]）/ 幅度
缩放（c~U(0.5,1.5) 且波动率≤历史 P99，超限钳制）/ 切片混合（拼接点须
市场状态切换点）/ Jittering / Permutation（随机源全注入）+ 增强样本
``synthetic=True`` 标注 + 训练权重 0.5 + **KS test 分布质量门**（注入
ks_tester，未注入/不过 Fail-Closed）+ **混入比例≤30% 硬约束**。
GAN/VAE 不建（蓝图 §0 明确排除）。

查重分工（蓝图 §0）：scenario_generator=情景路径生成（本件=训练样本轻量
增强，不生成宏观情景）；training_dataset_manager=样本集管理（本件仅产
增强样本与混入裁决）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: rng 参数
#   fields: 参数 rng（无注解）
#   code: ts_augmentation.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: ks_tester 参数
#   fields: 参数 ks_tester（无注解）
#   code: ts_augmentation.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TsAugmentor
#   name_en: TsAugmentor
#   intro: 金融时序轻量增强器（五法 + KS 质量门 + 混入硬约束）。
#   desc: 金融时序轻量增强器（五法 + KS 质量门 + 混入硬约束）。；公共方法（定义序）: time_warp, amplitude_scale, slice_mix, jitter, permutation, mix_ba…
#   inputs: rng ks_tester
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: TsAugmentor
#   downstream: 运行时装配批（训练集增强混入统一注入点装配）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Callable, Final, Sequence

import numpy as np

_log = logging.getLogger(__name__)

__all__: Final = [
    "AugmentedSample",
    "AUGMENT_METHODS",
    "SYNTHETIC_TRAIN_WEIGHT",
    "MAX_MIX_RATIO",
    "TsAugmentError",
    "TsAugmentor",
]

#: 增强方法词表（闭合）
AUGMENT_METHODS: Final[frozenset[str]] = frozenset(
    {
        "time_warp",
        "amplitude_scale",
        "slice_mix",
        "jitter",
        "permutation",
    }
)
#: 增强样本训练权重（硬约束 0.5）
SYNTHETIC_TRAIN_WEIGHT: Final[float] = 0.5
#: 增强样本混入比例上限（硬约束 ≤30%）
MAX_MIX_RATIO: Final[float] = 0.30
#: 时间扭曲 ε 界
_EPSILON_BOUND: Final[float] = 0.3
#: 幅度缩放 c 界
_SCALE_LOW: Final[float] = 0.5
_SCALE_HIGH: Final[float] = 1.5


class TsAugmentError(Exception):
    """时序增强输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLT-UNREGISTERED-TS-AUGMENT。
    """


@dataclass(frozen=True)
class AugmentedSample:
    """增强样本（synthetic 标注 + 训练权重 0.5，frozen）。"""

    values: tuple[float, ...]
    method: str
    synthetic: bool = True
    train_weight: float = SYNTHETIC_TRAIN_WEIGHT
    meta: dict = field(default_factory=dict)


class TsAugmentor:
    """金融时序轻量增强器（五法 + KS 质量门 + 混入硬约束）。"""

    def __init__(
        self,
        *,
        rng: random.Random | None = None,
        ks_tester: Callable[[Sequence[float], Sequence[float]], bool] | None = None,
    ) -> None:
        self._rng = rng or random.Random(0)
        self._ks_tester = ks_tester

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _as_array(series: Sequence[float], name: str = "series") -> np.ndarray:
        arr = np.asarray(series, dtype=float)
        if arr.ndim != 1 or len(arr) < 2:
            raise TsAugmentError(f"{name} 须为一维且长度≥2，实得 shape={arr.shape}")
        return arr

    def _gate(self, original: np.ndarray, augmented: np.ndarray, method: str) -> None:
        """KS 分布质量门：未注入/不过 Fail-Closed。"""
        if self._ks_tester is None:
            raise TsAugmentError("ks_tester 未注入（KS 分布质量门强制，禁止旁路）")
        try:
            ok = bool(self._ks_tester(tuple(original.tolist()), tuple(augmented.tolist())))
        except Exception:  # noqa: BLE001 — 质量门异常按不过处理不抛
            _log.exception("ks_tester 判定异常: method=%s", method)
            ok = False
        if not ok:
            raise TsAugmentError(f"KS 分布质量门未通过: method={method}（增强样本拒收）")

    def _sample(self, values: np.ndarray, method: str, meta: dict) -> AugmentedSample:
        return AugmentedSample(values=tuple(float(v) for v in values), method=method, meta=dict(meta))

    # ── 五法 ──────────────────────────────────────────────────────────────

    def time_warp(self, series: Sequence[float], epsilon: float | None = None) -> AugmentedSample:
        """时间扭曲：ε∈[-0.3,0.3]（未给则随机源抽取），线性插值回原长。"""
        arr = self._as_array(series)
        eps = self._rng.uniform(-_EPSILON_BOUND, _EPSILON_BOUND) if epsilon is None else float(epsilon)
        if not -_EPSILON_BOUND <= eps <= _EPSILON_BOUND:
            raise TsAugmentError(f"ε 越界: {eps}（须 ∈[-0.3,0.3]）")
        n = len(arr)
        warped_index = np.clip(np.linspace(0.0, (n - 1) * (1.0 + eps), n), 0.0, n - 1)
        out = np.interp(warped_index, np.arange(n, dtype=float), arr)
        self._gate(arr, out, "time_warp")
        return self._sample(out, "time_warp", {"epsilon": eps})

    def amplitude_scale(
        self,
        series: Sequence[float],
        c: float | None = None,
        *,
        history: Sequence[float] | None = None,
    ) -> AugmentedSample:
        """幅度缩放：c~U(0.5,1.5)；波动率≤历史 P99（超限自动钳制 c）。"""
        arr = self._as_array(series)
        factor = self._rng.uniform(_SCALE_LOW, _SCALE_HIGH) if c is None else float(c)
        if not _SCALE_LOW <= factor <= _SCALE_HIGH:
            raise TsAugmentError(f"c 越界: {factor}（须 ∈[0.5,1.5]）")
        hist = arr if history is None else self._as_array(history, "history")
        p99 = float(np.percentile(np.abs(np.diff(hist)), 99))
        max_diff = float(np.max(np.abs(np.diff(arr))))
        clamped = False
        if max_diff > 0.0 and factor * max_diff > p99:
            factor = p99 / max_diff  # 钳制至波动率上限
            clamped = True
        out = arr * factor
        self._gate(arr, out, "amplitude_scale")
        return self._sample(out, "amplitude_scale", {"c": factor, "clamped": clamped})

    def slice_mix(
        self,
        series_a: Sequence[float],
        series_b: Sequence[float],
        cut_index: int,
        switch_points: Sequence[int],
    ) -> AugmentedSample:
        """切片混合：拼接点须为市场状态切换点（否则 Fail-Closed）。"""
        a = self._as_array(series_a, "series_a")
        b = self._as_array(series_b, "series_b")
        if len(a) != len(b):
            raise TsAugmentError(f"长度不齐: len(a)={len(a)} != len(b)={len(b)}")
        if cut_index not in set(int(p) for p in switch_points):
            raise TsAugmentError(f"拼接点 {cut_index} 非市场状态切换点（合法: {sorted(set(switch_points))}）")
        if not 0 < cut_index < len(a):
            raise TsAugmentError(f"拼接点越界: {cut_index}（须 ∈(0,{len(a)})）")
        out = np.concatenate([a[:cut_index], b[cut_index:]])
        self._gate(a, out, "slice_mix")
        return self._sample(out, "slice_mix", {"cut_index": cut_index})

    def jitter(self, series: Sequence[float], sigma: float) -> AugmentedSample:
        """Jittering：高斯噪声（随机源注入）。"""
        arr = self._as_array(series)
        if sigma <= 0.0:
            raise TsAugmentError(f"sigma 越界: {sigma}（须 >0）")
        noise = np.array([self._rng.gauss(0.0, sigma) for _ in range(len(arr))])
        out = arr + noise
        self._gate(arr, out, "jitter")
        return self._sample(out, "jitter", {"sigma": float(sigma)})

    def permutation(self, series: Sequence[float], n_segments: int) -> AugmentedSample:
        """Permutation：等长分段乱序（随机源注入）。"""
        arr = self._as_array(series)
        if not 2 <= n_segments <= len(arr):
            raise TsAugmentError(f"n_segments 越界: {n_segments}（须 ∈[2,{len(arr)}]）")
        segments = [seg for seg in np.array_split(arr, n_segments)]
        order = list(range(n_segments))
        self._rng.shuffle(order)
        out = np.concatenate([segments[i] for i in order])
        self._gate(arr, out, "permutation")
        return self._sample(out, "permutation", {"n_segments": n_segments, "order": tuple(order)})

    # ── 混入硬约束 ────────────────────────────────────────────────────────

    def mix_batch(
        self,
        originals: Sequence[object],
        augmented: Sequence[AugmentedSample],
    ) -> list[object]:
        """混入训练批：增强样本占比≤30% 硬约束（超限 Fail-Closed）。"""
        n_orig, n_aug = len(originals), len(augmented)
        total = n_orig + n_aug
        if total == 0:
            raise TsAugmentError("混入批为空")
        for sample in augmented:
            if not sample.synthetic:
                raise TsAugmentError("增强样本须 synthetic=True 标注")
            if sample.train_weight != SYNTHETIC_TRAIN_WEIGHT:
                raise TsAugmentError(f"增强样本训练权重须为 {SYNTHETIC_TRAIN_WEIGHT}，实得 {sample.train_weight}")
        ratio = n_aug / total
        if ratio > MAX_MIX_RATIO:
            raise TsAugmentError(f"混入比例超限: {ratio:.4f} > {MAX_MIX_RATIO}（{n_aug}/{total}，硬约束）")
        _log.info("混入批: orig=%d aug=%d ratio=%.4f", n_orig, n_aug, ratio)
        return list(originals) + list(augmented)
