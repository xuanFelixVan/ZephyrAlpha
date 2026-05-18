# [BLUEPRINT] MOD-INF-021 | 03_modules/l01_infrastructure/rollback-system/blueprint.md | §

# [MODULE] zephyr.rollback.rollback_context_restorer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
RollbackContextRestorer — 上下文恢复器。

依据: 蓝图 MOD-INF-021 §6.2 B44

回滚后注入 AI 会话恢复 prompt——告知 AI 当前状态已被回滚、原因、可操作建议。
防止 AI agent 误以为代码是"自己刚写的"而产生幻觉。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
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
        lines.append(f"# AI Session Context Restore")
        lines.append(f"")
        lines.append(f"**IMPORTANT**: Your previous session has been partially rolled back. "
                      f"The following context explains what happened and what you should do next.")
        lines.append(f"")
        lines.append(f"## What Happened")
        lines.append(f"- **Rollback Reason**: {context.rollback_reason}")
        lines.append(f"- **Reverted Commit**: {context.reverted_commit}")
        lines.append(f"- **Affected Files**: {', '.join(context.files_affected[:10])}")
        lines.append(f"- **Session ID**: {context.session_id}")
        lines.append(f"")
        lines.append(f"## Current State")
        lines.append(f"The code repository has been reverted to the state before commit `{context.reverted_commit}`.")
        lines.append(f"Do NOT assume that code you wrote in the rolled-back session still exists.")
        lines.append(f"")
        lines.append(f"## Recommended Action")
        lines.append(f"{context.action_plan}")
        lines.append(f"")
        lines.append(f"## Verification Required")
        lines.append(f"Before making any changes, verify the current state of all affected files.")
        lines.append(f"Run `git log --oneline -5` to confirm the current HEAD.")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"*Generated at {datetime.now(timezone.utc).isoformat()}*")

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
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
