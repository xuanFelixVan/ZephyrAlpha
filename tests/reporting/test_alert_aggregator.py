# [BLUEPRINT] MOD-RPT-030 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-28 行）
# [MODULE] tests.reporting.test_alert_aggregator
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.reporting.alert_aggregator
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据不触库不触网（通知管理器全 mock）；pytest filterwarnings=error 兼容
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=告警聚合逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-RPT-030_test | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-030 告警聚合器 单元测试（GAP-F-28，合成数据不触库）。

覆盖：三源适配（风控枚举级/数据质量记录/回测完成事件）、严重度映射、
未知级别/状态 fail-closed、同批去重保留最新、页面流排序（严重度+时间）、
派发阈值（info 不派发）、manager 注入位（None 仅页面流）、send 异常容错、
MOD-L08-001 Notification 契约映射、确定性 id 幂等、JSON 可序列化。
"""

from __future__ import annotations

import json
from dataclasses import asdict
from dataclasses import dataclass
from enum import Enum

import pytest

from zephyr.reporting.alert_aggregator import (
    SEVERITY_CRITICAL,
    SEVERITY_ERROR,
    SEVERITY_INFO,
    SEVERITY_WARNING,
    AggregationResult,
    AggregatorConfig,
    UnifiedAlert,
    aggregate_unified_alerts,
    alert_from_backtest,
    alert_from_data_quality,
    alert_from_risk,
    to_notification,
)


class _RiskLevel(Enum):
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"


@dataclass
class _RiskAlert:
    level: _RiskLevel
    source: str
    message: str
    timestamp: str


class _FakeManager:
    def __init__(self, ok=True, boom=False):
        self.sent = []
        self._ok = ok
        self._boom = boom

    def send(self, notification, channels=None):
        if self._boom:
            raise RuntimeError("channel down")
        self.sent.append(notification)
        return self._ok


# ------------------------------------------------------------------
# 三源适配
# ------------------------------------------------------------------


def test_from_risk_enum_levels():
    red = alert_from_risk(_RiskAlert(_RiskLevel.RED, "stop_loss", "触发熔断", "2026-08-21 10:00:00"))
    assert red.severity == SEVERITY_CRITICAL
    assert red.source == "risk"
    assert red.title == "风控告警[stop_loss]"
    yellow = alert_from_risk(_RiskAlert(_RiskLevel.YELLOW, "drawdown", "回撤逼近", "2026-08-21 10:01:00"))
    assert yellow.severity == SEVERITY_WARNING


def test_from_risk_unknown_level_fail_closed():
    bad = _RiskAlert(_RiskLevel.RED, "x", "x", "t")
    bad.level = "purple"  # 未知级别
    with pytest.raises(ValueError):
        alert_from_risk(bad)


def test_from_data_quality_record():
    record = {
        "task_id": "kline_daily_incremental", "error": "连接超时", "level": "ERROR",
        "source": "akshare", "timestamp": "2026-08-21T09:00:00", "extra": {"rows": 0},
    }
    alert = alert_from_data_quality(record)
    assert alert.severity == SEVERITY_ERROR
    assert alert.title == "数据质量[kline_daily_incremental]"
    assert alert.metadata["task_id"] == "kline_daily_incremental"


def test_from_data_quality_unknown_level_fail_closed():
    with pytest.raises(ValueError):
        alert_from_data_quality({"task_id": "t", "level": "FATAL"})


def test_from_backtest_statuses():
    ok = alert_from_backtest("run-1", "success", "完成", "2026-08-21 15:30:00")
    assert ok.severity == SEVERITY_INFO
    bad = alert_from_backtest("run-2", "failed", "异常终止", "2026-08-21 15:31:00")
    assert bad.severity == SEVERITY_ERROR
    deg = alert_from_backtest("run-3", "degraded", "部分数据缺失", "2026-08-21 15:32:00")
    assert deg.severity == SEVERITY_WARNING


def test_from_backtest_unknown_status_fail_closed():
    with pytest.raises(ValueError):
        alert_from_backtest("run-x", "exploded", "", "t")


def test_alert_id_deterministic():
    a1 = alert_from_backtest("run-1", "success", "完成", "2026-08-21 15:30:00")
    a2 = alert_from_backtest("run-1", "success", "完成", "2026-08-21 15:30:00")
    assert a1.alert_id == a2.alert_id  # 幂等重放


# ------------------------------------------------------------------
# 聚合
# ------------------------------------------------------------------


def _batch() -> list[UnifiedAlert]:
    return [
        alert_from_backtest("run-1", "success", "完成", "2026-08-21 15:30:00"),
        alert_from_data_quality({"task_id": "k", "error": "e", "level": "CRITICAL", "timestamp": "2026-08-21 09:00:00"}),
        alert_from_risk(_RiskAlert(_RiskLevel.ORANGE, "veto", "否决", "2026-08-21 10:00:00")),
    ]


def test_aggregate_sorted_by_severity_then_time():
    result = aggregate_unified_alerts(_batch())
    assert [a.severity for a in result.alerts] == [SEVERITY_CRITICAL, SEVERITY_ERROR, SEVERITY_INFO]


def test_aggregate_dedup_keeps_latest():
    dup = [
        alert_from_backtest("run-1", "success", "完成", "2026-08-21 15:30:00"),
        alert_from_backtest("run-1", "success", "完成", "2026-08-21 16:00:00"),  # 同 (source,title) 更新
    ]
    result = aggregate_unified_alerts(dup)
    assert len(result.alerts) == 1
    assert result.alerts[0].occurred_at == "2026-08-21 16:00:00"
    assert result.suppressed_count == 1


def test_dispatch_threshold_info_not_sent():
    manager = _FakeManager()
    result = aggregate_unified_alerts(_batch(), notification_manager=manager)
    # 默认 warning 起派发：critical+error 两条，info(回测成功) 仅页面流
    assert result.dispatched_count == 2
    assert len(manager.sent) == 2
    assert all(n.level.value in ("critical", "error") for n in manager.sent)


def test_dispatch_none_manager_page_only():
    result = aggregate_unified_alerts(_batch())
    assert result.dispatched_count == 0
    assert any("仅页面流" in n for n in result.notes)


def test_dispatch_manager_exception_tolerated():
    manager = _FakeManager(boom=True)
    result = aggregate_unified_alerts(_batch(), notification_manager=manager)
    assert result.dispatched_count == 0
    assert any("派发异常" in n for n in result.notes)
    assert len(result.alerts) == 3  # 页面流不受派发影响


def test_dispatch_partial_failure_note():
    manager = _FakeManager(ok=False)
    result = aggregate_unified_alerts(_batch(), notification_manager=manager)
    assert result.dispatched_count == 0
    assert any("渠道部分失败" in n for n in result.notes)


def test_bad_min_severity_fail_closed():
    with pytest.raises(ValueError):
        aggregate_unified_alerts([], config=AggregatorConfig(min_dispatch_severity="fatal"))


def test_to_notification_contract():
    alert = alert_from_risk(_RiskAlert(_RiskLevel.RED, "stop_loss", "触发熔断", "2026-08-21 10:00:00"))
    n = to_notification(alert)
    assert n.notification_id == alert.alert_id
    assert n.level.value == "critical"
    assert n.source_layer == "risk"


def test_result_json_serializable():
    result: AggregationResult = aggregate_unified_alerts(_batch())
    json.dumps(asdict(result), ensure_ascii=False)
