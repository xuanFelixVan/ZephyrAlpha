# [BLUEPRINT] MOD-REGIME_VAL-002 | 13_regime_phase3_engineering_plan §2.2 P0-E2
# [MODULE] zephyr.regime.validation.phase2.confidence_calibrator
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; scipy; sklearn; pandas
# [CONSUMERS] zephyr.regime.validation.phase2.phase2_runner; scripts.tests.run_phase2_validation
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 校准只减自信不减锐度(T>1降温); 保序性(argmax不变); PIT防泄漏(IS裁剪+方向只用IS数据); BCE非多类NLL; 四级降级(n>=50/20/prev/identity); Isotonic原始数据fit(PAVA自带正则化,无需预分桶); overlay态走Stage2校准
# [MODIFY-GUARD] 13_regime_phase3_engineering_plan.md §2.2
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CalibrationError(ZA-REGIME-0024)
# [TESTS] tests/regime/phase2/test_confidence_calibrator.py
# [A_module] module_id=MOD-REGIME_VAL-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #13_regime_phase3_engineering_plan §2.2 #12_regime_phase2_validation §2.4 B1
"""两阶段概率校准器（13_regime_phase3_engineering_plan §2.2 P0-E2）。

Stage 1: Temperature Scaling（全局降温，治本）
    softmax(log_proba / T)，T 从 IS 数据最小化二元交叉熵学习。
    Guo et al. 2017 证明保序约束下 Brier 最优（但 HMM log_proba 是对数后验非
    pre-softmax logits，故为 tempering——数学有效但非严格 Brier 最优，§2.2.3）。

Stage 2: Isotonic Regression（局部修正，治标）
    直接在原始 (confidence, occurred) 对上 fit IsotonicRegression（PAVA 算法），
    无需预分桶。PAVA 的单调性约束自带正则化，避免预分桶导致的信息损失
    （5 桶预分桶仅产生 3-4 个拟合点，局部修正过粗）。分桶点仅用于日志可观测性。
    亦用于 overlay 态 confidence 校准（HMM 基态走 Stage 1+2，overlay 态走 Stage 2）。

降级策略（§2.2.10）：
    Level 1 (n≥50): 正常 fit Stage 1 + Stage 2
    Level 2 (20≤n<50): 只 fit Stage 1（Isotonic 需更多样本）
    Level 3 (n<20): 回退上季度校准器
    Level 4 (n<20 + 无上季度): T=1.0 不校准

PIT 防泄漏（§2.2.9）：
    #1 forward_returns 跨 IS/OOS 边界 → IS 尾部裁剪 forward_days * 1.5
    #2 regime_directions 用全量数据 → 只用 IS 安全数据推断
    #3 NLL 用二元交叉熵（occurred 是二值指标非类别标签）

依据: 13_regime_phase3_engineering_plan §2.2 / 12_regime_phase2_validation §2.4 B1
Version: 0.1.0
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from scipy.optimize import minimize_scalar
except ImportError:  # pragma: no cover
    minimize_scalar = None  # type: ignore[assignment,misc]

try:
    from sklearn.isotonic import IsotonicRegression
except ImportError:  # pragma: no cover
    IsotonicRegression = None  # type: ignore[assignment,misc]

try:
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

# ── 常量 ────────────────────────────────────────────────────────────

# T 参数搜索范围（§2.2.8 B）
# 上界 30.0：HMM 后验极度过自信（P=0.95+），T=10 仅能降到 ~0.5-0.8，
# 实测所有季度 T 命中 10.0 上界。提高至 30.0 让优化器找到 BCE 最小值。
T_BOUNDS: tuple[float, float] = (0.1, 30.0)

# confidence 分桶边界——对齐 B1 验证器（b1_probability_calibration.py:63）
BUCKET_EDGES: list[float] = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

# Isotonic 每桶最少样本数（§2.2.8 D：防止稀有桶过拟合）——仅用于日志分桶
MIN_BUCKET_SAMPLES: int = 5

# Isotonic 原始数据 fit 所需的最少唯一 confidence 值（防止退化拟合）
# 5 桶预分桶仅产生 3-4 个拟合点（局部修正过粗）；直接在原始 (confidence, occurred)
# 对上 fit IsotonicRegression（PAVA 单调性约束 = 自带正则化），保留全部分辨率。
MIN_UNIQUE_FOR_FIT: int = 5

# 降级阈值（§2.2.10）
LEVEL1_MIN_SAMPLES: int = 50  # ≥50 → 正常 fit Stage 1 + Stage 2
LEVEL2_MIN_SAMPLES: int = 20  # ≥20 → 只 fit Stage 1

# forward_days 默认值——继承 B1 验证器（b1_probability_calibration.py:60）
DEFAULT_FORWARD_DAYS: int = 20

# 态平均收益 |mean| < 此值视为无明确方向（b1_probability_calibration.py:61）
MIN_RETURN_THRESHOLD: float = 0.005

# IS 尾部裁剪倍数（§2.2.9 防泄漏 #1：forward_days * 1.5 天余量）
IS_TRIM_MULTIPLIER: float = 1.5


class CalibrationError(ZephyrBaseError):
    """ZA-REGIME-0024: 校准器错误（数据不足/拟合失败/序列化异常）。"""

    error_code = "ZA-REGIME-0024"


class DegradationLevel(Enum):
    """校准器降级级别（§2.2.10）。"""

    LEVEL_1 = 1  # n≥50: 正常 fit Stage 1 + Stage 2
    LEVEL_2 = 2  # 20≤n<50: 只 fit Stage 1（跳过 Isotonic）
    LEVEL_3 = 3  # n<20: 回退上季度校准器
    LEVEL_4 = 4  # n<20 + 无上季度: T=1.0 不校准


@dataclass(frozen=True)
class CalibrationResult:
    """校准器 fit 结果（含降级信息）。"""

    level: DegradationLevel
    n_samples: int
    T: float | None  # Stage 1 温度参数（None=未 fit Stage 1）
    isotonic_points: tuple[tuple[float, float], ...] | None  # Stage 2 拟合点
    summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level.value,
            "n_samples": self.n_samples,
            "T": round(self.T, 6) if self.T is not None else None,
            "isotonic_points": (
                [(round(x, 6), round(y, 6)) for x, y in self.isotonic_points] if self.isotonic_points else None
            ),
            "summary": self.summary,
        }


# ── Calibrator 基类 ────────────────────────────────────────────────


class Calibrator(ABC):
    """可插拔校准器接口（§2.2.5 可升级架构）。

    Stage 1 可插拔：TemperatureCalibrator（当前）/ SMARTCalibrator（未来 v2）
    Stage 2 固定：IsotonicCalibrator

    子类实现 fit(X, occurred) + transform(X)。
    X 的语义由子类决定：Stage 1 接收 log_proba，Stage 2 接收 confidence。
    """

    @abstractmethod
    def fit(self, X: np.ndarray, occurred: np.ndarray) -> None:
        """从 IS 数据拟合校准参数。"""

    @abstractmethod
    def transform(self, X: np.ndarray) -> np.ndarray:
        """应用校准，返回校准后 confidence (N,)。"""

    def to_dict(self) -> dict[str, Any]:
        """序列化校准参数（持久化用）。"""
        return {"type": self.__class__.__name__}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Calibrator:
        """反序列化校准参数。"""
        raise NotImplementedError(f"{cls.__name__} 未实现 from_dict")


# ── Stage 1: TemperatureCalibrator ─────────────────────────────────


class TemperatureCalibrator(Calibrator):
    """Stage 1: Temperature Scaling（全局降温）。

    softmax(log_proba / T)，T>1 降温（摊平分布，缓解过度自信）。
    T 从 IS 数据最小化二元交叉熵学习（§2.2.8 B / §2.2.9 Bug #3 修正）。

    ⚠️ T=1.0 → 不校准（identity）。scipy 不可用时无法优化 T，保持初始值。
    """

    def __init__(self, T: float = 1.0) -> None:
        self.T = float(T)

    def fit(self, X: np.ndarray, occurred: np.ndarray) -> None:
        """从 IS 数据学习 T——最小化二元交叉熵。

        Args:
            X: (N, n_states) HMM 对数后验概率矩阵（log_proba）。
            occurred: (N,) 二值标签（1=预测方向正确）。
        """
        log_proba = np.asarray(X, dtype=float)
        occurred_arr = np.asarray(occurred, dtype=float)

        if log_proba.ndim != 2:
            raise CalibrationError(f"TemperatureCalibrator.fit: log_proba 须 2D (N, n_states)，实际 {log_proba.ndim}D")
        if len(log_proba) != len(occurred_arr):
            raise CalibrationError(f"样本数不匹配: log_proba={len(log_proba)}, occurred={len(occurred_arr)}")
        if len(log_proba) < 2:
            _logger.warning("TemperatureCalibrator: 样本不足 %d，保持 T=%.3f", len(log_proba), self.T)
            return

        if minimize_scalar is None:
            _logger.warning("scipy 不可用，TemperatureCalibrator 无法优化 T，保持 T=%.3f", self.T)
            return

        # 边界情况：occurred 全 0 或全 1 → BCE 退化为边界，T 优化无意义
        unique = np.unique(occurred_arr)
        if len(unique) < 2:
            _logger.warning(
                "TemperatureCalibrator: occurred 全 %.0f，无法优化 T，保持 T=%.3f",
                unique[0] if len(unique) > 0 else -1,
                self.T,
            )
            return

        self.T = self._optimize_T(log_proba, occurred_arr)
        _logger.info("TemperatureCalibrator: T=%.4f (n=%d)", self.T, len(log_proba))

    def transform(self, X: np.ndarray) -> np.ndarray:
        """应用温度缩放，返回校准后 confidence = max(softmax(log_proba/T))。

        Args:
            X: (N, n_states) log_proba 矩阵，或 (n_states,) 单样本。

        Returns:
            (N,) 校准后 confidence。
        """
        proba = self.transform_proba(X)
        return proba.max(axis=1)

    def transform_proba(self, X: np.ndarray) -> np.ndarray:
        """应用温度缩放，返回完整校准概率矩阵。

        softmax(log_proba / T) ≡ P^(1/T) / ΣP^(1/T)
        数值稳定实现：log-sum-exp 减最大值。
        """
        log_proba = np.asarray(X, dtype=float)
        if log_proba.ndim == 1:
            log_proba = log_proba.reshape(1, -1)
        if self.T == 1.0:
            # T=1 短路：直接 exp(log_proba)（已是后验概率）
            return np.exp(log_proba)
        scaled = log_proba / self.T
        log_softmax = scaled - np.logaddexp.reduce(scaled, axis=1, keepdims=True)
        return np.exp(log_softmax)

    def to_dict(self) -> dict[str, Any]:
        return {"type": "TemperatureCalibrator", "T": round(self.T, 6)}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TemperatureCalibrator:
        return cls(T=float(d["T"]))

    # ── 内部 ──────────────────────────────────────────────────────

    @staticmethod
    def _optimize_T(log_proba: np.ndarray, occurred: np.ndarray) -> float:
        """scipy.optimize.minimize_scalar 求 BCE 最小化的 T（§2.2.8 B 修正版）。"""

        def binary_cross_entropy(T: float) -> float:
            scaled = log_proba / T
            log_softmax = scaled - np.logaddexp.reduce(scaled, axis=1, keepdims=True)
            proba = np.exp(log_softmax)
            calibrated_confidence = proba.max(axis=1)
            eps = 1e-8
            return float(
                -np.mean(
                    occurred * np.log(calibrated_confidence + eps)
                    + (1.0 - occurred) * np.log(1.0 - calibrated_confidence + eps)
                )
            )

        result = minimize_scalar(binary_cross_entropy, bounds=T_BOUNDS, method="bounded")
        return float(result.x)


# ── Stage 2: IsotonicCalibrator ────────────────────────────────────


class IsotonicCalibrator(Calibrator):
    """Stage 2: Isotonic Regression（局部修正）。

    直接在原始 (confidence, occurred) 对上 fit IsotonicRegression（PAVA 算法），
    无需预分桶。PAVA 的单调性约束自带正则化，避免 5 桶预分桶导致的信息损失
    （预分桶仅产生 3-4 个拟合点，局部修正过粗）。分桶点仅用于日志可观测性。

    亦用于 overlay 态 confidence 校准：HMM 基态走 Stage 1(Temperature)+Stage 2，
    overlay 态（r10-r12）直接走 Stage 2（输入 merged max(P) confidence）。

    降级：sklearn 不可用 / 唯一值不足 / 拟合失败 → passthrough。
    """

    def __init__(self) -> None:
        self._x_thresh: np.ndarray | None = None  # isotonic x 断点
        self._y_thresh: np.ndarray | None = None  # isotonic y 断点（单调非递减）
        self._fit_points: tuple[tuple[float, float], ...] = ()  # 分桶点（日志用）

    def fit(self, X: np.ndarray, occurred: np.ndarray) -> None:
        """在原始 (confidence, occurred) 上 fit IsotonicRegression。

        PAVA（Pool Adjacent Violators Algorithm）保证单调性，自带正则化——
        无需预分桶，保留全部分辨率。

        Args:
            X: (N,) confidence 值（Stage 1 输出，或 overlay merged max(P)）。
            occurred: (N,) 二值标签。
        """
        confidences = np.asarray(X, dtype=float).ravel()
        occurred_arr = np.asarray(occurred, dtype=float).ravel()

        if len(confidences) != len(occurred_arr):
            raise CalibrationError(
                f"IsotonicCalibrator: 样本数不匹配 confidence={len(confidences)}, occurred={len(occurred_arr)}"
            )

        if IsotonicRegression is None:
            _logger.warning("sklearn 不可用，IsotonicCalibrator 降级 passthrough")
            return

        if len(confidences) < 2:
            _logger.warning("IsotonicCalibrator: 样本不足 %d，降级 passthrough", len(confidences))
            return

        # 唯一 confidence 值不足 → 退化（无法拟合有意义的单调映射）
        unique_count = int(np.unique(confidences).size)
        if unique_count < MIN_UNIQUE_FOR_FIT:
            _logger.warning(
                "IsotonicCalibrator: 唯一 confidence 值 %d < %d，降级 passthrough",
                unique_count,
                MIN_UNIQUE_FOR_FIT,
            )
            return

        # 直接在原始数据上 fit（PAVA 单调性约束 = 自带正则化）
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        iso.fit(confidences, occurred_arr)

        # 提取 thresholds 用于 transform + 序列化
        # sklearn ≥1.0: X_thresholds_/y_thresholds_; <1.0: X_/y_
        x_thresh = getattr(iso, "X_thresholds_", getattr(iso, "X_", None))
        y_thresh = getattr(iso, "y_thresholds_", getattr(iso, "y_", None))
        if x_thresh is None or len(x_thresh) < 2:
            _logger.warning("IsotonicCalibrator: 拟合后 thresholds 不足，降级 passthrough")
            return

        self._x_thresh = np.asarray(x_thresh, dtype=float)
        self._y_thresh = np.asarray(y_thresh, dtype=float)

        # 分桶点（日志可观测性，不参与拟合）
        self._fit_points = tuple(self._bucketize(confidences, occurred_arr))

        _logger.info(
            "IsotonicCalibrator: 原始数据 fit (n=%d, %d thresholds), 分桶点 %s",
            len(confidences),
            len(self._x_thresh),
            [(round(x, 3), round(y, 3)) for x, y in self._fit_points],
        )

    def transform(self, X: np.ndarray) -> np.ndarray:
        """应用 isotonic 映射。未 fit 时 passthrough。

        np.interp 线性插值 + 越界 clip（等价于 sklearn IsotonicRegression.predict）。
        """
        confidences = np.asarray(X, dtype=float).ravel()
        if self._x_thresh is None:
            return confidences  # passthrough
        return np.clip(
            np.interp(confidences, self._x_thresh, self._y_thresh),
            0.0,
            1.0,
        )

    def to_dict(self) -> dict[str, Any]:
        if self._x_thresh is not None:
            return {
                "type": "IsotonicCalibrator",
                "x_thresholds": [round(float(x), 6) for x in self._x_thresh],
                "y_thresholds": [round(float(y), 6) for y in self._y_thresh],
                # 分桶点（日志用 + backward compat）
                "points": [(round(x, 6), round(y, 6)) for x, y in self._fit_points],
            }
        return {"type": "IsotonicCalibrator", "points": []}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> IsotonicCalibrator:
        cal = cls()
        # 新格式：x_thresholds / y_thresholds（原始 PAVA 断点）
        x = d.get("x_thresholds")
        y = d.get("y_thresholds")
        if x and y and len(x) >= 2:
            cal._x_thresh = np.array(x, dtype=float)
            cal._y_thresh = np.array(y, dtype=float)
            cal._fit_points = tuple((float(xi), float(yi)) for xi, yi in zip(x, y, strict=False))
            return cal
        # 旧格式：points（binned means）—— 直接用作插值断点
        pts = d.get("points") or []
        if len(pts) >= 2:
            cal._x_thresh = np.array([p[0] for p in pts], dtype=float)
            cal._y_thresh = np.array([p[1] for p in pts], dtype=float)
            cal._fit_points = tuple((float(xi), float(yi)) for xi, yi in pts)
        return cal

    # ── 内部 ──────────────────────────────────────────────────────

    @staticmethod
    def _bucketize(confidences: np.ndarray, occurred: np.ndarray) -> list[tuple[float, float]]:
        """分桶对齐 B1 的 BUCKET_EDGES，每桶算 (mean_confidence, mean_occurred)。

        仅用于日志可观测性，不参与 isotonic 拟合。
        每桶 < MIN_BUCKET_SAMPLES 时跳过。
        """
        bucket_idx = np.digitize(confidences, BUCKET_EDGES[1:-1])
        points: list[tuple[float, float]] = []
        for i in range(len(BUCKET_EDGES) - 1):
            mask = bucket_idx == i
            count = int(mask.sum())
            if count < MIN_BUCKET_SAMPLES:
                continue
            points.append((float(confidences[mask].mean()), float(occurred[mask].mean())))
        return points


# ── TwoStageCalibrator（串联 Stage 1 → Stage 2）────────────────────


class TwoStageCalibrator:
    """两阶段串联校准器（§2.2.4）。

    Stage 1 (Temperature) → Stage 2 (Isotonic) → 校准 confidence。
    Stage 2 可为 None（Level 2 降级时跳过 Isotonic）。

    Usage::

        calibrator = TwoStageCalibrator(
            stage1=TemperatureCalibrator(),
            stage2=IsotonicCalibrator(),
        )
        calibrator.fit(log_proba_is, occurred_is)
        confidence_calibrated = calibrator.transform(log_proba_oos)
    """

    def __init__(
        self,
        stage1: TemperatureCalibrator | None,
        stage2: IsotonicCalibrator | None,
    ) -> None:
        self.stage1 = stage1
        self.stage2 = stage2

    def fit(self, log_proba: np.ndarray, occurred: np.ndarray) -> None:
        """串联 fit：Stage 1 先 fit，Stage 2 在 Stage 1 输出上 fit。"""
        if self.stage1 is None:
            raise CalibrationError("TwoStageCalibrator: stage1 为 None")
        self.stage1.fit(log_proba, occurred)
        if self.stage2 is not None:
            mid_confidence = self.stage1.transform(log_proba)
            self.stage2.fit(mid_confidence, occurred)

    def transform(self, log_proba: np.ndarray) -> np.ndarray:
        """串联 transform：log_proba → Stage 1 → Stage 2 → 校准 confidence。"""
        if self.stage1 is None:
            # 极端降级：无 Stage 1，返回 max(exp(log_proba)) 作为 confidence
            proba = np.exp(np.asarray(log_proba, dtype=float))
            if proba.ndim == 1:
                proba = proba.reshape(1, -1)
            return proba.max(axis=1)
        mid = self.stage1.transform(log_proba)
        if self.stage2 is not None:
            return self.stage2.transform(mid)
        return mid

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage1": self.stage1.to_dict() if self.stage1 else None,
            "stage2": self.stage2.to_dict() if self.stage2 else None,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TwoStageCalibrator:
        stage1 = None
        stage2 = None
        s1 = d.get("stage1")
        if s1:
            stage1 = TemperatureCalibrator.from_dict(s1)
        s2 = d.get("stage2")
        if s2:
            stage2 = IsotonicCalibrator.from_dict(s2)
        return cls(stage1=stage1, stage2=stage2)


# ── 四级降级 fit ────────────────────────────────────────────────────


def fit_calibrator_with_fallback(
    log_proba: np.ndarray,
    occurred: np.ndarray,
    prev_calibrator: TwoStageCalibrator | None = None,
) -> tuple[TwoStageCalibrator, CalibrationResult]:
    """四级降级 fit（§2.2.10）。

    Level 1 (n≥50): 正常 fit Stage 1 + Stage 2
    Level 2 (20≤n<50): 只 fit Stage 1（跳过 Isotonic 防过拟合）
    Level 3 (n<20): 回退上季度校准器
    Level 4 (n<20 + 无上季度): T=1.0 不校准

    Args:
        log_proba: (N, n_states) HMM 对数后验概率。
        occurred: (N,) 二值标签。
        prev_calibrator: 上季度校准器（Level 3 回退用）。

    Returns:
        (calibrator, result): 校准器 + 降级结果（含级别/样本数/T/summary）。
    """
    log_proba = np.asarray(log_proba, dtype=float)
    occurred_arr = np.asarray(occurred, dtype=float)
    n_samples = len(occurred_arr)

    if log_proba.ndim == 1:
        log_proba = log_proba.reshape(1, -1)

    # ── Level 1：样本 ≥ 50 → 正常 fit Stage 1 + Stage 2 ──
    if n_samples >= LEVEL1_MIN_SAMPLES:
        calibrator = TwoStageCalibrator(
            stage1=TemperatureCalibrator(),
            stage2=IsotonicCalibrator(),
        )
        calibrator.fit(log_proba, occurred_arr)
        T = calibrator.stage1.T if calibrator.stage1 else None
        iso_points = (
            calibrator.stage2._fit_points  # noqa: SLF001
            if calibrator.stage2 and calibrator.stage2._x_thresh is not None  # noqa: SLF001
            else None
        )
        result = CalibrationResult(
            level=DegradationLevel.LEVEL_1,
            n_samples=n_samples,
            T=T,
            isotonic_points=iso_points,
            summary=f"Level 1: 正常 fit (n={n_samples}, T={T:.4f})",
        )
        _logger.info("校准器 %s", result.summary)
        return calibrator, result

    # ── Level 2：20 ≤ 样本 < 50 → 只 fit Stage 1 ──
    if n_samples >= LEVEL2_MIN_SAMPLES:
        calibrator = TwoStageCalibrator(
            stage1=TemperatureCalibrator(),
            stage2=None,  # 跳过 Isotonic 防过拟合
        )
        calibrator.fit(log_proba, occurred_arr)
        T = calibrator.stage1.T if calibrator.stage1 else None
        result = CalibrationResult(
            level=DegradationLevel.LEVEL_2,
            n_samples=n_samples,
            T=T,
            isotonic_points=None,
            summary=f"Level 2: 只 fit Stage 1 (n={n_samples} < {LEVEL1_MIN_SAMPLES}, T={T:.4f})",
        )
        _logger.warning("校准器 %s", result.summary)
        return calibrator, result

    # ── Level 3：样本 < 20 → 回退上季度校准器 ──
    if prev_calibrator is not None:
        result = CalibrationResult(
            level=DegradationLevel.LEVEL_3,
            n_samples=n_samples,
            T=None,
            isotonic_points=None,
            summary=f"Level 3: 样本不足 (n={n_samples} < {LEVEL2_MIN_SAMPLES})，回退上季度校准器",
        )
        _logger.warning("校准器 %s", result.summary)
        return prev_calibrator, result

    # ── Level 4：无上季度校准器 → T=1.0 不校准 ──
    calibrator = TwoStageCalibrator(
        stage1=TemperatureCalibrator(T=1.0),  # T=1.0 = identity
        stage2=None,
    )
    result = CalibrationResult(
        level=DegradationLevel.LEVEL_4,
        n_samples=n_samples,
        T=1.0,
        isotonic_points=None,
        summary=f"Level 4: 样本不足且无上季度校准器 (n={n_samples})，T=1.0 不校准",
    )
    _logger.warning("校准器 %s", result.summary)
    return calibrator, result


# ── PIT 防泄漏 occurred 标签计算 ────────────────────────────────────


def compute_occurred_pit(
    log_proba: np.ndarray,
    timestamps: pd.DatetimeIndex | list[pd.Timestamp],
    close: pd.Series,
    forward_days: int = DEFAULT_FORWARD_DAYS,
    min_return_threshold: float = MIN_RETURN_THRESHOLD,
) -> tuple[np.ndarray, np.ndarray]:
    """PIT 安全的 occurred 标签计算（§2.2.9 防泄漏 #1 #2）。

    流程：
      1. dominant_state = argmax(log_proba)（HMM 预测的主导态）
      2. forward_return = close.shift(-forward_days) / close - 1
      3. regime_directions = sign(mean_forward_return per state)——**只用 IS 数据**
      4. occurred = 1 if (方向匹配) else 0
      5. 过滤无 forward_return 或无明确方向的样本

    ⚠️ 防泄漏 #1：调用方须确保 close 已裁剪到 safe_end（train_end - forward_days * 1.5），
       使所有 forward_return 完全在 IS 范围内。本函数不重复裁剪——裁剪是调用方职责。
    ⚠️ 防泄漏 #2：regime_directions 只用传入的 IS 数据推断，不看 OOS。

    Args:
        log_proba: (T, n_states) HMM 对数后验概率矩阵。
        timestamps: T 个时间戳（与 log_proba 行对齐）。
        close: 收盘价序列（pd.Series, index=日期）。调用方须裁剪到 IS 安全范围。
        forward_days: 后续收益天数（默认 20）。
        min_return_threshold: 态平均收益 |mean| < 此值视为无明确方向。

    Returns:
        (log_proba_valid, occurred_valid): 过滤后的 log_proba + 二值 occurred 标签。
        无 forward_return 或无明确方向的样本被过滤。
    """
    log_proba = np.asarray(log_proba, dtype=float)
    if log_proba.ndim == 1:
        log_proba = log_proba.reshape(1, -1)

    ts_list = list(timestamps)
    if len(ts_list) != log_proba.shape[0]:
        raise CalibrationError(
            f"compute_occurred_pit: timestamps ({len(ts_list)}) 与 log_proba 行数 ({log_proba.shape[0]}) 不匹配"
        )

    # 1. dominant state per timestamp
    dominant = log_proba.argmax(axis=1)  # (T,) int

    # 2. forward returns（复用 B1 的逻辑）
    forward_returns = close.shift(-forward_days) / close - 1.0

    # 3. 按 state 分组，PIT 推断方向（只用 IS 数据）
    state_returns: dict[int, list[float]] = {}
    for i, ts in enumerate(ts_list):
        if ts not in forward_returns.index:
            continue
        fr = forward_returns.loc[ts]
        if pd.isna(fr):
            continue
        state = int(dominant[i])
        state_returns.setdefault(state, []).append(float(fr))

    state_directions: dict[int, bool] = {}  # state → True(涨) / False(跌)
    for state, rets in state_returns.items():
        mean_r = float(np.mean(rets))
        if abs(mean_r) < min_return_threshold:
            continue  # 无明确方向
        state_directions[state] = mean_r > 0

    # 4. 标记 occurred
    valid_idx: list[int] = []
    occurred: list[int] = []
    for i, ts in enumerate(ts_list):
        state = int(dominant[i])
        if state not in state_directions:
            continue  # 该态无明确方向
        if ts not in forward_returns.index:
            continue
        fr = forward_returns.loc[ts]
        if pd.isna(fr):
            continue
        expected_pos = state_directions[state]
        actual_pos = float(fr) > 0
        occurred.append(1 if (expected_pos == actual_pos) else 0)
        valid_idx.append(i)

    if not valid_idx:
        _logger.warning("compute_occurred_pit: 无有效样本（全部过滤）")
        return np.empty((0, log_proba.shape[1])), np.array([], dtype=int)

    return log_proba[valid_idx], np.array(occurred, dtype=int)


def trim_is_for_pit(
    features: pd.DataFrame,
    close: pd.Series,
    train_start: pd.Timestamp,
    train_end: pd.Timestamp,
    forward_days: int = DEFAULT_FORWARD_DAYS,
) -> tuple[pd.DataFrame, pd.Series]:
    """IS 数据尾部裁剪（§2.2.9 防泄漏 #1）。

    裁剪 train_end 前 forward_days * 1.5 天，确保所有 forward_return 完全在 IS 范围内。

    Args:
        features: 全历史特征 DataFrame（取 IS 段并裁剪尾部）。
        close: 收盘价序列（取 IS 段并裁剪尾部）。
        train_start: IS 训练窗口起点。
        train_end: IS 训练窗口终点（季度末）。
        forward_days: 后续收益天数。

    Returns:
        (features_safe, close_safe): 裁剪后的 IS 特征 + 收盘价。
    """
    safe_end = train_end - pd.Timedelta(days=int(forward_days * IS_TRIM_MULTIPLIER))
    features_safe = features.loc[train_start:safe_end]
    close_safe = close.loc[train_start:safe_end]
    return features_safe, close_safe


# ── 持久化 ──────────────────────────────────────────────────────────


def save_calibration(
    calibrator: TwoStageCalibrator,
    result: CalibrationResult,
    quarter: str,
    output_dir: str | Path = "runtime/calibration",
) -> Path:
    """保存校准参数到 JSON（§2.2.8 E 持久化机制）。

    Args:
        calibrator: 校准器实例。
        result: 校准结果（含降级信息）。
        quarter: 季度标识（如 "2024Q3"）。
        output_dir: 输出目录。

    Returns:
        保存的文件路径。
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = {
        "quarter": quarter,
        "calibrator": calibrator.to_dict(),
        "result": result.to_dict(),
    }
    path = out_dir / f"calibration_{quarter}.json"
    path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    _logger.info("校准参数保存到 %s", path)
    return path


def load_calibration(
    quarter: str,
    input_dir: str | Path = "runtime/calibration",
) -> TwoStageCalibrator | None:
    """从 JSON 加载校准参数。

    Args:
        quarter: 季度标识。
        input_dir: 输入目录。

    Returns:
        校准器实例，文件不存在返回 None。
    """
    path = Path(input_dir) / f"calibration_{quarter}.json"
    if not path.exists():
        return None
    artifact = json.loads(path.read_text(encoding="utf-8"))
    return TwoStageCalibrator.from_dict(artifact["calibrator"])


__all__ = [
    "BUCKET_EDGES",
    "MIN_UNIQUE_FOR_FIT",
    "T_BOUNDS",
    "CalibrationError",
    "CalibrationResult",
    "Calibrator",
    "DegradationLevel",
    "IsotonicCalibrator",
    "TemperatureCalibrator",
    "TwoStageCalibrator",
    "compute_occurred_pit",
    "fit_calibrator_with_fallback",
    "load_calibration",
    "save_calibration",
    "trim_is_for_pit",
]
