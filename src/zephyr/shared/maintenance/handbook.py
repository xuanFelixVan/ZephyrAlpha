# [BLUEPRINT] SH-MAIN-001 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.maintenance.handbook
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.maintenance.zero_config
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
# [A_module] module_id=MOD-INF-handbook | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Onboarding Handbook — AI Agent 施工手册生成。

依据：
    蓝图 MOD-TASK_SYSTEM §6.5.4 + v0.6.0
    任务卡 TASK-INF-0110 (Part 4/4)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 项目根目录 project_root
#   fields: Path 可选, 默认 Path.cwd()
#   code: Handbook.__init__(project_root)
# 层: 算法
# - id: A1
#   name_zh: ① Agent上手上下文生成
#   name_en: Handbook.generate_onboarding_context
#   intro: 把核心约束、关键目录、任务状态机、关键工具拼成一段固定markdown给新Agent看
#   desc: 固定sections列表拼接: 5条Core Constraints(删文件需授权/锁协议/原子写/日志/检查点) + Key Directories + 状态机CREATED→...→COMPLETED + Key Tools → "\n".join
#   inputs: I1
#   outputs: onboarding markdown 字符串
# - id: A2
#   name_zh: ② 任务卡模板提供
#   name_en: Handbook.get_task_card_template
#   intro: 返回一张固定的任务卡markdown表格模板，照填即可
#   desc: 返回固定表头 | # | Task ID | Status | Layer | Files | Description | 的markdown模板字符串
#   inputs: I1
#   outputs: 任务卡模板字符串
# - id: A3
#   name_zh: ③ 目录地图提供
#   name_en: Handbook.get_directory_map
#   intro: 返回核心源码/蓝图/任务系统目录到中文说明的映射字典
#   desc: 固定dict: src/zephyr/core/、lifecycle/、reliability/、observability/、maintenance/、dependency/、mcp/、task-system蓝图 → 各一句话说明
#   inputs: I1
#   outputs: 目录→说明 dict[str,str]
# 层: 输出
# - id: O1
#   name_zh: Agent施工手册内容
#   name_en: onboarding context / template / directory map
#   intro: 上手文档字符串、任务卡模板与目录地图，供AI Agent施工时查阅
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# A1 --> O1
# A2 --> O1
# A3 --> O1
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class HandbookSection:
    section_id: str
    title: str
    content: str
    source_file: str = ""


class Handbook:
    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def generate_onboarding_context(self) -> str:
        sections = [
            "# Agent Onboarding Context",
            "",
            "## Project: ZephyrAlpha",
            "",
            "### Core Constraints",
            "1. Never delete files without explicit Owner authorization",
            "2. All file writes go through lock protocol (RULE-ZERO)",
            "3. Atomic writes using temp-file + os.replace() (RULE-ONE)",
            "4. Every task card execution is journaled",
            "5. Checkpoints are saved after each task batch",
            "",
            "### Key Directories",
            "- Source: `src/zephyr/`",
            "- Blueprints: `docs/03_modules/`",
            "- Journals: `_journals/`",
            "- Tasks: `docs/03_modules/_domain-infra_ops/task-system/changes/MOD-TASK_SYSTEM/`",
            "",
            "### State Machine",
            "CREATED -> LOCKED -> ASSIGNED -> IN_PROGRESS -> REVIEWING -> COMPLETED",
            "",
            "### Key Tools",
            "- `lock_files.py` — file lock protocol",
            "- `journal-13.md` — session log (current)",
            "- `checkpoint-13.json` — progress tracking",
            "- `_temp_execution_plan.md` — execution plan",
        ]

        return "\n".join(sections)

    def get_task_card_template(self) -> str:
        return """| # | Task ID | Status | Layer | Files | Description |
|---|---------|--------|-------|-------|-------------|
| 1 | TASK_NAME | ✅ | 0 | N | Description here |"""

    def get_directory_map(self) -> dict[str, str]:
        return {
            "src/zephyr/core/": "Core models, decomposer, context engine",
            "src/zephyr/core/lifecycle/": "G0-G7 lifecycle management",
            "src/zephyr/core/reliability/": "Circuit breaker, retry, diff planner",
            "src/zephyr/core/observability/": "Trace, cost, failure matching, notifier",
            "src/zephyr/core/maintenance/": "Zero config, dogfooding, autonomy",
            "src/zephyr/core/dependency/": "Dependency graph",
            "src/zephyr/mcp/": "MCP task manager server",
            "docs/03_modules/_domain-infra_ops/task-system/": "Task system blueprint",
        }
