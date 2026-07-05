# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md
# [MODULE] zephyr.governance.semantic_audit.feedback_self_audit
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.semantic_audit.__init__
# [CONSUMERS] 见蓝图 §4 接口契约
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 蓝图 §4 文件清单与代码双向对齐
# [MODIFY-GUARD] semantic-auditor/blueprint.md; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SemanticAuditError
# [TESTS] tests/semantic-auditor/
# [A_module] module_id=MOD-GOV_feedback_self_audit | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic-auditor/blueprint.md

audit-trail.feedback_self_audit — MOD-INF-020 · 反馈自审计

============================================================

蓝图 D-020-26 · 自强化反馈环检测 + 循环依赖检测

特性

----

  - 检测自强化反馈环: Agent 行为与自身反馈形成正反馈

  - 循环依赖检测: 检测模块间循环依赖

  - 异常放大检测: 检测反馈导致的行为偏差放大

"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

_logger = logging.getLogger(__name__)


class FeedbackNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str = ""

    node_type: str = ""

    outputs_to: list[str] = Field(default_factory=list)


class SelfReinforcementResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_self_reinforcing: bool = False

    loop_nodes: list[str] = Field(default_factory=list)

    loop_length: int = 0

    amplification_factor: float = 1.0

    description: str = ""

    detected_at: str = ""


class CircularDependencyResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    has_circular: bool = False

    cycles: list[list[str]] = Field(default_factory=list)

    cycle_count: int = 0

    detected_at: str = ""


class FeedbackSelfAuditor:
    def __init__(self, amplification_threshold: float = 2.0) -> None:
        self._amplification_threshold = amplification_threshold

        self._feedback_history: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def detect_self_reinforcement(
        self,
        agent_id: str,
        feedback_events: list[dict[str, Any]],
    ) -> list[SelfReinforcementResult]:
        results: list[SelfReinforcementResult] = []

        self._feedback_history[agent_id].extend(feedback_events)

        events = self._feedback_history[agent_id]

        if len(events) < 3:
            return results

        action_scores: dict[str, list[float]] = defaultdict(list)

        for event in events:
            action = event.get("action_type", event.get("operation", ""))

            score = event.get("trust-score", event.get("confidence", 0.5))

            if action:
                action_scores[action].append(float(score))

        for action, scores in action_scores.items():
            if len(scores) < 3:
                continue

            first_third = scores[: len(scores) // 3]

            last_third = scores[-(len(scores) // 3) :]

            if not first_third or not last_third:
                continue

            avg_first = sum(first_third) / len(first_third)

            avg_last = sum(last_third) / len(last_third)

            if avg_first > 0:
                amplification = avg_last / avg_first

                if amplification >= self._amplification_threshold:
                    results.append(
                        SelfReinforcementResult(
                            is_self_reinforcing=True,
                            loop_nodes=[agent_id, action],
                            loop_length=2,
                            amplification_factor=round(amplification, 4),
                            description=(
                                f"Agent {agent_id} action '{action}' shows self-reinforcing feedback: "
                                f"score amplified {amplification:.2f}x (early={avg_first:.3f}, recent={avg_last:.3f})"
                            ),
                            detected_at=datetime.now(UTC).isoformat(),
                        )
                    )

        self_actions = set()

        for event in events:
            action = event.get("action_type", "")

            feedback_target = event.get("feedback_target", event.get("target_path", ""))

            if action and feedback_target and action == feedback_target:
                self_actions.add(action)

        for action in self_actions:
            results.append(
                SelfReinforcementResult(
                    is_self_reinforcing=True,
                    loop_nodes=[agent_id, action, agent_id],
                    loop_length=3,
                    amplification_factor=1.5,
                    description=f"Agent {agent_id} provides feedback on its own action '{action}'",
                    detected_at=datetime.now(UTC).isoformat(),
                )
            )

        if results:
            _logger.warning(
                "FeedbackSelfAuditor: detected %d self-reinforcing loops for %s",
                len(results),
                agent_id,
            )

        return results

    def check_circular(
        self,
        nodes: list[FeedbackNode] | list[dict[str, Any]],
    ) -> CircularDependencyResult:
        normalized = self._normalize_nodes(nodes)

        adjacency: dict[str, list[str]] = {}

        for node in normalized:
            adjacency[node.node_id] = node.outputs_to

        cycles = self._find_cycles(adjacency)

        result = CircularDependencyResult(
            has_circular=len(cycles) > 0,
            cycles=cycles,
            cycle_count=len(cycles),
            detected_at=datetime.now(UTC).isoformat(),
        )

        if result.has_circular:
            _logger.warning(
                "FeedbackSelfAuditor: detected %d circular dependencies: %s",
                len(cycles),
                cycles,
            )

        return result

    def _find_cycles(self, adjacency: dict[str, list[str]]) -> list[list[str]]:
        cycles: list[list[str]] = []

        visited: set[str] = set()

        rec_stack: set[str] = set()

        path: list[str] = []

        def dfs(node: str) -> None:
            visited.add(node)

            rec_stack.add(node)

            path.append(node)

            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)

                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)

                    cycle = path[cycle_start:] + [neighbor]

                    cycles.append(cycle)

            path.pop()

            rec_stack.discard(node)

        for node in adjacency:
            if node not in visited:
                dfs(node)

        return cycles

    @staticmethod
    def _normalize_nodes(
        nodes: list[FeedbackNode] | list[dict[str, Any]],
    ) -> list[FeedbackNode]:
        normalized: list[FeedbackNode] = []

        for item in nodes:
            if isinstance(item, FeedbackNode):
                normalized.append(item)

            elif isinstance(item, dict):
                normalized.append(FeedbackNode(**item))

            else:
                raise TypeError(f"Unsupported node type: {type(item)}")

        return normalized
