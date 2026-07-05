# [BLUEPRINT] MOD-INF-013 | docs/03_modules/_cross_layer/mcp-servers/blueprint.md
# [MODULE] zephyr.infrastructure.handoff_auto_loader
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
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
# [A_module] module_id=MOD-INF_handoff_auto_loader | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Handoff 自动加载器——从 handoff 包恢复 AI session 上下文（MOD-INF-013 §5.3）。"""

import logging
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


class HandoffAutoLoader:
    """从 HandoffPackage 自动加载上一次 AI session 的上下文。

    集成 ai-autonomy-authority-registry 中 mcp/ 目录的自治权限声明。
    """

    def __init__(self, handoff_dir: Path | None = None) -> None:
        self._dir = handoff_dir or Path("data/handoff")
        self._latest: dict[str, Any] | None = None

    @property
    def has_handoff(self) -> bool:
        return self._dir.exists() and any(self._dir.iterdir())

    def load_latest(self) -> dict[str, Any] | None:
        if not self.has_handoff:
            return None
        try:
            files = sorted(self._dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
            if files:
                import json

                with open(files[0], encoding="utf-8") as fh:
                    self._latest = json.load(fh)
                return self._latest
        except Exception as exc:
            _log.warning("handoff load failed: %s", exc, exc_info=True)
        return None

    def get_carryover_context(self) -> list[str]:
        pkg = self.load_latest()
        if not pkg:
            return []
        items: list[str] = []
        for task_id in pkg.get("completed_tasks", [])[:5]:
            items.append(f"已完成: {task_id}")
        for task_id in pkg.get("next_tasks", [])[:5]:
            items.append(f"待办: {task_id}")
        return items
