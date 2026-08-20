"""D-SIGNAL-06 信号审计日志 单元测试"""

import os
import tempfile
from datetime import datetime, timedelta, timezone

import pytest

from zephyr.signal_fundamental.audit.signal_audit_logger import (
    AuditLogConfig,
    AuditLogEntry,
    AuditSeverity,
    SignalAuditEvent,
    SignalAuditLogger,
    SignalEventType,
)


@pytest.fixture
def logger() -> SignalAuditLogger:
    return SignalAuditLogger()


@pytest.fixture
def file_logger() -> SignalAuditLogger:
    tmpdir = tempfile.mkdtemp()
    config = AuditLogConfig(log_dir=tmpdir)
    return SignalAuditLogger(config)


def make_event(
    event_type: SignalEventType = SignalEventType.GENERATED,
    signal_id: str = "SIG_001",
    symbol: str = "000001",
    severity: AuditSeverity = AuditSeverity.INFO,
) -> SignalAuditEvent:
    return SignalAuditEvent(
        event_type=event_type,
        signal_id=signal_id,
        symbol=symbol,
        timestamp=datetime(2026, 8, 3, 10, 0, tzinfo=timezone.utc),
        severity=severity,
        description="测试事件",
        metadata={"test": True},
        source_module="test_module",
    )


# ------------------------------------------------------------------
# 1. WORM写入
# ------------------------------------------------------------------
class TestWormWrite:
    def test_write_returns_entry(self, logger: SignalAuditLogger):
        entry = logger.log_event(make_event())
        assert isinstance(entry, AuditLogEntry)
        assert entry.entry_id == 1

    def test_entry_id_monotonic(self, logger: SignalAuditLogger):
        e1 = logger.log_event(make_event(signal_id="S1"))
        e2 = logger.log_event(make_event(signal_id="S2"))
        e3 = logger.log_event(make_event(signal_id="S3"))
        assert e1.entry_id < e2.entry_id < e3.entry_id
        assert e3.entry_id == 3

    def test_entries_immutable(self, logger: SignalAuditLogger):
        entry = logger.log_event(make_event())
        with pytest.raises((AttributeError, TypeError)):
            entry.entry_id = 999  # type: ignore[misc]

    def test_content_hash_present(self, logger: SignalAuditLogger):
        entry = logger.log_event(make_event())
        assert len(entry.content_hash) == 64  # SHA-256

    def test_file_mode_writes_to_file(self, file_logger: SignalAuditLogger):
        file_logger.log_event(make_event())
        assert file_logger.entry_count == 1
        # Verify file exists and has content
        log_files = [f for f in os.listdir(file_logger._writer._current_file.rsplit("\\", 1)[0]) if f.endswith(".log")]
        assert len(log_files) > 0


# ------------------------------------------------------------------
# 2. 便捷方法
# ------------------------------------------------------------------
class TestConvenienceMethods:
    def test_log_signal_generated(self, logger: SignalAuditLogger):
        entry = logger.log_signal_generated("SIG_001", "000001", source_module="D-SIGNAL-25")
        assert entry.event.event_type == SignalEventType.GENERATED
        assert entry.event.severity == AuditSeverity.INFO

    def test_log_signal_revoked(self, logger: SignalAuditLogger):
        entry = logger.log_signal_revoked("SIG_001", "000001", reason="SEVERE降级")
        assert entry.event.event_type == SignalEventType.REVOKED
        assert entry.event.severity == AuditSeverity.WARNING
        assert entry.event.metadata["reason"] == "SEVERE降级"

    def test_log_signal_degraded(self, logger: SignalAuditLogger):
        entry = logger.log_signal_degraded("SIG_001", "000001", degradation_level="MILD")
        assert entry.event.event_type == SignalEventType.DEGRADED
        assert entry.event.metadata["degradation_level"] == "MILD"


# ------------------------------------------------------------------
# 3. 查询接口
# ------------------------------------------------------------------
class TestQuery:
    def test_query_by_symbol(self, logger: SignalAuditLogger):
        logger.log_event(make_event(signal_id="S1", symbol="000001"))
        logger.log_event(make_event(signal_id="S2", symbol="000002"))
        logger.log_event(make_event(signal_id="S3", symbol="000001"))
        results = logger.query(symbol="000001")
        assert len(results) == 2
        assert all(r.event.symbol == "000001" for r in results)

    def test_query_by_signal_id(self, logger: SignalAuditLogger):
        logger.log_event(make_event(signal_id="S1"))
        logger.log_event(make_event(signal_id="S2"))
        results = logger.query(signal_id="S1")
        assert len(results) == 1
        assert results[0].event.signal_id == "S1"

    def test_query_by_event_type(self, logger: SignalAuditLogger):
        logger.log_event(make_event(event_type=SignalEventType.GENERATED))
        logger.log_event(make_event(event_type=SignalEventType.REVOKED))
        logger.log_event(make_event(event_type=SignalEventType.EXPIRED))
        results = logger.query(event_type=SignalEventType.REVOKED)
        assert len(results) == 1

    def test_query_by_time_range(self, logger: SignalAuditLogger):
        base = datetime(2026, 8, 3, 10, 0, tzinfo=timezone.utc)
        e1 = SignalAuditEvent(
            SignalEventType.GENERATED,
            "S1",
            "000001",
            base,
            AuditSeverity.INFO,
            "test",
        )
        e2 = SignalAuditEvent(
            SignalEventType.GENERATED,
            "S2",
            "000001",
            base + timedelta(hours=2),
            AuditSeverity.INFO,
            "test",
        )
        logger.log_event(e1)
        logger.log_event(e2)
        results = logger.query(
            start_time=base + timedelta(hours=1),
            end_time=base + timedelta(hours=3),
        )
        assert len(results) == 1
        assert results[0].event.signal_id == "S2"

    def test_query_limit(self, logger: SignalAuditLogger):
        for i in range(10):
            logger.log_event(make_event(signal_id=f"S{i}"))
        results = logger.query(limit=3)
        assert len(results) == 3

    def test_get_by_id(self, logger: SignalAuditLogger):
        entry = logger.log_event(make_event(signal_id="S1"))
        found = logger.get_by_id(entry.entry_id)
        assert found is not None
        assert found.entry_id == entry.entry_id

    def test_get_by_id_not_found(self, logger: SignalAuditLogger):
        assert logger.get_by_id(999) is None


# ------------------------------------------------------------------
# 4. 合规报告
# ------------------------------------------------------------------
class TestComplianceReport:
    def test_report_has_required_fields(self, logger: SignalAuditLogger):
        logger.log_event(make_event(event_type=SignalEventType.GENERATED))
        logger.log_event(make_event(event_type=SignalEventType.REVOKED))
        report = logger.generate_compliance_report()
        assert "total_entries" in report
        assert "event_type_breakdown" in report
        assert "severity_breakdown" in report
        assert "chain_integrity_valid" in report
        assert "worm_compliant" in report
        assert report["worm_compliant"] is True

    def test_report_counts_correct(self, logger: SignalAuditLogger):
        logger.log_event(make_event(event_type=SignalEventType.GENERATED))
        logger.log_event(make_event(event_type=SignalEventType.GENERATED))
        logger.log_event(make_event(event_type=SignalEventType.REVOKED))
        report = logger.generate_compliance_report()
        assert report["total_entries"] == 3
        assert report["event_type_breakdown"]["SIGNAL_GENERATED"] == 2
        assert report["event_type_breakdown"]["SIGNAL_REVOKED"] == 1

    def test_report_retention_policy(self, logger: SignalAuditLogger):
        report = logger.generate_compliance_report()
        assert report["retention_policy_years"] == 5  # SEC合规5年


# ------------------------------------------------------------------
# 5. 链式完整性
# ------------------------------------------------------------------
class TestChainIntegrity:
    def test_chain_valid_after_writes(self, logger: SignalAuditLogger):
        for i in range(5):
            logger.log_event(make_event(signal_id=f"S{i}"))
        assert logger.verify_integrity() is True

    def test_chain_genesis_hash(self, logger: SignalAuditLogger):
        entry = logger.log_event(make_event())
        assert entry.prev_hash == "0" * 64

    def test_chain_links_entries(self, logger: SignalAuditLogger):
        e1 = logger.log_event(make_event(signal_id="S1"))
        e2 = logger.log_event(make_event(signal_id="S2"))
        assert e2.prev_hash == e1.content_hash


# ------------------------------------------------------------------
# 可配置性
# ------------------------------------------------------------------
class TestConfigurable:
    def test_memory_mode_default(self):
        logger = SignalAuditLogger()
        assert logger._config.log_dir == ""

    def test_custom_retention(self):
        config = AuditLogConfig(retention_years=7)
        logger = SignalAuditLogger(config)
        assert logger._config.retention_years == 7

    def test_hash_chain_can_be_disabled(self):
        config = AuditLogConfig(enable_hash_chain=False)
        logger = SignalAuditLogger(config)
        entry = logger.log_event(make_event())
        assert entry.prev_hash == ""
        assert logger.verify_integrity() is True  # No chain = always valid
