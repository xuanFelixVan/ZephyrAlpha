"""Config Governance — v0.3.0 R8

Blindspot: Config changes unversioned; no rollback capability.
Risk: R8 — Bad config deploy breaks FLE with no recovery path.
"""
from dataclasses import dataclass, field

@dataclass
class ConfigGovernance:
    versions: list[dict] = field(default_factory=list)

    def snapshot(self, config: dict) -> int:
        self.versions.append(dict(config))
        return len(self.versions) - 1
