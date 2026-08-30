# [BLUEPRINT] 90_methodology_open_questions.md §19（v2.0.0 裁定）
# [MODULE] zephyr.ex_sor.core.execution_route_policy
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] 无（纯配置+判定）
# [CONSUMERS] 执行层下单入口（接线待排期，本批仅交付模块本体）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 默认限价单直投；打板不可拆单；算法族降级远期不启用；拆分仅防异常交易监控
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 非正订单量→ValueError
# [TESTS] tests/ex_sor/test_execution_route_policy.py
# [A_module] module_id=MOD-XS-ROUTE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
D_EX_SOR — 执行路由策略（90 号 Phase1 项③：默认限价单 + 打板专用路径）

裁定真源：90_methodology_open_questions.md §19（v2.0.0）：
  ① 删除"单笔>5% ADV 切算法执行"硬条款——个人资金量级永远触不到，伪精确；
  ② 默认单笔限价单（miniQMT 10 笔/秒限制对个人策略绰绰有余）；
  ③ 打板买入逻辑上不可拆单（抢排队优先级）→打板专用执行路径：集合竞价/早盘
     瞬时单笔限价（涨停价）申报+封单强度过滤（封成比≥5%）；
  ④ 防异常交易监控：单笔>该票分钟级均量 5 倍→分 2-3 笔、间隔 3-5 秒
     （2026-04 程序化新规，避免单笔记入交易所异常交易监控）；
  ⑦ TWAP/VWAP/POV/ICEBERG 代码保留但降级远期——单票百万+前不启用
     （algo_enabled=False 时本策略永不路由 ALGO）。

注意：本模块为 90 号 Phase1 交付物，MATURITY=testing；与 MOD-XS-011 算法选择器
/OrderGateway 的生产接线挂起待 Owner（宪章 B-007 纪律）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: order_qty 参数
#   fields: 参数 order_qty，类型注解 Decimal
#   code: execution_route_policy.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: minute_avg_volume 参数
#   fields: 参数 minute_avg_volume，类型注解 Decimal
#   code: execution_route_policy.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: is_daban 参数
#   fields: 参数 is_daban（无注解）
#   code: execution_route_policy.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: seal_ratio 参数
#   fields: 参数 seal_ratio（无注解）
#   code: execution_route_policy.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① route_order
#   name_en: route_order
#   intro: 执行路由判定。
#   desc: 执行路由判定。 Args: order_qty: 订单数量（股） minute_avg_volume: 该票分钟级均量（股） is_daban: 是否打板策略订单 seal_ra…；源码 L121-L186
#   inputs: order_qty minute_avg_volume is_daban seal_ratio policy
#   outputs: RouteDecision
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: RouteDecision
#   name_en: RouteDecision
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 执行层下单入口（接线待排期，本批仅交付模块本体）
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

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

__all__ = [
    "ExecutionRoute",
    "ExecutionRoutePolicy",
    "RouteDecision",
    "route_order",
]


class ExecutionRoute(str, Enum):
    """执行路由（90 号 §19 裁定②③⑦）。"""

    DIRECT_LIMIT = "direct_limit"  # 默认：单笔限价单直投
    DABAN_LIMIT = "daban_limit"  # 打板专用：涨停价单笔限价申报（不可拆单）
    ALGO = "algo"  # 算法执行（TWAP/VWAP/POV/ICEBERG）——远期，默认不启用


@dataclass(frozen=True)
class ExecutionRoutePolicy:
    """执行路由策略配置（C 类可调参数）。"""

    default_route: ExecutionRoute = ExecutionRoute.DIRECT_LIMIT
    algo_enabled: bool = False  # ⑦ 算法族降级远期
    daban_seal_ratio_min: Decimal = Decimal("0.05")  # ③ 封成比≥5% 过滤
    abnormal_volume_multiplier: Decimal = Decimal("5")  # ④ 分钟级均量 5 倍阈值
    split_parts: int = 3  # ④ 分 2-3 笔（取 3）
    split_interval_seconds: int = 3  # ④ 间隔 3-5 秒（取 3）


@dataclass(frozen=True)
class RouteDecision:
    """路由决策（可审计）。"""

    route: ExecutionRoute
    allowed: bool  # 打板封单强度过滤=False 时禁止申报
    parts: int  # 拆分笔数（1=不拆）
    split_interval_seconds: int  # 拆单间隔（秒；不拆=0）
    reason: str


def route_order(
    order_qty: Decimal,
    minute_avg_volume: Decimal,
    *,
    is_daban: bool = False,
    seal_ratio: Decimal | None = None,
    policy: ExecutionRoutePolicy | None = None,
) -> RouteDecision:
    """执行路由判定。

    Args:
        order_qty: 订单数量（股）
        minute_avg_volume: 该票分钟级均量（股）
        is_daban: 是否打板策略订单
        seal_ratio: 封成比（打板必填；<5% 拒绝申报）
        policy: 路由策略配置（None=默认）

    Returns:
        RouteDecision 路由决策
    """
    if order_qty <= 0:
        raise ValueError("订单数量必须为正")
    if minute_avg_volume <= 0:
        raise ValueError("分钟级均量必须为正")
    cfg = policy or ExecutionRoutePolicy()

    # ③ 打板专用路径：单笔限价（涨停价由调用方定价），逻辑上不可拆单
    if is_daban:
        seal = seal_ratio if seal_ratio is not None else Decimal("0")
        if seal < cfg.daban_seal_ratio_min:
            return RouteDecision(
                route=ExecutionRoute.DABAN_LIMIT,
                allowed=False,
                parts=1,
                split_interval_seconds=0,
                reason=f"封成比 {seal} < {cfg.daban_seal_ratio_min}，封单强度过滤拒绝申报",
            )
        return RouteDecision(
            route=ExecutionRoute.DABAN_LIMIT,
            allowed=True,
            parts=1,
            split_interval_seconds=0,
            reason=f"打板专用路径：封成比 {seal} 达标，单笔涨停价限价申报（不可拆单）",
        )

    # ④ 防异常交易监控：单笔>分钟级均量 5 倍→简单拆分
    if order_qty > cfg.abnormal_volume_multiplier * minute_avg_volume:
        return RouteDecision(
            route=ExecutionRoute.DIRECT_LIMIT,
            allowed=True,
            parts=cfg.split_parts,
            split_interval_seconds=cfg.split_interval_seconds,
            reason=(
                f"单笔超分钟级均量 {cfg.abnormal_volume_multiplier} 倍，"
                f"分 {cfg.split_parts} 笔间隔 {cfg.split_interval_seconds}s"
            ),
        )

    # ② 默认单笔限价单（① 5%ADV 硬条款已删除；⑦ 算法族 algo_enabled=False 不路由）
    return RouteDecision(
        route=ExecutionRoute.DIRECT_LIMIT,
        allowed=True,
        parts=1,
        split_interval_seconds=0,
        reason="默认限价单直投",
    )
