"""MOD-CMP-008 数据源授权条款合规审计 单元测试（43 号 §5，BM-BUY-09）。"""

from __future__ import annotations

from datetime import date, timedelta

import pytest
import yaml

from zephyr.compliance.compliance_log import ComplianceLogger
from zephyr.compliance.license_usage_auditor import (
    LicenseAuditError,
    LicenseUsageAuditor,
    ViolationLevel,
)


def _registry(tmp_path, sources: list[dict]) -> LicenseUsageAuditor:
    p = tmp_path / "reg.yaml"
    p.write_text(yaml.safe_dump({"sources": sources}, allow_unicode=True), encoding="utf-8")
    return LicenseUsageAuditor(p, ComplianceLogger(tmp_path / "c.jsonl"))


_LEGACY = {"source_id": "SRC-X-001", "provider_name": "X", "compliance": "自由文本"}

_STRUCTURED = {
    "source_id": "SRC-Y-001",
    "provider_name": "Y",
    "compliance": {
        "vendor": "Y Corp",
        "license_type": "personal",
        "permitted_use": ["backtest", "display"],
        "redistribution": False,
        "derived_data_policy": "因子可自用不可发布",
        "expiry": (date.today() + timedelta(days=30)).isoformat(),
        "terms_ref": "docs/terms/y.pdf",
        "registered_at": date.today().isoformat(),
        "review_cycle_days": 90,
    },
}


def test_missing_section_backtest_only_compliant(tmp_path):
    """缺 compliance 段 → 仅 backtest 保守默认；backtest 用途合规。"""
    r = _registry(tmp_path, [_LEGACY]).audit("SRC-X-001", {"backtest"})
    assert r.compliant
    assert r.effective_permitted_use == frozenset({"backtest"})


def test_missing_section_live_trading_l1(tmp_path):
    """缺段源用于 live_trading → L1 超范围（最保守假设）。"""
    r = _registry(tmp_path, [_LEGACY]).audit("SRC-X-001", {"live_trading"})
    assert not r.compliant
    assert r.findings[0].level is ViolationLevel.L1_SCOPE


def test_structured_permitted_use_compliant(tmp_path):
    r = _registry(tmp_path, [_STRUCTURED]).audit("SRC-Y-001", {"backtest", "display"})
    assert r.compliant


def test_structured_scope_violation_l1(tmp_path):
    """trial/个人授权用于 ml_training 未许可 → L1。"""
    r = _registry(tmp_path, [_STRUCTURED]).audit("SRC-Y-001", {"ml_training"})
    assert any(f.level is ViolationLevel.L1_SCOPE for f in r.findings)


def test_expired_license_l2_fail_closed(tmp_path):
    src = dict(_STRUCTURED)
    src["compliance"] = dict(_STRUCTURED["compliance"], expiry=(date.today() - timedelta(days=1)).isoformat())
    r = _registry(tmp_path, [src]).audit("SRC-Y-001", {"backtest"})
    assert any(f.level is ViolationLevel.L2_EXPIRED for f in r.findings)
    assert any("Fail-Closed" in f.action for f in r.findings)


def test_redistribution_l3(tmp_path):
    r = _registry(tmp_path, [_STRUCTURED]).audit("SRC-Y-001", {"backtest", "redistribution"})
    assert any(f.level is ViolationLevel.L3_REDISTRIBUTION for f in r.findings)


def test_unknown_use_l1(tmp_path):
    r = _registry(tmp_path, [_STRUCTURED]).audit("SRC-Y-001", {"quantum_trading"})
    assert any("未知用途" in f.detail for f in r.findings)


def test_unregistered_source_raises(tmp_path):
    with pytest.raises(LicenseAuditError):
        _registry(tmp_path, [_LEGACY]).audit("SRC-ZZZ-999", {"backtest"})


def test_missing_registry_file_raises(tmp_path):
    a = LicenseUsageAuditor(tmp_path / "nope.yaml", ComplianceLogger(tmp_path / "c.jsonl"))
    with pytest.raises(LicenseAuditError):
        a.audit("SRC-X-001", {"backtest"})


def test_review_due_rules(tmp_path):
    """缺段 → 需复核；新登记 → 未到；超周期 → 到期。"""
    a = _registry(tmp_path, [_LEGACY, _STRUCTURED])
    assert a.review_due("SRC-X-001")  # 缺段
    assert not a.review_due("SRC-Y-001")  # 今日登记，90 天周期
    old = dict(_STRUCTURED)
    old["compliance"] = dict(_STRUCTURED["compliance"], registered_at=(date.today() - timedelta(days=100)).isoformat())
    a2 = _registry(tmp_path, [old])
    assert a2.review_due("SRC-Y-001")


def test_audit_logged(tmp_path):
    log = ComplianceLogger(tmp_path / "c.jsonl")
    p = tmp_path / "reg.yaml"
    p.write_text(yaml.safe_dump({"sources": [_LEGACY]}, allow_unicode=True), encoding="utf-8")
    LicenseUsageAuditor(p, log).audit("SRC-X-001", {"backtest"})
    assert log.read_all()[-1].event_type == "LICENSE_AUDIT"
