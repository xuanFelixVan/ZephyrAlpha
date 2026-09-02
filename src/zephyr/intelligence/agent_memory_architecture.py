# [BLUEPRINT] MOD-INT-AGENT-MEMORY | docs/03_modules/_domain_intelligence/agent_memory_architecture/blueprint.md | §0-5
# [MODULE] zephyr.intelligence.agent_memory_architecture
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.shared.foundation.errors(ZephyrBaseError)
# [CONSUMERS] 运行时装配批（四层 backend 装配 / 策略声明式配置注入）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定核心纯内存无IO; 策略声明式非法即拒; 巩固方向恒working→episodic→semantic; 程序记忆恒人工登记源; 淘汰/遗忘判定确定性; 零密钥字段
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/agent_memory_architecture/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidMemoryPolicyError(ZA-IT-0021); MemoryBackendMissingError(ZA-IT-0022)
# [TESTS] tests/intelligence/test_agent_memory_architecture.py
# [A_module] module_id=MOD-INT-AGENT-MEMORY | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""AgentMemoryArchitecture — Agent 四层记忆架构（MOD-INT-AGENT-MEMORY）。

B11-02457（AUD-DRAFT-001-DIGEST P1 波 W-P1-10，§0边界声明/§7）：四层记忆
统一模型 + 五阶段流水线接口统一 + 各层 TTL/淘汰策略声明式配置。

查重裁定：不复制 memory_bank（持久上下文存储件）、unified_memory_api
（ChromaDB 知识库）、in_process_vector_memory（VMS FAISS 入口）、reflexion
（三角色骨架）；情景层后端与 B11-02613 episodic_memory_store 同波接口对齐。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_log = logging.getLogger(__name__)

__all__: Final = [
    "AgentMemoryArchitecture",
    "EvictionDecision",
    "InvalidMemoryPolicyError",
    "MemoryBackendMissingError",
    "MemoryItem",
    "MemoryLayer",
    "MemoryPolicy",
    "PipelineStage",
]


class MemoryLayer(Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class PipelineStage(Enum):
    ENCODE = "encode"
    STORE = "store"
    RETRIEVE = "retrieve"
    CONSOLIDATE = "consolidate"
    FORGET = "forget"


class InvalidMemoryPolicyError(ZephyrBaseError):
    """策略配置非法（Fail-Closed）。"""

    error_code = "ZA-IT-0021"


class MemoryBackendMissingError(ZephyrBaseError):
    """层 backend 未注入（Fail-Closed）。"""

    error_code = "ZA-IT-0022"


@dataclass(frozen=True)
class MemoryPolicy:
    """层策略（声明式）。"""

    ttl_seconds: int
    max_entries: int
    eviction: str  # "lru" | "fifo"

    def __post_init__(self) -> None:
        if self.ttl_seconds <= 0:
            raise InvalidMemoryPolicyError(f"ttl_seconds 非正: {self.ttl_seconds}")
        if self.max_entries <= 0:
            raise InvalidMemoryPolicyError(f"max_entries 非正: {self.max_entries}")
        if self.eviction not in ("lru", "fifo"):
            raise InvalidMemoryPolicyError(f"未知淘汰策略: {self.eviction}")


@dataclass(frozen=True)
class MemoryItem:
    """记忆条目。"""

    item_id: str
    layer: str
    content: str
    metadata: dict[str, Any]
    created_at: float
    last_accessed_at: float


@dataclass(frozen=True)
class EvictionDecision:
    """淘汰判定。"""

    layer: str
    evicted_ids: tuple[str, ...]
    reasons: tuple[str, ...]


def _now() -> float:
    import time

    return time.time()


class AgentMemoryArchitecture:
    """四层记忆统一接口层（纯内存，无 IO）。"""

    def __init__(
        self,
        policies: dict[str, MemoryPolicy] | None = None,
        backends: dict[str, Any] | None = None,
    ) -> None:
        self._policies: dict[str, MemoryPolicy] = policies or {}
        self._backends: dict[str, Any] = backends or {}
        self._ledger: dict[str, list[MemoryItem]] = {}

    def policy_of(self, layer: str) -> MemoryPolicy:
        if layer not in self._policies:
            raise InvalidMemoryPolicyError(f"层 {layer} 无策略配置")
        return self._policies[layer]

    def encode(self, item_id: str, layer: str, content: str, metadata: dict[str, Any] | None = None) -> MemoryItem:
        if not content:
            raise ValueError("content 不能为空")
        if layer not in {m.value for m in MemoryLayer}:
            raise ValueError(f"未知记忆层: {layer}")
        now = _now()
        return MemoryItem(
            item_id=item_id,
            layer=layer,
            content=content,
            metadata=metadata or {},
            created_at=now,
            last_accessed_at=now,
        )

    def store(self, item: MemoryItem) -> EvictionDecision:
        layer = item.layer
        policy = self.policy_of(layer)
        backend = self._backends.get(layer)
        if backend is None:
            raise MemoryBackendMissingError(f"层 {layer} 无 backend")
        ledger_layer = self._ledger.setdefault(layer, [])
        ledger_layer.append(item)
        evicted: list[str] = []
        reasons: list[str] = []
        if len(ledger_layer) > policy.max_entries:
            if policy.eviction == "lru":
                sorted_items = sorted(ledger_layer, key=lambda x: x.last_accessed_at)
            else:
                sorted_items = sorted(ledger_layer, key=lambda x: x.created_at)
            to_remove = len(ledger_layer) - policy.max_entries
            for i in range(to_remove):
                evicted.append(sorted_items[i].item_id)
                reasons.append(f"{policy.eviction} 淘汰超容")
            self._ledger[layer] = sorted_items[to_remove:]
        try:
            backend.store(item)
        except Exception as exc:
            _log.warning("backend store 异常（不阻断台账）: %s", exc)
        return EvictionDecision(
            layer=layer,
            evicted_ids=tuple(evicted),
            reasons=tuple(reasons),
        )

    def retrieve(self, query: str, layer: str, k: int) -> list[MemoryItem]:
        if k <= 0:
            raise ValueError(f"k 必须为正: {k}")
        backend = self._backends.get(layer)
        if backend is None:
            raise MemoryBackendMissingError(f"层 {layer} 无 backend")
        try:
            hits = backend.retrieve(query, k)
        except Exception as exc:
            _log.warning("backend retrieve 异常: %s", exc)
            hits = []
        now = _now()
        updated = []
        for item in hits:
            updated.append(item)
            # 刷新访问时间（纯内存，不修改 frozen dataclass——重建）
            updated[-1] = MemoryItem(
                item_id=item.item_id,
                layer=item.layer,
                content=item.content,
                metadata=item.metadata,
                created_at=item.created_at,
                last_accessed_at=now,
            )
        self._ledger[layer] = [
            updated[-1] if h.item_id == updated[-1].item_id else h for h in self._ledger.get(layer, [])
        ]
        return updated

    def consolidate(self, item: MemoryItem, from_layer: str, to_layer: str) -> MemoryItem:
        order = {"working": 0, "episodic": 1, "semantic": 2, "procedural": 3}
        if order.get(from_layer, -1) >= order.get(to_layer, -1):
            raise ValueError(f"非法巩固方向: {from_layer} -> {to_layer}")
        if to_layer == "procedural" and item.metadata.get("source") != "manual":
            raise ValueError("程序记忆只接受人工登记源")
        return self.encode(
            item_id=item.item_id,
            layer=to_layer,
            content=item.content,
            metadata={**item.metadata, "consolidated_from": from_layer},
        )

    def forget(self, layer: str) -> EvictionDecision:
        policy = self.policy_of(layer)
        now = _now()
        ledger_layer = self._ledger.get(layer, [])
        expired = [item for item in ledger_layer if now - item.created_at > policy.ttl_seconds]
        evicted = [item.item_id for item in expired]
        reasons = [f"TTL 过期({policy.ttl_seconds}s)"] * len(expired)
        remaining = [item for item in ledger_layer if item not in expired]
        self._ledger[layer] = remaining
        backend = self._backends.get(layer)
        if backend is not None:
            try:
                for item in expired:
                    backend.delete(item.item_id)
            except Exception as exc:
                _log.warning("backend delete 异常: %s", exc)
        return EvictionDecision(
            layer=layer,
            evicted_ids=tuple(evicted),
            reasons=tuple(reasons),
        )
