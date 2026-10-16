"""goal_readiness_aggregator 测试（Q6，裁定#516）——纯注入零库依赖＋分母交叉核。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]  # tests/data → worktree 根（usercustomize 主区 src 优先级压制）
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src"))

from zephyr.data.goal_readiness_aggregator import (  # noqa: E402
    _grade,
    _is_core,
    aggregate,
)

GOAL = {
    "family": "F01_大盘两态",
    "goal_statement": "x",
    "output_contract": "y",
    "exam_ref": "z",
    "campaign_ref": "w",
    "status": "active",
}


def _tdm(nodes, edges=None):
    return {"nodes": nodes, "edges": edges or []}


def _node(nid, **kw):
    base = {"node_id": nid, "confidence": "proposed", "goal": dict(GOAL)}
    base.update(kw)
    return base


# ── 分档 ─────────────────────────────────────────────────────────
def test_grade_green_all_four():
    st = _grade(GOAL, has_card=True, has_consumer=True, has_reading=True)
    assert st[0] == "green" and st[1:5] == (1, 1, 1, 1)


def test_grade_yellow_exactly_one_missing():
    for kw in (
        {"has_card": True, "has_consumer": True, "has_reading": False},
        {"has_card": True, "has_consumer": False, "has_reading": True},
        {"has_card": False, "has_consumer": True, "has_reading": True},
    ):
        st = _grade(GOAL, **kw)
        assert st[0] == "yellow", kw
    st = _grade({**GOAL, "goal_statement": ""}, has_card=True, has_consumer=True, has_reading=True)
    assert st[0] == "yellow" and "goal" in st[5]


def test_grade_red_missing_two_plus():
    st = _grade(GOAL, has_card=False, has_consumer=False, has_reading=True)
    assert st[0] == "red" and "缺2件" in st[5]
    st = _grade(GOAL, has_card=False, has_consumer=False, has_reading=False)
    assert st[0] == "red"


def test_grade_suspended_not_red():
    st = _grade(
        {**GOAL, "status": "suspended", "suspension_basis": "B 档"},
        has_card=True,
        has_consumer=False,
        has_reading=False,
    )
    assert st[0] == "suspended" and "不计红" in st[5]


def test_grade_no_goal_block_red():
    st = _grade(None, has_card=True, has_consumer=True, has_reading=True)
    assert st[0] == "red" and st[1] == 0


# ── 聚合（注入零库） ─────────────────────────────────────────────
def test_aggregate_denominator_and_summary():
    nodes = [
        _node("TDM-E-L1", confidence="verified"),
        _node("TDM-E-L9-A01", goal={**GOAL, "status": "suspended_reference"}),
        _node("TDM-E-L9-B01", goal={**GOAL, "status": "suspended"}),
        _node("TDM-C-L1", goal={**GOAL, "status": "suspended"}),
        _node("TDM-E-L9-AGG"),
        _node("TDM-E-L9-G5"),
    ]
    rows = aggregate(
        "2026-10-13",
        tdm=_tdm(nodes, [{"from": "TDM-E-L1", "to": "TDM-E-FLOW"}]),
        cards={"TDM-E-L1": 2, "TDM-E-L9-A01": 1, "TDM-E-L9-B01": 1, "TDM-E-L9-G5": 1},
        scores={"TDM-E-L1"},
        produced_at="2026-10-13T12:00:00+08:00",
    )
    by = {r["node_id"]: r for r in rows}
    assert by["TDM-E-L1"]["status"] == "green"  # 目标+卡+边消费+verified 读数
    assert by["TDM-E-L9-A01"]["status"] == "suspended"  # A 档=引用型
    assert by["TDM-E-L9-B01"]["status"] == "suspended"
    assert by["TDM-C-L1"]["status"] == "suspended"
    assert by["TDM-E-L9-G5"]["status"] == "red"  # 无边无 mounts 无读数=缺2
    summ = rows[-1]
    assert summ["node_id"] == "AGG-GOAL" and "分母=2" in summ["detail"] and "red=1" in summ["detail"]
    assert len(rows) == 7  # 6 节点＋1 汇总


def test_aggregate_mounts_count_as_consumer():
    nodes = [_node("TDM-P-P2-02", module_mounts=["MOD-SELL-018"])]
    rows = aggregate("2026-10-13", tdm=_tdm(nodes), cards={"TDM-P-P2-02": 1}, scores=set(), produced_at="t")
    assert rows[0]["has_consumer"] == 1 and rows[0]["status"] == "yellow"  # 恰缺 reading


# ── 分母口径交叉核（真源=tdm_goal_blocks 同判据） ─────────────────
def test_core_denominator_cross_check_with_injector_truth():
    """仓内真实 TDM：151 分母与注入器口径逐位一致（真源唯一性回归）。"""
    import importlib.util

    repo = _REPO
    spec = importlib.util.spec_from_file_location(
        "tdm_goal_blocks", repo / "scripts" / "governance" / "tdm_goal_blocks.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import yaml

    d = yaml.safe_load((repo / "config" / "trading_decision_map.yaml").read_text(encoding="utf-8"))
    mine = [n["node_id"] for n in d["nodes"] if _is_core(n["node_id"])]
    truth = [
        n["node_id"]
        for n in d["nodes"]
        if not (
            mod.RE_SRC_LINE.match(n["node_id"]) or mod.RE_CRYPTO.match(n["node_id"]) or n["node_id"] == mod.AGG_NODE
        )
    ]
    assert mine == truth and len(mine) == 151
