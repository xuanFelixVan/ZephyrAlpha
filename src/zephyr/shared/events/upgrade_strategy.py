# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.events.upgrade_strategy
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.observer
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
# [A_module] module_id=MOD-SHR_upgrade_strategy | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""EventBus 升级策略引擎

从 infrastructure_runtime_integration.event_bus_upgrade 迁移至此。
原始路径保留为 compat shim，新代码应从此处导入。

模块 ID: M-16 EventBusUpgrade（曾用名: infrastructure_runtime_integration/event_bus_upgrade.py）
# SRC-0037: 版本分叉→独立命名 — 升级策略（非事件版本化）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

__all__ = [
    "EventBusUpgrade",
    "UpgradePlan",
    "UpgradeStatus",
    "UpgradeStep",
]


class UpgradeStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class UpgradeStep:
    step_id: str
    name: str
    description: str
    status: UpgradeStatus = UpgradeStatus.PENDING
    depends_on: list[str] = field(default_factory=list)
    rollback_action: str = ""
    duration_estimate_s: float = 0.0
    started_at: str = ""
    completed_at: str = ""


@dataclass
class UpgradePlan:
    plan_id: str
    version_from: str
    version_to: str
    steps: list[UpgradeStep] = field(default_factory=list)
    total_estimated_s: float = 0.0
    generated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def is_safe(self) -> bool:
        for step in self.steps:
            if step.status in (UpgradeStatus.FAILED,):
                return False
        return True


class EventBusUpgrade:
    """事件总线升级策略

    管理事件总线从 V1（内存版）到 V2（持久化版）的升级过程：
    - 自动升级计划生成
    - 渐进式迁移（不中断服务）
    - 自动回滚机制
    - 升级后验证
    """

    _UPGRADE_STEPS: list[dict[str, Any]] = [
        {
            "step_id": "UPG-01",
            "name": "前置检查",
            "description": "验证当前系统状态是否满足升级条件",
            "depends_on": [],
            "rollback_action": "无需回滚（只读检查）",
            "duration_estimate_s": 5.0,
        },
        {
            "step_id": "UPG-02",
            "name": "备份现有事件日志",
            "description": "将当前内存事件队列转储为SQLite",
            "depends_on": ["UPG-01"],
            "rollback_action": "恢复内存备份",
            "duration_estimate_s": 10.0,
        },
        {
            "step_id": "UPG-03",
            "name": "初始化持久化存储",
            "description": "创建SQLite EventStore并建立索引",
            "depends_on": ["UPG-02"],
            "rollback_action": "删除SQLite数据库",
            "duration_estimate_s": 3.0,
        },
        {
            "step_id": "UPG-04",
            "name": "双写模式开启",
            "description": "新事件同时写入内存和SQLite（过渡态）",
            "depends_on": ["UPG-03"],
            "rollback_action": "关闭双写，仅保留内存",
            "duration_estimate_s": 1.0,
        },
        {
            "step_id": "UPG-05",
            "name": "验证双写一致性",
            "description": "对比内存与SQLite事件是否一致",
            "depends_on": ["UPG-04"],
            "rollback_action": "停止双写",
            "duration_estimate_s": 15.0,
        },
        {
            "step_id": "UPG-06",
            "name": "切换为主SQLite模式",
            "description": "关闭内存写入，完全由SQLite承载",
            "depends_on": ["UPG-05"],
            "rollback_action": "恢复双写模式",
            "duration_estimate_s": 2.0,
        },
        {
            "step_id": "UPG-07",
            "name": "清理内存队列",
            "description": "安全删除旧的内存事件队列（可选）",
            "depends_on": ["UPG-06"],
            "rollback_action": "从SQLite恢复内存队列",
            "duration_estimate_s": 5.0,
        },
        {
            "step_id": "UPG-08",
            "name": "升级后验证",
            "description": "全量检查升级后系统正常运行",
            "depends_on": ["UPG-07"],
            "rollback_action": "整体回滚到V1",
            "duration_estimate_s": 10.0,
        },
    ]

    def __init__(self):
        self._upgrade_history: list[UpgradePlan] = []

    def generate_upgrade_plan(
        self,
        version_from: str = "v1.0.0",
        version_to: str = "v2.0.0",
    ) -> UpgradePlan:
        steps = [UpgradeStep(**s) for s in self._UPGRADE_STEPS]
        total = sum(s.duration_estimate_s for s in steps)

        plan = UpgradePlan(
            plan_id=f"UP-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
            version_from=version_from,
            version_to=version_to,
            steps=steps,
            total_estimated_s=round(total, 1),
        )
        return plan

    def execute_upgrade(
        self,
        plan: UpgradePlan,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        result: dict[str, Any] = {
            "plan_id": plan.plan_id,
            "dry_run": dry_run,
            "steps_completed": 0,
            "steps_failed": 0,
            "status": "completed" if dry_run else "pending",
            "details": [],
        }

        for step in plan.steps:
            if dry_run:
                step.status = UpgradeStatus.COMPLETED
                result["steps_completed"] += 1
                result["details"].append(
                    {
                        "step": step.step_id,
                        "name": step.name,
                        "status": "dry_run_passed",
                        "would_rollback": step.rollback_action,
                    }
                )
            else:
                try:
                    step.status = UpgradeStatus.IN_PROGRESS
                    step.started_at = datetime.now(UTC).isoformat()
                    self._execute_step(step)
                    step.status = UpgradeStatus.COMPLETED
                    step.completed_at = datetime.now(UTC).isoformat()
                    result["steps_completed"] += 1
                except Exception as e:
                    step.status = UpgradeStatus.FAILED
                    result["steps_failed"] += 1
                    result["details"].append(
                        {
                            "step": step.step_id,
                            "name": step.name,
                            "status": "failed",
                            "error": str(e),
                            "rollback": step.rollback_action,
                        }
                    )

                    for prev_step in reversed(plan.steps):
                        if prev_step.status != UpgradeStatus.COMPLETED:
                            continue
                        try:
                            self._rollback_step(prev_step)
                            prev_step.status = UpgradeStatus.ROLLED_BACK
                        except Exception as re:
                            result["details"].append(
                                {
                                    "rollback_error": f"{prev_step.step_id}: {re}",
                                }
                            )
                    break

        self._upgrade_history.append(plan)
        return result

    def _execute_step(self, step: UpgradeStep) -> None:
        if step.step_id == "UPG-01":
            pass

    def _rollback_step(self, step: UpgradeStep) -> None:
        pass

    def get_history(self) -> list[UpgradePlan]:
        return self._upgrade_history

    def validate_current_state(self) -> dict[str, Any]:
        import importlib.util

        result: dict[str, Any] = {
            "event_bus_type": "shared.observer",
            "is_upgraded": False,
            "issues": [],
        }

        # Use importlib.util.find_spec to avoid shared->infrastructure circular import
        if importlib.util.find_spec("zephyr.infrastructure.event_store") is not None:
            result["event_store_available"] = True
        else:
            result["event_store_available"] = False
            result["issues"].append("EventStore 不可用——升级未完成")

        try:
            from zephyr.shared.events.observer import Observer as ObserverAlias

            result["event_bus_available"] = True
        except ImportError:
            result["event_bus_available"] = False
            result["issues"].append("共享事件总线不可用")

        return result
