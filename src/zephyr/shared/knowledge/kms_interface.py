# [BLUEPRINT] SRC-106 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.knowledge.kms_interface
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.knowledge.ke_linker
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_kms_interface | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
KMS Interface — KE 推送契约 + 生命周期关联。

依据：
    蓝图 MOD-TASK_SYSTEM §13.3 路线图 #27 + v0.6.0
    任务卡 TASK-INF-0132 (Part 4/4)

功能：
    - KE 推送格式定义
    - KE 生命周期与 TaskCard 状态关联
    - §3.2.3 接口契约
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class KERecord:
    task_id: str
    ke_type: str
    content_snippet: str
    source_file: str
    priority: str
    created_at: str
    lifecycle_phase: str = "active"


@dataclass
class TaskStateAssociation:
    task_status: str
    ke_lifecycle: str
    action: str


TASK_KE_LIFECYCLE: dict[str, str] = {
    "created": "draft",
    "locked": "draft",
    "assigned": "pending_review",
    "in_progress": "active",
    "reviewing": "active",
    "completed": "finalized",
    "failed": "archived",
}


class KMSInterface:
    PUSH_FORMAT = {
        "ke_record": {
            "task_id": "string",
            "ke_type": "insight|procedure|pattern|failure|heuristic",
            "content_snippet": "string (max 500 chars)",
            "source_file": "string",
            "priority": "P0|P1|P2",
            "lifecycle_phase": "draft|pending_review|active|finalized|archived",
        }
    }

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path("data/knowledge")
        self._push_log_path = self._data_dir / "kms_push_log.jsonl"

    def push_ke(
        self, task_id: str, ke_type: str, content_snippet: str, source_file: str = "", priority: str = "P2"
    ) -> KERecord:
        record = KERecord(
            task_id=task_id,
            ke_type=ke_type,
            content_snippet=content_snippet[:500],
            source_file=source_file,
            priority=priority,
            created_at=datetime.now(UTC).isoformat(),
            lifecycle_phase="active",
        )

        self._data_dir.mkdir(parents=True, exist_ok=True)

        with open(self._push_log_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "task_id": record.task_id,
                        "ke_type": record.ke_type,
                        "content_snippet": record.content_snippet,
                        "source_file": record.source_file,
                        "priority": record.priority,
                        "created_at": record.created_at,
                        "lifecycle_phase": record.lifecycle_phase,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )

        return record

    def update_ke_lifecycle(self, task_id: str, task_status: str) -> str:
        lifecycle = TASK_KE_LIFECYCLE.get(task_status, "draft")
        return lifecycle

    def get_task_association(self, task_status: str) -> TaskStateAssociation:
        ke_lifecycle = TASK_KE_LIFECYCLE.get(task_status, "draft")

        action_map = {
            "draft": "KE in draft mode — not yet verified",
            "pending_review": "KE pending review by Owner",
            "active": "KE active — available for AI context assembly",
            "finalized": "KE finalized — immutable",
            "archived": "KE archived — task failed/abandoned",
        }

        return TaskStateAssociation(
            task_status=task_status,
            ke_lifecycle=ke_lifecycle,
            action=action_map.get(ke_lifecycle, "Unknown"),
        )

    def get_ke_pushes_for_task(self, task_id: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        if not self._push_log_path.exists():
            return results

        try:
            for line in self._push_log_path.read_text(encoding="utf-8").strip().split("\n"):
                if not line:
                    continue
                data = json.loads(line)
                if data.get("task_id") == task_id:
                    results.append(data)
        except (json.JSONDecodeError, KeyError):
            pass

        return results

    def get_contract_spec(self) -> dict[str, Any]:
        return {
            "contract_id": "KMS-IF-001",
            "version": "0.6.0",
            "push_format": self.PUSH_FORMAT,
            "lifecycle_map": TASK_KE_LIFECYCLE,
            "max_content_length": 500,
            "supported_ke_types": ["insight", "procedure", "pattern", "failure", "heuristic"],
        }
