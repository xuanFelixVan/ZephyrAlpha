# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] zephyr.ex_core.daban_instant_circuit_breaker
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] （首批实盘接线前暂无，与 Kill Switch 并列的 sleeve 级盘中瞬时熔断）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 封单崩塌≥30%瞬时熔断; 梯队FRACTURE/LONE_DRAGON/COLLAPSE瞬时熔断; 量化席位>70%瞬时熔断; 三触发器按序判定先到先熔断
# [MODIFY-GUARD] 24_daban_strategy_detail.md §3.13 缺失#2（v1.9.2）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_daban_instant_circuit_breaker.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: live_data(current_seal/initial_seal) + echelon_status + quant_seat_ratio
# F1: 触发器①seal_ratio<70%→SEAL_COLLAPSE ②梯队断层→ECHELON_FRACTURE ③量化席位hard→QUANT_SEAT_HARD
# O1: {trigger, action, qty_ratio?, reason?}（熔断=INSTANT_SELL 全仓 / 未触发=MONITOR）
# [/ALGO_FLOW]
"""



打板专用瞬时风控（24_daban_strategy_detail §3.13 缺失#2 施工，首批实盘前必做）。

三触发器→瞬时熔断卖出。与 §3.6 Kill Switch 并列但优先级更高——
Kill Switch 是账户级日度熔断，本类是 sleeve 级盘中瞬时熔断。

理论背书：arXiv:2608.03616 liquidation cascade 亚临界分支——封单崩塌时
止损触发更多止损形成局部级联（88% 级联卖出 30 分钟内完成），需在级联
扩散前瞬时卖出。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: daban_instant_circuit_breaker.py
# 层: 算法
# - id: A1
#   name_zh: ① DabanInstantCircuitBreaker
#   name_en: DabanInstantCircuitBreaker
#   intro: 打板专用瞬时风控（v1.9.2 补，三触发器→瞬时熔断卖出）。
#   desc: 打板专用瞬时风控（v1.9.2 补，三触发器→瞬时熔断卖出）。；公共方法（定义序）: check_instant_break；源码 L71-L105
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: DabanInstantCircuitBreaker
#   downstream: （首批实盘接线前暂无，与 Kill Switch 并列的 sleeve 级盘中瞬时熔断）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DabanInstantCircuitBreaker",
]


@dataclass
class DabanInstantCircuitBreaker:
    """打板专用瞬时风控（v1.9.2 补，三触发器→瞬时熔断卖出）。"""

    seal_collapse_threshold: float = 0.30  # 封单瞬间消失30%即熔断
    quant_seat_hard_threshold: float = 0.70  # 量化席位买入占比>70%
    # 梯队断层动作集（spec 类属性，非 dataclass 字段）
    echelon_fracture_actions = {"FRACTURE", "LONE_DRAGON", "COLLAPSE"}

    def check_instant_break(
        self, position: dict, live_data: dict, echelon_status: str, quant_seat_ratio: float
    ) -> dict:
        """三触发器按序检查，任一命中→瞬时熔断全卖；全不命中→MONITOR。"""
        seal_ratio = live_data.get("current_seal", 0) / max(live_data.get("initial_seal", 1), 1)
        if seal_ratio < (1 - self.seal_collapse_threshold):  # 触发器①：封单崩塌
            return {
                "trigger": "SEAL_COLLAPSE",
                "action": "INSTANT_SELL",
                "qty_ratio": 1.0,
                "reason": f"封单崩塌{(1 - seal_ratio):.0%}≥30%→瞬时熔断",
            }
        if echelon_status in self.echelon_fracture_actions:  # 触发器②：梯队断层
            return {
                "trigger": "ECHELON_FRACTURE",
                "action": "INSTANT_SELL",
                "qty_ratio": 1.0,
                "reason": f"梯队{echelon_status}→瞬时熔断清仓",
            }
        if quant_seat_ratio > self.quant_seat_hard_threshold:  # 触发器③：量化席位hard预警
            return {
                "trigger": "QUANT_SEAT_HARD",
                "action": "INSTANT_SELL",
                "qty_ratio": 1.0,
                "reason": f"量化席位{quant_seat_ratio:.0%}>70%→瞬时熔断",
            }
        return {"trigger": None, "action": "MONITOR"}
