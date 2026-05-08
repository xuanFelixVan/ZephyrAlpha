"""Concurrent Change Deconfliction — v0.16.0 R230

Blindspot: Owner manual change + FLE auto-repair target same config simultaneously.
Risk: R230 — Owner and FLE overwrite each other; final state is neither intended.

Mitigation: Concurrent change detection with optimistic locking and conflict resolution protocol.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import time


class ChangeSource(str, Enum):
    OWNER = "OWNER"
    FLE = "FLE"
    EXTERNAL = "EXTERNAL"


@dataclass
class ChangeAttempt:
    source: ChangeSource
    resource: str
    version: int
    timestamp: float = field(default_factory=time.time)
    accepted: bool = False


@dataclass
class ConcurrentChangeDeconfliction:
    resource_versions: dict[str, int] = field(default_factory=dict)
    resolution_log: list[ChangeAttempt] = field(default_factory=list)
    conflict_grace_period: float = 5.0

    def attempt(self, source: ChangeSource, resource: str, expected_version: int) -> bool:
        current_version = self.resource_versions.get(resource, 0)
        if expected_version != current_version:
            self.resolution_log.append(ChangeAttempt(source=source, resource=resource, version=expected_version, accepted=False))
            return False
        new_version = current_version + 1
        self.resource_versions[resource] = new_version
        self.resolution_log.append(ChangeAttempt(source=source, resource=resource, version=new_version, accepted=True))
        return True

    def recent_conflicts(self) -> list[ChangeAttempt]:
        now = time.time()
        return [a for a in self.resolution_log if not a.accepted and now - a.timestamp < self.conflict_grace_period]
