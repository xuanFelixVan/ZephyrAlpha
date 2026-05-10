"""三冗余 Watchdog（CT-WATCHDOG-001）——互检+Panic Mode+Dead Man's Switch。"""

from __future__ import annotations

import time
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class WatchdogHeartbeat(BaseModel):
    watchdog_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    alive: bool = True


class Watchdog:
    def __init__(self, watchdog_id: str):
        self._id = watchdog_id
        self._heartbeats: dict[str, WatchdogHeartbeat] = {}
        self._external_file = f".watchdog_heartbeat_{watchdog_id}"
        self._panic_mode = False

    @property
    def panic_mode(self) -> bool:
        return self._panic_mode

    def check_peers(self, peers: list[str], peer_heartbeats: dict[str, float]) -> bool:
        missing = 0
        for peer in peers:
            last = peer_heartbeats.get(peer, 0)
            if time.time() - last > 1800:
                missing += 1
        self._panic_mode = missing >= 2
        return not self._panic_mode

    def write_external_heartbeat(self) -> None:
        pass

    def should_alert_dead_mans_switch(self, last_heartbeat_s: float) -> bool:
        return time.time() - last_heartbeat_s > 1800
