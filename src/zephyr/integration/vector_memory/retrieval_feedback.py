# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain_knowledge/vector_memory/blueprint.md | §
# [MODULE] zephyr.integration.vector_memory.retrieval_feedback
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.shared.schema.schemas
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
# [A_module] module_id=MOD-INF-011 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
RetrievalFeedback — MOD-INF-011 FLE 检索质量消费
===================================================
蓝图 §7 · §6 · 检索结果质量闭环 + IMET 采样接口

功能
----
- log_feedback(trace, user_rating): 记录检索质量反馈
- track_hit_rates(): 统计各 Collection 命中率
- sample_for_quality_monitor(): 为 QM 子系统提供抽样数据
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from zephyr.shared.schema.schemas import BASE_CONFIG

if TYPE_CHECKING:
    from zephyr.integration.vector_memory.hybrid_retriever import RetrievalTrace
    from zephyr.integration.vector_memory.in_process_vector_memory import InProcessVectorMemory

_logger = logging.getLogger(__name__)


class FeedbackEntry(BaseModel):
    model_config = BASE_CONFIG

    collection: str
    query: str
    hit_count: int
    rating: float | None = None
    timestamp: str = ""


class RetrievalFeedback:
    def __init__(self, vms: InProcessVectorMemory | None = None) -> None:
        self._vms = vms
        self._feedback_log: list[FeedbackEntry] = []
        self._long_tail: dict[str, int] = {}

    def record(self, hit_id: str, was_useful: bool, task_id: str = "", collection: str = "") -> FeedbackEntry:
        entry = FeedbackEntry(
            query=task_id,
            hit_count=1 if was_useful else 0,
            rating=1.0 if was_useful else 0.0,
            timestamp=datetime.now(UTC).isoformat(),
            collection=collection,
        )
        self._feedback_log.append(entry)
        _logger.info("RetrievalFeedback.record: hit=%s useful=%s task=%s", hit_id, was_useful, task_id)
        return entry

    def write_failure_pattern(self, pattern_text: str) -> str | None:
        if self._vms is None:
            _logger.warning("RetrievalFeedback: VMS 未注入，跳过失败模式写入")
            return None
        # 内容哈希作 doc_id——pattern_text 稳定时幂等
        # 治本(风险B): scheduler.py 调用方已提取稳定 root_cause(去 z_score) 作 pattern_text
        doc_id = f"lesson::{hashlib.sha256(pattern_text.encode()).hexdigest()[:16]}"
        return self._vms.write(
            "lessons",
            pattern_text,
            metadata={
                "origin": "fle/retrieval_feedback",
                "audit_chain": ["fle"],
                "arbitration": "autonomous",
            },
            doc_id=doc_id,
        )

    def track_long_tail(self, query: str) -> None:
        self._long_tail[query] = self._long_tail.get(query, 0) + 1

    def log_feedback(
        self,
        trace: RetrievalTrace,
        user_rating: float | None = None,
    ) -> FeedbackEntry:
        entry = FeedbackEntry(
            collection=getattr(trace, "collection", "unknown"),
            query=getattr(trace, "query", ""),
            hit_count=len(getattr(trace, "hits", [])),
            rating=user_rating,
            timestamp=datetime.now(UTC).isoformat(),
        )
        self._feedback_log.append(entry)
        _logger.info(
            "RetrievalFeedback: %s -> %s (%d hits, rating=%s)",
            entry.query[:30],
            entry.collection,
            entry.hit_count,
            entry.rating,
        )
        return entry

    def track_hit_rates(self) -> dict[str, dict[str, Any]]:
        stats: dict[str, dict[str, Any]] = {}
        for entry in self._feedback_log:
            if entry.collection not in stats:
                stats[entry.collection] = {"total": 0, "hits": 0, "ratings": []}
            stats[entry.collection]["total"] += 1
            stats[entry.collection]["hits"] += min(entry.hit_count, 1)
            if entry.rating is not None:
                stats[entry.collection]["ratings"].append(entry.rating)

        result: dict[str, dict[str, Any]] = {}
        for col, data in stats.items():
            total = max(data["total"], 1)
            avg_rating = sum(data["ratings"]) / max(len(data["ratings"]), 1) if data["ratings"] else None
            result[col] = {
                "total_queries": data["total"],
                "hit_rate": round(data["hits"] / total, 4),
                "avg_rating": round(avg_rating, 2) if avg_rating is not None else None,
            }
        return result

    def sample_for_quality_monitor(self, sample_size: int = 10) -> list[FeedbackEntry]:
        return self._feedback_log[-sample_size:] if self._feedback_log else []
