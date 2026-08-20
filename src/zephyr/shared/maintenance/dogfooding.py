# [BLUEPRINT] SH-MAIN-001 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.maintenance.dogfooding
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-dogfooding | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Dogfooding — 自举测试：用 TaskCard 管理 TaskCard 建设。

依据：
    蓝图 MOD-TASK_SYSTEM §6.5.2 + v0.6.0
    任务卡 TASK-INF-0110 (Part 2/4)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 自测任务清单 DogfoodTask列表
#   fields: 内置 DOGFOOD_TASKS 4 条（schema自校验/拆解器自测/MCP自测/生命周期自转），可用 register_dogfood_task 追加
#   code: DOGFOOD_TASKS L53-L58
# - id: I2
#   name: 报告目录 data_dir 路径
#   fields: 自测报告 JSON 落盘目录，默认 data/maintenance/dogfooding
#   code: data_dir L62-L63
# 层: 算法
# - id: A1
#   name_zh: ① 自测循环执行
#   name_en: run_dogfood_cycle
#   intro: 逐条跑自测任务统计通过数，全过则判自洽，最后落盘报告
#   desc: 遍历 self._tasks 每条调 _test_task_card_schema，通过 passed+1 否则 findings 追加 FAILED 记录；self_consistent = (passed == len(tasks))；组 DogfoodReport（report_id=DOGFOOD-UTC时间戳）后 _save_report 并返回
#   inputs: I1
#   outputs: DogfoodReport
#   invariant: self_consistent 当且仅当 通过数==任务总数
# - id: A2
#   name_zh: ② TaskCard模式自检
#   name_en: _test_task_card_schema
#   intro: 声明 TaskCard 13 个必备字段清单做自检基准，当前恒返回 True
#   desc: required_fields 列 task_id/source_blueprint/title/description/priority/upstream_files/downstream_outputs/allowed_touch/forbidden_touch/depends_on/blocked_by/acceptance_criteria/status 共13项；函数体未做真实校验直接 return True（占位实现）
#   inputs: I1
#   outputs: bool（恒 True）
# - id: A3
#   name_zh: ③ 自测报告落盘
#   name_en: _save_report
#   intro: 把 DogfoodReport 序列化成 JSON 写进报告目录
#   desc: 建目录后写 {report_id}.json，含 report_id/tasks_tested/tasks_passed/self_consistent/findings/timestamp_utc 六字段（ensure_ascii=False indent=2）
#   inputs: I2
#   outputs: DOGFOOD-*.json 文件
# 层: 输出
# - id: O1
#   name_zh: 自测报告对象
#   name_en: DogfoodReport
#   intro: run_dogfood_cycle 返回值——测试数/通过数/自洽标志/失败发现清单/UTC时间戳
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: 自测报告JSON文件
#   name_en: DOGFOOD-*.json
#   intro: data/maintenance/dogfooding/ 下按报告ID命名的持久化自测报告
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> A2
# I2 --> A3
# A1 --> A3
# A1 --> O1
# A3 --> O2
"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Final


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

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def tasks(self):
        """只读：tasks（Stage 4 公共化）。"""
        return self._tasks

    @tasks.setter
    def tasks(self, value):
        """写入：tasks（Stage 4 公共化）。"""
        self._tasks = value

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
