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
from datetime import datetime, timezone
from pathlib import Path

from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import Finding
from zephyr.infrastructure.system_telemetry.alerts.resource_schedule_alerts import (
    _TITLES,
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

def test_pool_concurrency_maps_to_critical_with_title(tmp_path):
    """第四查码（v2 C-8）映射同步：block→critical + 标题非裸码 + key 含池内两实体。"""
    from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import (
        REASON_POOL_CONCURRENCY,
        check_pool_concurrency,
    )

    ents = [{"task_id": "sch_c4_exam", "status": "active", "exclusive_group": ["mine_vs_exam"],
             "window_expr": "0 14 * * 6", "window_type": "cron", "est_duration_min": 480,
             "peak_mem_gb": 2.0, "trading_sensitive": False, "pool": "heavy"},
            {"task_id": "sch_f06_grid", "status": "active", "exclusive_group": [],
             "window_expr": "0 14 * * 6", "window_type": "cron", "est_duration_min": 1440,
             "peak_mem_gb": 0.5, "trading_sensitive": False, "pool": "heavy"}]
    finds = check_pool_concurrency(ents, datetime(2026, 9, 16, 2, 0, tzinfo=timezone.utc))
    assert [f.reason_code for f in finds] == [REASON_POOL_CONCURRENCY]
    bridge = ResourceScheduleAlerts(board_dir=_board(tmp_path))
    r = bridge.publish_findings(finds)
    assert r["active_keys"] == ["sched_pool_concurrency:sch_c4_exam,sch_f06_grid"]
    entries = _read(tmp_path)
    assert len(entries) == 1 and entries[0]["severity"] == "critical"
    assert entries[0]["title"] == _TITLES[REASON_POOL_CONCURRENCY]
    assert "排班冲突" in entries[0]["title"]  # 板上不得是裸理由码
    assert "14:00" in entries[0]["message"]  # 冲突时刻入消息（重排班要的是哪一秒）
    assert entries[0]["labels"]["reason_code"] == REASON_POOL_CONCURRENCY


def test_reason_code_inventory_synced_with_gate():
    """清单同步钉：闸导出的每个 sched_* 理由码都要有桥标题（改码不同步=板上裸码）。"""
    import zephyr.gov_enforcement.commit_gates.resource_schedule_gate as gate_mod

    codes = {v for k, v in vars(gate_mod).items() if k.startswith("REASON_") and str(v).startswith("sched_")}
    assert "sched_pool_concurrency" in codes
    assert codes <= set(_TITLES), sorted(codes - set(_TITLES))
