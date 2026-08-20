# [BLUEPRINT] MOD-POS-001 | docs/03_modules/_domain_position/position_sizing_engine/blueprint.md
# [MODULE] zephyr.position.core.position_sizing_engine
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.position.core.capital_curve_manager; zephyr.position.core.cash_manager; zephyr.position.core.calendar_position_constraint; zephyr.risk.risk_limits
# [CONSUMERS] D-EX-CORE(执行PositionSizingPlan CTR-POS-001); D-PF-CORE(消费E-POS-01 PositionSized)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] w_kelly<=0.5*f*(半Kelly硬上限);参与率>15%的标的不得出现在PositionSizingPlan(否决非截断);total_exposure<=min(市场状态上限,风控上限,资金曲线上限,日历约束上限);应急模式单标的<=10%总仓位<=30%;降级模式必须标记degraded=true;PositionSizingPlan幂等(idempotency_key防重复)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidPositionInputError(ZA-POS-0001); KellyEstimationError(ZA-POS-0002); ConstraintViolationError(ZA-POS-0003)
# [TESTS] tests/position/test_position_sizing_engine.py
# [A_module] module_id=MOD-POS-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Position Sizing Engine — 仓位决策引擎 (MOD-POS-001)

D-POSITION 域核心裁决器: 消费四轨输入+目标权重+策略分配+密度预测分布参数,
综合 13 项硬约束, 产出最终仓位方案 PositionSizingPlan (CTR-POS-001)。

阶段1 范围 (P0, 不依赖未建上游):
    - 预筛阶段(退出时间检查 + 流动性上限预筛)
    - Kelly 仓位计算 + 半 Kelly 截断(C1)
    - 风险配额(C2) / 波动率检查(C3) / VaR-CVaR 下调(C4/C5)
    - 单票上限(C12) / 市场状态上限(C13)
    - 参与率否决(C6) / 退出时间减仓(C7/C8) / 策略容量预警(C9) / 冲击成本否决(C11)
    - 资金曲线缩放(POS-007) / 现金约束(POS-006) / 日历约束(POS-017)
    - 降级模式(上游缺失时保守仓位)

不包含 (阶段2): 四轨融合(轨道2/3/4) / 分布感知(C10) / 跨策略合并(POS-005)

依据: D:\\临时工作区\\依赖图\\07-D-POSITION-仓位管理域.md §1.1 POS-01, §7.1/§7.2/§8
SSoT: depgraph MOD-POS-001
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Callable, Final

from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final[list[str]] = [
    "SizingMarketRegime",
    "PositionSizingConfig",
    "SymbolInput",
    "PositionSizingInput",
    "PositionTarget",
    "ConstraintCheck",
    "PositionSizingPlan",
    "PositionSizingEngine",
    "InvalidPositionInputError",
    "KellyEstimationError",
    "ConstraintViolationError",
    "MARKET_REGIME_CAPS",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 市场状态枚举 (设计真源 §7.3, immutable)
# ──────────────────────────────────────────────────────────────────────────────


class SizingMarketRegime(str, Enum):
    """仓位决策市场状态 ①~⑫ (设计真源 §7.3 v8.1, 12 种 immutable 映射)。

    12 态 = 9 基础网格(3×3, 趋势方向×波动率) + 3 特殊态(CRISIS/RECOVERY/BREAKOUT),
    与 D-SIGNAL-04 定义方对齐。事件驱动/板块轮动为正交 overlay, 由
    PositionSizingInput.is_event_driven/is_sector_rotation 标志位表达, 不占 enum。

    与 feedback_loop/gov_drift 的 MarketRegime 同名不同义——彼处为增益调度/ML 特征
    (3~4 态), 本处为仓位上限映射 (12 态), 故冠 Sizing 前缀以区分 (ARCH-034)。
    """

    CALM_BULL = "CALM_BULL"  # ①平稳牛市
    MOMENTUM_BULL = "MOMENTUM_BULL"  # ②动量牛市
    PANIC_BOUNCE = "PANIC_BOUNCE"  # ③恐慌反弹
    NARROW_RANGE = "NARROW_RANGE"  # ④窄幅盘整
    WIDE_CHOP = "WIDE_CHOP"  # ⑤宽幅震荡
    COMPRESS_BREAKOUT = "COMPRESS_BREAKOUT"  # ⑥压缩突破
    SLOW_DECLINE = "SLOW_DECLINE"  # ⑦阴跌
    ACCEL_DECLINE = "ACCEL_DECLINE"  # ⑧加速下跌
    PANIC_CRASH = "PANIC_CRASH"  # ⑨恐慌崩盘
    CRISIS = "CRISIS"  # ⑩危机(特殊态)
    RECOVERY = "RECOVERY"  # ⑪复苏(特殊态)
    BREAKOUT = "BREAKOUT"  # ⑫突破(特殊态)


# 市场状态 → 仓位上限映射 (immutable, 不可 AI 修改, 调整需 Trader 审批)
MARKET_REGIME_CAPS: Final[dict[SizingMarketRegime, float]] = {
    SizingMarketRegime.CALM_BULL: 0.80,
    SizingMarketRegime.MOMENTUM_BULL: 0.80,
    SizingMarketRegime.PANIC_BOUNCE: 0.60,
    SizingMarketRegime.NARROW_RANGE: 0.40,
    SizingMarketRegime.WIDE_CHOP: 0.50,
    SizingMarketRegime.COMPRESS_BREAKOUT: 0.60,
    SizingMarketRegime.SLOW_DECLINE: 0.30,
    SizingMarketRegime.ACCEL_DECLINE: 0.20,
    SizingMarketRegime.PANIC_CRASH: 0.10,
    SizingMarketRegime.CRISIS: 0.05,  # ⑩极端行情, 仅减仓不开新
    SizingMarketRegime.RECOVERY: 0.50,  # ⑪回撤回补期, 逐步重建
    SizingMarketRegime.BREAKOUT: 0.70,  # ⑫趋势确立, 加仓
}

# ── sizing_basis binding constraint 命名（31号 §2.3.4，deadeye-rs 2026-06 模式）──
# 7 值契约栈 + 代码级联现实扩展（C3 波动率/C7 退出时间/降级等权）
SIZING_BASIS_STRATEGY_INTENT = "strategy_intent"  # 策略意愿约束（粗仓位求和×分布调整）
SIZING_BASIS_KELLY_BUDGET = "kelly_budget"  # Kelly 风险预算约束（半 Kelly+截0）
SIZING_BASIS_VAR_CAP = "var_cap"  # VaR_95 上限约束（C4）
SIZING_BASIS_CVAR_CAP = "cvar_cap"  # CVaR_95 上限约束（C5，比 VaR 更严）
SIZING_BASIS_SINGLE_NAME_CAP = "single_name_cap"  # 单票硬上限约束（C12，§2.4.1 三层口径）
SIZING_BASIS_LIQUIDITY_MODERATE = "liquidity_cap_moderate"  # 流动性削半档（§2.4.4，MOD-POS-021 消费预留）
SIZING_BASIS_LIQUIDITY_SEVERE = "liquidity_cap_severe"  # 流动性严重档（§2.4.4，MOD-POS-021 消费预留）
SIZING_BASIS_VOLATILITY_CHECK = "volatility_check"  # C3 波动率减半（代码级联扩展）
SIZING_BASIS_EXIT_TIME_CAP = "exit_time_cap"  # C7/C8 退出时间减仓（代码级联扩展）
SIZING_BASIS_DEGRADED = "degraded_equal_weight"  # 无密度预测降级等权（Kelly 缺失路径）


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidPositionInputError(ZephyrBaseError):
    """仓位决策输入数据非法(目标权重空/负值、AUM<=0、持仓快照缺失等)。"""

    error_code = "ZA-POS-0001"


class KellyEstimationError(ZephyrBaseError):
    """Kelly 估计异常(p<=0 或 b<=0、分布参数非法)。"""

    error_code = "ZA-POS-0002"


class ConstraintViolationError(ZephyrBaseError):
    """约束执行后仓位仍超限(不变量被破坏, 需告警)。"""

    error_code = "ZA-POS-0003"


# ──────────────────────────────────────────────────────────────────────────────
# 配置 (C 类可调参数, §5.1 约束阈值)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PositionSizingConfig:
    """仓位决策配置 (§5.1 约束阈值, 避免 Long Parameter List)。"""

    # C1 半Kelly系数
    half_kelly_factor: float = 0.5
    # C3 波动率检查
    vol_sigma_multiplier: float = 2.0  # 超 μ+2σ → 仓位减半
    vol_halve_factor: float = 0.5
    # C4/C5 VaR/CVaR 下调
    var_threshold: float = 0.025  # 前瞻95%VaR > 2.5% → 下调
    var_reduce_factor: float = 0.8
    cvar_threshold: float = 0.04  # 前瞻95%CVaR > 4% → 进一步下调
    cvar_reduce_factor: float = 0.7
    # C6 参与率否决
    max_participation_rate: float = 0.15  # >15% 日成交量 → 否决
    # C7/C8 退出时间减仓
    exit_days_hard: int = 3  # >3天 → 强制减仓至可退出
    exit_days_soft: int = 1  # >1天 → 仓位上限折扣
    exit_soft_discount: float = 0.8
    # C9 策略容量预警
    capacity_warn_ratio: float = 0.80  # >AUM×80% → 预警
    capacity_veto_ratio: float = 1.00  # >AUM×100% → 否决新资金
    # C11 冲击成本否决
    max_impact_cost: float = 0.005  # >0.5% → 否决
    impact_cost_coeff: float = 0.1  # 冲击成本系数 (sqrt模型)
    # C12 单票上限 (默认, 可被 RiskLimits.symbol_overrides 覆盖)
    default_single_position_cap: float = 0.05  # 5% NAV
    # 降级默认市场状态
    degradation_market_regime: SizingMarketRegime = SizingMarketRegime.NARROW_RANGE  # ④(40%)

    def __post_init__(self) -> None:
        if not 0 < self.half_kelly_factor <= 1:
            raise InvalidPositionInputError(f"half_kelly_factor must be in (0,1], got {self.half_kelly_factor}")
        if self.vol_sigma_multiplier <= 0:
            raise InvalidPositionInputError("vol_sigma_multiplier must be positive")
        if not 0 < self.vol_halve_factor <= 1:
            raise InvalidPositionInputError("vol_halve_factor must be in (0,1]")
        if self.var_threshold <= 0 or self.cvar_threshold <= 0:
            raise InvalidPositionInputError("var/cvar thresholds must be positive")
        if self.cvar_threshold < self.var_threshold:
            raise InvalidPositionInputError("cvar_threshold must be >= var_threshold")
        if not 0 < self.max_participation_rate <= 1:
            raise InvalidPositionInputError("max_participation_rate must be in (0,1]")
        if self.exit_days_hard <= self.exit_days_soft:
            raise InvalidPositionInputError("exit_days_hard must be > exit_days_soft")
        if not 0 < self.exit_soft_discount <= 1:
            raise InvalidPositionInputError("exit_soft_discount must be in (0,1]")
        if self.capacity_veto_ratio < self.capacity_warn_ratio:
            raise InvalidPositionInputError("capacity_veto_ratio must be >= capacity_warn_ratio")
        if self.max_impact_cost <= 0:
            raise InvalidPositionInputError("max_impact_cost must be positive")
        if not 0 < self.default_single_position_cap <= 1:
            raise InvalidPositionInputError("default_single_position_cap must be in (0,1]")


# ──────────────────────────────────────────────────────────────────────────────
# 输入数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SymbolInput:
    """单标的输入数据。"""

    symbol: str
    price: float  # 当前价格
    current_qty: int = 0  # 当前持仓量(股)
    avg_daily_volume: float = 0.0  # 20日均量(股)
    target_weight: float | None = None  # 目标权重(D-PF-CORE, None=降级)
    win_probability: float | None = None  # 胜率p(密度预测, None=降级)
    win_loss_ratio: float | None = None  # 盈亏比b(密度预测, None=降级)
    current_volatility: float | None = None  # 当前波动率σ
    hist_vol_mean: float | None = None  # 历史波动率均值
    hist_vol_std: float | None = None  # 历史波动率标准差
    strategy_capacity: float = 0.0  # 策略历史最大持仓市值
    is_st: bool = False
    market_cap_yi: float = 0.0


@dataclass(frozen=True)
class PositionSizingInput:
    """仓位决策聚合输入。"""

    symbols: list[SymbolInput]
    nav: float  # 当前净值(AUM)
    strategy_id: str
    trade_date: date
    risk_limits: RiskLimits | None = None  # D-RISK (CTR-003)
    capital_curve_discount: float = 1.0  # POS-007 资金曲线缩放系数
    capital_curve_cap: float = 1.0  # POS-007 仓位上限
    defensive_only: bool = False  # POS-007 EMERGENCY 禁止新开仓
    max_investable: float | None = None  # POS-006 可投资上限
    calendar_cap_adjustment: float = 1.0  # POS-017 日历仓位上限调整
    calendar_block_new: bool = False  # POS-017 全面否决新开仓
    calendar_block_symbols: frozenset[str] = field(default_factory=frozenset)
    calendar_force_clear_symbols: frozenset[str] = field(default_factory=frozenset)
    var_95: float | None = None  # 前瞻95%VaR(D-RISK/D-ML-SERVE)
    cvar_95: float | None = None  # 前瞻95%CVaR
    market_regime: SizingMarketRegime | None = None  # D-SIGNAL (12态, §7.3 v8.1)
    is_event_driven: bool = False  # overlay: 事件驱动→基础仓位×70%
    is_sector_rotation: bool = False  # overlay: 板块轮动→行业集中度放宽(POS-010消费, POS-001透传)


# ──────────────────────────────────────────────────────────────────────────────
# 输出数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PositionTarget:
    """单标的目标仓位。"""

    symbol: str
    target_qty: int
    current_qty: int
    delta: int  # target - current
    target_weight: float
    reason: str
    # sizing_basis（31号 §2.3.4 binding constraint 命名, 归因审计用）:
    # 记录标的级约束级联中最终 binding（实际限住仓位）的约束名——级联只减不增,
    # 最后一个实际缩减的步骤产出最终权重即 binding。空串=非 sizing 裁决路径
    # （veto 保持现仓/日历强清）。组合级缩放（C2/POS-006/POS-007）不改写本字段,
    # 在 plan.constraints_check 中记录。
    sizing_basis: str = ""


@dataclass(frozen=True)
class ConstraintCheck:
    """单约束检查结果。"""

    constraint_id: str
    passed: bool
    action: str  # "pass" / "truncate" / "veto" / "warn" / "degraded"
    detail: str = ""


@dataclass(frozen=True)
class PositionSizingPlan:
    """仓位方案 (CTR-POS-001, 设计真源 §8)。

    与 position_limit_enforcer.PositionPlan 同名不同义——彼处为简单持仓列表,
    本处为完整仓位裁决契约, 故冠 Sizing 后缀以区分 (ARCH-034)。
    """

    plan_id: str
    strategy_id: str
    positions: dict[str, PositionTarget]
    cash_reserve: float
    total_exposure: float
    capital_curve_discount: float
    calendar_constraint_active: bool
    volatility_adjustment: float
    constraints_check: dict[str, Any]
    created_at: datetime
    idempotency_key: str
    schema_version: str = "1.0"
    degraded: bool = False


# ──────────────────────────────────────────────────────────────────────────────
# 流水线内部上下文 (避免 Long Parameter List, §5.150/§5.158)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class _SymbolSizingContext:
    """单标的处理上下文——捆绑逐标的处理所需的共享参数(配置/上限/调整系数/检查列表)。"""

    cfg: PositionSizingConfig
    single_cap: float
    total_cap: float
    var_adjust: float
    gross_leverage: float
    checks: list[ConstraintCheck]


@dataclass
class _SizingState:
    """仓位决策流水线状态——组合级累加器, 在各阶段间传递(positions/总权重/波动率调整等)。"""

    positions: dict[str, PositionTarget] = field(default_factory=dict)
    total_weight: float = 0.0
    vol_product: float = 1.0
    vol_count: int = 0
    degraded: bool = False
    regime: SizingMarketRegime = SizingMarketRegime.NARROW_RANGE
    market_cap: float = 0.0
    total_cap: float = 0.0


# ──────────────────────────────────────────────────────────────────────────────
# Kelly 计算工具
# ──────────────────────────────────────────────────────────────────────────────


def _compute_kelly_fraction(p: float, b: float) -> float:
    """计算 Kelly 分数 f* = (bp - q) / b, q = 1-p。

    f* <= 0 表示无正期望 → 不下注(返回0)。

    Raises:
        KellyEstimationError: p 不在 (0,1) 或 b <= 0
    """
    if not 0 < p < 1:
        raise KellyEstimationError(f"win_probability must be in (0,1), got {p}")
    if b <= 0:
        raise KellyEstimationError(f"win_loss_ratio must be positive, got {b}")
    q = 1.0 - p
    f_star = (b * p - q) / b
    return max(0.0, f_star)


# ──────────────────────────────────────────────────────────────────────────────
# 仓位决策引擎
# ──────────────────────────────────────────────────────────────────────────────


class PositionSizingEngine:
    """仓位决策引擎——预筛+Kelly+13约束+降级模式。

    用法:
        engine = PositionSizingEngine()
        plan = engine.size(PositionSizingInput(
            symbols=[SymbolInput("000001.SZ", price=10.0, ...)],
            nav=1_000_000.0,
            strategy_id="strat_001",
            trade_date=date(2026, 8, 3),
            risk_limits=risk_limits,
            ...
        ))
        for symbol, target in plan.positions.items():
            # 执行 target.delta 股的买卖

    Args:
        config: 仓位决策配置(约束阈值)
        clock: 可选时间源(测试注入)
    """

    def __init__(
        self,
        config: PositionSizingConfig | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._config = config or PositionSizingConfig()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @property
    def config(self) -> PositionSizingConfig:
        return self._config

    # ── 主入口 ──

    def size(self, inp: PositionSizingInput) -> PositionSizingPlan:
        """执行仓位决策流水线, 产出 PositionSizingPlan。

        流水线: 市场状态/上限 → 逐标的(预筛+Kelly+约束) → 组合缩放 → 输出
        """
        self._validate_input(inp)
        cfg = self._config
        checks: list[ConstraintCheck] = []

        # 组合级上下文准备: 市场状态 + C13 总仓位上限
        state = _SizingState()
        state.regime, state.market_cap, state.total_cap, state.degraded = self._resolve_market_context(inp, cfg, checks)
        # C12 风控单票上限 + 总杠杆 (RiskLimits.symbol_overrides 覆盖默认)
        single_cap = cfg.default_single_position_cap
        gross_leverage = 1.0
        if inp.risk_limits is not None:
            single_cap = inp.risk_limits.max_single_position
            gross_leverage = inp.risk_limits.max_gross_leverage
        # C4/C5 VaR/CVaR 下调 (组合级)
        var_adjust = 1.0
        if inp.var_95 is not None and inp.var_95 > cfg.var_threshold:
            var_adjust *= cfg.var_reduce_factor
            checks.append(
                ConstraintCheck(
                    "C4", False, "truncate", f"VaR {inp.var_95:.4f}>{cfg.var_threshold} → ×{cfg.var_reduce_factor}"
                )
            )
        if inp.cvar_95 is not None and inp.cvar_95 > cfg.cvar_threshold:
            var_adjust *= cfg.cvar_reduce_factor
            checks.append(
                ConstraintCheck(
                    "C5", False, "truncate", f"CVaR {inp.cvar_95:.4f}>{cfg.cvar_threshold} → ×{cfg.cvar_reduce_factor}"
                )
            )
        ctx = _SymbolSizingContext(cfg, single_cap, state.total_cap, var_adjust, gross_leverage, checks)

        # 逐标的处理: 预筛+Kelly+约束
        for sym in inp.symbols:
            result = self._process_symbol(sym, inp, ctx)
            if result is None:
                continue
            tgt, weight, vol_adj = result
            state.positions[sym.symbol] = tgt
            state.total_weight += weight
            if vol_adj < 1.0:
                state.vol_product *= vol_adj
                state.vol_count += 1

        # 组合级约束缩放
        self._apply_portfolio_scaling(inp, state, gross_leverage, checks)

        return self._build_plan(inp, checks, state)

    # ── 组合级上下文准备 ──

    def _resolve_market_context(
        self, inp: PositionSizingInput, cfg: PositionSizingConfig, checks: list[ConstraintCheck]
    ) -> tuple[SizingMarketRegime, float, float, bool]:
        """确定市场状态 + C13 总仓位上限。返回(regime, market_cap, total_cap, degraded)。"""
        degraded = False
        regime = inp.market_regime or cfg.degradation_market_regime
        if inp.market_regime is None:
            degraded = True
            checks.append(ConstraintCheck("C13", False, "degraded", "D-SIGNAL缺失, 默认状态④(40%)"))
        market_cap = MARKET_REGIME_CAPS[regime]
        total_cap = min(market_cap, inp.capital_curve_cap, inp.calendar_cap_adjustment)
        # overlay: 事件驱动叠加态 → 基础仓位×70% (§7.3 v8.1, 正交修饰, 不占 enum)
        if inp.is_event_driven:
            total_cap *= 0.70
            checks.append(ConstraintCheck("overlay", True, "truncate", "事件驱动overlay ×0.70"))
        return regime, market_cap, total_cap, degraded

    # ── 逐标的处理 ──

    def _process_symbol(
        self, sym: SymbolInput, inp: PositionSizingInput, ctx: _SymbolSizingContext
    ) -> tuple[PositionTarget, float, float] | None:
        """处理单个标的: 预筛 → Kelly → 约束链 → 返回(target, weight, vol_adj)。"""
        # POS-017 日历约束: 标的级否决
        vetoed, force_target = self._check_calendar_veto(sym, inp, ctx.checks)
        if vetoed:
            if force_target is not None:
                return force_target, 0.0, 1.0
            return None

        # [0] 预筛阶段
        if self._prefilter(sym, inp, ctx) is None:
            return None  # 全否决, 跳过

        # Kelly 计算 + C1 半Kelly
        weight, kelly_degraded = self._compute_weight(sym, inp, ctx)
        if kelly_degraded:
            ctx.checks.append(ConstraintCheck("Kelly", False, "degraded", f"{sym.symbol} 密度预测缺失, 降级等权"))
        # sizing_basis 初始判定（31号 §2.3.4：策略意愿 vs Kelly 预算取小者 binding）
        basis = self._initial_sizing_basis(sym, ctx.cfg)

        # C3 波动率检查
        vol_adj = self._apply_volatility_check(sym, ctx.cfg, ctx.checks)

        # C12 单票上限 (symbol_overrides 覆盖) + 波动率/VaR 调整
        sym_cap = ctx.single_cap
        if inp.risk_limits is not None and sym.symbol in inp.risk_limits.symbol_overrides:
            sym_cap = inp.risk_limits.symbol_overrides[sym.symbol]
        if weight > sym_cap:
            basis = SIZING_BASIS_SINGLE_NAME_CAP
        weight = min(weight, sym_cap) * vol_adj * ctx.var_adjust
        # 级联只减不增——最后一个实际缩减的步骤即 binding（31号 §2.3.4 归因语义）
        if vol_adj < 1.0:
            basis = SIZING_BASIS_VOLATILITY_CHECK
        if ctx.var_adjust < 1.0:
            basis = (
                SIZING_BASIS_CVAR_CAP
                if inp.cvar_95 is not None and inp.cvar_95 > ctx.cfg.cvar_threshold
                else SIZING_BASIS_VAR_CAP
            )

        # C7/C8 退出时间减仓 (预筛已检查, 此处应用减仓)
        weight_after_exit = self._apply_exit_time_adjust(sym, inp, ctx.cfg, weight, ctx.checks)
        if weight_after_exit < weight:
            basis = SIZING_BASIS_EXIT_TIME_CAP
        weight = weight_after_exit

        # C6/C9/C11 否决 (参与率/容量/冲击成本)
        vetoed, veto_result = self._apply_veto_constraints(sym, inp, ctx, weight, vol_adj)
        if vetoed:
            return veto_result

        # 重新计算目标量 (经所有调整后)
        target_qty = int(weight * inp.nav / sym.price) if sym.price > 0 else 0
        return (
            self._make_target(sym, target_qty, f"Kelly+约束裁决 w={weight:.4f}", inp.nav, sizing_basis=basis),
            weight,
            vol_adj,
        )

    def _initial_sizing_basis(self, sym: SymbolInput, cfg: PositionSizingConfig) -> str:
        """sizing_basis 初始判定（31号 §2.3.4 min(策略意愿, Kelly 预算) 取小者 binding）。

        Kelly 路径：target_weight ≤ 半Kelly → strategy_intent（策略意愿更保守），
        否则 kelly_budget（Kelly 风险预算限住）；f*≤0 不下注亦归 kelly_budget。
        降级路径：有目标权重 → strategy_intent；全无 → degraded_equal_weight。
        """
        if sym.win_probability is not None and sym.win_loss_ratio is not None:
            f_star = _compute_kelly_fraction(sym.win_probability, sym.win_loss_ratio)
            w_kelly = cfg.half_kelly_factor * f_star
            if sym.target_weight is not None and sym.target_weight <= w_kelly:
                return SIZING_BASIS_STRATEGY_INTENT
            return SIZING_BASIS_KELLY_BUDGET
        if sym.target_weight is not None:
            return SIZING_BASIS_STRATEGY_INTENT
        return SIZING_BASIS_DEGRADED

    # ── POS-017 日历约束 ──

    def _check_calendar_veto(
        self, sym: SymbolInput, inp: PositionSizingInput, checks: list[ConstraintCheck]
    ) -> tuple[bool, PositionTarget | None]:
        """POS-017 日历否决。返回(vetoed, force_clear_target)。

        vetoed=True 且 force_target 非 None → 强制清仓(返回该 target);
        vetoed=True 且 force_target=None → 跳过该标的;
        vetoed=False → 继续正常处理。
        """
        if sym.symbol in inp.calendar_force_clear_symbols:
            checks.append(ConstraintCheck("POS-017", False, "veto", f"{sym.symbol} 日历强制清仓"))
            if sym.current_qty > 0:
                return True, self._make_target(sym, 0, "日历强制清仓", inp.nav)
            return True, None

        if inp.calendar_block_new and sym.current_qty == 0:
            checks.append(ConstraintCheck("POS-017", False, "veto", f"{sym.symbol} 日历否决新开仓"))
            return True, None

        if sym.symbol in inp.calendar_block_symbols and sym.current_qty == 0:
            checks.append(ConstraintCheck("POS-017", False, "veto", f"{sym.symbol} 日历标的级否决新开仓"))
            return True, None

        return False, None

    # ── [0] 预筛阶段 ──

    def _prefilter(self, sym: SymbolInput, inp: PositionSizingInput, ctx: _SymbolSizingContext) -> bool | None:
        """预筛: 退出时间检查 + 流动性上限预筛。返回 True=通过, None=跳过。"""
        cfg = ctx.cfg
        # C7 退出时间硬限 (基于当前持仓)
        if sym.avg_daily_volume > 0 and sym.current_qty > 0:
            exit_days = sym.current_qty / sym.avg_daily_volume
            if exit_days > cfg.exit_days_hard:
                ctx.checks.append(
                    ConstraintCheck(
                        "C7",
                        False,
                        "truncate",
                        f"{sym.symbol} 退出时间 {exit_days:.1f}>{cfg.exit_days_hard}天 → 强制减仓",
                    )
                )

        # 流动性预筛: 最大可能仓位的参与率
        if sym.avg_daily_volume > 0 and sym.price > 0:
            max_qty = ctx.single_cap * inp.nav / sym.price
            max_participation = max_qty / sym.avg_daily_volume
            if max_participation > cfg.max_participation_rate:
                # 低流动性标的: Kelly 后会被精确否决, 但先标记
                ctx.checks.append(
                    ConstraintCheck(
                        "prefilter",
                        False,
                        "warn",
                        f"{sym.symbol} 流动性预筛: max参与率 {max_participation:.4f}>{cfg.max_participation_rate}",
                    )
                )

        return True

    # ── Kelly 计算 + C1 ──

    def _compute_weight(
        self, sym: SymbolInput, inp: PositionSizingInput, ctx: _SymbolSizingContext
    ) -> tuple[float, bool]:
        """计算标的权重: Kelly(半Kelly) 或降级等权。返回(weight, degraded)。"""
        cfg = ctx.cfg
        num_symbols = max(len(inp.symbols), 1)

        if sym.win_probability is not None and sym.win_loss_ratio is not None:
            # Kelly 路径
            f_star = _compute_kelly_fraction(sym.win_probability, sym.win_loss_ratio)
            w_kelly = cfg.half_kelly_factor * f_star  # C1 半Kelly

            if sym.target_weight is not None:
                # 有目标权重: 取 min(target, half_kelly)
                w = min(sym.target_weight, w_kelly)
            else:
                w = w_kelly

            if f_star <= 0:
                ctx.checks.append(ConstraintCheck("C1", True, "pass", f"{sym.symbol} f*={f_star:.4f}<=0 → 不下注"))
                return 0.0, False

            ctx.checks.append(ConstraintCheck("C1", True, "pass", f"{sym.symbol} f*={f_star:.4f} → 半Kelly w={w:.4f}"))
            return w, False

        # 降级路径: 无密度预测
        if sym.target_weight is not None:
            # 有目标权重但无Kelly: 直接用目标权重
            w = sym.target_weight
        else:
            # 全降级: 等权分配 (市场状态上限 / 标的数)
            w = ctx.total_cap / num_symbols

        return w, (sym.win_probability is None)

    # ── C3 波动率检查 ──

    def _apply_volatility_check(
        self, sym: SymbolInput, cfg: PositionSizingConfig, checks: list[ConstraintCheck]
    ) -> float:
        """C3: 波动率超 μ+2σ → 仓位减半。返回调整系数(1.0 或 0.5)。"""
        if (
            sym.current_volatility is not None
            and sym.hist_vol_mean is not None
            and sym.hist_vol_std is not None
            and sym.hist_vol_std > 0
        ):
            threshold = sym.hist_vol_mean + cfg.vol_sigma_multiplier * sym.hist_vol_std
            if sym.current_volatility > threshold:
                checks.append(
                    ConstraintCheck(
                        "C3",
                        False,
                        "truncate",
                        f"{sym.symbol} 波动率 {sym.current_volatility:.4f}>{threshold:.4f} → ×{cfg.vol_halve_factor}",
                    )
                )
                return cfg.vol_halve_factor
        return 1.0

    # ── C7/C8 退出时间减仓 ──

    def _apply_exit_time_adjust(
        self,
        sym: SymbolInput,
        inp: PositionSizingInput,
        cfg: PositionSizingConfig,
        weight: float,
        checks: list[ConstraintCheck],
    ) -> float:
        """C7/C8: 退出时间>3天强制减仓, >1天折扣。"""
        if sym.avg_daily_volume <= 0 or sym.current_qty <= 0:
            return weight
        exit_days = sym.current_qty / sym.avg_daily_volume
        if exit_days > cfg.exit_days_hard:
            # 强制减仓至可退出量(3天内)
            exitable_qty = sym.avg_daily_volume * cfg.exit_days_hard
            exitable_weight = exitable_qty * sym.price / inp.nav if inp.nav > 0 else 0.0
            return min(weight, exitable_weight)
        if exit_days > cfg.exit_days_soft:
            checks.append(
                ConstraintCheck(
                    "C8",
                    False,
                    "truncate",
                    f"{sym.symbol} 退出时间 {exit_days:.1f}>{cfg.exit_days_soft}天 → ×{cfg.exit_soft_discount}",
                )
            )
            return weight * cfg.exit_soft_discount
        return weight

    # ── C6/C9/C11 否决 ──

    def _apply_veto_constraints(
        self,
        sym: SymbolInput,
        inp: PositionSizingInput,
        ctx: _SymbolSizingContext,
        weight: float,
        vol_adj: float,
    ) -> tuple[bool, tuple[PositionTarget, float, float] | None]:
        """C6/C9/C11 否决。返回(vetoed, result)。

        vetoed=False → 继续正常处理;
        vetoed=True 且 result 非 None → 否决保持现仓(返回该 result);
        vetoed=True 且 result=None → 否决跳过该标的。
        """
        cfg = ctx.cfg
        target_qty = int(weight * inp.nav / sym.price) if sym.price > 0 else 0
        participation = target_qty / sym.avg_daily_volume if sym.avg_daily_volume > 0 else 0.0

        # C6 参与率否决 (精确检查, 用实际目标量): 有现仓保持, 无现仓跳过
        if participation > cfg.max_participation_rate:
            ctx.checks.append(
                ConstraintCheck(
                    "C6", False, "veto", f"{sym.symbol} 参与率 {participation:.4f}>{cfg.max_participation_rate}"
                )
            )
            if sym.current_qty > 0:
                return True, (self._make_target(sym, sym.current_qty, "参与率否决, 保持现仓", inp.nav), 0.0, vol_adj)
            return True, None

        # C9 策略容量预警
        if self._check_capacity_veto(sym, inp, ctx):
            return True, None  # 容量超限且无持仓 → 跳过

        # C11 冲击成本否决 (sqrt模型): 有现仓保持, 无现仓跳过
        impact_cost = cfg.impact_cost_coeff * math.sqrt(participation) if participation > 0 else 0.0
        if impact_cost > cfg.max_impact_cost:
            ctx.checks.append(
                ConstraintCheck("C11", False, "veto", f"{sym.symbol} 冲击成本 {impact_cost:.6f}>{cfg.max_impact_cost}")
            )
            if sym.current_qty > 0:
                return True, (self._make_target(sym, sym.current_qty, "冲击成本否决, 保持现仓", inp.nav), 0.0, vol_adj)
            return True, None

        return False, None

    def _check_capacity_veto(self, sym: SymbolInput, inp: PositionSizingInput, ctx: _SymbolSizingContext) -> bool:
        """C9: 容量超 veto_ratio 且无持仓 → 跳过。返回 True=跳过(仅当无现仓)。"""
        if sym.strategy_capacity <= 0 or inp.nav <= 0:
            return False
        cfg = ctx.cfg
        cap_ratio = sym.strategy_capacity / inp.nav
        if cap_ratio > cfg.capacity_veto_ratio:
            ctx.checks.append(
                ConstraintCheck(
                    "C9", False, "veto", f"{sym.symbol} 容量 {cap_ratio:.2f}>{cfg.capacity_veto_ratio} → 否决新资金"
                )
            )
            return sym.current_qty == 0  # 仅无现仓时跳过; 有现仓则继续(仅记录)
        if cap_ratio > cfg.capacity_warn_ratio:
            ctx.checks.append(
                ConstraintCheck("C9", False, "warn", f"{sym.symbol} 容量 {cap_ratio:.2f}>{cfg.capacity_warn_ratio}")
            )
        return False

    # ── 组合级约束缩放 ──

    def _apply_portfolio_scaling(
        self,
        inp: PositionSizingInput,
        state: _SizingState,
        gross_leverage: float,
        checks: list[ConstraintCheck],
    ) -> None:
        """组合级约束: C2 风险配额 + POS-007 资金曲线 + POS-006 现金 + defensive_only。"""
        # C2 风险配额 (组合级: total_exposure <= gross_leverage × total_cap)
        max_exposure = min(gross_leverage, state.total_cap)
        if state.total_weight > max_exposure:
            scale = max_exposure / state.total_weight if state.total_weight > 0 else 0.0
            checks.append(
                ConstraintCheck(
                    "C2",
                    False,
                    "truncate",
                    f"总仓位 {state.total_weight:.4f}>{max_exposure:.4f} → 等比缩放 ×{scale:.4f}",
                )
            )
            state.positions, state.total_weight = self._rescale_positions(state.positions, inp, scale)

        # POS-007 资金曲线缩放
        cc_discount = inp.capital_curve_discount
        if cc_discount < 1.0:
            state.positions, state.total_weight = self._rescale_positions(state.positions, inp, cc_discount)
            checks.append(ConstraintCheck("POS-007", False, "truncate", f"资金曲线缩放 ×{cc_discount:.4f}"))

        # POS-006 现金约束
        if inp.max_investable is not None:
            investable_weight = inp.max_investable / inp.nav if inp.nav > 0 else 0.0
            if state.total_weight > investable_weight:
                scale = investable_weight / state.total_weight if state.total_weight > 0 else 0.0
                state.positions, state.total_weight = self._rescale_positions(state.positions, inp, scale)
                checks.append(ConstraintCheck("POS-006", False, "truncate", f"现金约束缩放 ×{scale:.4f}"))

        # POS-007 defensive_only: 禁止新开仓 (只允许减仓)
        if inp.defensive_only:
            state.positions = self._enforce_defensive_only(state.positions, inp)
            checks.append(ConstraintCheck("POS-007", True, "pass", "defensive_only: 禁止新开仓, 仅保留减仓"))

    def _build_plan(
        self, inp: PositionSizingInput, checks: list[ConstraintCheck], state: _SizingState
    ) -> PositionSizingPlan:
        """构造最终 PositionSizingPlan。"""
        vol_adjustment = state.vol_product ** (1.0 / state.vol_count) if state.vol_count > 0 else 1.0
        idempotency_key = self._make_idempotency_key(inp)
        cash_reserve = inp.nav * (1.0 - state.total_weight)
        cc_discount = inp.capital_curve_discount
        degraded = state.degraded or any(c.action == "degraded" for c in checks)

        return PositionSizingPlan(
            plan_id=f"plan_{idempotency_key}",
            strategy_id=inp.strategy_id,
            positions=state.positions,
            cash_reserve=cash_reserve,
            total_exposure=state.total_weight,
            capital_curve_discount=cc_discount,
            calendar_constraint_active=inp.calendar_cap_adjustment < 1.0 or inp.calendar_block_new,
            volatility_adjustment=vol_adjustment,
            constraints_check={
                "checks": [c.__dict__ for c in checks],
                "degraded": degraded,
                "regime": state.regime.value,
                "market_cap": state.market_cap,
                "total_cap": state.total_cap,
            },
            created_at=self._clock(),
            idempotency_key=idempotency_key,
            degraded=degraded,
        )

    # ── 辅助方法 ──

    def _rescale_positions(
        self,
        positions: dict[str, PositionTarget],
        inp: PositionSizingInput,
        scale: float,
    ) -> tuple[dict[str, PositionTarget], float]:
        """等比缩放所有仓位。"""
        new_positions: dict[str, PositionTarget] = {}
        total_weight = 0.0
        for symbol, tgt in positions.items():
            new_weight = tgt.target_weight * scale
            sym = next((s for s in inp.symbols if s.symbol == symbol), None)
            price = sym.price if sym else 1.0
            new_qty = int(new_weight * inp.nav / price) if price > 0 else 0
            new_positions[symbol] = PositionTarget(
                symbol=symbol,
                target_qty=new_qty,
                current_qty=tgt.current_qty,
                delta=new_qty - tgt.current_qty,
                target_weight=new_weight,
                reason=tgt.reason + f" → 缩放×{scale:.4f}",
                sizing_basis=tgt.sizing_basis,  # 保留标的级 binding（组合级缩放在 constraints_check 记录）
            )
            total_weight += new_weight
        return new_positions, total_weight

    def _enforce_defensive_only(
        self,
        positions: dict[str, PositionTarget],
        inp: PositionSizingInput,
    ) -> dict[str, PositionTarget]:
        """defensive_only: 禁止新开仓, 只保留减仓/持平。"""
        new_positions: dict[str, PositionTarget] = {}
        for symbol, tgt in positions.items():
            if tgt.delta > 0:
                # 新开仓/加仓 → 禁止, 目标=现仓
                new_positions[symbol] = PositionTarget(
                    symbol=symbol,
                    target_qty=tgt.current_qty,
                    current_qty=tgt.current_qty,
                    delta=0,
                    target_weight=tgt.target_weight,
                    reason=tgt.reason + " → defensive_only禁止加仓",
                    sizing_basis=tgt.sizing_basis,
                )
            else:
                new_positions[symbol] = tgt
        return new_positions

    def _make_target(
        self, sym: SymbolInput, target_qty: int, reason: str, nav: float, sizing_basis: str = ""
    ) -> PositionTarget:
        """构造 PositionTarget (target_weight = target_qty × price / nav)。"""
        weight = target_qty * sym.price / nav if nav > 0 else 0.0
        return PositionTarget(
            symbol=sym.symbol,
            target_qty=target_qty,
            current_qty=sym.current_qty,
            delta=target_qty - sym.current_qty,
            target_weight=weight,
            reason=reason,
            sizing_basis=sizing_basis,
        )

    def _make_idempotency_key(self, inp: PositionSizingInput) -> str:
        """生成幂等键: strategy_id:trade_date:hash(target_weights)[:8]。"""
        weights = sorted((s.symbol, s.target_weight if s.target_weight is not None else 0.0) for s in inp.symbols)
        weights_str = ",".join(f"{sym}:{w:.6f}" for sym, w in weights)
        digest = hashlib.md5(weights_str.encode("utf-8")).hexdigest()[:8]
        return f"{inp.strategy_id}:{inp.trade_date.isoformat()}:{digest}"

    def _validate_input(self, inp: PositionSizingInput) -> None:
        """输入校验。"""
        if inp.nav <= 0:
            raise InvalidPositionInputError(f"nav must be positive, got {inp.nav}")
        if not inp.symbols:
            raise InvalidPositionInputError("symbols list is empty")
        for sym in inp.symbols:
            if sym.price <= 0:
                raise InvalidPositionInputError(f"{sym.symbol} price must be positive, got {sym.price}")
            if sym.target_weight is not None and sym.target_weight < 0:
                raise InvalidPositionInputError(f"{sym.symbol} target_weight must be >= 0, got {sym.target_weight}")
