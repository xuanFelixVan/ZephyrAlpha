# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] zephyr.data.knowledge_management.kb.storage.unified_memory_api
# [DOMAIN] D-GOVERNANCE
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
# [TTL] task_bound

"""
UnifiedMemoryAPI — RI-02 统一记忆 API（M2 跨模块封装）
====================================================
任务编号 : T-V2-007（experimental RI-02）
权限层级 : Human-Gated（M2 ChromaDB 操作 = 关键架构变更，R84 修正）
真源声明 : ai_autonomy_authority_registry.yaml §2.9（RI-01~07）+ §2.10（三件套）
关联决策 : rationale-log R84（RI-02/03 偏松 → Human-Gated 修正）
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
- **底层切换可替换**：默认 ``ChromaMemoryBackend``；ChromaDB 不可用时降级 ``InMemoryMemoryBackend``
- **provenance 强制**：``write()`` 必传 ``WriteTrace``（origin / audit_chain[≥1] / arbitration）
- **CBAC 集成**：``write()`` 调用 ``capability_check("write_kb", f"unified_memory/{topic}")``
- **Pydantic v2 frozen**：``WriteTrace`` 一旦构建即不可变（防回填污染）
- **experimental 嵌入选型**：bge-small-zh-v1.5（中文优先）→ all-MiniLM-L6-v2（fallback）→ Mock（兜底）

集合 schema（不可变，beta 升级须经 Owner 审批）
------------------------------------------------
Collection: ``unified_memory``
- ids:        ``f"{topic}::{ts_safe}::{uuid12}"``
- documents:  ``content`` 原文
- metadatas:  {topic, origin, audit_chain_csv, arbitration, written_at, ...}

不依赖关系
----------
- 不直接 import M1 / M3 / M4 模块（避免循环依赖）
- 通过 ``get_chroma_client()`` 复用 ChromaDB 单例（与 kb_repo 共享）
"""

from __future__ import annotations

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
    "DEFAULT_EMBEDDING_MODELS",
    "UNIFIED_COLLECTION",
    "ChromaMemoryBackend",
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

UNIFIED_COLLECTION: str = "unified_memory"
"""ChromaDB 中承载 RI-02 跨模块记忆的集合名（不可变 schema）。"""

DEFAULT_EMBEDDING_MODELS: tuple[str, ...] = (
    "BAAI/bge-small-zh-v1.5",
    "sentence-transformers/all-MiniLM-L6-v2",
)
"""嵌入模型尝试顺序：中文优先（bge）→ 通用回退（MiniLM）→ Mock（InMemoryBackend）。"""

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
# ChromaMemoryBackend — 默认生产后端
# ---------------------------------------------------------------------------


class ChromaMemoryBackend:
    """ChromaDB 持久化后端（生产默认）。

    参数
    ----
    collection_name
        ChromaDB collection 名称；默认 ``UNIFIED_COLLECTION``。
    persist_dir
        ChromaDB 存储根目录；None 时使用 ``chromadb_init`` 默认值。
    embedding_models
        嵌入模型尝试顺序；首个成功加载者生效。
    score_threshold
        ``query()`` 的最低相似度阈值（0-1），低于该值不返回。
    """

    def __init__(
        self,
        collection_name: str = UNIFIED_COLLECTION,
        persist_dir: Any | None = None,
        embedding_models: tuple[str, ...] = DEFAULT_EMBEDDING_MODELS,
        score_threshold: float = 0.0,
    ) -> None:
        self._collection_name = collection_name
        self._persist_dir = persist_dir
        self._embedding_models = embedding_models
        self._score_threshold = score_threshold
        self._collection: Any | None = None
        self._lock = threading.RLock()

    def _ensure_collection(self) -> Any:
        """惰性初始化 collection；失败时抛 MemoryBackendError。"""
        with self._lock:
            if self._collection is not None:
                return self._collection
            try:
                from zephyr.governance.kb.storage.chromadb_init import get_chroma_client
            except Exception as exc:
                raise MemoryBackendError(f"chromadb_init import failed: {exc}") from exc

            try:
                client = get_chroma_client(self._persist_dir)
            except Exception as exc:
                raise MemoryBackendError(f"ChromaDB client init failed: {exc}") from exc

            embedding_fn = self._build_embedding_function()

            try:
                kwargs: dict[str, Any] = {
                    "name": self._collection_name,
                    "metadata": {"hnsw:space": "cosine", "schema_version": "1.0.0"},
                }
                if embedding_fn is not None:
                    kwargs["embedding_function"] = embedding_fn
                if hasattr(client, "get_or_create_collection"):
                    self._collection = client.get_or_create_collection(**kwargs)
                else:
                    try:
                        self._collection = client.get_collection(name=self._collection_name)
                    except Exception:
                        self._collection = client.create_collection(**kwargs)
            except Exception as exc:
                raise MemoryBackendError(f"ChromaDB collection init failed: {exc}") from exc

            return self._collection

    def _build_embedding_function(self) -> Any | None:
        """按 ``DEFAULT_EMBEDDING_MODELS`` 顺序尝试，全部失败时返回 None（使用 ChromaDB 默认）。"""
        try:
            from chromadb.utils import embedding_functions  # type: ignore[import-not-found]
        except Exception:
            return None

        for model_name in self._embedding_models:
            try:
                fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=model_name,
                )
                _logger.info("ChromaMemoryBackend embedding model loaded: %s", model_name)
                return fn
            except Exception as exc:
                _logger.warning(
                    "ChromaMemoryBackend embedding model load failed: %s (%s)",
                    model_name,
                    exc,
                )
                continue
        return None

    def write(self, record: MemoryRecord) -> str:
        col = self._ensure_collection()
        try:
            col.upsert(
                ids=[record.chunk_id],
                documents=[record.content],
                metadatas=[
                    _flatten_metadata({"topic": record.topic, "written_at": record.written_at, **record.metadata})
                ],
            )
        except Exception as exc:
            raise MemoryBackendError(f"ChromaDB upsert failed: {exc}") from exc
        return record.chunk_id

    def list_by_topic(self, topic: str, k: int) -> list[MemoryRecord]:
        col = self._ensure_collection()
        try:
            raw = col.get(where={"topic": topic})
        except Exception as exc:
            raise MemoryBackendError(f"ChromaDB get failed: {exc}") from exc

        ids = raw.get("ids") or []
        docs = raw.get("documents") or []
        metas = raw.get("metadatas") or []
        records: list[MemoryRecord] = []
        for chunk_id, doc, meta in zip(ids, docs, metas, strict=False):
            meta = meta or {}
            records.append(
                MemoryRecord(
                    chunk_id=chunk_id,
                    topic=str(meta.get("topic", topic)),
                    content=doc or "",
                    score=1.0,
                    written_at=str(meta.get("written_at", "")),
                    metadata={kk: vv for kk, vv in meta.items() if kk not in {"topic", "written_at"}},
                )
            )
        records.sort(key=lambda r: r.written_at, reverse=True)
        return records[: max(0, k)]

    def query(
        self,
        query_text: str,
        k: int,
        topic: str | None = None,
    ) -> list[MemoryRecord]:
        col = self._ensure_collection()
        where = {"topic": topic} if topic is not None else None
        try:
            raw = col.query(
                query_texts=[query_text],
                n_results=max(1, k),
                where=where,
            )
        except Exception as exc:
            raise MemoryBackendError(f"ChromaDB query failed: {exc}") from exc

        if not raw.get("ids") or not raw["ids"][0]:
            return []
        ids = raw["ids"][0]
        distances = raw["distances"][0] if raw.get("distances") else [0.0] * len(ids)
        docs = raw["documents"][0] if raw.get("documents") else [""] * len(ids)
        metas = raw["metadatas"][0] if raw.get("metadatas") else [{}] * len(ids)

        records: list[MemoryRecord] = []
        for chunk_id, dist, doc, meta in zip(ids, distances, docs, metas, strict=False):
            meta = meta or {}
            score = max(0.0, min(1.0, 1.0 - float(dist)))
            if score < self._score_threshold:
                continue
            records.append(
                MemoryRecord(
                    chunk_id=chunk_id,
                    topic=str(meta.get("topic", topic or "")),
                    content=doc or "",
                    score=round(score, 4),
                    written_at=str(meta.get("written_at", "")),
                    metadata={kk: vv for kk, vv in meta.items() if kk not in {"topic", "written_at"}},
                )
            )
        return records

    def count(self) -> int:
        try:
            col = self._ensure_collection()
            return int(col.count())
        except Exception:
            return -1


def _flatten_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    """ChromaDB metadata 仅接受 str/int/float/bool；将 list/dict 序列化为 CSV/JSON。"""
    flat: dict[str, Any] = {}
    for key, val in meta.items():
        if val is None:
            continue
        if isinstance(val, (str, int, float, bool)):
            flat[key] = val
        elif isinstance(val, (list, tuple)):
            flat[key] = ",".join(str(x) for x in val)
        else:
            flat[key] = str(val)
    return flat


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
        ``MemoryBackend`` 实例；默认惰性构建 ``ChromaMemoryBackend``；
        ChromaDB 不可用时调用方可传入 ``InMemoryMemoryBackend``。
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
        self._backend: MemoryBackend = backend or ChromaMemoryBackend()
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
        VMS 不可用时自动降级到 ChromaMemoryBackend。
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
                    _logger.info("get_unified_memory_api: VMS unavailable, falling back to ChromaDB: %s", exc)
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
