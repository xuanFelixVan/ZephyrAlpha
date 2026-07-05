# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate-engine/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.gate_engine.gate_pipeline
# [DOMAIN] D_GOV_RULE
# [DEPENDENCIES] zephyr.governance.rule_enforcement.gate_context
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
# [A_module] module_id=MOD-GOV_gate_pipeline | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""门禁评估管线——排序解析、组合逻辑（AND/OR/NOT）、并行调度（beta）

v0.2.0: 统一 GateResult + GatePipeline 可编排 GateEngine
  - GateStep.checker 返回 gate_context.GateResult（统一模型）
  - 新增 from_engine_step() 工厂方法：将 GateEngine.evaluate() 包装为 GateStep
  - run() 中自动通过 GateResult.from_engine_result() 桥接旧版 Engine 输出
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from zephyr.governance.rule_enforcement.gate_engine.gate_context import GateContext, GateResult, GateStatus

logger = logging.getLogger(__name__)


class Combinator(Enum):
    AND = auto()
    OR = auto()
    NOT = auto()


@dataclass
class GateStep:
    gate_id: str
    checker: Callable[[GateContext], GateResult]
    combinator: Combinator = Combinator.AND
    depends_on: list[str] = field(default_factory=list)


class GatePipeline:
    _MAX_WORKERS = 8

    def __init__(self, name: str = "default") -> None:
        self.name = name
        self._steps: list[GateStep] = []

    def add(self, step: GateStep) -> None:
        self._steps.append(step)

    @classmethod
    def from_engine_step(
        cls,
        gate_id: str,
        engine: Any,
        task: Any,
        *,
        combinator: Combinator = Combinator.AND,
        depends_on: list[str] | None = None,
    ) -> GateStep:
        def checker(ctx: GateContext) -> GateResult:
            try:
                engine_result = engine.evaluate(task, gate_id)
                return GateResult.from_engine_result(engine_result)
            except Exception as exc:
                return GateResult(
                    gate_id=gate_id,
                    status=GateStatus.ERROR,
                    reasons=[f"GateEngine.evaluate() raised: {exc}"],
                    task_id=getattr(task, "task_id", ""),
                )

        return GateStep(
            gate_id=gate_id,
            checker=checker,
            combinator=combinator,
            depends_on=depends_on or [],
        )

    def run(self, ctx: GateContext) -> list[GateResult]:
        sequential_steps = [s for s in self._steps if not s.depends_on]
        conditional_steps = [s for s in self._steps if s.depends_on]

        results: list[GateResult] = []
        results.extend(self._run_parallel(sequential_steps, ctx))
        if any(r.status == GateStatus.FAIL for r in results):
            return results

        results.extend(self._run_sequential(conditional_steps, ctx))
        return results

    def _run_parallel(self, steps: list[GateStep], ctx: GateContext) -> list[GateResult]:
        results: list[GateResult] = []
        with ThreadPoolExecutor(max_workers=self._MAX_WORKERS) as executor:
            futures = {executor.submit(s.checker, ctx): s for s in steps}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if not isinstance(result, GateResult):
                        result = GateResult.from_engine_result(result)
                    results.append(result)
                except Exception as exc:
                    step = futures[future]
                    results.append(
                        GateResult(
                            gate_id=step.gate_id,
                            status=GateStatus.ERROR,
                            reasons=[f"Step raised: {exc}"],
                        )
                    )
        return results

    def _run_sequential(self, steps: list[GateStep], ctx: GateContext) -> list[GateResult]:
        results: list[GateResult] = []
        for step in steps:
            try:
                result = step.checker(ctx)
                if not isinstance(result, GateResult):
                    result = GateResult.from_engine_result(result)
                results.append(result)
            except Exception as exc:
                results.append(
                    GateResult(
                        gate_id=step.gate_id,
                        status=GateStatus.ERROR,
                        reasons=[f"Step raised: {exc}"],
                    )
                )
        return results

    def evaluate(self, results: list[GateResult]) -> GateStatus:
        failures = [r for r in results if r.status == GateStatus.FAIL]
        if failures:
            return GateStatus.FAIL
        return GateStatus.PASS

    def __len__(self) -> int:
        return len(self._steps)

    def __bool__(self) -> bool:
        """5.124.1 修复：GatePipeline 不是容器，__len__ 语义为"gate数量"而非"容器大小"。

        显式 __bool__ 消除 `if pipeline:` 歧义——空 pipeline 不应被误判为 False。
        """
        return True


__all__ = ["Combinator", "GatePipeline", "GateStep"]


def main() -> None:
    pass


if __name__ == "__main__":
    main()
