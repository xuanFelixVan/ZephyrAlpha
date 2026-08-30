# [BLUEPRINT] MOD-RK-32 | docs/03_modules/_domain_risk/crowding_response_engine/blueprint.md
# [MODULE] zephyr.risk.core.crowding_response_engine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.clone_guard.strategy_fingerprint(DTW唯一真源); zephyr.shared.foundation.errors; numpy
# [CONSUMERS] 筛选漏斗第六层降权(weight_penalty, 设计契约); MOD-RK-30(熔断式退出联动, 设计契约)
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 拥挤判定=crowding_score超阈 OR 逻辑指纹相似度超阈; 响应缩放∈[0,1]; weight_penalty∈[0,1); 悖论防护需三条件同时(拥挤+回撤超阈+斜率恶化)→forced_exit+position_scale=0; 指纹<2路→similarity=None不参与判定; 指纹z-归一化后DTW(形态可比); 纯函数无IO
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidCrowdingResponseConfigError; InvalidCrowdingResponseInputError
# [TESTS] tests/risk/test_crowding_response_engine.py
# [TTL] permanent

# [ALGO_FLOW]
# I1: crowding_score(MOD-RK-13产出标量) + drawdown_pct/slope(回撤状态标量)
# I2: fingerprints {strategy_id: PnL形态序列}(可空)
# I3: CrowdingResponseConfig(拥挤阈/相似阈/三档缩放/悖论回撤阈)
# A1: 逻辑指纹相似度(z-归一化→两两DTW复用clone_guard→sim=1/(1+dtw)取max)
# A2: 拥挤判定(score超阈 OR sim超阈)→降杠杆/降仓/漏斗降权
# A3: 悖论防护(拥挤∧回撤超阈∧斜率>0→熔断式退出)
# O1: CrowdingResponseAction(frozen) → 漏斗第六层降权/仓位杠杆收紧/强制退出
# [/ALGO_FLOW]
#
# 边:
# I1 --> A2
# I2 --> A1
# I3 --> A1
# I3 --> A2
# I3 --> A3
# A1 --> A2
# A2 --> A3
# I1 --> A3
# A3 --> O1
"""
Crowding Response Engine — C-045 拥挤度响应引擎 (MOD-RK-32, MVP)

MOD-RK-13 CrowdingMonitor（跨参与者拥挤度**度量**）的深度增强**响应**层：
策略逻辑指纹相似度（PnL 形态 z-归一化 + 两两 DTW，复用 clone_guard
strategy_fingerprint.dtw_distance）补拥挤判定维度；拥挤超阈自动降杠杆/降仓并产
漏斗第六层降权系数；拥挤-回撤正反馈悖论防护（拥挤∧回撤超阈∧斜率恶化 → 熔断式
退出，打断"踩踏→回撤→再抛售"回路）。

不复制裁定（W1c 同族整合）：拥挤度度量在 MOD-RK-13（本引擎消费其 crowding_score
标量，不重算）；DTW 唯一真源 = clone_guard。

SSoT: docs/03_modules/_domain_risk/crowding_response_engine/blueprint.md
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: crowding_score 参数
#   fields: 参数 crowding_score，类型注解 float
#   code: crowding_response_engine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: fingerprints 参数
#   fields: 参数 fingerprints（无注解）
#   code: crowding_response_engine.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: drawdown_pct 参数
#   fields: 参数 drawdown_pct（无注解）
#   code: crowding_response_engine.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: drawdown_slope 参数
#   fields: 参数 drawdown_slope（无注解）
#   code: crowding_response_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① assess_crowding_response
#   name_en: assess_crowding_response
#   intro: 拥挤响应主入口：拥挤判定 → 降杠杆/降仓/漏斗降权 + 悖论防护。
#   desc: 拥挤响应主入口：拥挤判定 → 降杠杆/降仓/漏斗降权 + 悖论防护。 Args: crowding_score: MOD-RK-13 CrowdingMonitor 产出（∈[0…；源码 L199-L271
#   inputs: crowding_score fingerprints drawdown_pct drawdown_slope config
#   outputs: CrowdingResponseAction
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: CrowdingResponseAction
#   name_en: CrowdingResponseAction
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 筛选漏斗第六层降权(weight_penalty, 设计契约); MOD-RK-30(熔断式退出联动, 设计契约)
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

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

import numpy as np

from zephyr.clone_guard.strategy_fingerprint import dtw_distance
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "CrowdingResponseAction",
    "CrowdingResponseConfig",
    "InvalidCrowdingResponseConfigError",
    "InvalidCrowdingResponseInputError",
    "assess_crowding_response",
]


class InvalidCrowdingResponseConfigError(ZephyrBaseError):
    """拥挤响应配置非法（Fail-Closed）。"""


class InvalidCrowdingResponseInputError(ZephyrBaseError):
    """拥挤响应输入非法（Fail-Closed）。"""


@dataclass(frozen=True)
class CrowdingResponseConfig:
    """拥挤响应配置（C 类可调参数）。

    Attributes:
        crowded_threshold: crowding_score 拥挤阈（≥，对齐 MOD-RK-13 默认 0.6）
        similarity_threshold: 逻辑指纹相似度拥挤阈（≥，sim=1/(1+dtw)）
        leverage_when_crowded: 拥挤时杠杆缩放
        position_when_crowded: 拥挤时仓位缩放
        weight_penalty_when_crowded: 拥挤时漏斗降权系数（∈[0,1)，越大降权越多）
        paradox_drawdown_threshold: 悖论防护回撤阈（≥，NAV 占比）
    """

    crowded_threshold: float = 0.6
    similarity_threshold: float = 0.8
    leverage_when_crowded: float = 0.5
    position_when_crowded: float = 0.5
    weight_penalty_when_crowded: float = 0.5
    paradox_drawdown_threshold: float = 0.08

    def __post_init__(self) -> None:
        for name in ("crowded_threshold", "similarity_threshold"):
            v = getattr(self, name)
            if not math.isfinite(v) or not 0.0 < v <= 1.0:
                raise InvalidCrowdingResponseConfigError(f"{name} 必须 ∈ (0,1]: {v}")
        for name in ("leverage_when_crowded", "position_when_crowded"):
            v = getattr(self, name)
            if not math.isfinite(v) or not 0.0 < v <= 1.0:
                raise InvalidCrowdingResponseConfigError(f"{name} 必须 ∈ (0,1]: {v}")
        if not math.isfinite(self.weight_penalty_when_crowded) or not 0.0 <= self.weight_penalty_when_crowded < 1.0:
            raise InvalidCrowdingResponseConfigError(
                f"weight_penalty_when_crowded 必须 ∈ [0,1): {self.weight_penalty_when_crowded}"
            )
        if not math.isfinite(self.paradox_drawdown_threshold) or not 0.0 < self.paradox_drawdown_threshold <= 1.0:
            raise InvalidCrowdingResponseConfigError(
                f"paradox_drawdown_threshold 必须 ∈ (0,1]: {self.paradox_drawdown_threshold}"
            )


@dataclass(frozen=True)
class CrowdingResponseAction:
    """拥挤响应动作（frozen 不可变）。"""

    is_crowded: bool
    logic_similarity_max: float | None  # 指纹<2路 → None
    leverage_scale: float  # ∈(0,1]
    position_scale: float  # ∈[0,1]（forced_exit → 0）
    weight_penalty: float  # ∈[0,1) 漏斗第六层降权系数
    paradox_guard_triggered: bool
    forced_exit: bool
    reasons: tuple[str, ...]


def _z_normalize(series: Sequence[float]) -> np.ndarray:
    """z-归一化（DTW 形态可比前提；常数序列→零向量）。"""
    a = np.asarray(series, dtype=float).ravel()
    std = float(a.std())
    if std < 1e-12:
        return np.zeros_like(a)
    return (a - float(a.mean())) / std


def _max_logic_similarity(fingerprints: Mapping[str, Sequence[float]]) -> float | None:
    """两两 DTW（z-归一化）→ sim=1/(1+dtw) 的最大值；<2 路 → None。"""
    keys = sorted(fingerprints.keys())
    if len(keys) < 2:
        return None
    best = 0.0
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            d = dtw_distance(_z_normalize(fingerprints[keys[i]]), _z_normalize(fingerprints[keys[j]]))
            best = max(best, 1.0 / (1.0 + float(d)))
    return best


def assess_crowding_response(
    crowding_score: float,
    *,
    fingerprints: Mapping[str, Sequence[float]] | None = None,
    drawdown_pct: float = 0.0,
    drawdown_slope: float = 0.0,
    config: CrowdingResponseConfig | None = None,
) -> CrowdingResponseAction:
    """拥挤响应主入口：拥挤判定 → 降杠杆/降仓/漏斗降权 + 悖论防护。

    Args:
        crowding_score: MOD-RK-13 CrowdingMonitor 产出（∈[0,1]）
        fingerprints: {strategy_id: PnL 形态序列}（可空；<2 路不算相似度）
        drawdown_pct: 当前回撤（NAV 占比，≥0）
        drawdown_slope: 回撤斜率（>0 = 恶化中）
        config: 配置（None → 默认）

    Returns:
        CrowdingResponseAction

    Raises:
        InvalidCrowdingResponseInputError: 输入越界/非有限/指纹序列空
    """
    if not math.isfinite(crowding_score) or not 0.0 <= crowding_score <= 1.0:
        raise InvalidCrowdingResponseInputError(f"crowding_score 必须 ∈ [0,1] 有限值: {crowding_score}")
    if not math.isfinite(drawdown_pct) or not 0.0 <= drawdown_pct <= 1.0:
        raise InvalidCrowdingResponseInputError(f"drawdown_pct 必须 ∈ [0,1] 有限值: {drawdown_pct}")
    if not math.isfinite(drawdown_slope):
        raise InvalidCrowdingResponseInputError(f"drawdown_slope 必须为有限值: {drawdown_slope}")
    cfg = config or CrowdingResponseConfig()

    sim_max: float | None = None
    if fingerprints is not None:
        for sid, series in fingerprints.items():
            if len(series) == 0:
                raise InvalidCrowdingResponseInputError(f"指纹序列为空: {sid}")
        sim_max = _max_logic_similarity(fingerprints)

    reasons: list[str] = []
    crowded_by_score = crowding_score >= cfg.crowded_threshold
    crowded_by_logic = sim_max is not None and sim_max >= cfg.similarity_threshold
    is_crowded = crowded_by_score or crowded_by_logic
    if crowded_by_score:
        reasons.append(f"crowding_score={crowding_score:.3f} ≥ 拥挤阈 {cfg.crowded_threshold}")
    if crowded_by_logic:
        reasons.append(f"策略逻辑指纹相似度 max={sim_max:.3f} ≥ 阈 {cfg.similarity_threshold}")

    if is_crowded:
        leverage = cfg.leverage_when_crowded
        position = cfg.position_when_crowded
        penalty = cfg.weight_penalty_when_crowded
    else:
        leverage = 1.0
        position = 1.0
        penalty = 0.0

    paradox = bool(is_crowded and drawdown_pct >= cfg.paradox_drawdown_threshold and drawdown_slope > 0.0)
    if paradox:
        position = 0.0
        reasons.append(
            f"拥挤-回撤正反馈悖论防护：拥挤∧回撤 {drawdown_pct:.1%}≥{cfg.paradox_drawdown_threshold:.0%}∧斜率 {drawdown_slope:+.3f} 恶化 → 熔断式退出"
        )

    return CrowdingResponseAction(
        is_crowded=is_crowded,
        logic_similarity_max=sim_max,
        leverage_scale=leverage,
        position_scale=position,
        weight_penalty=penalty,
        paradox_guard_triggered=paradox,
        forced_exit=paradox,
        reasons=tuple(reasons),
    )
