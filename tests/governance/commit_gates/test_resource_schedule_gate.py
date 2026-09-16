# [A_test] module_id: MOD-RESCHED-GATE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-GATE | docs/03_modules/_cross_layer/resource_schedule_gate/blueprint.md | §
# [MODULE] tests.governance.commit_gates.test_resource_schedule_gate
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/governance/commit_gates/test_resource_schedule_gate.py
# [TTL] task_bound
"""排班冲突闸测试：三检查+漂移+own-scope+红蓝（E0 异常 fail-closed/JSONL 损坏/时钟回拨/cron 坏）。"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import (
    Finding,
    check_e0_trading,
    check_mem_ceiling,
    check_overlap_group,
    check_truth_drift,
    expand_windows,
    load_registry_entities,
    make_resource_schedule_gate,
    run_all_checks,
)

TZ = timezone.utc
WED = datetime(2026, 9, 16, 2, 0, tzinfo=TZ)  # 周三 10:00 北京


def _reg(tmp_path, entities, **header):
    data = {"mem_ceiling_gb": 10.0, "entities": entities}
    data.update(header)
    p = tmp_path / "resource_profile_registry.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


def _e(tid, grp=None, expr="0 10 * * 1", dur=60, mem=2.0, ts=True, status="active"):
    return {"task_id": tid, "status": status, "exclusive_group": grp or [], "window_expr": expr,
            "est_duration_min": dur, "peak_mem_gb": mem, "trading_sensitive": ts}


# ── 检查①：互斥组重叠 ──

def test_overlap_group_block_and_reason_code(tmp_path):
    ents = [_e("a", ["g1"], "0 10 * * 1", 300), _e("b", ["g1"], "0 12 * * 1", 120)]
    f = check_overlap_group(ents, WED)
    assert f and f[0].reason_code == "sched_overlap_group" and f[0].severity == "block"
    assert sorted(f[0].task_ids) == ["a", "b"] and f[0].at


def test_overlap_ignores_non_overlapping_and_different_groups(tmp_path):
    ents = [_e("a", ["g1"], "0 10 * * 1", 60), _e("b", ["g1"], "30 14 * * 1", 60),
            _e("c", ["g2"], "0 10 * * 1", 60)]
    assert check_overlap_group(ents, WED) == []


def test_overlap_skips_retired_and_orphaned(tmp_path):
    ents = [_e("a", ["g1"]), _e("b", ["g1"], status="retired"), _e("c", ["g1"], status="orphaned_source")]
    assert check_overlap_group(ents, WED) == []


def test_overlap_bad_cron_degrades_to_warn(tmp_path):
    ents = [_e("a", ["g1"], "not a cron"), _e("b", ["g1"])]
    f = check_overlap_group(ents, WED)
    assert f and f[0].severity == "warn"


# ── 检查②：内存天花板 ──

def test_mem_ceiling_concurrent_sum_block(tmp_path):
    ents = [_e("a", ["g1"], "0 10 * * 1", 120, mem=6.0, ts=False),
            _e("b", ["g1"], "30 10 * * 1", 120, mem=6.0, ts=False)]
    f = check_mem_ceiling(ents, WED)
    assert f and f[0].reason_code == "sched_mem_ceiling" and f[0].severity == "block"
    assert f[0].detail.startswith("同窗并发内存和 12.0GB")


def test_mem_ceiling_single_declaration_over_line(tmp_path):
    ents = [_e("repair", [], "0 2 * * 0", 600, mem=11.0, ts=False)]
    f = check_mem_ceiling(ents, WED)
    assert f and "超 mem_ceiling_gb=10.0" in f[0].detail


def test_mem_ceiling_undeclared_skipped_then_total_ok(tmp_path):
    ents = [_e("a", ["g1"], "0 10 * * 1", 120, mem=6.0, ts=False),
            {"task_id": "b", "status": "active", "exclusive_group": ["g1"], "window_expr": "30 10 * * 1",
             "est_duration_min": 120, "peak_mem_gb": None, "trading_sensitive": False}]
    assert check_mem_ceiling(ents, WED) == []  # 未申报不参与求和（实测回写后自动纳入）


def test_mem_ceiling_planned_excluded_from_sum_but_single_line_still_checked():
    """裁定 R-D（2026-09-17 v2 方案 §3）：planned=画像在册但**未排产**，不占并发预算。

    31 个纸面实体一起进求和会把真实重活的预算挤掉（"防纸面排班挤掉真实重活"）。
    两条判据都要钉住，缺一即回归：
    ① planned+planned 同窗 6+6=12 > 10 → **不报**（未排产不计和）；
    ② 同两实体改成 active → **必报**（求和臂没被顺手删空，只是换了准入条件）；
    ③ planned 单实体自己申报 11GB → **仍报**（那是画像本身的问题，与排没排产无关）。
    """
    planned_pair = [_e("p1", ["g1"], "0 10 * * 1", 120, mem=6.0, ts=False, status="planned"),
                    _e("p2", ["g1"], "30 10 * * 1", 120, mem=6.0, ts=False, status="planned")]
    assert check_mem_ceiling(planned_pair, WED) == []
    # 同载荷换 active 必须出码——否则上面那条"不报"只是求和被删空的假绿
    active_pair = [dict(e, status="active") for e in planned_pair]
    f = check_mem_ceiling(active_pair, WED)
    assert f and f[0].reason_code == "sched_mem_ceiling" and f[0].detail.startswith("同窗并发内存和 12.0GB")
    # 单实体超线照查（准入=_eligible，不含排产判据）
    solo = _e("paper_big", [], "0 2 * * 0", 600, mem=11.0, ts=False, status="planned")
    s = check_mem_ceiling([solo], WED)
    assert s and s[0].task_ids == ["paper_big"] and "超 mem_ceiling_gb=10.0" in s[0].detail


# ── 检查③：E0 交易时段 ──

def test_e0_blocks_trading_sensitive_weekday_noon():
    ents = [_e("noon_heavy", [], "30 14 * * 1-5", 30, ts=True)]  # 工作日 14:30 北京（盘中保守带）
    f = check_e0_trading(ents, WED)
    assert f and f[0].reason_code == "sched_e0_block" and f[0].severity == "block"


def test_e0_allows_after_close_buffer_and_weekend():
    ents = [_e("eve", [], "0 16 * * 1-5", 30, ts=True),   # 16:00 北京 > 15:30 收盘缓冲
            _e("sat", [], "0 2 * * 6", 30, ts=True)]      # 周六恒休市
    assert check_e0_trading(ents, WED) == []


def test_e0_non_trading_sensitive_ignored():
    ents = [_e("noon_light", [], "30 14 * * 1-5", 30, ts=False)]
    assert check_e0_trading(ents, WED) == []


def test_e0_module_failure_fail_closed(monkeypatch):
    """红蓝：E0 函数异常 → fail-closed 阻断（宁停不裸奔）。"""
    import zephyr.gov_enforcement.commit_gates.resource_schedule_gate as g

    def _boom():
        raise RuntimeError("E0 calendar channel down")

    monkeypatch.setattr(g, "_load_e0_module", _boom)
    f = check_e0_trading([_e("a", [], "30 2 * * 1-5", 30, ts=True)], WED)
    assert f and f[0].severity == "block" and "fail-closed" in f[0].detail


def test_e0_bad_cron_fail_closed():
    f = check_e0_trading([_e("a", [], "bad cron", 30, ts=True)], WED)
    assert f and f[0].severity == "block" and "fail-closed" in f[0].detail


# ── 检查④：真源漂移 ──

def test_truth_drift_detects_window_change(tmp_path):
    """真源漂移：注册表 cron 与 ps1 真源重抽不一致 → warn。"""
    ents = [{"task_id": "sch_factory_lane_c", "status": "active", "window_expr": "0 23 * * 6",
             "window_type": "cron", "trading_sensitive": False}]
    f = check_truth_drift(ents)
    drifts = [x for x in f if x.reason_code == "sched_truth_drift" and x.task_ids == ["sch_factory_lane_c"]]
    assert drifts and drifts[0].severity == "warn"


def test_truth_drift_skips_manual_entities():
    ents = [{"task_id": "manual_factory_grid_executor", "status": "planned", "window_expr": None,
             "window_type": "manual"}]
    drifts = [x for x in check_truth_drift(ents) if x.task_ids == ["manual_factory_grid_executor"]]
    assert drifts == []


# ── expand_windows ──

def test_expand_windows_multi_cron_and_horizon():
    wins = expand_windows("5 10 * * *|5 11 * * *", 10, WED, horizon_days=7)
    assert len(wins) == 14  # 7 天 × 2 触发点
    assert all((e - s).total_seconds() == 600 for (s, e) in wins)


def test_expand_windows_six_field_seconds_stripped():
    """6 段 cron（auction）秒段剥离降级。"""
    wins = expand_windows("*/10 15-25 9 * * 0-4", 10, WED, horizon_days=7)
    assert wins  # 周一~周五 09:15-09:25
    s, e = wins[0]
    assert s.hour == 9 and s.minute == 15 and (e - s).total_seconds() == 600


def test_expand_windows_resident_or_no_expr_empty():
    assert expand_windows(None, 60, WED) == []
    assert expand_windows("*/5 * * * *", 0, WED) == []  # 常驻 est=0 不参与重叠数学


# ── 全量+gate 装配 ──

def test_run_all_checks_and_gate_block(tmp_path):
    p = _reg(tmp_path, [_e("a", ["g1"], "0 10 * * 1", 300, mem=6.0),
                        _e("b", ["g1"], "0 12 * * 1", 120, mem=6.0)])
    finds = run_all_checks(p, WED)
    assert any(x.reason_code == "sched_overlap_group" for x in finds)
    gate = make_resource_schedule_gate()
    ok, msg = gate.check(None, [str(p)])
    assert ok is False and "RESOURCE-SCHEDULE" in msg and "sched_overlap_group" in msg


def test_gate_passes_clean_registry_and_non_trigger_files(tmp_path):
    p = _reg(tmp_path, [_e("a", ["g1"], "0 10 * * 1", 60, mem=2.0, ts=False),
                        _e("b", ["g2"], "0 12 * * 1", 60, mem=2.0, ts=False)])
    gate = make_resource_schedule_gate()
    ok, msg = gate.check(None, [str(p)])
    assert ok is True
    ok2, _ = gate.check(None, ["src/zephyr/foo.py"])  # 未命中注册表 → 不触发
    assert ok2 is True


def test_gate_corrupt_registry_fail_closed(tmp_path):
    """红蓝：注册表 YAML 损坏 → fail-closed 阻断。"""
    p = tmp_path / "resource_profile_registry.yaml"
    p.write_text("entities: [ {broken::::", encoding="utf-8")
    gate = make_resource_schedule_gate()
    ok, msg = gate.check(None, [str(p)])
    assert ok is False and "解析异常" in msg


def test_production_registry_clean(tmp_path):
    """生产注册表（真实真源）三检查全绿+漂移绿——防止本批施工自身带病入库。"""
    from pathlib import Path as P

    reg = P(__file__).resolve().parents[3] / "config" / "resource_profile_registry.yaml"
    if not reg.exists():
        pytest.skip("生产注册表未生成")
    finds = run_all_checks(reg, WED)
    blocks = [x for x in finds if x.severity == "block"]
    assert blocks == [], [b.render() for b in blocks]
