# [A_test] module_id: MOD-RESCHED-GATE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-GATE | docs/03_modules/_cross_layer/resource_schedule_gate/blueprint.md | §
# [MODULE] tests.governance.commit_gates.test_resource_schedule_gate
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/governance/commit_gates/test_resource_schedule_gate.py
# [TTL] task_bound
"""排班冲突闸测试：四检查+漂移+own-scope+红蓝（E0 异常 fail-closed/JSONL 损坏/时钟回拨/cron 坏）。"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import (
    REASON_POOL_CONCURRENCY,
    Finding,
    check_e0_trading,
    check_mem_ceiling,
    check_overlap_group,
    check_pool_concurrency,
    check_truth_drift,
    expand_windows,
    load_registry_entities,
    make_resource_schedule_gate,
    run_all_checks,
    run_pool_concurrency_audit,
)

TZ = timezone.utc
WED = datetime(2026, 9, 16, 2, 0, tzinfo=TZ)  # 周三 10:00 北京


def _reg(tmp_path, entities, **header):
    data = {"mem_ceiling_gb": 10.0, "entities": entities}
    data.update(header)
    p = tmp_path / "resource_profile_registry.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


def _e(tid, grp=None, expr="0 10 * * 1", dur=60, mem=2.0, ts=True, status="active", pool=None, wtype="cron"):
    return {"task_id": tid, "status": status, "exclusive_group": grp or [], "window_expr": expr,
            "window_type": wtype, "est_duration_min": dur, "peak_mem_gb": mem, "trading_sensitive": ts,
            "pool": pool}


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



# ── 检查④：同池并发账（v2 C-8 同刻冲突结构盲区，2026-09-17 P2-a）──

def _c4_exam(**over):
    """生产实样 fixture（不依赖真注册表）：sch_c4_exam=heavy 池/[mine_vs_exam] 组/周六 14:00/2.0GB÷8h。"""
    return dict(_e("sch_c4_exam", ["mine_vs_exam"], "0 14 * * 6", 480, mem=2.0, ts=True, pool="heavy"), **over)


def _f06_grid(**over):
    """生产实样 fixture：sch_f06_grid=heavy 池/**无互斥组**/同 cron 0 14 * * 6/0.5GB÷24h。"""
    return dict(_e("sch_f06_grid", [], "0 14 * * 6", 1440, mem=0.5, ts=True, pool="heavy"), **over)


def test_pool_concurrency_same_instant_cross_group_caught():
    """C-8 实证场景：C4Exam×F06Grid 同秒开工且无共享互斥组 → 第四查必抓，既有两查全瞎。

    "必抓"的反面就是本查存在的理由——同一对实体喂给检查①（只查同组）与检查②
    （2.0+0.5=2.5GB 远低于天花板）都零 finding，于是 2.5GB 并发全仓无一处记账。
    """
    ents = [_c4_exam(), _f06_grid()]
    assert check_overlap_group(ents, WED) == []  # 结构盲区面 1：不同互斥组，检查①永不可见
    assert check_mem_ceiling(ents, WED) == []  # 结构盲区面 2：和未超天花板，检查②也不报
    f = check_pool_concurrency(ents, WED)
    assert len(f) == 1  # 28 天地平线内周六触发 4 次 → 同对去重后仍只 1 条（不重复刷账）
    x = f[0]
    assert x.reason_code == REASON_POOL_CONCURRENCY == "sched_pool_concurrency"
    assert x.severity == "block"
    assert x.task_ids == ["sch_c4_exam", "sch_f06_grid"]
    assert x.at and x.at.startswith("2026-09-19T14:00")  # 周六 14:00 北京（cron 0=周日，与生成器归一同口径）
    assert x.extra["pool"] == "heavy" and x.extra["kind"] == "same_instant_cross_group"
    assert x.extra["concurrent_mem_gb"] == 2.5  # 第一次被算出来的那个和
    assert "错峰或声明互斥" in x.detail  # 出口指路（P3 重排班两条合法出路）


def test_pool_concurrency_different_pool_same_instant_not_caught():
    """不同 pool 同刻不抓：两条泳道各有各的 worker，不构成同池并发账。"""
    assert check_pool_concurrency([_c4_exam(), _f06_grid(pool="default")], WED) == []


def test_pool_concurrency_planned_pileup_does_not_crowd_budget():
    """裁定 R-D 同判适用第四查：planned 纸面实体不占并发预算（未排产不计和）。"""
    paper = [_c4_exam(), _f06_grid(status="planned")]
    assert check_pool_concurrency(paper, WED) == []
    # 反证假绿：同载荷换 active 必出码（否则上面的"不报"只是判据被删空）
    assert len(check_pool_concurrency([dict(e, status="active") for e in paper], WED)) == 1
    # planned 单实体申报超线仍照查（画像本身的问题，与排没排产无关）——账在检查②那儿
    over = check_mem_ceiling([_f06_grid(status="planned", peak_mem_gb=11.0)], WED)
    assert over and over[0].reason_code == "sched_mem_ceiling"


def test_pool_concurrency_sum_over_ceiling_across_groups():
    """判据②：同池并发内存和超 mem_ceiling（跨互斥组一律计入）；拆到两池即不报。"""
    pair = [_e("h1", [], "0 10 * * 1", 120, mem=6.0, ts=False, pool="heavy"),
            _e("h2", [], "30 10 * * 1", 120, mem=6.0, ts=False, pool="heavy")]
    f = check_pool_concurrency(pair, WED)
    assert len(f) == 1 and f[0].extra["kind"] == "pool_mem_sum"
    assert f[0].task_ids == ["h1", "h2"]
    assert f[0].detail.startswith("池 heavy 同窗并发内存和 12.0GB > mem_ceiling_gb=10.0")
    assert "跨互斥组同样计入" in f[0].detail
    # 同样的两笔账拆到两条泳道 → 同池再无 ≥2 并发 → 不报（证明本查是"分池归口"账）
    assert check_pool_concurrency([pair[0], dict(pair[1], pool="default")], WED) == []


def test_pool_concurrency_three_way_accumulation():
    """累加越界抓：三笔错峰（10:00/10:20/10:40 各 180min）叠到 12.0GB → 一条集合级 finding。"""
    ents = [_e("a", [], "0 10 * * 1", 180, mem=4.0, ts=False, pool="heavy"),
            _e("b", [], "20 10 * * 1", 180, mem=4.0, ts=False, pool="heavy"),
            _e("c", [], "40 10 * * 1", 180, mem=4.0, ts=False, pool="heavy")]
    f = check_pool_concurrency(ents, WED)
    assert len(f) == 1 and f[0].task_ids == ["a", "b", "c"]
    assert "12.0GB" in f[0].detail and f[0].at
    assert f[0].extra["concurrent_mem_gb"] == 12.0
    assert f[0].extra["pool"] == "heavy"


def test_pool_concurrency_shared_group_left_to_overlap_check():
    """同组同刻=检查①的互斥账（并已 block），第四查不重复记账（避免同刻冲突双开）。"""
    pair = [_c4_exam(), _f06_grid(exclusive_group=["mine_vs_exam"])]
    assert check_pool_concurrency(pair, WED) == []
    assert check_overlap_group(pair, WED)  # 账在检查①那儿


def test_pool_concurrency_never_invents_a_synthetic_pool():
    """pool 未声明的实体整条不判：臆造"合成池"=给执行器不存在的泳道记账（池缺席归 sched_pool_undeclared）。"""
    pile = [dict(_c4_exam(), pool=None), dict(_f06_grid(), pool=None)]
    assert check_pool_concurrency(pile, WED) == []
    # 连"必然越线"的账也不记在合成池上（sched_mem_ceiling 才是它们的出口）
    big = pile + [_e("big1", [], "0 12 * * 1", 60, mem=9.0, ts=False, pool=None),
                  _e("big2", [], "30 12 * * 1", 60, mem=9.0, ts=False, pool=None)]
    assert check_pool_concurrency(big, WED) == []


def test_pool_concurrency_resident_event_entities_are_baseline_not_window_sum():
    """常驻/event 实体（无窗档）不进求和，只显影为该池 resident_baseline_gb（与检查②同口径）。"""
    resident = [_e("sch_ollama_serve", [], None, 0, mem=8.0, ts=False, pool="heavy", wtype="event"),
                _e("sch_tick_subscriber", [], None, 5, mem=6.0, ts=False, pool="realtime", wtype="event")]
    assert check_pool_concurrency(resident, WED) == []  # 8+6=14 也绝不进窗档和（无窗可求交）
    ents = [_e("h1", [], "0 10 * * 1", 120, mem=6.0, ts=False, pool="heavy"),
            _e("h2", [], "30 10 * * 1", 120, mem=6.0, ts=False, pool="heavy"),
            _e("sch_ollama_serve", [], None, 0, mem=3.0, ts=False, pool="heavy", wtype="event")]
    f = check_pool_concurrency(ents, WED)
    assert len(f) == 1 and f[0].extra["resident_baseline_gb"] == 3.0
    assert "12.0GB" in f[0].detail  # 基线 3.0 未被掺进窗档和（否则 15.0GB）


def test_pool_concurrency_focus_pileup_own_scope_discipline():
    """own-scope（宪法 §3）：focus=本次变更实体，未命中的存量冲突不连坐；pileup=False=归因退化面。"""
    pair = [_c4_exam(), _f06_grid()]
    assert len(check_pool_concurrency(pair, WED)) == 1  # focus=None=全量（审计/视图场景）
    assert len(check_pool_concurrency(pair, WED, focus={"sch_f06_grid"})) == 1  # 变更方在账里→判
    assert check_pool_concurrency(pair, WED, focus={"someone_else"}) == []  # 与本提交无关→不连坐
    staggered = [_e("h1", [], "0 10 * * 1", 120, mem=6.0, ts=False, pool="heavy"),
                 _e("h2", [], "30 10 * * 1", 120, mem=6.0, ts=False, pool="heavy")]
    # 归因失败（非 git 通道）时：跨组同刻不判（存量债），预算类越线照判（保守面不窄）
    assert check_pool_concurrency(pair, WED, pileup=False) == []
    assert len(check_pool_concurrency(staggered, WED, pileup=False)) == 1
    assert check_pool_concurrency(staggered, WED, focus={"nope"}, pileup=False) == []


def test_pool_concurrency_audit_entry_point_and_run_all_checks_exclusion(tmp_path):
    """全仓清单真源=run_pool_concurrency_audit（P3 输入）；run_all_checks 有意不并（告警链不淹）。"""
    p = _reg(tmp_path, [_c4_exam(), _f06_grid()])
    audit = run_pool_concurrency_audit(p, WED)
    assert [x.reason_code for x in audit] == [REASON_POOL_CONCURRENCY]
    assert audit[0].extra["pool"] == "heavy" and audit[0].severity == "block"
    reasons = {x.reason_code for x in run_all_checks(p, WED)}
    assert REASON_POOL_CONCURRENCY not in reasons


def test_gate_exports_fourth_check_symbols():
    """闸导出面：第四查+审计入口+新码必须齐（告警桥标题同步由 test_resource_schedule_alerts 钉）。"""
    from zephyr.gov_enforcement.commit_gates import resource_schedule_gate as g

    for sym in ("check_pool_concurrency", "run_pool_concurrency_audit", "REASON_POOL_CONCURRENCY"):
        assert sym in g.__all__, sym
        assert hasattr(g, sym), sym


def test_production_registry_pool_concurrency_audit_is_usable_input():
    """真注册表只读体检（只读，不改排班数据）：全仓清单结构自洽，供 P3 重排班消化。

    有意**不**断言"零 finding"——同刻跨组存量债正是 P3 的清零对象（方案 §4 P3 验收）。
    本钉保的是清单可用：池∈注册表词表、task_ids 全在表内、≥2 实体、和>0、有冲突时刻。
    """
    from zephyr.gov_enforcement.commit_gates.resource_schedule_gate import _registry_relpath

    reg = Path(__file__).resolve().parents[3] / "config" / "resource_profile_registry.yaml"
    if not reg.exists():
        pytest.skip("生产注册表未生成")
    # 归因口径自检：闸把仓内绝对路径折成 git 相对正斜杠路径（``git show :<rel>`` 吃这个）
    assert _registry_relpath(reg) == "config/resource_profile_registry.yaml"
    entities, header = load_registry_entities(reg)
    lanes = set((header.get("pool_vocabulary") or {}).get("lanes") or [])
    known = {str(e.get("task_id")) for e in entities}
    findings = run_pool_concurrency_audit(reg, WED)
    for f in findings:
        assert f.reason_code == REASON_POOL_CONCURRENCY and f.severity == "block"
        assert f.extra.get("pool") in lanes, f"finding 挂了词表外的池：{f.extra.get('pool')}"
        assert set(f.task_ids) <= known and len(f.task_ids) >= 2  # 单实体超线归 sched_mem_ceiling
        assert f.at and f.extra.get("concurrent_mem_gb", 0) > 0

# ── 检查⑤：真源漂移 ──

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
    # 注：本钉**不含**第四查 sched_pool_concurrency 的同刻跨组存量债（run_all_checks 有意
    # 不并，见其 docstring）——那批冲突是 P3 重排班的清零对象，全仓清单走
    # run_pool_concurrency_audit（其结构自洽由 test_production_registry_pool_concurrency_* 钉）。


# ── 第四查闸侧接线：staged 归因（own-scope，宪法 §3 禁连坐）──────────────────

class _FakeGateway:
    """最小 gateway 替身：只回答 ``git show :<rel>``（staged）与 ``git show HEAD:<rel>``。

    真提交链路里注册表路径在仓内，_registry_relpath 自然折出 rel；测试用 tmp_path（仓外）
    写盘，故把 rel 钉成仓内字面值，其余行为与真 gateway 一致（rc=1 表达"读不到"）。
    """

    def __init__(self, staged, head):
        self._staged = staged
        self._head = head
        self.calls: list[list[str]] = []

    def run_git(self, args):
        from types import SimpleNamespace

        self.calls.append(list(args))
        out = None
        if len(args) >= 3 and args[0] == "git" and args[1] == "show":
            spec = args[2]
            if spec.startswith("HEAD:"):
                out = self._head
            elif spec.startswith(":"):
                out = self._staged
        if out is None:
            return SimpleNamespace(returncode=1, stdout="")
        return SimpleNamespace(returncode=0, stdout=out)


def _pin_repo_relpath(monkeypatch):
    """把归因用的 rel 折算钉成仓内路径（tmp_path 在仓外，真实 git show 必然读空）。"""
    import zephyr.gov_enforcement.commit_gates.resource_schedule_gate as g

    monkeypatch.setattr(g, "_registry_relpath", lambda path: "config/resource_profile_registry.yaml")


def _dump(entities):
    return yaml.safe_dump({"mem_ceiling_gb": 10.0, "entities": entities}, allow_unicode=True)


def test_gate_blocks_pileup_when_changed_entity_is_in_it(tmp_path, monkeypatch):
    """本次变更实体正是同刻跨组堆积的一员 → 闸阻断（登记时把 C-8 盲区堵上）。"""
    _pin_repo_relpath(monkeypatch)
    ents = [_c4_exam(), _f06_grid()]
    p = _reg(tmp_path, ents)
    # HEAD 里 f06_grid 还排在周日 03:00——本次 staged 把它挪到周六 14:00，撞上 c4_exam
    gw = _FakeGateway(staged=_dump(ents), head=_dump([ents[0], dict(ents[1], window_expr="0 3 * * 0")]))
    ok, msg = make_resource_schedule_gate().check(gw, [str(p)])
    assert ok is False and REASON_POOL_CONCURRENCY in msg and "sch_f06_grid" in msg


def test_gate_does_not_blame_committer_for_untouched_pileup(tmp_path, monkeypatch):
    """own-scope：只改了无关实体的账 → 存量同刻冲突不连坐本提交人（闸放行）。"""
    _pin_repo_relpath(monkeypatch)
    ents = [_c4_exam(), _f06_grid(), _e("sch_benign", [], "0 5 * * 2", 30, mem=1.0, ts=False, pool="default")]
    p = _reg(tmp_path, ents)
    gw = _FakeGateway(staged=_dump(ents), head=_dump(ents[:2] + [dict(ents[2], pool="heavy")]))
    ok, msg = make_resource_schedule_gate().check(gw, [str(p)])
    assert ok is True and msg == ""
    assert gw.calls, "归因通道未被调用=本钉成了假绿"


def test_gate_unattributable_channel_skips_pileup_but_keeps_ceiling(tmp_path):
    """归因不可能（非 git 通道，gateway=None）：跨组同刻不判（存量债），同池内存和超线照判。"""
    gate = make_resource_schedule_gate()
    ok, msg = gate.check(None, [str(_reg(tmp_path, [_c4_exam(), _f06_grid()]))])
    assert ok is True and REASON_POOL_CONCURRENCY not in msg
    breached = [_e("h1", [], "0 10 * * 1", 120, mem=6.0, ts=False, pool="heavy"),
                _e("h2", ["mine_vs_exam"], "30 10 * * 1", 120, mem=6.0, ts=False, pool="heavy")]
    ok2, msg2 = gate.check(None, [str(_reg(tmp_path, breached))])
    assert ok2 is False and REASON_POOL_CONCURRENCY in msg2 and "12.0GB" in msg2
