# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md
# [MODULE] zephyr.governance.kb.kb_gate_task
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.__init__; zephyr.integration.shared.schema.severity_types
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_kb_gate_task | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""KB 五阶段门禁 evaluate 用的最小合法 Task（对齐  / tasks 表）。"""

from datetime import UTC, datetime
from pathlib import Path

from zephyr.integration.shared.schema.severity_types import SafetyLevel
from zephyr.shared.schema.task_types import TaskCard, TaskNamespace, TaskStatus, normalize_execution_model

# 与 KB 流水线文档任务链隔离的专用 seq，避免与真实 tasks 表主键碰撞概率
_GATE_SEQ: dict[str, tuple[TaskNamespace, int]] = {
    "G1": (TaskNamespace.KBG, 9101),
    "G2": (TaskNamespace.KBG, 9102),
    "G3": (TaskNamespace.KBG, 9103),
    "G4": (TaskNamespace.KBG, 9104),
    "G5": (TaskNamespace.KBG, 9105),
}


def build_kb_gate_eval_task(*, gate_id: str, title: str, deliverable: Path) -> TaskCard:
    """构造 ``GateEngine.evaluate(task, gate_id)`` 所需的最小 TaskCard。"""
    ns, seq = _GATE_SEQ[gate_id]
    now = datetime.now(UTC)
    return TaskCard(
        task_id=f"{ns.value}-{seq}",
        namespace=ns,
        seq=seq,
        title=title,
        phase=2,
        status=TaskStatus.IN_PROGRESS,
        execution_model=normalize_execution_model("system"),
        safety_level=SafetyLevel.M,
        source_blueprint="KB-GATE",
        source_section=gate_id,
        description=f"KB 门禁 {gate_id} 评估任务: {title}",
        deliverables=[str(deliverable)],
        created_at=now,
        updated_at=now,
    )
