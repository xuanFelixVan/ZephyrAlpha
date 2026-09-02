# [BLUEPRINT] MOD-RK-34 | docs/03_modules/_domain_risk/systemic_risk_alert_state_machine/blueprint.md
# [MODULE] zephyr.risk.core.systemic_risk_alert_state_machine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 编排层(减仓/禁开/清仓执行); MOD-INF-016 trading_kill_switch(BLACK 触发标记消费); 风险仪表盘
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 五级取最严(BLACK>RED>ORANGE>YELLOW>GREEN); 触发理由全量记录不短路; 指令=纯数据(scale/reduce/close_only/liquidate/trigger)不执行; 迁移历史只追加; 同级重复评估不重复记录; 阈值边界左闭右开(VaR档)/阈值即触发(CVaR黑/单日亏); 非法输入Fail-Closed
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidSystemicAlertInputError
# [TESTS] tests/risk/core/test_systemic_risk_alert_state_machine.py
# [A_module] module_id=MOD-RK-34 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Systemic Risk Alert State Machine — 系统性风险分级预警 5 级状态机 (MOD-RK-34, CAND-RSK-037)

模块37 落码：把组合侧 VaR95/CVaR、单日亏损、连续两日亏损统一映射为
绿/黄/橙/红/黑 5 级（Basel III 逆周期缓冲思想的分级预警框架），逐级产出
减仓/禁开/清仓指令与 kill switch 触发标记：

  | 级 | 触发（任一，默认阈值） | 指令 |
  |---|---|---|
  | 绿 GREEN | 其余皆不命中 | scale=1.0 正常 |
  | 黄 YELLOW | VaR95∈[2%,4%) 或 连续 2 日亏均≤−1% | 新开仓减半 scale=0.5 |
  | 橙 ORANGE | VaR95∈[4%,6%) 或 单日亏≤−2% | 禁新开仓 + 减仓 30% |
  | 红 RED | VaR95≥6% 或 单日亏≤−4% | 全线减仓 50% + 只平不开 |
  | 黑 BLACK | CVaR≥10% 或 流动性危机 | 全部清仓 + kill switch 触发标记 |

与既有件分工：MOD-RK-10 为市场侧 5 信号计数→3 级；本模块为组合侧阈值分级→5 级，
补齐"绿黄橙红黑+连续亏损触发"缺口。本模块纯计算输出指令（RiskDirective），
减仓/禁开/清仓与 MOD-INF-016 trading_kill_switch 的执行接线归编排层（三维解耦）。

纪律：纯函数式评估 + 只追加迁移历史；输入（VaR/CVaR 由 MOD-RK-05 口径计算、
盈亏由调用方注入）不越域自取。阈值为 C 类可调参数（SystemicRiskAlertConfig）。
依据: blueprint.md（MOD-RK-34）§3 核心规则（候选登记真源默认阈值）
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 组合风险标量
#   fields: var95_pct(VaR95/NAV,正=损失) + cvar_pct(CVaR/NAV) + daily_pnl_pct + prev_day_pnl_pct + liquidity_crisis
#   code: assess() 参数
# - id: I2
#   name: 配置 SystemicRiskAlertConfig
#   fields: VaR三档边界(2%/4%/6%) + CVaR黑档(10%) + 单日亏橙/红(−2%/−4%) + 连续亏阈(−1%) + 指令参数(0.5/0.3/0.5/1.0)
#   code: SystemicRiskAlertConfig
# 层: 算法
# - id: A1
#   name_zh: ① 五路阈值检测不短路
#   name_en: _collect_hits
#   intro: CVaR黑/流动性黑 + VaR档 + 单日亏橙/红 + 连续2日亏黄, 命中全量记录理由
# - id: A2
#   name_zh: ② 取最严级定档
#   name_en: _severity_max
#   intro: BLACK>RED>ORANGE>YELLOW>GREEN 取最高命中级
# - id: A3
#   name_zh: ③ 级别→指令映射
#   name_en: _directive_for
#   intro: scale/reduce_pct/close_only/liquidate_all/trigger_kill_switch 纯数据输出
# - id: A4
#   name_zh: ④ 迁移历史只追加
#   name_en: _record_transition
#   intro: 级别变化才追加(seq,level,reasons), 同级不重复
# 层: 输出
# - id: O1
#   name: SystemicRiskAssessment
#   fields: level/directive(RiskDirective)/reasons tuple
# 边:
# I1 --> A1
# I2 --> A1
# I2 --> A3
# A1 --> A2
# A2 --> A3
# A2 --> A4
# A3 --> O1
# A4 --> O1
# [/ALGO_FLOW]
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidSystemicAlertInputError",
    "RiskDirective",
    "RiskLevel",
    "SystemicRiskAlertConfig",
    "SystemicRiskAlertStateMachine",
    "SystemicRiskAssessment",
]


class InvalidSystemicAlertInputError(ZephyrBaseError):
    """系统性风险分级预警输入/配置非法（Fail-Closed）。"""


class RiskLevel(str, Enum):
    """系统性风险 5 级（severity 升序）。"""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"
    BLACK = "BLACK"


_SEVERITY: Final[dict[RiskLevel, int]] = {
    RiskLevel.GREEN: 0,
    RiskLevel.YELLOW: 1,
    RiskLevel.ORANGE: 2,
    RiskLevel.RED: 3,
    RiskLevel.BLACK: 4,
}


@dataclass(frozen=True)
class SystemicRiskAlertConfig:
    """5 级阈值与指令参数（C 类可调；默认值=候选登记真源）。"""

    var_yellow_min: float = 0.02  # VaR95/NAV 黄档下界（左闭右开）
    var_orange_min: float = 0.04
    var_red_min: float = 0.06
    cvar_black_min: float = 0.10  # CVaR/NAV 黑档（≥触发）
    daily_loss_orange: float = -0.02  # 单日亏 ≤ 阈 → 橙
    daily_loss_red: float = -0.04  # 单日亏 ≤ 阈 → 红
    consecutive_loss_daily: float = -0.01  # 连续 2 日均 ≤ 阈 → 黄
    yellow_new_position_scale: float = 0.5
    orange_reduce_pct: float = 0.30
    red_reduce_pct: float = 0.50

    def __post_init__(self) -> None:
        bounds = (self.var_yellow_min, self.var_orange_min, self.var_red_min, self.cvar_black_min)
        if any(not math.isfinite(v) or v <= 0 for v in bounds):
            raise InvalidSystemicAlertInputError(f"VaR/CVaR 阈值必须为正有限值: {bounds}")
        if not (self.var_yellow_min < self.var_orange_min < self.var_red_min):
            raise InvalidSystemicAlertInputError(
                f"VaR 档边界必须严格递增: {self.var_yellow_min}/{self.var_orange_min}/{self.var_red_min}"
            )
        if self.cvar_black_min <= self.var_red_min:
            raise InvalidSystemicAlertInputError(
                f"CVaR 黑档阈 {self.cvar_black_min} 须高于 VaR 红档阈 {self.var_red_min}（防档位语义重叠）"
            )
        if not (self.daily_loss_red < self.daily_loss_orange < 0):
            raise InvalidSystemicAlertInputError(
                f"单日亏阈值须满足 red<orange<0: {self.daily_loss_red}/{self.daily_loss_orange}"
            )
        if not (self.consecutive_loss_daily < 0):
            raise InvalidSystemicAlertInputError(f"连续亏损日阈必须为负: {self.consecutive_loss_daily}")
        for name, v in (
            ("yellow_new_position_scale", self.yellow_new_position_scale),
            ("orange_reduce_pct", self.orange_reduce_pct),
            ("red_reduce_pct", self.red_reduce_pct),
        ):
            if not (0.0 < v < 1.0):
                raise InvalidSystemicAlertInputError(f"{name} 须 ∈(0,1): {v}")


@dataclass(frozen=True)
class RiskDirective:
    """分级联动指令（纯数据，执行归编排层）。"""

    new_position_scale: float  # 新开仓规模缩放（1.0 正常 / 0.5 减半 / 0.0 禁开）
    reduce_pct: float  # 存量减仓比例（0~1）
    close_only: bool  # 只平不开
    liquidate_all: bool  # 全部清仓
    trigger_kill_switch: bool  # kill switch 触发标记（MOD-INF-016 消费）


@dataclass(frozen=True)
class SystemicRiskAssessment:
    """一次分级评估结果。"""

    level: RiskLevel
    directive: RiskDirective
    reasons: tuple[str, ...]


def _require_finite(name: str, value: float) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise InvalidSystemicAlertInputError(f"{name} 必须为有限值: {value}")
    return v


class SystemicRiskAlertStateMachine:
    """系统性风险 5 级状态机（评估纯函数 + 迁移历史只追加）。"""

    def __init__(self, config: SystemicRiskAlertConfig | None = None) -> None:
        self._config = config or SystemicRiskAlertConfig()
        self._current: RiskLevel = RiskLevel.GREEN
        self._history: list[tuple[int, RiskLevel, tuple[str, ...]]] = []
        self._seq = 0

    @property
    def config(self) -> SystemicRiskAlertConfig:
        return self._config

    @property
    def current_level(self) -> RiskLevel:
        return self._current

    def transition_history(self) -> list[tuple[int, RiskLevel, tuple[str, ...]]]:
        """迁移历史 [(seq, level, reasons)]（只追加副本）。"""
        return list(self._history)

    def assess(
        self,
        *,
        var95_pct: float,
        cvar_pct: float,
        daily_pnl_pct: float,
        prev_day_pnl_pct: float,
        liquidity_crisis: bool = False,
    ) -> SystemicRiskAssessment:
        """评估当前组合风险级别并产出联动指令。

        Args:
            var95_pct: VaR95 占 NAV 比例（正=损失幅度，MOD-RK-05 口径）
            cvar_pct: CVaR/ES 占 NAV 比例（同口径）
            daily_pnl_pct: 当日盈亏比例（负=亏）
            prev_day_pnl_pct: 前一日盈亏比例（连续 2 日亏判定）
            liquidity_crisis: 流动性危机标记（上游 MOD-RK-08/21 口径）

        Returns:
            SystemicRiskAssessment（取最严级 + 指令 + 全量触发理由）

        Raises:
            InvalidSystemicAlertInputError: 输入非有限值（Fail-Closed）
        """
        var95 = _require_finite("var95_pct", var95_pct)
        cvar = _require_finite("cvar_pct", cvar_pct)
        daily = _require_finite("daily_pnl_pct", daily_pnl_pct)
        prev = _require_finite("prev_day_pnl_pct", prev_day_pnl_pct)
        cfg = self._config

        # ① 五路检测不短路（理由全量）
        hits: list[tuple[RiskLevel, str]] = []
        if liquidity_crisis:
            hits.append((RiskLevel.BLACK, "流动性危机标记=True → 黑档（全部清仓+kill switch）"))
        if cvar >= cfg.cvar_black_min:
            hits.append((RiskLevel.BLACK, f"CVaR {cvar:.2%} ≥ 黑档阈 {cfg.cvar_black_min:.2%}"))
        if var95 >= cfg.var_red_min:
            hits.append((RiskLevel.RED, f"VaR95 {var95:.2%} ≥ 红档阈 {cfg.var_red_min:.2%}"))
        elif var95 >= cfg.var_orange_min:
            hits.append(
                (RiskLevel.ORANGE, f"VaR95 {var95:.2%} ∈ 橙档 [{cfg.var_orange_min:.2%},{cfg.var_red_min:.2%})")
            )
        elif var95 >= cfg.var_yellow_min:
            hits.append(
                (RiskLevel.YELLOW, f"VaR95 {var95:.2%} ∈ 黄档 [{cfg.var_yellow_min:.2%},{cfg.var_orange_min:.2%})")
            )
        if daily <= cfg.daily_loss_red:
            hits.append((RiskLevel.RED, f"单日亏 {daily:.2%} ≤ 红档阈 {cfg.daily_loss_red:.2%}"))
        elif daily <= cfg.daily_loss_orange:
            hits.append((RiskLevel.ORANGE, f"单日亏 {daily:.2%} ≤ 橙档阈 {cfg.daily_loss_orange:.2%}"))
        if daily <= cfg.consecutive_loss_daily and prev <= cfg.consecutive_loss_daily:
            hits.append(
                (
                    RiskLevel.YELLOW,
                    f"连续 2 日亏（当日 {daily:.2%} / 前日 {prev:.2%} 均 ≤ {cfg.consecutive_loss_daily:.2%}）",
                )
            )

        # ② 取最严
        if hits:
            level = max((lv for lv, _ in hits), key=lambda lv: _SEVERITY[lv])
            reasons = tuple(reason for _, reason in hits)
        else:
            level = RiskLevel.GREEN
            reasons = ("各阈值均未命中 → 绿档正常",)

        # ④ 迁移历史（同级不重复）
        if level is not self._current:
            self._seq += 1
            self._history.append((self._seq, level, reasons))
            self._current = level

        return SystemicRiskAssessment(level=level, directive=self._directive_for(level), reasons=reasons)

    # ── 内部 ─────────────────────────────────────────────────────────

    def _directive_for(self, level: RiskLevel) -> RiskDirective:
        cfg = self._config
        if level is RiskLevel.BLACK:
            return RiskDirective(
                new_position_scale=0.0,
                reduce_pct=1.0,
                close_only=True,
                liquidate_all=True,
                trigger_kill_switch=True,
            )
        if level is RiskLevel.RED:
            return RiskDirective(
                new_position_scale=0.0,
                reduce_pct=cfg.red_reduce_pct,
                close_only=True,
                liquidate_all=False,
                trigger_kill_switch=False,
            )
        if level is RiskLevel.ORANGE:
            return RiskDirective(
                new_position_scale=0.0,
                reduce_pct=cfg.orange_reduce_pct,
                close_only=False,
                liquidate_all=False,
                trigger_kill_switch=False,
            )
        if level is RiskLevel.YELLOW:
            return RiskDirective(
                new_position_scale=cfg.yellow_new_position_scale,
                reduce_pct=0.0,
                close_only=False,
                liquidate_all=False,
                trigger_kill_switch=False,
            )
        return RiskDirective(
            new_position_scale=1.0,
            reduce_pct=0.0,
            close_only=False,
            liquidate_all=False,
            trigger_kill_switch=False,
        )
