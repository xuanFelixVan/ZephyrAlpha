# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | CT-FLE-ORC-001
# [MODULE] zephyr.trading.orchestrator.contracts.alert_handler
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.models; zephyr.shared.__init__; zephyr.integration.shared.schema.severity_types; zephyr.integration.shared.schema.base_config; zephyr.integration.shared.schema.execution_model; zephyr.shared.contracts.task_repository_protocol; zephyr.governance.persistence.task_repo; zephyr.governance.persistence.sqlite_schema
# [CONSUMERS] zephyr.trading.feedback_loop.alert_dispatcher; zephyr.trading.work_orchestrator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] CRITICAL→P0+HIGH→P1任务; MEDIUM→不创建任务仅日志; 同 event_id 不重复创建
# [MODIFY-GUARD] CT-FLE-ORC-001 协议变更必须同步更新 feedback-loop/alert_dispatcher
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError 模块缺失; TaskCreationError 任务创建失败
# [TESTS] scripts/connect/fle_orc.py --trigger
# [A_module] module_id=MOD-ORC_alert_handler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Orc 告警接收器 — handle_alert() 消费者

CT-FLE-ORC-001: 接收 FLE 分派的 AlertEvent, 创建修复任务或阻断关联。
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol

logger = logging.getLogger(__name__)

__all__ = [
    "AlertHandler",
    "handle_alert",
]


class AlertHandler:
    def __init__(self, task_repo: TaskRepositoryProtocol | None = None) -> None:
        self._task_repo = task_repo

    def handle_alert(self, event: Any) -> Any | None:
        try:
            severity_val = _get_severity(event)
            category_val = _get_category(event)
            task_id_val = event.event_id if hasattr(event, "event_id") else str(hash(str(event)))

            if severity_val in ("MEDIUM", "LOW"):
                _record_event(task_id_val, severity_val, category_val, event)
                logger.info("[ORC-FLE] %s alert '%s' — 不创建任务", severity_val, _get_title(event)[:60])
                return None

            task = _create_repair_task(
                event_id=task_id_val,
                severity=severity_val,
                category=category_val,
                title=_get_title(event),
                detail=_get_detail(event),
                task_repo=self._task_repo,
            )
            logger.info("[ORC-FLE] %s alert → task %s created", severity_val, task.task_id)
            return task
        except Exception as exc:
            logger.error("[ORC-FLE] handle_alert 失败: %s", exc, exc_info=True)
            return None


def _get_severity(event: Any) -> str:
    if hasattr(event, "severity"):
        sv = event.severity
        return sv.value if hasattr(sv, "value") else str(sv)
    return str(getattr(event, "severity", "MEDIUM"))


def _get_category(event: Any) -> str:
    if hasattr(event, "category"):
        cat = event.category
        return cat.value if hasattr(cat, "value") else str(cat)
    return str(getattr(event, "category", "unknown"))


def _get_title(event: Any) -> str:
    return str(getattr(event, "title", "") or "FLE Alert")


def _get_detail(event: Any) -> str:
    return str(getattr(event, "detail", ""))


def _record_event(event_id: str, severity: str, category: str, event: Any) -> None:
    try:
        from zephyr.governance.persistence.sqlite_schema import get_db_connection

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO events (event_type, event_data, created_at) VALUES (?, ?, ?)",
            (
                "fle_alert",
                json.dumps(
                    {
                        "event_id": event_id,
                        "severity": severity,
                        "category": category,
                        "title": _get_title(event),
                        "detail": _get_detail(event)[:2000],
                    }
                ),
                datetime.now(UTC).isoformat(),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.debug("suppressed error in alert_handler", exc_info=True)


def _create_repair_task(
    event_id: str,
    severity: str,
    category: str,
    title: str,
    detail: str,
    task_repo: TaskRepositoryProtocol | None = None,
) -> Any:
    from zephyr.integration.shared.schema.base_config import Classification, EvolutionPolicy
    from zephyr.integration.shared.schema.execution_model import ExecutionModel
    from zephyr.integration.shared.schema.severity_types import Priority
    from zephyr.shared.foundation.models import TaskCard
    from zephyr.shared.schema.task_types import TaskNamespace, TaskStatus

    priority = Priority.P0 if severity == "CRITICAL" else Priority.P1

    import hashlib

    task_num = int(hashlib.md5(event_id.encode()).hexdigest()[:8], 16) % 100000 + 100000

    now_iso = datetime.now(UTC).isoformat()
    task = TaskCard(
        task_id=f"OPS-{task_num}",
        namespace=TaskNamespace.OPS,
        seq=task_num,
        title=f"[FLE-{severity}] {title[:150]}",
        status=TaskStatus.PENDING,
        priority=priority,
        phase=1,
        execution_model=ExecutionModel.deepseek,
        model_rationale=f"FLE 自动创建的 {severity} 修复任务",
        safety_level="L",
        classification=Classification.INTERNAL,
        evolution_policy=EvolutionPolicy.EXTENDABLE,
        estimate_hours=2.0,
        files_in_scope=["待确定（FLE 自动任务）"],
        deliverables=[f"修复 {title[:80]}"],
        acceptance=[f"alert {event_id} resolved"],
        depends_on=[],
        tags=["fle-alert", category, f"severity-{severity.lower()}"],
        session_id="system-fle-auto",
        created_at=now_iso,
        updated_at=now_iso,
        source_blueprint="MOD-MASTER_BLUEPRINT",
        source_section="CT-FLE-ORC-001",
        description=f"[FLE自动] {severity} 告警: {title[:200]}。根因: FLE detect 检测异常。治根: 自动创建修复任务。",
        upstream_files=[],
        downstream_outputs=[],
        allowed_touch=["待确定"],
        applicable_rules=[{"rule": "GOV-TASK-001", "reason": "FLE自动创建的任务遵守任务治理标准"}],
        rollback_instructions="标记任务为 CANCELLED",
        post_sync_standard=["验证告警已解除"],
        dependency_type="none" if severity != "CRITICAL" else "hard",
    )

    repo = task_repo
    if repo is None:
        from zephyr.governance.persistence.task_repo import TaskRepository

        repo = TaskRepository()
    return repo.create(task, allow_direct_create=True)


def handle_alert(event: Any) -> Any | None:
    return AlertHandler().handle_alert(event)