# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.ide_watcher
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — IDE Watcher
Blueprint: docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
Author: factory-agent
Version: 0.1.0
"""

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any


class IDEWatcher:
    """IDE 热重载监视器——Skill 文件变更自动刷新 AGENTS.md"""

    def __init__(self, skills_dir: Path | None = None):
        self.skills_dir = skills_dir or (Path(__file__).resolve().parent / "skills")
        self._last_mtimes: dict[str, float] = {}
        self._callbacks: list = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def callbacks(self) -> list:
        """只读：callbacks（Stage 4 公共化）。"""
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value):
        """写入：callbacks（Stage 4 公共化）。"""
        self._callbacks = value

    @property
    def last_mtimes(self) -> dict[str, float]:
        """只读：last_mtimes（Stage 4 公共化）。"""
        return self._last_mtimes

    @last_mtimes.setter
    def last_mtimes(self, value):
        """写入：last_mtimes（Stage 4 公共化）。"""
        self._last_mtimes = value


    def scan(self) -> dict[str, Any]:
        changes = []
        for root, dirs, files in os.walk(str(self.skills_dir)):
            for f in files:
                if f.endswith((".md", ".yaml", ".yml")):
                    full_path = os.path.join(root, f)
                    mtime = os.path.getmtime(full_path)
                    if full_path in self._last_mtimes and self._last_mtimes[full_path] != mtime:
                        changes.append(full_path)
                    self._last_mtimes[full_path] = mtime
        if changes:
            self._trigger_agents_md_refresh()
        return {"changes_detected": len(changes), "files": changes}

    def _trigger_agents_md_refresh(self):
        for cb in self._callbacks:
            cb()

    def on_change(self, callback: Callable):
        self._callbacks.append(callback)
