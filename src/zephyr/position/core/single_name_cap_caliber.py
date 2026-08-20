# [BLUEPRINT] 31_position_sizing §2.4.1（8% vs 5% 分层口径澄清）+ §5 待裁定（单票上限三层口径统一）
# [MODULE] zephyr.position.core.single_name_cap_caliber
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.position.core.position_sizing_engine; zephyr.position.core.firm_risk_aggregator; zephyr.position.core.position_limit_enforcer
# [CONSUMERS] 治理审计/配置校验调用方（G04 首批策略产出后统一口径时的核查工具）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读校验不改生产默认（§5 裁定"最终值待校准"）；三层全 ∈(0,1]；firm 中间层 > 最终硬限 → 冗余裁剪警告（登记非错误）
# [MODIFY-GUARD] 31号 §2.4.1/§5
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无（校验结果以问题列表返回，不抛异常）
# [TESTS] tests/position/test_single_name_cap_caliber.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 三层单票上限口径映射 SINGLE_NAME_CAP_LAYERS（MOD-POS-001 策略层 5% / MOD-POS-021 firm 聚合 8% / MOD-POS-010 最终硬限 5%）
# A1: validate_tier_calibers（合法性+冗余裁剪检测：firm 层 > 最终硬限时 8% 永不 binding 属冗余中间值）
# A2: check_production_consistency（映射表 vs 三模块生产默认值漂移检测）
# O1: 问题列表 list[str]（空=通过；冗余裁剪为 WARNING 级登记项，非阻断）
# [/ALGO_FLOW]
"""单票上限三层口径映射 + 校验（31号 §2.4.1 / §5，32号 §6 同名行）。

分层关系（31号 §2.4.1 ⚠️ 澄清）：
  - MOD-POS-001 策略层裁决默认 5%（default_single_position_cap，可被 symbol_overrides 覆盖）
  - MOD-POS-021 firm 聚合后 8%（single_name_cap，跨策略求和后的中间裁剪）
  - MOD-POS-010 最终硬限 5% NAV（position_limit_enforcer，5 级否决裁决的兜底）

因 8% > 5%，MOD-POS-010 的 5% 会在 MOD-POS-021 的 8% 之后再次裁剪，8% 实为冗余
中间值。最终值待 G04 首批策略产出后统一（候选：全对齐 8% 或全对齐 5%，§5 待裁定）。
本模块只做口径映射与校验（不硬改生产默认），供统一施工前的漂移检测与冗余登记。

Version: 1.0.0
"""

from __future__ import annotations

from zephyr.position.core.firm_risk_aggregator import SINGLE_NAME_CAP as _FIRM_AGG_CAP
from zephyr.position.core.position_limit_enforcer import PositionLimitConfig
from zephyr.position.core.position_sizing_engine import PositionSizingConfig

# ── 三层口径映射常量（31号 §2.4.1 分层关系真源表）──
LAYER_STRATEGY = "MOD-POS-001"   # 策略层裁决（PositionSizingEngine）
LAYER_FIRM_AGG = "MOD-POS-021"   # firm 聚合后中间裁剪（FirmRiskAggregator）
LAYER_FINAL_HARD = "MOD-POS-010"  # 最终硬限执行器（PositionLimitEnforcer）

SINGLE_NAME_CAP_LAYERS: dict[str, float] = {
    LAYER_STRATEGY: 0.05,    # 策略层裁决默认 5% NAV
    LAYER_FIRM_AGG: 0.08,    # firm 聚合后 8%（跨策略求和口径）
    LAYER_FINAL_HARD: 0.05,  # 最终硬限 5% NAV（兜底）
}

# 层级流水线顺序（上游→下游）
LAYER_PIPELINE_ORDER: tuple[str, str, str] = (
    LAYER_STRATEGY, LAYER_FIRM_AGG, LAYER_FINAL_HARD,
)


def validate_tier_calibers(caps: dict[str, float] | None = None) -> list[str]:
    """校验单票三层口径配置（不改动生产默认，只返回问题列表）。

    校验规则（31号 §2.4.1）：
      1. 三层齐全（MOD-POS-001/021/010 各一条）
      2. 各层值 ∈ (0,1]
      3. 冗余裁剪检测：firm 聚合层 cap > 最终硬限 cap 时，firm 层永不 binding
         （8% > 5% 现状登记为 WARNING——§5 待裁定统一后应消除）

    Args:
        caps: {layer: cap}；None=用 SINGLE_NAME_CAP_LAYERS 默认映射

    Returns:
        问题描述列表（空=通过）；"WARNING:" 前缀为登记项（冗余裁剪），非阻断
    """
    caps = SINGLE_NAME_CAP_LAYERS if caps is None else caps
    issues: list[str] = []

    for layer in LAYER_PIPELINE_ORDER:
        if layer not in caps:
            issues.append(f"ERROR: 缺少 {layer} 层口径配置")
    if issues:
        return issues

    for layer, cap in caps.items():
        if not 0 < cap <= 1:
            issues.append(f"ERROR: {layer} 层 cap={cap} 越界（须 ∈(0,1]）")

    firm_cap = caps[LAYER_FIRM_AGG]
    final_cap = caps[LAYER_FINAL_HARD]
    if firm_cap > final_cap:
        issues.append(
            f"WARNING: {LAYER_FIRM_AGG} firm 聚合层 cap={firm_cap:.2%} > "
            f"{LAYER_FINAL_HARD} 最终硬限 {final_cap:.2%}——firm 层永不 binding，"
            f"属冗余中间裁剪（31号 §2.4.1 登记，§5 待 G04 后统一口径）"
        )
    return issues


def check_production_consistency() -> list[str]:
    """映射表 vs 三模块生产默认值的漂移检测（只读，不改生产）。

    Returns:
        漂移问题列表（空=映射表与生产默认一致）
    """
    production = {
        LAYER_STRATEGY: PositionSizingConfig().default_single_position_cap,
        LAYER_FIRM_AGG: _FIRM_AGG_CAP,
        LAYER_FINAL_HARD: PositionLimitConfig().single_instrument_cap,
    }
    issues: list[str] = []
    for layer, prod_val in production.items():
        mapped = SINGLE_NAME_CAP_LAYERS[layer]
        if abs(prod_val - mapped) > 1e-12:
            issues.append(
                f"ERROR: {layer} 生产默认 {prod_val:.4f} 与口径映射表 {mapped:.4f} 漂移"
            )
    return issues
