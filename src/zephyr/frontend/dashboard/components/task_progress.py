# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.components.task_progress
# [DEPENDENCIES]
# [CONSUMERS] zephyr.frontend.dashboard.app_panel
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-L08-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-4-07 Task Progress Component
"""task_progress · 任务进度看板组件（v3.1.0 Panel 迁移, #ARCH-047）

蓝图规格: docs/03_modules/_domain_frontend/blueprint.md §3.1
数据源: TaskRepository.list_by_phase() -> 4 阶段任务进度
渲染依赖: Panel(布局) — 指标卡片+阶段进度条+明细表，无专业图表需求故不调用 ChartFactory

v3.1.0 变更 (#ARCH-047):
  - Streamlit(st.metric/st.progress/st.expander) -> Panel(pn.pane.Markdown 卡片+进度条)
  - callback仅编排: 数据计算在 fetch_task_progress(纯函数)
  - 测试环境(无 panel)仅返回 dict payload, 便于断言
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass, field
from typing import Any

# 5.160.11 修复：TaskStatus字符串替换为Enum引用
from zephyr.shared.foundation.constants import TaskStatus

try:
    import panel as pn
except ImportError:  # 测试环境无 panel
    pn = None


@dataclass
class PhaseProgress:
    phase: int
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    failed_tasks: int = 0
    pending_tasks: int = 0

    @property
    def completion_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks


@dataclass
class TaskProgressData:
    phases: list[PhaseProgress] = field(default_factory=list)
    total_tasks: int = 0
    total_completed: int = 0

    @property
    def overall_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.total_completed / self.total_tasks


def fetch_task_progress(task_repo: object = None) -> TaskProgressData:
    data = TaskProgressData()
    for phase in range(5):
        pp = PhaseProgress(phase=phase)
        if task_repo is not None:
            try:
                tasks = task_repo.list_by_phase(phase)
                pp.total_tasks = len(tasks)
                pp.completed_tasks = sum(1 for t in tasks if t.status.value in (TaskStatus.COMPLETED, TaskStatus.VERIFIED))
                pp.in_progress_tasks = sum(1 for t in tasks if t.status.value == TaskStatus.IN_PROGRESS)
                pp.failed_tasks = sum(1 for t in tasks if t.status.value == TaskStatus.FAILED)
                pp.pending_tasks = sum(1 for t in tasks if t.status.value == TaskStatus.PENDING)
            except Exception as e:
                logger.warning("suppressed error in task_progress", exc_info=True)
        data.phases.append(pp)
        data.total_tasks += pp.total_tasks
        data.total_completed += pp.completed_tasks
    return data


def _metric_card(label: str, value: str, color: str = "#333") -> object:
    if pn is None:
        return {"label": label, "value": value, "color": color}
    return pn.pane.Markdown(
        f"**{label}**\n\n## {value}",
        styles={"color": color, "text-align": "center", "padding": "8px",
                "border": "1px solid #e0e0e0", "border-radius": "4px"},
    )


def _progress_bar(label: str, rate: float, width: int = 30) -> str:
    """生成文本进度条（Markdown 友好）— width 为字符数"""
    filled = int(rate * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"`{bar}` {rate:.1%}"


def render_task_progress(data: TaskProgressData) -> dict[str, Any]:
    """Panel 渲染任务进度看板（v3.1.0, #ARCH-047）

    布局:
      - 顶部: 汇总指标卡片(overall_rate/total_tasks/total_completed)
      - 中部: 各阶段进度条(phase 0~4)
      - 底部: 各阶段明细表

    callback仅编排: 数据计算在 fetch_task_progress(纯函数).
    测试环境(无 panel)仅返回 dict payload, 便于断言.
    """
    payload: dict[str, Any] = {
        "overall_rate": round(data.overall_rate, 4),
        "total_tasks": data.total_tasks,
        "total_completed": data.total_completed,
        "phases": [
            {
                "phase": pp.phase,
                "total": pp.total_tasks,
                "completed": pp.completed_tasks,
                "in_progress": pp.in_progress_tasks,
                "failed": pp.failed_tasks,
                "pending": pp.pending_tasks,
                "completion_rate": round(pp.completion_rate, 4),
            }
            for pp in data.phases
        ],
        "renderer": "panel" if pn is not None else "dict",
    }

    if pn is None:
        return payload

    rate_color = "#28a745" if data.overall_rate >= 0.5 else "#ffc107"

    metric_row = pn.Row(
        _metric_card("Overall Completion", f"{data.overall_rate:.1%}", rate_color),
        _metric_card("Total Tasks", str(data.total_tasks)),
        _metric_card("Completed", str(data.total_completed)),
        sizing_mode="stretch_width",
    )

    layout_items: list[Any] = [
        pn.pane.Markdown("## 任务进度看板 (Task Progress)"),
        metric_row,
        pn.pane.Markdown("### 各阶段进度"),
    ]

    if data.phases:
        # 进度条
        bar_lines = []
        for pp in data.phases:
            bar_lines.append(
                f"**Phase {pp.phase}** ({pp.completed_tasks}/{pp.total_tasks}):  "
                + _progress_bar("", pp.completion_rate)
            )
        layout_items.append(pn.pane.Markdown("\n\n".join(bar_lines)))

        # 明细表
        rows = ["| Phase | Total | Completed | In Progress | Failed | Pending | Rate |",
                "|---|---|---|---|---|---|---|"]
        for pp in data.phases:
            rows.append(
                f"| {pp.phase} | {pp.total_tasks} | {pp.completed_tasks} | "
                f"{pp.in_progress_tasks} | {pp.failed_tasks} | {pp.pending_tasks} | "
                f"{pp.completion_rate:.1%} |"
            )
        layout_items.append(pn.pane.Markdown("\n".join(rows)))
    else:
        layout_items.append(pn.pane.Alert("无任务进度数据（TaskRepository 未配置）", alert_type="info"))

    layout = pn.Column(*layout_items, sizing_mode="stretch_width")
    payload["_layout"] = layout
    return payload


__all__ = [
    "PhaseProgress",
    "TaskProgressData",
    "fetch_task_progress",
    "render_task_progress",
]
