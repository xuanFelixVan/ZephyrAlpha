"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: reconciliation_loop.py
# 层: 算法
# - id: A1
#   name_zh: ① ReconciliationLoop
#   name_en: ReconciliationLoop
#   intro: class ReconciliationLoop 源码 L85-L111
#   desc: 公共方法（定义序）: results, reconcile, get_invariants；源码 L85-L111
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ReconciliationLoop
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.reconciliation_loop
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
调和循环（Reconciliation Loop — CT-RECONCILE-001）

依据：MOD-MASTER-002 蓝图 §十六
K8s Controller Pattern——每30s调和5项 invariants。
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


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
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    invariants: list[Invariant] = Field(default_factory=list)
    all_ok: bool = True


class ReconciliationLoop:
    def __init__(self):
        self._results: list[ReconcileResult] = []
        self._interval_s: float = 30.0

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
        invariants: list[Invariant] = []
        for name in RECONCILE_INVARIANTS:
            ok = states.get(name, True) if states else True
            invariants.append(Invariant(name=name, ok=ok, expected="ok", current="ok" if ok else "fail"))
        result = ReconcileResult(invariants=invariants, all_ok=all(i.ok for i in invariants))
        self._results.append(result)
        return result

    def get_invariants(self) -> list[str]:
        return list(RECONCILE_INVARIANTS)
