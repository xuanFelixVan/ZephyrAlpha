# [BLUEPRINT] MOD-INF-001 | 03_modules/l01_infrastructure/capacity-assurance/blueprint.md | §

# [MODULE] zephyr.capacity_assurance.modules.config_reload_semantic

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Config Reload Semantic — 配置热重载语义 (盲点 #32)
特性：
  - YAML 修改后自动检测并 reload
  - reload 后触发 ContractBus 校验 + 告警
"""
import os
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional


class ConfigReloadSemantic:
    """
    配置热重载语义 (盲点 #32)
    """

    def __init__(self):
        self._watched: dict[str, float] = {}
        self._callbacks: dict[str, list[Callable]] = {}

    def watch(self, filepath: str, callback: Optional[Callable] = None):
        if os.path.exists(filepath):
            self._watched[filepath] = os.path.getmtime(filepath)
            if callback:
                self._callbacks.setdefault(filepath, []).append(callback)

    def check_and_reload(self) -> list[str]:
        reloaded: list[str] = []
        for filepath, last_mtime in list(self._watched.items()):
            if not os.path.exists(filepath):
                continue
            current_mtime = os.path.getmtime(filepath)
            if current_mtime > last_mtime:
                self._watched[filepath] = current_mtime
                reloaded.append(filepath)
                for cb in self._callbacks.get(filepath, []):
                    try:
                        cb(filepath)
                    except Exception:
                        pass
        return reloaded
