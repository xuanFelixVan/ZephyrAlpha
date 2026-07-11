# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.phase_executor
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.governance.__init__
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_phase_executor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""6Phase施工执行器 — Phase 0~5 执行状态追踪."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class PhaseStatus:
    name: str = ""
    description: str = ""
    completed: bool = False
    file_count: int = 0
    notes: str = ""


class PhaseExecutor:
    """6 Phase 施工执行器."""

    _PHASES: list[dict[str, Any]] = [
        {
            "name": "Phase 0: 基础设施",
            "desc": "包目录+data/cache/+tests目录+__init__.py",
            "files": 4,
        },
        {
            "name": "Phase 1: 核心检测流水线",
            "desc": "6模块: cache/scanner/ast/signature/degradation/config",
            "files": 6,
        },
        {
            "name": "Phase 2: 自动修复+自保护",
            "desc": "auto_fixer/doom_loop/self_scanner/codegen_guard等",
            "files": 8,
        },
        {
            "name": "Phase 3: 闭环生态",
            "desc": "Monoculture/Grandfather/Atomic/决策审计/漏报盲审",
            "files": 12,
        },
        {
            "name": "Phase 4: 全民升级",
            "desc": "Wave 3 debt/hotspot/shadow/evolver/simplicity等",
            "files": 10,
        },
        {
            "name": "Phase 5: 全量基线+验证",
            "desc": "全量扫描+测试+报告+pre-commit+CI集成",
            "files": 12,
        },
    ]

    def __init__(self, package_dir: str | Path | None = None) -> None:
        if package_dir is None:
            package_dir = Path("src/zephyr/testing/code_dedup")
        self._pkg = Path(package_dir)

    def get_status(self) -> list[PhaseStatus]:
        """获取所有 Phase 的状态."""
        results: list[PhaseStatus] = []
        for phase in self._PHASES:
            py_count = len(list(self._pkg.glob("*.py")))
            completed = py_count >= phase["files"]

            results.append(
                PhaseStatus(
                    name=phase["name"],
                    description=phase["desc"],
                    completed=completed,
                    file_count=py_count,
                    notes=f"达成 {py_count}/{phase['files']} 文件",
                )
            )
        return results

    def generate_report(self) -> dict[str, Any]:
        """生成施工进度报告."""
        statuses = self.get_status()
        completed = sum(1 for s in statuses if s.completed)
        total_files = len(list(self._pkg.glob("*.py")))

        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "phases_completed": f"{completed}/{len(self._PHASES)}",
            "total_python_files": total_files,
            "phases": [
                {
                    "phase": s.name,
                    "completed": s.completed,
                    "file_count": s.file_count,
                    "notes": s.notes,
                }
                for s in statuses
            ],
        }
