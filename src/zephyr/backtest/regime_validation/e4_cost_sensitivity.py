# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §4.5 E4 / §5
# [MODULE] zephyr.backtest.regime_validation.e4_cost_sensitivity
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan Phase 4 E4
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯分析函数: 只消费既有成本网格回测产出的效果指标, 不重跑回测; 方向一致=全部效果同号且非零; 成本单位 bps; frozen 不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] E4CostSensitivityError(ZA-BT-0029)
# [TESTS] tests/backtest/test_e4_cost_sensitivity.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: points(各交易成本 bps 下的 Shrinkage 效果指标, 如 MaxDD 改善, 既有网格回测产物)
# I2: cost_range=[0,50]bps(§4.5 E4 设计网格 0/2/5/10/50bps)
# A1: analyze_cost_sensitivity(符号一致性检验 + 效果区间统计 + 网格覆盖度检查)
# O1: E4CostReport(direction / direction_consistent / passed + 覆盖度信息)
# [/ALGO_FLOW]
"""
D_BACKTEST — E4 交易成本敏感性 0-50bps 分析（11 号 memo §4.5 E4）。

纯分析函数：不重跑回测，只消费既有成本网格（§4.5 设计 0/2/5/10/50bps）
开/关对比回测产出的 Shrinkage 效果指标（如 MaxDD 改善），按
「0-50bps 范围内方向一致 → 稳健」判定。

依据: 11_regime_backtest_validation_plan §4.5 E4 / §5
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: points 参数
#   fields: 参数 points，类型注解 list[E4CostPoint]
#   code: e4_cost_sensitivity.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: cost_min 参数
#   fields: 参数 cost_min，类型注解 float
#   code: e4_cost_sensitivity.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: cost_max 参数
#   fields: 参数 cost_max，类型注解 float
#   code: e4_cost_sensitivity.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① analyze_cost_sensitivity
#   name_en: analyze_cost_sensitivity
#   intro: E4 主入口：0-50bps 成本网格下 Shrinkage 效果方向一致性判定。
#   desc: E4 主入口：0-50bps 成本网格下 Shrinkage 效果方向一致性判定。 Args: points: 各成本点效果（≥2 点），effect>0 表示该成本下节流仍有正…；源码 L111-L163
#   inputs: points cost_min cost_max
#   outputs: E4CostReport
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: E4CostReport
#   name_en: E4CostReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 人工审查; 11_regime_backtest_validation_plan Phase 4 E4
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)


class E4CostSensitivityError(ZephyrBaseError):
    """ZA-BT-0029: E4 成本敏感性分析错误（输入非法）。"""

    error_code = "ZA-BT-0029"


@dataclass(frozen=True)
class E4CostPoint:
    """单成本点效果——不可变。"""

    cost_bps: float  # 交易成本（bps）
    effect: float  # 该成本下的 Shrinkage 效果指标（如 MaxDD 改善幅度）


@dataclass(frozen=True)
class E4CostReport:
    """E4 成本敏感性报告——不可变。"""

    points: tuple[E4CostPoint, ...]  # 按 cost_bps 升序
    direction: int  # +1=全为正效果 / −1=全为负 / 0=不一致
    direction_consistent: bool
    min_effect: float
    max_effect: float
    covers_design_range: bool  # 网格是否覆盖 [cost_min, cost_max]
    passed: bool  # = direction_consistent（§4.5 E4 方向一致即稳健）
    summary: str


def analyze_cost_sensitivity(
    points: list[E4CostPoint],
    cost_min: float = 0.0,
    cost_max: float = 50.0,
) -> E4CostReport:
    """E4 主入口：0-50bps 成本网格下 Shrinkage 效果方向一致性判定。

    Args:
        points: 各成本点效果（≥2 点），effect>0 表示该成本下节流仍有正效果。
        cost_min / cost_max: 设计成本范围（§4.5 E4 = 0-50bps），仅做覆盖度检查。

    Returns:
        E4CostReport；passed = 全部效果同号且非零（方向一致）。

    Raises:
        E4CostSensitivityError: 点数<2 / 成本重复 / 值非有限 / cost_min≥cost_max。
    """
    if cost_min >= cost_max:
        raise E4CostSensitivityError(f"cost_min 需 < cost_max: {cost_min} vs {cost_max}")
    if len(points) < 2:
        raise E4CostSensitivityError(f"成本网格点数需 ≥2: {len(points)}")
    ordered = tuple(sorted(points, key=lambda p: p.cost_bps))
    costs = [p.cost_bps for p in ordered]
    if len(set(costs)) != len(costs):
        raise E4CostSensitivityError(f"成本点重复: {costs}")
    for p in ordered:
        if p.effect != p.effect or abs(p.effect) == float("inf"):
            raise E4CostSensitivityError(f"成本 {p.cost_bps}bps 的 effect 非有限: {p.effect}")

    effects = [p.effect for p in ordered]
    all_pos = all(e > 0 for e in effects)
    all_neg = all(e < 0 for e in effects)
    direction = 1 if all_pos else (-1 if all_neg else 0)
    consistent = direction != 0
    covers = costs[0] <= cost_min and costs[-1] >= cost_max
    summary = (
        f"E4 成本敏感性: {len(ordered)} 成本点 [{costs[0]:g},{costs[-1]:g}]bps, "
        f"效果区间 [{min(effects):+.4f},{max(effects):+.4f}], "
        f"方向={'一致为正' if direction > 0 else ('一致为负' if direction < 0 else '不一致')}"
        f"{'' if covers else f'（警告: 未覆盖设计范围 [{cost_min:g},{cost_max:g}]bps）'} → "
        f"{'稳健' if consistent else '不稳健'}"
    )
    _logger.info("E4 完成: %s", summary)
    return E4CostReport(
        points=ordered,
        direction=direction,
        direction_consistent=consistent,
        min_effect=min(effects),
        max_effect=max(effects),
        covers_design_range=covers,
        passed=consistent,
        summary=summary,
    )


__all__ = [
    "E4CostPoint",
    "E4CostReport",
    "E4CostSensitivityError",
    "analyze_cost_sensitivity",
]
