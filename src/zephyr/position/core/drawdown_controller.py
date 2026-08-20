# [BLUEPRINT] MOD-POS-008 | docs/03_modules/_domain_position/drawdown_controller/blueprint.md
# [MODULE] zephyr.position.core.drawdown_controller
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-POS-001(仓位上限调整) ; D-EX-CORE(执行减仓) ; D-REPORTING(审计)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 响应级别单调不减(升级立即/降级走回补); 取最严(黑天鹅>系统性风险>策略止损); 不覆盖风控熔断(KS-L4由stop_loss触发); BS-007→KillSwitch建议非直接触发
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDrawdownControlError
# [TESTS] tests/position/test_drawdown_controller.py
# [A_module] module_id=MOD-POS-008 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Drawdown Controller — 回撤控制器 (MOD-POS-008)

消费组合回撤 + VaR/CVaR 系统性风险分级 + 黑天鹅模式信号, 产出分级响应指令
(减仓比例/仓位上限/动作列表/Kill Switch 建议)。

三级响应 (D-POSITION §1.3 POS-08):
    1. 系统性风险 5 级 (VaR/CVaR 驱动): 绿/黄/橙/红/黑
    2. 策略级止损: Soft Stop(单策略回撤>5%)/Hard Stop(>10%)
    3. 黑天鹅 7 模式 (§14.3): BS-001~BS-007

回撤回补恢复: 回撤回补 50% → 逐步恢复仓位上限(每步 25%)。

边界: 不覆盖风控熔断(KS-L4 由 D-RISK stop_loss 触发); BS-007 产出 Kill Switch 建议,
委托 stop_loss 执行, 本模块不直接触发。

属 A 类基础设施(阈值判定+分级响应), 5 级阈值与黑天鹅处置为 C 类可调参数。
依据: D:\临时工作区\依赖图-D-POSITION-仓位管理域.md §1.3 POS-08, §14.3 黑天鹅模式
SSoT: depgraph MOD-POS-008
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 组合回撤信息 DrawdownInfo
#   fields: drawdown_pct(≤0) + peak_nav + current_nav + recovered_pct回补比例
#   code: evaluate() 参数 drawdown_info，来自POS-07 Capital Curve Manager
# - id: I2
#   name: VaR/CVaR系统性风险指标 VarCvarMetrics
#   fields: var_95 + cvar_95(cvar≥var)
#   code: evaluate() 参数 var_cvar，来自D-RISK risk_limits
# - id: I3
#   name: 黑天鹅模式信号 BlackSwanSignal
#   fields: active_modes 触发的BS-001~BS-007模式集合
#   code: evaluate() 参数 black_swan，来自D-RISK/D-SIGNAL
# - id: I4
#   name: 策略级PnL列表
#   fields: [{strategy_id, drawdown_pct(≤0)}]
#   code: evaluate() 参数 strategy_pnls，来自D-PF-CORE
# - id: I5
#   name: 回撤控制可调配置 DrawdownControllerConfig
#   fields: soft_stop=5% hard_stop=10% var黄2%/橙4%/红6% cvar黑10% 回补触发50% 每步25%
#   code: DrawdownControllerConfig L287
# 层: 算法
# - id: A1
#   name_zh: ① 系统性风险5级判定
#   name_en: _evaluate_risk_level
#   intro: 用VaR/CVaR把市场风险分成绿黄橙红黑5级
#   desc: CVaR>10%→BLACK；VaR>6%→RED、>4%→ORANGE、>2%→YELLOW、否则GREEN；对应仓位上限1.0/0.5/0.5/0.5/0.0(单调非增,P1-4裁定)
#   inputs: I2 I5
#   outputs: SystemicRiskLevel及仓位上限系数
# - id: A2
#   name_zh: ② 策略级止损判定
#   name_en: _evaluate_strategy_stops
#   intro: 单策略回撤超5%砍仓、超10%直接关闭策略
#   desc: |dd|>hard_stop→HARD关闭策略；|dd|>soft_stop→SOFT砍仓；否则NONE
#   inputs: I4 I5
#   outputs: StrategyStopLoss列表
# - id: A3
#   name_zh: ③ 黑天鹅处置
#   name_en: _evaluate_black_swan
#   intro: 多模式同触发视为BS-007系统性风险，建议Kill Switch
#   desc: ≥2模式或显式BS-007→cap=0+kill_advised；单模式查_BLACK_SWAN_CAP表取最严，-1=外部决定不参与取严
#   inputs: I3 I5
#   outputs: (cap系数, 动作列表, kill_advised)
#   invariant: BS-007→KillSwitch建议非直接触发，委托stop_loss执行
# - id: A4
#   name_zh: ④ 回撤回补恢复系数
#   name_en: _evaluate_recovery
#   intro: 回撤回补过半后按每步25%逐步放开仓位上限
#   desc: 无回撤或回补<50%→1.0；回补≥50%→steps=int(recovered/0.25)×0.25封顶1.0
#   inputs: I1 I5
#   outputs: recovery_factor 0.25~1.0
# - id: A5
#   name_zh: ⑤ 取最严合成分级响应
#   name_en: evaluate
#   intro: 把风险级/黑天鹅/恢复系数取最严合成最终响应指令
#   desc: position_cap=clamp(min(caps)×recovery,0,1)；reduce_ratio=1-cap；汇总动作列表
#   inputs: A1 A2 A3 A4
#   outputs: DrawdownResponse
#   invariant: 取最严(黑天鹅>系统性风险>策略止损)；响应级别单调不减；不覆盖KS-L4风控熔断
# 层: 输出
# - id: O1
#   name_zh: 分级响应指令
#   name_en: DrawdownResponse
#   intro: 风险级别+仓位上限+减仓比例+动作列表+策略止损清单
#   downstream: MOD-POS-001仓位上限调整 D-EX-CORE执行减仓 D-REPORTING审计
# - id: O2
#   name_zh: Kill Switch建议
#   name_en: kill_switch_advised
#   intro: BS-007触发时置True，委托D-RISK stop_loss执行熔断
#   downstream: D-RISK stop_loss
# [/ALGO_FLOW]
#
# 边:
# I1 --> A4
# I2 --> A1
# I3 --> A3
# I4 --> A2
# I5 --> A1
# I5 --> A2
# I5 --> A3
# I5 --> A4
# A1 --> A5
# A2 --> A5
# A3 --> A5
# A4 --> A5
# A5 --> O1
# A3 --> O2
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final[list[str]] = [
    "SystemicRiskLevel",
    "BlackSwanMode",
    "StopLossType",
    "DrawdownInfo",
    "VarCvarMetrics",
    "BlackSwanSignal",
    "StrategyPnl",
    "StrategyStopLoss",
    "DrawdownControllerConfig",
    "DrawdownResponse",
    "DrawdownController",
    "InvalidDrawdownControlError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class SystemicRiskLevel(str, Enum):
    """系统性风险 5 级 (基于 VaR/CVaR)。"""

    GREEN = "GREEN"  # VaR < 2%: 正常
    YELLOW = "YELLOW"  # VaR 2%-4%: 新开仓减半
    ORANGE = "ORANGE"  # VaR 4%-6%: 禁止新开 + 减仓(上限 50%)
    RED = "RED"  # VaR > 6%: 减仓 50% + 只平不开
    BLACK = "BLACK"  # CVaR > 10%: 全部清仓

    @property
    def position_cap(self) -> float:
        """该风险级别对应的仓位上限系数(1.0=无限制)。"""
        return _RISK_LEVEL_CAP[self]


_RISK_LEVEL_CAP: dict[SystemicRiskLevel, float] = {
    SystemicRiskLevel.GREEN: 1.0,
    SystemicRiskLevel.YELLOW: 0.5,  # 新开仓减半
    # 2026-08-16 双轮审查 P1-4 裁定: ORANGE 原值 0.7 致序列非单调
    # (YELLOW 0.5 → ORANGE 0.7 风险升级上限反而放宽), 降为 0.5 恢复单调;
    # 级别严格度由动作语义区分 (ORANGE 禁新开/RED 只平不开), 非由 cap 数值区分
    SystemicRiskLevel.ORANGE: 0.5,  # 禁止新开 + 减仓 (cap 与 YELLOW/RED 同档)
    SystemicRiskLevel.RED: 0.5,  # 减仓 50% + 只平不开
    SystemicRiskLevel.BLACK: 0.0,  # 全部清仓
}

# 级别严重度排序(用于取最严)
_RISK_SEVERITY: dict[SystemicRiskLevel, int] = {
    SystemicRiskLevel.GREEN: 0,
    SystemicRiskLevel.YELLOW: 1,
    SystemicRiskLevel.ORANGE: 2,
    SystemicRiskLevel.RED: 3,
    SystemicRiskLevel.BLACK: 4,
}


class BlackSwanMode(str, Enum):
    """黑天鹅 7 模式 (§14.3)。"""

    BS001_LIQUIDITY = "BS001_LIQUIDITY"  # 流动性蒸发
    BS002_CORRELATION = "BS002_CORRELATION"  # 相关性崩塌
    BS003_VOLATILITY = "BS003_VOLATILITY"  # 波动率爆发
    BS004_MARGIN = "BS004_MARGIN"  # 融资盘踩踏
    BS005_CONTAGION = "BS005_CONTAGION"  # 跨市场传导
    BS006_POLICY = "BS006_POLICY"  # 政策黑天鹅
    BS007_SYSTEMIC = "BS007_SYSTEMIC"  # 系统性风险(多模式同触发)


# 黑天鹅模式 → 仓位上限系数
_BLACK_SWAN_CAP: dict[BlackSwanMode, float] = {
    BlackSwanMode.BS001_LIQUIDITY: 0.05,  # 参与率收紧至 5%
    BlackSwanMode.BS002_CORRELATION: 0.5,  # 降总仓位
    BlackSwanMode.BS003_VOLATILITY: 0.5,  # 仓位减半
    BlackSwanMode.BS004_MARGIN: 0.5,  # 降杠杆敞口
    BlackSwanMode.BS005_CONTAGION: -1.0,  # 市场状态对应档位(动态, -1=外部决定)
    BlackSwanMode.BS006_POLICY: -1.0,  # 暂停受影响标的(动态)
    BlackSwanMode.BS007_SYSTEMIC: 0.0,  # Kill Switch
}

# VaR breach 状态 → position_cap 乘性折扣 (36号 §3.15 协同表:
# NORMAL×1.0 / BREACHED×0.8 / RECOVERY×0.9; 与回撤状态机正交, 乘性叠加)
_VAR_BREACH_CAP_MULTIPLIER: Final = {"NORMAL": 1.0, "BREACHED": 0.8, "RECOVERY": 0.9}


class StopLossType(str, Enum):
    """策略级止损类型。"""

    NONE = "NONE"  # 未触发
    SOFT = "SOFT"  # 单策略回撤 > 5%: 砍仓
    HARD = "HARD"  # 单策略回撤 > 10%: 关闭策略


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidDrawdownControlError(ZephyrBaseError):
    """回撤输入数据非法(回撤率越界/VaR 为负/策略 PnL 缺失等)。"""

    error_code = "ZA-POS-0008"


# ──────────────────────────────────────────────────────────────────────────────
# 输入数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DrawdownInfo:
    """组合回撤信息 (来自 POS-07 Capital Curve Manager)。

    Attributes:
        drawdown_pct: 当前回撤率(负数, 如 -0.08 = 回撤 8%; 0 = 无回撤)
        peak_nav: 峰值净值
        current_nav: 当前净值
        recovered_pct: 相对最大回撤的回补比例(0=未回补, 0.5=回补50%)
    """

    drawdown_pct: float
    peak_nav: float
    current_nav: float
    recovered_pct: float = 0.0


@dataclass(frozen=True)
class VarCvarMetrics:
    """VaR/CVaR 系统性风险指标 (来自 D-RISK risk_limits)。

    Attributes:
        var_95: 95% 置信度 VaR(正值, 如 0.025 = 2.5%)
        cvar_95: 95% 置信度 CVaR(正值, ≥ var_95)
    """

    var_95: float
    cvar_95: float


@dataclass(frozen=True)
class BlackSwanSignal:
    """黑天鹅模式信号 (来自 D-RISK / D-SIGNAL)。

    Attributes:
        active_modes: 当前触发的黑天鹅模式集合
    """

    active_modes: frozenset[BlackSwanMode] = field(default_factory=frozenset)

    @property
    def has_black_swan(self) -> bool:
        return len(self.active_modes) > 0

    @property
    def is_systemic(self) -> bool:
        """是否触发 BS-007 系统性风险(多模式同触发或显式 BS-007)。"""
        return BlackSwanMode.BS007_SYSTEMIC in self.active_modes or len(self.active_modes) >= 2


@dataclass(frozen=True)
class StrategyPnl:
    """单策略 PnL 信息 (来自 D-PF-CORE)。

    Attributes:
        strategy_id: 策略 ID
        drawdown_pct: 该策略回撤率(负数, 如 -0.06 = 回撤 6%)
    """

    strategy_id: str
    drawdown_pct: float


# ──────────────────────────────────────────────────────────────────────────────
# 输出数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class StrategyStopLoss:
    """单策略止损判定结果。

    Attributes:
        strategy_id: 策略 ID
        stop_type: 止损类型(NONE/SOFT/HARD)
        drawdown_pct: 触发回撤率
    """

    strategy_id: str
    stop_type: StopLossType
    drawdown_pct: float

    @property
    def triggered(self) -> bool:
        return self.stop_type != StopLossType.NONE


@dataclass(frozen=True)
class DrawdownResponse:
    """分级响应指令 (POS-008 输出)。

    Attributes:
        risk_level: 系统性风险级别
        position_cap: 仓位上限系数(取最严, 0=清仓, 1=无限制)
        reduce_ratio: 减仓比例(0=不减, 1=全清)
        actions: 动作列表(人类可读)
        strategy_stops: 策略级止损列表
        black_swan_modes: 触发的黑天鹅模式
        kill_switch_advised: 是否建议 Kill Switch(BS-007)
        recovery_factor: 回撤回补恢复系数(0=未恢复, 1=完全恢复)
    """

    risk_level: SystemicRiskLevel
    position_cap: float
    reduce_ratio: float
    actions: list[str] = field(default_factory=list)
    strategy_stops: list[StrategyStopLoss] = field(default_factory=list)
    black_swan_modes: frozenset[BlackSwanMode] = field(default_factory=frozenset)
    kill_switch_advised: bool = False
    recovery_factor: float = 1.0

    @property
    def allow_new_position(self) -> bool:
        """是否允许新开仓(橙/红/黑禁止新开)。"""
        return (
            self.risk_level
            not in (
                SystemicRiskLevel.ORANGE,
                SystemicRiskLevel.RED,
                SystemicRiskLevel.BLACK,
            )
            and not self.kill_switch_advised
        )

    @property
    def only_close(self) -> bool:
        """是否只平不开(红/黑)。"""
        return self.risk_level in (SystemicRiskLevel.RED, SystemicRiskLevel.BLACK)


# ──────────────────────────────────────────────────────────────────────────────
# 回撤控制器配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DrawdownControllerConfig:
    """回撤控制器可调参数(§5.150 参数对象, 避免 Long Parameter List)。

    Attributes:
        soft_stop_threshold: Soft Stop 回撤阈值(默认 0.05=5%)
        hard_stop_threshold: Hard Stop 回撤阈值(默认 0.10=10%)
        var_yellow: 黄级 VaR 阈值(默认 0.02)
        var_orange: 橙级 VaR 阈值(默认 0.04)
        var_red: 红级 VaR 阈值(默认 0.06)
        cvar_black: 黑级 CVaR 阈值(默认 0.10)
        recovery_step: 回补恢复每步比例(默认 0.25)
        recovery_trigger: 触发恢复的回补比例(默认 0.50)
    """

    soft_stop_threshold: float = 0.05
    hard_stop_threshold: float = 0.10
    var_yellow: float = 0.02
    var_orange: float = 0.04
    var_red: float = 0.06
    cvar_black: float = 0.10
    recovery_step: float = 0.25
    recovery_trigger: float = 0.50


# ──────────────────────────────────────────────────────────────────────────────
# 回撤控制器
# ──────────────────────────────────────────────────────────────────────────────


class DrawdownController:
    """回撤控制器——系统性风险 5 级 + 策略止损 + 黑天鹅处置 + 回撤回补恢复。

    用法::

        controller = DrawdownController()
        response = controller.evaluate(
            drawdown_info=DrawdownInfo(-0.08, 1.10, 1.012, 0.3),
            var_cvar=VarCvarMetrics(var_95=0.045, cvar_95=0.07),
            black_swan=BlackSwanSignal(frozenset({BlackSwanMode.BS003_VOLATILITY})),
            strategy_pnls=[StrategyPnl("alpha1", -0.06)],
        )
        if response.kill_switch_advised:
            # 委托 stop_loss 触发 Kill Switch
        if response.position_cap < 1.0:
            # 调整 POS-01 仓位上限

    Args:
        config: 可调参数配置(缺省用设计默认值)
    """

    def __init__(self, config: DrawdownControllerConfig | None = None) -> None:
        cfg = config or DrawdownControllerConfig()
        if cfg.soft_stop_threshold <= 0 or cfg.hard_stop_threshold <= 0:
            raise InvalidDrawdownControlError("stop thresholds must be positive")
        if cfg.soft_stop_threshold >= cfg.hard_stop_threshold:
            raise InvalidDrawdownControlError(
                f"soft_stop({cfg.soft_stop_threshold}) must < hard_stop({cfg.hard_stop_threshold})"
            )
        if not (0 < cfg.var_yellow < cfg.var_orange < cfg.var_red):
            raise InvalidDrawdownControlError("var thresholds must be 0<yellow<orange<red")
        if cfg.cvar_black <= 0:
            raise InvalidDrawdownControlError("cvar_black must be positive")
        if not (0 < cfg.recovery_trigger <= 1.0):
            raise InvalidDrawdownControlError("recovery_trigger must be in (0,1]")
        if not (0 < cfg.recovery_step <= 1.0):
            raise InvalidDrawdownControlError("recovery_step must be in (0,1]")

        self._soft_stop = cfg.soft_stop_threshold
        self._hard_stop = cfg.hard_stop_threshold
        self._var_yellow = cfg.var_yellow
        self._var_orange = cfg.var_orange
        self._var_red = cfg.var_red
        self._cvar_black = cfg.cvar_black
        self._recovery_step = cfg.recovery_step
        self._recovery_trigger = cfg.recovery_trigger

    # ── 公共属性 ──

    @property
    def soft_stop_threshold(self) -> float:
        return self._soft_stop

    @property
    def hard_stop_threshold(self) -> float:
        return self._hard_stop

    # ── 主入口 ──

    def evaluate(
        self,
        drawdown_info: DrawdownInfo,
        var_cvar: VarCvarMetrics,
        black_swan: BlackSwanSignal | None = None,
        strategy_pnls: list[StrategyPnl] | None = None,
        var_breach_state: str | None = None,
    ) -> DrawdownResponse:
        """综合评估产出分级响应指令。

        Args:
            drawdown_info: 组合回撤信息
            var_cvar: VaR/CVaR 指标
            black_swan: 黑天鹅信号(可选, 缺省无黑天鹅)
            strategy_pnls: 策略级 PnL 列表(可选)
            var_breach_state: VaR breach 状态机当前状态(可选, 36号 §3.15:
                "NORMAL"/"BREACHED"/"RECOVERY" 或 VarBreachState 枚举;
                None=未接线不加折扣; BREACHED×0.8 / RECOVERY×0.9 乘性折扣
                作用于系统性风险仓位上限, 与回撤状态机正交乘性叠加)

        Returns:
            DrawdownResponse (取最严的仓位上限 + 动作列表)

        Raises:
            InvalidDrawdownControlError: 输入数据非法(含未知 var_breach_state)
        """
        self._validate(drawdown_info, var_cvar)
        black_swan = black_swan or BlackSwanSignal()
        strategy_pnls = strategy_pnls or []
        breach_state_key, breach_multiplier = self._var_breach_multiplier(var_breach_state)

        # 1. 系统性风险级别
        risk_level = self._evaluate_risk_level(var_cvar)
        # 2. 策略级止损
        strategy_stops = self._evaluate_strategy_stops(strategy_pnls)
        # 3. 黑天鹅处置
        bs_cap, bs_actions, kill_advised = self._evaluate_black_swan(black_swan)
        # 4. 回撤回补恢复
        recovery_factor = self._evaluate_recovery(drawdown_info)

        # 5. 取最严仓位上限 (36号 §3.15 E3: base_cap = 风险级 cap × breach 折扣
        #    → 与黑天鹅 cap 取 min → × 回撤恢复系数, 下限 max(0.0))
        caps = [risk_level.position_cap * breach_multiplier]
        if bs_cap >= 0:  # -1 表示外部决定, 不参与取严
            caps.append(bs_cap)
        if kill_advised:
            caps.append(0.0)
        # Hard Stop 策略 → 该策略清仓, 但不影响组合上限(组合上限由风险级别决定)
        position_cap = min(caps) * recovery_factor
        position_cap = max(0.0, min(1.0, position_cap))

        # 6. 减仓比例
        reduce_ratio = 1.0 - position_cap

        # 7. 动作列表
        actions = self._build_actions(risk_level, strategy_stops, black_swan, kill_advised, recovery_factor)
        if breach_multiplier < 1.0:
            actions.append(
                f"VaR breach 状态 {breach_state_key}: 仓位上限乘性折扣 ×{breach_multiplier:.2f} (36号 §3.15)"
            )

        return DrawdownResponse(
            risk_level=risk_level,
            position_cap=position_cap,
            reduce_ratio=reduce_ratio,
            actions=actions,
            strategy_stops=strategy_stops,
            black_swan_modes=black_swan.active_modes,
            kill_switch_advised=kill_advised,
            recovery_factor=recovery_factor,
        )

    @staticmethod
    def _var_breach_multiplier(var_breach_state: object) -> tuple[str, float]:
        """36号 §3.15 乘性折扣: NORMAL×1.0 / BREACHED×0.8 / RECOVERY×0.9。

        None=未接线(×1.0 不加折扣); 接受字符串或 VarBreachState 枚举
        (str mixin, 经 .value 归一); 未知值 fail-closed 抛错。
        """
        if var_breach_state is None:
            return "NORMAL", 1.0
        key = str(getattr(var_breach_state, "value", var_breach_state)).upper()
        if key not in _VAR_BREACH_CAP_MULTIPLIER:
            raise InvalidDrawdownControlError(
                f"未知 var_breach_state: {var_breach_state!r} (合法值: NORMAL/BREACHED/RECOVERY)"
            )
        return key, _VAR_BREACH_CAP_MULTIPLIER[key]

    # ── 内部: 系统性风险级别 ──

    def _evaluate_risk_level(self, vc: VarCvarMetrics) -> SystemicRiskLevel:
        """基于 VaR/CVaR 判定系统性风险级别。

        优先级: CVaR(黑) > VaR(红/橙/黄/绿)。
        """
        if vc.cvar_95 > self._cvar_black:
            return SystemicRiskLevel.BLACK
        if vc.var_95 > self._var_red:
            return SystemicRiskLevel.RED
        if vc.var_95 > self._var_orange:
            return SystemicRiskLevel.ORANGE
        if vc.var_95 > self._var_yellow:
            return SystemicRiskLevel.YELLOW
        return SystemicRiskLevel.GREEN

    # ── 内部: 策略级止损 ──

    def _evaluate_strategy_stops(self, strategy_pnls: list[StrategyPnl]) -> list[StrategyStopLoss]:
        """评估每个策略的止损状态。"""
        stops: list[StrategyStopLoss] = []
        for sp in strategy_pnls:
            abs_dd = abs(sp.drawdown_pct)
            if abs_dd > self._hard_stop:
                stops.append(StrategyStopLoss(sp.strategy_id, StopLossType.HARD, sp.drawdown_pct))
            elif abs_dd > self._soft_stop:
                stops.append(StrategyStopLoss(sp.strategy_id, StopLossType.SOFT, sp.drawdown_pct))
            else:
                stops.append(StrategyStopLoss(sp.strategy_id, StopLossType.NONE, sp.drawdown_pct))
        return stops

    # ── 内部: 黑天鹅处置 ──

    def _evaluate_black_swan(self, bs: BlackSwanSignal) -> tuple[float, list[str], bool]:
        """评估黑天鹅模式 → (仓位上限系数, 动作列表, 是否建议 Kill Switch)。

        Returns:
            (cap, actions, kill_advised): cap=-1 表示外部决定(不参与取严)
        """
        if not bs.has_black_swan:
            return 1.0, [], False

        actions: list[str] = []
        kill_advised = False

        # BS-007 系统性风险: 多模式同触发 → Kill Switch 建议
        if bs.is_systemic:
            kill_advised = True
            actions.append("BS-007 系统性风险: 建议 Kill Switch(P0), 委托 stop_loss 执行")
            return 0.0, actions, True

        # 单模式: 取最严 cap
        caps: list[float] = []
        for mode in bs.active_modes:
            cap = _BLACK_SWAN_CAP[mode]
            if cap >= 0:
                caps.append(cap)
            actions.append(f"{mode.value}: {self._black_swan_action(mode)}")

        final_cap = min(caps) if caps else 1.0
        return final_cap, actions, kill_advised

    @staticmethod
    def _black_swan_action(mode: BlackSwanMode) -> str:
        """黑天鹅模式的处置动作描述。"""
        return {
            BlackSwanMode.BS001_LIQUIDITY: "参与率收紧至 5% + 暂停做 T",
            BlackSwanMode.BS002_CORRELATION: "集中度强制分散 + 降总仓位",
            BlackSwanMode.BS003_VOLATILITY: "仓位减半 + 暂停新开仓",
            BlackSwanMode.BS004_MARGIN: "降杠杆敞口 + 暂停融资标的",
            BlackSwanMode.BS005_CONTAGION: "降仓位至市场状态对应档位",
            BlackSwanMode.BS006_POLICY: "暂停受影响标的交易 + 评估",
            BlackSwanMode.BS007_SYSTEMIC: "Kill Switch(P0)",
        }[mode]

    # ── 内部: 回撤回补恢复 ──

    def _evaluate_recovery(self, di: DrawdownInfo) -> float:
        """回撤回补恢复系数。

        回补 >= recovery_trigger → 开始恢复, 每步 recovery_step。
        未触发恢复 → 1.0(不受恢复约束, 由风险级别决定)。
        已开始恢复 → 0.25/0.50/0.75/1.0 逐步恢复。

        注意: 恢复系数是乘性的, 与风险级别 cap 相乘。
        无回撤(drawdown_pct==0)时 recovery_factor=1.0。
        """
        if di.drawdown_pct >= 0:
            return 1.0  # 无回撤, 不受恢复约束
        if di.recovered_pct < self._recovery_trigger:
            return 1.0  # 未触发恢复阈值, 由风险级别主导(不额外折扣)
        # 已触发恢复: 每步 recovery_step
        steps = int(di.recovered_pct / self._recovery_step)
        return min(1.0, steps * self._recovery_step)

    # ── 内部: 动作列表 ──

    def _build_actions(
        self,
        risk_level: SystemicRiskLevel,
        strategy_stops: list[StrategyStopLoss],
        black_swan: BlackSwanSignal,
        kill_advised: bool,
        recovery_factor: float,
    ) -> list[str]:
        actions: list[str] = []
        # 系统性风险
        actions.append(f"系统性风险级别: {risk_level.value} (仓位上限 {risk_level.position_cap:.0%})")
        if risk_level == SystemicRiskLevel.YELLOW:
            actions.append("黄级: 新开仓减半")
        elif risk_level == SystemicRiskLevel.ORANGE:
            actions.append("橙级: 禁止新开仓 + 减仓(仓位上限 50%)")
        elif risk_level == SystemicRiskLevel.RED:
            actions.append("红级: 减仓 50% + 只平不开")
        elif risk_level == SystemicRiskLevel.BLACK:
            actions.append("黑级: 全部清仓")
        # 策略止损
        for ss in strategy_stops:
            if ss.stop_type == StopLossType.SOFT:
                actions.append(f"Soft Stop: 策略 {ss.strategy_id} 回撤 {abs(ss.drawdown_pct):.1%} 砍仓")
            elif ss.stop_type == StopLossType.HARD:
                actions.append(f"Hard Stop: 策略 {ss.strategy_id} 回撤 {abs(ss.drawdown_pct):.1%} 关闭策略")
        # 黑天鹅
        if black_swan.has_black_swan:
            _, bs_actions, _ = self._evaluate_black_swan(black_swan)
            actions.extend(bs_actions)
        # Kill Switch
        if kill_advised:
            actions.append("⚠ 建议 Kill Switch(P0), 委托 D-RISK stop_loss 执行")
        # 恢复
        if recovery_factor < 1.0:
            actions.append(f"回撤回补恢复中: 恢复系数 {recovery_factor:.0%}")
        return actions

    # ── 内部: 校验 ──

    @staticmethod
    def _validate(di: DrawdownInfo, vc: VarCvarMetrics) -> None:
        if di.drawdown_pct > 0:
            raise InvalidDrawdownControlError(f"drawdown_pct must be <= 0, got {di.drawdown_pct}")
        if di.drawdown_pct < -1.0:
            raise InvalidDrawdownControlError(f"drawdown_pct must be >= -1.0, got {di.drawdown_pct}")
        if vc.var_95 < 0:
            raise InvalidDrawdownControlError(f"var_95 must be >= 0, got {vc.var_95}")
        if vc.cvar_95 < vc.var_95:
            raise InvalidDrawdownControlError(f"cvar_95({vc.cvar_95}) must be >= var_95({vc.var_95})")
        if di.peak_nav <= 0:
            raise InvalidDrawdownControlError(f"peak_nav must be > 0, got {di.peak_nav}")
