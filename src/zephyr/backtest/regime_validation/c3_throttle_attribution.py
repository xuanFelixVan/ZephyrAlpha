# [BLUEPRINT] none | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/11_regime_backtest_validation_plan.md §4.3 C3 / §0.5.7
# [MODULE] zephyr.backtest.regime_validation.c3_throttle_attribution
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pandas; numpy; zephyr.shared.foundation.errors
# [CONSUMERS] 人工审查; 11_regime_backtest_validation_plan C3 节流归因
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯分析函数: 只消费既有 C1 开/关回测逐日产物, 零新回测成本; 态贡献=该态 Σ(ret_开−ret_关) 避免损失正部占全态正部和的份额(MaxDD改善的可加代理分解); 防御态默认(r4,r10); frozen 不可变
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] C3AttributionError(ZA-BT-0031)
# [TESTS] tests/backtest/test_c3_throttle_attribution.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: records(逐日 DataFrame: state/shrinkage/ret_baseline/ret_experiment, 既有 C1 回测产物+Viterbi 主导态)
# I2: defensive_states=(r4,r10) + bull_state=r3 + 门槛(防御贡献≥60% / 牛均值Shrinkage≥0.85, §4.3 C3)
# A1: attribute_throttle(按态分组: 天数/均值Shrinkage/避免损失→正部归一化贡献份额)
# A2: 判定: r4+CRISIS 贡献份额≥60% 且 r3 均值 Shrinkage≥0.85(牛市基本不缩)
# O1: C3AttributionReport(逐态归因 + defensive_share + bull_mean_shrinkage + passed)
# [/ALGO_FLOW]
"""
D_BACKTEST — C3 节流归因分析（11 号 memo §4.3 C3）。

纯分析函数：基于 C1 既有回测产物（零新回测成本），按 Viterbi 主导态 +
overlay 态分组归因：各态天数占比、平均 Shrinkage、避免损失
（Σ(ret_开 − ret_关)，正值=该态节流后少亏/多赚）及其正部归一化份额
（MaxDD 改善的可加代理分解）。

判定（§4.3 C3）：
  - r4 熊市阴跌 + CRISIS(r10) 两态贡献 ≥ 60%（改善应来自预期防御态）；
  - r3 牛市态平均 Shrinkage ≥ 0.85（牛市基本不缩，否则收缩方向错误）。

依据: 11_regime_backtest_validation_plan §4.3 C3 / §0.5.7
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: records 参数
#   fields: 参数 records，类型注解 pd.DataFrame
#   code: c3_throttle_attribution.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: defensive_states 参数
#   fields: 参数 defensive_states，类型注解 Sequence[Hashable]
#   code: c3_throttle_attribution.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: bull_state 参数
#   fields: 参数 bull_state，类型注解 Hashable
#   code: c3_throttle_attribution.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: defensive_share_min 参数
#   fields: 参数 defensive_share_min，类型注解 float
#   code: c3_throttle_attribution.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① attribute_throttle
#   name_en: attribute_throttle
#   intro: C3 主入口：各态 Shrinkage 贡献归因。
#   desc: C3 主入口：各态 Shrinkage 贡献归因。 Args: records: 逐日 DataFrame，列 = state / shrinkage / ret_baselin…；源码 L134-L216
#   inputs: records defensive_states bull_state defensive_share_min bull_shrink_m…
#   outputs: C3AttributionReport
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: C3AttributionReport
#   name_en: C3AttributionReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 人工审查; 11_regime_backtest_validation_plan C3 节流归因
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from typing import Hashable, Sequence

import numpy as np
import pandas as pd

try:  # 治理基类缺失时降级为 Exception，保证模块可独立 import
    from zephyr.shared.foundation.errors import ZephyrBaseError
except Exception:  # pragma: no cover  # noqa: BLE001
    ZephyrBaseError = Exception  # type: ignore[assignment,misc]

_logger = logging.getLogger(__name__)

_EPS = 1e-12
_REQUIRED_COLUMNS = ("state", "shrinkage", "ret_baseline", "ret_experiment")


class C3AttributionError(ZephyrBaseError):
    """ZA-BT-0031: C3 节流归因分析错误（输入非法/缺列）。"""

    error_code = "ZA-BT-0031"


@dataclass(frozen=True)
class C3StateAttribution:
    """单态归因——不可变。"""

    state: Hashable
    days: int
    day_share: float  # 天数占比
    mean_shrinkage: float
    mean_ret_baseline: float
    mean_ret_experiment: float
    avoided_return: float  # Σ(ret_开 − ret_关)，正值=该态节流减少损失
    contribution_share: float  # 避免损失正部占全态正部和的份额


@dataclass(frozen=True)
class C3AttributionReport:
    """C3 节流归因报告——不可变。"""

    states: tuple[C3StateAttribution, ...]  # 按天数降序
    total_days: int
    total_avoided: float  # 全样本 Σ(ret_开 − ret_关)
    defensive_share: float  # 防御态（r4+CRISIS）贡献份额
    bull_mean_shrinkage: float | None  # r3 平均 Shrinkage；无 r3 样本=None（该条 vacuous 通过）
    passed: bool  # defensive_share≥min 且 bull≥min
    summary: str


def attribute_throttle(
    records: pd.DataFrame,
    defensive_states: Sequence[Hashable] = ("r4", "r10"),
    bull_state: Hashable = "r3",
    defensive_share_min: float = 0.60,
    bull_shrink_min: float = 0.85,
) -> C3AttributionReport:
    """C3 主入口：各态 Shrinkage 贡献归因。

    Args:
        records: 逐日 DataFrame，列 = state / shrinkage / ret_baseline /
            ret_experiment（C1 开/关回测逐日产物 + Viterbi 主导态）。
        defensive_states: 防御态清单（默认 r4 熊市 + r10 CRISIS）。
        bull_state: 牛市态（默认 r3，其平均 Shrinkage 应 ≥0.85）。
        defensive_share_min: 防御态贡献份额门槛（§4.3 C3=0.60）。
        bull_shrink_min: 牛市态平均 Shrinkage 门槛（§4.3 C3=0.85）。

    Raises:
        C3AttributionError: 空表 / 缺列 / 含 NaN / shrinkage 越出 [0,1] / 门槛非法。
    """
    if not 0.0 < defensive_share_min <= 1.0 or not 0.0 < bull_shrink_min <= 1.0:
        raise C3AttributionError(f"门槛非法: defensive={defensive_share_min} bull={bull_shrink_min}")
    missing = [c for c in _REQUIRED_COLUMNS if c not in records.columns]
    if missing:
        raise C3AttributionError(f"records 缺列: {missing}（需 {list(_REQUIRED_COLUMNS)}）")
    if len(records) == 0:
        raise C3AttributionError("records 不能为空")
    df = records[list(_REQUIRED_COLUMNS)]
    if df.isna().any().any():
        raise C3AttributionError("records 含 NaN")
    shr = df["shrinkage"].to_numpy(dtype=float)
    if (shr < 0.0).any() or (shr > 1.0).any():
        raise C3AttributionError("shrinkage 须 ∈ [0,1]（只减不增）")

    total_days = len(df)
    total_avoided = float((df["ret_experiment"] - df["ret_baseline"]).sum())

    per_state: list[C3StateAttribution] = []
    for state, g in df.groupby("state", sort=False):
        avoided = float((g["ret_experiment"] - g["ret_baseline"]).sum())
        per_state.append(
            C3StateAttribution(
                state=state,
                days=int(len(g)),
                day_share=len(g) / total_days,
                mean_shrinkage=float(g["shrinkage"].mean()),
                mean_ret_baseline=float(g["ret_baseline"].mean()),
                mean_ret_experiment=float(g["ret_experiment"].mean()),
                avoided_return=avoided,
                contribution_share=0.0,  # 占位，下方统一归一化
            )
        )
    pos_total = sum(max(s.avoided_return, 0.0) for s in per_state)
    per_state = [
        replace(
            s,
            contribution_share=(max(s.avoided_return, 0.0) / pos_total if pos_total > _EPS else 0.0),
        )
        for s in per_state
    ]
    per_state.sort(key=lambda s: (-s.days, str(s.state)))

    defensive = tuple(defensive_states)
    defensive_share = sum(s.contribution_share for s in per_state if s.state in defensive)
    bull = next((s for s in per_state if s.state == bull_state), None)
    bull_mean = bull.mean_shrinkage if bull is not None else None
    passed = defensive_share >= defensive_share_min and (bull_mean is None or bull_mean >= bull_shrink_min)
    summary = (
        f"C3 节流归因: {total_days} 天 / {len(per_state)} 态, 总避免损失={total_avoided:+.4f}, "
        f"防御态{[str(d) for d in defensive]}贡献={defensive_share:.2%} 门槛≥{defensive_share_min:.0%}, "
        f"牛态{bull_state}均值Shrinkage={bull_mean if bull_mean is not None else 'N/A(无样本)'} "
        f"门槛≥{bull_shrink_min} → {'通过' if passed else '不通过（收缩方向可能错误）'}"
    )
    _logger.info("C3 完成: %s", summary)
    return C3AttributionReport(
        states=tuple(per_state),
        total_days=total_days,
        total_avoided=total_avoided,
        defensive_share=defensive_share,
        bull_mean_shrinkage=bull_mean,
        passed=passed,
        summary=summary,
    )


__all__ = [
    "C3AttributionError",
    "C3AttributionReport",
    "C3StateAttribution",
    "attribute_throttle",
]
