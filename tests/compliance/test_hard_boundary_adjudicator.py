"""MOD-CMP-005 硬边界功能裁定门禁 单元测试（43 号 §6，BM-BUY-12）。"""

from __future__ import annotations

import yaml

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.hard_boundary_adjudicator import (
    FeatureGate,
    FeatureGateDecision,
    FeatureVerdict,
)

_FEATURES = {
    "features": [
        {
            "feature": "市场操纵检测",
            "verdict": "BUILDABLE",
            "reason": "自证清白",
            "adjudicated_at": "2026-08-01",
            "re_review_condition": "—",
            "related_bm": "BM-BUY-15",
        },
        {
            "feature": "T+0 变相回转交易工具",
            "verdict": "FORBIDDEN",
            "reason": "法规明令禁止",
            "adjudicated_at": "2026-08-15",
            "re_review_condition": "T+0 试点放开",
            "related_bm": None,
        },
    ]
}


def _gate(tmp_path, data=None) -> FeatureGate:
    p = tmp_path / "adj.yaml"
    p.write_text(yaml.safe_dump(data if data is not None else _FEATURES, allow_unicode=True), encoding="utf-8")
    return FeatureGate(p, ComplianceLogger(tmp_path / "c.jsonl"))


def test_buildable_pass(tmp_path):
    r = _gate(tmp_path).check("市场操纵检测")
    assert r.decision is FeatureGateDecision.PASS
    assert r.entry is not None and r.entry.verdict is FeatureVerdict.BUILDABLE
    assert r.entry.related_bm == "BM-BUY-15"


def test_forbidden_block_with_rereview_hint(tmp_path):
    r = _gate(tmp_path).check("T+0 变相回转交易工具")
    assert r.decision is FeatureGateDecision.BLOCK
    assert "T+0 试点放开" in r.detail


def test_unregistered_pending_as_block(tmp_path):
    """未登记=PENDING 视同 BLOCK（裁定未决暂缓上线，安全优先）。"""
    r = _gate(tmp_path).check("全新未裁定功能")
    assert r.decision is FeatureGateDecision.BLOCK
    assert r.entry is None
    assert "PENDING" in r.detail


def test_registry_missing_fail_closed(tmp_path):
    """登记表不可读 → 一切 BLOCK（Fail-Closed）。"""
    g = FeatureGate(tmp_path / "nope.yaml", ComplianceLogger(tmp_path / "c.jsonl"))
    r = g.check("任何功能")
    assert r.decision is FeatureGateDecision.BLOCK
    assert "Fail-Closed" in r.detail


def test_registry_corrupt_fail_closed(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("features: [unclosed", encoding="utf-8")
    g = FeatureGate(p, ComplianceLogger(tmp_path / "c.jsonl"))
    assert g.check("x").decision is FeatureGateDecision.BLOCK


def test_list_entries(tmp_path):
    assert len(_gate(tmp_path).list_entries()) == 2


def test_check_logged(tmp_path):
    log = ComplianceLogger(tmp_path / "c.jsonl")
    p = tmp_path / "adj.yaml"
    p.write_text(yaml.safe_dump(_FEATURES, allow_unicode=True), encoding="utf-8")
    FeatureGate(p, log).check("市场操纵检测")
    assert log.read_all()[-1].event_type == "FEATURE_GATE_CHECK"


def test_real_registry_seed_integrity(tmp_path):
    """仓内真表：19 条种子齐全且关键裁定在位（防误删回归）。"""
    from zephyr.compliance.hard_boundary_adjudicator import DEFAULT_REGISTRY_PATH

    g = FeatureGate(DEFAULT_REGISTRY_PATH, ComplianceLogger(tmp_path / "c.jsonl"))
    entries = {e.feature: e for e in g.list_entries()}
    assert len(entries) == 19
    assert entries["T+0 变相回转交易工具"].verdict is FeatureVerdict.FORBIDDEN
    assert entries["50μs 订单停留时间锁"].verdict is FeatureVerdict.FORBIDDEN
    assert g.check("市场操纵检测（Market Manipulation Detector）").decision is FeatureGateDecision.PASS
