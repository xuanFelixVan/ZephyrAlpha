# [BLUEPRINT] MOD-CMP-017 | docs/03_modules/_domain_compliance/regulatory_change_tracker/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-CMP-017 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.compliance.test_regulatory_change_tracker
# [TESTS] src/zephyr/compliance/regulatory_change_tracker.py
"""MOD-CMP-017 单元测试：regulatory_change_tracker 监管变更追踪器。

蓝图验收（B14-04671/CAND-CMP-008，§0定位/§1规则）：
公告采集注入 + NLP 变更抽取注入（变更类型/生效日期/涉及条款结构化校验）+
影响域映射（条款关联表）+ 评审任务生成与人工确认。源/抽取器/时钟全注入，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.compliance.regulatory_change_tracker",
    reason="regulatory_change_tracker not importable",
)

from zephyr.compliance.regulatory_change_tracker import (  # noqa: E402
    Announcement,
    ChangeType,
    RegulatoryChangeTracker,
    RegulatoryTrackerError,
    ReviewStatus,
)

_T0 = datetime.datetime(2026, 8, 25, 20, 0, 0)

_IMPACT = {
    "《减持规定》第5条": ("position", "trading"),
    "《交易规则》第3.2条": ("order", "trading"),
}

_EXTRACTION_OK = {
    "change_type": "amendment",
    "effective_date": datetime.date(2026, 9, 1),
    "clauses": ["《减持规定》第5条"],
}


def _notice(
    notice_id: str = "N-001",
    issuer: str = "CSRC",
    published_at: datetime.datetime = datetime.datetime(2026, 8, 20, 18, 0, 0),
) -> Announcement:
    return Announcement(
        notice_id=notice_id, issuer=issuer,
        title="关于修订减持规定的公告", body="……",
        published_at=published_at,
    )


def _tracker(
    notices=None,
    extraction: dict | None = None,
    source=None,
    extractor=None,
    impact_table=None,
) -> RegulatoryChangeTracker:
    return RegulatoryChangeTracker(
        clock=lambda: _T0,
        source=source if source is not None else (lambda: list(notices or [])),
        extractor=extractor if extractor is not None
        else (lambda a: dict(_EXTRACTION_OK if extraction is None else extraction)),
        impact_table=_IMPACT if impact_table is None else impact_table,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 注入门禁（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInjectionGuards:
    def test_source_missing_raises(self) -> None:
        with pytest.raises(RegulatoryTrackerError):
            RegulatoryChangeTracker(clock=lambda: _T0, source=None, extractor=lambda a: {})

    def test_extractor_missing_raises(self) -> None:
        with pytest.raises(RegulatoryTrackerError):
            RegulatoryChangeTracker(clock=lambda: _T0, source=lambda: [], extractor=None)

    def test_impact_table_bad_key_raises(self) -> None:
        with pytest.raises(RegulatoryTrackerError):
            _tracker(impact_table={"": ("x",)})


# ──────────────────────────────────────────────────────────────────────────────
# 采集 + 评审任务生成
# ──────────────────────────────────────────────────────────────────────────────


class TestCollect:
    def test_collect_ok(self) -> None:
        t = _tracker(notices=[_notice()])
        tasks = t.collect()
        assert len(tasks) == 1
        task = tasks[0]
        assert task.task_id == "REV-N-001"
        assert task.status is ReviewStatus.PENDING
        assert task.change_type is ChangeType.AMENDMENT
        assert task.effective_date == datetime.date(2026, 9, 1)
        assert task.affected_domains == ("position", "trading")  # 影响域映射

    def test_dedup_idempotent(self) -> None:
        t = _tracker(notices=[_notice()])
        t.collect()
        assert t.collect() == []  # 同 notice_id 幂等
        assert t.tracked_notices() == ("N-001",)

    def test_deterministic_order(self) -> None:
        n2 = _notice("N-002", published_at=datetime.datetime(2026, 8, 22, 9, 0, 0))
        n1 = _notice("N-001", published_at=datetime.datetime(2026, 8, 20, 18, 0, 0))
        t = _tracker(notices=[n2, n1])
        tasks = t.collect()
        assert [x.notice_id for x in tasks] == ["N-001", "N-002"]  # 按发布时间

    def test_unmapped_clause_empty_domains(self) -> None:
        t = _tracker(notices=[_notice()],
                     extraction={**_EXTRACTION_OK, "clauses": ["《未知条款》"]})
        (task,) = t.collect()
        assert task.affected_domains == ()

    def test_multi_clause_domain_union(self) -> None:
        t = _tracker(
            notices=[_notice()],
            extraction={**_EXTRACTION_OK,
                        "clauses": ["《减持规定》第5条", "《交易规则》第3.2条"]},
        )
        (task,) = t.collect()
        assert task.affected_domains == ("order", "position", "trading")  # 排序去重并集

    def test_source_bad_return_raises(self) -> None:
        t = _tracker(source=lambda: {"not": "iterable-of-announcements"})
        with pytest.raises(RegulatoryTrackerError):
            t.collect()

    def test_bad_announcement_element_raises(self) -> None:
        t = _tracker(source=lambda: ["not-an-announcement"])
        with pytest.raises(RegulatoryTrackerError):
            t.collect()

    def test_empty_notice_id_raises(self) -> None:
        t = _tracker(notices=[_notice(notice_id="")])
        with pytest.raises(RegulatoryTrackerError):
            t.collect()


# ──────────────────────────────────────────────────────────────────────────────
# 抽取结果结构化校验（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestExtractionValidation:
    def test_missing_key_raises(self) -> None:
        t = _tracker(notices=[_notice()],
                     extraction={"change_type": "amendment", "effective_date": datetime.date(2026, 9, 1)})
        with pytest.raises(RegulatoryTrackerError):
            t.collect()

    def test_change_type_out_of_vocab_raises(self) -> None:
        t = _tracker(notices=[_notice()],
                     extraction={**_EXTRACTION_OK, "change_type": "magic"})
        with pytest.raises(RegulatoryTrackerError):
            t.collect()

    def test_bad_effective_date_raises(self) -> None:
        t = _tracker(notices=[_notice()],
                     extraction={**_EXTRACTION_OK, "effective_date": "2026-09-01"})
        with pytest.raises(RegulatoryTrackerError):
            t.collect()

    def test_clauses_non_sequence_raises(self) -> None:
        t = _tracker(notices=[_notice()],
                     extraction={**_EXTRACTION_OK, "clauses": "《减持规定》第5条"})
        with pytest.raises(RegulatoryTrackerError):
            t.collect()

    def test_clause_empty_str_raises(self) -> None:
        t = _tracker(notices=[_notice()],
                     extraction={**_EXTRACTION_OK, "clauses": ["ok", ""]})
        with pytest.raises(RegulatoryTrackerError):
            t.collect()

    def test_extraction_non_mapping_raises(self) -> None:
        t = _tracker(notices=[_notice()], extractor=lambda a: ["bad"])
        with pytest.raises(RegulatoryTrackerError):
            t.collect()


# ──────────────────────────────────────────────────────────────────────────────
# 人工确认 + 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestConfirmAndQuery:
    def test_confirm_ok(self) -> None:
        t = _tracker(notices=[_notice()])
        t.collect()
        confirmed = t.confirm_task("REV-N-001")
        assert confirmed.status is ReviewStatus.CONFIRMED
        assert t.pending_tasks() == []
        assert t.task_of("N-001").status is ReviewStatus.CONFIRMED

    def test_confirm_unknown_raises(self) -> None:
        t = _tracker(notices=[_notice()])
        t.collect()
        with pytest.raises(RegulatoryTrackerError):
            t.confirm_task("REV-ghost")

    def test_double_confirm_raises(self) -> None:
        t = _tracker(notices=[_notice()])
        t.collect()
        t.confirm_task("REV-N-001")
        with pytest.raises(RegulatoryTrackerError):
            t.confirm_task("REV-N-001")

    def test_pending_sorted(self) -> None:
        n2 = _notice("N-002", published_at=datetime.datetime(2026, 8, 22, 9, 0, 0))
        t = _tracker(notices=[n2, _notice("N-001")])
        t.collect()
        assert [x.task_id for x in t.pending_tasks()] == ["REV-N-001", "REV-N-002"]

    def test_task_of_unknown_raises(self) -> None:
        t = _tracker()
        with pytest.raises(RegulatoryTrackerError):
            t.task_of("ghost")

    def test_deterministic_same_input(self) -> None:
        t1 = _tracker(notices=[_notice()])
        t2 = _tracker(notices=[_notice()])
        assert t1.collect() == t2.collect()
