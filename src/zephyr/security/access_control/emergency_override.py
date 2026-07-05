# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.emergency_override
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] token expires_at strictly > issue time; verify returns dict with valid key; one-time use
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] issue() never raises; verify() returns dict, never raises
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_emergency_override | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""EmergencyOverride — 紧急覆盖令牌管理.

依据蓝图 MOD-INF-018 §3:
- 紧急情况下签发临时权限令牌
- 令牌有过期时间，过期后失效
- 令牌为一次性使用，验证后即消耗
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

_MAX_DURATION_SECONDS = 300
_DEFAULT_DURATION_SECONDS = 300


@dataclass
class OverrideToken:
    """紧急覆盖令牌.

    Attributes:
        token_id: 令牌 ID（以 EMG- 开头）
        token_hash: 令牌哈希
        issued_by: 签发者
        permissions: 权限列表
        max_duration_seconds: 最大有效时长（秒）
        expires_at: 过期时间戳
        issued_at: 签发时间戳
        used: 是否已使用
        revoked: 是否已撤销
    """

    token_id: str
    token_hash: str = ""
    issued_by: str = ""
    permissions: list[str] = field(default_factory=list)
    max_duration_seconds: float = _MAX_DURATION_SECONDS
    expires_at: float = 0.0
    issued_at: float = 0.0
    used: bool = False
    revoked: bool = False


class EmergencyOverride:
    """紧急覆盖管理器 — 签发与验证临时权限令牌."""

    def __init__(self) -> None:
        self._tokens: dict[str, OverrideToken] = {}

    def issue(
        self,
        issued_by: str,
        permissions: list[str],
        duration_seconds: float = _DEFAULT_DURATION_SECONDS,
    ) -> OverrideToken:
        """签发紧急令牌.

        Args:
            issued_by: 签发者标识
            permissions: 授予的权限列表
            duration_seconds: 有效时长（秒），上限 300

        Returns:
            OverrideToken 签发的令牌
        """
        capped_duration = min(duration_seconds, _MAX_DURATION_SECONDS)
        now = time.time()
        raw_id = uuid.uuid4().hex
        token_hash = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()
        token = OverrideToken(
            token_id=f"EMG-{raw_id}",
            token_hash=token_hash,
            issued_by=issued_by,
            permissions=list(permissions),
            max_duration_seconds=capped_duration,
            expires_at=now + capped_duration,
            issued_at=now,
            used=False,
            revoked=False,
        )
        self._tokens[token.token_id] = token
        logger.info(
            "EmergencyOverride: token issued by '%s' (perms=%s, expires_in=%ss)",
            issued_by,
            permissions,
            capped_duration,
        )
        return token

    def verify(self, token_id: str) -> dict[str, Any]:
        """验证令牌.

        Args:
            token_id: 令牌 ID

        Returns:
            dict 包含 valid 标志和相关信息
        """
        token = self._tokens.get(token_id)
        if token is None:
            return {"valid": False, "reason": "token_not_found"}
        if token.revoked:
            return {"valid": False, "reason": "token_revoked"}
        if token.used:
            return {"valid": False, "reason": "token_already_used"}
        if time.time() > token.expires_at:
            return {"valid": False, "reason": "token_expired"}

        token.used = True
        return {
            "valid": True,
            "permissions": list(token.permissions),
            "issued_by": token.issued_by,
            "token_id": token.token_id,
        }

    def revoke(self, token_id: str) -> dict[str, Any]:
        """撤销令牌.

        Args:
            token_id: 令牌 ID

        Returns:
            dict 包含 revoked 标志
        """
        token = self._tokens.get(token_id)
        if token is None:
            return {"revoked": False, "reason": "token_not_found"}
        token.revoked = True
        # 5.63.1 修复：token_id在info级别持久化到日志，若日志被聚合到外部系统可被关联追踪。
        # 降为debug级别 + 脱敏为 tok_***1234 格式。
        masked = f"tok_***{token_id[-4:]}" if len(token_id) > 4 else "tok_***"
        logger.debug("EmergencyOverride: token '%s' revoked", masked)
        return {"revoked": True, "token_id": token_id}


class EmergencyToken:
    """EmergencyToken — 兼容别名.

    保留以兼容旧导入路径，用于直接构造。
    """

    def __init__(
        self,
        issued_by: str = "",
        permissions: list[str] | None = None,
        max_duration_seconds: float = _MAX_DURATION_SECONDS,
    ) -> None:
        raw_id = uuid.uuid4().hex
        self.token_id = f"EMG-{raw_id}"
        self.issued_by = issued_by
        self.permissions = permissions if permissions is not None else []
        self.max_duration_seconds = max_duration_seconds
        self.used = False
        self.revoked = False


__all__ = [
    "EmergencyOverride",
    "EmergencyToken",
    "OverrideToken",
]
