# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.non_repudiation
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py; tests/agent_rbac/test_forensic_a.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] sign returns AuditEntry with non-None hmac_hash; verify(entry) returns dict-like with ["verified"] key; truthy when verified
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] sign/verify never raise; verify returns {"verified": False} on tampered data or missing hmac_hash
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py; tests/agent_rbac/test_forensic_a.py
# [A_module] module_id=MOD-SEC_non_repudiation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""NonRepudiation — 不可抵赖性审计签名.

依据蓝图 MOD-INF-018 §3:
- 对 agent 操作进行 HMAC 签名，确保审计日志不可抵赖
- sign() 生成带 hmac_hash 的 AuditEntry
- verify() 校验签名完整性
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Any


class VerifyResult(dict):
    """验证结果 — 支持 result["verified"] 下标访问，同时支持 bool 上下文."""

    def __bool__(self) -> bool:
        # 5.124.2 修复：显式 bool() 包装，确保 __bool__ 协议返回 True/False。
        # self.get("verified", False) 的值可能是字符串或其他类型，直接返回违反协议。
        return bool(self.get("verified", False))

    def __len__(self) -> int:
        # 5.108.3 修复: __len__ 与 __bool__ 语义一致,避免 bool(VerifyResult) vs len(VerifyResult) 矛盾
        # 原 dict.__len__ 返回键数量,与 __bool__ 返回 verified 值不一致
        return 1 if bool(self.get("verified", False)) else 0


@dataclass
class AuditEntry:
    """审计日志条目."""

    operation: str
    agent_id: str
    timestamp: float
    hmac_hash: str
    data: str


class NonRepudiation:
    """不可抵赖性签名器."""

    def __init__(self, secret: str | None = None) -> None:
        self._secret = secret or "zephyr-non-repudiation-default-secret"

    def _build_payload(self, operation: str, agent_id: str, timestamp: float, data: str) -> bytes:
        return f"{operation}|{agent_id}|{timestamp:.6f}|{data}".encode("utf-8")

    def sign(self, operation: str, agent_id: str, data: str = "") -> AuditEntry:
        """签名操作，返回带 hmac_hash 的 AuditEntry."""
        timestamp = time.time()
        payload = self._build_payload(operation, agent_id, timestamp, data)
        digest = hmac.new(
            self._secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return AuditEntry(
            operation=operation,
            agent_id=agent_id,
            timestamp=timestamp,
            hmac_hash=digest,
            data=data,
        )

    def verify(self, entry: AuditEntry) -> VerifyResult:
        """验证 AuditEntry 签名.

        Returns:
            VerifyResult: {"verified": bool, "reason": str}
            支持 result["verified"] 下标访问，同时支持 bool(result) 上下文判断。
        """
        if entry is None:
            return VerifyResult(verified=False, reason="entry is None")
        if not entry.hmac_hash:
            return VerifyResult(verified=False, reason="missing hmac_hash")
        payload = self._build_payload(
            entry.operation,
            entry.agent_id,
            entry.timestamp,
            entry.data,
        )
        expected = hmac.new(
            self._secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        if hmac.compare_digest(expected, entry.hmac_hash):
            return VerifyResult(verified=True, reason="signature valid")
        return VerifyResult(verified=False, reason="signature mismatch — tampered")


__all__ = [
    "AuditEntry",
    "NonRepudiation",
    "VerifyResult",
]
