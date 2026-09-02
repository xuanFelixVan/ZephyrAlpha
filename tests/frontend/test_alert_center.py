# [BLUEPRINT] MOD-FE-003 | docs/03_modules/_domain_frontend/alert_center/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-FE-003 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.frontend.test_alert_center
# [TESTS] src/zephyr/frontend/dashboard/components/alert_center.py
"""MOD-FE-003 单元测试：alert_center 告警中心面板。

蓝图验收（B14-04625/CAND-FE-002，A9 §8.3.2）：
AL-P1~P4 分级在野列表 + 6 维收敛视图（时间/空间/根因/抑制/升级/静默）+
MTTR/日均/确认率/误报率统计 + render dict 可序列化。
数据源全部内存构造（DI 注入记录序列），不连任何真实告警后端/DB。
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip(
    "zephyr.frontend.dashboard.components.alert_center",
    reason="alert_center not importable",
)

from zephyr.frontend.dashboard.components.alert_center import (  # noqa: E402
    AlertCenterInputError,
    AlertCenterRecord,
    fetch_alert_center,
    render_alert_center,
)

_NOW = datetime(2026, 8, 25, 12, 0, 0, tzinfo=timezone.utc)


def _rec(
    alert_id: str,
    severity: str = "AL-P2",
    source: str = "alert_router",
    status: str = "active",
    hours_ago: float = 1.0,
    resolved_after_sec: float | None = None,
    ack: bool = False,
    root_cause: str = "数据缺失",
    suppressed: bool = False,
    escalated: bool = False,
    false_positive: bool = False,
) -> AlertCenterRecord:
    created = _NOW - timedelta(hours=hours_ago)
    return AlertCenterRecord(
        alert_id=alert_id,
        title=f"告警{alert_id}",
        severity=severity,
        source=source,
        status=status,
        created_at=created,
        acknowledged_at=created + timedelta(minutes=5) if ack else None,
        resolved_at=(created + timedelta(seconds=resolved_after_sec) if resolved_after_sec is not None else None),
        root_cause=root_cause,
        suppressed=suppressed,
        escalated=escalated,
        false_positive=false_positive,
    )


class TestStats:
    def test_empty_records(self) -> None:
        data = fetch_alert_center([], now_utc=_NOW)
        assert data.stats.total == 0
        assert data.stats.active_by_severity == {"AL-P1": 0, "AL-P2": 0, "AL-P3": 0, "AL-P4": 0}
        assert data.stats.mttr_seconds is None
        assert data.stats.ack_rate == pytest.approx(0.0)

    def test_active_by_severity(self) -> None:
        records = [
            _rec("a1", severity="AL-P1"),
            _rec("a2", severity="AL-P1"),
            _rec("a3", severity="AL-P3"),
            _rec("a4", severity="AL-P4", status="resolved", resolved_after_sec=60),
        ]
        data = fetch_alert_center(records, now_utc=_NOW)
        assert data.stats.active_by_severity == {"AL-P1": 2, "AL-P2": 0, "AL-P3": 1, "AL-P4": 0}
        assert data.stats.total == 4

    def test_mttr_known_answer(self) -> None:
        records = [
            _rec("a1", status="resolved", resolved_after_sec=120),
            _rec("a2", status="resolved", resolved_after_sec=240),
            _rec("a3"),  # active 不计入 MTTR
        ]
        data = fetch_alert_center(records, now_utc=_NOW)
        assert data.stats.mttr_seconds == pytest.approx(180.0)

    def test_ack_and_false_positive_rate(self) -> None:
        records = [
            _rec("a1", status="acknowledged", ack=True),
            _rec("a2", status="resolved", resolved_after_sec=60),
            _rec("a3", false_positive=True),
            _rec("a4"),
        ]
        data = fetch_alert_center(records, now_utc=_NOW)
        assert data.stats.ack_rate == pytest.approx(0.5)  # 2/4
        assert data.stats.false_positive_rate == pytest.approx(0.25)  # 1/4

    def test_daily_average(self) -> None:
        records = [_rec(f"a{i}", hours_ago=i * 12.0) for i in range(4)]  # 覆盖 1.5 天
        data = fetch_alert_center(records, now_utc=_NOW)
        assert data.stats.daily_average == pytest.approx(4 / 1.5, rel=1e-6)


class TestConvergenceViews:
    def _records(self) -> list[AlertCenterRecord]:
        return [
            _rec("a1", source="alert_router", root_cause="数据缺失"),
            _rec("a2", source="alert_router", root_cause="数据缺失", suppressed=True),
            _rec("a3", source="alert_manager", root_cause="延迟超限", escalated=True),
            _rec("a4", source="alert_manager", root_cause="延迟超限", status="silenced"),
        ]

    def test_by_space(self) -> None:
        data = fetch_alert_center(self._records(), now_utc=_NOW)
        assert data.views["by_space"] == {"alert_router": 2, "alert_manager": 2}

    def test_by_root_cause(self) -> None:
        data = fetch_alert_center(self._records(), now_utc=_NOW)
        assert data.views["by_root_cause"] == {"数据缺失": 2, "延迟超限": 2}

    def test_by_time_hourly_buckets(self) -> None:
        data = fetch_alert_center(self._records(), now_utc=_NOW)
        assert sum(data.views["by_time"].values()) == 4

    def test_suppressed_escalated_silenced_lists(self) -> None:
        data = fetch_alert_center(self._records(), now_utc=_NOW)
        assert [r.alert_id for r in data.views["suppressed"]] == ["a2"]
        assert [r.alert_id for r in data.views["escalated"]] == ["a3"]
        assert [r.alert_id for r in data.views["silenced"]] == ["a4"]

    def test_active_list_only_active(self) -> None:
        data = fetch_alert_center(self._records(), now_utc=_NOW)
        ids = {r.alert_id for r in data.active_list}
        assert ids == {"a1", "a2", "a3"}  # a4 silenced 不在实时列表


class TestRender:
    def test_render_dict_json_serializable(self) -> None:
        data = fetch_alert_center([_rec("a1")], now_utc=_NOW)
        payload = render_alert_center(data)
        text = json.dumps(payload, ensure_ascii=False)  # 不抛即可序列化
        assert "AL-P1" in text or "alerts" in text

    def test_render_payload_keys(self) -> None:
        data = fetch_alert_center([_rec("a1"), _rec("a2", escalated=True)], now_utc=_NOW)
        payload = render_alert_center(data)
        for key in ("page", "stats", "views", "active_list"):
            assert key in payload


class TestFailClosed:
    def test_invalid_severity(self) -> None:
        with pytest.raises(AlertCenterInputError):
            _rec("a1", severity="P9")

    def test_invalid_status(self) -> None:
        with pytest.raises(AlertCenterInputError):
            _rec("a1", status="limbo")

    def test_resolved_before_created(self) -> None:
        created = _NOW
        with pytest.raises(AlertCenterInputError):
            AlertCenterRecord(
                alert_id="a1",
                title="t",
                severity="AL-P1",
                source="s",
                status="resolved",
                created_at=created,
                acknowledged_at=None,
                resolved_at=created - timedelta(seconds=1),
            )

    def test_records_not_iterable_of_records(self) -> None:
        with pytest.raises(AlertCenterInputError):
            fetch_alert_center([{"not": "a record"}], now_utc=_NOW)  # type: ignore[list-item]
