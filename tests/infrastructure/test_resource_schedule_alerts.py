# [A_test] module_id: MOD-RESCHED-ALERT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-ALERT | docs/03_modules/_cross_layer/resource_schedule_alerts/blueprint.md | §
# [MODULE] tests.infrastructure.test_resource_schedule_alerts
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/infrastructure/test_resource_schedule_alerts.py
# [TTL] task_bound
"""告警桥测试：发布映射/静默去重/解除联动/fail-safe（板目录注入 tmp_path，禁写生产 .runtime）。"""
from __future__ import annotations

import json
from pathlib import Path

from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import Finding
from zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts import (
    ResourceScheduleAlerts,
    publish_findings,
)


def _board(tmp_path):
    return tmp_path / "ops_board"


def _read(tmp_path):
    f = _board(tmp_path) / "notifications.jsonl"
    if not f.exists():
        return []
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]


def test_publish_block_critical_and_key_stable(tmp_path):
    b = _board(tmp_path)
    bridge = ResourceScheduleAlerts(board_dir=b)
    f = Finding("sched_overlap_group", "block", ["task_b", "task_a"], "互斥组 g1 时间窗交叠", at="2026-09-16T10:00:00+00:00")
    r = bridge.publish_findings([f])
    assert r["active_keys"] == ["sched_overlap_group:task_a,task_b"]  # 排序稳定 key
    entries = _read(tmp_path)
    assert len(entries) == 1
    assert entries[0]["severity"] == "critical"
    assert entries[0]["module_id"] == "resource-schedule-gate"


def test_publish_warn_warning_severity(tmp_path):
    bridge = ResourceScheduleAlerts(board_dir=_board(tmp_path))
    f = Finding("sched_truth_drift", "warn", ["sch_x"], "真源漂移 window_expr")
    bridge.publish_findings([f])
    assert _read(tmp_path)[0]["severity"] == "warning"


def test_silence_window_refresh_not_duplicate(tmp_path):
    """同 key 静默窗口内只刷新 count（照抄 OpsAlertFeed 语义）。"""
    bridge = ResourceScheduleAlerts(board_dir=_board(tmp_path))
    f = Finding("sched_mem_ceiling", "block", ["a"], "超线")
    bridge.publish_findings([f])
    bridge.publish_findings([Finding("sched_mem_ceiling", "block", ["a"], "超线")])
    entries = _read(tmp_path)
    assert len(entries) == 1 and entries[0]["count"] == 2


def test_resolve_cleared_conflicts(tmp_path):
    """冲突消失 → resolve（promotion 页灰显解除）。"""
    bridge = ResourceScheduleAlerts(board_dir=_board(tmp_path))
    bridge.publish_findings([Finding("sched_overlap_group", "block", ["a", "b"], "撞车")])
    assert _read(tmp_path)[0]["resolved_at"] is None
    r = bridge.publish_findings([])  # 本轮无 findings → 解除
    assert any(o["op"] == "resolved" for o in r["ops"])
    assert _read(tmp_path)[0]["resolved_at"] is not None


def test_publish_failure_fail_safe(tmp_path, monkeypatch):
    """红蓝：发布失败降级记日志不抛（告警线不得成为故障源）。"""
    bridge = ResourceScheduleAlerts(board_dir=_board(tmp_path))

    class BoomFeed:
        module_id = "resource-schedule-gate"

        def publish(self, **kw):
            raise OSError("board CAS conflict")

        def list_active(self):
            return []

        def resolve(self, key):
            return 0

    monkeypatch.setattr(bridge, "_feed", lambda: BoomFeed())
    r = bridge.publish_findings([Finding("sched_e0_block", "block", ["x"], "盘中重活")])
    assert r["ops"][0]["op"] == "failed"


def test_module_level_convenience(tmp_path):
    r = publish_findings([Finding("sched_e0_block", "block", ["e"], "盘中重活")], board_dir=_board(tmp_path))
    assert r["active_keys"] == ["sched_e0_block:e"]
