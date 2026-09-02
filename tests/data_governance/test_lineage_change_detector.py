# [BLUEPRINT] MOD-DATA_GOV-010 | docs/03_modules/_domain_data_governance/lineage_change_detector/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATA_GOV-010 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_governance.test_lineage_change_detector
# [TESTS] src/zephyr/data_governance/lineage_change_detector.py
"""MOD-DATA_GOV-010 单元测试：lineage_change_detector 血缘变更检测器。

蓝图验收（B10-02319/CAND-DATGOV-007，A1 M8-S07；canonical 承接 CAND-DATGOV-012）：
周期快照边集合指纹 + 新增/删除/改向边检测 + 下游影响集合 DFS + 变更报告 +
下游依赖方通知回调 + detector_id/schedule 注册元数据。
通知回调全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data_governance.lineage_change_detector",
    reason="lineage_change_detector not importable",
)

from zephyr.data_governance.lineage_change_detector import (  # noqa: E402
    LineageChangeDetector,
    LineageChangeError,
    LineageChangeReport,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

_BASE_EDGES = [
    ("market.kline", "factor.mom20", "compute"),
    ("factor.mom20", "signal.alpha", "generate"),
]


def _detector(notified: list | None = None) -> LineageChangeDetector:
    return LineageChangeDetector(
        detector_id="det-lineage-01",
        schedule="0 6 * * *",
        clock=lambda: _T0,
        notifier=(lambda r: notified.append(r)) if notified is not None else None,
    )


def _baseline(det: LineageChangeDetector) -> None:
    det.take_snapshot(_BASE_EDGES)


# ──────────────────────────────────────────────────────────────────────────────
# 构造与快照
# ──────────────────────────────────────────────────────────────────────────────


class TestInitAndSnapshot:
    def test_empty_detector_id_raises(self) -> None:
        with pytest.raises(LineageChangeError):
            LineageChangeDetector(detector_id="")

    def test_metadata_registered(self) -> None:
        det = _detector()
        assert det.detector_id == "det-lineage-01"
        assert det.schedule == "0 6 * * *"

    def test_snapshot_fingerprint_deterministic(self) -> None:
        det = _detector()
        s1 = det.take_snapshot(_BASE_EDGES)
        s2 = det.take_snapshot(list(reversed(_BASE_EDGES)))
        assert s1.fingerprint == s2.fingerprint  # 与输入顺序无关

    def test_snapshot_edges_sorted_dedup(self) -> None:
        det = _detector()
        snap = det.take_snapshot(_BASE_EDGES + [_BASE_EDGES[0]])
        assert len(snap.edges) == 2
        assert snap.edges == tuple(sorted(_BASE_EDGES))

    def test_invalid_edge_raises(self) -> None:
        det = _detector()
        with pytest.raises(LineageChangeError):
            det.take_snapshot([("", "b", "t")])
        with pytest.raises(LineageChangeError):
            det.take_snapshot([("a", "", "t")])

    def test_self_loop_edge_raises(self) -> None:
        det = _detector()
        with pytest.raises(LineageChangeError):
            det.take_snapshot([("a", "a", "t")])


# ──────────────────────────────────────────────────────────────────────────────
# diff 检测（新增/删除/改向）
# ──────────────────────────────────────────────────────────────────────────────


class TestDetect:
    def test_detect_without_baseline_raises(self) -> None:
        det = _detector()
        with pytest.raises(LineageChangeError):
            det.detect(_BASE_EDGES)

    def test_no_change_empty_report_no_notify(self) -> None:
        notified: list[LineageChangeReport] = []
        det = _detector(notified)
        _baseline(det)
        report = det.detect(_BASE_EDGES)
        assert report.added == () and report.removed == () and report.redirected == ()
        assert notified == []

    def test_added_edge(self) -> None:
        det = _detector()
        _baseline(det)
        report = det.detect(_BASE_EDGES + [("signal.alpha", "order.exec", "route")])
        assert report.added == (("signal.alpha", "order.exec", "route"),)
        assert report.removed == ()

    def test_removed_edge(self) -> None:
        det = _detector()
        _baseline(det)
        report = det.detect([_BASE_EDGES[1]])
        assert report.removed == (("market.kline", "factor.mom20", "compute"),)

    def test_redirected_edge(self) -> None:
        det = _detector()
        _baseline(det)
        report = det.detect(
            [
                ("market.kline", "factor.rsi14", "compute"),  # mom20 → rsi14 改向
                _BASE_EDGES[1],
            ]
        )
        assert len(report.redirected) == 1
        r = report.redirected[0]
        assert r.source == "market.kline"
        assert r.old_target == "factor.mom20"
        assert r.new_target == "factor.rsi14"
        assert report.added == () and report.removed == ()

    def test_redirect_leftover_stays_added(self) -> None:
        det = _detector()
        det.take_snapshot([("a", "b", "t")])
        report = det.detect([("a", "c", "t"), ("a", "d", "t")])  # 1 删 2 增 → 1 改向 + 1 新增
        assert len(report.redirected) == 1
        assert report.redirected[0].old_target == "b"
        assert report.redirected[0].new_target == "c"
        assert report.added == (("a", "d", "t"),)

    def test_transformation_change_is_remove_and_add(self) -> None:
        det = _detector()
        det.take_snapshot([("a", "b", "compute")])
        report = det.detect([("a", "b", "aggregate")])  # 同 (a,b) transform 变更
        assert report.redirected == ()
        assert report.removed == (("a", "b", "compute"),)
        assert report.added == (("a", "b", "aggregate"),)

    def test_baseline_advances_after_detect(self) -> None:
        det = _detector()
        _baseline(det)
        det.detect(_BASE_EDGES + [("x", "y", "t")])
        report = det.detect(_BASE_EDGES + [("x", "y", "t")])
        assert report.added == ()  # 第二次已与新基线一致

    def test_report_fingerprints(self) -> None:
        det = _detector()
        _baseline(det)
        report = det.detect(_BASE_EDGES + [("x", "y", "t")])
        assert report.fingerprint_before != report.fingerprint_after
        assert report.fingerprint_after == det.fingerprint_of(_BASE_EDGES + [("x", "y", "t")])


# ──────────────────────────────────────────────────────────────────────────────
# 下游影响集合（DFS）与通知
# ──────────────────────────────────────────────────────────────────────────────


class TestImpactAndNotify:
    def test_impact_dfs_transitive(self) -> None:
        det = _detector()
        _baseline(det)
        report = det.detect(_BASE_EDGES + [("signal.alpha", "order.exec", "route")])
        # 变更点 signal.alpha 的下游 + order.exec 本身
        assert report.impacted_downstream == ("order.exec",)

    def test_impact_on_removed_uses_new_graph(self) -> None:
        det = _detector()
        det.take_snapshot([("a", "b", "t"), ("b", "c", "t")])
        report = det.detect([("a", "b", "t")])  # 删 b->c；新图 b 无下游
        assert report.impacted_downstream == ()

    def test_impact_sorted_dedup(self) -> None:
        det = _detector()
        det.take_snapshot([("a", "b", "t")])
        report = det.detect([("a", "b", "t"), ("a", "c", "t"), ("c", "b", "t")])
        assert report.impacted_downstream == tuple(sorted(report.impacted_downstream))
        assert len(set(report.impacted_downstream)) == len(report.impacted_downstream)

    def test_notifier_called_on_change(self) -> None:
        notified: list[LineageChangeReport] = []
        det = _detector(notified)
        _baseline(det)
        det.detect(_BASE_EDGES + [("x", "y", "t")])
        assert len(notified) == 1
        assert notified[0].detector_id == "det-lineage-01"

    def test_notifier_exception_swallowed(self) -> None:
        det = LineageChangeDetector(
            detector_id="det-x",
            clock=lambda: _T0,
            notifier=lambda r: (_ for _ in ()).throw(RuntimeError("boom")),
        )
        _baseline(det)
        report = det.detect(_BASE_EDGES + [("x", "y", "t")])  # 不抛
        assert report.added == (("x", "y", "t"),)

    def test_downstream_impact_static(self) -> None:
        edges = [("a", "b", ""), ("b", "c", ""), ("a", "d", "")]
        assert LineageChangeDetector.downstream_impact(edges, ["a"]) == ("b", "c", "d")
