# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_context_restorer
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
# [A_module] module_id=MOD-INF_rollback_context_restorer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RollbackContextRestorer — 上下文恢复器。

依据: 蓝图 MOD-INF-021 §6.2 B44

回滚后注入 AI 会话恢复 prompt——告知 AI 当前状态已被回滚、原因、可操作建议。
防止 AI agent 误以为代码是"自己刚写的"而产生幻觉。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class RestoreContext:
    rollback_reason: str
    reverted_commit: str
    files_affected: list[str]
    session_id: str
    action_plan: str


class RollbackContextRestorer:
    PROMPT_FILE: str = ".zephyr/context_restore_prompt.md"

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()
        self._prompt_path = self._project_root / self.PROMPT_FILE

    def generate_restore_prompt(self, context: RestoreContext) -> str:
        lines: list[str] = []
        lines.append("# AI Session Context Restore")
        lines.append("")
        lines.append(
            "**IMPORTANT**: Your previous session has been partially rolled back. "
            "The following context explains what happened and what you should do next."
        )
        lines.append("")
        lines.append("## What Happened")
        lines.append(f"- **Rollback Reason**: {context.rollback_reason}")
        lines.append(f"- **Reverted Commit**: {context.reverted_commit}")
        lines.append(f"- **Affected Files**: {', '.join(context.files_affected[:10])}")
        lines.append(f"- **Session ID**: {context.session_id}")
        lines.append("")
        lines.append("## Current State")
        lines.append(f"The code repository has been reverted to the state before commit `{context.reverted_commit}`.")
        lines.append("Do NOT assume that code you wrote in the rolled-back session still exists.")
        lines.append("")
        lines.append("## Recommended Action")
        lines.append(f"{context.action_plan}")
        lines.append("")
        lines.append("## Verification Required")
        lines.append("Before making any changes, verify the current state of all affected files.")
        lines.append("Run `git log --oneline -5` to confirm the current HEAD.")
        lines.append("")
        lines.append("---")
        lines.append(f"*Generated at {datetime.now(UTC).isoformat()}*")

        content = "\n".join(lines)
        self._prompt_path.parent.mkdir(parents=True, exist_ok=True)
        self._prompt_path.write_text(content, encoding="utf-8")
        return content

    def inject_for_session(self, context: RestoreContext) -> dict[str, Any]:
        prompt = self.generate_restore_prompt(context)
        return {
            "session_id": context.session_id,
            "restore_prompt": prompt,
            "prompt_file": str(self._prompt_path),
            "generated_at": datetime.now(UTC).isoformat(),
        }
