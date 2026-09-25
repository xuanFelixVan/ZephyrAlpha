"""test_venues — C4 考场适配器×4：薄封装零复制 + fail-closed 拒考 + 判据快照同源。"""

from __future__ import annotations

import pytest

from zephyr.ai_layer.comparator import VENUE_IDS, VenueUnavailable, import_ruler, ruler_available
from zephyr.ai_layer.comparator import venue_c4, venue_dual_run, venue_replay, venue_tool_bench

ALL_VENUES = (venue_c4, venue_replay, venue_dual_run, venue_tool_bench)


# ---------------------------------------------------------------------------
# 制式一致性（四适配器同形态；VENUE_ID 与包注册表同源）
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("venue", ALL_VENUES, ids=lambda v: v.VENUE_ID)
def test_venue_shape(venue: object) -> None:
    assert venue.VENUE_ID in VENUE_IDS                      # type: ignore[attr-defined]
    assert venue.RULER_MODULES                              # type: ignore[attr-defined]
    assert callable(venue.available) and callable(venue.criteria) and callable(venue.run)  # type: ignore[attr-defined]


@pytest.mark.parametrize("venue", ALL_VENUES, ids=lambda v: v.VENUE_ID)
def test_venue_criteria_snapshot(venue: object) -> None:
    if not venue.available():  # type: ignore[attr-defined]
        pytest.skip("考尺未建成（fail-closed 是既定态）")
    snap = venue.criteria()  # type: ignore[attr-defined]
    assert isinstance(snap, dict) and snap["venue"] == venue.VENUE_ID  # type: ignore[attr-defined]


def test_criteria_snapshots_reference_ruler_constants() -> None:
    # SSOT 引用不复制：快照值必须与考尺模块常量逐值相等（改考尺不改快照=测试红）
    rr = import_ruler("zephyr.governance.standards_governance.rule_replay")
    snap = venue_replay.criteria()
    assert snap["P1_pass_leak_allowed"] == rr.P1_PASS_LEAK_ALLOWED == 0
    assert snap["P2_new_block_rate"] == rr.P2_NEW_BLOCK_RATE == 0.02
    assert snap["P3_jaccard_global"] == rr.P3_JACCARD_GLOBAL == 0.98
    assert snap["P3_jaccard_per_gate"] == rr.P3_JACCARD_PER_GATE == 0.95


def test_c4_available_and_dsr_batch_dispatch() -> None:
    assert venue_c4.available() is True
    out = venue_c4.run({
        "op": "dsr_batch",
        "returns_by_variant": {
            "champ": [0.01, 0.02, 0.01, 0.015, 0.012],
            "cand": [0.02, 0.03, 0.025, 0.031, 0.028],
        },
    })
    assert out["venue"] == "venue_c4" and out["op"] == "dsr_batch"
    assert isinstance(out["passed"], bool) and out["report"] is not None


# ---------------------------------------------------------------------------
# fail-closed：未知 op / 契约不符 / 考尺不可达
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("venue", ALL_VENUES, ids=lambda v: v.VENUE_ID)
def test_unknown_op_rejected(venue: object) -> None:
    with pytest.raises(ValueError, match="unknown_op"):
        venue.run({"op": "nope"})  # type: ignore[attr-defined]


def test_replay_request_contract_enforced() -> None:
    rr = import_ruler("zephyr.governance.standards_governance.rule_replay")
    with pytest.raises(TypeError, match="ReplayRequest"):
        venue_replay.run({"op": "replay", "request": {"repo_root": "not-a-request"}})
    assert rr.ReplayRequest is not None  # 契约真源在考尺侧


def test_dual_run_stats_dispatch() -> None:
    out = venue_dual_run.run({"op": "mcnemar", "b": 3, "c": 1})
    assert 0.0 <= out["p"] <= 1.0
    # n<10 → NaN=样本不足不硬判（OBJ_M 诚实条款的薄封装转调，零逻辑复制）
    small = venue_dual_run.run({"op": "wilcoxon", "diffs": [1.0, 2.0, 3.0, -1.0]})
    import math

    assert math.isnan(small["p"])
    out2 = venue_dual_run.run({
        "op": "wilcoxon",
        "diffs": [1.0, 2.0, 2.5, 3.0, -1.0, 2.0, 1.5, 0.5, 1.2, 2.8],
    })
    assert 0.0 <= out2["p"] <= 1.0


def test_dual_run_criteria_freeze_hash() -> None:
    snap = venue_dual_run.criteria()
    assert len(snap["freeze_hash"]) == 64 and snap["criteria_path"].endswith("dual_run_criteria.yaml")


# ---------------------------------------------------------------------------
# venue_tool_bench：OBJ_T 考尺未建成 → 拒考是正常态（DESIGN §2.1 工具行）
# ---------------------------------------------------------------------------

def test_tool_bench_ruler_wired_to_objt_suite() -> None:
    """接线批 2026-09-24：指针已接通 OBJ_T 真源；拒考从"考尺缺席"升级为"runner 缺席"。"""
    assert venue_tool_bench.RULER_MODULES == ("zephyr.ai_layer.tools.suite",)
    assert venue_tool_bench.available() is True
    snap = venue_tool_bench.criteria()
    assert snap["task_suite_version"] == "tool_suite_v0"
    from zephyr.ai_layer.tools.suite import SuiteError
    with pytest.raises(SuiteError, match="runner_not_injected"):
        venue_tool_bench.run({"op": "suite_run", "tool_ref": "t", "suite_version": "tool_suite_v0"})


def test_tool_bench_fail_closed_when_ruler_absent(monkeypatch) -> None:
    """考尺真身缺席=拒考（fail-closed 路径保留，模拟缺席注入）。"""
    def _boom(_mod: str):
        raise VenueUnavailable("ruler_unreachable")
    monkeypatch.setattr(venue_tool_bench, "import_ruler", _boom)
    monkeypatch.setattr(venue_tool_bench, "ruler_available", lambda _mods: False)
    assert venue_tool_bench.available() is False
    with pytest.raises(VenueUnavailable, match="ruler_unreachable"):
        venue_tool_bench.run({"op": "suite_run", "tool_ref": "t", "suite_version": "v0"})
    with pytest.raises(VenueUnavailable, match="ruler_unreachable"):
        venue_tool_bench.criteria()


def test_import_ruler_and_availability_probe() -> None:
    with pytest.raises(VenueUnavailable, match="ruler_unreachable"):
        import_ruler("zephyr.ai_layer.comparator.definitely_not_a_module")
    assert ruler_available([]) is True
    assert ruler_available(("zephyr.ai_layer.comparator.venue_c4",)) is True
    assert ruler_available(("no.such.module",)) is False
