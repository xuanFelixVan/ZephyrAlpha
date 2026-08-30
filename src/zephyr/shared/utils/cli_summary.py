# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md
# [MODULE] zephyr.shared.utils.cli_summary
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
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
CLI Summary — CLI 友好施工汇总。

依据：
    蓝图 MOD-TASK_SYSTEM §6.3.4 + v0.6.0
    任务卡 TASK-INF-0109 (Part 4/5)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: output_dir 参数
#   fields: 参数 output_dir（无注解）
#   code: cli_summary.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① CLISummary
#   name_en: CLISummary
#   intro: class CLISummary 源码 L71-L140
#   desc: 公共方法（定义序）: generate, generate_journal, save_summary；源码 L71-L140
#   inputs: output_dir
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: CLISummary
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class BuildSummary:
    task_id: str
    status: str
    files_created: int
    files_modified: int
    warnings: list[str]
    errors: list[str]
    duration_s: float
    timestamp_utc: str


class CLISummary:
    def __init__(self, output_dir: Path | None = None) -> None:
        self._output_dir = output_dir or Path("data/observability/summaries")

    def generate(self, summary: BuildSummary) -> str:
        status_icon = {"completed": "[OK]", "failed": "[FAIL]", "partial": "[WARN]"}.get(summary.status, "[???]")

        lines = [
            f"  {status_icon} {summary.task_id}",
            f"     Files: +{summary.files_created} created, ~{summary.files_modified} modified",
            f"     Duration: {summary.duration_s:.1f}s",
        ]

        if summary.warnings:
            lines.append(f"     Warnings: {len(summary.warnings)}")
        if summary.errors:
            lines.append(f"     Errors: {len(summary.errors)}")

        return "\n".join(lines)

    def generate_journal(self, summaries: list[BuildSummary]) -> str:
        total_created = sum(s.files_created for s in summaries)
        total_modified = sum(s.files_modified for s in summaries)
        total_duration = sum(s.duration_s for s in summaries)
        failed = [s for s in summaries if s.status == "failed"]

        lines = [
            "=" * 60,
            f"Build Session Summary — {datetime.now(UTC).isoformat()}",
            "=" * 60,
            f"  Tasks: {len(summaries)} ({len(failed)} failed)",
            f"  Files: +{total_created} created, ~{total_modified} modified",
            f"  Total Time: {total_duration:.1f}s ({total_duration / 60:.1f}m)",
            "",
        ]

        for s in summaries:
            lines.append(self.generate(s))
            lines.append("")

        if failed:
            lines.append(f"[!] {len(failed)} TASKS FAILED:")
            for f in failed:
                lines.append(f"    - {f.task_id}: {', '.join(f.errors[:3])}")

        return "\n".join(lines)

    def save_summary(self, summary: BuildSummary) -> Path:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self._output_dir / f"{summary.task_id}_summary.json"

        output_path.write_text(
            json.dumps(
                {
                    "task_id": summary.task_id,
                    "status": summary.status,
                    "files_created": summary.files_created,
                    "files_modified": summary.files_modified,
                    "warnings": summary.warnings,
                    "errors": summary.errors,
                    "duration_s": summary.duration_s,
                    "timestamp_utc": summary.timestamp_utc,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return output_path
