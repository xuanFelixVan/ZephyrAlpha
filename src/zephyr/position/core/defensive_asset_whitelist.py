# [BLUEPRINT] MOD-POS-026 | docs/03_modules/_domain_position/defensive_asset_whitelist/blueprint.md
# [CORE-ALGORITHM] X-R1-03 护盘资产定向加仓白名单——熔断期窄门三重门（晨审重点：白名单来源固化/方向=买入核对/休眠铁律）
# [MODULE] zephyr.position.core.defensive_asset_whitelist
# [DOMAIN] D_POSITION
# [DEPENDENCIES] 无（纯函数核，零 IO、零 zephyr 内部件）
# [CONSUMERS] TDM-X-R1-03（熔断期窄门决策）；X-R1-01 drawdown_state_machine（L2/L3 转入时调用，待接线）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] enabled=False(默认)恒 DISALLOWED(D114 休眠铁律 fail-closed); 方向非 BUY 恒拒(DIRECTION_NOT_BUY); 三重门逐门短路留 reason_code 可审计; 计划分笔≤min(尾部弹药预算,总资金×上限10%); 分笔≤3 且第 2/3 笔须确认收复旗标; 金额 Decimal-only 拒 float; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_position/defensive_asset_whitelist/blueprint.md + design_memos/69_trading_decision_map.md §2.33 D114
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 非法请求（负金额/未知方向/负分笔数/float 金额）→ DefensiveWhitelistError（fail-closed）
# [TESTS] tests/position/test_defensive_asset_whitelist.py
# [TTL] permanent
"""DefensiveAssetWhitelist — 熔断期护盘资产定向加仓白名单（MOD-POS-026，D114）。

熔断五级中只有 L2（日亏≥4% 禁开仓+白名单窄门开启）/L3（日亏≥6% 减仓）允许本通道，
是熔断期唯一的买入例外。三重门全过才开窄门（69 号 §2.33 D114，proposed 假说）：

① 状态门：circuit_level ∈ {L2, L3}（其余级别窄门不开；L4 已清仓无买的意义）。
② 信号门：D110 超跌反转（KDJ J<-10 且 量能>20 日均量 2 倍 且 无系统性利空）
   或 国家队明牌（ETF 天量成交 / 官方增持公告）——满足其一即可。
③ 分批门：金字塔法——首笔 1/3 预算；第 2/3 笔必须"确认收复"（三重门再次全过）
   才放行；分笔上限 3 笔，严禁一次到位。

白名单（来源固化，方向=买入核对）：T1 宽基 ETF 优先（沪深300/中证500/中证1000/红利），
T2 银行/高股息次之。仓位=D107 尾部弹药预算，上限总资金 5-10%（默认取上限 10%）。

**休眠铁律**：D114 裁定"回测验证前整节点休眠"——`enabled` 默认 False，任何调用
返回 DISALLOWED(DORMANT)。启用必须走回测验证批（holdout 纪律：12 个月保密考卷）。

风险声明：政策底≠市场底（历史滞后 40 天~半年）——分批+确认信号是铁律。

查重分工（蓝图 §1）：drawdown_state_machine=熔断分级判定（X-R1-01，状态门的
上游真源）；本件=白名单窄门的放行裁决（买什么/买多少/第几笔），不判熔断级、
不算 KDJ/量比（由调用方算好传入，本件只做组合判定）。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from enum import Enum

_QUANT = Decimal("0.01")


class DefensiveWhitelistError(ValueError):
    """非法请求（fail-closed）：负金额/未知方向/负分笔数/float 金额。"""


class CircuitLevel(str, Enum):
    """熔断五级（真源=X-R1-01 drawdown_state_machine，本模块只消费不判定）。"""

    L0 = "L0"  # 正常
    L1 = "L1"  # 警戒（日亏≥2% 禁加仓）
    L2 = "L2"  # 禁开仓（日亏≥4%：白名单窄门开启）
    L3 = "L3"  # 减仓（日亏≥6%）
    L4 = "L4"  # 保命（清仓+Owner 接管）


class NationalTeamSignal(str, Enum):
    """国家队明牌信号（D114：ETF 天量成交 / 官方增持公告）。"""

    NONE = "NONE"
    ETF_VOLUME_SURGE = "ETF_VOLUME_SURGE"
    OFFICIAL_ANNOUNCEMENT = "OFFICIAL_ANNOUNCEMENT"


class Direction(str, Enum):
    """交易方向——白名单语义只买不卖（方向=买入核对）。"""

    BUY = "BUY"
    SELL = "SELL"


class WhitelistTier(str, Enum):
    """白名单分层：T1 宽基 ETF 优先，T2 银行/高股息次之。"""

    T1_BROAD_ETF = "T1_BROAD_ETF"
    T2_BANK_DIVIDEND = "T2_BANK_DIVIDEND"


class ReasonCode(str, Enum):
    """裁决原因码（逐门短路，首败即拒，可审计）。"""

    DORMANT = "DORMANT"  # D114 休眠铁律：回测验证前整节点休眠
    DIRECTION_NOT_BUY = "DIRECTION_NOT_BUY"
    NOT_WHITELISTED = "NOT_WHITELISTED"
    LEVEL_GATE_FAIL = "LEVEL_GATE_FAIL"
    SIGNAL_GATE_FAIL = "SIGNAL_GATE_FAIL"
    CONFIRMATION_REQUIRED = "CONFIRMATION_REQUIRED"
    TRANCHE_LIMIT_REACHED = "TRANCHE_LIMIT_REACHED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    ALLOWED = "ALLOWED"


#: T1 宽基 ETF（经验拍定默认值，config 可注入；启用前须随回测批核定）
DEFAULT_TIER1: tuple[str, ...] = ("510300", "510500", "512100", "510880")
#: T2 银行/高股息（经验拍定默认值，config 可注入）
DEFAULT_TIER2: tuple[str, ...] = ("512800", "512890")


@dataclass(frozen=True)
class DefensiveWhitelistConfig:
    """白名单窄门配置（D114 全参数，默认值=休眠+经验拍定阈值）。"""

    enabled: bool = False  # D114：回测验证前整节点休眠（fail-closed 默认）
    tier1: tuple[str, ...] = DEFAULT_TIER1
    tier2: tuple[str, ...] = DEFAULT_TIER2
    max_total_pct: Decimal = Decimal("0.10")  # 上限总资金 5-10%，默认取上限
    max_tranches: int = 3
    tranche_numer: int = 1  # 每笔 = cap × numer/denom（首笔 1/3 预算，分数避免精度尾差）
    tranche_denom: int = 3
    kdj_j_threshold: Decimal = Decimal("-10")  # D110：KDJ J<-10
    volume_ratio_threshold: Decimal = Decimal("2")  # D110：量能>20 日均量 2 倍

    def __post_init__(self) -> None:
        if not isinstance(self.max_total_pct, Decimal):
            raise DefensiveWhitelistError("金额/比例字段必须为 Decimal（拒 float）")
        if not (Decimal(0) < self.max_total_pct <= Decimal("0.10")):
            raise DefensiveWhitelistError(
                f"max_total_pct 必须落在 (0, 0.10]（D114 上限 5-10%）: {self.max_total_pct}"
            )
        if not (0 < self.tranche_numer < self.tranche_denom):
            raise DefensiveWhitelistError(
                f"分笔比例须满足 0 < numer < denom: {self.tranche_numer}/{self.tranche_denom}"
            )
        if self.max_tranches < 1:
            raise DefensiveWhitelistError(f"max_tranches 必须≥1: {self.max_tranches}")


#: 默认配置（休眠态）
DEFAULT_CONFIG = DefensiveWhitelistConfig()


@dataclass(frozen=True)
class ReversalSignal:
    """D110 超跌反转信号三组件（由调用方算好传入，本模块不做指标计算）。"""

    kdj_j: float  # KDJ J 值
    volume_ratio: float  # 成交量 / 20 日均量
    systemic_bad_news: bool = False  # 系统性利空过滤：True=有系统性利空（D110 拒绝）


@dataclass(frozen=True)
class DefensiveAdditionRequest:
    """白名单窄门裁决请求。"""

    symbol: str
    direction: Direction | str
    circuit_level: CircuitLevel | str
    reversal: ReversalSignal
    nt_signal: NationalTeamSignal | str
    reserve_budget: Decimal  # D107 尾部弹药预算
    total_capital: Decimal
    deployed_amount: Decimal = Decimal("0")  # 本轮已投护盘额
    tranches_done: int = 0  # 已完成分笔数
    confirm_recovered: bool = False  # 上一笔后"确认收复"旗标（第 2/3 笔必需）


@dataclass(frozen=True)
class TranchePlan:
    """本笔放行的分笔计划。"""

    tranche_no: int  # 第几笔（1 起）
    amount: Decimal  # 本笔金额（Decimal，向下取分）


@dataclass(frozen=True)
class DefensiveVerdict:
    """白名单窄门裁决（frozen，可审计）。"""

    allowed: bool
    reason_codes: tuple[ReasonCode, ...]
    tier: WhitelistTier | None = None
    tranche: TranchePlan | None = None
    remaining_budget: Decimal | None = None


def _to_direction(value: Direction | str) -> Direction:
    try:
        return Direction(value)
    except ValueError as exc:
        raise DefensiveWhitelistError(f"未知方向: {value!r}") from exc


def _to_level(value: CircuitLevel | str) -> CircuitLevel:
    try:
        return CircuitLevel(value)
    except ValueError as exc:
        raise DefensiveWhitelistError(f"未知熔断级: {value!r}") from exc


def _to_nt_signal(value: NationalTeamSignal | str) -> NationalTeamSignal:
    try:
        return NationalTeamSignal(value)
    except ValueError as exc:
        raise DefensiveWhitelistError(f"未知国家队信号: {value!r}") from exc


def _require_decimal(value: Decimal, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, Decimal):
        raise DefensiveWhitelistError(f"{name} 必须为 Decimal（拒 float/int）")
    return value


def _validate_request(req: DefensiveAdditionRequest) -> None:
    _require_decimal(req.reserve_budget, "reserve_budget")
    _require_decimal(req.total_capital, "total_capital")
    _require_decimal(req.deployed_amount, "deployed_amount")
    if req.reserve_budget < Decimal(0):
        raise DefensiveWhitelistError("reserve_budget 不可为负")
    if req.total_capital <= Decimal(0):
        raise DefensiveWhitelistError("total_capital 必须为正")
    if req.deployed_amount < Decimal(0):
        raise DefensiveWhitelistError("deployed_amount 不可为负")
    if req.tranches_done < 0:
        raise DefensiveWhitelistError("tranches_done 不可为负")
    if not req.symbol:
        raise DefensiveWhitelistError("symbol 不可为空")


def _lookup_tier(
    symbol: str, config: DefensiveWhitelistConfig
) -> WhitelistTier | None:
    if symbol in config.tier1:
        return WhitelistTier.T1_BROAD_ETF
    if symbol in config.tier2:
        return WhitelistTier.T2_BANK_DIVIDEND
    return None


def evaluate_defensive_addition(
    req: DefensiveAdditionRequest,
    config: DefensiveWhitelistConfig = DEFAULT_CONFIG,
) -> DefensiveVerdict:
    """白名单窄门三重门裁决（纯函数，同输入必同输出）。

    Args:
        req: 裁决请求（金额字段必须 Decimal）。
        config: 白名单配置（默认休眠态——enabled=False 恒拒）。

    Returns:
        DefensiveVerdict：allowed=False 时 reason_codes 给出首个败因
        （逐门短路顺序：休眠→方向→白名单→状态门→信号门→分批门→预算）。
    """
    _validate_request(req)
    direction = _to_direction(req.direction)
    level = _to_level(req.circuit_level)
    nt_signal = _to_nt_signal(req.nt_signal)

    # 休眠铁律（D114）：门0，先于一切
    if not config.enabled:
        return DefensiveVerdict(
            allowed=False, reason_codes=(ReasonCode.DORMANT,)
        )
    # 门a：方向=买入核对
    if direction != Direction.BUY:
        return DefensiveVerdict(
            allowed=False, reason_codes=(ReasonCode.DIRECTION_NOT_BUY,)
        )
    # 门b：白名单来源固化
    tier = _lookup_tier(req.symbol, config)
    if tier is None:
        return DefensiveVerdict(
            allowed=False, reason_codes=(ReasonCode.NOT_WHITELISTED,)
        )
    # 门①：状态门——只有 L2/L3 开窄门
    if level not in (CircuitLevel.L2, CircuitLevel.L3):
        return DefensiveVerdict(
            allowed=False, reason_codes=(ReasonCode.LEVEL_GATE_FAIL,)
        )
    # 门②：信号门——D110 超跌反转 或 国家队明牌（满足其一）
    d110_ok = (
        req.reversal.kdj_j < float(config.kdj_j_threshold)
        and req.reversal.volume_ratio > float(config.volume_ratio_threshold)
        and not req.reversal.systemic_bad_news
    )
    nt_ok = nt_signal != NationalTeamSignal.NONE
    if not (d110_ok or nt_ok):
        return DefensiveVerdict(
            allowed=False, reason_codes=(ReasonCode.SIGNAL_GATE_FAIL,)
        )
    # 门③：分批门——上限 3 笔；第 2/3 笔须确认收复
    if req.tranches_done >= config.max_tranches:
        return DefensiveVerdict(
            allowed=False,
            reason_codes=(ReasonCode.TRANCHE_LIMIT_REACHED,),
            tier=tier,
        )
    if req.tranches_done >= 1 and not req.confirm_recovered:
        return DefensiveVerdict(
            allowed=False,
            reason_codes=(ReasonCode.CONFIRMATION_REQUIRED,),
            tier=tier,
        )
    # 预算闸：cap = min(尾部弹药预算, 总资金×上限比例)
    cap = min(req.reserve_budget, req.total_capital * config.max_total_pct)
    remaining = cap - req.deployed_amount
    if remaining <= Decimal(0):
        return DefensiveVerdict(
            allowed=False,
            reason_codes=(ReasonCode.BUDGET_EXHAUSTED,),
            tier=tier,
            remaining_budget=Decimal("0.00"),
        )
    amount = (cap * config.tranche_numer / config.tranche_denom).quantize(
        _QUANT, rounding=ROUND_DOWN
    )
    amount = min(amount, remaining).quantize(_QUANT, rounding=ROUND_DOWN)
    if amount <= Decimal(0):
        return DefensiveVerdict(
            allowed=False,
            reason_codes=(ReasonCode.BUDGET_EXHAUSTED,),
            tier=tier,
            remaining_budget=remaining.quantize(_QUANT),
        )
    return DefensiveVerdict(
        allowed=True,
        reason_codes=(ReasonCode.ALLOWED,),
        tier=tier,
        tranche=TranchePlan(tranche_no=req.tranches_done + 1, amount=amount),
        remaining_budget=(remaining - amount).quantize(_QUANT),
    )
