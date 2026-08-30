# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.identity.agent_identity
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.security.access_control.identity;zephyr.infrastructure.escalation;zephyr.governance;zephyr.integration.mcp
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Agent身份模型不可被篡改;成熟度分级不可扩展
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_agent_rbac.py
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: agent_identity.py
# 层: 算法
# - id: A1
#   name_zh: ① 数据契约声明
#   name_en: data class declarations
#   intro: 纯声明类（无公共方法，AST 事实）: MaturityLevel, IDESource, RbacRole, AgentIdentity
#   desc: 数据契约/异常/枚举声明共 4 类；无算法流程（AST 事实）
#   inputs: I1
#   outputs: 数据契约类集合
# 层: 输出
# - id: O1
#   name_zh: 数据契约声明（4 类）
#   name_en: data classes
#   intro: MaturityLevel, IDESource, RbacRole, AgentIdentity
#   downstream: zephyr.security.access_control.identity;zephyr.infrastructure.escalation;zephyr…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import hashlib
import hmac
import time
from enum import Enum
from typing import Final

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


class RbacRole(str, Enum):
    # P1-3: AgentRole → RbacRole（消除与 RoutingRole/ArbitrationRole/MultiAgentRole 同名冲突）
    # 合并 shared 版（AUDITOR）+ security 版（REVIEWER）为 7 成员，值统一小写
    READER = "reader"
    WRITER = "writer"
    EXECUTOR = "executor"
    ADMIN = "admin"
    AUDITOR = "auditor"
    REVIEWER = "reviewer"
    AUTONOMOUS_AGENT = "autonomous_agent"


# P1-3 兼容层：旧名 AgentRole 保留为 RbacRole 别名，标 DEPRECATED + TTL task_bound
# 消费方迁移期内可继续用 AgentRole，过渡期后由 reconciler 清理
AgentRole = RbacRole  # noqa: F811  # [DEPRECATED] [TTL] task_bound — P1-3 兼容层


ROLE_DEFAULT_PERMISSIONS: Final[dict[RbacRole, list[str]]] = {
    RbacRole.READER: [
        "read:docs",
        "read:src",
        "read:tests",
        "read:config",
        "read:logs",
        "read:data",
    ],
    RbacRole.WRITER: [
        "read:docs",
        "read:src",
        "read:tests",
        "write:src",
        "write:tests",
        "read:config",
        "read:logs",
        "read:data",
    ],
    RbacRole.EXECUTOR: [
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
    RbacRole.ADMIN: [
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
    RbacRole.AUDITOR: [
        "read:docs",
        "read:src",
        "read:tests",
        "read:config",
        "read:logs",
        "read:data",
        "read:audit",
        "audit:full",
    ],
    RbacRole.REVIEWER: [
        "read:docs",
        "read:src",
        "read:tests",
        "read:config",
        "review:code",
        "approve:merge",
    ],
    RbacRole.AUTONOMOUS_AGENT: [
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
}


MATURITY_TLB_LIMITS: Final[dict[MaturityLevel, int]] = {
    MaturityLevel.L0_INTERN: 100,
    MaturityLevel.L1_JUNIOR: 500,
    MaturityLevel.L2_REGULAR: 2000,
    MaturityLevel.L3_SENIOR: 10000,
    MaturityLevel.L4_PRINCIPAL: 50000,
}

MATURITY_AUTO_GUARD_TIMEOUT: Final[dict[MaturityLevel, int]] = {
    MaturityLevel.L0_INTERN: 300,
    MaturityLevel.L1_JUNIOR: 300,
    MaturityLevel.L2_REGULAR: 600,
    MaturityLevel.L3_SENIOR: 1800,
    MaturityLevel.L4_PRINCIPAL: 7200,
}


class AgentIdentity(BaseModel):
    session_id: str
    maturity: MaturityLevel = MaturityLevel.L0_INTERN
    role: RbacRole = RbacRole.WRITER
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
