# [BLUEPRINT] MOD-EX-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] zephyr.ex_core.daban_execution
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] （首批实盘接线前暂无；G22 执行层落线后由 sleeve 组装消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 首批60%+回封30%+余量 opportunistic 三段分笔; SaR>2%→目标量削30%; 封板概率≥85%且封流比≥5%→追板市价单/50-85%→板前埋伏限价单; 容量=SaR/封单/流通盘/NAV 四约束取最小
# [MODIFY-GUARD] 24_daban_strategy_detail.md §3.13 缺失#4（v1.9.2+v1.9.3 升级）/ §3.14 缺失#11/#12（v1.9.3，Phase 3）
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空订单簿→depth=0/concentration=0 兜底（SaR 放大→保守方向，Fail-Closed）; price<=0→nav 容量=0（拒绝下仓，Fail-Closed）
# [TESTS] tests/ex_core/test_daban_execution.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: queue_position/seal_volume/order_volume/distance_to_mid（填充概率）; order_book(bid_levels)（SaR）
# I2: near_limit/seal_strength/volume_surge/time_to_close_min（时点决策）
# I3: nav/seal_volume/float_shares/order_book/price（动态容量）
# F1: DabanExecutionAlgorithm——指数填充概率+SaR 前置检查→FIRST/REFLUSH/RESERVE 三段执行计划
# F2: DabanTimingDecision——封板概率估算→CHASE(MARKET)/AMBUSH(LIMIT)/WAIT
# F3: DynamicCapacityCalculator——sar/seal/float/nav 四约束取 min→max_qty+binding_constraint
# O1: 执行计划 list[dict] / 时点决策 dict / 容量测算 dict
# [/ALGO_FLOW]
"""



打板执行族（24_daban_strategy_detail §3.13 缺失#4 + §3.14 缺失#11/#12 施工，Phase 3）。

缺失#4 DabanExecutionAlgorithm（分笔建仓，容量管理执行层）：v1.9.3 升级
arXiv:2607.28323 Passive Market Impact——限价单填充概率随距 midprice 距离指数
衰减 λ(d)=λ₀·exp(-κd)；v1.9.3 整合 arXiv:2603.09164 SaR（Slippage-at-Risk）
前瞻性流动性风险——分笔建仓前先评估订单簿可承受冲击量，SaR>2% 削目标量 30%。
v1.9.5 补 arXiv:2608.02002 Hawkes 长记忆核（封单增减是自激励点过程）；
v1.9.7 补 arXiv:2608.00988 扩散价格动力学悖论（拆单不泄露信息理论依据）。

缺失#11 DabanTimingDecision（打板时点决策）：§3.5 输出 BOARD 后的具体下单时点
——封板瞬间追板（市价单确定性高冲击大）vs 板前埋伏（限价单成本低填充概率低），
在"追板成交概率"vs"埋伏等待时间"间权衡。

缺失#12 DynamicCapacityCalculator（容量动态测算）：§3.4 13 约束链是静态阈值，
本类基于实时流动性（封单量/委买队列/流通盘）动态测算可下仓量，是 §3.13#4
分笔建仓的前置"可下多少仓"测算；SaR 直接映射容量上限（arXiv:2603.09164）。

spec 转写登记（语义锁定不偏移）：
  ① DabanTimingDecision._estimate_seal_probability 下限为 0.5（base 0.5 + 全部
     非负增量），故 decide_timing 两条 WAIT 分支（seal_prob<50%）按 spec 公式
     不可达——逐字保留 spec 分支结构，概率模型校准属 Phase 3 回测工程。
  ② AMBUSH 的 limit_price 为 spec 占位标记 "涨停价-0.01"（实际限价由 G22
     执行层按价格笼子规则解析，本类只产出时点/单型决策）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: daban_execution.py
# 层: 算法
# - id: A1
#   name_zh: ① DabanExecutionAlgorithm
#   name_en: DabanExecutionAlgorithm
#   intro: 打板分笔建仓（v1.9.2 补，v1.9.3 升级 passive impact 理论背书）。
#   desc: 打板分笔建仓（v1.9.2 补，v1.9.3 升级 passive impact 理论背书）。依赖 G22 执行层。；公共方法（定义序）: estimate_fill_probability, estimate_sar…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② DabanTimingDecision
#   name_en: DabanTimingDecision
#   intro: 打板时点决策（v1.9.3 补，追板 vs 埋伏权衡）。
#   desc: 打板时点决策（v1.9.3 补，追板 vs 埋伏权衡）。；公共方法（定义序）: decide_timing；源码 L172-L210
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ DynamicCapacityCalculator
#   name_en: DynamicCapacityCalculator
#   intro: 打板容量动态测算（v1.9.3 补，实时流动性→可下仓量）。
#   desc: 打板容量动态测算（v1.9.3 补，实时流动性→可下仓量）。与 §3.4 13 约束链（静态阈值）互补。；公共方法（定义序）: calculate；源码 L214-L247
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: DabanExecutionAlgorithm, DabanTimingDecision, DynamicCapacityCalculator
#   downstream: （首批实盘接线前暂无；G22 执行层落线后由 sleeve 组装消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

__all__: Final = [
    "DabanExecutionAlgorithm",
    "DabanTimingDecision",
    "DynamicCapacityCalculator",
]


@dataclass
class DabanExecutionAlgorithm:
    """打板分笔建仓（v1.9.2 补，v1.9.3 升级 passive impact 理论背书）。依赖 G22 执行层。"""

    fill_decay_kappa: float = 0.20  # 填充概率指数衰减率（被动 impact 校准）
    fill_base_lambda: float = 1.0  # 基础填充强度（涨停板=封单强，基础高）
    price_impact_eta: float = 0.001  # 线性响应系数（OFI→ΔP）
    sar_alpha: float = 0.95  # SaR 分位数（95% 滑点风险）
    first_batch_ratio: float = 0.6  # 封板瞬间首批60%
    reflush_batch_ratio: float = 0.3  # 回封补量30%
    cancel_timeout_sec: int = 30  # 30秒未成交考虑撤单

    def estimate_fill_probability(
        self, queue_position: int, seal_volume: int, order_volume: int, distance_to_mid: float = 0.0
    ) -> float:
        """指数填充概率衰减（v1.9.3 passive impact 理论）：基础强度×距离衰减×队列位置衰减。"""
        base_prob = min(seal_volume / max(order_volume * 10, 1), 1.0)  # 基础填充强度（封单量/订单量比）
        distance_decay = math.exp(-self.fill_decay_kappa * distance_to_mid)  # 距 midprice 指数衰减
        position_decay = (1 - 0.15) ** queue_position  # 队列位置衰减（保留 v1.9.2 启发式，作为补充）
        return base_prob * distance_decay * position_decay

    def estimate_sar(self, order_book: dict, order_volume: int) -> float:
        """Slippage-at-Risk 前瞻性滑点评估（v1.9.3）：深度浅+集中度高→脆弱流动性→SaR 大。
        空订单簿→depth=0/concentration=0 兜底（sar=order_volume×eta，保守方向）。"""
        bid_levels = order_book.get("bid_levels", [])
        depth = sum(level["volume"] for level in bid_levels[:5])
        concentration = (max(level["volume"] for level in bid_levels) / max(depth, 1)) if bid_levels else 0.0
        return (order_volume / max(depth, 1)) * (1 + concentration) * self.price_impact_eta

    def build_execution_plan(
        self, target_volume: int, seal_volume: int, queue_position: int, order_book: dict = None
    ) -> list[dict]:
        """三段分笔执行计划：SaR 前置检查→FIRST 封板瞬间→REFLUSH 回封补量→RESERVE 余量伺机。"""
        plan = []
        if order_book:  # v1.9.3: 前置 SaR 检查——若 SaR 超阈值则削减 target_volume
            sar = self.estimate_sar(order_book, target_volume)
            if sar > 0.02:  # 滑点>2% 削减
                target_volume = int(target_volume * 0.7)
                plan.append({"batch": "SAR_TRIM", "qty": target_volume, "reason": f"SaR={sar:.3f}>2%→削30%"})
        first_qty = int(target_volume * self.first_batch_ratio)
        plan.append(
            {
                "batch": "FIRST",
                "qty": first_qty,
                "timing": "SEAL_INSTANT",
                "fill_prob": self.estimate_fill_probability(queue_position, seal_volume, first_qty),
            }
        )
        reflush_qty = int(target_volume * self.reflush_batch_ratio)
        plan.append(
            {
                "batch": "REFLUSH",
                "qty": reflush_qty,
                "timing": "RESEAL",
                "fill_prob": self.estimate_fill_probability(queue_position + 5, seal_volume, reflush_qty),
            }
        )
        reserve_qty = target_volume - first_qty - reflush_qty
        plan.append({"batch": "RESERVE", "qty": reserve_qty, "timing": "OPPORTUNISTIC", "fill_prob": 0.3})
        return plan


@dataclass
class DabanTimingDecision:
    """打板时点决策（v1.9.3 补，追板 vs 埋伏权衡）。"""

    chase_threshold: float = 0.85  # 封板概率>85%→追板（市价单）
    ambush_threshold: float = 0.50  # 封板概率50-85%→板前埋伏（限价单）
    max_ambush_wait_sec: int = 120  # 埋伏最长等待120秒
    seal_strength_required: float = 0.05  # 封流比>5%才追板

    def decide_timing(
        self, near_limit: bool, seal_strength: float, volume_surge: float, time_to_close_min: int
    ) -> dict:
        """打板时点决策：封板概率≥85%+封流比≥5%→追板；50-85%→板前埋伏；<50%→观望。"""
        seal_prob = self._estimate_seal_probability(near_limit, seal_strength, volume_surge)  # 封板概率估算
        if seal_prob >= self.chase_threshold and seal_strength >= self.seal_strength_required:
            return {
                "action": "CHASE",
                "order_type": "MARKET",
                "reason": f"封板概率{seal_prob:.0%}>85%+封流比{seal_strength:.1%}>5%→追板",
            }
        if seal_prob >= self.ambush_threshold:
            return {
                "action": "AMBUSH",
                "order_type": "LIMIT",
                "limit_price": "涨停价-0.01",  # spec 占位标记，实际限价由 G22 执行层解析
                "max_wait": self.max_ambush_wait_sec,
                "reason": f"封板概率{seal_prob:.0%}50-85%→板前埋伏",
            }
        if time_to_close_min < 30 and seal_prob < self.ambush_threshold:
            return {"action": "WAIT", "reason": f"封板概率{seal_prob:.0%}<50%+临近收盘→观望"}
        return {"action": "WAIT", "reason": f"封板概率{seal_prob:.0%}<50%→观望"}

    def _estimate_seal_probability(self, near_limit, seal_strength, volume_surge):
        # 简化概率模型（下限 0.5，校准属 Phase 3 回测工程——spec 转写登记①）
        prob = 0.5
        if near_limit:
            prob += 0.2
        prob += min(seal_strength * 5, 0.2)
        prob += min(volume_surge * 0.1, 0.15)
        return min(prob, 0.95)


@dataclass
class DynamicCapacityCalculator:
    """打板容量动态测算（v1.9.3 补，实时流动性→可下仓量）。与 §3.4 13 约束链（静态阈值）互补。"""

    max_sar_tolerance: float = 0.015  # SaR 容忍度 1.5%
    max_seal_ratio: float = 0.10  # 单票不超过封单量 10%
    max_float_turnover: float = 0.02  # 单票不超过流通盘 2%
    nav_ratio_cap: float = 0.05  # C12 单票 ≤5% NAV

    def calculate(self, nav: float, seal_volume: int, float_shares: int, order_book: dict, price: float) -> dict:
        """动态测算可下仓量：sar/seal/float/nav 四约束取最小，返回 binding 约束。"""
        # ① SaR 约束——滑点风险反推容量：SaR(q)=(q/depth)·(1+concentration)·eta ≤ max_sar_tolerance
        bid_levels = order_book.get("bid_levels", [])
        depth = sum(level["volume"] for level in bid_levels[:5])
        concentration = (max(level["volume"] for level in bid_levels) / max(depth, 1)) if bid_levels else 0.0
        eta = 0.001
        sar_capacity = int(self.max_sar_tolerance * depth / max((1 + concentration) * eta, 0.001))
        seal_capacity = int(seal_volume * self.max_seal_ratio)  # ② 封单量约束
        float_capacity = int(float_shares * self.max_float_turnover)  # ③ 流通盘约束
        nav_capacity = (
            int(nav * self.nav_ratio_cap / price) if price > 0 else 0
        )  # ④ NAV 约束（C12）；price<=0→0（Fail-Closed）
        capacities = {
            "sar": sar_capacity,
            "seal": seal_capacity,
            "float": float_capacity,
            "nav": nav_capacity,
        }  # 取最小值
        binding = min(capacities, key=capacities.get)
        return {
            "max_qty": capacities[binding],
            "binding_constraint": binding,
            "all_constraints": capacities,
            "reason": f"binding={binding}({capacities[binding]})→可下{capacities[binding]}股",
        }
