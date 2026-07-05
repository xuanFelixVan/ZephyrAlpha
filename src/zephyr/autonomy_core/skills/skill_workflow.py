# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_workflow
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_skill_workflow | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Workflow Orchestrator
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

多 Skill 工作流编排引擎
=======================
机制:
  1. WorkflowDefinition: 定义多 Skill 串行/并行执行的 DAG
  2. DependencyResolution: 解析 Skill 间依赖拓扑排序
  3. ParallelExecution: 无依赖 Skill 并行加载
  4. Aggregation: 合并多 Skill 输出
"""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Any


class SkillWorkflow:
    """多 Skill 工作流编排器"""

    def __init__(self):
        self._workflows: dict[str, dict[str, Any]] = {}
        self._executions: dict[str, dict[str, Any]] = {}

    def define(
        self,
        workflow_id: str,
        skills: list[str],
        dependencies: dict[str, list[str]] | None = None,
        parallel_groups: list[list[str]] | None = None,
    ) -> dict[str, Any]:
        deps = dependencies or {}

        adj: dict[str, list[str]] = defaultdict(list)
        indegree: dict[str, int] = defaultdict(int)

        for sid in skills:
            indegree[sid] = indegree.get(sid, 0)

        for sid, prereqs in deps.items():
            for p in prereqs:
                adj[p].append(sid)
                indegree[sid] = indegree.get(sid, 0) + 1

        topo: list[str] = []
        queue = [s for s in skills if indegree.get(s, 0) == 0]

        while queue:
            node = queue.pop(0)
            topo.append(node)
            for neighbor in adj.get(node, []):
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    queue.append(neighbor)

        if len(topo) != len(skills):
            cycle = [s for s in skills if indegree.get(s, 0) > 0]
            return {
                "workflow_id": workflow_id,
                "status": "invalid",
                "error": "dependency_cycle_detected",
                "cycle_skills": cycle,
            }

        levels: list[list[str]] = []
        if parallel_groups:
            levels = parallel_groups
        else:
            indegree_level = defaultdict(int)
            for sid, prereqs in deps.items():
                indegree_level[sid] = max(0, len(prereqs))
            while skills:
                level = [s for s in skills if indegree_level.get(s, 0) == 0]
                if not level:
                    break
                levels.append(level)
                for s in level:
                    skills.remove(s)
                    for neighbor in adj.get(s, []):
                        indegree_level[neighbor] -= 1

        self._workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "skills": skills,
            "dependencies": deps,
            "topological_order": topo,
            "parallel_levels": levels,
            "defined_at": datetime.now(UTC).isoformat(),
        }

        return {
            "workflow_id": workflow_id,
            "status": "defined",
            "skill_count": len(skills),
            "topological_order": topo,
            "parallel_levels": levels,
            "parallelism": max(len(l) for l in levels) if levels else 1,
        }

    def execute(
        self,
        workflow_id: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        wf = self._workflows.get(workflow_id)
        if not wf:
            return {
                "workflow_id": workflow_id,
                "status": "not_found",
            }

        results: dict[str, dict[str, Any]] = {}
        errors: dict[str, str] = {}

        for skill_id in wf["topological_order"]:
            try:
                from zephyr.autonomy_core.skills.skill_loader import SkillLoader

                loader = SkillLoader()
                loaded = loader.progressive_load(skill_id)

                results[skill_id] = {
                    "status": "loaded",
                    "l1": loaded.get("l1"),
                    "token_count": loaded.get("token_count_l2"),
                }
            except Exception as e:
                errors[skill_id] = str(e)
                results[skill_id] = {"status": "failed", "error": str(e)}

        execution_id = f"exec:{workflow_id}:{datetime.now(UTC).timestamp()}"
        self._executions[execution_id] = {
            "workflow_id": workflow_id,
            "results": results,
            "errors": errors,
            "executed_at": datetime.now(UTC).isoformat(),
        }

        all_ok = len(errors) == 0

        return {
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "status": "completed" if all_ok else "partial",
            "results": {k: v.get("status", "?") for k, v in results.items()},
            "errors": errors,
            "skill_count": len(results),
            "success_count": len(results) - len(errors),
            "error_count": len(errors),
        }
