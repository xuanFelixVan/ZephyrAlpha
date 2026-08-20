# [BLUEPRINT] 90_methodology_open_questions.md §15（v2.0.0 裁定④）
# [MODULE] zephyr.signal_ashare.market_cap_tier
# [DOMAIN] D_SIGNAL_ASHARE
# [DEPENDENCIES] 无（纯函数）
# [CONSUMERS] universe_registry 流通市值分层计算字段（登记待回填）；信号解释"市值定调子"第一道筛子
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 6 级分层边界含下限；输入单位=亿元（流通市值）；负数拒绝
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 负市值→ValueError
# [TESTS] tests/signal_ashare/test_market_cap_tier.py
# [A_module] module_id=MOD-SIGNAL-ASHARE-MCT | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_SIGNAL_ASHARE — 流通市值 6 级分层（90 号 Phase2 项，#15 资产分级两维精简）

裁定真源：90_methodology_open_questions.md §15（v2.0.0）：
  ④ 流通市值 6 级分层采纳为交易准入内的子维度（"市值定调子"原则：同一信号在
  不同市值段含义不同——大蓝筹"放量大涨"=机构业绩建仓，小盘"放量大涨"=游资拉题材
  准备出货；流通市值是第一道筛子，排在所有技术指标之前）。

分层（流通市值，亿元）：1000亿+ 超级大蓝筹 / 300-1000 行业头部白马 /
100-300 成长股二线龙头 / 50-100 中小盘 / 20-50 小盘（游资主场）/ <20亿 超小盘。

注意：本模块为 90 号 Phase2 交付物，MATURITY=testing；universe_registry 回填与
信号链路接线挂起待 Owner（宪章 B-007 纪律）。
"""

from __future__ import annotations

from enum import Enum

__all__ = ["MarketCapTier", "float_mcap_tier"]


class MarketCapTier(str, Enum):
    """流通市值 6 级分层（90 号 §15 裁定④）。"""

    MEGA = "mega"  # 1000亿+ 超级大蓝筹（公募/社保/北向，业绩驱动波动小）
    LARGE = "large"  # 300-1000亿 行业头部/白马（北向/公募核心，行业景气驱动）
    MID = "mid"  # 100-300亿 成长股/二线龙头（机构覆盖中等，成长+估值博弈）
    SMALL_MID = "small_mid"  # 50-100亿 中小盘（机构覆盖少，共识弱流动性中等）
    SMALL = "small"  # 20-50亿 小盘（游资主场，题材/资金驱动波动大）
    MICRO = "micro"  # <20亿 超小盘（散户/游资做妖，高风险）


#: 分层阈值（亿元，含下限；降序判定）
_TIER_FLOORS_YI: tuple[tuple[float, MarketCapTier], ...] = (
    (1000.0, MarketCapTier.MEGA),
    (300.0, MarketCapTier.LARGE),
    (100.0, MarketCapTier.MID),
    (50.0, MarketCapTier.SMALL_MID),
    (20.0, MarketCapTier.SMALL),
)


def float_mcap_tier(float_mcap_yi: float) -> MarketCapTier:
    """流通市值（亿元）→ 6 级分层。

    Args:
        float_mcap_yi: 流通市值，单位亿元（≥0）

    Returns:
        MarketCapTier 分层标签

    Raises:
        ValueError: 负市值
    """
    if float_mcap_yi < 0:
        raise ValueError(f"流通市值不能为负，实际 {float_mcap_yi}")
    for floor, tier in _TIER_FLOORS_YI:
        if float_mcap_yi >= floor:
            return tier
    return MarketCapTier.MICRO
