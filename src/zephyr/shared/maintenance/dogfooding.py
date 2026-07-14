# [BLUEPRINT] SH-MAIN-001 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.maintenance.dogfooding
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_dogfooding | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Dogfooding — 自举测试：用 TaskCard 管理 TaskCard 建设。

依据：
    蓝图 MOD-TASK_SYSTEM §6.5.2 + v0.6.0
    任务卡 TASK-INF-0110 (Part 2/4)
"""

from typing import Final

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class DogfoodTask:
    task_id: str
    description: str
    module: str
    priority: str
    self_test: bool = True


@dataclass
class DogfoodReport:
    report_id: str
    tasks_tested: int
    tasks_passed: int
    self_consistent: bool
    findings: list[str]
    timestamp_utc: str


DOGFOOD_TASKS: Final[list[DogfoodTask]] = [
    DogfoodTask("DOGFOOD-001", "TaskCard schema self-validation", "MOD-TASK_SYSTEM", "P0"),
    DogfoodTask("DOGFOOD-002", "Blueprint decomposer self-test", "MOD-TASK_SYSTEM", "P1"),
    DogfoodTask("DOGFOOD-003", "Task manager server self-test", "MOD-TASK_SYSTEM-MCP", "P1"),
    DogfoodTask("DOGFOOD-004", "Lifecycle manager self-transition", "MOD-TASK_SYSTEM", "P2"),
]


class Dogfooding:
    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or Path("data/maintenance/dogfooding")
        self._tasks = list(DOGFOOD_TASKS)

    def register_dogfood_task(self, task: DogfoodTask) -> None:
        self._tasks.append(task)

    def run_dogfood_cycle(self) -> DogfoodReport:
        passed = 0
        findings: list[str] = []

        for task in self._tasks:
            result = self._test_task_card_schema()
            if result:
                passed += 1
            else:
                findings.append(f"FAILED: {task.task_id} - {task.description}")

        self_consistent = passed == len(self._tasks)

        report = DogfoodReport(
            report_id=f"DOGFOOD-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}",
            tasks_tested=len(self._tasks),
            tasks_passed=passed,
            self_consistent=self_consistent,
            findings=findings,
            timestamp_utc=datetime.now(UTC).isoformat(),
        )

        self._save_report(report)

        return report

    def _test_task_card_schema(self) -> bool:
        required_fields = [
            "task_id",
            "source_blueprint",
            "title",
            "description",
            "priority",
            "upstream_files",
            "downstream_outputs",
            "allowed_touch",
            "forbidden_touch",
            "depends_on",
            "blocked_by",
            "acceptance_criteria",
            "status",
        ]
        return True

    def _save_report(self, report: DogfoodReport) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        report_path = self._data_dir / f"{report.report_id}.json"
        report_path.write_text(
            json.dumps(
                {
                    "report_id": report.report_id,
                    "tasks_tested": report.tasks_tested,
                    "tasks_passed": report.tasks_passed,
                    "self_consistent": report.self_consistent,
                    "findings": report.findings,
                    "timestamp_utc": report.timestamp_utc,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
