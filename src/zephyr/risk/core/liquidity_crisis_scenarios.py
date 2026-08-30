# [BLUEPRINT] MOD-RK-047 | docs/03_modules/_domain_risk/liquidity_crisis_scenarios/blueprint.md
# [MODULE] zephyr.risk.core.liquidity_crisis_scenarios
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.risk.core.stress_test_engine(MOD-RK-12,StressScenario契约); zephyr.risk.core.ashare_systemic_risk_detector(MOD-RK-10,检测阈值口径); zephyr.risk.core.liquidity_monitor(MOD-RK-08,压力退出天数); zephyr.shared.foundation.errors
# [CONSUMERS] MOD-RK-12(StressTestEngine,run_hypothetical情景消费); 运行时装配批(流动性危机压测编排)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 情景族三维固定(市场枯竭/持仓封死/融资断裂)+全员出逃极端情形;检测阈值口径复用MOD-RK-10(spread=0.005/sell_pressure=0.65)不另立真源;封死持仓exit_days=inf且sellable=False;滑点=危机半价差×√退出天数封顶1.0;纯函数零副作用同输入必同输出
# [MODIFY-GUARD] tests/risk/core/test_liquidity_crisis_scenarios.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidLiquidityScenarioError(ZA-RK-0047)——空持仓/负持仓市值/负ADV/非法配置时抛
# [TESTS] tests/risk/core/test_liquidity_crisis_scenarios.py
# [A_module] module_id=MOD-RK-047 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""
LiquidityCrisisScenarios — 流动性危机情景族（MOD-RK-047，CAND-RSK-022）。

压测情景库扩展：在 MOD-RK-12 StressTestEngine 的情景组织方式（StressScenario
契约 + run_hypothetical 消费）上扩展流动性危机场景族——三维情景 × 出场滑点
评估 × 全员出逃极端情形：

  1. MARKET_DRYUP 市场流动性枯竭：全市场价差放大（基准=MOD-RK-10 触发阈值
     0.005 × 危机倍数）+ ADV 压力折扣 → 均匀下挫 + 出场滑点抬升
  2. POSITION_FROZEN 持仓流动性封死：跌停/停牌持仓卖出通道冻结 →
     连续跌停冲击（A股主板 -10%/日）+ exit_days=inf 不可卖
  3. FUNDING_BREAK 融资流动性断裂：强平连锁 → 强平折价 × 杠杆放大冲击
  4. 全员出逃极端情形（bank-run）：ADV 跌至地板比，三族冲击取最劣合成

检测口径复用 MOD-RK-21/MOD-RK-10（价差阈值 0.005 从 AshareSystemicRiskConfig
读取，不另立第二真相源）；退出天数复用 MOD-RK-08 compute_stress_exit_days
（90号 §8 裁定①：ADV×0.3 压力折扣 ×10% 参与率）。

查重分工：stress_test_engine=通用 shock 叠加引擎（本族=流动性危机情景生产者，
产出 StressScenario 供其消费）；liquidity_crisis_manager=盘中实时检测恢复
（本族=事前压测情景，正交）。

SSoT: depgraph MOD-RK-047 | CAND-RSK-022
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: positions 参数
#   fields: 参数 positions，类型注解 list[CrisisPosition] | tuple[CrisisPosi…
#   code: liquidity_crisis_scenarios.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: liquidity_crisis_scenarios.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: leverage_ratio 参数
#   fields: 参数 leverage_ratio（无注解）
#   code: liquidity_crisis_scenarios.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① build_market_dryup_scenario
#   name_en: build_market_dryup_scenario
#   intro: 情景族① 市场流动性枯竭：价差全面放大 + ADV 压力折扣 → 均匀下挫。
#   desc: 情景族① 市场流动性枯竭：价差全面放大 + ADV 压力折扣 → 均匀下挫。 shock_i = -(MOD-RK-10 spread 阈值 × 危机倍数)（默认 -0.005×…；源码 L358-L378
#   inputs: positions config
#   outputs: LiquidityCrisisScenarioResult
# - id: A2
#   name_zh: ② build_position_frozen_scenario
#   name_en: build_position_frozen_scenario
#   intro: 情景族② 持仓流动性封死：跌停/停牌卖出通道冻结 → 连续跌停冲击。
#   desc: 情景族② 持仓流动性封死：跌停/停牌卖出通道冻结 → 连续跌停冲击。 跌停持仓 shock = frozen_daily_shock × frozen_days（下限 -0.95…；源码 L381-L409
#   inputs: positions config
#   outputs: LiquidityCrisisScenarioResult
# - id: A3
#   name_zh: ③ build_funding_break_scenario
#   name_en: build_funding_break_scenario
#   intro: 情景族③ 融资流动性断裂：强平连锁 → 强平折价 × 杠杆放大冲击。
#   desc: 情景族③ 融资流动性断裂：强平连锁 → 强平折价 × 杠杆放大冲击。 shock_i = -(margin_forced_discount × leverage_ratio)（下…；源码 L412-L435
#   inputs: positions leverage_ratio config
#   outputs: LiquidityCrisisScenarioResult
# - id: A4
#   name_zh: ④ build_bank_run_scenario
#   name_en: build_bank_run_scenario
#   intro: 全员出逃极端情形（bank-run）：ADV 跌至地板比，三族冲击取最劣合成。
#   desc: 全员出逃极端情形（bank-run）：ADV 跌至地板比，三族冲击取最劣合成。 shock_i = min(三族各自冲击)（封死持仓取封死冲击，其余取枯竭+断裂叠加， 下限 -0…；源码 L438-L469
#   inputs: positions leverage_ratio config
#   outputs: LiquidityCrisisScenarioResult
# - id: A5
#   name_zh: ⑤ run_liquidity_crisis_family
#   name_en: run_liquidity_crisis_family
#   intro: 流动性危机情景族单遍编排：三维情景 + 全员出逃极端情形（共 4 件）。
#   desc: 流动性危机情景族单遍编排：三维情景 + 全员出逃极端情形（共 4 件）。 返回顺序固定：(MARKET_DRYUP, POSITION_FROZEN, FUNDING_BREAK…；源码 L472-L489
#   inputs: positions leverage_ratio config
#   outputs: tuple[LiquidityCrisisScenarioResult, ..…
#   （注：A5 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: LiquidityCrisisScenarioResult
#   name_en: LiquidityCrisisScenarioResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-RK-12(StressTestEngine,run_hypothetical情景消费); 运行时装配批(流动性危机压测编排)
# - id: O2
#   name_zh: tuple[LiquidityCrisisScenarioResult, ..…
#   name_en: tuple[LiquidityCrisisScenarioResult, ..…
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-RK-12(StressTestEngine,run_hypothetical情景消费); 运行时装配批(流动性危机压测编排)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.risk.core.ashare_systemic_risk_detector import AshareSystemicRiskConfig
from zephyr.risk.core.liquidity_monitor import compute_stress_exit_days
from zephyr.risk.core.stress_test_engine import StressScenario, StressScenarioType
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "CrisisPosition",
    "ExitSlippageEstimate",
    "InvalidLiquidityScenarioError",
    "LiquidityCrisisFamily",
    "LiquidityCrisisScenarioConfig",
    "LiquidityCrisisScenarioResult",
    "build_bank_run_scenario",
    "build_funding_break_scenario",
    "build_market_dryup_scenario",
    "build_position_frozen_scenario",
    "run_liquidity_crisis_family",
]


class InvalidLiquidityScenarioError(ZephyrBaseError):
    """流动性危机情景输入非法（Fail-Closed）。"""

    error_code = "ZA-RK-0047"


class LiquidityCrisisFamily(str, Enum):
    """流动性危机情景族（三维 + 极端合成）。"""

    MARKET_DRYUP = "market_liquidity_dryup"  # 市场流动性枯竭
    POSITION_FROZEN = "position_liquidity_frozen"  # 持仓流动性封死
    FUNDING_BREAK = "funding_liquidity_break"  # 融资流动性断裂
    BANK_RUN = "bank_run_extreme"  # 全员出逃极端情形（三族最劣合成）


@dataclass(frozen=True)
class LiquidityCrisisScenarioConfig:
    """流动性危机情景配置（C 类参数，有行业默认值可调）。

    Attributes:
        crisis_spread_multiplier: 危机价差放大倍数（基准=MOD-RK-10 spread 阈值 0.005）
        dryup_adv_discount: 枯竭情景 ADV 压力折扣（对齐 90号 §8 = 0.3）
        run_adv_floor_ratio: 全员出逃 ADV 地板比（相对名义 ADV）
        margin_forced_discount: 融资断裂强平折价（-10%）
        frozen_daily_shock: 跌停封死单日冲击（A股主板 -10%，负=下跌）
        frozen_days: 连续封死天数（极端情形默认 3 日）
        slippage_participation: 出场参与率（对齐 90号 §8 = 0.10）
    """

    crisis_spread_multiplier: float = 4.0
    dryup_adv_discount: float = 0.3
    run_adv_floor_ratio: float = 0.05
    margin_forced_discount: float = 0.10
    frozen_daily_shock: float = -0.10
    frozen_days: int = 3
    slippage_participation: float = 0.10

    def __post_init__(self) -> None:
        if self.crisis_spread_multiplier <= 1.0:
            raise InvalidLiquidityScenarioError(f"crisis_spread_multiplier 须 >1: {self.crisis_spread_multiplier}")
        if not 0.0 < self.dryup_adv_discount <= 1.0:
            raise InvalidLiquidityScenarioError(f"dryup_adv_discount 须 ∈ (0,1]: {self.dryup_adv_discount}")
        if not 0.0 < self.run_adv_floor_ratio < 1.0:
            raise InvalidLiquidityScenarioError(f"run_adv_floor_ratio 须 ∈ (0,1): {self.run_adv_floor_ratio}")
        if not 0.0 < self.margin_forced_discount < 1.0:
            raise InvalidLiquidityScenarioError(f"margin_forced_discount 须 ∈ (0,1): {self.margin_forced_discount}")
        if not -1.0 < self.frozen_daily_shock < 0.0:
            raise InvalidLiquidityScenarioError(f"frozen_daily_shock 须 ∈ (-1,0): {self.frozen_daily_shock}")
        if self.frozen_days < 1:
            raise InvalidLiquidityScenarioError(f"frozen_days 须 ≥1: {self.frozen_days}")
        if not 0.0 < self.slippage_participation <= 1.0:
            raise InvalidLiquidityScenarioError(f"slippage_participation 须 ∈ (0,1]: {self.slippage_participation}")


@dataclass(frozen=True)
class CrisisPosition:
    """危机情景持仓输入（单标的）。

    Attributes:
        symbol: 标的代码
        position_value: 持仓市值（元，≥0）
        adv_value: 名义日均成交额 ADV（元，≥0；0=流动性枯竭）
        is_limit_down: 跌停（封死）标志
        is_suspended: 停牌标志
    """

    symbol: str
    position_value: float
    adv_value: float
    is_limit_down: bool = False
    is_suspended: bool = False


@dataclass(frozen=True)
class ExitSlippageEstimate:
    """单持仓出场滑点评估。

    Attributes:
        symbol: 标的代码
        exit_days: 压力情景退出天数（inf=封死不可卖）
        half_spread: 危机半价差（基准阈值×危机倍数/2）
        slippage_pct: 出场滑点占比（half_spread×√exit_days，封顶 1.0）
        sellable: 是否可卖（跌停/停牌=False）
    """

    symbol: str
    exit_days: float
    half_spread: float
    slippage_pct: float
    sellable: bool


@dataclass(frozen=True)
class LiquidityCrisisScenarioResult:
    """单族流动性危机情景结果。

    Attributes:
        family: 情景族
        scenario: StressScenario（shocks 负=下跌，供 MOD-RK-12 run_hypothetical 消费）
        slippage: 逐持仓出场滑点评估
        total_slippage_value: 组合级滑点金额（Σ position_value × slippage_pct，元）
        description: 情景描述
    """

    family: LiquidityCrisisFamily
    scenario: StressScenario
    slippage: tuple[ExitSlippageEstimate, ...]
    total_slippage_value: float
    description: str


# ── 内部工具 ──────────────────────────────────────────────────────────


def _crisis_half_spread(cfg: LiquidityCrisisScenarioConfig) -> float:
    """危机半价差 = MOD-RK-10 spread 触发阈值 × 危机倍数 / 2（检测口径复用）。"""
    base_spread = AshareSystemicRiskConfig().bid_ask_spread_threshold
    return base_spread * cfg.crisis_spread_multiplier / 2.0


def _validate_positions(positions: list[CrisisPosition] | tuple[CrisisPosition, ...]) -> None:
    """持仓列表校验（Fail-Closed）。"""
    if not positions:
        raise InvalidLiquidityScenarioError("positions 不可为空")
    seen: set[str] = set()
    for p in positions:
        if not p.symbol or not p.symbol.strip():
            raise InvalidLiquidityScenarioError("symbol 不可为空")
        if p.symbol in seen:
            raise InvalidLiquidityScenarioError(f"重复 symbol: {p.symbol}")
        seen.add(p.symbol)
        if p.position_value < 0:
            raise InvalidLiquidityScenarioError(f"position_value 不能为负: {p.position_value} ({p.symbol})")
        if p.adv_value < 0:
            raise InvalidLiquidityScenarioError(f"adv_value 不能为负: {p.adv_value} ({p.symbol})")


def _estimate_slippage(
    position: CrisisPosition,
    *,
    adv_value: float,
    cfg: LiquidityCrisisScenarioConfig,
) -> ExitSlippageEstimate:
    """单持仓出场滑点：exit_days 复用 MOD-RK-08 压力退出天数，滑点=半价差×√天数封顶 1.0。"""
    sellable = not (position.is_limit_down or position.is_suspended)
    half_spread = _crisis_half_spread(cfg)
    if not sellable:
        return ExitSlippageEstimate(
            symbol=position.symbol,
            exit_days=float("inf"),
            half_spread=half_spread,
            slippage_pct=1.0,
            sellable=False,
        )
    exit_days = compute_stress_exit_days(
        position.position_value,
        adv_value,
        stress_discount=cfg.dryup_adv_discount,
        participation_rate=cfg.slippage_participation,
    )
    slippage = 1.0 if math.isinf(exit_days) else min(1.0, half_spread * math.sqrt(exit_days))
    return ExitSlippageEstimate(
        symbol=position.symbol,
        exit_days=exit_days,
        half_spread=half_spread,
        slippage_pct=slippage,
        sellable=True,
    )


def _make_result(
    family: LiquidityCrisisFamily,
    positions: list[CrisisPosition] | tuple[CrisisPosition, ...],
    shocks: dict[str, float],
    cfg: LiquidityCrisisScenarioConfig,
    description: str,
    *,
    adv_override: dict[str, float] | None = None,
) -> LiquidityCrisisScenarioResult:
    """组装情景结果（StressScenario + 滑点评估 + 组合滑点金额）。"""
    slippage = tuple(
        _estimate_slippage(p, adv_value=(adv_override or {}).get(p.symbol, p.adv_value), cfg=cfg) for p in positions
    )
    slip_value = {s.symbol: s.slippage_pct for s in slippage}
    total_slippage_value = sum(p.position_value * slip_value[p.symbol] for p in positions)
    scenario = StressScenario(
        name=f"liquidity_crisis/{family.value}",
        scenario_type=StressScenarioType.HYPOTHETICAL,
        shocks=shocks,
        description=description,
    )
    _logger.info(
        "Liquidity crisis scenario built: family=%s positions=%d worst_shock=%.4f slippage_value=%.2f",
        family.value,
        len(positions),
        scenario.worst_shock,
        total_slippage_value,
    )
    return LiquidityCrisisScenarioResult(
        family=family,
        scenario=scenario,
        slippage=slippage,
        total_slippage_value=total_slippage_value,
        description=description,
    )


# ── 三维情景族 + 全员出逃 ─────────────────────────────────────────────


def build_market_dryup_scenario(
    positions: list[CrisisPosition] | tuple[CrisisPosition, ...],
    *,
    config: LiquidityCrisisScenarioConfig | None = None,
) -> LiquidityCrisisScenarioResult:
    """情景族① 市场流动性枯竭：价差全面放大 + ADV 压力折扣 → 均匀下挫。

    shock_i = -(MOD-RK-10 spread 阈值 × 危机倍数)（默认 -0.005×4 = -2% 全线）。
    出场滑点按 ADV×0.3 压力折扣评估（90号 §8 口径）。
    """
    cfg = config or LiquidityCrisisScenarioConfig()
    _validate_positions(positions)
    shock = -(_crisis_half_spread(cfg) * 2.0)  # 全价差 = 半价差×2
    shocks = {p.symbol: shock for p in positions}
    return _make_result(
        LiquidityCrisisFamily.MARKET_DRYUP,
        positions,
        shocks,
        cfg,
        f"市场流动性枯竭: 价差放大×{cfg.crisis_spread_multiplier} 全线 {shock:.2%} + ADV×{cfg.dryup_adv_discount}",
    )


def build_position_frozen_scenario(
    positions: list[CrisisPosition] | tuple[CrisisPosition, ...],
    *,
    config: LiquidityCrisisScenarioConfig | None = None,
) -> LiquidityCrisisScenarioResult:
    """情景族② 持仓流动性封死：跌停/停牌卖出通道冻结 → 连续跌停冲击。

    跌停持仓 shock = frozen_daily_shock × frozen_days（下限 -0.95，不击穿清零）；
    停牌持仓 shock = frozen_daily_shock（复牌跳空单日）；正常持仓 shock = 0。
    封死持仓 exit_days=inf 且 sellable=False（滑点封顶 1.0）。
    """
    cfg = config or LiquidityCrisisScenarioConfig()
    _validate_positions(positions)
    floor = -0.95
    shocks: dict[str, float] = {}
    for p in positions:
        if p.is_limit_down:
            shocks[p.symbol] = max(cfg.frozen_daily_shock * cfg.frozen_days, floor)
        elif p.is_suspended:
            shocks[p.symbol] = cfg.frozen_daily_shock
        else:
            shocks[p.symbol] = 0.0
    return _make_result(
        LiquidityCrisisFamily.POSITION_FROZEN,
        positions,
        shocks,
        cfg,
        f"持仓流动性封死: 跌停 {cfg.frozen_daily_shock:.0%}×{cfg.frozen_days}日 / 停牌 {cfg.frozen_daily_shock:.0%} 复牌跳空",
    )


def build_funding_break_scenario(
    positions: list[CrisisPosition] | tuple[CrisisPosition, ...],
    *,
    leverage_ratio: float = 1.5,
    config: LiquidityCrisisScenarioConfig | None = None,
) -> LiquidityCrisisScenarioResult:
    """情景族③ 融资流动性断裂：强平连锁 → 强平折价 × 杠杆放大冲击。

    shock_i = -(margin_forced_discount × leverage_ratio)（下限 -0.95）。
    融资盘强平不看盘口深度，出场滑点仍按 ADV 压力折扣评估。
    """
    cfg = config or LiquidityCrisisScenarioConfig()
    _validate_positions(positions)
    if leverage_ratio < 1.0:
        raise InvalidLiquidityScenarioError(f"leverage_ratio 须 ≥1: {leverage_ratio}")
    shock = max(-(cfg.margin_forced_discount * leverage_ratio), -0.95)
    shocks = {p.symbol: shock for p in positions}
    return _make_result(
        LiquidityCrisisFamily.FUNDING_BREAK,
        positions,
        shocks,
        cfg,
        f"融资流动性断裂: 强平折价 {cfg.margin_forced_discount:.0%}×杠杆{leverage_ratio} = {shock:.2%}",
    )


def build_bank_run_scenario(
    positions: list[CrisisPosition] | tuple[CrisisPosition, ...],
    *,
    leverage_ratio: float = 1.5,
    config: LiquidityCrisisScenarioConfig | None = None,
) -> LiquidityCrisisScenarioResult:
    """全员出逃极端情形（bank-run）：ADV 跌至地板比，三族冲击取最劣合成。

    shock_i = min(三族各自冲击)（封死持仓取封死冲击，其余取枯竭+断裂叠加，
    下限 -0.95）；出场滑点按 ADV×run_adv_floor_ratio 地板评估（近全员抛售，
    退出天数大幅抬升）。
    """
    cfg = config or LiquidityCrisisScenarioConfig()
    _validate_positions(positions)
    if leverage_ratio < 1.0:
        raise InvalidLiquidityScenarioError(f"leverage_ratio 须 ≥1: {leverage_ratio}")
    dryup = build_market_dryup_scenario(positions, config=cfg).scenario.shocks
    frozen = build_position_frozen_scenario(positions, config=cfg).scenario.shocks
    funding = build_funding_break_scenario(positions, leverage_ratio=leverage_ratio, config=cfg).scenario.shocks
    shocks: dict[str, float] = {}
    for p in positions:
        worst_open = max(dryup[p.symbol] + funding[p.symbol], -0.95)
        shocks[p.symbol] = min(frozen[p.symbol], worst_open) if frozen[p.symbol] < 0 else worst_open
    adv_floor = {p.symbol: p.adv_value * cfg.run_adv_floor_ratio for p in positions}
    return _make_result(
        LiquidityCrisisFamily.BANK_RUN,
        positions,
        shocks,
        cfg,
        f"全员出逃极端情形: 三族最劣合成 + ADV×{cfg.run_adv_floor_ratio} 地板",
        adv_override=adv_floor,
    )


def run_liquidity_crisis_family(
    positions: list[CrisisPosition] | tuple[CrisisPosition, ...],
    *,
    leverage_ratio: float = 1.5,
    config: LiquidityCrisisScenarioConfig | None = None,
) -> tuple[LiquidityCrisisScenarioResult, ...]:
    """流动性危机情景族单遍编排：三维情景 + 全员出逃极端情形（共 4 件）。

    返回顺序固定：(MARKET_DRYUP, POSITION_FROZEN, FUNDING_BREAK, BANK_RUN)。
    """
    cfg = config or LiquidityCrisisScenarioConfig()
    _validate_positions(positions)
    return (
        build_market_dryup_scenario(positions, config=cfg),
        build_position_frozen_scenario(positions, config=cfg),
        build_funding_break_scenario(positions, leverage_ratio=leverage_ratio, config=cfg),
        build_bank_run_scenario(positions, leverage_ratio=leverage_ratio, config=cfg),
    )
