# [BLUEPRINT] MOD-INF-035 | docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md
# [MODULE] zephyr.trading.stop_gate
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.trading.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-035 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
StopGate — 质量闸门
====================
蓝图: docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md §3.1
借鉴: Claude Code 45天自主实验——被动质量闸门
阻止 AI 什么都不做就退出。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: session_max_actions 参数
#   fields: 参数 session_max_actions（无注解）
#   code: stop_gate.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: session_max_minutes 参数
#   fields: 参数 session_max_minutes（无注解）
#   code: stop_gate.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① StopGate
#   name_en: StopGate
#   intro: 质量闸门——AI 不能空手退出。
#   desc: 质量闸门——AI 不能空手退出。 借鉴: Claude Code 45天自主实验——Stop Gate 阻止了 19/30 的空转 session。 设计原理: - 不告诉 AI…；公共方法（定义序）: session…
#   inputs: session_max_actions session_max_minutes
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: StopGate
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field
from datetime import datetime

from zephyr.shared.utils.time_utils import now_utc


@dataclass
class StopGateResult:
    can_stop: bool = True
    reasons: list[str] = field(default_factory=list)


class StopGate:
    """质量闸门——AI 不能空手退出。

    借鉴: Claude Code 45天自主实验——Stop Gate 阻止了 19/30 的空转 session。
    设计原理:
      - 不告诉 AI 该做什么（避免过度约束）
      - 只阻止 AI 什么都不做就退出（最低质量标准）

    Session 预算（蓝图 §16.3 步骤 1「StopGate session 预算参数」）：
      - session_max_actions / session_max_minutes 为 session 继续工作的预算上限；
      - 预算超限 → 阻断 session 继续工作（can_continue()=False），质量闸门
        放行退出（check() 强制 can_stop=True 并记录预算原因）——预算是
        「继续」的预算而非「退出」的预算，语义与空转闸门的初衷一致（防空转、
        也防失控长跑）；
      - 默认 None 不设限，零行为变化。
    """

    def __init__(
        self,
        session_max_actions: int | None = None,
        session_max_minutes: float | None = None,
    ) -> None:
        self._session_start: str = ""
        self._shutdown_acknowledged = False
        self._session_max_actions = session_max_actions
        self._session_max_minutes = session_max_minutes
        self._action_count = 0

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def session_start(self) -> str:
        """只读：session_start（Stage 4 公共化）。"""
        return self._session_start

    @session_start.setter
    def session_start(self, value):
        """写入：session_start（Stage 4 公共化）。"""
        self._session_start = value

    @property
    def shutdown_acknowledged(self):
        """只读：shutdown_acknowledged（Stage 4 公共化）。"""
        return self._shutdown_acknowledged

    @shutdown_acknowledged.setter
    def shutdown_acknowledged(self, value):
        """写入：shutdown_acknowledged（Stage 4 公共化）。"""
        self._shutdown_acknowledged = value

    def initialize(self) -> None:
        self._session_start = now_utc().isoformat()
        self._shutdown_acknowledged = False
        self._action_count = 0

    # ── Session 预算（蓝图 §16.3 步骤 1）──
    def record_action(self, n: int = 1) -> None:
        """记录 session 工作动作计数（用于动作数预算）。"""
        self._action_count += n

    def budget_status(self) -> dict[str, int | float | bool | None]:
        return {
            "action_count": self._action_count,
            "session_max_actions": self._session_max_actions,
            "session_max_minutes": self._session_max_minutes,
            "exceeded": self.budget_exceeded(),
        }

    def budget_exceeded(self) -> bool:
        if self._session_max_actions is not None and self._action_count >= self._session_max_actions:
            return True
        if self._session_max_minutes is not None and self._session_start:
            try:
                start = datetime.fromisoformat(self._session_start)
            except ValueError:
                return False
            elapsed_s = (now_utc() - start).total_seconds()
            return elapsed_s >= self._session_max_minutes * 60
        return False

    def can_continue(self) -> bool:
        """session 是否可继续工作——预算超限即阻断继续。"""
        return not self.budget_exceeded()

    def check(
        self,
        *,
        audit_has_new_entries: bool = True,
        night_shift_all_resolved: bool = True,
        dream_cycle_archived: bool = True,
        git_clean: bool = True,
    ) -> StopGateResult:
        result = StopGateResult(can_stop=True, reasons=[])

        if not audit_has_new_entries:
            result.can_stop = False
            result.reasons.append("AiAuditLogger: no new entries since last check")

        if not night_shift_all_resolved:
            result.can_stop = False
            result.reasons.append("NightShiftQueue: unresolved entries remain")

        if not dream_cycle_archived:
            result.can_stop = False
            result.reasons.append("DreamCycle: unarchived memory remains")

        if not git_clean:
            result.can_stop = False
            result.reasons.append("Git: uncommitted changes remain")

        if self.budget_exceeded():
            # 预算超限：阻断 session 继续工作，质量闸门放行退出（防止失控长跑）
            result.can_stop = True
            result.reasons.append("Session budget exceeded: further work blocked, stop forced")

        return result

    def can_stop(self, **kwargs: bool) -> bool:
        return self.check(**kwargs).can_stop

    def acknowledge_shutdown(self) -> None:
        self._shutdown_acknowledged = True
