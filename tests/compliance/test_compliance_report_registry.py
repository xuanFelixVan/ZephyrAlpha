# [BLUEPRINT] MOD-CMP-007 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""MOD-CMP-009 程序化交易报告登记+报送门禁 单元测试（43 号 §7.4/§7.5）。"""

from __future__ import annotations

import yaml

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.compliance_report_registry import (
    ComplianceReportRegistry,
    ReportGate,
    ReportGateDecision,
)

_ITEMS = {
    "order_min_dwell_us": 50,
    "report_items": [
        {
            "item_id": "RPT-A",
            "name": "账户基本信息",
            "content_source": "券商",
            "timing": "首次交易前",
            "required": True,
            "reported_at": None,
            "broker_ack": False,
        },
        {
            "item_id": "RPT-B",
            "name": "交易软件信息",
            "content_source": "miniQMT",
            "timing": "首次交易前",
            "required": True,
            "reported_at": None,
            "broker_ack": False,
        },
    ],
}


def _gate(tmp_path, data=None) -> ReportGate:
    p = tmp_path / "rpt.yaml"
    p.write_text(yaml.safe_dump(data if data is not None else _ITEMS, allow_unicode=True), encoding="utf-8")
    return ReportGate(ComplianceReportRegistry(p), ComplianceLogger(tmp_path / "c.jsonl"))


def test_all_acked_pass(tmp_path):
    data = yaml.safe_load(yaml.safe_dump(_ITEMS))
    for it in data["report_items"]:
        it["broker_ack"] = True
        it["reported_at"] = "2026-08-15"
    assert _gate(tmp_path, data).check().decision is ReportGateDecision.PASS


def test_missing_ack_block_with_ids(tmp_path):
    """先报告后交易：任一必报项未确认 → BLOCK 并列出缺项。"""
    r = _gate(tmp_path).check()
    assert r.decision is ReportGateDecision.BLOCK
    assert set(r.missing) == {"RPT-A", "RPT-B"}


def test_optional_item_not_blocking(tmp_path):
    data = yaml.safe_load(yaml.safe_dump(_ITEMS))
    data["report_items"][0]["broker_ack"] = True
    data["report_items"][1]["required"] = False
    assert _gate(tmp_path, data).check().decision is ReportGateDecision.PASS


def test_registry_missing_fail_closed(tmp_path):
    g = ReportGate(ComplianceReportRegistry(tmp_path / "nope.yaml"), ComplianceLogger(tmp_path / "c.jsonl"))
    r = g.check()
    assert r.decision is ReportGateDecision.BLOCK
    assert "Fail-Closed" in r.detail


def test_order_min_dwell_us(tmp_path):
    p = tmp_path / "rpt.yaml"
    p.write_text(yaml.safe_dump(_ITEMS), encoding="utf-8")
    assert ComplianceReportRegistry(p).order_min_dwell_us() == 50


def test_check_logged(tmp_path):
    log = ComplianceLogger(tmp_path / "c.jsonl")
    p = tmp_path / "rpt.yaml"
    p.write_text(yaml.safe_dump(_ITEMS), encoding="utf-8")
    ReportGate(ComplianceReportRegistry(p), log).check()
    assert log.read_all()[-1].event_type == "REPORT_GATE_CHECK"


def test_real_registry_passes_after_reporting(tmp_path):
    """仓内真表：报送确认后 6 项全 ack → PASS（先报告后交易·后半段实证）+ 50μs 记录性参数。

    2026-09-27 改判：Owner 经认证对话确认 2025-12 开通 QMT 时已按券商流程报送全部六项，
    登记表 v1.0.1 回填 broker_ack/reported_at（合规状态是活事实，测试随真值演进）。
    BLOCK 侧行为（任一必报项缺失→拒单）由上方合成数据测试继续覆盖，fail-closed 语义不变。
    """
    log = ComplianceLogger(tmp_path / "c.jsonl")
    g = ReportGate(ComplianceReportRegistry(), log)
    r = g.check()
    assert r.decision is ReportGateDecision.PASS
    assert r.missing == ()
    for item in ComplianceReportRegistry().load_items():
        assert item.broker_ack is True
        assert item.reported_at  # 月锚 "2025-12"
    assert ComplianceReportRegistry().order_min_dwell_us() == 50
