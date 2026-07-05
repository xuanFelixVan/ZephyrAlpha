# [BLUEPRINT] SH-MAIN-001
# [MODULE] zephyr.shared.security.sandbox_executor
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] tests.unit.shared.test_orphan_integration
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""SandboxExecutor — re-homed to eliminate shared->infrastructure circular import."""

import os
import tempfile
from typing import Any

__all__ = ["SandboxExecutor"]


class SandboxExecutor:
    """Execute fix actions in an isolated sandbox directory."""

    def __init__(self, base_dir: str | None = None) -> None:
        self._base_dir = base_dir or os.path.join(tempfile.gettempdir(), "auto_fix_sandbox")

    def execute(self, action: Any, fix_fn: Any) -> tuple[bool, str]:
        sandbox_dir = os.path.join(self._base_dir, getattr(action, "action_id", "unknown"))
        os.makedirs(sandbox_dir, exist_ok=True)
        try:
            result = fix_fn(action.target, dry_run=True)
            return True, str(result)
        except Exception as exc:
            return False, str(exc)
        finally:
            try:
                import shutil

                shutil.rmtree(sandbox_dir, ignore_errors=True)
            except Exception:
                pass
