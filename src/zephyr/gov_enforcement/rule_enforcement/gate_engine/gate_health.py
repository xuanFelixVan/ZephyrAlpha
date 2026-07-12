# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_health
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_gate_health | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""门禁健康仪表板——per-gate SLI 报告、误报率、延迟分布、1人+AI运维视图（beta）"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class GateSLI:
    gate_id: str
    total_evaluations: int = 0
    pass_count: int = 0
    fail_count: int = 0
    skip_count: int = 0
    false_positive_count: int = 0
    latencies_ms: list[float] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if self.total_evaluations == 0:
            return 1.0
        return self.pass_count / self.total_evaluations

    @property
    def false_positive_rate(self) -> float:
        if self.fail_count == 0:
            return 0.0
        return self.false_positive_count / self.fail_count

    @property
    def p50_latency_ms(self) -> float:
        return _percentile(self.latencies_ms, 50)

    @property
    def p99_latency_ms(self) -> float:
        return _percentile(self.latencies_ms, 99)


def _percentile(data: list[float], pct: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = int(len(sorted_data) * pct / 100.0)
    idx = min(idx, len(sorted_data) - 1)
    return sorted_data[idx]


class GateHealth:
    def __init__(self) -> None:
        self._slis: dict[str, GateSLI] = {}

    def get_or_create(self, gate_id: str) -> GateSLI:
        if gate_id not in self._slis:
            self._slis[gate_id] = GateSLI(gate_id=gate_id)
        return self._slis[gate_id]

    def record(self, gate_id: str, passed: bool, latency_ms: float, is_false_positive: bool = False) -> None:
        sli = self.get_or_create(gate_id)
        sli.total_evaluations += 1
        sli.latencies_ms.append(latency_ms)
        if passed:
            sli.pass_count += 1
        else:
            sli.fail_count += 1
            if is_false_positive:
                sli.false_positive_count += 1

    def summary(self) -> list[GateSLI]:
        return list(self._slis.values())

    def health_score(self, gate_id: str) -> float:
        sli = self.get_or_create(gate_id)
        fp_penalty = sli.false_positive_rate * 0.5
        latency_penalty = max(0, (sli.p99_latency_ms - 1000) / 5000)
        return max(0.0, min(1.0, sli.pass_rate - fp_penalty - latency_penalty))


__all__ = ["GateHealth", "GateSLI"]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
