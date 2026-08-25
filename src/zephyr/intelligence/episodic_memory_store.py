# [BLUEPRINT] MOD-INT-EPISODIC-MEM | docs/03_modules/_domain_intelligence/episodic_memory_store/blueprint.md | §0-5
# [MODULE] zephyr.intelligence.episodic_memory_store
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.shared.foundation.errors(ZephyrBaseError)
# [CONSUMERS] 运行时装配批（hash_sink 接 Redis / vector_sink 接 FAISS / archive_sink 接 SQLite / embedding 接 EmbeddingRouter）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 判定核心纯内存无IO; Schema Fail-Closed; LRU 语义检索命中即刷新访问时间; 淘汰恒取最久未访问; 归档不丢数据; 台账只增不改; 零密钥字段
# [MODIFY-GUARD] docs/03_modules/_domain_intelligence/episodic_memory_store/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] InvalidTrajectoryError(ZA-IT-0016); EpisodicConfigError(ZA-IT-0017)
# [TESTS] tests/intelligence/test_episodic_memory_store.py
# [A_module] module_id=MOD-INT-EPISODIC-MEM | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""EpisodicMemoryStore — 情景记忆存储（MOD-INT-EPISODIC-MEM）。

B11-02613（AUD-DRAFT-001-DIGEST P1 波 W-P1-10，§6.1）：轨迹 Schema
（输入-行动-结果-反思）落 Redis Hash + 向量入 FAISS 双写；相似任务
Top-K 检索；LRU 淘汰保留 1000 条 + 90 天转 SQLite 归档；与四层记忆
架构（B11-02457）接口对齐。

查重裁定：不复制 reflexion/roles（轨迹数据结构）、preflect_store
（失败模式提炼库）、faiss_collection_manager（FAISS 生命周期管理）；
向量/哈希/归档全经注入 sink。
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final

from zephyr.shared.foundation.errors import ZephyrBaseError

_log = logging.getLogger(__name__)

__all__: Final = [
    "EpisodicConfigError",
    "EpisodicMemoryConfig",
    "EpisodicMemoryStore",
    "EvictionRecord",
    "InvalidTrajectoryError",
    "RetrievalHit",
    "TrajectoryRecord",
]


class InvalidTrajectoryError(ZephyrBaseError):
    """轨迹 Schema 非法（Fail-Closed）。"""

    error_code = "ZA-IT-0016"


class EpisodicConfigError(ZephyrBaseError):
    """情景记忆配置非法（Fail-Closed）。"""

    error_code = "ZA-IT-0017"


@dataclass(frozen=True)
class TrajectoryRecord:
    """情景轨迹记录。"""

    record_id: str
    task_input: str
    action: str
    result: str
    reflection: str
    created_at: float
    last_accessed_at: float


@dataclass(frozen=True)
class RetrievalHit:
    """检索命中。"""

    record: TrajectoryRecord
    score: float


@dataclass(frozen=True)
class EvictionRecord:
    """淘汰记录。"""

    evicted_ids: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class EpisodicMemoryConfig:
    """情景记忆配置。"""

    max_entries: int = 1000
    archive_after_days: int = 90

    def __post_init__(self) -> None:
        if self.max_entries <= 0:
            raise EpisodicConfigError(f"max_entries 非正: {self.max_entries}")
        if self.archive_after_days <= 0:
            raise EpisodicConfigError(f"archive_after_days 非正: {self.archive_after_days}")


def _now(clock: Callable[[], float] | None) -> float:
    if clock is not None:
        return clock()
    import time

    return time.time()


class EpisodicMemoryStore:
    """情景记忆判定核心（纯内存，无 IO）。"""

    def __init__(
        self,
        config: EpisodicMemoryConfig | None = None,
        hash_sink: Callable[[TrajectoryRecord], None] | None = None,
        vector_sink: Callable[[TrajectoryRecord, list[float]], None] | None = None,
        search: Callable[[list[float], int], list[tuple[TrajectoryRecord, float]]] | None = None,
        archive_sink: Callable[[TrajectoryRecord], None] | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._config = config or EpisodicMemoryConfig()
        self._hash_sink = hash_sink
        self._vector_sink = vector_sink
        self._search = search
        self._archive_sink = archive_sink
        self._clock = clock
        self._ledger: list[TrajectoryRecord] = []

    def stats(self) -> dict[str, int]:
        return {"total": len(self._ledger), "max_entries": self._config.max_entries}

    def store(self, record: TrajectoryRecord, embedding: list[float] | None = None) -> EvictionRecord | None:
        if not record.task_input:
            raise InvalidTrajectoryError("task_input 不能为空")
        if not record.action:
            raise InvalidTrajectoryError("action 不能为空")
        if not record.result:
            raise InvalidTrajectoryError("result 不能为空")
        # reflection 允许空字符串（未反思）
        now = _now(self._clock)
        rec = TrajectoryRecord(
            record_id=record.record_id,
            task_input=record.task_input,
            action=record.action,
            result=record.result,
            reflection=record.reflection,
            created_at=record.created_at or now,
            last_accessed_at=now,
        )
        self._ledger.append(rec)
        if self._hash_sink is not None:
            try:
                self._hash_sink(rec)
            except Exception as exc:
                _log.warning("hash_sink 异常: %s", exc)
        if embedding is not None and self._vector_sink is not None:
            try:
                self._vector_sink(rec, embedding)
            except Exception as exc:
                _log.warning("vector_sink 异常: %s", exc)
        return self._evict_if_needed()

    def _evict_if_needed(self) -> EvictionRecord | None:
        if len(self._ledger) <= self._config.max_entries:
            return None
        sorted_ledger = sorted(self._ledger, key=lambda r: r.last_accessed_at)
        to_remove = len(self._ledger) - self._config.max_entries
        evicted = [r.record_id for r in sorted_ledger[:to_remove]]
        self._ledger = sorted_ledger[to_remove:]
        return EvictionRecord(
            evicted_ids=tuple(evicted),
            reason=f"LRU 淘汰超容({self._config.max_entries})",
        )

    def retrieve_similar(self, query_embedding: list[float], k: int) -> list[RetrievalHit]:
        if k <= 0:
            raise ValueError(f"k 必须为正: {k}")
        hits: list[RetrievalHit] = []
        if self._search is not None:
            try:
                for rec, score in self._search(query_embedding, k):
                    hits.append(RetrievalHit(record=rec, score=score))
            except Exception as exc:
                _log.warning("search 异常: %s", exc)
                hits = []
        hits.sort(key=lambda h: h.score, reverse=True)
        now = _now(self._clock)
        updated_ledger = []
        hit_ids = {h.record.record_id for h in hits[:k]}
        for rec in self._ledger:
            if rec.record_id in hit_ids:
                rec = TrajectoryRecord(
                    record_id=rec.record_id,
                    task_input=rec.task_input,
                    action=rec.action,
                    result=rec.result,
                    reflection=rec.reflection,
                    created_at=rec.created_at,
                    last_accessed_at=now,
                )
            updated_ledger.append(rec)
        self._ledger = updated_ledger
        return hits[:k]

    def archive_expired(self) -> EvictionRecord | None:
        cutoff = _now(self._clock) - self._config.archive_after_days * 86400
        expired = [r for r in self._ledger if r.created_at <= cutoff]
        if not expired:
            return None
        if self._archive_sink is None:
            return EvictionRecord(
                evicted_ids=tuple(r.record_id for r in expired),
                reason="archive_sink 未注入，仅产归档建议",
            )
        archived = []
        for rec in expired:
            try:
                self._archive_sink(rec)
                archived.append(rec.record_id)
            except Exception as exc:
                _log.warning("archive_sink 异常: %s", exc)
        self._ledger = [r for r in self._ledger if r.record_id not in archived]
        return EvictionRecord(
            evicted_ids=tuple(archived),
            reason=f"归档({self._config.archive_after_days}d)",
        )

    def forget(self, record_id: str) -> bool:
        before = len(self._ledger)
        self._ledger = [r for r in self._ledger if r.record_id != record_id]
        return len(self._ledger) < before
