# [BLUEPRINT] MOD-SIG-044 | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/91_density_prediction.md §1
# [MODULE] zephyr.signal_ashare.conformal_predictor
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy
# [CONSUMERS] (待 BM-EXE-01 共形 VaR / 信号置信区间消费层)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 分位数指标 k=⌈(n+1)(1−α)⌉ 有限样本边际覆盖保证；rolling 变体无加权（slow unweighted，Phase 0 基线）；纯函数无副作用
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] α∉(0,1) / 校准集为空 → ValueError
# [TESTS] tests/signal_ashare/test_conformal_predictor.py
# [A_module] module_id=MOD-SIG-044 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# I1: 校准集 (预测值, 实际值) 序列 / 滚动残差流 / 密度 PDF 分位数
# A1: split-conformal 标准算法——非 conformity 分数 s_i=|y−ŷ|，q̂=第 ⌈(n+1)(1−α)⌉ 小值
# A2: rolling conformal——trailing window 无加权残差分位数（Phase 0 基线，慢而稳）
# A3: conformal_band_around_quantiles——PDF 分位数外裹 conformal 安全缓冲
# O1: PredictionInterval(lo, hi) / margin；empirical_coverage 覆盖率评估件
# [/ALGO_FLOW]
"""
共形预测器（BM-SEL-14，MOD-SIG-044）。

给预测区间加数学保证——不管分布长什么样，区间覆盖率有数学证明（分布无关、
有限样本边际覆盖）：校准集非 conformity 分数 s_i=|y_i−ŷ_i|，取第
⌈(n+1)(1−α)⌉ 小值为安全缓冲 q̂，区间 = ŷ ± q̂（split-conformal 标准算法，
Vovk et al.；目标覆盖率 1−α=95%）。

变体路线按 91 号 memo 裁定：Phase 0 基线 = slow unweighted rolling conformal
（Conformal Kelly 实证"慢而稳 conformal 胜过快而自适应"）——RollingConformal
Calibrator 即该基线：trailing window 无加权残差分位数，不加 EWMA/regime 权重
（RWC/TCP-RM 等加权变体登记 Phase 2 远期，MOD-SIG-052）。

与 BM-SEL-13 密度预测的衔接（91 号区间层设计）：PDF 分位数（2.5%/97.5%）外裹
conformal 安全缓冲 —— conformal_band_around_quantiles()。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: lower_q 参数
#   fields: 参数 lower_q，类型注解 float
#   code: conformal_predictor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: upper_q 参数
#   fields: 参数 upper_q，类型注解 float
#   code: conformal_predictor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: margin 参数
#   fields: 参数 margin，类型注解 float
#   code: conformal_predictor.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: lowers 参数
#   fields: 参数 lowers，类型注解 Iterable[float]
#   code: conformal_predictor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SplitConformalPredictor
#   name_en: SplitConformalPredictor
#   intro: split-conformal 标准预测器（一次性校准集）。
#   desc: split-conformal 标准预测器（一次性校准集）。；公共方法（定义序）: margin, fit, predict_interval；源码 L158-L194
#   inputs: alpha
#   outputs: 返回值
# - id: A2
#   name_zh: ② RollingConformalCalibrator
#   name_en: RollingConformalCalibrator
#   intro: slow unweighted rolling conformal（91 号 Phase 0 基线）。
#   desc: slow unweighted rolling conformal（91 号 Phase 0 基线）。 trailing window 无加权残差分位数——不加任何时间/regi…；公共方法（定义序）: update,…
#   inputs: window alpha min_samples
#   outputs: 返回值
# - id: A3
#   name_zh: ③ conformal_band_around_quantiles
#   name_en: conformal_band_around_quantiles
#   intro: PDF 分位数外裹 conformal 安全缓冲（91 号区间层设计）。
#   desc: PDF 分位数外裹 conformal 安全缓冲（91 号区间层设计）。 (lower_q − margin, upper_q + margin)。lower_q>upper_q…；源码 L248-L259
#   inputs: lower_q upper_q margin
#   outputs: tuple[float, float]
# - id: A4
#   name_zh: ④ empirical_coverage
#   name_en: empirical_coverage
#   intro: 区间集经验覆盖率（校准验证件：实测覆盖率 vs 名义 1−α）。
#   desc: 区间集经验覆盖率（校准验证件：实测覆盖率 vs 名义 1−α）。空输入 → ValueError。；源码 L262-L275
#   inputs: lowers uppers actuals
#   outputs: float
#   （注：A4 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: tuple[float, float]
#   name_en: tuple[float, float]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 BM-EXE-01 共形 VaR / 信号置信区间消费层)
# - id: O2
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: (待 BM-EXE-01 共形 VaR / 信号置信区间消费层)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Final, Iterable

import numpy as np

__all__: Final = [
    "PredictionInterval",
    "RollingConformalCalibrator",
    "SplitConformalPredictor",
    "conformal_band_around_quantiles",
    "empirical_coverage",
]


@dataclass(frozen=True)
class PredictionInterval:
    """共形预测区间（含中位点预测与覆盖参数留痕）。"""

    point: float  # 点预测
    lower: float  # 区间下界
    upper: float  # 区间上界
    alpha: float  # 目标显著性水平（覆盖率=1−α）
    margin: float  # 安全缓冲 q̂
    n_calibration: int  # 校准集样本数


def _validate_alpha(alpha: float) -> None:
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha 必须 ∈ (0,1): {alpha}")


def _conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    """split-conformal 分位数：第 k=⌈(n+1)(1−α)⌉ 小的非 conformity 分数。

    k> n 时退化为样本最大值的 +∞ 外推——工程口径取样本最大值并在调用方可见
    （n 太小给不出 1−α 保证时区间取最宽，保守方向）。
    """
    n = len(scores)
    k = int(np.ceil((n + 1) * (1.0 - alpha)))
    k = min(max(k, 1), n)
    return float(np.partition(scores, k - 1)[k - 1])


class SplitConformalPredictor:
    """split-conformal 标准预测器（一次性校准集）。"""

    def __init__(self, *, alpha: float = 0.05) -> None:
        _validate_alpha(alpha)
        self._alpha = alpha
        self._margin: float | None = None
        self._n_cal = 0

    @property
    def margin(self) -> float | None:
        return self._margin

    def fit(self, predictions: Iterable[float], actuals: Iterable[float]) -> SplitConformalPredictor:
        """校准：q̂ = 第 ⌈(n+1)(1−α)⌉ 小的 |y−ŷ|。长度不一致/空集 → ValueError。"""
        p = np.asarray(list(predictions), dtype=float)
        y = np.asarray(list(actuals), dtype=float)
        if p.shape != y.shape:
            raise ValueError(f"校准集长度不一致: {len(p)} vs {len(y)}")
        if len(p) == 0:
            raise ValueError("校准集为空")
        self._margin = _conformal_quantile(np.abs(y - p), self._alpha)
        self._n_cal = len(p)
        return self

    def predict_interval(self, point: float) -> PredictionInterval:
        """区间 = point ± q̂。未 fit → ValueError。"""
        if self._margin is None:
            raise ValueError("未 fit（校准集未提供）")
        return PredictionInterval(
            point=float(point),
            lower=float(point) - self._margin,
            upper=float(point) + self._margin,
            alpha=self._alpha,
            margin=self._margin,
            n_calibration=self._n_cal,
        )


class RollingConformalCalibrator:
    """slow unweighted rolling conformal（91 号 Phase 0 基线）。

    trailing window 无加权残差分位数——不加任何时间/regime 权重（加权变体
    RWC/TCP-RM 登记 MOD-SIG-052 Phase 2，实证裁定前不引入）。
    """

    def __init__(self, *, window: int = 250, alpha: float = 0.05, min_samples: int = 30) -> None:
        _validate_alpha(alpha)
        if window < 1:
            raise ValueError(f"window 必须 ≥1: {window}")
        if min_samples < 1:
            raise ValueError(f"min_samples 必须 ≥1: {min_samples}")
        self._window = window
        self._alpha = alpha
        self._min_samples = min_samples
        self._scores: deque[float] = deque(maxlen=window)

    def update(self, prediction: float, actual: float) -> None:
        """追加一对 (预测, 实际) 到滚动校准窗口。"""
        self._scores.append(abs(float(actual) - float(prediction)))

    @property
    def sample_count(self) -> int:
        return len(self._scores)

    def ready(self) -> bool:
        """窗口样本 ≥ min_samples 才可给出区间。"""
        return len(self._scores) >= self._min_samples

    def margin(self) -> float | None:
        """当前安全缓冲 q̂；样本不足返回 None（调用方走降级：无覆盖率保证区间）。"""
        if not self.ready():
            return None
        return _conformal_quantile(np.asarray(self._scores, dtype=float), self._alpha)

    def predict_interval(self, point: float) -> PredictionInterval | None:
        """区间 = point ± q̂；样本不足返回 None。"""
        m = self.margin()
        if m is None:
            return None
        return PredictionInterval(
            point=float(point),
            lower=float(point) - m,
            upper=float(point) + m,
            alpha=self._alpha,
            margin=m,
            n_calibration=len(self._scores),
        )


def conformal_band_around_quantiles(
    lower_q: float,
    upper_q: float,
    margin: float,
) -> tuple[float, float]:
    """PDF 分位数外裹 conformal 安全缓冲（91 号区间层设计）。

    (lower_q − margin, upper_q + margin)。lower_q>upper_q → ValueError（分位数倒挂）。
    """
    if lower_q > upper_q:
        raise ValueError(f"分位数倒挂: lower={lower_q} > upper={upper_q}")
    return (float(lower_q) - float(margin), float(upper_q) + float(margin))


def empirical_coverage(
    lowers: Iterable[float],
    uppers: Iterable[float],
    actuals: Iterable[float],
) -> float:
    """区间集经验覆盖率（校准验证件：实测覆盖率 vs 名义 1−α）。空输入 → ValueError。"""
    lo = np.asarray(list(lowers), dtype=float)
    hi = np.asarray(list(uppers), dtype=float)
    y = np.asarray(list(actuals), dtype=float)
    if not (lo.shape == hi.shape == y.shape):
        raise ValueError(f"区间/实际值长度不一致: {len(lo)}/{len(hi)}/{len(y)}")
    if len(y) == 0:
        raise ValueError("覆盖率评估输入为空")
    return float(((y >= lo) & (y <= hi)).mean())
