# [BLUEPRINT] MOD-DATSEC-002 | docs/03_modules/_domain_data_security/data_access_auditor/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-DATSEC-002 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.data_security.test_data_access_auditor
# [TESTS] src/zephyr/data_security/data_access_auditor.py
"""MOD-DATSEC-002 单元测试：data_access_auditor 数据访问审计器。

蓝图验收（B13-04294/CAND-DATSEC-002，A3数据架构）：
AccessEvent 统一采集（CH/SQLite/Parquet）+ 查询模式基线画像（常用表/时段/量级）
+ 异常访问三维规则（非常用表/大批量导出/非常时段）+ 敏感表注册追踪 +
事件写 gov_audit 审计回调。审计/告警全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.data_security.data_access_auditor",
    reason="data_access_auditor not importable",
)

from zephyr.data_security.data_access_auditor import (  # noqa: E402
    AccessAction,
    AccessAnomaly,
    AccessEvent,
    AnomalyKind,
    DataAccessAuditError,
    DataAccessAuditor,
    SourceType,
)

_T0 = datetime.datetime(2026, 8, 25, 10, 0, 0)


def _auditor(
    audits: list | None = None,
    alerts: list | None = None,
    **kw,
) -> DataAccessAuditor:
    return DataAccessAuditor(
        clock=lambda: _T0,
        audit_sink=(lambda e: audits.append(e)) if audits is not None else None,
        alert_sink=(lambda a: alerts.append(a)) if alerts is not None else None,
        **kw,
    )


def _event(
    event_id: str = "evt-1",
    subject: str = "analyst_a",
    action: AccessAction = AccessAction.QUERY,
    source: SourceType = SourceType.CLICKHOUSE,
    table_name: str = "kline_daily",
    row_count: int = 100,
    occurred_at: datetime.datetime = _T0,
) -> AccessEvent:
    return AccessEvent(
        event_id=event_id,
        subject=subject,
        action=action,
        source=source,
        table_name=table_name,
        row_count=row_count,
        occurred_at=occurred_at,
    )


def _seed_baseline(auditor: DataAccessAuditor, subject: str = "analyst_a") -> None:
    """播种 4 条常规事件：kline_daily / 10 时 / 行均 105（基线样本≥3）。"""
    for i, rows in enumerate((100, 100, 100, 120)):
        auditor.record(_event(event_id=f"seed-{i}", subject=subject, row_count=rows))


# ──────────────────────────────────────────────────────────────────────────────
# 构造 / 敏感表注册（Fail-Closed）
# ──────────────────────────────────────────────────────────────────────────────


class TestInitAndSensitive:
    def test_invalid_bulk_multiplier_raises(self) -> None:
        with pytest.raises(DataAccessAuditError):
            _auditor(bulk_multiplier=0)
        with pytest.raises(DataAccessAuditError):
            _auditor(bulk_multiplier=-1.0)

    def test_init_sensitive_tables(self) -> None:
        auditor = _auditor(sensitive_tables={"positions": "high", "accounts": "critical"})
        assert auditor.is_sensitive("positions")
        assert not auditor.is_sensitive("kline_daily")
        assert list(auditor.sensitive_tables()) == ["accounts", "positions"]  # 确定性排序

    def test_register_sensitive_idempotent(self) -> None:
        auditor = _auditor()
        auditor.register_sensitive_table("positions")
        auditor.register_sensitive_table("positions", "critical")  # 幂等覆盖不抛
        assert auditor.sensitive_tables() == {"positions": "critical"}

    def test_register_empty_table_or_level_raises(self) -> None:
        auditor = _auditor()
        with pytest.raises(DataAccessAuditError):
            auditor.register_sensitive_table("")
        with pytest.raises(DataAccessAuditError):
            auditor.register_sensitive_table("positions", "")


# ──────────────────────────────────────────────────────────────────────────────
# 采集（校验 + 审计回调）
# ──────────────────────────────────────────────────────────────────────────────


class TestRecord:
    def test_record_ok_no_baseline_no_anomaly(self) -> None:
        auditor = _auditor()
        assert auditor.record(_event()) == ()

    def test_record_writes_audit(self) -> None:
        audits: list[AccessEvent] = []
        auditor = _auditor(audits)
        evt = _event()
        auditor.record(evt)
        assert audits == [evt]

    def test_audit_sink_failure_not_blocking(self) -> None:
        def _bad_sink(_e: AccessEvent) -> None:
            raise RuntimeError("audit down")

        auditor = DataAccessAuditor(clock=lambda: _T0, audit_sink=_bad_sink)
        assert auditor.record(_event()) == ()

    def test_duplicate_event_id_raises(self) -> None:
        auditor = _auditor()
        auditor.record(_event())
        with pytest.raises(DataAccessAuditError):
            auditor.record(_event())

    def test_empty_subject_raises(self) -> None:
        with pytest.raises(DataAccessAuditError):
            _auditor().record(_event(subject=""))

    def test_negative_row_count_raises(self) -> None:
        with pytest.raises(DataAccessAuditError):
            _auditor().record(_event(row_count=-1))

    def test_invalid_action_raises(self) -> None:
        with pytest.raises(DataAccessAuditError):
            _auditor().record(_event(action="query"))  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# 三维异常检测
# ──────────────────────────────────────────────────────────────────────────────


class TestDetect:
    def test_unusual_table_detected(self) -> None:
        auditor = _auditor()
        _seed_baseline(auditor)
        kinds = auditor.record(_event(event_id="x1", table_name="order_blotter"))
        assert kinds == (AnomalyKind.UNUSUAL_TABLE,)

    def test_bulk_export_detected(self) -> None:
        auditor = _auditor()
        _seed_baseline(auditor)  # 行均 105，阈值 10×105=1050
        kinds = auditor.record(
            _event(event_id="x2", action=AccessAction.EXPORT, row_count=5000)
        )
        assert kinds == (AnomalyKind.BULK_EXPORT,)

    def test_off_hours_detected(self) -> None:
        auditor = _auditor()
        _seed_baseline(auditor)
        night = datetime.datetime(2026, 8, 25, 3, 0, 0)
        kinds = auditor.record(_event(event_id="x3", occurred_at=night))
        assert kinds == (AnomalyKind.OFF_HOURS,)

    def test_multi_dimension_fixed_order(self) -> None:
        auditor = _auditor()
        _seed_baseline(auditor)
        night = datetime.datetime(2026, 8, 25, 3, 0, 0)
        kinds = auditor.record(
            _event(
                event_id="x4",
                action=AccessAction.EXPORT,
                table_name="order_blotter",
                row_count=9999,
                occurred_at=night,
            )
        )
        assert kinds == (
            AnomalyKind.UNUSUAL_TABLE,
            AnomalyKind.BULK_EXPORT,
            AnomalyKind.OFF_HOURS,
        )

    def test_normal_event_no_anomaly(self) -> None:
        auditor = _auditor()
        _seed_baseline(auditor)
        assert auditor.record(_event(event_id="x5")) == ()

    def test_alert_fired_with_payload(self) -> None:
        alerts: list[AccessAnomaly] = []
        auditor = _auditor(alerts=alerts)
        _seed_baseline(auditor)
        auditor.record(_event(event_id="x6", table_name="order_blotter"))
        assert len(alerts) == 1
        assert alerts[0].subject == "analyst_a"
        assert alerts[0].event_id == "x6"
        assert alerts[0].kinds == (AnomalyKind.UNUSUAL_TABLE,)
        assert alerts[0].raised_at == _T0

    def test_alert_sink_failure_not_blocking(self) -> None:
        def _bad_alert(_a: AccessAnomaly) -> None:
            raise RuntimeError("alert down")

        auditor = DataAccessAuditor(clock=lambda: _T0, alert_sink=_bad_alert)
        _seed_baseline(auditor)
        kinds = auditor.record(_event(event_id="x7", table_name="order_blotter"))
        assert kinds == (AnomalyKind.UNUSUAL_TABLE,)

    def test_detect_replay_without_recording(self) -> None:
        auditor = _auditor()
        _seed_baseline(auditor)
        candidate = _event(event_id="ghost", table_name="order_blotter")
        assert auditor.detect(candidate) == (AnomalyKind.UNUSUAL_TABLE,)
        assert auditor.events_of("analyst_a")[-1].event_id == "seed-3"  # 未落库

    def test_detect_invalid_input_raises(self) -> None:
        auditor = _auditor()
        with pytest.raises(DataAccessAuditError):
            auditor.detect("not-an-event")  # type: ignore[arg-type]


# ──────────────────────────────────────────────────────────────────────────────
# 基线画像 / 查询 / 敏感追踪
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_build_baseline(self) -> None:
        auditor = _auditor()
        _seed_baseline(auditor)
        profile = auditor.build_baseline("analyst_a")
        assert profile.sample_size == 4
        assert profile.common_tables == ("kline_daily",)
        assert profile.common_hours == (10,)
        assert profile.avg_rows == pytest.approx(105.0)
        assert profile.max_rows == 120

    def test_build_baseline_unknown_subject_raises(self) -> None:
        with pytest.raises(DataAccessAuditError):
            _auditor().build_baseline("ghost")

    def test_events_of_deterministic_order(self) -> None:
        auditor = _auditor()
        later = datetime.datetime(2026, 8, 25, 11, 0, 0)
        auditor.record(_event(event_id="e2", occurred_at=later))
        auditor.record(_event(event_id="e1"))
        auditor.record(_event(event_id="e0"))  # 同刻按 event_id 排序
        assert [e.event_id for e in auditor.events_of("analyst_a")] == ["e0", "e1", "e2"]

    def test_sensitive_events_filtered(self) -> None:
        auditor = _auditor(sensitive_tables={"positions": "high"})
        auditor.record(_event(event_id="s1", table_name="positions"))
        auditor.record(_event(event_id="s2", table_name="kline_daily"))
        auditor.record(
            _event(event_id="s3", subject="risk_b", table_name="positions")
        )
        assert [e.event_id for e in auditor.sensitive_events()] == ["s1", "s3"]
        assert [e.event_id for e in auditor.sensitive_events(subject="risk_b")] == ["s3"]
        assert auditor.sensitive_events(table_name="kline_daily") == []
