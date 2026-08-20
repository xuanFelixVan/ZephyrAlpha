# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] zephyr.ex_core.daban_exit_decision
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] zephyr.ex_core.daban_pit_safety（PIT 回测框架调用次日出场）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 低开≤-5%硬止损全卖; 持仓≥3天未晋级时间退出; 炸板+退潮硬退出; 高开≥5%全卖/≥3%卖半; cost_basis<=0拒绝决策(人工复核)
# [MODIFY-GUARD] 24_daban_strategy_detail.md §3.13 缺失#1（v1.9.2）/ 缺失#7（v1.9.2，Phase 5 候选）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] cost_basis<=0→HOLD+人工复核（不抛异常，Fail-Closed 不误导卖出）
# [TESTS] tests/ex_core/test_daban_exit_decision.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: position(cost_basis/consecutive_board/exploded) + auction_data(open_price) + forecast(phase/divergence) + holding_days
# I2: t1_data(close/high/limit_up_price/seal_ratio) + echelon_status（classify_position_status 输入）
# F1: NextDayExitDecision.decide——硬退出①低开闷杀②持仓超时③炸板退潮→高开两档止盈→分歧度软退出→连板持有
# F2: classify_position_status——T+1涨停收盘+封单存在+梯队非孤板→consecutive_board; 触涨停未封收→exploded（回写 position）
# F3: reflush_next_day_exit_decision——反核后次日：高开≥5%止盈/低开≤-3%止损/持5天时间止盈/其余观察
# O1: {action, qty_ratio, reason}（action∈STOP_LOSS/SELL_ALL/SELL_HALF/HOLD）
# [/ALGO_FLOW]
"""打板次日出场决策族（24_daban_strategy_detail §3.13 缺失#1/#7 施工）。

缺失#1 NextDayExitDecision（首批实盘前必做）：T+1 闭环断裂修复——
T 日打板买入后 T+1 日开盘竞价的完整出场决策（硬退出三件套 + 高开两档止盈
+ 分歧度软退出 + 连板晋级持有）。classify_position_status 补全 decide()
依赖的 consecutive_board/exploded 字段填充算法（v1.9.6）。

缺失#7 reflush_next_day_exit_decision（Phase 5 候选）：反核入场后次日
不同走势的分别出场决策（§3.12 静态出场参数的动态化补全）。

理论背书：北大 Jiang & Li 理性预期模型——封死涨停平均隔夜收益 +2.43%，
打开涨停平均回撤 -5.25%（回撤不对称性支撑"低开闷杀硬止损"纪律）。
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "NextDayExitDecision",
    "reflush_next_day_exit_decision",
]


@dataclass
class NextDayExitDecision:
    """次日出场完整决策（v1.9.2 补，整合 forecast_next_day_premium + 20号三档退出）。"""

    hard_exit_premium_low: float = -0.05  # 低开≥5%→硬止损全卖（核按钮闷杀）
    hard_exit_consecutive_loss: int = (
        3  # 连续3板未晋级→硬退出（保留字段，v1.9.2 spec 定义，decide 以 max_holding_days 落地）
    )
    soft_exit_divergence: float = 0.5  # 分歧度>0.5→软退出
    take_profit_tier1: float = 0.03  # 高开≥3%→竞价卖50%
    take_profit_tier2: float = 0.05  # 高开≥5%→全卖
    max_holding_days: int = 3  # 持仓≥3天未晋级→硬退出

    def decide(self, position: dict, auction_data: dict, forecast: dict, holding_days: int) -> dict:
        """T+1 日开盘出场决策。判定顺序即 spec 优先级：硬退出→止盈→软退出→持有。"""
        cost_basis = position.get("cost_basis", 0)
        if cost_basis <= 0:  # 退化输入：成本价缺失/非法→不决策，人工复核（Fail-Closed）
            return {"action": "HOLD", "qty_ratio": 0.0, "reason": f"cost_basis={cost_basis}非法→拒绝决策，人工复核"}
        open_premium = auction_data.get("open_price", 0) / cost_basis - 1
        if open_premium <= self.hard_exit_premium_low:  # 硬退出①：低开闷杀
            return {"action": "STOP_LOSS", "qty_ratio": 1.0, "reason": f"核按钮闷杀 open={open_premium:.1%}"}
        if holding_days >= self.max_holding_days and not position.get("consecutive_board", False):  # 硬退出②：持仓超时
            return {"action": "SELL_ALL", "qty_ratio": 1.0, "reason": f"持仓{holding_days}天未晋级→时间退出"}
        if position.get("exploded", False) and forecast.get("phase") == "退潮":  # 硬退出③：炸板+退潮
            return {"action": "SELL_ALL", "qty_ratio": 1.0, "reason": "炸板+退潮→硬退出"}
        if open_premium >= self.take_profit_tier2:  # 高开止盈：分批
            return {"action": "SELL_ALL", "qty_ratio": 1.0, "reason": f"高开{open_premium:.1%}≥5%→全卖"}
        if open_premium >= self.take_profit_tier1:
            return {"action": "SELL_HALF", "qty_ratio": 0.5, "reason": f"高开{open_premium:.1%}≥3%→竞价卖50%"}
        if forecast.get("divergence", 0) > self.soft_exit_divergence:  # 软退出：分歧度高
            return {"action": "SELL_HALF", "qty_ratio": 0.5, "reason": "分歧度>0.5→分批退"}
        if position.get("consecutive_board", False) and open_premium > 0:  # 连板晋级者持有
            return {"action": "HOLD", "qty_ratio": 0.0, "reason": "连板晋级+高开→持有"}
        return {"action": "HOLD", "qty_ratio": 0.0, "reason": "等盘中确认"}

    @staticmethod
    def classify_position_status(position: dict, t1_data: dict, echelon_status: str) -> dict:
        """持仓状态分类（v1.9.6 补，填充 consecutive_board/exploded 字段——decide() 依赖此两字段）。

        连板晋级判断：T+1日涨停收盘+封单存在+梯队非孤板（与 §3.1 classify_echelon_health 联动）；
        炸板判断：T日封板后 T+1日盘中打开（触涨停但未封收，与 §3.13#2 DabanInstantCircuitBreaker 联动）。
        就地回写 position 并返回分类结果。
        """
        t1_close = t1_data.get("close", 0)
        t1_high = t1_data.get("high", 0)
        limit_up_price = t1_data.get("limit_up_price", 0)
        t1_seal_ratio = t1_data.get("seal_ratio", 0)  # T+1日封流比（0=无封单）
        # ① 连板晋级：T+1日收盘涨停 + 封单存在 + 梯队非孤板
        is_limit_up_close = limit_up_price > 0 and abs(t1_close - limit_up_price) < 0.01
        has_seal = t1_seal_ratio > 0.001  # 封流比>0.1%
        is_in_echelon = echelon_status not in ("LONE_DRAGON", "COLLAPSE")
        consecutive_board = is_limit_up_close and has_seal and is_in_echelon
        # ② 炸板：T+1日盘中触及涨停但未封住（最高价≈涨停价但收盘<涨停价）
        touched_limit = limit_up_price > 0 and t1_high >= limit_up_price * 0.999
        not_sealed_close = not is_limit_up_close
        exploded = touched_limit and not_sealed_close
        position["consecutive_board"] = consecutive_board
        position["exploded"] = exploded
        return {
            "consecutive_board": consecutive_board,
            "exploded": exploded,
            "reason": (
                f"连板晋级={consecutive_board}（涨停收盘={is_limit_up_close}+封单={has_seal}+梯队={is_in_echelon}），"
                f"炸板={exploded}（触涨停={touched_limit}+未封收={not_sealed_close}）"
            ),
        }


def reflush_next_day_exit_decision(position: dict, auction_data: dict, holding_days: int) -> dict:
    """反核二次出场决策（v1.9.2 补，Phase 5 候选）——§3.12 反核后次日不同走势的分别出场决策。"""
    cost_basis = position.get("cost_basis", 0)
    if cost_basis <= 0:  # 退化输入：成本价缺失/非法→不决策，人工复核
        return {"action": "HOLD", "qty_ratio": 0.0, "reason": f"cost_basis={cost_basis}非法→拒绝决策，人工复核"}
    open_premium = auction_data.get("open_price", 0) / cost_basis - 1
    if open_premium >= 0.05:
        return {"action": "SELL_ALL", "qty_ratio": 1.0, "reason": "反核后高开≥5%→止盈"}
    if -0.03 < open_premium < 0.05:
        if holding_days >= 5:
            return {"action": "SELL_ALL", "qty_ratio": 1.0, "reason": "反核持有5天→时间止盈"}
        return {"action": "HOLD", "qty_ratio": 0.0, "reason": "低开>-3%→观察等反抽"}
    if open_premium <= -0.03:
        return {"action": "STOP_LOSS", "qty_ratio": 1.0, "reason": "低开≤-3%→止损"}
    if auction_data.get("is_limit_down", False):
        return {"action": "HOLD", "qty_ratio": 0.0, "reason": "继续跌停→持有等反抽"}
    return {"action": "HOLD", "qty_ratio": 0.0, "reason": "观察"}
