# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.security.secret_rotation

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Secret Rotation — v0.14.0 R189

Blindspot: API keys/secrets never rotated; leaked credentials valid indefinitely.
Risk: R189 — Compromised secret grants permanent access; no automated rotation.

Mitigation: Secret lifecycle management with automated rotation scheduling.
"""
from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


@dataclass
class SecretEntry:
    secret_id: str
    service_name: str
    last_rotated: float
    rotation_interval_days: int = 90
    current_hash: str = ""

    @property
    def days_since_rotation(self) -> float:
        return (time.time() - self.last_rotated) / 86400.0

    @property
    def needs_rotation(self) -> bool:
        return self.days_since_rotation > self.rotation_interval_days


@dataclass
class SecretRotation:
    secrets: dict[str, SecretEntry] = field(default_factory=dict)

    def register(self, secret_id: str, service_name: str, interval_days: int = 90) -> SecretEntry:
        entry = SecretEntry(
            secret_id=secret_id,
            service_name=service_name,
            last_rotated=time.time(),
            rotation_interval_days=interval_days,
        )
        self.secrets[secret_id] = entry
        return entry

    def rotate(self, secret_id: str) -> str:
        entry = self.secrets.get(secret_id)
        if entry is None:
            raise KeyError(f"Secret {secret_id} not registered")
        new_secret = secrets.token_hex(32)
        entry.current_hash = new_secret
        entry.last_rotated = time.time()
        return new_secret

    def pending_rotations(self) -> list[str]:
        return [sid for sid, e in self.secrets.items() if e.needs_rotation]
