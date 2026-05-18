# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.derive_rbac_roles

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
GOV-AI-001 → rbac_roles.yaml 自动派生器

MOD-INF-018 §2.12  D-018-03

从 GOV-AI-001 确定性生成 rbac_roles.yaml，消除手动复制 = 消除漂移。
"""

import hashlib
from pathlib import Path
from typing import Optional

import yaml


DEFAULT_DERIVATIONS: dict[str, dict] = {
    "agent_writer": {
        "maturity": "L0_INTERN",
        "permissions": [
            "read:docs", "read:src", "read:tests",
            "write:src", "write:tests",
            "execute:scripts", "execute:tests",
        ],
        "auto_guard_eligible": True,
        "owner_approved": False,
    },
    "agent_reviewer": {
        "maturity": "L1_JUNIOR",
        "permissions": [
            "read:docs", "read:src", "read:tests",
            "read:config", "read:logs", "read:data",
            "audit:full",
        ],
        "auto_guard_eligible": False,
        "owner_approved": False,
    },
    "agent_architect": {
        "maturity": "L3_SENIOR",
        "permissions": [
            "read:docs", "read:src", "read:tests",
            "write:src", "write:tests",
            "execute:scripts", "execute:tests",
            "read:config", "read:logs", "read:data",
            "modify:blueprint", "modify:document",
        ],
        "auto_guard_eligible": True,
        "owner_approved": True,
    },
}


class RBACRoleDeriver:
    def __init__(self) -> None:
        self._derivations = dict(DEFAULT_DERIVATIONS)

    def derive(self, output_path: Path) -> str:
        config = {
            "version": "0.14.0",
            "auto_generated": True,
            "source": "GOV-AI-001",
            "agents": dict(self._derivations),
        }
        content = yaml.dump(config, default_flow_style=False, allow_unicode=True)
        output_path.write_text(content, encoding="utf-8")
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def compare_with_existing(self, existing_path: Path) -> Optional[dict]:
        if not existing_path.exists():
            return {"status": "MISSING", "action": "GENERATE_NEW"}
        existing_hash = hashlib.sha256(existing_path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        new_content = yaml.dump(
            {"version": "0.14.0", "agents": dict(self._derivations)},
            default_flow_style=False,
            allow_unicode=True,
        )
        new_hash = hashlib.sha256(new_content.encode("utf-8")).hexdigest()
        if existing_hash != new_hash:
            return {"status": "DRIFT_DETECTED", "action": "REGENERATE"}
        return {"status": "CONSISTENT", "action": "NO_ACTION"}
