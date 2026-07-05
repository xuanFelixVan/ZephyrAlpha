# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_durable
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
# [A_module] module_id=MOD-ORC_skill_durable | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Durable Execution
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 持久化执行引擎
====================
确保 Skill 执行不丢失:
  1. Checkpointing: 执行关键步骤前自动打检查点
  2. ResumeFrom: 中断后从最近的检查点恢复
  3. StateSerialization: 执行状态序列化为 JSON
  4. ProgressTracking: 追踪执行进度
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class DurableExecution:
    """Skill 持久化执行器"""

    def __init__(self, storage_dir: Path | None = None):
        self._storage_dir = storage_dir or (Path(__file__).resolve().parent / "_durable_state")
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._checkpoints: dict[str, list[dict[str, Any]]] = {}
        self._active_executions: dict[str, dict[str, Any]] = {}

    def start(self, skill_id: str, operation: str, input_context: str | None = None) -> str:
        execution_id = f"{skill_id}:{operation}:{datetime.now(UTC).timestamp()}"

        self._active_executions[execution_id] = {
            "execution_id": execution_id,
            "skill_id": skill_id,
            "operation": operation,
            "status": "running",
            "progress": 0.0,
            "started_at": datetime.now(UTC),
            "input_context": input_context[:500] if input_context else "",
        }

        self._checkpoint(skill_id, execution_id, "started")

        return execution_id

    def _checkpoint(self, skill_id: str, execution_id: str, stage: str):
        data = {
            "stage": stage,
            "timestamp": datetime.now(UTC).isoformat(),
            "execution_id": execution_id,
        }

        if execution_id in self._active_executions:
            active = self._active_executions[execution_id]
            data.update(
                {
                    "skill_id": active["skill_id"],
                    "operation": active["operation"],
                    "progress": active["progress"],
                }
            )

        self._checkpoints.setdefault(skill_id, []).append(data)

        file_path = self._storage_dir / f"{execution_id}.json"
        try:
            file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass

    def advance(self, execution_id: str, checkpoint_stage: str, progress: float):
        pct = max(0.0, min(100.0, progress))
        if execution_id in self._active_executions:
            self._active_executions[execution_id]["progress"] = pct
        self._checkpoint(
            self._active_executions.get(execution_id, {}).get("skill_id", "?"),
            execution_id,
            checkpoint_stage,
        )

    def complete(self, execution_id: str, output_preview: str = ""):
        if execution_id in self._active_executions:
            self._active_executions[execution_id]["status"] = "completed"
            self._active_executions[execution_id]["completed_at"] = datetime.now(UTC)
            self._active_executions[execution_id]["progress"] = 100.0

        skill_id = self._active_executions.get(execution_id, {}).get("skill_id", "?")
        self._checkpoint(skill_id, execution_id, "completed")

    def fail(self, execution_id: str, error: str):
        if execution_id in self._active_executions:
            self._active_executions[execution_id]["status"] = "failed"
            self._active_executions[execution_id]["error"] = error[:500]

        skill_id = self._active_executions.get(execution_id, {}).get("skill_id", "?")
        self._checkpoint(skill_id, execution_id, f"failed: {error[:100]}")

    def resume(self, execution_id: str) -> dict[str, Any]:
        file_path = self._storage_dir / f"{execution_id}.json"
        if file_path.exists():
            data = json.loads(file_path.read_text(encoding="utf-8"))
            skill_id = data.get("skill_id", "?")

            self._active_executions[execution_id] = {
                "execution_id": execution_id,
                "skill_id": skill_id,
                "status": "resuming",
                "resumed_at": datetime.now(UTC),
                "previous_stage": data.get("stage", "unknown"),
                "previous_progress": data.get("progress", 0.0),
            }

            return {
                "execution_id": execution_id,
                "skill_id": skill_id,
                "resumed_at": datetime.now(UTC).isoformat(),
                "previous_stage": data.get("stage"),
                "checkpoints": len(self._checkpoints.get(skill_id, [])),
            }

        return {
            "execution_id": execution_id,
            "resumed_at": 0.0,
            "status": "not_found",
        }

    def get_status(self, execution_id: str) -> dict[str, Any]:
        if execution_id in self._active_executions:
            active = self._active_executions[execution_id]
            return {
                "execution_id": execution_id,
                "skill_id": active["skill_id"],
                "status": active["status"],
                "progress": active["progress"],
                "elapsed": (
                    (datetime.now(UTC) - active["started_at"]).total_seconds()
                    if isinstance(active["started_at"], datetime)
                    else 0
                ),
            }

        return {"execution_id": execution_id, "status": "unknown"}
