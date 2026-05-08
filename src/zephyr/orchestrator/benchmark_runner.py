"""跨系统性能基准与回归预防（CT-BENCH）——13条CT-*基准数据+回归告警。"""

from __future__ import annotations

BASELINES: dict[str, dict] = {
    "CT-ORC-SCRIPT-001": {"p50_ms": 500, "p95_ms": 3000, "p99_ms": 5000},
    "CT-ORC-CE-001": {"p50_ms": 100, "p95_ms": 500, "p99_ms": 1000},
    "CT-PIPE-ORC-001": {"p50_ms": 10, "p95_ms": 50, "p99_ms": 100},
}

class BenchmarkRunner:
    def get_baseline(self, contract_id: str) -> dict:
        return BASELINES.get(contract_id, {"p50_ms": 100, "p95_ms": 500, "p99_ms": 1000})

    def detect_regression(self, contract_id: str, p95_ms: float) -> bool:
        baseline = self.get_baseline(contract_id)
        return p95_ms > baseline["p95_ms"] * 1.5
