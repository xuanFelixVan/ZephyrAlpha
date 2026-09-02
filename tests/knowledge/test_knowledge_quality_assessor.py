# [BLUEPRINT] MOD-KNW-002 | docs/03_modules/_domain_knowledge/knowledge_quality_assessor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-KNW-002 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.knowledge.test_knowledge_quality_assessor
# [TESTS] src/zephyr/knowledge/knowledge_quality_assessor.py
"""MOD-KNW-002 单元测试：knowledge_quality_assessor 知识质量评估器。

蓝图验收（B14-04624/CAND-KNW-013，A9 D-KNOWLEDGE-11）：
四维评分（权重可配）+ 时效半衰期衰减（注入时钟）+ 低分隔离降权 +
复核队列FIFO + 评分变化审计 + 质量分写回回调。时钟/审计/写回全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.knowledge.knowledge_quality_assessor",
    reason="knowledge_quality_assessor not importable",
)

from zephyr.knowledge.knowledge_quality_assessor import (  # noqa: E402
    KnowledgeQualityAssessor,
    KnowledgeQualityError,
    QualityAuditRecord,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_PUB = datetime.datetime(2026, 8, 26, 9, 30, 0)  # 与 _T0 同刻 → 时效=1.0


def _assessor(
    audits: list | None = None,
    writes: list | None = None,
    **kwargs,
) -> KnowledgeQualityAssessor:
    return KnowledgeQualityAssessor(
        clock=lambda: _T0,
        audit_sink=(lambda r: audits.append(r)) if audits is not None else None,
        kb_writer=(lambda eid, s: writes.append((eid, s))) if writes is not None else None,
        **kwargs,
    )


def _assess(assessor: KnowledgeQualityAssessor, entry_id: str = "e1", **kwargs):
    params = dict(
        accuracy=0.9,
        source_credibility=0.8,
        citation_count=50,
        published_at=_PUB,
    )
    params.update(kwargs)
    return assessor.assess(entry_id, **params)


# ──────────────────────────────────────────────────────────────────────────────
# 构造 / 权重校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_default_weights(self) -> None:
        assessor = _assessor()
        score = _assess(assessor)
        # 四维等权：acc .9 / time 1.0 / src .8 / cite .5 → 0.8
        assert score.total == pytest.approx(0.8)

    def test_custom_weights_normalized(self) -> None:
        assessor = _assessor(
            weights={
                "accuracy": 3.0,
                "timeliness": 1.0,
                "source_credibility": 0.0,
                "citation_frequency": 0.0,
            }
        )
        score = _assess(assessor)  # (3*.9 + 1*1.0)/4
        assert score.total == pytest.approx((3 * 0.9 + 1.0) / 4)

    def test_unknown_dimension_raises(self) -> None:
        with pytest.raises(KnowledgeQualityError):
            _assessor(
                weights={
                    "accuracy": 1.0,
                    "timeliness": 1.0,
                    "source_credibility": 1.0,
                    "citation_frequency": 1.0,
                    "ghost": 1.0,
                }
            )

    def test_missing_dimension_raises(self) -> None:
        with pytest.raises(KnowledgeQualityError):
            _assessor(weights={"accuracy": 1.0})

    def test_negative_weight_raises(self) -> None:
        with pytest.raises(KnowledgeQualityError):
            _assessor(
                weights={
                    "accuracy": -1.0,
                    "timeliness": 1.0,
                    "source_credibility": 1.0,
                    "citation_frequency": 1.0,
                }
            )

    def test_zero_total_weight_raises(self) -> None:
        with pytest.raises(KnowledgeQualityError):
            _assessor(
                weights={
                    "accuracy": 0.0,
                    "timeliness": 0.0,
                    "source_credibility": 0.0,
                    "citation_frequency": 0.0,
                }
            )

    def test_bad_threshold_raises(self) -> None:
        with pytest.raises(KnowledgeQualityError):
            _assessor(quarantine_threshold=1.5)

    def test_bad_half_life_raises(self) -> None:
        with pytest.raises(KnowledgeQualityError):
            _assessor(half_life_days=0)

    def test_bad_citation_cap_raises(self) -> None:
        with pytest.raises(KnowledgeQualityError):
            _assessor(citation_cap=0)


# ──────────────────────────────────────────────────────────────────────────────
# 四维评分 + 时效衰减
# ──────────────────────────────────────────────────────────────────────────────


class TestAssess:
    def test_citation_capped_at_one(self) -> None:
        assessor = _assessor(citation_cap=10)
        score = _assess(assessor, citation_count=999)
        assert score.citation_frequency == 1.0

    def test_timeliness_half_life_decay(self) -> None:
        assessor = _assessor(half_life_days=10)
        pub = _T0 - datetime.timedelta(days=10)
        score = _assess(assessor, published_at=pub)
        assert score.timeliness == pytest.approx(0.5)

    def test_timeliness_two_half_lives(self) -> None:
        assessor = _assessor(half_life_days=10)
        pub = _T0 - datetime.timedelta(days=20)
        score = _assess(assessor, published_at=pub)
        assert score.timeliness == pytest.approx(0.25)

    def test_future_published_raises(self) -> None:
        assessor = _assessor()
        with pytest.raises(KnowledgeQualityError):
            _assess(assessor, published_at=_T0 + datetime.timedelta(days=1))

    def test_dimension_out_of_range_raises(self) -> None:
        assessor = _assessor()
        with pytest.raises(KnowledgeQualityError):
            _assess(assessor, accuracy=1.2)
        with pytest.raises(KnowledgeQualityError):
            _assess(assessor, source_credibility=-0.1)

    def test_negative_citation_raises(self) -> None:
        assessor = _assessor()
        with pytest.raises(KnowledgeQualityError):
            _assess(assessor, citation_count=-1)

    def test_blank_entry_id_raises(self) -> None:
        assessor = _assessor()
        with pytest.raises(KnowledgeQualityError):
            _assess(assessor, entry_id="")

    def test_reassess_updates_score(self) -> None:
        assessor = _assessor()
        _assess(assessor, accuracy=0.5)
        score = _assess(assessor, accuracy=1.0)
        assert assessor.get_score("e1") is score
        assert score.total == pytest.approx((1.0 + 1.0 + 0.8 + 0.5) / 4)


# ──────────────────────────────────────────────────────────────────────────────
# 隔离降权
# ──────────────────────────────────────────────────────────────────────────────


class TestQuarantine:
    def test_low_score_quarantined_and_downweighted(self) -> None:
        assessor = _assessor(quarantine_threshold=0.5, quarantine_weight=0.2)
        score = _assess(assessor, accuracy=0.0, source_credibility=0.0, citation_count=0)
        assert score.quarantined is True
        assert assessor.retrieval_weight("e1") == pytest.approx(0.2)

    def test_high_score_not_quarantined(self) -> None:
        assessor = _assessor(quarantine_threshold=0.5)
        score = _assess(assessor)
        assert score.quarantined is False
        assert assessor.retrieval_weight("e1") == 1.0

    def test_threshold_boundary_not_quarantined(self) -> None:
        assessor = _assessor(quarantine_threshold=0.8)
        score = _assess(assessor)  # total 恰 0.8
        assert score.quarantined is False

    def test_quarantine_auto_enqueues_review_once(self) -> None:
        assessor = _assessor(quarantine_threshold=0.9)
        _assess(assessor, accuracy=0.0, source_credibility=0.0, citation_count=0)
        _assess(assessor, accuracy=0.0, source_credibility=0.0, citation_count=0)
        assert len(assessor.review_queue()) == 1  # 在队期间去重

    def test_get_unknown_raises(self) -> None:
        assessor = _assessor()
        with pytest.raises(KnowledgeQualityError):
            assessor.get_score("ghost")
        with pytest.raises(KnowledgeQualityError):
            assessor.retrieval_weight("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 复核队列 FIFO
# ──────────────────────────────────────────────────────────────────────────────


class TestReviewQueue:
    def test_fifo_order(self) -> None:
        assessor = _assessor()
        assessor.enqueue_review("e1", "人工复核")
        assessor.enqueue_review("e2", "人工复核")
        assessor.enqueue_review("e3", "人工复核")
        assert assessor.next_review().entry_id == "e1"
        assert assessor.next_review().entry_id == "e2"
        assert assessor.next_review().entry_id == "e3"

    def test_empty_queue_raises(self) -> None:
        assessor = _assessor()
        with pytest.raises(KnowledgeQualityError):
            assessor.next_review()

    def test_dequeue_allows_reenqueue(self) -> None:
        assessor = _assessor()
        assessor.enqueue_review("e1", "第一次")
        assessor.next_review()
        assessor.enqueue_review("e1", "第二次")
        assert assessor.next_review().reason == "第二次"

    def test_blank_entry_id_raises(self) -> None:
        assessor = _assessor()
        with pytest.raises(KnowledgeQualityError):
            assessor.enqueue_review("", "x")


# ──────────────────────────────────────────────────────────────────────────────
# 审计 + 写回 + 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestAuditAndDeterminism:
    def test_audit_trail_with_old_new(self) -> None:
        audits: list[QualityAuditRecord] = []
        assessor = _assessor(audits)
        _assess(assessor, accuracy=0.5)
        _assess(assessor, accuracy=1.0)
        assert audits[0].old_total is None  # 首评
        assert audits[1].old_total == pytest.approx(audits[0].new_total)
        assert all(a.at == _T0 for a in audits)

    def test_kb_writer_called_with_total(self) -> None:
        writes: list[tuple[str, float]] = []
        assessor = _assessor(writes=writes)
        score = _assess(assessor)
        assert writes == [("e1", score.total)]

    def test_determinism_same_input_same_output(self) -> None:
        def _run() -> list:
            audits: list[QualityAuditRecord] = []
            assessor = _assessor(audits)
            s1 = _assess(assessor, "e1", published_at=_T0 - datetime.timedelta(days=7))
            s2 = _assess(assessor, "e2", accuracy=0.1, source_credibility=0.1, citation_count=0)
            queue = [(i.entry_id, i.reason) for i in assessor.review_queue()]
            return [
                (s1.total, s1.timeliness, s1.quarantined),
                (s2.total, s2.quarantined),
                queue,
                [(a.entry_id, a.old_total, a.new_total) for a in audits],
            ]

        assert _run() == _run()
