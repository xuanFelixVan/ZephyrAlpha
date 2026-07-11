# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.governance.kb.storage.unified_memory_api
# [DOMAIN] D_GOV_KB
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.shared.security.capability
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
# [A_module] module_id=MOD-DAT_unified_memory_api | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模块封装）
====================================================
任务编号 : T-V2-007（experimental RI-02）
权限层级 : Human-Gated（M2 ChromaDB 操作 = 关键架构变更，R84 修正）
真源声明 : ai_autonomy_authority_registry.yaml §2.9（RI-01~07）+ §2.10（三件套）
关联决策 : rationale-log R84（RI-02/03 偏松 -> Human-Gated 修正）
           B6 §2.4（RI-02 设计）
创建日期 : 2026-04-27
版本     : v1.0.0

功能说明
--------
封装 ChromaDB 调用为统一三件套 API，向 M1/M3/M4 等模块提供"切换底层不影响调用方"的记忆层：

1. ``kb.recall(topic, k=5)``   —— 按 topic 召回最近 K 条记录（不做相似度，按时间倒序）
2. ``kb.write(topic, content, provenance)`` —— 写入并强制 provenance（缺失抛 WriteTraceMissing）
3. ``kb.search(query, k=5)``   —— 跨 topic 的语义相似度检索

设计原则
--------
- **底层切换可替换**：默认 ``InMemoryMemoryBackend``（VMS 不可用时使用）
- **provenance 强制**：``write()`` 必传 ``WriteTrace``（origin / audit_chain[≥1] / arbitration）
- **CBAC 集成**：``write()`` 调用 ``capability_check("write_kb", f"unified_memory/{topic}")``
- **Pydantic v2 frozen**：``WriteTrace`` 一旦构建即不可变（防回填污染）
- **experimental 嵌入选型**：bge-small-zh-v1.5（中文优先）-> all-MiniLM-L6-v2（fallback）-> Mock（兜底）

集合 schema（不可变，beta 升级须经 Owner 审批）
------------------------------------------------
Collection: ``unified_memory``
- ids:        ``f"{topic}::{ts_safe}::{uuid12}"``
- documents:  ``content`` 原文
- metadatas:  {topic, origin, audit_chain_csv, arbitration, written_at, ...}

不依赖关系
----------
- 不直接 import M1 / M3 / M4 模块（避免循环依赖）
- 通过 ``get_chroma_client()`` 复用 ChromaDB 单例
"""

from __future__ import annotations

from typing import Final
import logging
import threading
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from zephyr.governance.kb.storage._backend_protocol import (
    InMemoryMemoryBackend,
    MemoryBackend,
    MemoryBackendError,
    MemoryRecord,
)
from zephyr.shared.security.capability import capability_check

__all__ = [
    "UNIFIED_COLLECTION",
    "InMemoryMemoryBackend",
    "MemoryBackend",
    "MemoryBackendError",
    "MemoryRecord",
    "UnifiedMemoryAPI",
    "WriteTrace",
    "WriteTraceMissing",
    "build_provenance",
    "get_unified_memory_api",
]

_logger = logging.getLogger(__name__)
_UTC = UTC

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

UNIFIED_COLLECTION: Final[str] = "unified_memory"
"""ChromaDB 中承载 RI-02 跨模块记忆的集合名（不可变 schema）。"""

# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------


class WriteTraceMissing(Exception):
    """``kb.write()`` 缺失或 provenance 字段不完整时抛出。

    参数
    ----
    topic
        触发异常的写入主题（用于审计追踪）。
    detail
        缺失字段的具体原因描述。
    """

    def __init__(self, topic: str, detail: str = "provenance is required") -> None:
        self.topic = topic
        self.detail = detail
        super().__init__(f"WriteTraceMissing: topic='{topic}' — {detail}")


# ---------------------------------------------------------------------------
# Pydantic 数据模型
# ---------------------------------------------------------------------------


class WriteTrace(BaseModel):
    """RI-02 写入溯源（Pydantic v2 frozen 不可变）。

    字段
    ----
    origin
        来源标识，建议格式 ``"<module>:<task_id>"`` 或 ``"<module>:<reason>"``，
        例如 ``"M1:doc_compressor"``、``"M4:reflection_loop:R84"``。
    audit_chain
        审计链路列表，至少 1 项（如 ``["T-V2-007", "RI-02"]``）。
    arbitration
        关键架构裁决标识（可选），如 ``"R84"`` 表示 rationale-log 决策编号。
    """

    model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)

    origin: str = Field(min_length=1, max_length=200, description="来源模块/任务标识")
    audit_chain: list[str] = Field(min_length=1, description="审计链路（至少 1 项）")
    arbitration: str | None = Field(default=None, max_length=100, description="架构裁决标识")


# ---------------------------------------------------------------------------
# UnifiedMemoryAPI — 三件套公开接口
# ---------------------------------------------------------------------------


class UnifiedMemoryAPI:
    """RI-02 统一记忆 API（三件套：recall / write / search）。

    生产用法
    --------
        from zephyr.governance.kb.unified_memory_api import get_unified_memory_api, build_provenance

        kb = get_unified_memory_api()
        prov = build_provenance(origin="M1:doc_compressor", audit_chain=["T-V2-006"])
        chunk_id = kb.write(topic="compression_history", content="...", provenance=prov)
        records = kb.recall(topic="compression_history", k=5)
        hits = kb.search(query="如何避免压缩失败", k=3)

    参数
    ----
    backend
        ``MemoryBackend`` 实例；默认惰性构建 ``InMemoryMemoryBackend``。
    enforce_capability
        是否启用 CBAC 校验；默认 True。
        测试可传 False 避免依赖 ``capabilities.yaml`` 中的 ``write_kb`` 规则。
    """

    def __init__(
        self,
        backend: MemoryBackend | None = None,
        *,
        enforce_capability: bool = True,
    ) -> None:
        self._backend: MemoryBackend = backend or InMemoryMemoryBackend()
        self._enforce_cbac = enforce_capability

    @property
    def backend(self) -> MemoryBackend:
        return self._backend

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def write(
        self,
        topic: str,
        content: str,
        provenance: WriteTrace,
    ) -> str:
        """写入一条记忆，强制 provenance 校验。

        Parameters
        ----------
        topic : str
            记忆主题（必填，非空），作为 metadata.topic 写入。
        content : str
            记忆内容（必填，非空）。
        provenance : WriteTrace
            写入溯源（必填）；缺失或类型错误抛 ``WriteTraceMissing``。

        Returns
        -------
        str
            后端生成的 ``chunk_id``。

        Raises
        ------
        WriteTraceMissing
            provenance 为 None / 非 WriteTrace 实例 / audit_chain 为空。
        zephyr.shared.capability.CapabilityDenied
            CBAC 规则拒绝该 topic 写入（``enforce_capability=True`` 时）。
        MemoryBackendError
            底层后端写入失败。
        """
        topic = (topic or "").strip()
        content = content or ""
        if not topic:
            raise ValueError("topic 不得为空")
        if not content.strip():
            raise ValueError("content 不得为空")

        if provenance is None or not isinstance(provenance, WriteTrace):
            raise WriteTraceMissing(
                topic=topic,
                detail="provenance must be a WriteTrace instance (origin / audit_chain / arbitration)",
            )
        if not provenance.audit_chain:
            raise WriteTraceMissing(
                topic=topic,
                detail="audit_chain must contain at least 1 entry",
            )

        if self._enforce_cbac:
            capability_check("write_kb", f"unified_memory/{topic}")

        now = datetime.now(_UTC).isoformat()
        ts_safe = now.replace(":", "-").replace("+", "Z").split("Z")[0]
        chunk_id = f"{topic}::{ts_safe}::{uuid.uuid4().hex[:12]}"
        meta = {
            "origin": provenance.origin,
            "audit_chain": list(provenance.audit_chain),
            "arbitration": provenance.arbitration or "",
        }
        record = MemoryRecord(
            chunk_id=chunk_id,
            topic=topic,
            content=content,
            score=1.0,
            written_at=now,
            metadata=meta,
        )
        return self._backend.write(record)

    def recall(self, topic: str, k: int = 5) -> list[MemoryRecord]:
        """按 topic 召回最近 K 条记忆（按 ``written_at`` 倒序）。

        Parameters
        ----------
        topic : str
            主题（必填）。
        k : int
            返回条数上限；默认 5；负数视为 0。

        Returns
        -------
        list[MemoryRecord]
            按写入时间倒序的记忆列表，长度 ≤ k。
        """
        topic = (topic or "").strip()
        if not topic:
            return []
        try:
            return self._backend.list_by_topic(topic, k=max(0, k))
        except MemoryBackendError as exc:
            _logger.warning("UnifiedMemoryAPI.recall(%s) backend error: %s", topic, exc)
            return []

    def search(
        self,
        query: str,
        k: int = 5,
        topic: str | None = None,
    ) -> list[MemoryRecord]:
        """跨 topic 的语义相似度检索。

        Parameters
        ----------
        query : str
            自然语言查询（必填）。
        k : int
            返回条数上限；默认 5。
        topic : str | None
            限定主题；None 表示跨所有主题。

        Returns
        -------
        list[MemoryRecord]
            按相似度降序的命中列表，长度 ≤ k。
        """
        query = (query or "").strip()
        if not query:
            return []
        try:
            return self._backend.query(query, k=max(0, k), topic=topic)
        except MemoryBackendError as exc:
            _logger.warning("UnifiedMemoryAPI.search(%r) backend error: %s", query, exc)
            return []

    def count(self) -> int:
        """返回当前后端的记忆总数（-1 表示不可用）。"""
        try:
            return int(self._backend.count())
        except Exception:
            return -1


# ---------------------------------------------------------------------------
# 模块级单例与辅助函数
# ---------------------------------------------------------------------------

_singleton_lock = threading.RLock()
_singleton_api: UnifiedMemoryAPI | None = None


def get_unified_memory_api(
    *,
    backend: MemoryBackend | None = None,
    enforce_capability: bool = True,
    reset: bool = False,
    prefer_vms: bool = True,
) -> UnifiedMemoryAPI:
    """返回 UnifiedMemoryAPI 模块级单例（线程安全）。

    参数
    ----
    backend
        指定后端；None 时按 prefer_vms 策略自动选择。
    enforce_capability
        是否启用 CBAC 校验；默认 True。
    reset
        强制重建单例（仅测试使用）。
    prefer_vms
        当 backend=None 时是否优先使用 VMS 后端；默认 True。
        VMS 不可用时自动降级到 InMemoryMemoryBackend。
    """
    global _singleton_api
    with _singleton_lock:
        if reset or _singleton_api is None:
            resolved_backend = backend
            if resolved_backend is None and prefer_vms:
                try:
                    from zephyr.governance.kb.vms_memory_backend import create_vms_backend

                    resolved_backend = create_vms_backend()
                    _logger.info("get_unified_memory_api: using VMSMemoryBackend")
                except Exception as exc:
                    _logger.info("get_unified_memory_api: VMS unavailable, falling back to ChromaDB: %s", exc, exc_info=True)
            _singleton_api = UnifiedMemoryAPI(
                backend=resolved_backend,
                enforce_capability=enforce_capability,
            )
        return _singleton_api


def reset_unified_memory_api() -> None:
    """重置模块级单例（仅测试使用）。"""
    global _singleton_api
    with _singleton_lock:
        _singleton_api = None


def build_provenance(
    *,
    origin: str,
    audit_chain: list[str],
    arbitration: str | None = None,
) -> WriteTrace:
    """便捷构造器：避免调用方重复 import WriteTrace。

    示例
    ----
        prov = build_provenance(
            origin="M3:trigger_router",
            audit_chain=["T-V2-007", "RI-03"],
            arbitration="R84",
        )
    """
    return WriteTrace(origin=origin, audit_chain=audit_chain, arbitration=arbitration)
