# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] zephyr.infrastructure.auto_fix_engine.fix_report
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS] engine.py;__main__.py;MOD-INF-027(audit-orchestrator)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 报告MUST包含所有修复结果;MUST包含预算状态
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ReportError
# [TESTS] tests/auto-fix-engine/test_fix_report.py
# [A_module] module_id=MOD-INF-031 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: fix_report.py
# 层: 算法
# - id: A1
#   name_zh: ① FixReportGenerator
#   name_en: FixReportGenerator
#   intro: class FixReportGenerator 源码 L66-L161
#   desc: 公共方法（定义序）: history, generate, generate_summary, to_json, get_history；源码 L66-L161
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: FixReportGenerator
#   downstream: engine.py;__main__.py;MOD-INF-027(audit-orchestrator)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import json
import logging
from collections import deque
from datetime import UTC, datetime
from typing import Any

from zephyr.infrastructure.auto_fix_engine.models import (
    BudgetInfo,
    FixAction,
    FixReport,
    FixStatus,
)

logger = logging.getLogger(__name__)


class FixReportGenerator:
    def __init__(self) -> None:
        # 5.65.8 修复：原 self._history: list[FixReport] = [] 无上限，长跑进程内存无界增长。
        # 改为 deque(maxlen=1000)，自动淘汰最旧记录。
        self._history: deque[FixReport] = deque(maxlen=1000)

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def history(self) -> deque[FixReport]:
        """只读：history（Stage 4 公共化）。"""
        return self._history

    @history.setter
    def history(self, value):
        """写入：history（Stage 4 公共化）。"""
        self._history = value

    def generate(
        self, actions: list[FixAction], budget_info: BudgetInfo | None = None, cascade_alerts: list[str] | None = None
    ) -> FixReport:
        succeeded = sum(1 for a in actions if a.status is FixStatus.COMPLETED)
        failed = sum(1 for a in actions if a.status is FixStatus.FAILED)
        escalated = sum(1 for a in actions if a.status is FixStatus.APPROVAL_PENDING or a.escalated)
        dead_lettered = sum(1 for a in actions if a.status is FixStatus.DEAD_LETTER)
        report = FixReport(
            total_attempted=len(actions),
            succeeded=succeeded,
            failed=failed,
            escalated=escalated,
            dead_lettered=dead_lettered,
            budget_remaining=budget_info or BudgetInfo(),
            actions=actions,
            cascade_alerts=cascade_alerts or [],
        )
        self._history.append(report)
        return report

    def generate_summary(self, report: FixReport) -> dict[str, Any]:
        by_type: dict[str, dict[str, int]] = {}
        for action in report.actions:
            t = action.action_type
            if t not in by_type:
                by_type[t] = {"total": 0, "succeeded": 0, "failed": 0}
            by_type[t]["total"] += 1
            if action.status is FixStatus.COMPLETED:
                by_type[t]["succeeded"] += 1
            elif action.status is FixStatus.FAILED:
                by_type[t]["failed"] += 1
        by_level: dict[str, int] = {}
        for action in report.actions:
            level = action.level.value
            by_level[level] = by_level.get(level, 0) + 1
        by_confidence: dict[str, int] = {}
        for action in report.actions:
            conf = action.confidence.value
            by_confidence[conf] = by_confidence.get(conf, 0) + 1
        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_attempted": report.total_attempted,
            "succeeded": report.succeeded,
            "failed": report.failed,
            "escalated": report.escalated,
            "dead_lettered": report.dead_lettered,
            "success_rate": report.succeeded / max(report.total_attempted, 1),
            "by_type": by_type,
            "by_level": by_level,
            "by_confidence": by_confidence,
            "budget_remaining": {
                "daily": report.budget_remaining.daily_remaining,
                "monthly": report.budget_remaining.monthly_remaining,
                "llm_tokens": report.budget_remaining.llm_tokens_remaining,
            },
            "cascade_alerts": report.cascade_alerts,
        }

    def to_json(self, report: FixReport) -> str:
        summary = self.generate_summary(report)
        actions_data = []
        for a in report.actions:
            actions_data.append(
                {
                    "action_id": a.action_id,
                    "action_type": a.action_type,
                    "level": a.level.value,
                    "status": a.status.value,
                    "target": a.target,
                    "confidence": a.confidence.value,
                    "verified": a.verified,
                    "escalated": a.escalated,
                }
            )
        summary["actions"] = actions_data
        return json.dumps(summary, indent=2, ensure_ascii=False)

    def get_history(self, limit: int = 10) -> list[FixReport]:
        return list(self._history)[-limit:]
