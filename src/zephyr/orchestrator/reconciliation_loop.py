"""
调和循环（Reconciliation Loop — CT-RECONCILE-001）

依据：MOD-MASTER-001 蓝图 §十六
K8s Controller Pattern——每30s调和5项 invariants。
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Invariant(BaseModel):
    name: str
    current: str = ""
    expected: str = ""
    ok: bool = True


RECONCILE_INVARIANTS: list[str] = [
    "contract_checksums_consistent",
    "circuit_breaker_states_valid",
    "cbac_matrix_checksum_valid",
    "taskcard_status_pipeline_valid",
    "dlq_message_count",
]


class ReconcileResult(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    invariants: list[Invariant] = Field(default_factory=list)
    all_ok: bool = True


class ReconciliationLoop:
    def __init__(self):
        self._results: list[ReconcileResult] = []
        self._interval_s: float = 30.0

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
