# [BLUEPRINT] MOD-INF-005 | scripts/construction/d_init_task_system.py | §
# [MODULE] scripts.construction.d_init_task_system
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.persistence.sqlite_schema; zephyr.governance.persistence.task_repo; zephyr.shared.models; zephyr.integration.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
初始化任务系统数据库 + 创建任务系统自身的施工任务卡（吃狗粮）
===========================================================
对应蓝图：MOD-TASK_SYSTEM (infrastructure_runtime_integration/task-system)
施工进度：phase_1_complete → 建立剩余任务的 TaskCard
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.integration.schema.schemas import TaskNamespace, TaskStatus

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.governance.persistence.task_repo import TaskRepository
from zephyr.shared.foundation.models import TaskCard

init_db()
repo = TaskRepository()

now_dt = datetime.now(UTC)


def make(cfg: dict) -> TaskCard:
    fields = {
        "task_id": cfg["task_id"],
        "namespace": cfg["namespace"],
        "seq": cfg["seq"],
        "title": cfg["title"],
        "status": cfg["status"],
        "priority": cfg["priority"],
        "phase": cfg["phase"],
        "execution_model": cfg["execution_model"],
        "safety_level": cfg["safety_level"],
        "source_blueprint": cfg["source_blueprint"],
        "source_section": cfg["source_section"],
        "description": cfg["description"],
        "directive": cfg.get("directive", ""),
        "idempotent": cfg.get("idempotent", True),
        "classification": cfg.get("classification", "internal"),
        "evolution_policy": cfg.get("evolution_policy", "extendable"),
        "estimate_hours": cfg.get("estimate_hours", 1.0),
        "actual_hours": 0.0,
        "files_in_scope": cfg.get("files_in_scope", []),
        "deliverables": cfg.get("deliverables", []),
        "acceptance": cfg.get("acceptance", []),
        "depends_on": cfg.get("depends_on", []),
        "tags": cfg.get("tags", []),
        "session_id": None,
        "waiting_for": None,
        "ready_at": None,
        "completed_at": None,
        "model_rationale": "DeepSeek V4 Pro — 主力生产模型",
        "fallback_model": "claude",
        "upstream_files": cfg.get("upstream_files", []),
        "downstream_outputs": cfg.get("downstream_outputs", []),
        "allowed_touch": cfg.get("allowed_touch", []),
        "forbidden_touch": cfg.get("forbidden_touch", []),
        "applicable_rules": cfg.get("applicable_rules", []),
        "context_assembly_manifest": cfg.get("context_assembly_manifest", []),
        "rollback_instructions": cfg.get("rollback_instructions", ""),
        "estimated_tokens": cfg.get("estimated_tokens", 8000),
        "timeout_minutes": cfg.get("timeout_minutes", 30),
        "assigned_pipeline": cfg.get("assigned_pipeline", "A"),
        "created_at": now_dt,
        "updated_at": now_dt,
        "is_deleted": 0,
        "deleted_at": None,
        "schema_version": "",
    }
    return TaskCard(**fields)


specs = [
    # ====== P0: 任务聚合与视图（直接服务于 all-construction 工作流）====== #
    {
        "task_id": "OPS-001",
        "namespace": TaskNamespace.OPS,
        "seq": 1,
        "title": "[任务系统-聚合] 实现 task_repo.list_by_phase() 方法",
        "status": TaskStatus.PENDING,
        "priority": "P0",
        "phase": 2,
        "execution_model": "deepseek",
        "safety_level": "L",
        "source_blueprint": "MOD-TASK_SYSTEM",
        "source_section": "盲点#28 / §13.3",
        "description": (
            "TaskRepository 缺少 list_by_phase(phase: int) 方法。"
            "Dashboard 的 fetch_task_progress() 已写好调用代码，但 repo 侧是空壳。"
            "需要添加 SQL: SELECT * FROM tasks WHERE phase=? ORDER BY priority DESC, seq ASC。"
        ),
        "files_in_scope": ["src/zephyr/db/task_repo.py"],
        "estimate_hours": 0.5,
        "allowed_touch": ["src/zephyr/db/task_repo.py"],
        "upstream_files": [
            "src/zephyr/db/task_repo.py",
            "docs/03_modules/infrastructure_runtime_integration/task-system/blueprint.md",
        ],
        "downstream_outputs": [
            {"path": "src/zephyr/db/task_repo.py", "description": "新增 list_by_phase() 方法"},
        ],
        "directive": "TaskRepository.list_by_phase(phase: int) -> list[TaskCard]: SELECT FROM tasks WHERE phase=?",
        "tags": ["task-system", "aggregation", "dashboard"],
    },
    {
        "task_id": "OPS-002",
        "namespace": TaskNamespace.OPS,
        "seq": 2,
        "title": "[任务系统-聚合] 实现父子任务状态自动聚合逻辑",
        "status": TaskStatus.PENDING,
        "priority": "P0",
        "phase": 2,
        "execution_model": "deepseek",
        "safety_level": "L",
        "source_blueprint": "MOD-TASK_SYSTEM",
        "source_section": "盲点#1 / §3.2.3",
        "description": (
            "TaskCard.parent_task_id 已定义，但父任务状态不会自动从子任务推导。"
            "在 task_repo.transition() 中添加 _derive_parent_status()："
            "子任务全COMPLETED→父COMPLETED；任一FAILED→父BLOCKED。"
        ),
        "files_in_scope": ["src/zephyr/db/task_repo.py"],
        "estimate_hours": 1.0,
        "allowed_touch": ["src/zephyr/db/task_repo.py"],
        "upstream_files": [
            "src/zephyr/db/task_repo.py",
            "docs/03_modules/infrastructure_runtime_integration/task-system/blueprint.md",
        ],
        "downstream_outputs": [
            {
                "path": "src/zephyr/db/task_repo.py",
                "description": "transition() 中添加 _derive_parent_status()",
            },
        ],
        "directive": "transition() 末尾加 _derive_parent_status(new_status, child_task_id)，查询子任务聚合父任务",
        "tags": ["task-system", "aggregation", "parent-task"],
    },
    {
        "task_id": "OPS-003",
        "namespace": TaskNamespace.OPS,
        "seq": 3,
        "title": "[任务系统-聚合] 构建 CLI 全局任务摘要 zalpha task summary",
        "status": TaskStatus.PENDING,
        "priority": "P0",
        "phase": 2,
        "execution_model": "deepseek",
        "safety_level": "L",
        "source_blueprint": "MOD-TASK_SYSTEM",
        "source_section": "盲点#28 / §13.3",
        "description": (
            "单一 CLI 入口查看全部任务进度。"
            "zalpha task summary [--by-epic] [--by-phase] [--by-status]"
            "输出：全局统计 + Epic分组 + Phase分组 + 状态分布。"
            "新建：scripts/governance/task_summary.py"
        ),
        "files_in_scope": ["scripts/governance/task_summary.py"],
        "estimate_hours": 1.5,
        "allowed_touch": [
            "scripts/governance/task_summary.py",
            "src/zephyr/db/task_repo.py",
        ],
        "upstream_files": [
            "src/zephyr/db/task_repo.py",
            "src/zephyr/db/sqlite_schema.py",
            "scripts/governance/status.py",
            "docs/03_modules/infrastructure_runtime_integration/task-system/blueprint.md",
        ],
        "downstream_outputs": [
            {"path": "scripts/governance/task_summary.py", "description": "zalpha task summary CLI"},
        ],
        "directive": "创建 task_summary.py——读取SQLite tasks表，格式化输出全局摘要（epic/phase/status透视）",
        "tags": ["task-system", "aggregation", "CLI", "epic"],
    },
    {
        "task_id": "OPS-004",
        "namespace": TaskNamespace.OPS,
        "seq": 4,
        "title": "[任务系统-仪表盘] Dashboard task_progress 接入 SQLite 真数据",
        "status": TaskStatus.PENDING,
        "priority": "P0",
        "phase": 2,
        "execution_model": "deepseek",
        "safety_level": "L",
        "source_blueprint": "MOD-TASK_SYSTEM",
        "source_section": "盲点#28 / D_FRONTEND融合",
        "description": (
            "D_FRONTEND dashboard 的 task_progress.py 是桩实现。"
            "OPS-001 补齐 repo 后，本任务接入真数据："
            "1. 确认 list_by_phase() 可用 2. 填充真数据 3. 输出 Phase 进度条"
        ),
        "files_in_scope": ["src/zephyr/frontend/dashboard/components/task_progress.py"],
        "depends_on": ["OPS-001"],
        "estimate_hours": 1.0,
        "allowed_touch": [
            "src/zephyr/frontend/dashboard/components/task_progress.py",
        ],
        "upstream_files": [
            "src/zephyr/db/task_repo.py",
            "src/zephyr/frontend/dashboard/components/task_progress.py",
            "docs/03_modules/infrastructure_runtime_integration/task-system/blueprint.md",
        ],
        "downstream_outputs": [
            {
                "path": "src/zephyr/frontend/dashboard/components/task_progress.py",
                "description": "task_progress 接入真数据",
            },
        ],
        "directive": "fetch_task_progress() 从桩→真：调用 task_repo.list_by_phase()，输出 Phase 进度条",
        "tags": ["task-system", "dashboard", "progress"],
    },
    # ====== P1: 基础设施补齐 ====== #
    {
        "task_id": "OPS-005",
        "namespace": TaskNamespace.OPS,
        "seq": 5,
        "title": "[任务系统-钩子] 实现 EventHook 声明式注册系统",
        "status": TaskStatus.PENDING,
        "priority": "P1",
        "phase": 2,
        "execution_model": "deepseek",
        "safety_level": "L",
        "source_blueprint": "MOD-TASK_SYSTEM",
        "source_section": "盲点#4 / §13.3",
        "description": (
            "盲点#4：状态变更后需 EventHook。"
            "HookRegistry — 全局 dict + transition() 中 _fire_hooks()。"
            "新建：src/zephyr/hooks/event_hook.py。内部事件总线。"
        ),
        "files_in_scope": ["src/zephyr/hooks/event_hook.py", "src/zephyr/db/task_repo.py"],
        "estimate_hours": 1.5,
        "upstream_files": [
            "src/zephyr/db/task_repo.py",
            "src/zephyr/db/sqlite_schema.py",
            "docs/03_modules/infrastructure_runtime_integration/task-system/blueprint.md",
        ],
        "downstream_outputs": [
            {"path": "src/zephyr/hooks/__init__.py", "description": "hooks包"},
            {"path": "src/zephyr/hooks/event_hook.py", "description": "EventHook"},
        ],
        "directive": "创建 src/zephyr/hooks/，HookRegistry(register/unregister + _fire)，transition() 中调用",
        "tags": ["task-system", "hooks", "event"],
    },
    {
        "task_id": "OPS-006",
        "namespace": TaskNamespace.OPS,
        "seq": 6,
        "title": "[任务系统-队列] 实现 ActiveTaskQueue 后台轮询器",
        "status": TaskStatus.PENDING,
        "priority": "P1",
        "phase": 2,
        "execution_model": "deepseek",
        "safety_level": "M",
        "source_blueprint": "MOD-TASK_SYSTEM",
        "source_section": "盲点#9 / §13.3",
        "description": (
            "盲点#9：ActiveTaskQueue — 后台线程扫描 READY 任务，"
            "自动 READY→IN_PROGRESS → dispatch PipelineOrchestrator。"
            "threading.Thread + sleep(4) 轮询。CLI: zalpha task queue start|stop|status。"
            "新建：src/zephyr/orchestrator/task_queue.py"
        ),
        "files_in_scope": ["src/zephyr/orchestrator/task_queue.py"],
        "estimate_hours": 2.0,
        "upstream_files": [
            "src/zephyr/db/task_repo.py",
            "src/zephyr/pipeline/pipeline_orchestrator.py",
            "docs/03_modules/infrastructure_runtime_integration/task-system/blueprint.md",
        ],
        "downstream_outputs": [
            {"path": "src/zephyr/orchestrator/task_queue.py", "description": "ActiveTaskQueue"},
        ],
        "directive": "ActiveTaskQueue — threading.Thread 定期 scan + dispatch，zalpha task queue start",
        "tags": ["task-system", "queue", "dispatch"],
        "idempotent": False,
    },
    {
        "task_id": "OPS-007",
        "namespace": TaskNamespace.OPS,
        "seq": 7,
        "title": "[任务系统-拆卡] 补齐 BlueprintDecomposer 通用格式支持",
        "status": TaskStatus.PENDING,
        "priority": "P1",
        "phase": 2,
        "execution_model": "deepseek",
        "safety_level": "L",
        "source_blueprint": "MOD-TASK_SYSTEM",
        "source_section": "对全蓝图的自动拆卡流水线",
        "description": (
            "decompose_blueprint() 依赖特定格式（- [XXX-N] Module —），"
            "大多蓝图用不同 §11 格式。加后备正则 + topology_sort + depends_on 自动推导。"
        ),
        "files_in_scope": ["src/zephyr/core/blueprint_decomposer.py"],
        "estimate_hours": 1.0,
        "allowed_touch": ["src/zephyr/core/blueprint_decomposer.py"],
        "upstream_files": [
            "src/zephyr/core/blueprint_decomposer.py",
            "docs/03_modules/infrastructure_runtime_integration/task-system/blueprint.md",
        ],
        "downstream_outputs": [
            {
                "path": "src/zephyr/core/blueprint_decomposer.py",
                "description": "BlueprintDecomposer 通用格式",
            },
        ],
        "directive": "补齐后备模式+topology_sort+depends_on，写入 task_repo+.md",
        "tags": ["task-system", "decomposer", "CLI"],
    },
    # ====== P2: 系统健壮性 ====== #
    {
        "task_id": "OPS-008",
        "namespace": TaskNamespace.OPS,
        "seq": 8,
        "title": "[任务系统-治理] 补齐 FailurePatternMatcher 失败模式匹配引擎",
        "status": TaskStatus.PENDING,
        "priority": "P2",
        "phase": 3,
        "execution_model": "deepseek",
        "safety_level": "L",
        "source_blueprint": "MOD-TASK_SYSTEM",
        "source_section": "盲点#22 / §13.3",
        "description": (
            "盲点#22：FailurePatternMatcher 识别常见失败模式"
            "（死循环/多模块失败/上下文不足），自动建议纠正。"
            "通过 EventHook 订阅 FAILED。新建：src/zephyr/orchestrator/failure_matcher.py"
        ),
        "files_in_scope": ["src/zephyr/orchestrator/failure_matcher.py"],
        "depends_on": ["OPS-005"],
        "estimate_hours": 1.5,
        "allowed_touch": ["src/zephyr/orchestrator/failure_matcher.py"],
        "upstream_files": [
            "src/zephyr/hooks/event_hook.py",
            "docs/03_modules/infrastructure_runtime_integration/task-system/blueprint.md",
        ],
        "downstream_outputs": [
            {
                "path": "src/zephyr/orchestrator/failure_matcher.py",
                "description": "FailurePatternMatcher",
            },
        ],
        "directive": "FailurePatternMatcher——模式匹配+纠正建议，通过 EventHook 订阅 FAILED",
        "tags": ["task-system", "failure-matcher", "governance"],
    },
    {
        "task_id": "OPS-009",
        "namespace": TaskNamespace.OPS,
        "seq": 9,
        "title": "[任务系统-诊断] 实现任务系统自身健康检查",
        "status": TaskStatus.PENDING,
        "priority": "P2",
        "phase": 3,
        "execution_model": "deepseek",
        "safety_level": "L",
        "source_blueprint": "MOD-TASK_SYSTEM",
        "source_section": "盲点#31 / §13.3",
        "description": ("盲点#31：SQLite完整性+Hook链+Schema版本自检。zalpha task self-check [--repair]"),
        "files_in_scope": ["scripts/governance/"],
        "depends_on": ["OPS-005"],
        "estimate_hours": 1.0,
        "allowed_touch": ["scripts/governance/"],
        "upstream_files": [
            "src/zephyr/db/task_repo.py",
            "src/zephyr/db/sqlite_schema.py",
            "src/zephyr/hooks/event_hook.py",
            "docs/03_modules/infrastructure_runtime_integration/task-system/blueprint.md",
        ],
        "downstream_outputs": [
            {"path": "scripts/governance/task_self_check.py", "description": "任务系统健康检查"},
        ],
        "directive": "zalpha task self-check [--repair] — SQLite完整性+Hook链+Schema版本自检",
        "tags": ["task-system", "self-diagnosis", "governance"],
    },
]

created: list[str] = []
for cfg in specs:
    try:
        card = make(cfg)
        repo.create(card)
        created.append(card.task_id)
    except Exception as exc:
        print(f"  SKIP {cfg['task_id']}: {exc}")

print(f"\nCreated {len(created)}/{len(specs)} task cards:")
for tid in created:
    card = repo.get(tid)
    print(f"  ✅ {tid} [{card.status.value}] {card.priority} — {card.title}")
