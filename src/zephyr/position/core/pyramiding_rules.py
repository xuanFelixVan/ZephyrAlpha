# [BLUEPRINT] MOD-POS-027 | docs/03_modules/_domain_position/pyramiding_rules/blueprint.md
# [CORE-ALGORITHM] P3-01/P3-02 加仓资格门+金字塔加仓规则（晨审重点：金字塔递减比例/总上限/禁补亏损仓红线）
# [MODULE] zephyr.position.core.pyramiding_rules
# [DOMAIN] D_POSITION
# [DEPENDENCIES] 无（纯函数核，零 IO；行情/情绪段/熔断级由调用方注入）
# [CONSUMERS] TDM-P-P3-01（加仓资格门）；TDM-P-P3-02（金字塔加仓规则）；P 流加仓链（待接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 资格四重门逐门短路留 reason（浮盈门/情绪段门/亲和度门/熔断门）; 现价≤成本恒拒（禁补亏损仓=红线, LEVEL_GATE 前置）; 情绪段只放行 IGNITION/EXPANSION; 金字塔三规则=递减（首加=剩余预算 1/2 逐次减半）+阶梯（较上次买价涨幅≥ladder_min 才加）+限次（≤3 次）; 跌破上次加仓价=停止后续计划; 分笔金额 Decimal-only 分数化精确拒 float; 同输入必同输出(frozen)
# [MODIFY-GUARD] docs/03_modules/_domain_position/pyramiding_rules/blueprint.md + 地图节点 TDM-P-P3-01/P3-02
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 非法金额（float/负数）/未知情绪段/未知熔断级/负分笔数 → PyramidingError（fail-closed）
# [TESTS] tests/position/test_pyramiding_rules.py
# [TTL] permanent
"""PyramidingRules — 加仓资格门 + 金字塔加仓规则（MOD-POS-027，TDM-P-P3-01/02）。

**P3-01 加仓资格四重门**（全过才进规则层，节点真源逐条）：
①只加浮盈仓（现价>成本，**禁补亏损仓=红线**）；②情绪段权限（点火/扩张段才开
加仓，退潮/亢奋关）；③策略亲和度>0（该策略在当前段的适配为正）；④非熔断禁加期
（日亏 4% 熔断=L2 触发时全禁，白名单窄门归 defensive_asset_whitelist 管辖）。

**P3-02 金字塔三规则**（怎么加）：
递减——首加占剩余预算 50%，逐次减半（越加越少防重仓在顶部）；阶梯——较上次
买价涨幅 ≥2.5%（区间 2.5-3% 取下限，config 可调）才加下一笔，禁止平加；
限次——最多 3 次。**跌破上次加仓价=停止后续计划**；加仓=新交易，需重新确认
入场条件仍成立（confirm_entry_ok 旗标）。

查重分工（蓝图 §1）：defensive_asset_whitelist（MOD-POS-026）=熔断期**护盘
白名单**买入窄门（L2/L3 特例通道）；本件=**正常行情**的浮盈仓金字塔加仓
（P3 链常态路径）。position_sizing_engine=首仓 sizing。正交不重叠。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from enum import Enum

# CircuitLevel 复用同域同语义枚举（defensive_asset_whitelist 同真源=X-R1-01 熔断五级，向内收禁第二定义）
from zephyr.position.core.defensive_asset_whitelist import CircuitLevel

_QUANT = Decimal("0.01")


class PyramidingError(ValueError):
    """非法输入（fail-closed）。"""


class PyramidingPhase(str, Enum):
    """情绪五段（真源=情绪周期轴；本模块只消费权限语义）。"""

    ICE = "ICE"  # 冰点
    IGNITION = "IGNITION"  # 点火（允许加仓）
    EXPANSION = "EXPANSION"  # 扩张（允许加仓）
    EXCITEMENT = "EXCITEMENT"  # 亢奋（关闭加仓）
    EBB = "EBB"  # 退潮（关闭加仓）


class GateCode(str, Enum):
    """资格门失败原因码（逐门短路，首败即拒）。"""

    NOT_PROFITABLE = "NOT_PROFITABLE"  # ①禁补亏损仓（红线）
    PHASE_CLOSED = "PHASE_CLOSED"  # ②情绪段关闭
    AFFINITY_NOT_POSITIVE = "AFFINITY_NOT_POSITIVE"  # ③亲和度≤0
    CIRCUIT_BAN = "CIRCUIT_BAN"  # ④熔断禁加期
    MAX_TRANCHE = "MAX_TRANCHE"  # 限次
    LADDER_NOT_MET = "LADDER_NOT_MET"  # 阶梯未到
    BELOW_LAST_ADD = "BELOW_LAST_ADD"  # 跌破上次加仓价=停止计划
    ENTRY_NOT_RECONFIRMED = "ENTRY_NOT_RECONFIRMED"  # 未重新确认入场条件
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    ALLOWED = "ALLOWED"


_PHASES_ALLOW: frozenset[PyramidingPhase] = frozenset(
    {PyramidingPhase.IGNITION, PyramidingPhase.EXPANSION}
)
_CIRCUIT_BAN_LEVELS: frozenset[CircuitLevel] = frozenset(
    {CircuitLevel.L2, CircuitLevel.L3, CircuitLevel.L4}
)


@dataclass(frozen=True)
class PyramidingConfig:
    """金字塔参数（P3-02：递减 50% 减半 / 阶梯 2.5-3% 取下限 / 限次 3）。"""

    max_tranches: int = 3
    halving_ratio_numer: int = 1  # 首加=剩余预算×1/2，逐次减半（分数精确）
    halving_ratio_denom: int = 2
    ladder_min_pct: float = 0.025  # 阶梯下限 2.5%（区间 2.5-3% 取下限）

    def __post_init__(self) -> None:
        if self.max_tranches < 1:
            raise PyramidingError(f"max_tranches ≥1: {self.max_tranches}")
        if not (0 < self.halving_ratio_numer < self.halving_ratio_denom):
            raise PyramidingError(
                f"递减比例须 0 < numer < denom: {self.halving_ratio_numer}/{self.halving_ratio_denom}"
            )
        if not (0.0 < self.ladder_min_pct < 1.0):
            raise PyramidingError(f"ladder_min_pct ∈ (0,1): {self.ladder_min_pct}")


DEFAULT_PYRAMIDING_CONFIG = None  # 占位杜绝模块级急切实例化——用 get_default_config()


def get_default_config() -> PyramidingConfig:
    """默认配置惰性工厂（S4-C 零副作用）。"""
    return PyramidingConfig()


@dataclass(frozen=True)
class PyramidingGateRequest:
    """P3-01 资格四重门请求。"""

    current_price: Decimal
    cost_price: Decimal  # 持仓成本
    sentiment_phase: PyramidingPhase | str
    strategy_affinity: float  # 该策略在当前段的适配度（>0 才放行）
    circuit_level: CircuitLevel | str


def _to_phase(v: PyramidingPhase | str) -> PyramidingPhase:
    try:
        return PyramidingPhase(v)
    except ValueError as exc:
        raise PyramidingError(f"未知情绪段: {v!r}") from exc


def _to_circuit(v: CircuitLevel | str) -> CircuitLevel:
    try:
        return CircuitLevel(v)
    except ValueError as exc:
        raise PyramidingError(f"未知熔断级: {v!r}") from exc


def _require_decimal_amount(value: Decimal, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, Decimal):
        raise PyramidingError(f"{name} 必须为 Decimal（拒 float）")
    if value < Decimal(0):
        raise PyramidingError(f"{name} 不可为负")
    return value


def check_pyramiding_eligibility(
    req: PyramidingGateRequest,
) -> tuple[bool, GateCode]:
    """P3-01 资格四重门（纯函数；返回 (allowed, code)，首败即拒）。

    门序：①浮盈红线 → ②情绪段 → ③亲和度 → ④熔断禁加期。
    """
    price = _require_decimal_amount(req.current_price, "current_price")
    cost = _require_decimal_amount(req.cost_price, "cost_price")
    phase = _to_phase(req.sentiment_phase)
    level = _to_circuit(req.circuit_level)

    # 门①：只加浮盈仓（红线）
    if price <= cost:
        return False, GateCode.NOT_PROFITABLE
    # 门②：情绪段权限
    if phase not in _PHASES_ALLOW:
        return False, GateCode.PHASE_CLOSED
    # 门③：策略亲和度 >0
    if req.strategy_affinity <= 0:
        return False, GateCode.AFFINITY_NOT_POSITIVE
    # 门④：非熔断禁加期（L2/L3 的买入窄门归 MOD-POS-026 白名单管）
    if level in _CIRCUIT_BAN_LEVELS:
        return False, GateCode.CIRCUIT_BAN
    return True, GateCode.ALLOWED


@dataclass(frozen=True)
class PyramidPlanRequest:
    """P3-02 金字塔分笔计划请求。"""

    current_price: Decimal
    last_add_price: Decimal | None  # 上次加仓价（首加为 None）
    last_add_price_below: bool  # 现价是否已跌破上次加仓价（调用方比对趋势后传入）
    tranches_done: int
    remaining_budget: Decimal  # 剩余加仓预算
    confirm_entry_ok: bool  # 加仓=新交易：入场条件重新确认旗标


@dataclass(frozen=True)
class PyramidPlan:
    """本笔金字塔分笔（frozen）。"""

    tranche_no: int
    amount: Decimal
    remaining_budget: Decimal


def plan_pyramid_addition(
    req: PyramidPlanRequest,
    config: PyramidingConfig | None = None,
) -> tuple[bool, GateCode, PyramidPlan | None]:
    """P3-02 金字塔分笔计算（纯函数；资格门通过后调用）。

    三规则：递减（首加=剩余预算×1/2，逐次减半）+ 阶梯（≥ladder_min 涨幅）
    + 限次（≤3）；跌破上次加仓价=停止计划；加仓=新交易须重新确认。
    """
    cfg = config or get_default_config()
    price = _require_decimal_amount(req.current_price, "current_price")
    budget = _require_decimal_amount(req.remaining_budget, "remaining_budget")
    if req.last_add_price is not None:
        _require_decimal_amount(req.last_add_price, "last_add_price")
    if req.tranches_done < 0:
        raise PyramidingError("tranches_done 不可为负")

    # 限次
    if req.tranches_done >= cfg.max_tranches:
        return False, GateCode.MAX_TRANCHE, None
    # 跌破上次加仓价=停止后续计划
    if req.tranches_done >= 1 and req.last_add_price_below:
        return False, GateCode.BELOW_LAST_ADD, None
    # 阶梯：较上次买价涨幅 ≥ ladder_min 才加下一笔（禁止平加）
    if req.last_add_price is not None:
        ladder_mult = Decimal(1) + Decimal(str(cfg.ladder_min_pct))
        ladder_floor = req.last_add_price * ladder_mult
        if price < ladder_floor:
            return False, GateCode.LADDER_NOT_MET, None
    # 加仓=新交易：重新确认入场条件
    if req.tranches_done >= 1 and not req.confirm_entry_ok:
        return False, GateCode.ENTRY_NOT_RECONFIRMED, None
    # 预算
    if budget <= Decimal(0):
        return False, GateCode.BUDGET_EXHAUSTED, None

    # 递减：本次额度 = 剩余预算 × 1/2（首加占剩余预算一半，逐次减半）
    amount = (
        budget * cfg.halving_ratio_numer / cfg.halving_ratio_denom
    ).quantize(_QUANT, rounding=ROUND_DOWN)
    if amount <= Decimal(0):
        return False, GateCode.BUDGET_EXHAUSTED, None
    remaining = budget - amount
    plan = PyramidPlan(
        tranche_no=req.tranches_done + 1,
        amount=amount,
        remaining_budget=remaining.quantize(_QUANT),
    )
    return True, GateCode.ALLOWED, plan
