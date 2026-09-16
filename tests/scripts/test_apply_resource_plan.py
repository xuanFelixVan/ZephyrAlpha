# [A_test] module_id=MOD-RESCHED-APPLY | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-APPLY | docs/_working/resource_schedule/resource_schedule_v2_construction_plan.md | §4-P2-b
# [MODULE] tests.scripts.test_apply_resource_plan
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/scripts/test_apply_resource_plan.py
# [TTL] task_bound
"""apply_resource_plan 测试（P2-b 受闸写回工具，tmp_path 副本，禁写生产真源）。

四臂：① 文本级 patch 字节保真（纯函数，零 IO）；② 非法方案拒绝（幽灵 task_id/坏 cron/
不可动实体/重复键/未知互斥组/缺理由/字段混填）→ 退出码 2 且零写；③ 闸挡超限（构造
heavy 池同刻内存爆表）→ 非零且副本真源逐字节零变化；④ dry-run 幂等 hash + apply→
rollback 逐字节还原 + 三角对账 summary。

生产文件零写纪律：②③④ 全在 `build_sandbox` 造出的 tmp 仓副本上跑（root≠REPO_ROOT 时
run_plan 自动强制 skip_schtasks，探针不外呼）。
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
    "apply_resource_plan_test", REPO_ROOT / "scripts" / "governance" / "apply_resource_plan.py"
)
arp = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("apply_resource_plan_test", arp)
_SPEC.loader.exec_module(arp)

NOW = datetime(2026, 9, 16, 4, 0, tzinfo=timezone.utc)  # 固定基准：闸窗档展开确定

SCHEDULE_SAMPLE = """data_slots:
  # L3.5 慢新闻层：串行限流，独立队列不堵快新闻
  news_slow:
    cron: "*/30 * * * *"    # 每30分钟触发；max_instances=1 下跑完才再跑
    executor: default
    description: "慢新闻层"

  # 盘后日K线层：16:30 周一至周五
  daily_kline:
    cron: 30 16 * * 0-4
    executor: heavy
    description: "日K线"

  monthly_static:
    cron: "00 9 1 * *"
    executor: default
    description: "月度静态层"
"""

PS1_SAMPLE = """# 注册 F06 网格搜索任务（真源必须纯 ASCII）
$ErrorActionPreference = "Stop"
$Name = "ZephyrAlpha_F06Grid"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At 14:00
$Action = New-ScheduledTaskAction -Execute "python"

$Name2 = "ZephyrAlpha_C4Exam"
$trigger2 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At "14:00"
"""

PS1_TIMES_SAMPLE = """$Name = "ZephyrAlpha_IntradayFundFlow"
$trigger = New-ScheduledTaskTrigger -Times @('05:05', '05:35')
"""

REGISTRY_SAMPLE = """schema_version: 1.0.0
total_entities: 2
entities:
- task_id: sch_c4_exam
  # 人审字段：生产者=人（§2.1），再生合并保全
  exclusive_group:
  - mine_vs_exam
  window_expr: 0 14 * * 6
  status: active
- task_id: sch_f06_grid
  exclusive_group: []
  window_expr: 0 14 * * 6
  status: active
"""


# ---------------------------------------------------------------------------
# ① 文本级 patch：未命中字节零改动
# ---------------------------------------------------------------------------
def test_patch_slot_cron_preserves_comment_quote_and_padding():
    lines = SCHEDULE_SAMPLE.split("\n")
    idx = arp.find_slot_cron_line(lines, "news_slow")
    assert lines[idx].strip().startswith("cron:")
    new_text, line_no, old_line, new_line = arp.patch_slot_cron(SCHEDULE_SAMPLE, "news_slow",
                                                                "15,45 * * * *")
    assert line_no == idx + 1
    # 引号风格 + 行内注释 + 缩进全保真
    assert new_line == '    cron: "15,45 * * * *"    # 每30分钟触发；max_instances=1 下跑完才再跑'
    assert old_line != new_line
    diffed = [(a, b) for a, b in zip(SCHEDULE_SAMPLE.split("\n"), new_text.split("\n"), strict=True) if a != b]
    assert len(diffed) == 1  # 整份文件只动这一行


def test_patch_slot_cron_keeps_unquoted_style_and_per_band_padding():
    _t, _l, _o, padded = arp.patch_slot_cron(SCHEDULE_SAMPLE, "monthly_static", "0 10 1 * *")
    assert padded == '    cron: "00 10 1 * *"'  # 分钟段沿用真源补零风格，小时段无补零可继承
    _t, _l, _o, plain = arp.patch_slot_cron(SCHEDULE_SAMPLE, "daily_kline", "45 16 * * 0-4")
    assert plain == "    cron: 45 16 * * 0-4"  # 无引号风格不被强加引号
    mixed = SCHEDULE_SAMPLE.replace("  monthly_static:\n    cron: \"00 9 1 * *\"",
                                    "  weekend_backfill:\n    cron: \"00 2 * * 1\"")
    _t, _l, _o, only_minute = arp.patch_slot_cron(mixed, "weekend_backfill", "30 2 * * 0")
    assert only_minute == '    cron: "30 2 * * 0"'  # 未改的小时段不得被补零成 "02"


def test_slot_aps_cron_shifts_dow_both_directions():
    # 注册表口径 0=周日 → 写回 APScheduler 口径 0=周一（周六 6 → 5）
    spec = arp.resolve_time_spec({"new_window_cron": "0 14 * * 6"}, "0 9 * * *")
    assert arp._slot_aps_cron(spec) == "0 14 * * 5"
    assert arp.standard_dow_to_aps("6") == "5"
    assert arp.standard_dow_to_aps("*") == "*"
    assert arp.standard_dow_to_aps("0") == "6"  # 周日 → APS 周六
    assert arp.dow_to_ps_names("6") == ["Saturday"]
    assert arp.cron_ok("0 99 * * *") is False and arp.cron_ok("0 14 * * 6") is True


def test_patch_ps1_trigger_only_owns_its_line_and_stays_ascii():
    spec = arp.resolve_time_spec({"new_window_cron": "0 16 * * 6"}, "0 14 * * 6")
    new_text, line_no, old_line, new_line = arp.patch_ps1_trigger(PS1_SAMPLE, "ZephyrAlpha_F06Grid", spec)
    assert line_no == 4 and new_line.isascii()
    assert new_line == "$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At 16:00"
    assert old_line not in new_text
    # 同文件另一任务的行原样不动（归属判定不吃别人的账）
    assert '$trigger2 = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At "14:00"' in new_text.split("\n")


def test_patch_ps1_trigger_daily_weekly_switch_and_quoting():
    daily = arp.resolve_time_spec({"new_window_cron": "30 8 * * *"}, "0 14 * * 6")
    _t, _l, _o, line = arp.patch_ps1_trigger(PS1_SAMPLE, "ZephyrAlpha_F06Grid", daily)
    assert "-Daily -At 8:30" in line and "-Weekly" not in line  # 每日型不带 DaysOfWeek
    weekly = arp.resolve_time_spec({"new_window_cron": "0 14 * * 1,3"}, "0 14 * * 6")
    _t, _l, _o, line2 = arp.patch_ps1_trigger(PS1_SAMPLE, "ZephyrAlpha_C4Exam", weekly)
    assert '-DaysOfWeek Monday,Wednesday -At "14:00"' in line2  # 引号风格随原行


def test_patch_ps1_trigger_times_list():
    spec = arp.resolve_time_spec({"new_times": ["05:10", "11:40"]}, "5 10 * * *")
    assert spec is not None and spec.mode == "times"
    _t, _l, _o, line = arp.patch_ps1_trigger(PS1_TIMES_SAMPLE, "ZephyrAlpha_IntradayFundFlow", spec)
    assert line.strip() == "-Times @('05:10', '11:40')" or line.strip().startswith(
        "$trigger = New-ScheduledTaskTrigger -Times @('05:10', '11:40')")


def test_patch_registry_group_preserves_surrounding_bytes():
    new_text, line_no, old_line, new_line = arp.patch_registry_group(REGISTRY_SAMPLE, "sch_c4_exam",
                                                                    ["mine_vs_exam", "gpu_default"])
    assert line_no == 6 and new_line == "  exclusive_group:\n  - mine_vs_exam\n  - gpu_default"
    # 替换单位=整块（键行 + 其列表项），不是键行单独改写
    assert old_line == "  exclusive_group:\n  - mine_vs_exam"
    diff = arp.unified_diff("config/resource_profile_registry.yaml", REGISTRY_SAMPLE, new_text)
    changed = [ln for ln in diff.splitlines()
               if ln.startswith(("+", "-")) and not ln.startswith(("+++", "---"))]
    assert all(("exclusive_group" in ln[1:] or ln[1:].strip().startswith("- ")) for ln in changed), changed
    assert sum(1 for ln in changed if ln.startswith("+")) == 1  # 只新增一行
    assert "window_expr: 0 14 * * 6" in new_text
    assert "total_entities: 2" in new_text  # 块外字节原样
    # 清空为 [] 时不留下悬空列表项
    emptied, _l, _o, e_line = arp.patch_registry_group(new_text, "sch_c4_exam", [])
    assert e_line == "  exclusive_group: []" and "  - mine_vs_exam" not in emptied


# ---------------------------------------------------------------------------
# ② 非法方案拒绝（全部退出码 2，零生产写）
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def real_gen():
    return arp.load_sibling(arp.GENERATOR_REL, "p2b_gen_fixture", REPO_ROOT)


@pytest.fixture(scope="module")
def located(real_gen):
    out = arp.locate_all(real_gen, REPO_ROOT)
    assert out, "生成器各源定位为空=真源链断了"
    return out


@pytest.fixture
def repo(tmp_path, located):
    """tmp 仓副本（生成器/闸/真源/词表源齐）——所有 run_plan 用例的家，生产零写。"""
    root = tmp_path / "repo"
    arp.build_sandbox(REPO_ROOT, root, {}, frozenset(getattr(arp.locate_all, "truth_rels", frozenset())))
    assert (root / arp.GENERATOR_REL).exists() and (root / arp.SCHEDULE_REL).exists()
    return root


def write_plan(root: Path, items: dict, name: str = "resource_plan.yaml") -> Path:
    """方案落在仓副本**之外**（否则 snapshot 会把它算成"被改动"）。"""
    plans = root.parent / "plans"
    plans.mkdir(exist_ok=True)
    path = plans / name
    path.write_text(yaml.safe_dump({"items": items}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def snapshot(root: Path) -> dict[str, str]:
    """副本仓的「除 .runtime/解释器字节码缓存外」逐文件指纹表——零写/回滚断言的判据。"""
    out = {}
    for r in sorted(root.rglob("*")):
        if not r.is_file():
            continue
        rel = r.relative_to(root)
        if ".runtime" in rel.parts or "__pycache__" in rel.parts or rel.suffix == ".pyc":
            continue  # 沙箱/存档/字节码副产：不属于被受管的真源字节
        out[rel.as_posix()] = r.read_bytes().hex()
    return out


def run(root: Path, plan: Path, apply: bool = False):
    return arp.run_plan(root=root, plan_path=plan, session="p2b-test", apply=apply, now=NOW,
                        sandbox_dir=root / ".runtime" / "tmp" / "sb")


@pytest.mark.parametrize("bad", [
    {"sch_no_such_task": {"new_window_cron": "0 3 * * *", "rationale_zh": "幽灵 task_id"}},
    {"data_slot_news_slow": {"new_window_cron": "0 99 * * *", "rationale_zh": "坏 cron（小时越界）"}},
    {"data_slot_news_slow": {"new_window_cron": "0 9 * *", "rationale_zh": "坏 cron（段数非法）"}},
    {"data_slot_news_slow": {"new_window_cron": "abc def ghi jkl mno", "rationale_zh": "坏 cron（非数字）"}},
    {"manual_run_sft_train": {"new_window_cron": "0 3 * * *", "rationale_zh": "不可动实体（§3.C 种子）"}},
    {"sch_data_scheduler": {"new_window_cron": "0 3 * * *", "rationale_zh": "常驻型无时刻字面量"}},
    {"data_slot_news_slow": {"new_exclusive_group": ["not_a_group"], "rationale_zh": "未知互斥组"}},
    {"data_slot_news_slow": {"new_window_cron": "15,45 * * * *"}},
    {"data_slot_news_slow": {"new_window_cron": "15,45 * * * *", "new_hour": 3, "rationale_zh": "字段混填"}},
    {"data_slot_news_slow": {"new_times": ["05:10"], "rationale_zh": "槽位无 -Times 形态"}},
    {"data_slot_news_slow": {"new_minute": 7, "rationale_zh": "现值分钟段非单值"}},
    {"data_slot_monthly_static": {"new_hour": 24, "rationale_zh": "小时越界"}},
    {"data_slot_news_slow": {"new_window_cron": "15,45 * * * *", "bogus_field": 1, "rationale_zh": "拼错字段"}},
])
def test_plan_refused_with_exit_2_and_zero_write(repo, bad):
    plan = write_plan(repo, bad, name="bad.yaml")
    before = snapshot(repo)
    rep, rc = run(repo, plan)
    assert rc == arp.EXIT_REFUSED, rep.get("refusals")
    assert rep["verdict"] == "refused" and rep["block_reasons"]
    assert [s["stage"] for s in rep["refusals"]] == ["build_patches"]
    assert rep["patches"] == [] and rep.get("files_touched", []) == []
    assert snapshot(repo) == before  # 拒绝=一个字节都不动


def test_missing_plan_file_is_exit_2_not_traceback(repo):
    rep, rc = run(repo, repo.parent / "nope.yaml")
    assert rc == arp.EXIT_REFUSED and rep["verdict"] == "refused"
    assert "方案文件不存在" in rep["block_reasons"][0]


def test_duplicate_yaml_key_refused(repo):
    path = repo.parent / "dup.yaml"
    path.write_text("items:\n  data_slot_news_slow:\n    new_window_cron: \"15,45 * * * *\"\n"
                    "    rationale_zh: a\n  data_slot_news_slow:\n    new_window_cron: \"7 3 * * *\"\n"
                    "    rationale_zh: b\n", encoding="utf-8")
    rep, rc = run(repo, path)
    assert rc == arp.EXIT_REFUSED and "重复键" in rep["refusals"][0]["reason"]


def test_drill_entities_located_but_not_window_patchable(real_gen, located):
    """第 4 真源源（P4-α/L-5）：实体须被定位（否则方案误报幽灵），但窗档不可写回。"""
    if getattr(real_gen, "parse_drill_entities", None) is None:  # 兄弟车道未合流时本臂不适用
        pytest.skip("生成器尚无 parse_drill_entities（P4-α 未合流）")
    drills = [v for v in located.values() if v.kind == arp.KIND_DRILL]
    assert drills, "生成器有 drill 源而定位为 0=映射漏源"
    assert all(not d.patchable_window and "drill_schedule.yaml" in d.why_not for d in drills)


# ---------------------------------------------------------------------------
# ③ 闸挡超限：构造 heavy 池同刻内存爆表 → 非零 + 副本真源零变化
# ---------------------------------------------------------------------------
def test_gate_blocks_mem_blowup(repo, located):
    """把 heavy 池全部可改窗班次并到周六 03:00 → 同刻并发和远超 mem_ceiling_gb。

    数学不复制：求和走 import 进来的 check_mem_ceiling/check_pool_concurrency，本用例只
    断言"工具绝不放行闸判 block 的方案"。
    """
    heavy = sorted(e.task_id for e in located.values() if e.pool == "heavy" and e.patchable_window)
    assert len(heavy) >= 4, heavy
    items = {t: {"new_window_cron": "0 3 * * 6", "rationale_zh": "构造同刻爆表（测试）"} for t in heavy}
    plan = write_plan(repo, items, name="blowup.yaml")
    before = snapshot(repo)
    rep, rc = run(repo, plan)
    assert rc == arp.EXIT_REFUSED, json.dumps(rep.get("gate"), ensure_ascii=False)[:600]
    assert rep["verdict"] == "blocked"
    assert rep["gate"]["new_blocks"], "闸未记新账=求和臂没接上"
    assert any(("内存" in b) or ("mem" in b) for b in rep["gate"]["new_blocks"]), rep["gate"]["new_blocks"][:3]
    assert rep["gate"]["materialization_problems"] == []
    assert "零生产写" in rep["apply_note"]
    assert snapshot(repo) == before  # 被闸挡下 → 副本真源也一字节未动


# ---------------------------------------------------------------------------
# ④ dry-run 幂等 + 三角对账 + apply/回滚逐字节
# ---------------------------------------------------------------------------
PASS_ITEMS = {
    "sch_f06_grid": {"new_window_cron": "0 16 * * 6", "rationale_zh": "错峰消解 heavy 周六 14:00 同刻"},
    "data_slot_daily_backfill": {"new_exclusive_group": ["gpu_default"], "rationale_zh": "人审字段改组"},
}


def test_dry_run_pass_is_idempotent_and_reports_triangle(repo):
    plan = write_plan(repo, PASS_ITEMS, name="pass.yaml")
    rep1, rc1 = run(repo, plan)
    assert rc1 == arp.EXIT_OK, json.dumps(rep1.get("gate"), ensure_ascii=False)[:800]
    assert rep1["verdict"] == "pass" and rep1["mode"] == "dry-run"
    rep2, rc2 = run(repo, plan)
    assert (rc2, rep2["report_sha256"]) == (arp.EXIT_OK, rep1["report_sha256"]), "同方案两次 dry-run 指纹必同"
    # 真源命中 + patch 行数 + 保真
    kinds = {i["task_id"]: (i["located"] or {}).get("kind") for i in rep1["items"]}
    assert kinds == {"sch_f06_grid": arp.KIND_PS1, "data_slot_daily_backfill": arp.KIND_SLOT}
    assert {p["kind"] for p in rep1["patches"]} == {"ps1_trigger", "registry_group"}
    assert all(st["added_lines"] == st["removed_lines"] == 1 for st in rep1["diff_stats"].values())
    assert rep1["gate"]["new_blocks"] == [] and rep1["gate"]["c8_available"] is True
    assert rep1["files_touched"] == ["config/resource_profile_registry.yaml",
                                     "scripts/register_f06_grid_task.ps1"]
    # 三角对账：表↔真源重抽↔schtasks（tmp 仓无 OS 任务角→探针降级健康码，不静默）
    tri = rep1["triangle"]
    assert tri["summary"]["changed_or_queried_tasks"] == 2
    assert tri["summary"]["truth_drifted"] == 0 and tri["summary"]["truth_aligned"] == 2
    assert tri["whole_table_drift"] == []
    assert any("schtasks_probe_skipped" in p for p in tri["schtasks_probe_problems"])
    # 沙箱再生人口与生产同口径（第 4 源不得被误判 orphaned）
    assert rep1["sandbox_registry"]["entity_delta_vs_baseline"] == 0


def test_pin_eval_now_floors_to_shanghai_day_start():
    """真实坑（P2-b 生产 dry-run run1/run2 差异 23 处，全源于此）：闸以 now 起算 28 天地平线，
    秒级差即让末端某刻进出展开集 → block 集合抖、幂等指纹失效。取整到上海日首后同日确定。
    """
    from datetime import timedelta
    a = datetime(2026, 9, 16, 4, 0, tzinfo=timezone.utc)      # 上海 9/16 12:00
    b = a + timedelta(hours=11, minutes=59)                   # 上海 9/16 23:59
    c = datetime(2026, 9, 16, 16, 0, tzinfo=timezone.utc)     # 上海 9/17 00:00
    day_start = datetime(2026, 9, 15, 16, 0, tzinfo=timezone.utc)
    assert arp.pin_eval_now(a) == day_start == arp.pin_eval_now(b)
    assert arp.pin_eval_now(c) == day_start + timedelta(days=1)
    assert arp.pin_eval_now(arp.pin_eval_now(c)) == arp.pin_eval_now(c)  # 幂等
    assert arp.pin_eval_now(datetime(2026, 9, 16, 4, 0)) == day_start    # naive 也可喂


def test_same_day_different_instant_reports_identical_fingerprint(repo):
    plan = write_plan(repo, PASS_ITEMS, name="pass2.yaml")
    outs = []
    for tag, inst in (("a", datetime(2026, 9, 16, 4, 0, tzinfo=timezone.utc)),
                      ("b", datetime(2026, 9, 16, 15, 59, 30, tzinfo=timezone.utc))):
        rep, rc = arp.run_plan(root=repo, plan_path=plan, session="p2b-test", apply=False, now=inst,
                              sandbox_dir=repo / ".runtime" / "tmp" / f"sb{tag}")
        assert rc == arp.EXIT_OK, json.dumps(rep.get("gate"), ensure_ascii=False)[:600]
        outs.append(rep)
    assert outs[0]["eval_now_utc"] == "2026-09-15T16:00:00Z" == outs[1]["eval_now_utc"]
    assert outs[0]["report_sha256"] == outs[1]["report_sha256"], "同日内换瞬间=同指纹"


def test_apply_then_rollback_is_byte_identical(repo):
    plan = write_plan(repo, PASS_ITEMS, name="apply.yaml")
    before = snapshot(repo)
    rep, rc = run(repo, plan, apply=True)
    assert rc == arp.EXIT_OK, json.dumps({k: rep.get(k) for k in
                                          ("verdict", "block_reasons", "post_apply", "env_error")},
                                         ensure_ascii=False)[:900]
    assert rep["verdict"] == "pass" and rep["mode"] == "apply"
    assert rep["post_apply"]["new_blocks"] == [] and rep["post_apply"]["materialization_problems"] == []
    changed = {k for k, v in snapshot(repo).items() if before.get(k) != v}
    assert {"scripts/register_f06_grid_task.ps1", "config/resource_profile_registry.yaml"} <= changed
    assert not any(k.endswith("schedule.yaml") for k in changed), changed  # 本方案未改槽位
    reg = yaml.safe_load((repo / arp.REGISTRY_REL).read_text(encoding="utf-8"))
    by = {str(e["task_id"]): e for e in reg["entities"]}
    assert by["sch_f06_grid"]["window_expr"] == "0 16 * * 6"                    # 再生跟上真源
    assert by["data_slot_daily_backfill"]["exclusive_group"] == ["gpu_default"]  # 合并保全生效
    arch = Path(rep["archive_dir"])
    assert (arch / "manifest.json").exists() and (arch / "plan.yaml").exists()
    assert (arch / "report.json").exists()
    assert (arch / "orig" / "config" / "resource_profile_registry.yaml").exists()
    res = arp.restore_archive(repo, arch)
    assert res["restored"]
    assert snapshot(repo) == before, "回滚后必须逐字节回到 apply 之前"


def test_cli_rollback_and_refusal_exit_codes(repo, capsys):
    assert arp.main(["--root", str(repo), "--rollback", str(repo / "no_such_archive")]) == arp.EXIT_ENV
    assert arp.main(["--root", str(repo), "--plan", str(repo.parent / "nope.yaml"),
                     "--skip-schtasks"]) == arp.EXIT_REFUSED
    assert "ROLLBACK-FAIL" in capsys.readouterr().out


def test_archive_records_absent_view_and_rollback_removes_it(tmp_path):
    """视图件事前不存在时：存档记 absent，回滚把 apply 新建的件移走（否则留半吊子态）。"""
    root = tmp_path / "mini"
    (root / "src" / "a").mkdir(parents=True)
    (root / "src" / "a" / "truth.yaml").write_text("k: 1\n", encoding="utf-8", newline="\n")
    ad = root / ".runtime" / "ar"
    arp.archive_originals(ad, root, ["src/a/truth.yaml", arp.VIEW_REL], {"plan_id": "p"})
    man = json.loads((ad / "manifest.json").read_text(encoding="utf-8"))
    by_rel = {f["rel_path"]: f for f in man["files"]}
    assert by_rel[arp.VIEW_REL].get("absent") is True
    assert by_rel["src/a/truth.yaml"]["sha256"]
    view = root / arp.VIEW_REL
    view.parent.mkdir(parents=True, exist_ok=True)
    view.write_text("window.__X = 1;\n", encoding="utf-8", newline="\n")
    res = arp.restore_archive(root, ad)
    assert any(r.get("removed_as_created_by_apply") for r in res["restored"])
    assert not view.exists() and (ad / "removed_by_rollback" / arp.VIEW_REL).exists()
    # 存档指纹被改动 → 拒绝据此回滚（底档自身完整性）
    (ad / "orig" / "src" / "a" / "truth.yaml").write_text("k: 2\n", encoding="utf-8", newline="\n")
    with pytest.raises(arp.EnvError, match="指纹不符"):
        arp.restore_archive(root, ad)


def test_stable_hash_ignores_representative_instant_and_paths():
    a = {"gate": {"f": [{"rendered": "[c/block] x: 说明（at=2026-09-17T14:00:00+08:00）"}]},
         "ts_utc": "1", "sandbox": "C:/w/sb", "archive_dir": "C:/w/ar", "report_path": "C:/w/r.json"}
    b = json.loads(json.dumps(a))
    b["gate"]["f"][0]["rendered"] = "[c/block] x: 说明（at=2026-09-20T09:30:00+08:00）"
    b["ts_utc"] = "2"
    b["sandbox"] = "D:/other/sb"
    assert arp.stable_hash(a) == arp.stable_hash(b)
    c = json.loads(json.dumps(a))
    c["gate"]["f"][0]["rendered"] = "[c/block] y: 别的实体（at=2026-09-17T14:00:00+08:00）"
    assert arp.stable_hash(a) != arp.stable_hash(c)  # 实质变化必须变
