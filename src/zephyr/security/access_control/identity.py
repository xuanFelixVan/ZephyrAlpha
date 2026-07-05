# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.identity
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py; permission_guard; rbac_guard; abac_guard
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] AgentIdentity attributes immutable after construction; role+maturity determine permission baseline
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AgentIdentity construction never raises; missing kwargs use defaults
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_identity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Agent identity — 角色与成熟度定义.

依据蓝图 MOD-INF-018 §3:
- AgentRole: 5 种角色枚举（READER/WRITER/EXECUTOR/REVIEWER/ADMIN）
- MaturityLevel: 5 级成熟度（L0_INTERN ~ L4_PRINCIPAL）
- IDESource: 7 种 IDE 来源（含 UNKNOWN）
- AgentIdentity: agent 身份载体（dataclass）
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentRole(str, Enum):
    """Agent 角色枚举."""

    READER = "READER"
    WRITER = "WRITER"
    EXECUTOR = "EXECUTOR"
    REVIEWER = "REVIEWER"
    ADMIN = "ADMIN"


class MaturityLevel(str, Enum):
    """Agent 成熟度枚举."""

    L0_INTERN = "L0_INTERN"
    L1_JUNIOR = "L1_JUNIOR"
    L2_REGULAR = "L2_REGULAR"
    L3_SENIOR = "L3_SENIOR"
    L4_PRINCIPAL = "L4_PRINCIPAL"


class IDESource(str, Enum):
    """IDE 来源枚举."""

    UNKNOWN = "UNKNOWN"
    TRAE = "TRAE"
    CURSOR = "CURSOR"
    CLAUDE = "CLAUDE"
    COPILOT = "COPILOT"
    CLI = "CLI"
    API = "API"


MATURITY_AUTO_GUARD_TIMEOUT = {
    "L0_INTERN": 300,
    "L1_JUNIOR": 900,
    "L2_REGULAR": 3600,
    "L3_SENIOR": 3600,
    "L4_PRINCIPAL": 7200,
}

MATURITY_TLB_LIMITS = {
    "L0_INTERN": 100,
    "L1_JUNIOR": 500,
    "L2_REGULAR": 2000,
    "L3_SENIOR": 10000,
    "L4_PRINCIPAL": 50000,
}

ROLE_DEFAULT_PERMISSIONS: dict[Any, list[str]] = {
    AgentRole.READER: ["read:docs", "read:src", "read:tests", "read:config"],
    AgentRole.WRITER: [
        "read:docs", "read:src", "read:tests", "read:config",
        "write:src", "write:tests", "write:docs",
    ],
    AgentRole.EXECUTOR: [
        "read:docs", "read:src", "read:tests", "read:config",
        "write:src", "write:tests", "write:docs",
        "execute:scripts", "execute:tests",
    ],
    AgentRole.REVIEWER: [
        "read:docs", "read:src", "read:tests", "read:config",
        "review:code", "approve:merge",
    ],
    AgentRole.ADMIN: [
        "read:docs", "read:src", "read:tests", "read:config",
        "write:src", "write:tests", "write:docs", "write:scripts",
        "execute:scripts", "execute:tests",
        "review:code", "approve:merge",
        "manage:rbac", "manage:kill_switch",
        "admin:*",
    ],
}


@dataclass
class AgentIdentity:
    """Agent 身份载体.

    Attributes:
        session_id: 会话 ID
        maturity: 成熟度等级
        role: 角色
        owner_approved: 是否经 Owner 批准
        auto_guard_eligible: 是否符合 auto-guard 条件
        permissions: 显式权限列表
        ide_source: IDE 来源
        delegation_depth: 委托深度
        session_token: 会话令牌（HMAC 签名）
    """

    session_id: str = ""
    maturity: MaturityLevel = MaturityLevel.L0_INTERN
    role: AgentRole = AgentRole.WRITER
    owner_approved: bool = False
    auto_guard_eligible: bool = False
    permissions: list[str] = field(default_factory=list)
    ide_source: IDESource = IDESource.UNKNOWN
    delegation_depth: int = 0
    session_token: str = ""

    def can_promote_to(self, target_level: MaturityLevel) -> bool:
        """检查是否可晋升到目标成熟度等级（最多跨 1 级）."""
        levels = list(MaturityLevel)
        current_idx = levels.index(self.maturity)
        target_idx = levels.index(target_level)
        return target_idx <= current_idx + 1

    def sign_token(self, secret: str) -> None:
        """使用密钥对 session_id 进行 HMAC-SHA256 签名."""
        msg = self.session_id.encode("utf-8")
        mac = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256)
        self.session_token = mac.hexdigest()

    def verify_token(self, secret: str) -> bool:
        """验证会话令牌是否与密钥匹配."""
        if not self.session_token:
            return False
        msg = self.session_id.encode("utf-8")
        expected = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
        return hmac.compare_digest(self.session_token, expected)

    def has_permission(self, permission: str) -> bool:
        """检查是否拥有指定权限（支持通配符 read:*）."""
        for perm in self.permissions:
            if perm == permission:
                return True
            if perm.endswith(":*"):
                prefix = perm[:-1]
                if permission.startswith(prefix):
                    return True
        return False

    def get_tlb_limit(self) -> int:
        """获取当前成熟度的 TLB 限制."""
        return MATURITY_TLB_LIMITS[self.maturity.value]

    def get_auto_guard_timeout(self) -> int:
        """获取当前成熟度的 auto-guard 超时时间（秒）."""
        return MATURITY_AUTO_GUARD_TIMEOUT[self.maturity.value]


__all__ = [
    "MATURITY_AUTO_GUARD_TIMEOUT",
    "MATURITY_TLB_LIMITS",
    "ROLE_DEFAULT_PERMISSIONS",
    "AgentIdentity",
    "AgentRole",
    "IDESource",
    "MaturityLevel",
]
