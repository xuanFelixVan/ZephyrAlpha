# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §4.1
# [MODULE] zephyr.security.access_control.orphan_judge.report_generator
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.db; zephyr.security.access_control.orphan_judge.models
# [CONSUMERS] orphan-judge.__main__._cmd_report
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 三种输出格式(JSON/CSV/Markdown); 不修改任何源文件
# [MODIFY-GUARD] 修改输出格式必须同步blueprint.md §4.1
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TypeError on unsupported format
# [TESTS] tests/orphan-judge/test_report_generator.py
# [A_module] module_id=MOD-INF-029 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: db 参数
#   fields: 参数 db（无注解）
#   code: report_generator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ReportGenerator
#   name_en: ReportGenerator
#   intro: class ReportGenerator 源码 L58-L121
#   desc: 公共方法（定义序）: generate, summary_text；源码 L58-L121
#   inputs: db
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ReportGenerator
#   downstream: orphan-judge.__main__._cmd_report
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import logging

from zephyr.security.access_control.orphan_judge.db import JudgmentDB
from zephyr.security.access_control.orphan_judge.models import JudgmentRecord
from zephyr.shared.io.serialization import dumps

logger = logging.getLogger(__name__)

__all__ = ["ReportGenerator"]


class ReportGenerator:
    def __init__(self, db: JudgmentDB | None = None) -> None:
        self._db = db or JudgmentDB()

    def generate(self, verdict_filter: str | None = None, fmt: str = "json") -> str:
        if verdict_filter:
            records = self._db.list_by_verdict(verdict_filter)
        else:
            records = self._db.list_by_verdict("KEEP")
            records += self._db.list_by_verdict("DELETE")
            records += self._db.list_by_verdict("DEPRECATE")
            records += self._db.list_by_verdict("EXTRACT_AND_MERGE")
            records += self._db.list_by_verdict("ESCALATE")

        if fmt == "json":
            return self._as_json(records)
        elif fmt == "csv":
            return self._as_csv(records)
        elif fmt == "markdown":
            return self._as_markdown(records)
        else:
            raise ValueError(f"Unsupported format: {fmt}")

    def _as_json(self, records: list[JudgmentRecord]) -> str:
        data = []
        for r in records:
            data.append(
                {
                    "path": r.path,
                    "verdict": r.verdict,
                    "confidence": r.confidence,
                    "reason": r.reason,
                    "scanned_at": r.scanned_at.isoformat(),
                }
            )
        return dumps(data, indent=2)

    def _as_csv(self, records: list[JudgmentRecord]) -> str:
        lines = ["path,verdict,confidence,reason,scanned_at"]
        for r in records:
            reason = r.reason.replace('"', '""')
            lines.append(f'{r.path},{r.verdict},{r.confidence},"{reason}",{r.scanned_at.isoformat()}')
        return "\n".join(lines)

    def _as_markdown(self, records: list[JudgmentRecord]) -> str:
        lines = ["| 文件 | 判决 | 置信度 | 原因 | 扫描时间 |", "|------|------|--------|------|----------|"]
        for r in records:
            lines.append(f"| {r.path} | {r.verdict} | {r.confidence} | {r.reason} | {r.scanned_at.isoformat()} |")
        lines.append("")
        s = self._db.summary()
        lines.append("### 统计")
        lines.append(f"- 总数: {s.total}")
        lines.append(
            f"- KEEP: {s.keep} | DELETE: {s.delete} | DEPRECATE: {s.deprecate} | EXTRACT_AND_MERGE: {s.extract_and_merge} | ESCALATE: {s.escalate}"
        )
        return "\n".join(lines)

    def summary_text(self) -> str:
        s = self._db.summary()
        return (
            f"Total: {s.total}\n"
            f"KEEP: {s.keep} | DELETE: {s.delete} | DEPRECATE: {s.deprecate} | "
            f"EXTRACT_AND_MERGE: {s.extract_and_merge} | ESCALATE: {s.escalate} | ERROR: {s.error}"
        )
