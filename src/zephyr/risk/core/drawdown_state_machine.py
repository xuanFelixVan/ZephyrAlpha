# [BLUEPRINT] 35_drawdown_protocol_impl | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/35_drawdown_protocol_impl.md | §3.11/§3.14/§3.20/§6.6
# [MODULE] zephyr.risk.core.drawdown_state_machine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.state_store
# [CONSUMERS] zephyr.risk.core.drawdown_session_persistence; RiskOrchestrator(§6.5 接线位)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 升级单调取最严(多源触发直接跳到最高态); 降级不可跳级(WARN→NORMAL/DANGER→WARN/CRISIS→DANGER逐级); 降级三重守卫(半阈值+min_hold+VaR交叉验证); RECOVERY阶梯不可跳过(0→1→2→NORMAL且须毕业准则); KILL仅人工复位可出(无自动路径); 状态外部化(JsonStateStore原子写,损坏抛StateCorruptError不静默兜底); peak语义不属本模块(capital_curve_manager管辖)
# [MODIFY-GUARD] tests/risk/test_drawdown_state_machine.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidDrawdownStateError(ZA-RK-0060); RefuseResetError(ZA-RK-0061)
# [TESTS] tests/risk/test_drawdown_state_machine.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: evaluate日输入(trade_date+drawdown_pct+var_95/cvar_95+recovered_pct+black_swan_systemic+strategy_pnls)
# I2: JsonStateStore(状态/复位历史外部化, namespace=drawdown_state_machine/drawdown_reset_history)
# I3: DrawdownStateMachineConfig(升级阈值5/10/15/25%+VaR2/4/6%+CVaR10%; 半阈值比0.5; min_hold5/10/20; 持续窗3/3/5; 毕业准则3盈利日/0.3R/80%/1.2R; 复位守卫3次/20日+冷却3日+永久锁5次)
# F1: 升级判定(多源OR取最严: dd/ var/cvar/BS-007→目标态, severity高于当前即直接升级)
# F2: hysteresis降级判定(§3.20: 半阈值持续N日+min_hold门控+VaR回落目标态触发阈值下, 逐级降一档)
# F3: RECOVERY阶梯机(0→1→2→NORMAL: recovered_pct≥0.5/0.75/1.0+毕业准则+阶梯min_hold5日; dd>15%回退阶梯, 阶梯0再退→KILL; dd>10%且step>0回退; dd>5%冻结5日)
# A1: request_manual_reset(KILL→RECOVERY唯一出口: 三项确认+复位窗口/冷却/永久锁三重守卫, §3.14)
# A2: 持久化(每次转换/日推进后原子写快照; load_or_none启动恢复, None=冷启动默认NORMAL)
# O1: StateTransition(from/to/reason/trade_date)或None + position_cap/recovery_factor/defensive_only查询面
# [/ALGO_FLOW]
"""D_RISK — 回撤持久化状态机（35 号 memo §6.6 施工，§3.11 状态机 + §3.20 hysteresis 落地）。

痛点（§3.11 代码差距）：
  1. DrawdownController 无状态持久化——级别每次重算，无"上一态"记忆，重启即丢。
  2. 无转换守卫——RECOVERY 可跳阶梯直接回 NORMAL，存在"刚 CRISIS 立即满仓"风险。
  3. 降级用与升级相同阈值——临界态 thrashing（触发→恢复→再触发）。

本模块落地（§3.11 转换规则表 + §3.20 恢复算法逐项对齐）：
  - 6 态：NORMAL/WARN/DANGER/CRISIS/KILL/RECOVERY；升级单调取最严（多源 OR，
    nexusfi "the most severe state wins. Always."），可直接跳高态；
    降级不可跳级，逐级且须经 hysteresis 三重守卫（半阈值 + min_hold + VaR 交叉验证）。
  - 半阈值 = 触发阈值 × 0.5（WARN 2.5% / DANGER 5% / CRISIS 7.5%），
    持续窗 N=3/3/5 交易日，min_hold=5/10/20 交易日（Triple Penance 2-3x 下限）。
  - RECOVERY 阶梯 0→1→2→NORMAL：recovered_pct ≥ 50%/75%/100% + 毕业准则
    （连续 3 盈利日 + 近 10 笔期望 ≥ 0.3R + 合规率 ≥ 80% + 单笔最大亏损 ≤ 1.2R）
    + 每阶梯 min_hold 5 日；回撤加深分级保护（>15% 回退阶梯/阶梯耗尽回 KILL、
    >10% 且 step>0 回退、>5% 冻结 5 日）。
  - KILL 仅人工复位可出（§3.7 不可覆盖）：三项确认（持仓清零/挂单已撤/锁新开仓）
    + 复位守卫（20 日窗最多 3 次 / 冷却 3 交易日 / 累计 5 次永久锁定）。
  - 状态外部化：JsonStateStore 原子写；损坏抛 StateCorruptError 由消费方
    fail-closed（本层绝不静默兜底，对齐 state_store 契约）。

计时约定：调用方每交易日盘前/盘后各至多调用一次 evaluate(trade_date=...)；
trade_date 前进才计一个交易日（同日重复调用幂等，不重复计日/不重复入史）。
SSoT: 35_drawdown_protocol_impl §3.11/§3.14/§3.20/§6.6
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Final, Mapping, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.state_store import JsonStateStore

__all__: Final = [
    "DrawdownState",
    "DrawdownStateMachineConfig",
    "DrawdownStateMachine",
    "DrawdownStateSnapshot",
    "StateTransition",
    "ResetConfirmation",
    "InvalidDrawdownStateError",
    "RefuseResetError",
    "DRAWDOWN_STATE_NAMESPACE",
    "RESET_HISTORY_NAMESPACE",
]

_logger = logging.getLogger(__name__)

#: 状态机快照命名空间（单条记录=最新真源）
DRAWDOWN_STATE_NAMESPACE: Final = "drawdown_state_machine"
#: 复位历史命名空间（§3.14 窗口/冷却/永久锁守卫数据源）
RESET_HISTORY_NAMESPACE: Final = "drawdown_reset_history"

#: dd_history 滚动窗口（hysteresis 持续窗最大 5 日，留 30 日余量）
_DD_HISTORY_WINDOW: Final = 30


class InvalidDrawdownStateError(ZephyrBaseError):
    """状态机输入非法（日期倒退/阈值非法/阶梯越界等）。"""

    error_code = "ZA-RK-0060"


class RefuseResetError(ZephyrBaseError):
    """人工复位被拒绝（确认项缺失/复位守卫触发/永久锁定）。"""

    error_code = "ZA-RK-0061"


class DrawdownState(str, Enum):
    """回撤协议 6 态（§3.11）。severity 越大越严重（取最严比较用）。"""

    NORMAL = "NORMAL"
    WARN = "WARN"
    DANGER = "DANGER"
    CRISIS = "CRISIS"
    KILL = "KILL"
    RECOVERY = "RECOVERY"

    @property
    def severity(self) -> int:
        """升级取最严用序数；RECOVERY 与 KILL 不参与自动升级比较。"""
        return _SEVERITY_ORDER[self]


_SEVERITY_ORDER: Final[dict[DrawdownState, int]] = {
    DrawdownState.NORMAL: 0,
    DrawdownState.WARN: 1,
    DrawdownState.DANGER: 2,
    DrawdownState.CRISIS: 3,
    DrawdownState.KILL: 4,
    DrawdownState.RECOVERY: 5,
}

#: 降级路径（不可跳级，§3.11 转换守卫）
_DEESCALATION_PATH: Final[dict[DrawdownState, DrawdownState]] = {
    DrawdownState.WARN: DrawdownState.NORMAL,
    DrawdownState.DANGER: DrawdownState.WARN,
    DrawdownState.CRISIS: DrawdownState.DANGER,
}


@dataclass(frozen=True)
class DrawdownStateMachineConfig:
    """回撤状态机配置（C 类可调参数，默认值真源=35 号 memo §3.11/§3.20/§3.14）。

    Attributes:
        warn_dd/danger_dd/crisis_dd/kill_dd: 升级回撤阈值（正数绝对值）
        warn_var/danger_var/crisis_var: 升级 VaR_95 阈值
        kill_cvar: 升级 CVaR_95 阈值（KILL 源之一）
        hysteresis_ratio: 恢复半阈值比例（默认 0.5，§3.20）
        sustained_warn/danger/crisis: 降级持续确认窗（交易日，3/3/5）
        min_hold_warn/danger/crisis/recovery_step: 最短持有日数（5/10/20/5）
        recovery_step_recovered: 阶梯 0→1→2→NORMAL 的 recovered_pct 门槛
        graduation_min_trades / min_profit_streak / min_expectancy_r /
            min_rule_compliance / max_single_loss_r: 毕业准则参数（§3.20 表）
        recovery_freeze_days: 恢复期 dd>5% 冻结天数（§3.14）
        reset_window_days / max_resets_per_window / reset_cooldown_days /
            permanent_lock_threshold: 复位守卫（§3.14）
    """

    warn_dd: float = 0.05
    danger_dd: float = 0.10
    crisis_dd: float = 0.15
    kill_dd: float = 0.25
    warn_var: float = 0.02
    danger_var: float = 0.04
    crisis_var: float = 0.06
    kill_cvar: float = 0.10
    hysteresis_ratio: float = 0.5
    sustained_warn: int = 3
    sustained_danger: int = 3
    sustained_crisis: int = 5
    min_hold_warn: int = 5
    min_hold_danger: int = 10
    min_hold_crisis: int = 20
    min_hold_recovery_step: int = 5
    recovery_step_recovered: tuple[float, float, float] = (0.50, 0.75, 1.0 - 1e-6)
    graduation_min_trades: int = 3
    graduation_min_profit_streak: int = 3
    graduation_min_expectancy_r: float = 0.3
    graduation_min_rule_compliance: float = 0.80
    graduation_max_single_loss_r: float = 1.2
    graduation_window: int = 10
    recovery_freeze_days: int = 5
    reset_window_days: int = 20
    max_resets_per_window: int = 3
    reset_cooldown_days: int = 3
    permanent_lock_threshold: int = 5

    def __post_init__(self) -> None:
        thresholds = (self.warn_dd, self.danger_dd, self.crisis_dd, self.kill_dd)
        if not all(0 < t < 1 for t in thresholds):
            raise InvalidDrawdownStateError(f"升级回撤阈值须在 (0,1): {thresholds}")
        if not (self.warn_dd < self.danger_dd < self.crisis_dd < self.kill_dd):
            raise InvalidDrawdownStateError("回撤阈值须递增 warn<danger<crisis<kill")
        vars_ = (self.warn_var, self.danger_var, self.crisis_var, self.kill_cvar)
        if not all(0 < v < 1 for v in vars_):
            raise InvalidDrawdownStateError(f"VaR/CVaR 阈值须在 (0,1): {vars_}")
        if not (self.warn_var < self.danger_var < self.crisis_var):
            raise InvalidDrawdownStateError("VaR 阈值须递增 warn<danger<crisis")
        if not 0 < self.hysteresis_ratio < 1:
            raise InvalidDrawdownStateError("hysteresis_ratio 须在 (0,1)")
        for name in (
            "sustained_warn", "sustained_danger", "sustained_crisis",
            "min_hold_warn", "min_hold_danger", "min_hold_crisis",
            "min_hold_recovery_step", "recovery_freeze_days",
            "graduation_min_trades", "graduation_min_profit_streak",
            "graduation_window", "reset_window_days", "max_resets_per_window",
            "reset_cooldown_days", "permanent_lock_threshold",
        ):
            if getattr(self, name) < 1:
                raise InvalidDrawdownStateError(f"{name} 须 >= 1")
        rec = self.recovery_step_recovered
        if len(rec) != 3 or not (0 < rec[0] < rec[1] < rec[2] <= 1.0):
            raise InvalidDrawdownStateError("recovery_step_recovered 须为递增三元组且 ≤1")


@dataclass(frozen=True)
class StateTransition:
    """一次状态转换记录（含阶梯内迁移）。"""

    from_state: DrawdownState
    to_state: DrawdownState
    reason: str
    trade_date: str  # ISO 日期
    from_step: int = 0
    to_step: int = 0


@dataclass(frozen=True)
class DrawdownStateSnapshot:
    """持久化快照（§3.18 阶段 3 保存对象）。"""

    current: DrawdownState
    recovery_step: int
    days_in_state: int
    dd_history: tuple[float, ...]
    freeze_days_remaining: int
    last_transition: StateTransition | None
    as_of_date: str  # 最近一次 evaluate 的 trade_date（ISO）


@dataclass(frozen=True)
class ResetConfirmation:
    """人工复位确认（§3.14 阶段 0 三项确认 + 审计字段）。"""

    confirmed_by: str
    override_reason: str
    holdings_verified_zero: bool = False
    orders_cancelled_verified: bool = False
    new_open_locked_verified: bool = False


def _trade_field(trade: Any, name: str) -> Any:
    """毕业准则交易记录字段读取（duck-typing：Mapping 或属性对象）。"""
    if isinstance(trade, Mapping):
        return trade.get(name)
    return getattr(trade, name, None)


class DrawdownStateMachine:
    """回撤持久化状态机——§3.11 转换守卫 + §3.20 hysteresis + §3.14 复位守卫。

    用法:
        sm = DrawdownStateMachine(store)              # store=None 则纯内存（测试）
        sm.load_or_none()                              # 启动恢复（None=冷启动 NORMAL）
        t = sm.evaluate(trade_date=d, drawdown_pct=-0.06, var_95=0.03)
        if sm.current is DrawdownState.KILL: ...       # 锁新开仓
        sm.request_manual_reset(confirmation, trade_date=d2)   # KILL→RECOVERY 唯一出口

    计时约定：每交易日至多一次日推进（trade_date 前进计 1 个交易日）；
    同日重复 evaluate 幂等（更新当日 dd_history 末位，不重复计日）。
    """

    def __init__(
        self,
        state_store: JsonStateStore | None = None,
        config: DrawdownStateMachineConfig | None = None,
        *,
        state_namespace: str = DRAWDOWN_STATE_NAMESPACE,
        reset_namespace: str = RESET_HISTORY_NAMESPACE,
    ) -> None:
        self._store = state_store
        self._config = config or DrawdownStateMachineConfig()
        self._state_ns = state_namespace
        self._reset_ns = reset_namespace
        self._current = DrawdownState.NORMAL
        self._recovery_step = 0
        self._days_in_state = 0
        self._dd_history: list[float] = []
        self._freeze_days_remaining = 0
        self._last_transition: StateTransition | None = None
        self._last_eval_date: date | None = None

    # ── 只读查询面 ──

    @property
    def current(self) -> DrawdownState:
        return self._current

    @property
    def recovery_step(self) -> int:
        return self._recovery_step

    @property
    def days_in_state(self) -> int:
        return self._days_in_state

    @property
    def last_transition(self) -> StateTransition | None:
        return self._last_transition

    @property
    def kill_switch_closed(self) -> bool:
        return self._current is DrawdownState.KILL

    @property
    def position_cap(self) -> float:
        """仓位硬上限（§3.11/§3.20 恢复动作表）。"""
        s = self._current
        if s is DrawdownState.NORMAL:
            return 1.0
        if s is DrawdownState.WARN:
            return 0.8
        if s is DrawdownState.DANGER:
            return 0.5
        if s is DrawdownState.CRISIS:
            return 0.3
        if s is DrawdownState.KILL:
            return 0.0
        # RECOVERY 阶梯 25%/50%/75%
        return 0.25 * (self._recovery_step + 1)

    @property
    def recovery_factor(self) -> float:
        """恢复节流系数（§3.4；非 RECOVERY 态恒 1.0，KILL 恒 0.0）。"""
        if self._current is DrawdownState.KILL:
            return 0.0
        if self._current is DrawdownState.RECOVERY:
            return 0.25 * (self._recovery_step + 1)
        return 1.0

    @property
    def defensive_only(self) -> bool:
        """CRISIS/KILL 禁止新开仓（对齐 capital_curve_manager EMERGENCY 语义）。"""
        return self._current in (DrawdownState.CRISIS, DrawdownState.KILL)

    # ── 主入口：日度评估 ──

    def evaluate(
        self,
        *,
        trade_date: date,
        drawdown_pct: float,
        var_95: float | None = None,
        cvar_95: float | None = None,
        recovered_pct: float = 0.0,
        black_swan_systemic: bool = False,
        strategy_pnls: Sequence[Any] | None = None,
    ) -> StateTransition | None:
        """日度评估：日推进 → 升级（取最严）/ RECOVERY 机 / hysteresis 降级。

        Args:
            trade_date: 交易日（前进才计日；同日幂等；倒退抛错）
            drawdown_pct: 当前回撤（≤0 或正数绝对值均可，内部取 abs）
            var_95/cvar_95: VaR/CVaR 交叉验证输入（None=跳过该维度）
            recovered_pct: 回撤回补比例（RECOVERY 阶梯门槛，0~1）
            black_swan_systemic: BS-007 系统性黑天鹅（→KILL 触发源）
            strategy_pnls: 毕业准则交易序列（pnl/r_multiple/rule_followed）

        Returns:
            StateTransition（本日发生转换）或 None（保持当前态）
        """
        self._validate_eval_inputs(trade_date, var_95, cvar_95, recovered_pct)
        is_new_day = self._advance_day(trade_date, abs(drawdown_pct))
        # 冻结计时：新交易日先扣减——本日冻结中（冻结期内禁止阶梯晋升）
        frozen_today = self._freeze_days_remaining > 0
        if is_new_day and frozen_today:
            self._freeze_days_remaining -= 1

        transition: StateTransition | None = None
        if self._current is DrawdownState.KILL:
            pass  # KILL 无自动出口（§3.7；仅 request_manual_reset）
        elif self._current is DrawdownState.RECOVERY:
            transition = self._evaluate_recovery_state(
                trade_date, abs(drawdown_pct), recovered_pct, strategy_pnls,
                frozen_today=frozen_today,
            )
        else:
            target = self._escalation_target(abs(drawdown_pct), var_95, cvar_95, black_swan_systemic)
            if _SEVERITY_ORDER[target] > _SEVERITY_ORDER[self._current]:
                transition = self._transition(
                    target, f"escalate_dd_{abs(drawdown_pct):.4f}", trade_date, to_step=0
                )
            elif _SEVERITY_ORDER[target] < _SEVERITY_ORDER[self._current]:
                transition = self._try_hysteresis_deescalation(
                    trade_date, abs(drawdown_pct), var_95
                )

        if transition is not None or is_new_day:
            self.persist()
        return transition

    # ── 升级 / 降级 ──

    def _escalation_target(
        self,
        dd: float,
        var_95: float | None,
        cvar_95: float | None,
        black_swan_systemic: bool,
    ) -> DrawdownState:
        """多源 OR 取最严（§3.11 升级触发条件表）。"""
        cfg = self._config
        if black_swan_systemic or dd > cfg.kill_dd or (
            cvar_95 is not None and cvar_95 > cfg.kill_cvar
        ):
            return DrawdownState.KILL
        if dd > cfg.crisis_dd or (var_95 is not None and var_95 > cfg.crisis_var):
            return DrawdownState.CRISIS
        if dd > cfg.danger_dd or (var_95 is not None and var_95 > cfg.danger_var):
            return DrawdownState.DANGER
        if dd > cfg.warn_dd or (var_95 is not None and var_95 > cfg.warn_var):
            return DrawdownState.WARN
        return DrawdownState.NORMAL

    def _try_hysteresis_deescalation(
        self, trade_date: date, dd: float, var_95: float | None
    ) -> StateTransition | None:
        """hysteresis 三重守卫降级（§3.20）：min_hold + 半阈值持续窗 + VaR 交叉验证。"""
        cfg = self._config
        target = _DEESCALATION_PATH.get(self._current)
        if target is None:
            return None
        rules = {
            DrawdownState.WARN: (cfg.min_hold_warn, cfg.warn_dd * cfg.hysteresis_ratio,
                                 cfg.sustained_warn, cfg.warn_var),
            DrawdownState.DANGER: (cfg.min_hold_danger, cfg.danger_dd * cfg.hysteresis_ratio,
                                   cfg.sustained_danger, cfg.danger_var),
            DrawdownState.CRISIS: (cfg.min_hold_crisis, cfg.crisis_dd * cfg.hysteresis_ratio,
                                   cfg.sustained_crisis, cfg.crisis_var),
        }
        min_hold, half_threshold, window, var_threshold = rules[self._current]
        if self._days_in_state < min_hold:
            return None
        # VaR 交叉验证：须回落到目标态触发阈值以下（None=该维度不否决）
        if var_95 is not None and var_95 >= var_threshold:
            return None
        if dd >= half_threshold:
            return None
        if not self._sustained(half_threshold, window):
            return None
        return self._transition(
            target, f"hysteresis_recovery_dd_{dd:.4f}", trade_date, to_step=0
        )

    def _sustained(self, threshold: float, window: int) -> bool:
        """CUSUM 式持续确认：dd_history 最近 window 日全部 < threshold。"""
        if len(self._dd_history) < window:
            return False
        return all(h < threshold for h in self._dd_history[-window:])

    # ── RECOVERY 阶梯机 ──

    def _evaluate_recovery_state(
        self,
        trade_date: date,
        dd: float,
        recovered_pct: float,
        strategy_pnls: Sequence[Any] | None,
        *,
        frozen_today: bool,
    ) -> StateTransition | None:
        """RECOVERY 态日评估：回撤加深保护优先，阶梯晋升其次（§3.14/§3.20）。"""
        cfg = self._config
        # 1. dd > 15% → 回退一级；阶梯 0 再回退 → KILL（§3.11 分级保护）
        if dd > cfg.crisis_dd:
            if self._recovery_step > 0:
                return self._transition(
                    DrawdownState.RECOVERY, f"recovery_retreat_dd_{dd:.4f}",
                    trade_date, to_step=self._recovery_step - 1,
                )
            return self._transition(
                DrawdownState.KILL, f"recovery_exhausted_kill_dd_{dd:.4f}",
                trade_date, to_step=0,
            )
        # 2. dd > 10% 且 step>0 → 回退一级（step=0 此区间为空档，由 freeze 兜底）
        if dd > cfg.danger_dd and self._recovery_step > 0:
            return self._transition(
                DrawdownState.RECOVERY, f"recovery_retreat_dd_{dd:.4f}",
                trade_date, to_step=self._recovery_step - 1,
            )
        # 3. dd > 5% → 冻结阶梯 N 日（不退级；全阶梯生效，再次加深刷新冻结）
        if dd > cfg.warn_dd:
            self._freeze_days_remaining = cfg.recovery_freeze_days
            return None
        # 4. 冻结期禁止晋升
        if frozen_today:
            return None
        # 5. 阶梯 min_hold 门控
        if self._days_in_state < cfg.min_hold_recovery_step:
            return None
        # 6. 阶梯晋升：recovered_pct 门槛 + 毕业准则
        step = self._recovery_step
        if step > 2:
            return None
        if recovered_pct < cfg.recovery_step_recovered[step]:
            return None
        if not self.graduation_criteria_met(strategy_pnls):
            return None
        if step == 2:
            return self._transition(
                DrawdownState.NORMAL, "recovery_graduated_new_high", trade_date, to_step=0
            )
        return self._transition(
            DrawdownState.RECOVERY, f"recovery_step_up_{step}_to_{step + 1}",
            trade_date, to_step=step + 1,
        )

    def graduation_criteria_met(self, strategy_pnls: Sequence[Any] | None) -> bool:
        """毕业准则（§3.20 四准则，BloFin "Advance only when objective criteria are met"）。

        ① 连续 ≥3 个盈利日；② 近 10 笔平均期望 ≥ +0.3R；
        ③ 规则合规率 ≥ 80%；④ 单笔最大亏损 ≤ 1.2R。样本不足不毕业。
        """
        cfg = self._config
        if strategy_pnls is None or len(strategy_pnls) < cfg.graduation_min_trades:
            return False
        pnls = [_trade_field(t, "pnl") for t in strategy_pnls]
        if any(p is None for p in pnls):
            return False
        streak = cfg.graduation_min_profit_streak
        if len(pnls) < streak or not all(p > 0 for p in pnls[-streak:]):
            return False
        recent = list(strategy_pnls[-cfg.graduation_window:])
        r_multiples = [_trade_field(t, "r_multiple") for t in recent]
        if any(r is None for r in r_multiples):
            return False
        if sum(r_multiples) / len(r_multiples) < cfg.graduation_min_expectancy_r:
            return False
        if min(r_multiples) < -cfg.graduation_max_single_loss_r:
            return False
        followed = [_trade_field(t, "rule_followed") for t in recent]
        if any(f is None for f in followed):
            return False
        compliance = sum(1 for f in followed if f) / len(followed)
        return compliance >= cfg.graduation_min_rule_compliance

    # ── KILL 人工复位（唯一出口，§3.14/§3.7）──

    def request_manual_reset(
        self, confirmation: ResetConfirmation, *, trade_date: date
    ) -> StateTransition:
        """KILL → RECOVERY 人工复位（三项确认 + 复位守卫 + 留痕持久化）。

        Raises:
            RefuseResetError: 非 KILL 态 / 确认项缺失 / 守卫触发（窗口超限/
                冷却期内/永久锁定）。
        """
        if self._current is not DrawdownState.KILL:
            raise RefuseResetError(f"仅 KILL 态可人工复位，当前 {self._current.value}")
        if not confirmation.holdings_verified_zero:
            raise RefuseResetError("持仓未清零，存在 Ghost Position，拒绝复位")
        if not confirmation.orders_cancelled_verified:
            raise RefuseResetError("存在未撤挂单，复位后可能意外成交，拒绝复位")
        if not confirmation.new_open_locked_verified:
            raise RefuseResetError("锁新开仓状态未确认，拒绝复位")

        history = self._load_reset_history()
        cfg = self._config
        total_resets = int(history.get("total_resets", 0))
        if total_resets >= cfg.permanent_lock_threshold:
            _logger.critical(
                "DRAWDOWN_PERMANENT_LOCK total_resets=%d threshold=%d",
                total_resets, cfg.permanent_lock_threshold,
            )
            raise RefuseResetError(
                f"累计复位 {total_resets} 次超阈值 {cfg.permanent_lock_threshold}，永久锁定"
            )
        records: list[dict[str, str]] = list(history.get("records", []))
        if records:
            last_date = date.fromisoformat(records[-1]["date"])
            elapsed = (trade_date - last_date).days
            if elapsed < cfg.reset_cooldown_days:
                raise RefuseResetError(
                    f"距上次复位不足 {cfg.reset_cooldown_days} 日冷却期（已过 {elapsed} 日），拒绝复位"
                )
        window_start = trade_date.fromordinal(
            trade_date.toordinal() - cfg.reset_window_days
        )
        in_window = [r for r in records if date.fromisoformat(r["date"]) >= window_start]
        if len(in_window) >= cfg.max_resets_per_window:
            raise RefuseResetError(
                f"近 {cfg.reset_window_days} 日复位 {len(in_window)} 次超上限 "
                f"{cfg.max_resets_per_window}，拒绝复位"
            )

        records.append({
            "date": trade_date.isoformat(),
            "confirmed_by": confirmation.confirmed_by,
            "reason": confirmation.override_reason,
        })
        self._save_reset_history({"total_resets": total_resets + 1, "records": records})
        _logger.warning(
            "DRAWDOWN_MANUAL_RESET by=%s reason=%s total=%d",
            confirmation.confirmed_by, confirmation.override_reason, total_resets + 1,
        )
        transition = self._transition(
            DrawdownState.RECOVERY, "manual_reset_confirmed", trade_date, to_step=0
        )
        self.persist()
        return transition

    # ── 持久化 ──

    def snapshot(self) -> DrawdownStateSnapshot:
        """当前状态快照（§3.18 阶段 3 保存对象）。"""
        return DrawdownStateSnapshot(
            current=self._current,
            recovery_step=self._recovery_step,
            days_in_state=self._days_in_state,
            dd_history=tuple(self._dd_history),
            freeze_days_remaining=self._freeze_days_remaining,
            last_transition=self._last_transition,
            as_of_date=self._last_eval_date.isoformat() if self._last_eval_date else "",
        )

    def persist(self) -> None:
        """原子写状态快照（store=None 纯内存模式跳过）。"""
        if self._store is None:
            return
        t = self._last_transition
        payload: dict[str, Any] = {
            "current": self._current.value,
            "recovery_step": self._recovery_step,
            "days_in_state": self._days_in_state,
            "dd_history": list(self._dd_history),
            "freeze_days_remaining": self._freeze_days_remaining,
            "as_of_date": self._last_eval_date.isoformat() if self._last_eval_date else "",
            "last_transition": (
                {
                    "from": t.from_state.value, "to": t.to_state.value,
                    "reason": t.reason, "trade_date": t.trade_date,
                    "from_step": t.from_step, "to_step": t.to_step,
                }
                if t is not None else None
            ),
        }
        self._store.save(self._state_ns, payload)

    def load_or_none(self) -> DrawdownStateSnapshot | None:
        """启动恢复：加载持久化快照。None=冷启动（保持默认 NORMAL）。

        Raises:
            StateCorruptError: 记录损坏——消费方必须 fail-closed，本层不兜底。
        """
        if self._store is None:
            return None
        data = self._store.load(self._state_ns)
        if data is None:
            return None
        try:
            self._current = DrawdownState(data["current"])
            self._recovery_step = int(data["recovery_step"])
            self._days_in_state = int(data["days_in_state"])
            self._dd_history = [float(h) for h in data.get("dd_history", [])][-_DD_HISTORY_WINDOW:]
            self._freeze_days_remaining = int(data.get("freeze_days_remaining", 0))
            t = data.get("last_transition")
            self._last_transition = (
                StateTransition(
                    from_state=DrawdownState(t["from"]), to_state=DrawdownState(t["to"]),
                    reason=str(t["reason"]), trade_date=str(t["trade_date"]),
                    from_step=int(t.get("from_step", 0)), to_step=int(t.get("to_step", 0)),
                )
                if t else None
            )
            as_of = str(data.get("as_of_date", ""))
            self._last_eval_date = date.fromisoformat(as_of) if as_of else None
        except (KeyError, ValueError, TypeError) as exc:
            raise InvalidDrawdownStateError(
                f"状态快照字段非法: {exc}", details={"namespace": self._state_ns}
            ) from exc
        if self._recovery_step < 0 or self._recovery_step > 2:
            raise InvalidDrawdownStateError(
                f"recovery_step 越界: {self._recovery_step}（合法 0/1/2）"
            )
        return self.snapshot()

    def _load_reset_history(self) -> dict[str, Any]:
        if self._store is None:
            return getattr(self, "_mem_reset_history", {"total_resets": 0, "records": []})
        data = self._store.load(self._reset_ns)
        return data if data is not None else {"total_resets": 0, "records": []}

    def _save_reset_history(self, history: dict[str, Any]) -> None:
        if self._store is None:
            self._mem_reset_history = history
            return
        self._store.save(self._reset_ns, history)

    # ── 内部 ──

    def _validate_eval_inputs(
        self, trade_date: date, var_95: float | None,
        cvar_95: float | None, recovered_pct: float,
    ) -> None:
        if self._last_eval_date is not None and trade_date < self._last_eval_date:
            raise InvalidDrawdownStateError(
                f"trade_date 倒退: {trade_date} < {self._last_eval_date}"
            )
        for name, v in (("var_95", var_95), ("cvar_95", cvar_95)):
            if v is not None and v < 0:
                raise InvalidDrawdownStateError(f"{name} 须 >= 0, got {v}")
        if not 0.0 <= recovered_pct <= 1.0 + 1e-9:
            raise InvalidDrawdownStateError(f"recovered_pct 须在 [0,1], got {recovered_pct}")

    def _advance_day(self, trade_date: date, dd_abs: float) -> bool:
        """日推进：trade_date 前进 → 计 1 个交易日（days_in_state+1、dd_history 追加）。

        同日重复调用：幂等更新 dd_history 末位（当日最新值），不重复计日。
        Returns: 是否新交易日。
        """
        if self._last_eval_date == trade_date:
            if self._dd_history:
                self._dd_history[-1] = dd_abs
            else:
                self._dd_history.append(dd_abs)
            return False
        self._last_eval_date = trade_date
        self._days_in_state += 1
        self._dd_history.append(dd_abs)
        if len(self._dd_history) > _DD_HISTORY_WINDOW:
            del self._dd_history[: len(self._dd_history) - _DD_HISTORY_WINDOW]
        return True

    def _transition(
        self,
        to_state: DrawdownState,
        reason: str,
        trade_date: date,
        *,
        to_step: int,
    ) -> StateTransition:
        """执行转换（含阶梯内迁移）：重置 days_in_state，记录 last_transition。"""
        transition = StateTransition(
            from_state=self._current, to_state=to_state, reason=reason,
            trade_date=trade_date.isoformat(),
            from_step=self._recovery_step, to_step=to_step,
        )
        _logger.info(
            "DRAWDOWN_TRANSITION %s(step=%d) -> %s(step=%d) reason=%s date=%s",
            transition.from_state.value, transition.from_step,
            transition.to_state.value, transition.to_step, reason, trade_date,
        )
        self._current = to_state
        self._recovery_step = to_step
        self._days_in_state = 0
        self._freeze_days_remaining = 0
        self._last_transition = transition
        return transition
