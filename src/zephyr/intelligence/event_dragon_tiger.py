# [BLUEPRINT] MOD-INT-EVENT-DT | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md | §2.5
# [MODULE] zephyr.intelligence.event_dragon_tiger
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] 无（纯函数+数据契约）
# [CONSUMERS] 事件驱动 sleeve（event_score 龙虎榜佐证乘法修正：event_score_final = event_score × modifier）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] modifier∈[0.7,1.2]；无龙虎榜数据→1.0 不修正；净买率≥12%→1.2（硬阈值，2026 实证 +5.11% 20日均收仍有效）；量化席位 hard（≥3席+买入占比>30%）→×0.7，soft（≥3席）→×0.85；机构净买入方向性佐证失效（45.7%<随机）不加分；turnover/total_buy<=0 → 对应比率按 0 处理不抛
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5（v1.8.0 与 24 号 v1.8.2 同步）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无自定义异常——数据缺失/零基线降级不抛
# [TESTS] tests/intelligence/test_event_dragon_tiger.py
# [A_module] module_id=MOD-INT-EVENT-DT | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] 26_event_driven_strategy_detail §2.5 龙虎榜 2026 机构信号失效校准
# [ALGO_FLOW]
# I1: DragonTigerData（net_buy_amount/total_turnover/total_buy/buyer_seats[type,buy_amount]）
# F1: 净买率=net_buy/turnover 硬阈值门控（≥12%→1.2 否则→1.0）
# F2: 量化席位过滤（≥3席：占比>30%→×0.7 hard；否则→×0.85 soft）
# O1: modifier∈[0.7,1.2]（event_score 乘法修正因子）
# [/ALGO_FLOW]
"""MOD-INT-EVENT-DT — 龙虎榜佐证修正因子（26 号 §2.5 v1.8.0，2026 失效校准）。

与 24 号 v1.8.2 实证同步：机构净买入次日胜率 62-68%→**45.7%（<50% 随机，
反向失效）**——"机构净买入=利好佐证"假设不再成立，校准口径：

- 方向性佐证失效 → 机构净买入不再自动强化 event_score，降级为中性参考（不加分）。
- 佐证转向"净买率极端值"：净买率 ≥12% 硬阈值（样本 20 日均收 +5.11% 仍有效）→ ×1.2。
- 量化席位过滤（24 号 §3.10/§3.11 双阈值）：≥3 量化席位 + 买入占比 >30%
  → hard ×0.7（量化主导→佐证无效化，次日高开低走概率 70%）；仅 ≥3 席
  → soft ×0.85（量化同现→佐证弱化，后续 3 日下跌概率 58%）。

与 24 号口径一致性：共用 dragon_tiger 表 + 12% 净买率硬阈值 + 量化席位双阈值，
确保两 sleeve 对龙虎榜信号解读一致。数据源：双表 ``dragon_tiger``（汇总）+
``dragon_tiger_seat``（席位明细，席位类型字段消费自 seat 表，tasks.yaml 盘后调度）。

用法：``event_score_final = event_score * dragon_tiger_corroboration_modifier(dt_data)``；
仅当事件源含龙虎榜佐证时调用；无龙虎榜数据时 modifier=1.0 不影响原 event_score。

依据: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/26_event_driven_strategy_detail.md §2.5
Version: 0.1.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

# ── 校准常量（2026 实证，26 号 §2.5 / 24 号 §3.5 同步口径）──
NET_BUY_RATIO_STRONG: Final[float] = 0.12      # 净买率极端值硬阈值（+5.11% 20日均收仍有效）
MODIFIER_STRONG: Final[float] = 1.2            # 强佐证加分
MODIFIER_NEUTRAL: Final[float] = 1.0           # 机构净买入方向失效→不加分
QUANT_SEAT_TYPE: Final[str] = "quant_inst"     # 量化席位类型标识（dragon_tiger_seat 表）
QUANT_SEAT_COUNT_MIN: Final[int] = 3           # 量化席位同现阈值
QUANT_BUY_RATIO_HARD: Final[float] = 0.30      # 量化买入占比 hard 阈值
MODIFIER_QUANT_HARD: Final[float] = 0.7        # hard：量化主导→佐证无效化
MODIFIER_QUANT_SOFT: Final[float] = 0.85       # soft：量化同现→佐证弱化


@dataclass(frozen=True, slots=True)
class DragonTigerSeat:
    """龙虎榜席位记录（dragon_tiger_seat 表口径，Top5 买卖席位合并去重）。"""

    type: str          # 席位类型（quant_inst=量化机构 / foreign=外资 / hot_money=游资 / ...）
    buy_amount: float  # 买入金额


@dataclass(frozen=True, slots=True)
class DragonTigerData:
    """龙虎榜佐证输入（dragon_tiger 汇总表 + seat 明细合并视图）。"""

    net_buy_amount: float
    total_turnover: float
    total_buy: float
    buyer_seats: tuple[DragonTigerSeat, ...] = field(default_factory=tuple)


def dragon_tiger_corroboration_modifier(data: DragonTigerData | None) -> float:
    """龙虎榜佐证修正因子（2026 失效校准）。返回乘法因子 ∈ [0.7, 1.2]。

    - 无数据 → 1.0（非龙虎榜标的不修正）
    - 净买率 ≥12% → 1.2（极端值硬阈值门控）；<12% → 1.0（方向性佐证失效不加分）
    - 量化席位 hard（≥3 席 + 买入占比 >30%）→ ×0.7；soft（≥3 席）→ ×0.85
    """
    if data is None:
        return 1.0

    # ① 净买率极端值硬阈值门控
    net_buy_ratio = data.net_buy_amount / data.total_turnover if data.total_turnover > 0 else 0.0
    base_modifier = MODIFIER_STRONG if net_buy_ratio >= NET_BUY_RATIO_STRONG else MODIFIER_NEUTRAL

    # ② 量化席位过滤（24 号 §3.10 + §3.11 双阈值预警）
    quant_seats = [s for s in data.buyer_seats if s.type == QUANT_SEAT_TYPE]
    quant_count = len(quant_seats)
    quant_buy_ratio = (
        sum(s.buy_amount for s in quant_seats) / data.total_buy if data.total_buy > 0 else 0.0
    )
    if quant_count >= QUANT_SEAT_COUNT_MIN and quant_buy_ratio > QUANT_BUY_RATIO_HARD:
        base_modifier *= MODIFIER_QUANT_HARD
    elif quant_count >= QUANT_SEAT_COUNT_MIN:
        base_modifier *= MODIFIER_QUANT_SOFT
    return base_modifier


__all__: Final = [
    "NET_BUY_RATIO_STRONG",
    "MODIFIER_STRONG",
    "MODIFIER_NEUTRAL",
    "QUANT_SEAT_TYPE",
    "QUANT_SEAT_COUNT_MIN",
    "QUANT_BUY_RATIO_HARD",
    "MODIFIER_QUANT_HARD",
    "MODIFIER_QUANT_SOFT",
    "DragonTigerSeat",
    "DragonTigerData",
    "dragon_tiger_corroboration_modifier",
]
