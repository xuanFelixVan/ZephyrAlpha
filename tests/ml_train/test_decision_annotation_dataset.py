# [BLUEPRINT] MOD-ML-014 | docs/03_modules/_domain_machine_learning_train/decision_annotation_dataset/blueprint.md | §test
# [A_module] module_id=MOD-ML-014 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-ML-014 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_train.test_decision_annotation_dataset
# [TESTS] src/zephyr/ml_train/decision_annotation_dataset.py
"""MOD-ML-014 单元测试：decision_annotation_dataset 交易决策标注数据集。

蓝图验收（B1-00631/CAND-MLT-018，C2 71）：
七要素 schema + SQLite 注入连接（未注入 Fail-Closed）+ 录入结构化校验
（词表/空字段/重复 id）+ 结果回填（仅一次）+ SFT/复盘导出（确定性排序）
+ 版本管理（不可变快照 + 内容 hash 确定性）。连接用 :memory: 内存库，不触盘。
"""

from __future__ import annotations

import datetime
import sqlite3

import pytest

pytest.importorskip(
    "zephyr.ml_train.decision_annotation_dataset",
    reason="decision_annotation_dataset not importable",
)

from zephyr.ml_train.decision_annotation_dataset import (  # noqa: E402
    AnnotationInput,
    DecisionAnnotationDataset,
    DecisionAnnotationError,
    EMOTION_TAGS,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_T1 = datetime.datetime(2026, 8, 26, 10, 30, 0)


def _dataset(clock=lambda: _T0) -> DecisionAnnotationDataset:
    return DecisionAnnotationDataset(connection=sqlite3.connect(":memory:"), clock=clock)


def _entry(
    decision_id: str = "dec-1",
    symbol: str = "600519.SH",
    decision_time: datetime.datetime = _T0,
    rationale: str = "放量突破年线，回踩确认",
    emotion_tag: str = "confident",
    chart_ref: str = "chart://kline/600519/20260826",
) -> AnnotationInput:
    return AnnotationInput(
        decision_id=decision_id,
        symbol=symbol,
        decision_time=decision_time,
        rationale=rationale,
        emotion_tag=emotion_tag,
        chart_ref=chart_ref,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 构造与录入校验
# ──────────────────────────────────────────────────────────────────────────────


class TestAddAnnotation:
    def test_connection_not_injected_fail_closed(self) -> None:
        with pytest.raises(DecisionAnnotationError):
            DecisionAnnotationDataset(connection=None)

    def test_add_ok(self) -> None:
        ds = _dataset()
        ann = ds.add_annotation(_entry())
        assert ann.decision_id == "dec-1"
        assert ann.outcome_return is None
        assert ann.created_at == _T0

    def test_add_duplicate_id_rejected(self) -> None:
        ds = _dataset()
        ds.add_annotation(_entry())
        with pytest.raises(DecisionAnnotationError):
            ds.add_annotation(_entry())

    def test_empty_decision_id_rejected(self) -> None:
        ds = _dataset()
        with pytest.raises(DecisionAnnotationError):
            ds.add_annotation(_entry(decision_id=""))

    def test_empty_symbol_rejected(self) -> None:
        ds = _dataset()
        with pytest.raises(DecisionAnnotationError):
            ds.add_annotation(_entry(symbol=""))

    def test_empty_rationale_rejected(self) -> None:
        ds = _dataset()
        with pytest.raises(DecisionAnnotationError):
            ds.add_annotation(_entry(rationale=""))

    def test_emotion_tag_out_of_vocab_rejected(self) -> None:
        ds = _dataset()
        with pytest.raises(DecisionAnnotationError):
            ds.add_annotation(_entry(emotion_tag="euphoric"))

    def test_all_vocab_emotion_tags_accepted(self) -> None:
        ds = _dataset()
        for i, tag in enumerate(sorted(EMOTION_TAGS)):
            ann = ds.add_annotation(_entry(decision_id=f"dec-{i}", emotion_tag=tag))
            assert ann.emotion_tag == tag

    def test_empty_chart_ref_rejected(self) -> None:
        ds = _dataset()
        with pytest.raises(DecisionAnnotationError):
            ds.add_annotation(_entry(chart_ref=""))


# ──────────────────────────────────────────────────────────────────────────────
# 结果回填
# ──────────────────────────────────────────────────────────────────────────────


class TestFillOutcome:
    def test_fill_ok(self) -> None:
        ds = _dataset()
        ds.add_annotation(_entry())
        ann = ds.fill_outcome("dec-1", 0.0523, note="T+5 止盈")
        assert ann.outcome_return == pytest.approx(0.0523)
        assert ann.outcome_note == "T+5 止盈"

    def test_fill_unknown_decision_raises(self) -> None:
        ds = _dataset()
        with pytest.raises(DecisionAnnotationError):
            ds.fill_outcome("ghost", 0.01)

    def test_double_fill_rejected(self) -> None:
        ds = _dataset()
        ds.add_annotation(_entry())
        ds.fill_outcome("dec-1", 0.01)
        with pytest.raises(DecisionAnnotationError):
            ds.fill_outcome("dec-1", 0.02)


# ──────────────────────────────────────────────────────────────────────────────
# 导出
# ──────────────────────────────────────────────────────────────────────────────


class TestExport:
    def test_sft_export_only_filled(self) -> None:
        ds = _dataset()
        ds.add_annotation(_entry(decision_id="dec-1"))
        ds.add_annotation(_entry(decision_id="dec-2", decision_time=_T1))
        ds.fill_outcome("dec-2", 0.03)
        samples = ds.export_sft_samples()
        assert [s.decision_id for s in samples] == ["dec-2"]
        assert "600519.SH" in samples[0].prompt
        assert "放量突破年线" in samples[0].completion
        assert samples[0].outcome_return == pytest.approx(0.03)

    def test_sft_export_empty_when_none_filled(self) -> None:
        ds = _dataset()
        ds.add_annotation(_entry())
        assert ds.export_sft_samples() == []

    def test_review_export_deterministic_order(self) -> None:
        ds = _dataset()
        ds.add_annotation(_entry(decision_id="dec-b", decision_time=_T1))
        ds.add_annotation(_entry(decision_id="dec-a", decision_time=_T0))
        review = ds.export_review_dataset()
        assert [a.decision_id for a in review] == ["dec-a", "dec-b"]  # 按时点序

    def test_export_determinism_same_input_same_output(self) -> None:
        ds1, ds2 = _dataset(), _dataset()
        for ds in (ds1, ds2):
            ds.add_annotation(_entry())
            ds.fill_outcome("dec-1", 0.01)
        assert ds1.export_sft_samples() == ds2.export_sft_samples()


# ──────────────────────────────────────────────────────────────────────────────
# 版本管理
# ──────────────────────────────────────────────────────────────────────────────


class TestVersioning:
    def test_create_version_ok(self) -> None:
        ds = _dataset()
        ds.add_annotation(_entry())
        ds.fill_outcome("dec-1", 0.01)
        version = ds.create_version("v1.0")
        assert version.n_annotations == 1
        assert version.n_filled == 1
        assert len(version.content_hash) == 64
        assert version.created_at == _T0

    def test_version_tag_conflict_rejected(self) -> None:
        ds = _dataset()
        ds.create_version("v1.0")
        with pytest.raises(DecisionAnnotationError):
            ds.create_version("v1.0")

    def test_empty_version_tag_rejected(self) -> None:
        ds = _dataset()
        with pytest.raises(DecisionAnnotationError):
            ds.create_version("")

    def test_content_hash_changes_with_data(self) -> None:
        ds = _dataset()
        v_empty = ds.create_version("v0")
        ds.add_annotation(_entry())
        v_one = ds.create_version("v1")
        assert v_empty.content_hash != v_one.content_hash

    def test_content_hash_deterministic(self) -> None:
        ds1, ds2 = _dataset(), _dataset()
        for ds in (ds1, ds2):
            ds.add_annotation(_entry())
        assert ds1.create_version("v1").content_hash == ds2.create_version("v1").content_hash

    def test_list_versions_order(self) -> None:
        ds = DecisionAnnotationDataset(connection=sqlite3.connect(":memory:"), clock=lambda: _T0)
        ds.create_version("v-b")
        ds2_clock = lambda: _T1  # noqa: E731
        ds._clock = ds2_clock
        ds.create_version("v-a")
        versions = ds.list_versions()
        assert [v.version_tag for v in versions] == ["v-b", "v-a"]  # 按创建时序

    def test_get_unknown_version_raises(self) -> None:
        ds = _dataset()
        with pytest.raises(DecisionAnnotationError):
            ds.get_version("ghost")


# ──────────────────────────────────────────────────────────────────────────────
# 查询
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_get_unknown_annotation_raises(self) -> None:
        ds = _dataset()
        with pytest.raises(DecisionAnnotationError):
            ds.get_annotation("ghost")

    def test_stats(self) -> None:
        ds = _dataset()
        ds.add_annotation(_entry(decision_id="dec-1"))
        ds.add_annotation(_entry(decision_id="dec-2"))
        ds.fill_outcome("dec-1", -0.02)
        assert ds.stats() == {"n_annotations": 2, "n_filled": 1}
