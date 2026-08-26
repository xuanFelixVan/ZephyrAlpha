# [BLUEPRINT] MOD-DATA_GOV-013 | docs/03_modules/_domain_data_governance/ml_lineage_tracker/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATA_GOV-013 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_governance.test_ml_lineage_tracker
# [TESTS] src/zephyr/data_governance/ml_lineage_tracker.py
"""MOD-DATA_GOV-013 单元测试：ml_lineage_tracker AI-ML 管线血缘追踪器。

蓝图验收（B10-02324/CAND-DATGOV-010，A1 M8-NEW-05）：
数据集版本->特征版本->模型版本->线上预测四类边词表闭合 + 登记接口
（experiment_tracking 事件经注入适配器落边）+ 模型到数据全链反查 +
预测到训练样本溯源。适配器全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data_governance.ml_lineage_tracker",
    reason="ml_lineage_tracker not importable",
)

from zephyr.data_governance.ml_lineage_tracker import (  # noqa: E402
    MlEdgeKind,
    MlLineageError,
    MlLineageTracker,
    MlNodeKind,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)


def _tracker() -> MlLineageTracker:
    """链路：ds_v1 -> feat_v3 -> model_v7 -> pred_99；另有 ds_v1 -> model_v7 直连。"""
    t = MlLineageTracker(clock=lambda: _T0)
    t.register_node("ds_v1", MlNodeKind.DATASET)
    t.register_node("feat_v3", MlNodeKind.FEATURE)
    t.register_node("model_v7", MlNodeKind.MODEL)
    t.register_node("pred_99", MlNodeKind.PREDICTION)
    t.register_edge(MlEdgeKind.DATASET_TO_FEATURE, "ds_v1", "feat_v3")
    t.register_edge(MlEdgeKind.FEATURE_TO_MODEL, "feat_v3", "model_v7")
    t.register_edge(MlEdgeKind.MODEL_TO_PREDICTION, "model_v7", "pred_99")
    return t


# ──────────────────────────────────────────────────────────────────────────────
# 节点登记（词表闭合）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterNode:
    def test_register_and_idempotent(self) -> None:
        t = MlLineageTracker()
        t.register_node("ds_v1", MlNodeKind.DATASET)
        t.register_node("ds_v1", MlNodeKind.DATASET)  # 幂等不抛
        assert t.node_kind("ds_v1") is MlNodeKind.DATASET

    def test_empty_node_id_raises(self) -> None:
        t = MlLineageTracker()
        with pytest.raises(MlLineageError):
            t.register_node("", MlNodeKind.DATASET)

    def test_vocab_outside_kind_raises(self) -> None:
        t = MlLineageTracker()
        with pytest.raises(MlLineageError):
            t.register_node("x", "pipeline")  # type: ignore[arg-type]

    def test_kind_conflict_raises(self) -> None:
        t = MlLineageTracker()
        t.register_node("x", MlNodeKind.DATASET)
        with pytest.raises(MlLineageError):
            t.register_node("x", MlNodeKind.MODEL)


# ──────────────────────────────────────────────────────────────────────────────
# 边登记（词表闭合 + 方向匹配）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterEdge:
    def test_four_edge_kinds_closed(self) -> None:
        assert {k.value for k in MlEdgeKind} == {
            "dataset_to_feature", "feature_to_model", "model_to_prediction", "dataset_to_model",
        }

    def test_register_edge_ok(self) -> None:
        t = _tracker()
        assert len(t.edges()) == 3

    def test_unknown_node_raises(self) -> None:
        t = _tracker()
        with pytest.raises(MlLineageError):
            t.register_edge(MlEdgeKind.DATASET_TO_FEATURE, "ghost", "feat_v3")
        with pytest.raises(MlLineageError):
            t.register_edge(MlEdgeKind.DATASET_TO_FEATURE, "ds_v1", "ghost")

    def test_vocab_outside_edge_kind_raises(self) -> None:
        t = _tracker()
        with pytest.raises(MlLineageError):
            t.register_edge("model_to_dataset", "model_v7", "ds_v1")  # type: ignore[arg-type]

    def test_direction_mismatch_raises(self) -> None:
        t = _tracker()
        with pytest.raises(MlLineageError):
            t.register_edge(MlEdgeKind.DATASET_TO_FEATURE, "ds_v1", "model_v7")  # 目标非 feature

    def test_dataset_to_model_direct_ok(self) -> None:
        t = _tracker()
        t.register_edge(MlEdgeKind.DATASET_TO_MODEL, "ds_v1", "model_v7")
        assert len(t.edges()) == 4

    def test_duplicate_edge_idempotent(self) -> None:
        t = _tracker()
        t.register_edge(MlEdgeKind.DATASET_TO_FEATURE, "ds_v1", "feat_v3")
        assert len(t.edges()) == 3  # 不新增

    def test_reverse_edge_blocked_by_direction_check(self) -> None:
        # 闭合词表下 kind 序号严格递增（dataset<feature<model<prediction），
        # 任何"回流"尝试必因方向不符被拒（等效防环门禁）。
        t = _tracker()
        with pytest.raises(MlLineageError):
            t.register_edge(MlEdgeKind.DATASET_TO_FEATURE, "feat_v3", "ds_v1")
        with pytest.raises(MlLineageError):
            t.register_edge(MlEdgeKind.FEATURE_TO_MODEL, "model_v7", "feat_v3")
        with pytest.raises(MlLineageError):
            t.register_edge(MlEdgeKind.MODEL_TO_PREDICTION, "pred_99", "model_v7")

    def test_edges_sorted_deterministic(self) -> None:
        t = _tracker()
        kinds_sources = [(e.kind.value, e.source) for e in t.edges()]
        assert kinds_sources == sorted(kinds_sources)


# ──────────────────────────────────────────────────────────────────────────────
# experiment 事件落边（注入适配器）
# ──────────────────────────────────────────────────────────────────────────────


class TestRegisterEvent:
    def test_event_via_adapter(self) -> None:
        def adapter(event):
            return [
                (MlEdgeKind.DATASET_TO_FEATURE, event["ds"], event["feat"]),
                (MlEdgeKind.FEATURE_TO_MODEL, event["feat"], event["model"]),
            ]

        t = MlLineageTracker(clock=lambda: _T0, event_adapter=adapter)
        for nid, kind in (("ds1", MlNodeKind.DATASET), ("f1", MlNodeKind.FEATURE), ("m1", MlNodeKind.MODEL)):
            t.register_node(nid, kind)
        edges = t.register_event({"ds": "ds1", "feat": "f1", "model": "m1"})
        assert len(edges) == 2
        assert t.datasets_of_model("m1") == ("ds1",)

    def test_event_without_adapter_raises(self) -> None:
        t = _tracker()
        with pytest.raises(MlLineageError):
            t.register_event({"any": 1})

    def test_adapter_exception_wrapped(self) -> None:
        def bad_adapter(event):
            raise ValueError("bad event")

        t = MlLineageTracker(clock=lambda: _T0, event_adapter=bad_adapter)
        with pytest.raises(MlLineageError):
            t.register_event({"x": 1})


# ──────────────────────────────────────────────────────────────────────────────
# 全链反查与预测溯源
# ──────────────────────────────────────────────────────────────────────────────


class TestTrace:
    def test_datasets_of_model_via_feature_chain(self) -> None:
        t = _tracker()
        assert t.datasets_of_model("model_v7") == ("ds_v1",)

    def test_datasets_of_model_includes_direct_edge(self) -> None:
        t = _tracker()
        t.register_node("ds_v2", MlNodeKind.DATASET)
        t.register_edge(MlEdgeKind.DATASET_TO_MODEL, "ds_v2", "model_v7")
        assert t.datasets_of_model("model_v7") == ("ds_v1", "ds_v2")

    def test_features_of_model(self) -> None:
        t = _tracker()
        assert t.features_of_model("model_v7") == ("feat_v3",)

    def test_model_of_prediction(self) -> None:
        t = _tracker()
        assert t.model_of_prediction("pred_99") == "model_v7"

    def test_trace_prediction_full_chain(self) -> None:
        t = _tracker()
        trace = t.trace_prediction("pred_99")
        assert trace.prediction_id == "pred_99"
        assert trace.model_versions == ("model_v7",)
        assert trace.feature_versions == ("feat_v3",)
        assert trace.dataset_versions == ("ds_v1",)

    def test_trace_unknown_prediction_raises(self) -> None:
        t = _tracker()
        with pytest.raises(MlLineageError):
            t.trace_prediction("ghost")

    def test_wrong_kind_query_raises(self) -> None:
        t = _tracker()
        with pytest.raises(MlLineageError):
            t.datasets_of_model("ds_v1")  # 非 model
        with pytest.raises(MlLineageError):
            t.trace_prediction("model_v7")  # 非 prediction
