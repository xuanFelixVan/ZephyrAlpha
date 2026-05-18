# [BLUEPRINT] MOD-INF-002 | 03_modules/l01_infrastructure/runtime-integration/blueprint.md | §

# [MODULE] zephyr.core.maintenance.handbook

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Onboarding Handbook — AI Agent 施工手册生成。

依据：
    蓝图 MOD-INF-006 §6.5.4 + v0.6.0
    任务卡 TASK-INF-0110 (Part 4/4)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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
            "- Tasks: `docs/03_modules/l01_infrastructure/task-system/changes/MOD-INF-006/`",
            "",
            "### State Machine",
            "CREATED → LOCKED → ASSIGNED → IN_PROGRESS → REVIEWING → COMPLETED",
            "",
            "### Key Tools",
            "- `lock_files.py` — file lock protocol",
            "- `journal_13.md` — session log (current)",
            "- `checkpoint_13.json` — progress tracking",
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
            "docs/03_modules/l01_infrastructure/task-system/": "Task system blueprint",
        }
