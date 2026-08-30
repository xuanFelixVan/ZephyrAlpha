# [BLUEPRINT] MOD-RK-05C | (36号 §3.15 VaR breach 状态机) | §
# [TTL] permanent
# [MODULE] zephyr.risk.core.var_breach_state_machine
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.state_store(可选,注入启用跨重启持久化)
# [CONSUMERS] MOD-POS-008(DrawdownController.evaluate var_breach_state 乘性折扣); RiskLayerOrchestrator(编排注入)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 状态迁移 NORMAL→BREACHED→RECOVERY→NORMAL; BREACHED→RECOVERY 需连续3日<recovery_threshold(反弹重置); RECOVERY→NORMAL 需连续5日(同一计数器续计); RECOVERY中VaR>breach_threshold→回BREACHED(复燃清零); 乘数 NORMAL×1.0/BREACHED×0.8/RECOVERY×0.9; 快照缺失→冷启动默认NORMAL
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidVarBreachConfigError; StateCorruptError(快照损坏上抛)
# [TESTS] tests/risk/test_var_breach_state_machine.py
# [TTL] permanent

# [ALGO_FLOW]
# I1: current_var(当日盘前 VaR 占净值比, ≥0) + today(交易日, 每日调用一次)
# I2: VarBreachConfig(breach_threshold=0.02 / recovery_threshold=×0.8 / 3日→RECOVERY / 5日→NORMAL)
# A1: transition(NORMAL超breach→BREACHED记date清零; BREACHED连续低于recovery计数≥3→RECOVERY; RECOVERY计数≥5→NORMAL; 复燃>breach→BREACHED清零; 中间带停留+计数重置)
# A2: save/load(JsonStateStore 命名空间快照, 缺失→冷启动NORMAL, 损坏→StateCorruptError 上抛由消费方 fail-closed)
# O1: VarBreachState + position_cap_multiplier(×1.0/×0.8/×0.9) → drawdown_controller.evaluate 乘性折扣
# [/ALGO_FLOW]
"""
VaR Breach State Machine — VaR breach 恢复/复位状态机 (36号 §3.15)

与 35号 DrawdownStateMachine 正交: 回撤状态机是账户级净值回撤驱动(已发生事实),
本状态机是组合级风险度量驱动(前瞻性风险), 两者经 drawdown_controller.evaluate(
var_breach_state=...) context 参数乘性折扣协同(任一触发即整体保守, 不累乘冲突):

    | VaR breach 状态 | position_cap 乘数 | 协同理由 |
    | NORMAL          | ×1.0              | VaR 未 breach, 回撤状态机独立运行 |
    | BREACHED        | ×0.8              | 组合风险恶化, 即便回撤未触发也需额外保守 |
    | RECOVERY        | ×0.9              | 风险缓解但未完全恢复, 轻量折扣 |

转换规则 (每日盘前调用一次 transition):
    - NORMAL → BREACHED: current_var > breach_threshold, 记录 breach_date, 计数清零
    - BREACHED → RECOVERY: current_var < recovery_threshold 连续 ≥3 日(期间反弹则计数重置)
    - RECOVERY → NORMAL: current_var < recovery_threshold 连续 ≥5 日(同一计数器续计, 恢复期更长)
    - RECOVERY 复燃: VaR 再超 breach_threshold → 回 BREACHED(计数清零, 重记 breach_date)

跨重启持久化 (§3.15 D3): VarBreachStateSnapshot(state, breach_date,
consecutive_days_below_recovery, last_transition); §3.18 盘后 save(), §3.19 盘前 load();
快照缺失 → 冷启动默认 NORMAL(不假设上次在 BREACHED); 快照损坏 → StateCorruptError
上抛(state_store 三分语义, 消费方 fail-closed)。

SSoT: docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/36_var_es_monitoring.md §3.15
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: config 参数
#   fields: 参数 config（无注解）
#   code: var_breach_state_machine.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: snapshot 参数
#   fields: 参数 snapshot（无注解）
#   code: var_breach_state_machine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① VarBreachConfig
#   name_en: VarBreachConfig
#   intro: VaR breach 状态机配置 (C 类可调参数, §3.15 参数表)。
#   desc: VaR breach 状态机配置 (C 类可调参数, §3.15 参数表)。 Attributes: breach_threshold: 进入 BREACHED 的 VaR 阈值…；公共方法（定义序）: recover…
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② VarBreachStateSnapshot
#   name_en: VarBreachStateSnapshot
#   intro: VaR breach 状态跨重启快照 (§3.15 D3)。
#   desc: VaR breach 状态跨重启快照 (§3.15 D3)。 Attributes: state: 当前状态 breach_date: 最近进入 BREACHED 的日期 (IS…；公共方法（定义序）: to_dict…
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ VarBreachStateMachine
#   name_en: VarBreachStateMachine
#   intro: VaR breach 恢复/复位状态机 (36号 §3.15)。
#   desc: VaR breach 恢复/复位状态机 (36号 §3.15)。 用法:: machine = VarBreachStateMachine() # 冷启动 NORMAL mach…；公共方法（定义序）: config,…
#   inputs: config snapshot
#   outputs: 返回值
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: VarBreachConfig, VarBreachStateSnapshot, VarBreachStateMachine
#   downstream: MOD-POS-008(DrawdownController.evaluate var_breach_state 乘性折扣); RiskLayerOrches…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.state_store import StateCorruptError

__all__: Final = [
    "VarBreachState",
    "VarBreachConfig",
    "VarBreachStateSnapshot",
    "VarBreachStateMachine",
    "InvalidVarBreachConfigError",
    "VAR_BREACH_STATE_NAMESPACE",
    "VAR_BREACH_CAP_MULTIPLIER",
]

logger = logging.getLogger(__name__)

#: 跨重启持久化命名空间 (§3.15 D3)
VAR_BREACH_STATE_NAMESPACE: Final = "var_breach_state"

#: 状态 → position_cap 乘性折扣 (§3.15 协同表)
VAR_BREACH_CAP_MULTIPLIER: Final = {"NORMAL": 1.0, "BREACHED": 0.8, "RECOVERY": 0.9}


class InvalidVarBreachConfigError(ZephyrBaseError):
    """VaR breach 状态机配置/输入非法。"""

    error_code = "ZA-RK-0030"


class VarBreachState(str, Enum):
    """VaR breach 状态机三态。"""

    NORMAL = "NORMAL"
    BREACHED = "BREACHED"
    RECOVERY = "RECOVERY"

    @property
    def position_cap_multiplier(self) -> float:
        """该状态对应的 position_cap 乘性折扣 (§3.15 协同表)。"""
        return VAR_BREACH_CAP_MULTIPLIER[self.value]


@dataclass(frozen=True)
class VarBreachConfig:
    """VaR breach 状态机配置 (C 类可调参数, §3.15 参数表)。

    Attributes:
        breach_threshold: 进入 BREACHED 的 VaR 阈值 (默认 var_yellow 0.02)
        recovery_threshold_ratio: recovery_threshold = breach_threshold × 本比例 (默认 0.8)
        days_to_recovery: BREACHED→RECOVERY 连续低于恢复阈值天数 (默认 3)
        days_to_normal: RECOVERY→NORMAL 连续低于恢复阈值天数 (默认 5, 同一计数器续计,
            必须 ≥ days_to_recovery)
    """

    breach_threshold: float = 0.02
    recovery_threshold_ratio: float = 0.8
    days_to_recovery: int = 3
    days_to_normal: int = 5

    def __post_init__(self) -> None:
        if self.breach_threshold <= 0:
            raise InvalidVarBreachConfigError(f"breach_threshold must be >0, got {self.breach_threshold}")
        if not 0.0 < self.recovery_threshold_ratio < 1.0:
            raise InvalidVarBreachConfigError(
                f"recovery_threshold_ratio must be in (0,1), got {self.recovery_threshold_ratio}"
            )
        if self.days_to_recovery < 1:
            raise InvalidVarBreachConfigError(f"days_to_recovery must be >=1, got {self.days_to_recovery}")
        if self.days_to_normal < self.days_to_recovery:
            raise InvalidVarBreachConfigError(
                f"days_to_normal({self.days_to_normal}) must be >= "
                f"days_to_recovery({self.days_to_recovery}) (同一计数器续计, 恢复期更长)"
            )

    @property
    def recovery_threshold(self) -> float:
        """恢复阈值 = breach_threshold × recovery_threshold_ratio。"""
        return self.breach_threshold * self.recovery_threshold_ratio


@dataclass(frozen=True)
class VarBreachStateSnapshot:
    """VaR breach 状态跨重启快照 (§3.15 D3)。

    Attributes:
        state: 当前状态
        breach_date: 最近进入 BREACHED 的日期 (ISO 字符串; NORMAL 为 None)
        consecutive_days_below_recovery: 连续低于恢复阈值天数 (跨 BREACHED→RECOVERY 续计)
        last_transition: 最近一次状态迁移日期 (ISO 字符串; 无迁移为 None)
    """

    state: VarBreachState
    breach_date: str | None
    consecutive_days_below_recovery: int
    last_transition: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "breach_date": self.breach_date,
            "consecutive_days_below_recovery": self.consecutive_days_below_recovery,
            "last_transition": self.last_transition,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VarBreachStateSnapshot:
        """从持久化字典恢复; 语义畸形 → StateCorruptError (消费方 fail-closed)。"""
        try:
            state = VarBreachState(str(data["state"]))
            consec = int(data["consecutive_days_below_recovery"])
            breach_date = data.get("breach_date")
            last_transition = data.get("last_transition")
        except (KeyError, TypeError, ValueError) as exc:
            raise StateCorruptError(
                "VarBreachStateSnapshot 语义畸形",
                details={"error": str(exc), "keys": sorted(data.keys())},
            ) from exc
        if consec < 0:
            raise StateCorruptError(
                "VarBreachStateSnapshot consecutive_days_below_recovery 为负",
                details={"value": consec},
            )
        return cls(state, breach_date, consec, last_transition)


class VarBreachStateMachine:
    """VaR breach 恢复/复位状态机 (36号 §3.15)。

    用法::

        machine = VarBreachStateMachine()                    # 冷启动 NORMAL
        machine = VarBreachStateMachine.load(state_store)    # 盘前加载 (§3.19)
        state = machine.transition(current_var, today)       # 每日盘前迁移
        controller.evaluate(..., var_breach_state=state)     # 乘性折扣协同
        machine.save(state_store)                            # 盘后持久化 (§3.18)
    """

    def __init__(
        self,
        config: VarBreachConfig | None = None,
        *,
        snapshot: VarBreachStateSnapshot | None = None,
    ) -> None:
        self._config = config or VarBreachConfig()
        snap = snapshot or VarBreachStateSnapshot(VarBreachState.NORMAL, None, 0, None)
        self._state = snap.state
        self._breach_date = snap.breach_date
        self._consec = snap.consecutive_days_below_recovery
        self._last_transition = snap.last_transition

    @property
    def config(self) -> VarBreachConfig:
        return self._config

    @property
    def state(self) -> VarBreachState:
        return self._state

    @property
    def breach_date(self) -> str | None:
        return self._breach_date

    @property
    def consecutive_days_below_recovery(self) -> int:
        return self._consec

    @property
    def position_cap_multiplier(self) -> float:
        """当前状态的 position_cap 乘性折扣 (NORMAL×1.0/BREACHED×0.8/RECOVERY×0.9)。"""
        return self._state.position_cap_multiplier

    # ── 状态迁移 ──

    def transition(self, current_var: float, today: date | None = None) -> VarBreachState:
        """当日盘前 VaR 驱动的状态迁移 (每日调用一次)。

        Args:
            current_var: 当日盘前 VaR 占净值比 (≥0, 如 0.025=2.5%)
            today: 交易日 (留痕 breach_date/last_transition; None=不记日期)

        Returns:
            迁移后状态。
        """
        if current_var < 0:
            raise InvalidVarBreachConfigError(f"current_var must be >=0, got {current_var}")
        cfg = self._config
        day = today.isoformat() if today is not None else None
        prev = self._state

        if self._state is VarBreachState.NORMAL:
            if current_var > cfg.breach_threshold:
                self._state = VarBreachState.BREACHED
                self._breach_date = day
                self._consec = 0
        elif self._state is VarBreachState.BREACHED:
            if current_var > cfg.breach_threshold:
                self._consec = 0  # 仍在 breach 线上方, 计数清零
            elif current_var < cfg.recovery_threshold:
                self._consec += 1
                if self._consec >= cfg.days_to_recovery:
                    self._state = VarBreachState.RECOVERY
            else:
                self._consec = 0  # 中间带反弹, 计数重置, 停留 BREACHED
        else:  # RECOVERY
            if current_var > cfg.breach_threshold:
                self._state = VarBreachState.BREACHED  # 复燃, 计数清零, 重记日期
                self._breach_date = day
                self._consec = 0
            elif current_var < cfg.recovery_threshold:
                self._consec += 1
                if self._consec >= cfg.days_to_normal:
                    self._state = VarBreachState.NORMAL
                    self._breach_date = None
                    self._consec = 0
            else:
                self._consec = 0  # 中间带, 停留 RECOVERY

        if self._state is not prev:
            self._last_transition = day
            logger.info(
                "VAR_BREACH transition %s -> %s (var=%.4f date=%s consec=%d)",
                prev.value,
                self._state.value,
                current_var,
                day,
                self._consec,
            )
        return self._state

    # ── 跨重启持久化 (§3.15 D3) ──

    def snapshot(self) -> VarBreachStateSnapshot:
        """当前状态快照 (§3.18 阶段 1 盘后持久化载荷)。"""
        return VarBreachStateSnapshot(
            state=self._state,
            breach_date=self._breach_date,
            consecutive_days_below_recovery=self._consec,
            last_transition=self._last_transition,
        )

    def save(self, store: Any, namespace: str = VAR_BREACH_STATE_NAMESPACE) -> None:
        """盘后持久化 (§3.18 阶段 1)。写失败仅告警不阻断 (fail-open-to-memory,
        对齐 PotFailureCounter 持久化策略)。"""
        try:
            store.save(namespace, self.snapshot().to_dict())
        except Exception:  # noqa: BLE001 — 写失败降级内存态, 不阻断主链路
            logger.warning("VarBreachState 持久化失败 (降级内存态)", exc_info=True)

    @classmethod
    def load(
        cls,
        store: Any,
        config: VarBreachConfig | None = None,
        namespace: str = VAR_BREACH_STATE_NAMESPACE,
    ) -> VarBreachStateMachine:
        """盘前加载 (§3.19 阶段 1)。

        无快照 → 冷启动默认 NORMAL (§3.15: 不假设上次在 BREACHED);
        快照损坏 → StateCorruptError 原样上抛 (state_store 三分语义,
        消费方 fail-closed)。
        """
        rec = store.load(namespace)
        if rec is None:
            logger.info("VAR_BREACH cold_start_default_NORMAL (无快照)")
            return cls(config)
        machine = cls(config, snapshot=VarBreachStateSnapshot.from_dict(rec))
        logger.info("VAR_BREACH restored_%s (快照续存)", machine.state.value)
        return machine
