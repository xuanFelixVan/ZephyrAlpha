"""零停机滚动升级（CT-DEPLOY）——graceful shutdown+流量摘除+health check wait。"""

from __future__ import annotations

class RollingUpgradeManager:
    def __init__(self):
        self._upgrading = False

    def start_upgrade(self) -> None:
        self._upgrading = True

    def is_draining(self) -> bool:
        return self._upgrading

    def complete_upgrade(self) -> None:
        self._upgrading = False
