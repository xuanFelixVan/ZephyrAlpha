# [BLUEPRINT] MOD-GOV_HEALTH_SCORE_CALCULATOR | docs/03_modules/_domain_governance/blueprint.md | §ARCH-PREVENTABILITY-LAYER-001 Phase 3 P3-2
# [MODULE] zephyr.governance.audit.health_score_calculator
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] stdlib (dataclasses, typing)
# [CONSUMERS] zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler (P3-3 接入综合评分判定)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 评分范围 [0.0, 1.0]（0=完全健康，1=完全失控）；权重总和=1.0；每维归一化得分=min(count/threshold, 1.0)；forged_gw_marker 权重最高（任何伪造都 serious）
# [MODIFY-GUARD] _DEFAULT_WEIGHTS / _NORMALIZE_DIM_NAMES
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] calculate_health_score 不抛异常——threshold=0 时该维得分返回 0.0（fail-safe，避免除零）；未知维度忽略
# [TESTS] tests/governance/audit/test_health_score_calculator.py
# [A_module] module_id=MOD-GOV_HEALTH_SCORE_CALCULATOR | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

health_score_calculator.py — commit gateway 滥用 6 维加权健康度评分（P3-2，#ARCH-PREVENTABILITY-LAYER-001 Phase 3）。

将 abuse_monitor 的 6 维 metrics（warn_only/emergency/allow_overlap/forged/non_gw/force_merge）
归一化为 0.0-1.0 综合评分，供 P3-3 的 critical_warn(>0.7)/block_next(>0.9) 判定使用。

设计权衡
--------
1. **归一化方式**: 每维得分 = min(count / threshold, 1.0)。超过阈值即得 1.0（满 分），
   未超过按比例。简单直观，便于解释。
2. **权重分配**: forged_gw_marker=0.30（任何伪造都 serious，最高权重），
   emergency_commit=0.20（逃生通道日常化，较严重），warn_only/allow_overlap 各 0.15
   （中等严重），non_gw/force_merge 各 0.10（v1.3.0 新增 force_merge 维度后重新归一化）。
   权重总和=1.0，保证评分在 [0, 1] 区间。
3. **threshold=0 fail-safe**: 若某维 threshold=0（不应发生，但防御性），该维得分=0.0
   （避免除零异常）。这是 fail-safe，不是 fail-open（得分 0 = 健康，不触发告警）。
4. **未知维度忽略**: metrics 中可能包含非 6 维的 key（如 thresholds/effective_thresholds），
   这些被 _NORMALIZE_DIM_NAMES 过滤，不参与评分。

Usage
-----
::

    from zephyr.governance.audit.health_score_calculator import calculate_health_score

    health = calculate_health_score(
        metrics={"warn_only_24h": 30, "emergency_commit_24h": 2, ...},
        thresholds={"warn_only_24h": 50, "emergency_commit_24h": 5, ...},
    )
    print(health.score)  # 0.0-1.0
    print(health.dimension_scores)  # {"warn_only_24h": 0.6, ...}

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 滥用 6 维计数 metrics
#   fields: warn_only_24h/emergency_commit_24h/allow_overlap_7d/forged_gw_marker_24h/non_gw_commit_24h/force_merge_7d
#   code: calculate_health_score(metrics) L97
# - id: I2
#   name: 各维阈值 thresholds
#   fields: 与 6 维同 key 的阈值（通常传 effective_thresholds）
#   code: calculate_health_score(thresholds) L98
# - id: I3
#   name: 维度权重 weights
#   fields: 可选自定义权重；默认 forged0.30/emergency0.20/warn_only0.15/allow_overlap0.15/non_gw0.10/force_merge0.10
#   code: _DEFAULT_WEIGHTS L61-68
# 层: 算法
# - id: A1
#   name_zh: ① 权重归一化
#   name_en: calculate_health_score 权重预处理
#   intro: 自定义权重总和不为 1 时自动归一化，异常回退默认权重
#   desc: weight_sum<=0 → 回退 _DEFAULT_WEIGHTS；sum!=1.0 → 逐项除以 sum
#   inputs: I3
#   outputs: 归一化权重（总和=1.0）
#   invariant: 权重总和=1.0
# - id: A2
#   name_zh: ② 单维归一化打分
#   name_en: calculate_health_score 维度评分循环
#   intro: 每维得分=min(计数/阈值, 1.0)，超阈值即满分并记入触发维度
#   desc: dim_score=min(count/threshold,1.0)；threshold 非数字或<=0 → fail-safe 得 0 防除零；未知维度被 _NORMALIZE_DIM_NAMES 过滤
#   inputs: I1 I2
#   outputs: dimension_scores + triggered_dimensions
#   invariant: 每维得分 ∈ [0.0, 1.0]
# - id: A3
#   name_zh: ③ 加权综合评分
#   name_en: calculate_health_score 综合聚合
#   intro: 各维得分按权重加权求和，钳制到 0-1 区间
#   desc: total=Σ w_i×dim_i → max(0,min(1,total)) 防浮点误差
#   inputs: A1 A2
#   outputs: AbuseHealthScore(score+dimension_scores+weights+triggered)
#   invariant: 综合评分 ∈ [0.0, 1.0]（0=健康 1=失控）
# 层: 输出
# - id: O1
#   name_zh: 滥用健康度评分 AbuseHealthScore
#   name_en: AbuseHealthScore
#   intro: 6 维加权综合评分与逐维明细，供滥用监控做 critical_warn/block_next 分级判定
#   downstream: commit_gateway_abuse_monitor_reconciler MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR（P3-3 综合评分判定）
# [/ALGO_FLOW]
#
# 边:
# I3 --> A1
# I1 --> A2
# I2 --> A2
# A1 --> A3
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# 6 维默认权重（总和=1.0）
# forged_gw_marker 权重最高（0.30）：任何伪造都是 intentional，严重治理失效
# emergency_commit 权重次高（0.20）：逃生通道日常化，系统性问题
# warn_only/allow_overlap 各 0.15：中等严重
# non_gw/force_merge 各 0.10：v1.3.0 新增 force_merge 维度后重新归一化
_DEFAULT_WEIGHTS: dict[str, float] = {
    "warn_only_24h": 0.15,
    "emergency_commit_24h": 0.20,
    "allow_overlap_7d": 0.15,
    "forged_gw_marker_24h": 0.30,
    "non_gw_commit_24h": 0.10,
    "force_merge_7d": 0.10,
}

# metrics 中参与评分的 6 维 key（过滤 thresholds/effective_thresholds 等非评分字段）
_NORMALIZE_DIM_NAMES = frozenset(_DEFAULT_WEIGHTS.keys())


@dataclass
class AbuseHealthScore:
    """6 维加权健康度评分结果（commit gateway abuse 维度专用）。

    命名说明：使用 AbuseHealthScore 而非 HealthScore，避免与
    ``src/zephyr/infrastructure/asset_inventory/models.py:HealthScore``
    同名冲突（CREATE-GUARD ARCH-034 CLASS-UNIQUENESS）——两者语义不同，
    asset_inventory 的 HealthScore 是资产健康度，本类是 commit gateway
    滥用健康度，必须用 Abuse* 前缀区分。

    Attributes:
        score: 综合评分 [0.0, 1.0]（0=完全健康，1=完全失控）。
        dimension_scores: 每维归一化得分 {dim_name: score_0_1}。
        weights: 使用的权重 {dim_name: weight}（供追溯）。
        triggered_dimensions: 得分=1.0（超过阈值）的维度名列表。
    """

    score: float
    dimension_scores: dict[str, float] = field(default_factory=dict)
    weights: dict[str, float] = field(default_factory=dict)
    triggered_dimensions: list[str] = field(default_factory=list)


def calculate_health_score(
    metrics: dict,
    thresholds: dict,
    weights: dict[str, float] | None = None,
) -> AbuseHealthScore:
    """计算 6 维加权健康度评分（P3-2）。

    Args:
        metrics: abuse_monitor 的 metrics 字典（含 warn_only_24h 等 6 维计数 +
            thresholds/effective_thresholds 等非评分字段，后者被过滤）。
        thresholds: 各维阈值字典（key 与 metrics 6 维一致）。
            通常传 metrics["effective_thresholds"] 或 metrics["thresholds"]。
        weights: 自定义权重（None 用 _DEFAULT_WEIGHTS）。权重总和应=1.0，
            若不为 1.0 会自动归一化（不抛异常）。

    Returns:
        AbuseHealthScore — 综合评分 + 每维得分 + 权重 + 触发维度。
    """
    use_weights = weights if weights is not None else dict(_DEFAULT_WEIGHTS)

    # 权重归一化（防御性：若自定义权重总和不为 1.0，自动归一化）
    weight_sum = sum(use_weights.values())
    if weight_sum <= 0:
        logger.warning("health_score: weight sum <= 0 (%.4f), using defaults", weight_sum)
        use_weights = dict(_DEFAULT_WEIGHTS)
        weight_sum = 1.0
    normalized_weights = {k: v / weight_sum for k, v in use_weights.items()} if weight_sum != 1.0 else use_weights

    dimension_scores: dict[str, float] = {}
    triggered: list[str] = []
    total_score = 0.0

    for dim_name in _NORMALIZE_DIM_NAMES:
        count = metrics.get(dim_name, 0)
        threshold = thresholds.get(dim_name, 0)
        weight = normalized_weights.get(dim_name, 0.0)

        # fail-safe: threshold 非数字/<=0/0 → 该维得分=0.0（避免除零或类型错误）
        try:
            threshold_val = float(threshold)
        except (TypeError, ValueError):
            threshold_val = 0.0
        if threshold_val <= 0:
            dim_score = 0.0
        else:
            try:
                dim_score = min(float(count) / threshold_val, 1.0)
            except (TypeError, ValueError, ZeroDivisionError):
                dim_score = 0.0

        dimension_scores[dim_name] = dim_score
        total_score += weight * dim_score

        # 得分=1.0 表示超过阈值（触发该维）
        if dim_score >= 1.0:
            triggered.append(dim_name)

    # 综合评分 clamp 到 [0, 1]（浮点误差防护）
    final_score = max(0.0, min(1.0, total_score))

    return AbuseHealthScore(
        score=final_score,
        dimension_scores=dimension_scores,
        weights=normalized_weights,
        triggered_dimensions=triggered,
    )


__all__ = ["AbuseHealthScore", "calculate_health_score", "_DEFAULT_WEIGHTS"]
