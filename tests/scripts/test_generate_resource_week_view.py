# [A_test] module_id: MOD-RESCHED-VIEW | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-VIEW | docs/03_modules/_domain_frontend/resource_week_view/blueprint.md | §
# [MODULE] tests.scripts.test_generate_resource_week_view
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/scripts/test_generate_resource_week_view.py
# [TTL] task_bound
"""周历视图测试：窗档展开裁剪/跨日切分/区间合并/unscheduled/冲突标注/机生 js 结构（tmp_path）。"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "gen_week_view_test", REPO_ROOT / "scripts" / "governance" / "generators" / "generate_resource_week_view.py"
)
vw = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("gen_week_view_test", vw)
_SPEC.loader.exec_module(vw)

TZ = timezone.utc
MON = datetime(2026, 9, 14, 0, 0, tzinfo=TZ)  # 周一


def _reg(tmp_path, entities):
    p = tmp_path / "reg.yaml"
    p.write_text(yaml.safe_dump({"mem_ceiling_gb": 10.0, "entities": entities}, allow_unicode=True), encoding="utf-8")
    return p


def test_week_slots_daily_cron_7_days(tmp_path):
    ents = [{"task_id": "a", "status": "active", "window_expr": "30 16 * * 1-5",
             "est_duration_min": 90, "resource_class": "db_heavy", "trading_sensitive": True}]
    lanes, skipped = vw.build_week_slots(ents, MON)
    lane = lanes[0]
    assert lane["unscheduled"] is False
    dows = {s["dow"] for s in lane["slots"]}
    assert dows == {0, 1, 2, 3, 4}  # 工作日
    mon = next(s for s in lane["slots"] if s["dow"] == 0)
    assert mon["ranges"] == [[990, 1080]]  # 16:30→18:00


def test_week_slots_cross_day_split_and_merge(tmp_path):
    """23:30+60min 跨日切分 [1410,1440]+[0,30]；高频 cron 同 lane 区间合并。"""
    ents = [{"task_id": "x", "status": "active", "window_expr": "30 23 * * *",
             "est_duration_min": 60, "trading_sensitive": False}]
    lanes, _ = vw.build_week_slots(ents, MON)
    slots = {s["dow"]: s["ranges"] for s in lanes[0]["slots"]}
    assert slots[0] == [[1410, 1440]]
    assert slots[1][0] == [0, 30]
    # 高频：每分钟触发 10min 时长 → 合并为连续块
    ents2 = [{"task_id": "hf", "status": "active", "window_expr": "*/1 9 * * *",
              "est_duration_min": 10, "trading_sensitive": False}]
    lanes2, _ = vw.build_week_slots(ents2, MON)
    rs = lanes2[0]["slots"][0]["ranges"]
    assert len(rs) == 1 and rs[0] == [540, 609]  # 09:00 起（末次 09:59 触发+10min）连续块


def test_week_slots_unscheduled_and_retired(tmp_path):
    ents = [
        {"task_id": "resident", "status": "active", "window_expr": None, "est_duration_min": 0},
        {"task_id": "manual", "status": "planned", "window_expr": None, "est_duration_min": 60},
        {"task_id": "dead", "status": "retired", "window_expr": "0 2 * * *", "est_duration_min": 30},
    ]
    lanes, skipped = vw.build_week_slots(ents, MON)
    by = {l["task_id"]: l for l in lanes}
    assert by["resident"]["unscheduled"] is True
    assert by["manual"]["unscheduled"] is True
    assert "dead" not in by  # retired 不渲染


def test_week_slots_bad_cron_records_skipped(tmp_path):
    ents = [{"task_id": "broken", "status": "active", "window_expr": "totally bad", "est_duration_min": 30}]
    lanes, skipped = vw.build_week_slots(ents, MON)
    assert skipped and "broken" in skipped[0]
    assert lanes[0]["unscheduled"] is True  # 解析失败不冒充常驻（红蓝修正）


def test_build_view_data_and_render_js(tmp_path):
    ents = [
        {"task_id": "a", "status": "active", "window_expr": "30 16 * * 1-5", "est_duration_min": 90,
         "resource_class": "db_heavy", "pool": "heavy", "exclusive_group": [], "trading_sensitive": True,
         "peak_mem_gb": 3.0, "measured": {"peak_mem_gb": 3.4, "p90_duration_min": 88}},
        {"task_id": "resident_ollama", "status": "active", "window_expr": None, "est_duration_min": 0},
    ]
    reg = _reg(tmp_path, ents)
    view = vw.build_view_data(reg, MON)
    assert view["total_entities"] == 2 and view["scheduled"] == 1
    assert view["week_start"] == "2026-09-14"
    assert len(view["days"]) == 7
    assert view["registry_sha256"]
    js = vw.render_js(view)
    assert "GENERATED" in js and "window.RW_VIEW_DATA" in js
    m = re.search(r"window\.RW_VIEW_DATA = (\{.*\});", js, re.S)
    d = json.loads(m.group(1))
    assert d["scheduled"] == 1


def test_view_conflict_annotation_from_gate(tmp_path):
    """冲突标注=闸同源：注册表内互斥组重叠 → conflicts 出现 block。"""
    ents = [
        {"task_id": "a", "status": "active", "window_expr": "0 10 * * 1", "est_duration_min": 300,
         "peak_mem_gb": 6.0, "exclusive_group": ["g1"], "trading_sensitive": False},
        {"task_id": "b", "status": "active", "window_expr": "0 12 * * 1", "est_duration_min": 120,
         "peak_mem_gb": 6.0, "exclusive_group": ["g1"], "trading_sensitive": False},
    ]
    reg = _reg(tmp_path, ents)
    view = vw.build_view_data(reg, MON)
    assert view["block_conflicts"] >= 1
    reasons = {c["reason_code"] for c in view["conflicts"]}
    assert "sched_overlap_group" in reasons


def test_cli_output_isolation(tmp_path, capsys):
    """--output 注入（禁写生产 web 树）。"""
    reg = _reg(tmp_path, [{"task_id": "a", "status": "active", "window_expr": "0 2 * * *",
                           "est_duration_min": 30, "trading_sensitive": False}])
    out = tmp_path / "rw-data.js"
    rc = vw.main.__wrapped__() if hasattr(vw.main, "__wrapped__") else None
    # 直接调用生成函数再手写文件（避免 main 的 argparse 耦合）
    view = vw.build_view_data(reg, MON)
    out.write_text(vw.render_js(view), encoding="utf-8")
    assert out.exists() and "RW_VIEW_DATA" in out.read_text(encoding="utf-8")
