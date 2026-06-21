# [A_module] module_id=MOD-ORC_ide_watcher | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md

# [MODULE] zephyr.orchestration.agent_lifecycle.ide_watcher

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
MOD-INF-019: Agent Spec — IDE Watcher
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.1.0
"""


import os
import time
from pathlib import Path
from typing import Dict, Any, Callable, Optional


class IDEWatcher:
    """IDE 热重载监视器——Skill 文件变更自动刷新 AGENTS.md"""

    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = skills_dir or (Path(__file__).resolve().parent / "skills")
        self._last_mtimes: Dict[str, float] = {}
        self._callbacks: list = []

    def scan(self) -> Dict[str, Any]:
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
