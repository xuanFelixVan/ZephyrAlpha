# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.key_hierarchy

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""密钥层级——root_key/signing_key/transport_key/audit_key 四层派生."""
from __future__ import annotations

import hashlib
import secrets
from typing import Any


class KeyHierarchy:
    LEVELS = ["ROOT", "SIGNING", "TRANSPORT", "AUDIT"]

    def __init__(self) -> None:
        self._keys: dict[str, str] = {}
        self._derived_from: dict[str, str] = {}

    def generate_root(self) -> str:
        root = f"ROOT-{secrets.token_hex(32)}"
        self._keys["ROOT"] = root
        return root

    def derive(self, level: str, from_level: str) -> str:
        if from_level not in self._keys:
            raise ValueError(f"Parent key '{from_level}' not found")
        if level not in self.LEVELS:
            raise ValueError(f"Unknown level '{level}'")

        parent = self._keys[from_level]
        derived = hashlib.sha256(f"{parent}:{level}:{secrets.token_hex(8)}".encode()).hexdigest()[:32]
        self._keys[level] = derived
        self._derived_from[level] = from_level
        return derived

    def get(self, level: str) -> str | None:
        return self._keys.get(level)

    def verify_chain(self) -> dict[str, Any]:
        issues = []
        for level in self.LEVELS:
            if level not in self._keys:
                issues.append(f"{level}:MISSING")
        return {"intact": len(issues) == 0, "issues": issues, "levels_present": len(self._keys)}
