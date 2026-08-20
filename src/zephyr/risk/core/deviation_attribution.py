# [BLUEPRINT] MOD-RK-23 | docs/03_modules/_domain_risk/strategy_deviation_monitor/blueprint.md
# [MODULE] zephyr.risk.core.deviation_attribution
# [DOMAIN] D_RISK
# [DEPENDENCIES] stdlib; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RPT-009(周复盘"偏离与告警事件"段); MOD-RK-23(偏离告警触发后按需分解, 55号§6重评条件)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 四因子加性恒等: H-A+H-B+H-C+H-D==总偏差(残差定义保证); H-A~H-C 数据获取归调用方(本模块纯计算); 输入必须有限实数(NaN/inf 拒绝); 只读不发射事件不改策略状态
# [MODIFY-GUARD] 55_monitoring_review.md §3.4/§6
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDeviationDecompositionError(ZA-RK-0030)
# [TESTS] tests/risk/core/test_deviation_attribution.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: total_deviation(累计收益口径总偏差, 带符号) + execution_cost_drag(H-A 执行成本拖累) + timing_lag(H-B 时滞/未成交错过收益) + position_weight_pairs(H-C 输入: [(权重差, 标的区间收益)])
# F1: H-A 执行成本偏差——实盘滑点+费用相对回测假设的多付出成本(收益口径, 通常≤0)
# F2: H-B 时滞/未成交偏差——实盘未成交/延迟成交部分错过的区间收益
# F3: H-C 仓位权重偏差——Σ(w_live_i - w_backtest_i) × r_i(权重偏离×标的收益)
# F4: H-D 残差——total - (H-A+H-B+H-C)(未解释: 市场环境/噪声/口径差)
# O1: 四因子分解 dict + 加性不变量 PASS/FAIL + dominant_factor + 各因子占总偏差份额
# [/ALGO_FLOW]
"""D_RISK — 实盘 vs 回测偏离归因分解 H-A~D 四因子（55 号 §6 暂缓项施工）。

55 号 §6："偏离度量两口径之外加归因分解（H-A~D 四因子）——battle_map 明示为
设计态，先总值报警器够用；重评条件=偏离告警首次真实触发后按需补"。本模块为
MOD-RK-23（strategy_deviation_monitor）总值报警器的**分解伴随件**：总值告警
触发后，把总偏差拆为四个加性因子定位来源：

  | 因子 | 含义 | 数据获取（归调用方） |
  |---|---|---|
  | H-A 执行成本偏差 | 滑点+费用相对回测成本假设的多付出 | TCA/成交对账（54 号 §3.2） |
  | H-B 时滞/未成交偏差 | 未成交/延迟成交错过的区间收益 | 未成交续接记录（40 号 §2.12） |
  | H-C 仓位权重偏差 | 实盘持仓权重偏离回测目标 × 标的收益 | 持仓快照 vs 目标权重 |
  | H-D 残差 | 未解释部分（市场环境/噪声/口径差） | 恒等式轧差 |

工程裁定（battle_map 设计态无字段级契约，本模块定义最小可加性口径）：
  - 四因子**加性恒等**：H-D 定义为轧差残差，保证分解不丢信息；
  - H-A/H-B 由调用方预计算传入（数据获取涉成交/持仓域，本模块纯计算不越界）；
  - H-C 在本模块内计算（权重差×标的收益是唯一可在本域闭环的实算因子）；
  - |残差| 占比高 = 四因子解释力不足的信号（调用方复盘口径，本模块不判定）。
"""

from __future__ import annotations

import math
from typing import Final, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

#: 加性恒等校验容差（浮点尾差）
_SUM_TOLERANCE: Final[float] = 1e-9


class InvalidDeviationDecompositionError(ZephyrBaseError):
    """偏离分解输入非法——非有限数值/权重对畸形等。"""

    error_code = "ZA-RK-0030"


def _require_finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise InvalidDeviationDecompositionError(
            f"{name} 必须为有限实数",
            details={"field": name, "value": str(value)},
        )
    return v


def decompose_deviation(
    total_deviation: float,
    execution_cost_drag: float,
    timing_lag: float,
    position_weight_pairs: Sequence[tuple[float, float]],
) -> dict:
    """实盘 vs 回测总偏差的 H-A~D 四因子加性分解。

    Args:
        total_deviation: 总偏差（累计收益口径，cum_live - cum_backtest，带符号）。
        execution_cost_drag: H-A 执行成本贡献（通常 ≤0，负=拖累）。
        timing_lag: H-B 时滞/未成交贡献（带符号）。
        position_weight_pairs: H-C 输入——[(w_live_i - w_backtest_i, r_i)] 序列
            （权重差、标的区间收益，均为小数）。

    Returns:
        dict：factors（H_A~H_D 四因子值）、sum_check、invariant_status
        （加性恒等 PASS/FAIL）、dominant_factor（|贡献|最大因子）、
        shares（各因子占 |total| 份额，total≈0 时全 0）。

    Raises:
        InvalidDeviationDecompositionError: 任一输入非有限实数 / 权重对长度≠2。
    """
    total = _require_finite("total_deviation", total_deviation)
    h_a = _require_finite("execution_cost_drag", execution_cost_drag)
    h_b = _require_finite("timing_lag", timing_lag)

    h_c = 0.0
    for pair in position_weight_pairs:
        if len(pair) != 2:
            raise InvalidDeviationDecompositionError(
                "position_weight_pairs 每项必须为 (weight_diff, symbol_return) 二元组",
                details={"pair": str(pair)},
            )
        w_diff = _require_finite("weight_diff", pair[0])
        sym_ret = _require_finite("symbol_return", pair[1])
        h_c += w_diff * sym_ret

    h_d = total - (h_a + h_b + h_c)

    abs_total = abs(total)
    shares = {
        key: (abs(val) / abs_total if abs_total > 1e-12 else 0.0)
        for key, val in (("H_A", h_a), ("H_B", h_b), ("H_C", h_c), ("H_D", h_d))
    }
    factors = {"H_A": h_a, "H_B": h_b, "H_C": h_c, "H_D": h_d}
    dominant = max(factors, key=lambda k: abs(factors[k]))
    sum_check = h_a + h_b + h_c + h_d

    return {
        "factors": factors,
        "sum_check": sum_check,
        "invariant_status": "PASS" if abs(sum_check - total) <= _SUM_TOLERANCE else "FAIL",
        "dominant_factor": dominant,
        "shares": shares,
        "total_deviation": total,
    }


__all__ = [
    "InvalidDeviationDecompositionError",
    "decompose_deviation",
]
