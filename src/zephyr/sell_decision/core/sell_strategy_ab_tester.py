# [BLUEPRINT] MOD-SELL-011 | docs/03_modules/MOD-SELL-011/
# [MODULE] zephyr.sell_decision.core.sell_strategy_ab_tester
# [DOMAIN] D_SELL_DECISION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 策略生命周期管理(B胜出→A退役,宪章§1.1自迭代) ; MOD-SELL-010(衰退后替换验证)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 双样本z检验(正态近似); 显著且diff>0→ADOPT_B,显著且diff<0→KEEP_A,否则INCONCLUSIVE; 样本不足一律INCONCLUSIVE+预警(防小样本过拟合决策,宪章§4.2 B-009); 纯函数可单测
# [MODIFY-GUARD] docs/03_modules/MOD-SELL-011/
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidABTestInputError(ZA-SELL-0026)
# [TESTS] tests/sell_decision/test_sell_strategy_ab_tester.py
# [A_module] module_id=MOD-SELL-011 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Sell Strategy AB Tester — 卖出策略 AB 测试 (MOD-SELL-011)

策略生命周期闭环（宪章 §1.1：A/B 对比→B 胜出→A 自动退役）的卖出域
统计判定器：比较两个卖出策略变体的逐笔结果样本（如同期超额收益/
卖出后 N 日相对兑现），双样本 z 检验（正态近似）：

    z = (mean_B − mean_A) / sqrt(var_A/n_A + var_B/n_B)

判定：
  - |z| > z_{1−α/2} 且 diff>0 → ADOPT_B（B 显著优，建议替换）；
  - |z| > z_{1−α/2} 且 diff<0 → KEEP_A（A 显著优，保留现状）；
  - 不显著或样本不足 → INCONCLUSIVE（不换——
    样本不足时换策略=过拟合决策，宪章 §4.2 B-009 精神）。

与具体策略内容零耦合：只吃两组 outcome 数字，不认识策略逻辑。

纪律：纯函数、无 IO。
Version: 1.0.0
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ABDecision",
    "ABTestReport",
    "InvalidABTestInputError",
    "evaluate_ab_test",
]

_DEFAULT_MIN_SAMPLES: Final = 30
_DEFAULT_ALPHA: Final = 0.05
# 常见 α → 双侧临界值（避免 scipy 依赖；未知 α 用 1.96 兜底近似）
_Z_CRIT_TABLE: Final = {0.10: 1.645, 0.05: 1.960, 0.01: 2.576}


class ABDecision(str, Enum):
    """AB 测试判定。"""

    ADOPT_B = "ADOPT_B"  # B 显著优 → 建议替换
    KEEP_A = "KEEP_A"  # A 显著优 → 保留
    INCONCLUSIVE = "INCONCLUSIVE"  # 不显著/样本不足 → 不动


class InvalidABTestInputError(ZephyrBaseError):
    """AB 测试输入非法（空样本/非有限值/参数越界）。"""

    error_code = "ZA-SELL-0026"


@dataclass(frozen=True)
class ABTestReport:
    """AB 测试报告（frozen 不可变）。

    Attributes:
        n_a / n_b: 样本量
        mean_a / mean_b: 组均值
        diff: mean_b − mean_a
        z_statistic: z 统计量
        significant: 是否显著（|z| > 临界值）
        decision: 判定
        warnings: 预警（样本不足等）
    """

    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    diff: float
    z_statistic: float
    significant: bool
    decision: ABDecision
    warnings: tuple[str, ...] = field(default_factory=tuple)


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs)


def _variance(xs: Sequence[float], mean: float) -> float:
    """样本方差（ddof=1）；单样本返回 0（无离散信息）。"""
    if len(xs) < 2:
        return 0.0
    return sum((x - mean) ** 2 for x in xs) / (len(xs) - 1)


def evaluate_ab_test(
    a_outcomes: Sequence[float],
    b_outcomes: Sequence[float],
    *,
    min_samples: int = _DEFAULT_MIN_SAMPLES,
    alpha: float = _DEFAULT_ALPHA,
) -> ABTestReport:
    """卖出策略 AB 测试判定（纯函数）。

    Args:
        a_outcomes: A 组（现策略）逐笔结果
        b_outcomes: B 组（候选策略）逐笔结果
        min_samples: 每组最小样本量 ≥2（默认 30）
        alpha: 显著性水平 ∈(0,1)（默认 0.05，双侧）

    Returns:
        ABTestReport

    Raises:
        InvalidABTestInputError: 输入非法
    """
    if not a_outcomes or not b_outcomes:
        raise InvalidABTestInputError("A/B 两组样本均不可为空")
    for name, xs in (("A", a_outcomes), ("B", b_outcomes)):
        for x in xs:
            if not math.isfinite(x):
                raise InvalidABTestInputError(f"{name} 组含非有限值 outcome，got {x}")
    if min_samples < 2:
        raise InvalidABTestInputError(f"min_samples 非法（须 ≥2），got {min_samples}")
    if not math.isfinite(alpha) or not (0.0 < alpha < 1.0):
        raise InvalidABTestInputError(f"alpha 非法（须 ∈(0,1)），got {alpha}")

    n_a, n_b = len(a_outcomes), len(b_outcomes)
    mean_a, mean_b = _mean(a_outcomes), _mean(b_outcomes)
    diff = mean_b - mean_a

    var_a = _variance(a_outcomes, mean_a)
    var_b = _variance(b_outcomes, mean_b)
    se = math.sqrt(var_a / n_a + var_b / n_b)
    z = diff / se if se > 0.0 else (0.0 if diff == 0.0 else math.copysign(float("inf"), diff))

    z_crit = _Z_CRIT_TABLE.get(round(alpha, 2), 1.960)
    significant = abs(z) > z_crit

    warnings: list[str] = []
    sufficient = n_a >= min_samples and n_b >= min_samples
    if not sufficient:
        warnings.append(
            f"样本不足（n_a={n_a}, n_b={n_b} < min_samples={min_samples}），"
            "一律 INCONCLUSIVE（防小样本过拟合决策）"
        )
        significant = False

    if significant and diff > 0.0:
        decision = ABDecision.ADOPT_B
    elif significant and diff < 0.0:
        decision = ABDecision.KEEP_A
    else:
        decision = ABDecision.INCONCLUSIVE

    return ABTestReport(
        n_a=n_a,
        n_b=n_b,
        mean_a=mean_a,
        mean_b=mean_b,
        diff=diff,
        z_statistic=z,
        significant=significant,
        decision=decision,
        warnings=tuple(warnings),
    )
