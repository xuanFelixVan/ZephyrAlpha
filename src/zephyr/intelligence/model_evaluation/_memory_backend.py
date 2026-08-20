# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model-capability-exam/blueprint.md
# [MODULE] zephyr.intelligence.model_evaluation._memory_backend
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.shared.__init__
# [CONSUMERS] zephyr.intelligence.model_evaluation.unified_memory_api; zephyr.integration.vector_memory.vms_memory_backend
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] MemoryBackend Protocol signature must not change without updating all implementors
# [MODIFY-GUARD] changes here affect unified_memory_api.py + vms_memory_backend.py + all backend implementors
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MemoryBackendError on backend failure; WriteTraceMissing on missing provenance
# [TESTS] tests/test_unified_memory_api.py; tests/test_vms_memory_backend.py
# [A_module] module_id=MOD-INF-036 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Backend protocol & shared data classes for the unified memory layer.
=====================================================
Extracted from unified_memory_api.py to break the circular dependency:

    unified_memory_api.py -> vms_memory_backend.py -> unified_memory_api.py

This module defines the *contract* (Protocol + data classes + exceptions +
InMemoryMemoryBackend fallback) that both unified_memory_api.py and
vms_memory_backend.py depend on, with no import cycle.

This module must NOT import from unified_memory_api.py or vms_memory_backend.py.

迁移说明 (2026-07-19)：本文件原位于 zephyr.gov_kb.storage._backend_protocol，
KBG 系统删除时随同 UnifiedMemoryAPI 一起迁移到 intelligence.model_evaluation，
内容未变。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 记忆写入记录
#   fields: chunk_id/topic/content/score/written_at/metadata（pydantic 校验，extra=forbid）
#   code: MemoryRecord L61
# - id: I2
#   name: 检索/列表查询请求
#   fields: query_text/k/topic（query 可按 topic 过滤）
#   code: query() L115 / list_by_topic() L109
# 层: 算法
# - id: A1
#   name_zh: ① 后端协议契约
#   name_en: MemoryBackend Protocol
#   intro: 定义 write/list_by_topic/query/count 四方法签名统一所有记忆后端
#   desc: runtime_checkable Protocol；为打破 unified_memory_api 与 vms_memory_backend 循环依赖而抽出的公共契约层
#   inputs: I1 I2
#   outputs: 统一接口签名
#   invariant: 签名变更必须同步所有实现方
# - id: A2
#   name_zh: ② 内存后端读写与排序
#   name_en: InMemoryMemoryBackend.write/list_by_topic
#   intro: 纯 Python dict 兜底后端，测试与降级路径使用
#   desc: dict+RLock 存储；write 记录写入序号；list_by_topic 按 (written_at, 写入序号) 倒序取 top-k
#   inputs: I1 A1
#   outputs: chunk_id / 按时间倒序的记录列表
# - id: A3
#   name_zh: ③ 简易分词器
#   name_en: _simple_tokens
#   intro: 最小分词：英文数字成词、中文逐字成词
#   desc: 非字母数字字符切分 ASCII 词；CJK 字符逐字成 token；全小写化
#   inputs: I2
#   outputs: token 列表
# - id: A4
#   name_zh: ④ 词重叠相似度检索
#   name_en: InMemoryMemoryBackend.query
#   intro: 用查询与内容的词集合重叠率当相似度打分检索
#   desc: score=|q_tokens∩r_tokens|/|q_tokens|（上限 1.0），score≤0 丢弃；可按 topic 过滤；按 score 倒序取 top-k 并重打分
#   inputs: A2 A3
#   outputs: 带 score 的 MemoryRecord 列表
# 层: 输出
# - id: O1
#   name_zh: 检索/列表结果记录集
#   name_en: list[MemoryRecord]
#   intro: query/list_by_topic 返回的统一记录列表，score∈[0,1]
#   invariant: score∈[0,1]；top-k 截断
#   downstream: unified_memory_api；vms_memory_backend（#[CONSUMERS] 头）
# - id: O2
#   name_zh: 写入返回 chunk_id
#   name_en: write 返回 str
#   intro: 写入成功返回后端唯一 chunk_id 供后续溯源
#   downstream: unified_memory_api；vms_memory_backend（#[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# A1 --> A2
# I2 --> A3
# A2 --> A4
# A3 --> A4
# A2 --> O1
# A4 --> O1
# A2 --> O2
"""

from __future__ import annotations

import threading
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

__all__ = [  # noqa: n114-final  n114-final豁免: __all__是Python导出约定且本文件运行时动态append，Final标注不适用
    "InMemoryMemoryBackend",
    "MemoryBackend",
    "MemoryBackendError",
    "MemoryRecord",
]


class MemoryBackendError(RuntimeError):
    """Raised when a memory backend is unavailable or an operation fails."""

    error_code = "ZA-GV-0038"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class MemoryRecord(BaseModel):
    """Unified return type for kb.recall / kb.search."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    chunk_id: str = Field(min_length=1, description="Backend-unique ID")
    topic: str = Field(min_length=1, description="Owning topic")
    content: str = Field(description="Raw content")
    score: float = Field(default=1.0, ge=0.0, le=1.0, description="Similarity score (recall defaults to 1.0)")
    written_at: str = Field(default="", description="UTC ISO 8601 write timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Extra metadata (incl. provenance)")


@runtime_checkable
class MemoryBackend(Protocol):
    """Memory backend protocol; InMemoryMemoryBackend / VMSMemoryBackend implement this."""

    def write(self, record: MemoryRecord) -> str: ...  # pragma: no cover - Protocol

    def list_by_topic(self, topic: str, k: int) -> list[MemoryRecord]: ...  # pragma: no cover

    def query(self, query_text: str, k: int, topic: str | None = None) -> list[MemoryRecord]: ...  # pragma: no cover

    def count(self) -> int: ...  # pragma: no cover


class InMemoryMemoryBackend:
    """Pure-Python dict fallback backend (no ChromaDB dependency).

    Used for:
    1. Unit tests — avoids ChromaDB startup cost and persistence side-effects
    2. Degradation path when embedding model download fails
    3. Offline CI runs
    """

    def __init__(self) -> None:
        self._records: dict[str, MemoryRecord] = {}
        self._order: dict[str, int] = {}
        self._counter: int = 0
        self._lock = threading.RLock()

    def write(self, record: MemoryRecord) -> str:
        with self._lock:
            self._counter += 1
            self._records[record.chunk_id] = record
            self._order[record.chunk_id] = self._counter
        return record.chunk_id

    def list_by_topic(self, topic: str, k: int) -> list[MemoryRecord]:
        with self._lock:
            matched = [(self._order.get(r.chunk_id, 0), r) for r in self._records.values() if r.topic == topic]
        matched.sort(key=lambda item: (item[1].written_at, item[0]), reverse=True)
        return [r for _, r in matched[: max(0, k)]]

    def query(self, query_text: str, k: int, topic: str | None = None) -> list[MemoryRecord]:
        if not query_text:
            return []
        q_tokens = set(_simple_tokens(query_text))
        if not q_tokens:
            return []

        with self._lock:
            candidates = list(self._records.values())
        if topic is not None:
            candidates = [r for r in candidates if r.topic == topic]

        scored: list[tuple[float, MemoryRecord]] = []
        for rec in candidates:
            r_tokens = set(_simple_tokens(rec.content))
            if not r_tokens:
                continue
            overlap = len(q_tokens & r_tokens)
            score = overlap / max(len(q_tokens), 1)
            if score <= 0.0:
                continue
            scored.append((min(score, 1.0), rec))

        scored.sort(key=lambda item: item[0], reverse=True)
        results: list[MemoryRecord] = []
        for score, rec in scored[: max(0, k)]:
            results.append(
                MemoryRecord(
                    chunk_id=rec.chunk_id,
                    topic=rec.topic,
                    content=rec.content,
                    score=round(score, 4),
                    written_at=rec.written_at,
                    metadata=dict(rec.metadata),
                )
            )
        return results

    def count(self) -> int:
        with self._lock:
            return len(self._records)

    def clear(self) -> None:
        """Test-only: wipe in-memory store."""
        with self._lock:
            self._records.clear()
            self._order.clear()
            self._counter = 0


def _simple_tokens(text: str) -> list[str]:
    """Minimal tokenizer: split on non-alnum + per-char CJK."""
    if not text:
        return []
    tokens: list[str] = []
    buf: list[str] = []
    for ch in text.lower():
        if ch.isascii() and (ch.isalnum() or ch == "_"):
            buf.append(ch)
        else:
            if buf:
                tokens.append("".join(buf))
                buf = []
            if "\u4e00" <= ch <= "\u9fff":
                tokens.append(ch)
    if buf:
        tokens.append("".join(buf))
    return [t for t in tokens if t]
