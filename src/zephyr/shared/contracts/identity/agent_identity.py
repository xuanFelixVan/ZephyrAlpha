# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.identity.agent_identity
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.access_control.identity;zephyr.infrastructure.escalation;zephyr.governance;zephyr.integration.mcp
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Agent身份模型不可被篡改;成熟度分级不可扩展
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_agent_rbac.py
# [A_module] module_id=MOD-SHR_agent_identity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

import hashlib
import hmac
import time
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class MaturityLevel(str, Enum):
    L0_INTERN = "L0_INTERN"
    L1_JUNIOR = "L1_JUNIOR"
    L2_REGULAR = "L2_REGULAR"
    L3_SENIOR = "L3_SENIOR"
    L4_PRINCIPAL = "L4_PRINCIPAL"


class IDESource(str, Enum):
    TRAE = "trae"
    CURSOR = "cursor"
    ROOCODE = "roocode"
    CLI = "cli"
    API = "api"
    UNKNOWN = "unknown"


class AgentRole(str, Enum):
    READER = "reader"
    WRITER = "writer"
    EXECUTOR = "executor"
    ADMIN = "admin"
    AUDITOR = "auditor"


ROLE_DEFAULT_PERMISSIONS: dict[AgentRole, list[str]] = {
    AgentRole.READER: [
        "read:docs",
        "read:src",
        "read:tests",
        "read:config",
        "read:logs",
        "read:data",
    ],
    AgentRole.WRITER: [
        "read:docs",
        "read:src",
        "read:tests",
        "write:src",
        "write:tests",
        "read:config",
        "read:logs",
        "read:data",
    ],
    AgentRole.EXECUTOR: [
        "read:docs",
        "read:src",
        "read:tests",
        "write:src",
        "write:tests",
        "execute:scripts",
        "execute:tests",
        "read:config",
        "read:logs",
        "read:data",
    ],
    AgentRole.ADMIN: [
        "read:docs",
        "read:src",
        "read:tests",
        "write:src",
        "write:tests",
        "execute:scripts",
        "execute:tests",
        "read:config",
        "read:logs",
        "read:data",
        "manage:rbac",
        "manage:kill_switch",
        "manage:gates",
        "manage:deploy",
    ],
    AgentRole.AUDITOR: [
        "read:docs",
        "read:src",
        "read:tests",
        "read:config",
        "read:logs",
        "read:data",
        "read:audit",
        "audit:full",
    ],
}


MATURITY_TLB_LIMITS: dict[MaturityLevel, int] = {
    MaturityLevel.L0_INTERN: 100,
    MaturityLevel.L1_JUNIOR: 500,
    MaturityLevel.L2_REGULAR: 2000,
    MaturityLevel.L3_SENIOR: 10000,
    MaturityLevel.L4_PRINCIPAL: 50000,
}

MATURITY_AUTO_GUARD_TIMEOUT: dict[MaturityLevel, int] = {
    MaturityLevel.L0_INTERN: 300,
    MaturityLevel.L1_JUNIOR: 300,
    MaturityLevel.L2_REGULAR: 600,
    MaturityLevel.L3_SENIOR: 1800,
    MaturityLevel.L4_PRINCIPAL: 7200,
}


class AgentIdentity(BaseModel):
    session_id: str
    maturity: MaturityLevel = MaturityLevel.L0_INTERN
    role: AgentRole = AgentRole.WRITER
    ide_source: IDESource = IDESource.UNKNOWN
    model: str = "unknown"
    task_context: str = ""
    session_token: str = ""
    parent_session_id: str | None = None
    delegation_depth: int = 0
    permissions: list[str] = Field(default_factory=list)
    auto_guard_eligible: bool = False
    owner_approved: bool = False
    created_at: float = Field(default_factory=time.time)
    last_active: float = Field(default_factory=time.time)

    model_config = ConfigDict(use_enum_values=True)

    def _maturity_value(self) -> str:
        if isinstance(self.maturity, MaturityLevel):
            return self.maturity.value
        return str(self.maturity)

    def sign_token(self, secret: str) -> str:
        payload = f"{self.session_id}:{self.created_at}:{self._maturity_value()}"
        self.session_token = hmac.new(
            secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return self.session_token

    def verify_token(self, secret: str) -> bool:
        if not self.session_token:
            return False
        expected = hmac.new(
            secret.encode("utf-8"),
            f"{self.session_id}:{self.created_at}:{self._maturity_value()}".encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(self.session_token, expected)

    def has_permission(self, permission: str) -> bool:
        if permission in self.permissions:
            return True
        for p in self.permissions:
            if p.endswith(":*") and permission.startswith(p[:-1]):
                return True
        return False

    def _resolve_maturity(self) -> MaturityLevel:
        if isinstance(self.maturity, MaturityLevel):
            return self.maturity
        try:
            return MaturityLevel(self.maturity)
        except (ValueError, TypeError):
            return MaturityLevel.L0_INTERN

    def get_tlb_limit(self) -> int:
        return MATURITY_TLB_LIMITS.get(self._resolve_maturity(), 100)

    def get_auto_guard_timeout(self) -> int:
        return MATURITY_AUTO_GUARD_TIMEOUT.get(self._resolve_maturity(), 300)

    def can_promote_to(self, target: MaturityLevel) -> bool:
        levels = list(MaturityLevel)
        resolved = self._resolve_maturity()
        current_idx = levels.index(resolved) if resolved in levels else 0
        target_idx = levels.index(target) if target in levels else 0
        return target_idx <= current_idx + 1


AgentMaturity = MaturityLevel
