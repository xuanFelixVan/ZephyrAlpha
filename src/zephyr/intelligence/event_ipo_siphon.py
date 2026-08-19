# [BLUEPRINT] MOD-INT-EVENT-IPO | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md | §2.5a
# [MODULE] zephyr.intelligence.event_ipo_siphon
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] 无（纯函数）
# [CONSUMERS] 事件驱动 sleeve（IPO/再融资事件类仓位策略）；37_liquidity_crisis_protocol §3.2 IPO 流动性抽离预警维度
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] siphon_ratio=募资额/全市场20日均成交额；分级阈值 1%/2%/3%；market_avg_volume<=0 降级 (0.0, NEGLIGIBLE) 不抛异常；仓位调整仅 SEVERE/EXTREME 触发非常态动作
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5a
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无自定义异常——退化输入降级 NEGLIGIBLE/NORMAL 不抛
# [TESTS] tests/intelligence/test_event_ipo_siphon.py
# [A_module] module_id=MOD-INT-EVENT-IPO | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] 26_event_driven_strategy_detail §2.5a IPO 虹吸效应量化算法
# [ALGO_FLOW]
# I1: raise_amount（募资额）+ market_avg_volume（全市场20日均成交额）
# F1: compute_ipo_siphon_coefficient——ratio→四级 NEGLIGIBLE/MODERATE/SEVERE/EXTREME
# F2: ipo_siphon_position_adjustment——days_to_listing×level→ACCELERATE_ENTRY/HOLD_CASH/REDUCE_EXISTING/NORMAL
# O1: (ratio, level) / (action, reason)
# [/ALGO_FLOW]
"""MOD-INT-EVENT-IPO — IPO 虹吸效应量化算法（26 号 §2.5a 施工化）。

背景：final_report_0724 实证长鑫科技科创板上市（募资 579-666 亿，科创板史上
最大 IPO）可吸金 500 亿+，对存量板块形成"虹吸效应"——上市前完成主仓布局
+保留 25% 现金；上市后存量板块降仓避险。

与 37 号 §3.2 联动：IPO 虹吸是**前瞻性**流动性预警（上市日前已知）——
37 号"检测+响应"，26 号"alpha 方向+仓位策略"（本模块）。

数据源：IPO 日历/募资规模来自 akshare_provider stock_ipo_info（production）。
申购热度代理变量（中签率/申购倍数）登记 26 号 §5 暂缓项 8，首版不引入。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5a
Version: 0.1.0
"""

from __future__ import annotations

import logging
from typing import Final

_log = logging.getLogger(__name__)

# ── 虹吸分级阈值（final_report 实证 + A 股历史 IPO 虹吸案例校准，§2.5a）──
SIPHON_RATIO_MODERATE_MAX: Final[float] = 0.01  # <1% 日均成交额 → 可忽略
SIPHON_RATIO_SEVERE_MAX: Final[float] = 0.02    # 1-2% → 局部扰动
SIPHON_RATIO_EXTREME_MIN: Final[float] = 0.03   # >3% → 极端虹吸（历史罕见）

SIPHON_LEVEL_NEGLIGIBLE: Final[str] = "NEGLIGIBLE"
SIPHON_LEVEL_MODERATE: Final[str] = "MODERATE"
SIPHON_LEVEL_SEVERE: Final[str] = "SEVERE"
SIPHON_LEVEL_EXTREME: Final[str] = "EXTREME"

# ── 仓位调整动作 ──
ACTION_ACCELERATE_ENTRY: Final[str] = "ACCELERATE_ENTRY"  # 上市前 3-5 天加速建仓
ACTION_HOLD_CASH: Final[str] = "HOLD_CASH"                # 上市前 1-2 天保留现金
ACTION_REDUCE_EXISTING: Final[str] = "REDUCE_EXISTING"    # 上市后 day 0-5 降仓避险
ACTION_NORMAL: Final[str] = "NORMAL"

CASH_RESERVE_PCT: Final[float] = 0.25  # HOLD_CASH 现金保留比例（final_report 实证 25%）


def compute_ipo_siphon_coefficient(
    raise_amount: float,
    market_avg_volume: float,
) -> tuple[float, str]:
    """IPO 上市日对存量板块的流动性分流系数。

    Parameters
    ----------
    raise_amount : IPO 募资额（如长鑫科技 579-666 亿）。
    market_avg_volume : 全市场 20 日均成交额（如 A 股日均 ~27000 亿）。

    Returns
    -------
    (siphon_ratio, siphon_level) —— ratio = 募资额/日均成交额；
    level ∈ NEGLIGIBLE(<1%) / MODERATE(1-2%) / SEVERE(2-3%) / EXTREME(>3%)。
    market_avg_volume <= 0（数据缺失）→ (0.0, NEGLIGIBLE) 降级不抛异常。
    """
    if market_avg_volume <= 0:
        _log.warning("compute_ipo_siphon_coefficient: market_avg_volume=%s 非法，降级 NEGLIGIBLE", market_avg_volume)
        return 0.0, SIPHON_LEVEL_NEGLIGIBLE
    ratio = max(0.0, raise_amount) / market_avg_volume
    if ratio < SIPHON_RATIO_MODERATE_MAX:
        level = SIPHON_LEVEL_NEGLIGIBLE
    elif ratio < SIPHON_RATIO_SEVERE_MAX:
        level = SIPHON_LEVEL_MODERATE
    elif ratio < SIPHON_RATIO_EXTREME_MIN:
        level = SIPHON_LEVEL_SEVERE
    else:
        level = SIPHON_LEVEL_EXTREME
    return ratio, level


def ipo_siphon_position_adjustment(
    days_to_listing: int,
    siphon_level: str,
    ipo_name: str = "",
) -> tuple[str, str]:
    """IPO 虹吸效应驱动的仓位调整（final_report 实证策略，§2.5a 算法 2）。

    Parameters
    ----------
    days_to_listing : 距上市日自然日数（上市日=0，上市后为负）。
    siphon_level : ``compute_ipo_siphon_coefficient`` 的分级结果。
    ipo_name : IPO 名称（reason 文案用）。

    Returns
    -------
    (action, reason) —— SEVERE/EXTREME 时：上市前 3-5 天 ACCELERATE_ENTRY；
    前 1-2 天 HOLD_CASH（保留≥25% 现金）；上市后 day 0-5 REDUCE_EXISTING；
    其余 NORMAL。MODERATE/NEGLIGIBLE 恒 NORMAL。
    """
    if siphon_level not in (SIPHON_LEVEL_SEVERE, SIPHON_LEVEL_EXTREME):
        return ACTION_NORMAL, "虹吸影响可忽略"

    if 3 <= days_to_listing <= 5:
        return ACTION_ACCELERATE_ENTRY, "上市前布局窗口，优先完成主仓位"
    if 0 < days_to_listing < 3:
        return ACTION_HOLD_CASH, f"保留≥{CASH_RESERVE_PCT:.0%}现金，{ipo_name}上市虹吸备用"
    if -5 <= days_to_listing <= 0:
        return ACTION_REDUCE_EXISTING, "存量板块降仓避险，虹吸峰值期"
    return ACTION_NORMAL, "虹吸期外，正常操作"


__all__: Final = [
    "SIPHON_RATIO_MODERATE_MAX",
    "SIPHON_RATIO_SEVERE_MAX",
    "SIPHON_RATIO_EXTREME_MIN",
    "SIPHON_LEVEL_NEGLIGIBLE",
    "SIPHON_LEVEL_MODERATE",
    "SIPHON_LEVEL_SEVERE",
    "SIPHON_LEVEL_EXTREME",
    "ACTION_ACCELERATE_ENTRY",
    "ACTION_HOLD_CASH",
    "ACTION_REDUCE_EXISTING",
    "ACTION_NORMAL",
    "CASH_RESERVE_PCT",
    "compute_ipo_siphon_coefficient",
    "ipo_siphon_position_adjustment",
]
