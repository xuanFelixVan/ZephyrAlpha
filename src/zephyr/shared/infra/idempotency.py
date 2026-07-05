# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.infra.idempotency
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_idempotency | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
idempotency.py —— 幂等性基础设施（Phase 8 新增 | 盲点 B15 修复）

痛点修复：cross_layer_contracts.yaml 定了 idempotency_key 字段，但没有幂等性存储/检查的实现——
  1. AI agent 重复发送相同的 API 请求 → 重复扣费 / 重复创建资源
  2. 网络重试导致重复处理同一个事件 → 数据不一致
  3. Stripe / AWS 等平台都内置幂等性——ZephyrAlpha 缺少这个基础设施

设计对标：
  - Stripe Idempotency-Key（最多保留 24h，相同 key 返回缓存结果）
  - AWS Lambda 幂等性（Event Source Mapping + idempotency）
  - IETF HTTP Idempotency-Key draft（I-D draft-idempotency-header-01）

设计原则：
  - key-value 存储——key → (status, result) 映射
  - 结果缓存——相同 key 直接返回之前的结果
  - TTL——过期后清理避免内存膨胀
  - async-first

AI 施工约定：
  - 任何可能产生副作用的操作 MUST 带 idempotency_key
  - 幂等性存储 SHOULD 配置合理的 TTL（默认 24h，与 Stripe 对齐）

SSoT: MOD-INF-016 §2.14 shared-idempotency
Version: 0.1.0
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Any

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "IdempotencyError",
    "IdempotencyRecord",
    "IdempotencyStatus",
    "IdempotencyStore",
]

logger = logging.getLogger(__name__)


class IdempotencyError(ZephyrBaseError):
    """幂等性冲突——相同 key 产生了不同结果或状态不一致。"""


@unique
class IdempotencyStatus(str, Enum):
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass
class IdempotencyRecord:
    key: str
    status: IdempotencyStatus
    result: Any = None
    created_at: float = field(default_factory=time.monotonic)
    completed_at: float = 0.0


class IdempotencyStore:
    """幂等性 key-value 存储——防止重复操作。

    对标 Stripe Idempotency-Key：24h TTL，相同 key 返回缓存结果。

    Usage::

        store = IdempotencyStore(default_ttl_seconds=86400)

        async with store.operation("req-abc123") as record:
            if record.status == IdempotencyStatus.COMPLETED:
                return record.result  # 直接返回缓存结果

            result = await do_work()
            record.result = result
            record.status = IdempotencyStatus.COMPLETED
            return result
    """

    def __init__(self, default_ttl_seconds: int = 86400) -> None:
        self._records: dict[str, IdempotencyRecord] = {}
        self._default_ttl = default_ttl_seconds

    def _cleanup_expired(self) -> None:
        now = time.monotonic()
        expired = [
            k
            for k, rec in self._records.items()
            if rec.completed_at > 0 and (now - rec.completed_at) > self._default_ttl
        ]
        for k in expired:
            del self._records[k]
        if expired:
            logger.debug("idempotency: cleaned up %d expired records", len(expired))

    def get(self, key: str) -> IdempotencyRecord | None:
        self._cleanup_expired()
        record = self._records.get(key)
        if record is None:
            return None
        if record.status == IdempotencyStatus.COMPLETED:
            elapsed = time.monotonic() - record.completed_at
            if elapsed > self._default_ttl:
                del self._records[key]
                return None
        return record

    def start(self, key: str) -> IdempotencyRecord:
        self._cleanup_expired()

        existing = self._records.get(key)
        if existing is not None:
            if existing.status == IdempotencyStatus.PROCESSING:
                raise IdempotencyError(
                    f"idempotency key '{key}' is already being processed",
                    details={"key": key, "status": existing.status.value},
                )
            return existing

        record = IdempotencyRecord(key=key, status=IdempotencyStatus.PROCESSING)
        self._records[key] = record
        return record

    def complete(self, key: str, result: Any) -> IdempotencyRecord:
        record = self._records.get(key)
        if record is None:
            raise IdempotencyError(
                f"idempotency key '{key}' not found—call start() first",
                details={"key": key},
            )
        record.status = IdempotencyStatus.COMPLETED
        record.result = result
        record.completed_at = time.monotonic()
        return record

    def fail(self, key: str) -> IdempotencyRecord:
        record = self._records.get(key)
        if record is None:
            raise IdempotencyError(
                f"idempotency key '{key}' not found—call start() first",
                details={"key": key},
            )
        record.status = IdempotencyStatus.FAILED
        record.completed_at = time.monotonic()
        return record

    @property
    def size(self) -> int:
        self._cleanup_expired()
        return len(self._records)


def _build_idempotency_key(prefix: str, *parts: str) -> str:
    """构建确定性幂等键——前缀 + SHA256 前 16 字符。"""
    raw = "|".join(parts)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{prefix}:{digest}"
