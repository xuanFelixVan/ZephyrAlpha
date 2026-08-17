# [BLUEPRINT] MOD-PLAN-003 | docs/03_modules/_domain_plan_engine/closing_session_decision/blueprint.md
# [MODULE] zephyr.plan_engine.closing_session_decision
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.plan_engine.tomorrow_boundary_planner(TomorrowBoundary); zephyr.plan_engine.premarket_constraint_loader(ConstraintState)
# [CONSUMERS] BM-BUY-02(买入融合); BM-SELL-02(卖出融合)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 尾盘决策未就绪→不操作(保持现有持仓过夜); 加仓阈值>70%高开概率; 减仓阈值>60%低开概率; 14:45-15:00决策窗口
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ClosingDecisionError(ZA-PLAN-0003)
# [TESTS] tests/plan_engine/test_plan_engine.py
# [A_module] module_id=MOD-PLAN-003 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


ClosingSessionDecision — 尾盘决策 (MOD-PLAN-003)

BM-PLAN-03 尾盘决策。14:45 尾盘决策窗口，基于今日盘中实时推演结果
与持仓状态，做加减仓决策（加仓博明天高开/减仓防明天低开/持有不动）。

核心设计（41 §3.10.4）：
    - 尾盘加仓阈值：明日高开概率 >70%
    - 尾盘减仓阈值：明日低开概率 >60%
    - 尾盘决策窗口：14:45-15:00
    - 尾盘决策未就绪→不操作（保持现有持仓过夜），宁可不操作也不在尾盘盲动

与 §3.4 的分工消歧：
    §3.4 是建仓执行窗口（把 31 号算好的目标权重落成订单），
    PLAN-03 是预测驱动调仓（基于明日高/低开概率调整已有持仓或加仓）。
    PLAN-03 产出调仓指令，§3.4 负责把指令落成限价单。

不做什么：不执行下单（归 §3.4 尾盘窗口）/ 不做盘中推演（归 BM-PLAN-01-C）

依据: 41_buy_flow §3.10.4 BM-PLAN-03
SSoT: depgraph MOD-PLAN-003
Version: 1.0.0

# [ALGO_FLOW]
# 输入: 今日盘中实时推演(BM-PLAN-01-C) + 今日持仓状态(BM-POS-01)
# 特征: 明日高开概率, 明日低开概率, 当前持仓, 尾盘决策窗口 14:45-15:00
# 算法: 高开概率>70%→加仓博高开 / 低开概率>60%→减仓防低开 / 否则→持有不动
# 输出: BoundedActionAdvice(action=ADD/REDUCE/HOLD/EXIT, price_bound, max_weight, reason)

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ── 常量（41 §3.10.4 参数默认值）──

ADD_POSITION_THRESHOLD = 0.70  # 尾盘加仓阈值（明日高开概率 >70%）
REDUCE_POSITION_THRESHOLD = 0.60  # 尾盘减仓阈值（明日低开概率 >60%）
DECISION_WINDOW_START = "14:45"  # 尾盘决策窗口开始
DECISION_WINDOW_END = "15:00"  # 尾盘决策窗口结束


class ClosingDecisionError(ValueError):
    """尾盘决策错误（ZA-PLAN-0003）——决策未就绪=不操作（保持现有持仓过夜）。

    继承 ValueError 保持向后兼容。当前实现异常向上传播由调用方捕获，
    本类为声明的错误契约锚点（供调用方 except 定向捕获）。
    """

    error_code = "ZA-PLAN-0003"


# ── 数据契约（41 §3.10.2 输出契约）──


@dataclass(frozen=True)
class BoundedActionAdvice:
    """边界内动作建议（BM-PLAN-01-C / BM-PLAN-03 产出）。

    在 TomorrowBoundary 边界内的动作建议，毫秒级。
    """

    symbol: str
    action: str  # "ADD" / "REDUCE" / "HOLD" / "EXIT"
    price_bound: tuple[float, float]  # 动作允许的价格区间（在 boundary 内）
    max_weight: float  # 动作允许的最大权重
    reason: str  # 边界内推演理由


# ── 尾盘决策引擎 ──


class ClosingSessionDecision:
    """尾盘决策引擎（MOD-PLAN-003）。

    14:45 尾盘决策窗口，基于今日盘中实时推演结果与持仓状态，
    做加减仓决策（加仓博明天高开/减仓防明天低开/持有不动）。
    """

    def decide(
        self,
        symbol: str,
        intraday_inference: dict[str, Any],
        position_state: dict[str, Any],
        high_open_prob: float = 0.0,
        low_open_prob: float = 0.0,
    ) -> BoundedActionAdvice:
        """尾盘决策。

        Args:
            symbol: 标的代码。
            intraday_inference: 今日盘中实时推演结果（BM-PLAN-01-C）。
            position_state: 今日持仓状态（BM-POS-01）。
            high_open_prob: 明日高开概率（0-1）。
            low_open_prob: 明日低开概率（0-1）。

        Returns:
            BoundedActionAdvice: 边界内动作建议。
        """
        box_upper = intraday_inference.get("box_upper", 0.0)
        box_lower = intraday_inference.get("box_lower", 0.0)
        current_weight = position_state.get("weight", 0.0)

        # 尾盘加仓：明日高开概率 >70%
        if high_open_prob > ADD_POSITION_THRESHOLD:
            return BoundedActionAdvice(
                symbol=symbol,
                action="ADD",
                price_bound=(box_lower, box_upper),
                max_weight=0.30,  # 加仓仓位上限
                reason=f"明日高开概率{high_open_prob:.1%}>{ADD_POSITION_THRESHOLD:.0%}，加仓博高开",
            )

        # 尾盘减仓：明日低开概率 >60%
        if low_open_prob > REDUCE_POSITION_THRESHOLD:
            return BoundedActionAdvice(
                symbol=symbol,
                action="REDUCE",
                price_bound=(box_lower, box_upper),
                max_weight=current_weight,
                reason=f"明日低开概率{low_open_prob:.1%}>{REDUCE_POSITION_THRESHOLD:.0%}，减仓防低开",
            )

        # 持有不动（默认）
        return BoundedActionAdvice(
            symbol=symbol,
            action="HOLD",
            price_bound=(box_lower, box_upper),
            max_weight=current_weight,
            reason="高开/低开概率均未超阈值，持有不动",
        )
