# [BLUEPRINT] MOD-L02-009 | docs/03_modules/_domain_factor/blueprint.md | §D-FACTOR-ANA-08
# [MODULE] zephyr.factor.analysis.multifactor_decay_lifecycle
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.analysis.decay_monitor(半衰期输出对接)
# [CONSUMERS] factor_pool_manager(decay_state字段); multifactor_pit_backtest
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] INV-004: PIT铁律——状态转移仅基于已实现IC/半衰期; DORMANT不参与合成; RETIRED完全退出
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知因子->先init_new_factor; 已RETIRED->不再转移
# [TESTS] tests/factor/test_multifactor_decay_lifecycle.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: factor_id + half_life(decay_monitor输出) + abs_ic(当日|IC|) + cusum_alert(CusumMonitor预警)
# I2: DecayLifecycleParams(halflife_observe=20/ic_floor_dormant=40/recovery_ic=0.03/recovery_days=10/warmup=20/new_mult=0.3/dormant_max=120)
# F1: CusumMonitor(§3.3 CUSUM预警层: S_t=max(0,S_{t-1}+(μ_IC-k-IC_t)), k=0.5σ h=4σ, S_t>h→衰减预警)
# F2: init_new_factor(新因子入池→NEW冷启动0.3权重试运行)
# F3: transition_with_boundaries(6态状态机: NEW→ACTIVE/OBSERVE; ACTIVE→OBSERVE; OBSERVE→DORMANT/ACTIVE; DORMANT→RECOVERY/RETIRED; RECOVERY→ACTIVE/DORMANT)
# F4: check_retirement(DORMANT≥120日无恢复→RETIRED清理)
# O1: FactorDecayState(state/weight_multiplier/days_in_state) + DECAY_TO_REGISTRY_STATUS(6态↔registry 5态映射常量)
# [/ALGO_FLOW]
"""25号memo §3.7#3 因子衰减→动作全生命周期（DecayActionLifecycle 6态状态机）。

补齐 §3.3 三层衰减监控（decay_monitor.py 半衰期）与池管理（factor_pool_manager.py）
之间的编排断裂："检测到衰减后降权/观察/淘汰/复激活"的统一动作状态机。

6 态：NEW（冷启动 0.3 权重试运行）/ ACTIVE（1.0）/ OBSERVE（0.5）/
DORMANT（0.0，不参与合成）/ RECOVERY（0.3 复激活观察）/ RETIRED（永久退役）。

随本模块一并落码（memo §3.3 代码现状注记 + §6 待裁定）：
- CUSUM 预警层（CusumMonitor）：S_t = max(0, S_{t-1} + (μ_IC - k - IC_t))，
  k=0.5σ, h=4σ，S_t>h 触发衰减预警（检测 IC 下行偏移；memo §3.3 公式为
  上行写法，此处按"衰减预警"语义取下行方向）。
- 自动淘汰层：连续 40 交易日 |IC|<0.02 → DORMANT（移入休眠池，停止参与合成）；
  DORMANT 持续 120 日无恢复 → RETIRED。

6态 ↔ factor_registry 5态映射规则（§6 待裁定项，代码内常量映射，不改注册表YAML）：
  NEW→experimental（入池试运行）/ ACTIVE→active / OBSERVE→active（仍参与合成）/
  DORMANT→deprecated / RECOVERY→experimental（复激活试运行）/ RETIRED→retired。
  反向：registry candidate 入池即初始化 NEW。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

__all__ = [
    "DecayState",
    "DecayLifecycleParams",
    "FactorDecayState",
    "CusumMonitor",
    "DecayActionLifecycle",
    "DECAY_TO_REGISTRY_STATUS",
    "registry_status_for",
]


class DecayState(str, Enum):
    """运行时 6 态（25号memo §3.7#3，v1.12.9 补 NEW/RETIRED 两边界态）。"""

    NEW = "NEW"
    ACTIVE = "ACTIVE"
    OBSERVE = "OBSERVE"
    DORMANT = "DORMANT"
    RECOVERY = "RECOVERY"
    RETIRED = "RETIRED"


# 6态 ↔ factor_registry 治理 5态（candidate/experimental/active/deprecated/retired）
# 映射规则（memo §6 待裁定项落码；只定义映射常量，不改动注册表 YAML）。
DECAY_TO_REGISTRY_STATUS: dict[DecayState, str] = {
    DecayState.NEW: "experimental",  # 冷启动试运行
    DecayState.ACTIVE: "active",
    DecayState.OBSERVE: "active",  # 观察中仍参与合成（0.5 权重）
    DecayState.DORMANT: "deprecated",  # 休眠退出合成
    DecayState.RECOVERY: "experimental",  # 复激活试运行
    DecayState.RETIRED: "retired",
}


def registry_status_for(state: DecayState) -> str:
    """运行时 6 态 → factor_registry status 5态映射。"""
    return DECAY_TO_REGISTRY_STATUS[state]


@dataclass(frozen=True)
class DecayLifecycleParams:
    """生命周期阈值参数（25号memo §3.7#3 参数表）。"""

    halflife_observe: float = 20.0  # 半衰期<20→OBSERVE
    cusum_alert_to_dormant: int = 40  # CUSUM 预警后 40 交易日无恢复→DORMANT
    ic_floor_dormant: int = 40  # 连续 40 日 |IC|<0.02→DORMANT
    recovery_ic_threshold: float = 0.03  # DORMANT 后连续 10 日 |IC|>0.03→RECOVERY
    recovery_observe_days: int = 10  # 复激活观察期
    ic_dormant_floor: float = 0.02  # |IC|<0.02 持续→DORMANT
    dormant_skip_synthesis: bool = True  # DORMANT 因子不参与合成
    new_factor_warmup_days: int = 20  # 新因子冷启动期（IC 样本积累）
    new_factor_weight_mult: float = 0.3  # 冷启动期权重乘子
    dormant_max_days: int = 120  # DORMANT 持续 120 日无恢复→永久退役
    retired_skip_all: bool = True  # RETIRED 完全退出


@dataclass
class FactorDecayState:
    """单因子衰减生命周期状态（factor_pool_manager 的 decay_state 字段载体）。"""

    factor_id: str
    state: DecayState = DecayState.NEW
    weight_multiplier: float = 0.3
    days_in_state: int = 0
    ic_below_floor_streak: int = 0  # 连续 |IC|<0.02 天数
    ic_recovery_streak: int = 0  # DORMANT 中连续 |IC|≥0.03 天数
    cusum_alert: bool = False
    cusum_alert_days: int = 0  # CUSUM 预警后无恢复天数

    @property
    def participates_in_synthesis(self) -> bool:
        return self.state is not DecayState.DORMANT and self.state is not DecayState.RETIRED


class CusumMonitor:
    """§3.3 CUSUM 预警层——累积 IC 下行偏移检测。

    S_t = max(0, S_{t-1} + (μ_IC - k - IC_t))，k=0.5σ，h=4σ；
    S_t > h → 触发衰减预警（进入观察池）。
    """

    def __init__(self, mu_ic: float, sigma_ic: float, k_mult: float = 0.5, h_mult: float = 4.0) -> None:
        self.mu_ic = float(mu_ic)
        self.k = k_mult * float(sigma_ic)
        self.h = h_mult * float(sigma_ic)
        self.s = 0.0

    def update(self, ic_t: float) -> bool:
        """喂入当日 IC，返回是否触发衰减预警。"""
        self.s = max(0.0, self.s + (self.mu_ic - self.k - float(ic_t)))
        return self.s > self.h

    @property
    def alert(self) -> bool:
        return self.s > self.h

    def reset(self) -> None:
        self.s = 0.0


class DecayActionLifecycle:
    """6 态衰减动作状态机——每日调 transition_with_boundaries() 更新状态+权重乘子。"""

    def __init__(self, params: DecayLifecycleParams | None = None) -> None:
        self._params = params or DecayLifecycleParams()
        self._states: dict[str, FactorDecayState] = {}

    @property
    def states(self) -> dict[str, FactorDecayState]:
        return self._states

    def init_new_factor(self, factor_id: str) -> FactorDecayState:
        """新因子入池初始化——NEW 冷启动（0.3 权重试运行）。"""
        st = FactorDecayState(
            factor_id=factor_id,
            state=DecayState.NEW,
            weight_multiplier=self._params.new_factor_weight_mult,
        )
        self._states[factor_id] = st
        return st

    def _enter(self, st: FactorDecayState, state: DecayState, mult: float) -> None:
        st.state = state
        st.weight_multiplier = mult
        st.days_in_state = 0
        if state is not DecayState.DORMANT:
            st.ic_recovery_streak = 0
        if state is DecayState.ACTIVE:
            st.cusum_alert = False
            st.cusum_alert_days = 0
            st.ic_below_floor_streak = 0

    def transition_with_boundaries(
        self,
        factor_id: str,
        half_life: float,
        abs_ic: float,
        cusum_alert: bool = False,
    ) -> FactorDecayState:
        """6 态状态转移（含 NEW/RETIRED 边界态）。

        Args:
            factor_id: 因子 ID（未知因子自动 init_new_factor 后当日记 NEW）
            half_life: decay_monitor 输出的 IC 半衰期
            abs_ic: 当日 |IC|
            cusum_alert: CusumMonitor 当日预警

        Returns:
            更新后的 FactorDecayState。RETIRED 为终态不再转移。
        """
        p = self._params
        st = self._states.get(factor_id)
        if st is None:
            st = self.init_new_factor(factor_id)
            return st
        if st.state is DecayState.RETIRED:
            return st

        st.days_in_state += 1
        if abs_ic < p.ic_dormant_floor:
            st.ic_below_floor_streak += 1
        else:
            st.ic_below_floor_streak = 0
        # CUSUM 预警闩锁：当日预警即置位；仅当半衰期恢复且监控器已解除预警才清除
        if cusum_alert:
            st.cusum_alert = True
        elif st.cusum_alert and half_life >= p.halflife_observe:
            st.cusum_alert = False
        # 预警后无恢复天数（半衰期未回到 halflife_observe 视为未恢复）
        if st.cusum_alert and half_life < p.halflife_observe:
            st.cusum_alert_days += 1
        else:
            st.cusum_alert_days = 0

        if st.state is DecayState.NEW:
            if st.days_in_state >= p.new_factor_warmup_days:
                if abs_ic >= p.ic_dormant_floor:
                    self._enter(st, DecayState.ACTIVE, 1.0)
                else:
                    self._enter(st, DecayState.OBSERVE, 0.5)
        elif st.state is DecayState.ACTIVE:
            if half_life < p.halflife_observe:
                self._enter(st, DecayState.OBSERVE, 0.5)
        elif st.state is DecayState.OBSERVE:
            if st.ic_below_floor_streak >= p.ic_floor_dormant or (
                st.cusum_alert and st.cusum_alert_days >= p.cusum_alert_to_dormant
            ):
                self._enter(st, DecayState.DORMANT, 0.0)
            elif half_life >= p.halflife_observe and not st.cusum_alert:
                self._enter(st, DecayState.ACTIVE, 1.0)
        elif st.state is DecayState.DORMANT:
            if abs_ic >= p.recovery_ic_threshold:
                st.ic_recovery_streak += 1
            else:
                st.ic_recovery_streak = 0
            if st.ic_recovery_streak >= p.recovery_observe_days:
                self._enter(st, DecayState.RECOVERY, 0.3)
            else:
                self.check_retirement(factor_id)
        elif st.state is DecayState.RECOVERY:
            if half_life >= p.halflife_observe:
                self._enter(st, DecayState.ACTIVE, 1.0)
            elif abs_ic < p.ic_dormant_floor:
                self._enter(st, DecayState.DORMANT, 0.0)
        return st

    def check_retirement(self, factor_id: str) -> bool:
        """DORMANT 持续 ≥120 日无恢复 → RETIRED。

        执行清理语义：移出活跃/休眠池、registry 标 retired（经映射常量）、
        释放池配额——由调用方（factor_pool_manager）按返回 True 执行。

        Returns:
            是否新转入 RETIRED。
        """
        st = self._states.get(factor_id)
        if st is None or st.state is not DecayState.DORMANT:
            return False
        if st.days_in_state >= self._params.dormant_max_days:
            self._enter(st, DecayState.RETIRED, 0.0)
            return True
        return False
