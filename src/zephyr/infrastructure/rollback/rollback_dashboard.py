# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_dashboard
# [DOMAIN] D_INFRA_RECOVERY
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
# [A_module] module_id=MOD-INF_rollback_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackDashboard — 回滚仪表盘（零依赖 Markdown）。

依据: 蓝图 MOD-INF-021 §6.2 B47

生成 Markdown 零依赖仪表盘，包含：
    回滚次数 / MTTR / 成功率 / 活跃 Kill Switch / 预算剩余 / IM 推送格式
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class DashboardMetrics:
    total_rollbacks: int = 0
    mttr_seconds: float = 0.0
    success_rate: float = 0.0
    active_kill_switches: int = 0
    budget_remaining: int = 0
    drill_pass_rate: float = 0.0


class RollbackDashboard:
    OUTPUT_PATH: str = ".zephyr/rollback_dashboard.md"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._output_path = self._project_root / self.OUTPUT_PATH

    def generate(self, metrics: DashboardMetrics) -> Path:
        lines: list[str] = []
        lines.append("# Rollback Dashboard")
        lines.append("")
        lines.append("## Metrics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Rollbacks | {metrics.total_rollbacks} |")
        lines.append(f"| MTTR (seconds) | {metrics.mttr_seconds:.1f} |")
        lines.append(f"| Success Rate | {metrics.success_rate:.1%} |")
        lines.append(f"| Active Kill Switches | {metrics.active_kill_switches} |")
        lines.append(f"| Budget Remaining | {metrics.budget_remaining} |")
        lines.append(f"| Drill Pass Rate | {metrics.drill_pass_rate:.1%} |")
        lines.append("")

        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        self._output_path.write_text("\n".join(lines), encoding="utf-8")
        return self._output_path

    def generate_im_format(self, metrics: DashboardMetrics) -> str:
        items: list[str] = []
        items.append("**Rollback Dashboard**")
        emoji = "🟢" if metrics.success_rate > 0.90 else ("🟡" if metrics.success_rate > 0.70 else "🔴")
        items.append(f"{emoji} Success: {metrics.success_rate:.0%}")
        items.append(f"⏱ MTTR: {metrics.mttr_seconds:.1f}s")
        items.append(f"🔢 Total: {metrics.total_rollbacks}")
        if metrics.active_kill_switches > 0:
            items.append(f"⚠️ Kill Switches: {metrics.active_kill_switches}")
        return "\n".join(items)
