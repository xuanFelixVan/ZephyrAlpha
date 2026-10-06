# [BLUEPRINT] MOD-INF-050 | docs/03_modules/MOD-INF-050/
# [MODULE] tests.intelligence.test_sentinel_hallucination_detector
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/intelligence/test_sentinel_hallucination_detector.py -q
# [TTL] permanent

"""sentinel 幻觉检测器（MOD-INF-050）单元测试——委托模式/审计留痕/统计。"""

from __future__ import annotations

import pytest

from zephyr.intelligence.sentinel_hallucination_detector import (
    SentinelAuditRecord,
    SentinelDetectorError,
    SentinelHallucinationDetector,
)
from zephyr.orchestrator.hallucination_detector import (
    HallucinationDetector,
    HallucinationResult,
)


def _make_sentinel(**kwargs) -> SentinelHallucinationDetector:
    return SentinelHallucinationDetector(**kwargs)


class TestDelegation:
    def test_detect_delegates_to_inner_detector(self):
        s = _make_sentinel()
        result = s.detect("IC: 0.35 的因子有效", risk_level="M")
        assert isinstance(result, HallucinationResult)
        assert result.triggered is True
        # 无 caller 注入 → keyword 兜底路径
        assert result.fallback_used == "keyword"

    def test_keyword_rule_hit_marks_hallucination(self):
        s = _make_sentinel()
        result = s.detect("该因子 IC: 5.2 远超基准", risk_level="M")
        assert result.is_hallucination is True
        assert any("numeric_out_of_range" in e for e in result.evidence)

    def test_custom_detector_is_used(self):
        inner = HallucinationDetector(daily_budget_usd=99.0)
        s = _make_sentinel(detector=inner)
        assert s.detector is inner
        result = s.detect("正常陈述", risk_level="L")
        assert result.triggered is True

    def test_empty_claim_fail_closed(self):
        s = _make_sentinel()
        with pytest.raises(SentinelDetectorError):
            s.detect("")
        with pytest.raises(SentinelDetectorError):
            s.detect("   ")


class TestAuditTrail:
    def test_each_detect_appends_audit_record(self):
        s = _make_sentinel()
        s.detect("claim-1", risk_level="L")
        s.detect("claim-2", risk_level="M")
        trail = s.audit_trail()
        assert len(trail) == 2
        assert all(isinstance(r, SentinelAuditRecord) for r in trail)
        assert trail[0].seq == 1 and trail[1].seq == 2
        assert trail[0].claim_hash != trail[1].claim_hash
        assert trail[1].prev_hash == trail[0].record_hash

    def test_audit_chain_verifies(self):
        s = _make_sentinel()
        for i in range(3):
            s.detect(f"claim-{i}", risk_level="L")
        assert s.verify_audit_chain() is True

    def test_audit_chain_detects_tamper(self):
        s = _make_sentinel()
        s.detect("claim-1", risk_level="L")
        rec = s.audit_trail()[0]
        s._records[0] = SentinelAuditRecord(
            seq=rec.seq,
            claim_hash=rec.claim_hash,
            is_hallucination=not rec.is_hallucination,
            risk_level=rec.risk_level,
            fallback_used=rec.fallback_used,
            prev_hash=rec.prev_hash,
            record_hash=rec.record_hash,
        )
        assert s.verify_audit_chain() is False

    def test_no_claim_text_in_audit(self):
        s = _make_sentinel()
        s.detect("敏感 claim 内容", risk_level="L")
        rec = s.audit_trail()[0]
        assert "敏感" not in rec.claim_hash


class TestStats:
    def test_stats_counts(self):
        s = _make_sentinel()
        s.detect("IC: 9.9 异常", risk_level="M")  # hallucination
        s.detect("正常陈述", risk_level="L")  # not hallucination
        stats = s.stats()
        assert stats["total_detects"] == 2
        assert stats["hallucination_count"] == 1
        assert stats["audit_records"] == 2

    def test_error_code_namespace(self):
        assert SentinelDetectorError.error_code == "ZA-IT-0010"
