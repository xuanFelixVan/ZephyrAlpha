# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §phase-executor
# [MODULE] zephyr.governance.rule_enforcement.phase_executor
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS] PhaseManager; GateEngine; task_repo.transition; phase_check_registry
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PhaseExecutor bridges PhaseManager and GateEngine; execute_phase stops on RED; execute_gate delegates to GateEngine.evaluate(); context propagation via ExecutionContext
# [MODIFY-GUARD] execute_phase contract (stops on RED); execute_gate delegation to GateEngine; ExecutionContext immutability
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on unknown phase; GateEngineError on gate evaluation failure; returns PhaseExecutionResult
# [TESTS] tests/test_phase_executor_rule_enforcement.py
# [A_module] module_id=MOD-INF-007_phase_executor | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable

"""PhaseExecutor — 阶段执行器，桥接 PhaseManager 和 GateEngine.

架构位置:
    PhaseManager (编排) → PhaseExecutor (执行) → PhaseCheckRegistry + GateEngine

职责:
    1. 接收 PhaseManager 的编排指令（ConstructionPhase）
    2. 调用 PhaseCheckRegistry.run_check 执行阶段门控检查
    3. 调用 GateEngine.evaluate 执行 YAML 门禁（G0-G7）
    4. 收集结果并传播上下文（ExecutionContext）
    5. 返回聚合的 PhaseExecutionResult

设计原则:
    - RED 检查立即停止后续执行（fail-fast）
    - YELLOW 检查继续执行但标记警告
    - GREEN 检查继续执行
    - 上下文在检查间传播（前序检查结果可供后续检查使用）
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from zephyr.governance.phase_check_registry import run_check
from zephyr.governance.phase_manager import ConstructionPhase, get_phase

logger = logging.getLogger(__name__)

__all__ = [
    "CheckResult",
    "ExecutionContext",
    "GateResultType",
    "PhaseExecutionResult",
    "PhaseExecutor",
]


class GateResultType(str, Enum):
    """门禁结果类型（与 PhaseCheckRegistry.GateResult 对齐）."""

    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


@dataclass
class CheckResult:
    """单个检查的结果."""

    check_name: str
    result: GateResultType
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """执行上下文 — 在检查间传播数据.

    前序检查可以将结果写入 context，后续检查可以读取。
    """

    phase: str = ""
    results: list[CheckResult] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def add_result(self, result: CheckResult) -> None:
        self.results.append(result)

    def has_red(self) -> bool:
        return any(r.result == GateResultType.RED for r in self.results)

    def has_yellow(self) -> bool:
        return any(r.result == GateResultType.YELLOW for r in self.results)

    def get_result(self, check_name: str) -> CheckResult | None:
        for r in self.results:
            if r.check_name == check_name:
                return r
        return None


@dataclass
class PhaseExecutionResult:
    """阶段执行的聚合结果."""

    phase: str
    checks_run: int
    results: list[CheckResult]
    overall: GateResultType
    context: ExecutionContext

    @property
    def passed(self) -> bool:
        return self.overall != GateResultType.RED

    @property
    def red_count(self) -> int:
        return sum(1 for r in self.results if r.result == GateResultType.RED)

    @property
    def yellow_count(self) -> int:
        return sum(1 for r in self.results if r.result == GateResultType.YELLOW)

    @property
    def green_count(self) -> int:
        return sum(1 for r in self.results if r.result == GateResultType.GREEN)


class PhaseExecutor:
    """阶段执行器 — 桥接 PhaseManager 和 GateEngine.

    使用方式:
        executor = PhaseExecutor()
        result = executor.execute_phase(ConstructionPhase.PHASE_0_SKELETON)
        if result.passed:
            gate_result = executor.execute_gate(task, "G1")
    """

    def __init__(self, gate_engine: Any | None = None) -> None:
        """初始化 PhaseExecutor.

        Args:
            gate_engine: GateEngine 实例。None 时延迟初始化。
        """
        self._gate_engine = gate_engine

    @property
    def gate_engine(self) -> Any:
        """延迟加载 GateEngine 实例."""
        if self._gate_engine is None:
            from zephyr.governance.rule_enforcement.gate_engine import GateEngine

            self._gate_engine = GateEngine()
        return self._gate_engine

    def execute_phase(
        self,
        phase: Any,
        *,
        context: ExecutionContext | None = None,
    ) -> PhaseExecutionResult:
        """执行指定阶段的所有门控检查.

        从 PhaseManager 获取 PhaseGate，逐个执行 gate_checks。
        RED 检查立即停止（fail-fast），YELLOW 继续执行。

        Args:
            phase: ConstructionPhase 枚举值
            context: 可选的执行上下文。None 时创建新上下文。

        Returns:
            PhaseExecutionResult: 聚合结果

        Raises:
            ValueError: 未知阶段
        """
        phase_gate = get_phase(phase)
        if phase_gate is None:
            raise ValueError(f"未知阶段: {phase}")

        if context is None:
            context = ExecutionContext(phase=phase.value if hasattr(phase, "value") else str(phase))

        results: list[CheckResult] = []
        overall = GateResultType.GREEN

        for check_name in phase_gate.gate_checks:
            try:
                raw_result = run_check(check_name)
                result_type = GateResultType(raw_result.value if hasattr(raw_result, "value") else str(raw_result))
            except Exception as e:
                logger.warning("检查 %s 异常: %s", check_name, e)
                result_type = GateResultType.YELLOW
                check_result = CheckResult(
                    check_name=check_name,
                    result=result_type,
                    message=f"检查异常: {e}",
                )
            else:
                check_result = CheckResult(
                    check_name=check_name,
                    result=result_type,
                    message="OK" if result_type == GateResultType.GREEN else "检查未通过",
                )

            results.append(check_result)
            context.add_result(check_result)

            if result_type == GateResultType.RED:
                overall = GateResultType.RED
                logger.error("检查 %s 返回 RED，停止后续检查", check_name)
                break
            if result_type == GateResultType.YELLOW and overall != GateResultType.RED:
                overall = GateResultType.YELLOW

        return PhaseExecutionResult(
            phase=phase.value if hasattr(phase, "value") else str(phase),
            checks_run=len(results),
            results=results,
            overall=overall,
            context=context,
        )

    def execute_gate(
        self,
        task: Any,
        gate_id: str,
        *,
        conn: Any | None = None,
    ) -> Any:
        """执行 YAML 门禁（G0-G7）via GateEngine.

        Args:
            task: Task 对象
            gate_id: 门禁 ID（如 "G1", "G7"）
            conn: 可选的 SQLite 连接

        Returns:
            GateResult: GateEngine 返回的门禁结果

        Raises:
            GateEngineError: 门禁评估失败
        """
        return self.gate_engine.evaluate(task, gate_id, conn=conn)

    def execute_phase_with_gates(
        self,
        phase: Any,
        task: Any,
        gate_ids: list[str],
        *,
        context: ExecutionContext | None = None,
    ) -> tuple[PhaseExecutionResult, list[Any]]:
        """执行阶段检查 + YAML 门禁.

        先执行阶段门控检查，若通过（非 RED）再执行 YAML 门禁。

        Args:
            phase: ConstructionPhase 枚举值
            task: Task 对象
            gate_ids: YAML 门禁 ID 列表
            context: 可选的执行上下文

        Returns:
            (PhaseExecutionResult, list[GateResult]): 阶段结果 + 门禁结果列表
        """
        phase_result = self.execute_phase(phase, context=context)
        gate_results: list[Any] = []

        if phase_result.passed:
            for gate_id in gate_ids:
                try:
                    gr = self.execute_gate(task, gate_id)
                    gate_results.append(gr)
                except Exception as e:
                    logger.error("门禁 %s 执行失败: %s", gate_id, e)
                    raise
        else:
            logger.warning(
                "阶段 %s 未通过（overall=%s），跳过 YAML 门禁",
                phase_result.phase,
                phase_result.overall,
            )

        return phase_result, gate_results

    def get_phase_summary(self, phase: Any) -> dict[str, Any]:
        """获取阶段摘要信息（不执行检查）.

        Args:
            phase: ConstructionPhase 枚举值

        Returns:
            dict: 阶段名称、检查数量、依赖项
        """
        phase_gate = get_phase(phase)
        if phase_gate is None:
            raise ValueError(f"未知阶段: {phase}")

        return {
            "phase": phase.value if hasattr(phase, "value") else str(phase),
            "name": phase_gate.name,
            "description": phase_gate.description,
            "check_count": phase_gate.check_count,
            "dependencies": [d.value if hasattr(d, "value") else str(d) for d in phase_gate.dependencies],
        }
