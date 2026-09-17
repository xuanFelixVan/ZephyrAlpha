# [A_test] module_id: MOD-RESCHED-MORNING | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-MORNING | docs/03_modules/_cross_layer/resource_morning_report/blueprint.md | §
# [MODULE] tests.scripts.test_generate_resource_morning_report
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/scripts/test_generate_resource_morning_report.py
# [TTL] task_bound
"""L-9 晨报生成器测试：五段拼装/时钟注入/路径注入/只读纪律/校准与告警缺席降级。

全部 tmp_path 合成（禁读生产 .runtime 与 config/ 注册表）；冲突段跑真闸
run_pool_concurrency_audit（只读），故注册表夹具必须给足 pool/peak_mem_gb/window_expr。
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "gen_morning_report_test",
    REPO_ROOT / "scripts" / "governance" / "generators" / "generate_resource_morning_report.py",
)
mr = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("gen_morning_report_test", mr)
_SPEC.loader.exec_module(mr)

GB = 1024**3
from zoneinfo import ZoneInfo  # noqa: E402

TZSH = ZoneInfo("Asia/Shanghai")
TUE = datetime(2026, 9, 22, 0, 30, tzinfo=TZSH)  # 周二凌晨（北京语义）


def _entity(tid, **kw):
    e = {"task_id": tid, "status": "active", "resource_class": "cpu_heavy", "pool": "heavy",
         "peak_mem_gb": 1.0, "est_duration_min": 60, "window_expr": "0 10 * * *",
         "exclusive_group": [], "trading_sensitive": False}
    e.update(kw)
    return e


def _write_registry(path: Path, entities, *, ceiling=10.0, total=None, generated_at="2026-09-22T00:00:00Z"):
    data = {
        "generated_at": generated_at,
        "mem_ceiling_gb": ceiling,
        "total_entities": total if total is not None else len(entities),
        "entities": entities,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


@pytest.fixture()
def root(tmp_path):
    """tmp 仓根：注册表 + 样本流 + 台账 + 通知板（全部 tmp，禁碰生产路径）。"""
    r = tmp_path / "root"
    _write_registry(r / "config" / "resource_profile_registry.yaml", [
        _entity("sch_morning_a", window_expr="0 10 * * *", est_duration_min=60, peak_mem_gb=6.0),
        _entity("sch_morning_b", window_expr="0 10 * * *", est_duration_min=60, peak_mem_gb=6.0,
                exclusive_group=["g_other"]),
        _entity("sch_late", window_expr="0 21 * * *", est_duration_min=30, pool="default"),
        _entity("sch_resident", window_expr=None, est_duration_min=0),
        _entity("sch_retired", status="retired"),
    ])
    (r / ".runtime" / "logs" / "resource_samples").mkdir(parents=True, exist_ok=True)
    (r / ".runtime" / "process_incubator").mkdir(parents=True, exist_ok=True)
    (r / ".runtime" / "process_incubator" / "ledger.jsonl").write_text("", encoding="utf-8")
    return r


def _build(root, **kw):
    kw.setdefault("now", TUE)
    return mr.build_report(root=root, **kw)


def test_timeline_sorted_and_retired_excluded(root):
    """时间线按窗起点排序；retired 不入账；常驻/无窗进 quiet。"""
    tl = _build(root)["timeline"]
    starts = [r["start"] for r in tl["fires"]]
    assert starts == sorted(starts)
    assert [r["task_id"] for r in tl["fires"]] == ["sch_morning_a", "sch_morning_b", "sch_late"]
    quiet_ids = {q["task_id"] for q in tl["quiet"]}
    assert "sch_resident" in quiet_ids
    assert "sch_retired" not in quiet_ids | {r["task_id"] for r in tl["fires"]}  # 退役整条剔除


def test_timeline_aggregates_high_frequency_slot(tmp_path):
    """高频槽位逐窗出行=300 行噪音：聚合成一行并带次数。"""
    reg = tmp_path / "hf"
    _write_registry(reg / "config" / "resource_profile_registry.yaml",
                    [_entity("sch_hf", window_expr="*/3 9-10 * * *", est_duration_min=2)])
    tl = _build(reg)["timeline"]
    assert len(tl["fires"]) == 1
    row = tl["fires"][0]
    assert row["fires"] == 40 and tl["total_fires"] == 40  # 9-10 点每小时 20 次（*/3）
    assert _hhmm_of(row["start"]) == "09:00" and _hhmm_of(row["end"]) == "10:59"
    assert "截断" not in mr.render_markdown(_build(reg))  # 未触顶不噪音


def test_timeline_truncation_caveat(root, tmp_path):
    """触到闸 64 步上限的高频行：末窗非本日真末窗，必须脚注可见（不静默少报）。"""
    reg = tmp_path / "cap"
    _write_registry(reg / "config" / "resource_profile_registry.yaml",
                    [_entity("sch_every_minute", window_expr="*/1 9-12 * * *", est_duration_min=1)])
    tl = _build(reg)["timeline"]
    assert tl["fires"][0]["fires"] == mr._EXPAND_STEP_CAP
    assert "截断" in mr.render_markdown(_build(reg))


def _hhmm_of(dt: datetime) -> str:
    return dt.astimezone(TZSH).strftime("%H:%M")


def test_timeline_window_is_today_only(root):
    """地平线=今日：21:00 班次在当天有窗，明日账不混进来。"""
    tl = _build(root)["timeline"]
    assert tl["date"] == "2026-09-22"
    for r in tl["fires"]:
        assert r["start"].astimezone(TZSH).date().isoformat() == "2026-09-22"


def test_conflicts_counted_from_gate(root):
    """同刻冲突=闸第四查同源：同池同秒开工 + 内存和超线 → block 非零。"""
    cf = _build(root)["conflicts"]
    assert cf["block"] >= 1
    assert cf["total"] == cf["block"] + cf["warn"]
    reasons = {i["reason_code"] for i in cf["items"]}
    assert reasons == {"sched_pool_concurrency"}


def test_calibration_absent_is_reported_honestly(root, tmp_path):
    """校准报告缺席 → 段内如实写"未生成"，不臆造 flag 数。"""
    rep = _build(root, calibration_path=tmp_path / "nowhere.yaml")
    md = mr.render_markdown(rep)
    assert rep["calibration"]["present"] is False
    assert "校准报告未生成" in md
    assert "## 3." in md


def test_calibration_report_flows_into_markdown(root, tmp_path):
    """真校准器产出的报告 → 晨报摘要段出现 flag 与方向。"""
    from zephyr.infrastructure.system_telemetry.measure_calibration import MeasureCalibrator

    cal_root = tmp_path / "calroot"
    _write_registry(cal_root / "config" / "resource_profile_registry.yaml",
                    [_entity("sch_under_est", est_duration_min=10, peak_mem_gb=1.0)])
    sdir = cal_root / ".runtime" / "logs" / "resource_samples"
    sdir.mkdir(parents=True)
    row = {"task_id": "sch_under_est", "process_cpu_ratio": 0.5, "exit_code": None,
           "attribution": "pattern", "process_resident_bytes": 2 * GB}
    with open(sdir / "sch_under_est.jsonl", "w", encoding="utf-8") as fh:
        for i in range(5):
            fh.write(json.dumps({**row, "sample_time_seconds": 1000.0 + i,
                                 "process_elapsed_seconds": 1800, "pid": 700 + i}) + "\n")
    cal = MeasureCalibrator(root=cal_root, now_fn=lambda: 1770000000.0)
    out = tmp_path / "calibration_report.yaml"
    cal.write_report(cal.calibrate(), out)
    md = mr.render_markdown(_build(root, calibration_path=out))
    assert "低估" in md and "sch_under_est" in md


def test_alerts_pending_and_resolved(root, tmp_path):
    """告警段：未决条目入表，已解除灰显单独计数（不进未决清单）。"""
    from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import OpsAlertFeed

    board = tmp_path / "board"
    feed = OpsAlertFeed(board_dir=board, module_id="resource-schedule-gate")
    ts = TUE.timestamp()
    feed.publish(key="sched_pool_concurrency:sch_a", severity="critical", title="同刻冲突",
                 message="heavy 池 2 实体同秒开工", now=ts)
    feed.publish(key="sched_view_stale:rw", severity="warning", title="视图过期",
                 message="指纹不一致", now=ts - 60)
    feed.publish(key="resolved-one", severity="warning", title="已解除项", message="x", now=ts - 120)
    feed.resolve("resolved-one", now=ts - 30)
    al = mr.build_alert_summary(board, TUE)
    assert al["total"] == 2 and al["critical"] == 1 and al["warning"] == 1
    assert al["resolved_recent"] == 1
    assert al["items"][0]["severity"] == "critical"  # critical 置顶
    md = mr.render_markdown(_build(root, board_dir=board))
    assert "同刻冲突" in md and "已解除项" not in md


def test_freshage_counts_and_drift(root, tmp_path):
    """再生新鲜度：generated_at 年龄 + total_entities 声明与实盘一致性。"""
    rep = _build(root)
    fr = rep["freshness"]
    assert fr["entity_count_consistent"] is True and fr["total_entities_actual"] == 5
    assert fr["registry_age_hours"] is not None and fr["registry_age_hours"] < 24
    bad = tmp_path / "bad"
    _write_registry(bad / "config" / "resource_profile_registry.yaml", [_entity("x")], total=99)
    fr2 = _build(bad)["freshness"]
    assert fr2["entity_count_consistent"] is False
    assert "不一致" in mr.render_markdown(_build(bad, ))


def test_clock_injection_changes_the_day(root):
    """时钟可注入：换 --now 就换一天，账不写死（生成器主体不吃真时钟）。"""
    monday = datetime(2026, 9, 21, 8, 0, tzinfo=TZSH)
    rep_mon = _build(root, now=monday)
    rep_tue = _build(root)
    assert rep_mon["local_date"] == "2026-09-21" and rep_tue["local_date"] == "2026-09-22"
    assert rep_mon["generated_at"] != rep_tue["generated_at"]
    # 周末窗（仅工作日 21:00）在周日无开工窗
    weekend = _entity("sch_weekday_only", window_expr="0 21 * * 1-5")
    (root / "config" / "resource_profile_registry.yaml").write_text(
        yaml.safe_dump({"entities": [weekend], "total_entities": 1,
                        "generated_at": "2026-09-20T00:00:00Z", "mem_ceiling_gb": 10.0}),
        encoding="utf-8")
    sun = datetime(2026, 9, 20, 8, 0, tzinfo=TZSH)
    tl_sun = _build(root, now=sun)["timeline"]
    assert tl_sun["total_fires"] == 0 and "今日无可展开窗档" in mr.render_markdown(_build(root, now=sun))


def test_corrupt_cron_degrades_visibly(root, tmp_path):
    """坏 cron 实体：进 quiet 带原因，不炸晨报（红蓝修正——不冒充常驻）。"""
    reg = tmp_path / "r2"
    _write_registry(reg / "config" / "resource_profile_registry.yaml",
                    [_entity("sch_broken", window_expr="totally bad cron", est_duration_min=30)])
    tl = _build(reg)["timeline"]
    assert tl["total_fires"] == 0
    assert any("解析失败" in q["reason_zh"] for q in tl["quiet"])


def test_read_only_discipline(root):
    """只读纪律：生成晨报不得改写注册表（写权各有其主）。"""
    reg = root / "config" / "resource_profile_registry.yaml"
    before = reg.read_bytes()
    mr.render_markdown(_build(root))
    assert reg.read_bytes() == before


def test_cli_writes_markdown_to_injected_output(root, tmp_path, capsys):
    """CLI --root/--now/--output 全注入：markdown 五段落盘 + JSON 摘要。"""
    out = tmp_path / "morning" / "latest.md"
    rc = mr.main(["--root", str(root), "--now", "2026-09-22T00:30:00+08:00",
                  "--output", str(out)])
    assert rc == 0
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert summary["ok"] is True and summary["today_fires"] >= 3
    text = out.read_text(encoding="utf-8")
    for anchor in ["## 1. 今日排班时间线", "## 2. 当前同刻冲突", "## 3. 校准 flag 摘要",
                   "## 4. 告警板未决条目", "## 5. 再生新鲜度"]:
        assert anchor in text
    assert "校准报告未生成" in text  # tmp 根下没有校准报告 → 如实降级


def test_cli_naive_now_treated_as_beijing(root, tmp_path, capsys):
    """裸 --now（无偏移）按北京 wall time 解释——与 window_expr 同口径，防 UTC 误读。"""
    rc = mr.main(["--root", str(root), "--now", "2026-09-22T00:30:00", "--output",
                  str(tmp_path / "o.md")])
    assert rc == 0
    assert "2026-09-22" in json.loads(capsys.readouterr().out.strip().splitlines()[-1])["local_date"]
