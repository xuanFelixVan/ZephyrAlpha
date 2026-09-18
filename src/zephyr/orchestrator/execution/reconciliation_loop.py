# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.reconciliation_loop
# [ALGO_FLOW] external: docs/03_modules/_domain_orchestrator/algo_flow/reconciliation_loop.yaml
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__; zephyr.shared.utils.time_utils
# [CONSUMERS] 无生产消费方（BRK-017 在册断点；本件调和的是**编排器自身完整性**5 项不变量，非 FF-11→FF-12 成交对账链）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 未观测的不变量一律判不通过(Fail-Closed)——缺证据即视为坏，禁"没测就算好"; all_ok=True 必须逐项显式 True
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 不向外抛——未观测项以 ok=False + current="unobserved" 表达
# [TESTS] tests/trading/test_reconciliation_loop.py
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
调和循环（Reconciliation Loop — CT-RECONCILE-001）

依据：MOD-MASTER-002 蓝图 §十六
K8s Controller Pattern——调和 5 项编排器完整性 invariants。

作用域澄清（全流通战役 BRK-017，2026-09-18 实测）：本件调和的是
**编排器自身**的 5 项不变量（契约校验和 / 熔断器状态 / CBAC 矩阵 /
任务卡状态机 / DLQ 消息数），**不是** FF-11→FF-12 的成交-持仓对账链
（那条链的事件入口在 ``zephyr.position.position_reconciler.handle_execution_report``，
断点 BRK-016）。断点普查把它记成"对账循环未接→与 BRK-020 同链"是**误归因**，
按此接线会把成交数据喂给一个只认 5 个治理键的循环——假闭环。
另：``_interval_s=30`` 是历史遗留的"每 30s 调和"注释，本件**不挂任何
定时线程**（宪法 §9.3：reconciler 必须事件触发，禁 cron/Timer/sleep-loop），
调用方须在事件到达时显式 ``reconcile(states=...)``。

Fail-Closed 加严（对齐裁定 R-E1"保留不产生约束力的门=没有门"）：
  此前实现 ``ok = states.get(name, True) if states else True`` —— 未观测项
  默认判好，即**恒真门**：不传 states 时 5 项全绿、all_ok=True，看起来
  "调和通过"实则一项未查。现契约：

    states=None / 缺某键 / 值非 bool      → 该项 ok=False, current="unobserved"
    全部键显式 True                        → all_ok=True
    新增 result.unobserved 列表            → 区分"查了且坏"与"根本没查"
"""

from typing import Final

from pydantic import BaseModel, Field

from zephyr.shared.utils.time_utils import now_utc

_UNOBSERVED: Final[str] = "unobserved"


class Invariant(BaseModel):
    name: str
    current: str = ""
    expected: str = ""
    ok: bool = True


RECONCILE_INVARIANTS: Final[list[str]] = [
    "contract_checksums_consistent",
    "circuit_breaker_states_valid",
    "cbac_matrix_checksum_valid",
    "taskcard_status_pipeline_valid",
    "dlq_message_count",
]


class ReconcileResult(BaseModel):
    timestamp: object = Field(default_factory=now_utc)
    invariants: list[Invariant] = Field(default_factory=list)
    all_ok: bool = True
    unobserved: list[str] = Field(default_factory=list)


def _evaluate(states: dict[str, bool] | None, name: str) -> Invariant:
    """单项判定：未观测/非 bool 一律 ok=False（Fail-Closed，禁默认判好）。"""
    if not isinstance(states, dict) or name not in states:
        return Invariant(name=name, ok=False, expected="ok", current=_UNOBSERVED)
    value = states[name]
    if not isinstance(value, bool):
        return Invariant(name=name, ok=False, expected="ok", current=f"invalid:{type(value).__name__}")
    return Invariant(name=name, ok=value, expected="ok", current="ok" if value else "fail")


class ReconciliationLoop:
    def __init__(self):
        self._results: list[ReconcileResult] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def results(self) -> list[ReconcileResult]:
        """只读：results（Stage 4 公共化）。"""
        return self._results

    @results.setter
    def results(self, value):
        """写入：results（Stage 4 公共化）。"""
        self._results = value

    def reconcile(self, states: dict[str, bool] | None = None) -> ReconcileResult:
        """调和 5 项不变量——**只有逐项显式给出 True 才算通过**。

        Args:
            states: ``{invariant_name: bool}``；缺键=未观测=不通过（Fail-Closed）。

        Returns:
            ReconcileResult，含 ``unobserved`` 列表（哪些门根本没查）。
        """
        invariants: list[Invariant] = [_evaluate(states, name) for name in RECONCILE_INVARIANTS]
        unobserved = [i.name for i in invariants if i.current == _UNOBSERVED]
        result = ReconcileResult(
            invariants=invariants,
            all_ok=all(i.ok for i in invariants),
            unobserved=unobserved,
        )
        self._results.append(result)
        return result

    def get_invariants(self) -> list[str]:
        return list(RECONCILE_INVARIANTS)
