# [BLUEPRINT] MOD-ML-005 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.adversarial_robustness_validator
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] numpy
# [CONSUMERS] （模型晋升前鲁棒性门禁消费方）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 预测函数经注入（本模块不持有模型）；同 seed 结果可复现；只评估不修改模型
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AdversarialValidationError(ZA-MLT-0009)——空样本/非有限值/非法扰动档位/标签长度不符
# [TESTS] tests/ml_train/test_adversarial_robustness_validator.py
# [A_module] module_id=MOD-ML-005 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""对抗鲁棒性验证器（MOD-ML-005）——轻量可单测实现。

对注入的 predict_fn 施加高斯噪声扰动（多档 epsilon × n_trials 蒙特卡洛），
度量预测漂移（mean L2 shift / max shift）；供给标签时同时报告扰动下准确率
降级（decision_threshold 符号化判定）。真对抗样本生成（FGSM/PGD 需梯度）
属模型侧能力，本模块做黑盒噪声鲁棒性基线。
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Final

import numpy as np

__all__: Final = [
    "AdversarialValidationError",
    "RobustnessPoint",
    "RobustnessReport",
    "validate_robustness",
]


class AdversarialValidationError(Exception):
    """ZA-MLT-0009: 对抗鲁棒性验证输入非法。"""

    error_code = "ZA-MLT-0009"


@dataclass(frozen=True)
class RobustnessPoint:
    """单档扰动强度下的鲁棒性度量。"""

    epsilon: float
    mean_shift: float
    max_shift: float
    accuracy: float | None


@dataclass(frozen=True)
class RobustnessReport:
    """鲁棒性验证报告。"""

    n_samples: int
    n_trials: int
    points: tuple[RobustnessPoint, ...]
    baseline_accuracy: float | None = field(default=None)


def validate_robustness(
    predict_fn: Callable[[np.ndarray], np.ndarray],
    samples: np.ndarray,
    *,
    labels: np.ndarray | None = None,
    epsilons: tuple[float, ...] = (0.01, 0.05, 0.1),
    n_trials: int = 8,
    seed: int = 42,
    decision_threshold: float = 0.0,
) -> RobustnessReport:
    """黑盒噪声鲁棒性验证。输入非法 → ZA-MLT-0009。"""
    x = np.asarray(samples, dtype=float)
    if x.size == 0:
        raise AdversarialValidationError("样本集为空")
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    if not np.all(np.isfinite(x)):
        raise AdversarialValidationError("样本含非有限值")
    if not epsilons or any(e < 0.0 or not np.isfinite(e) for e in epsilons):
        raise AdversarialValidationError(f"扰动档位非法: {epsilons}")
    if n_trials <= 0:
        raise AdversarialValidationError(f"n_trials 必须为正: {n_trials}")
    y = None
    if labels is not None:
        y = np.asarray(labels, dtype=float).ravel()
        if y.shape[0] != x.shape[0]:
            raise AdversarialValidationError(f"标签长度不符: {y.shape[0]} vs {x.shape[0]}")

    baseline = np.asarray(predict_fn(x), dtype=float).ravel()
    baseline_accuracy: float | None = None
    if y is not None:
        baseline_accuracy = float(np.mean((baseline > decision_threshold) == (y > decision_threshold)))

    rng = np.random.default_rng(seed)
    points: list[RobustnessPoint] = []
    for eps in epsilons:
        shifts: list[float] = []
        accs: list[float] = []
        for _ in range(n_trials):
            noise = rng.normal(0.0, eps, size=x.shape) if eps > 0 else np.zeros_like(x)
            perturbed = np.asarray(predict_fn(x + noise), dtype=float).ravel()
            shifts.extend(np.abs(perturbed - baseline).tolist())
            if y is not None:
                accs.append(float(np.mean((perturbed > decision_threshold) == (y > decision_threshold))))
        points.append(
            RobustnessPoint(
                epsilon=float(eps),
                mean_shift=float(np.mean(shifts)),
                max_shift=float(np.max(shifts)),
                accuracy=(float(np.mean(accs)) if accs else None),
            )
        )

    return RobustnessReport(
        n_samples=int(x.shape[0]),
        n_trials=n_trials,
        points=tuple(points),
        baseline_accuracy=baseline_accuracy,
    )
