# [BLUEPRINT] MOD-KNW-002 | docs/03_modules/_domain_knowledge/knowledge_quality_assessor/blueprint.md
# [MODULE] zephyr.knowledge.knowledge_quality_assessor
# [DOMAIN] D_KNOWLEDGE
# [DEPENDENCIES] 无（评分核心纯内存；clock/audit_sink/kb_writer 全注入）
# [CONSUMERS] 运行时装配批（KBEngine 质量分写回 / 检索降权 / 定期复核编排）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四维词表闭合(accuracy|timeliness|source_credibility|citation_frequency); 权重非负且和>0(内部归一); 时效=半衰期指数衰减(注入时钟); 总分<阈值即隔离降权; 复核队列严格FIFO(隔离自动入队去重); 每次评分写审计; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_knowledge/knowledge_quality_assessor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] KnowledgeQualityError(占位 ZA-KNW-UNREGISTERED-KNW-QUALITY)——非法权重/维度越界/空entry_id/未知条目/未来时间/空队列取件时抛
# [TESTS] tests/knowledge/test_knowledge_quality_assessor.py
# [A_module] module_id=MOD-KNW-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""KnowledgeQualityAssessor — 知识质量评估器（MOD-KNW-002）。

B14-04624（AUD-DRAFT-001-DIGEST P2 波 P2-W03，CAND-KNW-013，A9
D-KNOWLEDGE-11）：RAGAS 思想单机版——知识条目四维评分（准确性/时效性/
来源可信度/引用频次，权重可配）+ 时效衰减模型（半衰期指数衰减，注入时
钟）+ 低分条目隔离降权（阈值判定）+ 定期复核队列（FIFO）+ 评分变化写
审计回调，质量分经注入 kb_writer 写回 KBEngine 元数据语义。canonical 承
接 KNW-003/KNW-006（三稿重登）归并。

查重分工：gov_audit/kb_gate=入闸门禁（本件=入库后质量评分与隔离，不做门
禁判定）；kb_engine=条目存取（本件经注入回调写回质量分，不直连存储）。
"""

from __future__ import annotations

import datetime
import logging
from collections import deque
from dataclasses import dataclass
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "DIMENSIONS",
    "KnowledgeQualityAssessor",
    "KnowledgeQualityError",
    "QualityAuditRecord",
    "QualityScore",
    "ReviewItem",
]

#: 四维评分词表（闭合）
DIMENSIONS: Final = (
    "accuracy",
    "timeliness",
    "source_credibility",
    "citation_frequency",
)

_DEFAULT_WEIGHTS: Final = {dim: 1.0 for dim in DIMENSIONS}


class KnowledgeQualityError(Exception):
    """知识质量评估输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-KNW-UNREGISTERED-KNW-QUALITY。
    """


@dataclass(frozen=True)
class QualityScore:
    """单次质量评分结果（frozen）。"""

    entry_id: str
    accuracy: float
    timeliness: float
    source_credibility: float
    citation_frequency: float
    total: float
    quarantined: bool
    assessed_at: datetime.datetime


@dataclass(frozen=True)
class QualityAuditRecord:
    """评分变化审计载荷（注入 audit_sink 回调；old_total=None 为首评）。"""

    entry_id: str
    old_total: float | None
    new_total: float
    quarantined: bool
    at: datetime.datetime


@dataclass(frozen=True)
class ReviewItem:
    """复核队列条目（FIFO）。"""

    entry_id: str
    reason: str
    enqueued_at: datetime.datetime


class KnowledgeQualityAssessor:
    """知识条目四维评分 + 时效衰减 + 隔离降权 + 复核队列。"""

    def __init__(
        self,
        *,
        weights: Mapping[str, float] | None = None,
        quarantine_threshold: float = 0.4,
        quarantine_weight: float = 0.1,
        half_life_days: float = 30.0,
        citation_cap: int = 100,
        clock: Callable[[], datetime.datetime] | None = None,
        audit_sink: Callable[[QualityAuditRecord], None] | None = None,
        kb_writer: Callable[[str, float], None] | None = None,
    ) -> None:
        raw = dict(weights) if weights is not None else dict(_DEFAULT_WEIGHTS)
        unknown = set(raw) - set(DIMENSIONS)
        if unknown:
            raise KnowledgeQualityError(f"未知评分维度: {sorted(unknown)!r}（四维词表闭合）")
        if set(raw) != set(DIMENSIONS):
            raise KnowledgeQualityError("权重须覆盖全部四维")
        for dim, w in raw.items():
            if w < 0:
                raise KnowledgeQualityError(f"非法权重: {dim}={w}（须非负）")
        total_w = sum(raw.values())
        if total_w <= 0:
            raise KnowledgeQualityError("权重和须 > 0")
        if not 0.0 <= quarantine_threshold <= 1.0:
            raise KnowledgeQualityError(f"非法隔离阈值: {quarantine_threshold}")
        if not 0.0 < quarantine_weight <= 1.0:
            raise KnowledgeQualityError(f"非法降权系数: {quarantine_weight}")
        if half_life_days <= 0:
            raise KnowledgeQualityError(f"非法半衰期: {half_life_days}")
        if citation_cap < 1:
            raise KnowledgeQualityError(f"非法引用上限: {citation_cap}")
        self._weights: dict[str, float] = {d: raw[d] / total_w for d in DIMENSIONS}
        self._threshold = quarantine_threshold
        self._quarantine_weight = quarantine_weight
        self._half_life = half_life_days
        self._citation_cap = citation_cap
        self._clock = clock or datetime.datetime.now
        self._audit_sink = audit_sink
        self._kb_writer = kb_writer
        self._scores: dict[str, QualityScore] = {}
        self._review_queue: deque[ReviewItem] = deque()
        self._queued: set[str] = set()

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _unit(value: float, name: str) -> float:
        if not 0.0 <= value <= 1.0:
            raise KnowledgeQualityError(f"{name} 越界: {value}（须 ∈ [0,1]）")
        return value

    def _timeliness(self, published_at: datetime.datetime) -> float:
        now = self._clock()
        age_seconds = (now - published_at).total_seconds()
        if age_seconds < 0:
            raise KnowledgeQualityError(
                f"published_at 晚于当前时钟: {published_at!r}（时钟回拨拒绝）"
            )
        age_days = age_seconds / 86400.0
        return 0.5 ** (age_days / self._half_life)

    def _enqueue(self, entry_id: str, reason: str) -> None:
        if entry_id in self._queued:
            return
        self._review_queue.append(
            ReviewItem(entry_id=entry_id, reason=reason, enqueued_at=self._clock())
        )
        self._queued.add(entry_id)
        _log.info("复核入队: %s (%s)", entry_id, reason)

    # ── 评分 ─────────────────────────────────────────────────────────────

    def assess(
        self,
        entry_id: str,
        *,
        accuracy: float,
        source_credibility: float,
        citation_count: int,
        published_at: datetime.datetime,
    ) -> QualityScore:
        """四维评分：时效按半衰期衰减；总分低于阈值即隔离并入复核队列。"""
        if not entry_id:
            raise KnowledgeQualityError("entry_id 为空")
        self._unit(accuracy, "accuracy")
        self._unit(source_credibility, "source_credibility")
        if citation_count < 0:
            raise KnowledgeQualityError(f"非法引用数: {citation_count}")
        timeliness = self._timeliness(published_at)
        citation = min(citation_count / self._citation_cap, 1.0)
        dims = {
            "accuracy": accuracy,
            "timeliness": timeliness,
            "source_credibility": source_credibility,
            "citation_frequency": citation,
        }
        total = sum(self._weights[d] * dims[d] for d in DIMENSIONS)
        quarantined = total < self._threshold
        old = self._scores.get(entry_id)
        score = QualityScore(
            entry_id=entry_id,
            accuracy=accuracy,
            timeliness=timeliness,
            source_credibility=source_credibility,
            citation_frequency=citation,
            total=total,
            quarantined=quarantined,
            assessed_at=self._clock(),
        )
        self._scores[entry_id] = score
        if self._audit_sink is not None:
            self._audit_sink(QualityAuditRecord(
                entry_id=entry_id,
                old_total=old.total if old is not None else None,
                new_total=total,
                quarantined=quarantined,
                at=self._clock(),
            ))
        if self._kb_writer is not None:
            self._kb_writer(entry_id, total)  # 质量分写回 KBEngine 元数据语义
        if quarantined:
            self._enqueue(entry_id, f"质量分 {total:.4f} 低于阈值 {self._threshold}")
        return score

    # ── 查询 ─────────────────────────────────────────────────────────────

    def get_score(self, entry_id: str) -> QualityScore:
        """单条目最新评分（未知 → Fail-Closed）。"""
        score = self._scores.get(entry_id)
        if score is None:
            raise KnowledgeQualityError(f"未知条目: {entry_id!r}（未评分）")
        return score

    def retrieval_weight(self, entry_id: str) -> float:
        """检索降权系数：隔离条目按 quarantine_weight 降权，正常条目 1.0。"""
        score = self.get_score(entry_id)
        return self._quarantine_weight if score.quarantined else 1.0

    # ── 复核队列（FIFO） ──────────────────────────────────────────────────

    def enqueue_review(self, entry_id: str, reason: str) -> None:
        """人工登记复核（FIFO；同 entry 在队期间去重）。"""
        if not entry_id:
            raise KnowledgeQualityError("entry_id 为空")
        self._enqueue(entry_id, reason)

    def next_review(self) -> ReviewItem:
        """取队首复核条目（空队列 → Fail-Closed）。"""
        if not self._review_queue:
            raise KnowledgeQualityError("复核队列为空")
        item = self._review_queue.popleft()
        self._queued.discard(item.entry_id)
        return item

    def review_queue(self) -> tuple[ReviewItem, ...]:
        """复核队列快照（FIFO 序，确定性）。"""
        return tuple(self._review_queue)
