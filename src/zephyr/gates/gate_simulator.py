"""门禁模拟器——dry-run 全链路门禁演练，不修改任何状态（beta）"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from zephyr.gates.gate_context import GateContext, GateResult, GateStatus
from zephyr.gates.gate_pipeline import GatePipeline

logger = logging.getLogger(__name__)


@dataclass
class SimulationReport:
    pipeline_name: str
    results: list[GateResult]
    overall: GateStatus
    duration_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def summary(self) -> str:
        pass_count = sum(1 for r in self.results if r.status == GateStatus.PASS)
        fail_count = sum(1 for r in self.results if r.status == GateStatus.FAIL)
        return (
            f"[{self.pipeline_name}] {self.overall.name} "
            f"({pass_count}P/{fail_count}F/{len(self.results)}T) "
            f"in {self.duration_ms:.0f}ms"
        )


class GateSimulator:
    def __init__(self) -> None:
        self._reports: list[SimulationReport] = []

    def simulate(self, pipeline: GatePipeline, ctx: GateContext) -> SimulationReport:
        import time

        start = time.monotonic()
        results = pipeline.run(ctx)
        elapsed_ms = (time.monotonic() - start) * 1000

        overall = pipeline.evaluate(results)
        report = SimulationReport(
            pipeline_name=pipeline.name,
            results=results,
            overall=overall,
            duration_ms=elapsed_ms,
        )
        self._reports.append(report)
        logger.info(report.summary())
        return report

    @property
    def history(self) -> list[SimulationReport]:
        return list(self._reports)

    def clear_history(self) -> None:
        self._reports.clear()


__all__ = ["GateSimulator", "SimulationReport"]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
