# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_simulator
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.gov_enforcement.rule_enforcement.gate_context; zephyr.gov_enforcement.rule_enforcement.gate_pipeline
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
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

"""
门禁模拟器——dry-run 全链路门禁演练，不修改任何状态（beta）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: gate_simulator.py
# 层: 算法
# - id: A1
#   name_zh: ① SimulationReport
#   name_en: SimulationReport
#   intro: class SimulationReport 源码 L76-L90
#   desc: 公共方法（定义序）: summary；源码 L76-L90
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② GateSimulator
#   name_en: GateSimulator
#   intro: class GateSimulator 源码 L93-L120
#   desc: 公共方法（定义序）: simulate, history, clear_history；源码 L93-L120
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ main
#   name_en: main
#   intro: main() 源码 L126-L127
#   desc: 源码 L126-L127
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: SimulationReport, GateSimulator, main
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime

from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_context import GateContext, GateResult, GateStatus
from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_pipeline import GatePipeline

logger = logging.getLogger(__name__)


@dataclass
class SimulationReport:
    pipeline_name: str
    results: list[GateResult]
    overall: GateStatus
    duration_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

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
