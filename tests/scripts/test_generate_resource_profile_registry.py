# [A_test] module_id: MOD-RESCHED-PROFILE | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-RESCHED-PROFILE | docs/03_modules/_cross_layer/resource_profile_registry/blueprint.md | §
# [MODULE] tests.scripts.test_generate_resource_profile_registry
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/scripts/test_generate_resource_profile_registry.py
# [TTL] task_bound
"""生成器测试：ps1 解析/槽位抽取/合并保全/漂移检测/孤儿标记（tmp_path，禁写生产路径）。"""
from __future__ import annotations

import importlib.util
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "gen_resched_profile_test", REPO_ROOT / "scripts" / "governance" / "generators" / "generate_resource_profile_registry.py"
)
gen = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault("gen_resched_profile_test", gen)
_SPEC.loader.exec_module(gen)

NOW = datetime(2026, 9, 16, 4, 0, tzinfo=timezone.utc)  # 周三中午北京时间


def test_parse_ps1_entities_covers_all_task_names():
    ents, warns = gen.parse_ps1_entities()
    tids = {e["task_id"] for e in ents}
    # 全部 19 个 ZephyrAlpha_ 任务任务名（来自 13 个 ps1 真源；2026-09-16 采样器
    # scan/writeback 两任务接线 +1 源 +2 实体）
    assert "sch_factory_lane_c" in tids
    assert "sch_c4_exam" in tids
    assert "sch_ollama_serve" in tids
    assert "sch_intraday_fund_flow" in tids
    assert "sch_data_scheduler" in tids
    assert "sch_trading_watchdog" in tids
    assert "sch_resource_sampler_scan" in tids
    assert "sch_resource_sampler_writeback" in tids
    # 2026-09-17 追认：register_f06_grid_task.ps1 落地（4ea29d816f）使 ps1 实体 19→20，
    # 该测试解析真实磁盘 ps1（环境敏感），计数随真源走。
    # 2026-09-17 P0（v2 方案 L-2 再生排产化）：再生/视图发布两任务接线 → 20→22
    # （吃自己狗粮：排产动作本身进表，active 计入闸内存求和）。
    # 2026-09-17 P5：晨报（每日 06:31）+ 周校准（周六 06:17）两任务排上表 → 22→24
    assert "sch_resource_morning_report" in tids
    assert "sch_measure_calibration" in tids
    assert len(ents) == 25  # 2026-09-18 追认：新 register ps1 落地（环境敏感计数随真源走）
    # 杂音捕获杜绝：无变量名误捕实体
    assert not any("task_name" in t or t.endswith("_name") or t == "sch_svc" for t in tids)


def test_parse_ps1_triggers_extracted_from_truth():
    ents, _ = gen.parse_ps1_entities()
    by = {e["task_id"]: e for e in ents}
    # FactoryLaneC：周六 10:00（ps1 真源 Weekly DaysOfWeek Saturday At 10:00）
    assert by["sch_factory_lane_c"]["window_expr"] == "0 10 * * 6"
    assert by["sch_factory_lane_c"]["exclusive_group"] == ["mine_vs_exam"]
    # IntradayFundFlow：5 个每日触发点（'|'-连接）
    expr = by["sch_intraday_fund_flow"]["window_expr"]
    assert expr.count("|") == 4 and expr.startswith("5 10 * * *")
    # PostSettlement：工作日 15:30（多 dow 连接）
    assert by["sch_post_settlement"]["window_expr"] == "30 15 * * 1,2,3,4,5"
    # AtLogOn 常驻 → event + est=0
    assert by["sch_ollama_serve"]["window_type"] == "event"
    assert by["sch_ollama_serve"]["est_duration_min"] == 0
    # TradingWatchdog DISABLED → retired
    assert by["sch_trading_watchdog"]["status"] == "retired"


def test_parse_schedule_slots_21_slots_cron_verbatim():
    ents, warns = gen.parse_schedule_slots()
    assert len(ents) == 22  # 2026-09-18 追认：daily_alt_fx 第 22 槽（4058b7b1e0）
    by = {e["task_id"]: e for e in ents}
    assert by["data_slot_daily_kline"]["window_expr"] == "30 16 * * 1-5"  # APScheduler dow 归一为标准 cron
    assert by["data_slot_daily_kline"]["pool"] == "heavy"
    assert by["data_slot_auction_highfreq"]["pool"] == "realtime"
    assert by["data_slot_nightly_sentiment"]["resource_class"] == "light"  # 规则法不耗 LLM（方案 §5-2 防误报）
    assert by["data_slot_weekend_calibration"]["exclusive_group"] == ["ch_bulk_write"]


def test_manual_entities_seed_and_planned_status():
    ents = gen.manual_entities()
    tids = {e["task_id"] for e in ents}
    assert "manual_factory_grid_executor" in tids
    assert "manual_repair_kline_tz" in tids
    assert "dynamic_local_replay" in tids
    repair = next(e for e in ents if e["task_id"] == "manual_repair_kline_tz")
    assert repair["exclusive_group"] == ["repair_passport", "ch_bulk_write"]
    assert all(e["status"] == "planned" for e in ents)  # 手动实体行为零变更（方案 §8）


def test_merge_preserve_keeps_human_and_measured_fields(tmp_path):
    fresh = [
        {"task_id": "a", "resource_class": "cpu_heavy", "window_expr": "0 2 * * *", "window_type": "cron",
         "schedule_truth_source": "x.ps1", "trading_sensitive": True, "status": "active",
         "peak_mem_gb": 2.0, "est_duration_min": 30, "module_id": None, "measured": None, "samples_uri": "u"},
    ]
    existing = [
        {"task_id": "a", "module_id": "MOD-HUMAN-1", "peak_mem_gb": 4.5, "est_duration_min": 99,
         "status": "active", "notes_zh": "人复核过",
         "measured": {"peak_mem_gb": 5.1, "p90_duration_min": 42, "samples": 7, "last_at": "t"},
         "samples_uri": ".runtime/logs/resource_samples/a.jsonl",
         "window_expr": "旧值将被刷新"},
    ]
    merged, warns = gen.merge_preserve(fresh, existing)
    m = merged[0]
    assert m["module_id"] == "MOD-HUMAN-1"  # 人填保全
    assert m["peak_mem_gb"] == 4.5 and m["est_duration_min"] == 99
    assert m["measured"]["samples"] == 7  # 采样器独占保全
    assert m["window_expr"] == "0 2 * * *"  # 生成器字段刷新（时间值不搬家）


def test_merge_preserve_marks_orphaned_source(tmp_path):
    fresh = [{"task_id": "still_here", "status": "active"}]
    existing = [{"task_id": "ghost", "status": "active", "notes_zh": ""}]
    merged, warns = gen.merge_preserve(fresh, existing)
    ghost = next(e for e in merged if e["task_id"] == "ghost")
    assert ghost["status"] == "orphaned_source"
    assert any("ghost" in w for w in warns)


def test_merge_preserve_keeps_co_start_intent(tmp_path):
    """裁定 R-F：co_start_intent 是人审声明位，再生必须保全（否则豁免账被洗）。"""
    fresh = [{"task_id": "lane_a", "status": "active", "window_expr": "*/10 9 * * 1-5"}]
    existing = [{"task_id": "lane_a", "co_start_intent": True, "notes_zh": "[R-F] 行情时钟共生"}]
    merged, warns = gen.merge_preserve(fresh, existing)
    assert merged[0]["co_start_intent"] is True


def test_merge_preserve_warns_declaration_without_notes(tmp_path):
    """R-F 配套臂：只翻开关不写理由=warn 留痕（防豁免成为无理由静默）。"""
    fresh = [{"task_id": "lane_b", "status": "active"}]
    existing = [{"task_id": "lane_b", "co_start_intent": True, "notes_zh": "  "}]
    merged, warns = gen.merge_preserve(fresh, existing)
    assert any("co_start_declared_without_notes" in w for w in warns)
    ok = [{"task_id": "lane_c", "status": "active", "co_start_intent": True, "notes_zh": "理由在册"}]
    _m2, w2 = gen.merge_preserve([{"task_id": "lane_c", "status": "active"}], ok)
    assert not any("co_start_declared_without_notes" in w for w in w2)


def test_full_registry_build_and_drift_check(tmp_path):
    out = tmp_path / "reg.yaml"
    reg = gen.build_registry(existing_path=tmp_path / "nonexistent.yaml", output_path=out)
    assert reg["total_entities"] >= 50
    assert reg["mem_ceiling_gb"] == 10.0
    assert set(gen.GROUPS) == {"ch_bulk_write", "tick_drain", "mine_vs_exam", "repair_passport", "gpu_default", "llm_local", "machine_blackout"}
    text = gen.registry_text(reg)
    out.write_text(text, encoding="utf-8")
    # 磁盘内容可解析且 --check 无漂移
    d = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert d["total_entities"] == len(d["entities"])
    # 漂移检测（同输出路径，无人工篡改 → 无漂移）
    import subprocess

    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "governance" / "generators" / "generate_resource_profile_registry.py"),
         "--check", "--output", str(out), "--existing", str(out)],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_e0_mapping_layer():
    assert gen.E0_CLASS_TO_RESOURCE["local"] == "light"
    assert gen.E0_CLASS_TO_RESOURCE["local_gpu"] == "cpu_heavy"
    assert gen.E0_CLASS_TO_RESOURCE["mixed"] == "cpu_heavy"
    # trading_sensitive 推导：heavy 类受 E0 管辖
    assert "db_heavy" in gen.TRADING_SENSITIVE_CLASSES
    assert "light" not in gen.TRADING_SENSITIVE_CLASSES


# ---------------------------------------------------------------------------
# ⑤ L-5 第 4 真源源收编臂（drill_schedule.yaml）：归一 / 避让 / 降级 三态
# 纪律：断言只依赖 tmp 夹具（下面三份"真源样例"是 scripts/governance/meta/
# drill_schedule.yaml 排程字段的 1:1 复刻），生产文件增删条目不该红本测试。
# ---------------------------------------------------------------------------
_CRON_SHAPE = re.compile(r"^\d+ \d+ (?:\*|\d+(?:,\d+)*) (?:\*|\d+(?:,\d+)*) \*$")

# 真源三条（frequency/day_of_month/months 三元组，第三种日期法）——只取排程字段
_DRILL_TRUTH_SAMPLES = """
module_id: MOD-PROBE-SAMPLE
drills:
  script_failure_drill:
    type: "脚本故障演练"
    frequency: monthly
    day_of_month: 1
  emergency_bypass_drill:
    type: "紧急绕过演练"
    frequency: quarterly
    months: [1, 4, 7, 10]
    day_of_month: 15
  recovery_drill:
    type: "恢复演练"
    frequency: quarterly
    months: [2, 5, 8, 11]
    day_of_month: 15
"""


def _drill_file(tmp_path, text, name="drill.yaml"):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_drill_normalizes_frequency_triad_to_standard_cron(tmp_path):
    """态①归一：月/季×DOM 三元组 → 标准 cron，时刻取生成器档 04:00（不发明时间值）。"""
    ents, warns = gen.parse_drill_entities(_drill_file(tmp_path, _DRILL_TRUTH_SAMPLES))
    assert warns == []  # 三条全可归一 → 零告警（告警只属于态③）
    by = {e["task_id"]: e for e in ents}
    # 对照真源三条：月频 DOM=1 / 季频 1,4,7,10 月 DOM=15 / 季频 2,5,8,11 月 DOM=15
    assert by["drill_script_failure"]["window_expr"] == "0 4 1 * *"
    assert by["drill_emergency_bypass"]["window_expr"] == "0 4 15 1,4,7,10 *"
    assert by["drill_recovery"]["window_expr"] == "0 4 15 2,5,8,11 *"
    assert all(e["window_type"] == "cron" for e in ents)
    assert all(e["status"] == "planned" for e in ents)  # 无自动触发器 → R-D 不占闸内存和
    assert all(e["schedule_truth_source"] == gen.DRILL_SCHEDULE_RELPATH for e in ents)
    assert all(e["trading_sensitive"] is False for e in ents)  # light 类免 E0 管辖
    # task_id 去 `_drill` 冗余后缀（drill_ 前缀已表达身份）
    assert set(by) == {"drill_script_failure", "drill_emergency_bypass", "drill_recovery"}
    # 时刻档进 notes（人复核看得见"这个钟点是生成器档而非真源申报"）
    assert "04:00" in by["drill_script_failure"]["notes_zh"]
    # 申报初值取自 DRILL_OVERRIDES（人可复核），非覆盖类走默认 light/30min
    assert by["drill_recovery"]["peak_mem_gb"] == gen.DRILL_OVERRIDES["recovery_drill"]["mem"]
    assert by["drill_recovery"]["est_duration_min"] == 60


def test_drill_dom_list_and_missing_dom_normalization(tmp_path):
    """归一边界：DOM 列表→逗号串；缺 DOM→该字段 *（月频缺 months 同样 *，不猜月）。"""
    text = """
module_id: x
drills:
  multi_dom_drill:
    frequency: quarterly
    day_of_month: [1, 15]
    months: [3, 6, 9, 12]
  no_dom_drill:
    frequency: monthly
  no_months_drill:
    frequency: monthly
    day_of_month: 7
    months: []
"""
    ents, warns = gen.parse_drill_entities(_drill_file(tmp_path, text))
    by = {e["task_id"]: e for e in ents}
    assert by["drill_multi_dom"]["window_expr"] == "0 4 1,15 3,6,9,12 *"
    assert by["drill_no_dom"]["window_expr"] == "0 4 * * *"
    assert by["drill_no_months"]["window_expr"] == "0 4 7 * *"  # 空 months=月频不限月
    assert warns == []


@pytest.mark.parametrize(
    "start_min,duration_min,expected,shifted",
    [
        (390, 60, 660, True),    # 06:30×60min 落窗 → 后置到 10:00 + 60min 档 = 11:00
        (350, 90, 690, True),    # 05:50×90min 尾越界 → 11:30（时长完整保 30min 档对齐）
        (240, 30, 240, False),   # 生成器默认档 04:00：未落窗原样返回（判得准才动）
        (100, 30, 100, False),   # 凌晨档未落窗
        (359, 1, 359, False),    # 窗头前一分钟且尾不越界（[360,600) 半开区间）
        (359, 2, 600, True),     # 尾越界 1 分钟即整体移出
        (360, 1, 600, True),     # 窗头含
        (599, 1, 600, True),     # 窗尾前一分钟仍算落窗
        (600, 30, 600, False),   # 窗尾不含：10:00 起跑不必再挪
        (390, 0, 600, True),     # 零时长也必移（点落窗内=与备份同时起跑）
        (390, None, 600, True),  # 缺时长=None 当 0 处理，不因缺值放行
        (240, 600, 1200, True),  # 超长演练：窗尾 + 整段时长（30min 档对齐 = (600//30)*30）
    ],
)
def test_drill_avoid_backup_window_is_pure_and_conservative(start_min, duration_min, expected, shifted):
    """态②避让：落备份窗=整体后置到窗尾，按 30min 档对齐；未落窗原样返回。"""
    got, got_shifted = gen.avoid_backup_window(start_min, duration_min)
    assert (got, got_shifted) == (expected, shifted)
    lo = int(gen.BACKUP_WINDOW_GUARD["start_minute"])
    hi = int(gen.BACKUP_WINDOW_GUARD["end_minute"])
    dur = max(int(duration_min or 0), 0)
    if not shifted:  # 未避让者必须真的与禁排窗无交集（不是"避了但看不出来"）
        assert not (lo <= got < hi) and not (got < hi and got + dur > lo)
    if shifted:
        assert got >= hi and got % 30 == 0  # 后置方向 + 整档对齐（宁可错避，不可错排）


def test_drill_avoidance_shifts_cron_and_marks_notes(tmp_path, monkeypatch):
    """态②端到端：起跑档落窗时 cron 随之改写，且 notes 留"已避让"痕（不留静默）。"""
    monkeypatch.setattr(gen, "DRILL_START_MINUTE_OF_DAY", 6 * 60 + 30)  # 06:30 起跑
    for key in list(gen.DRILL_OVERRIDES):
        monkeypatch.setitem(gen.DRILL_OVERRIDES, key,
                            dict(gen.DRILL_OVERRIDES[key], dmin=60))
    ents, warns = gen.parse_drill_entities(_drill_file(tmp_path, _DRILL_TRUTH_SAMPLES))
    assert warns == []  # 避让不是降级，不该出归一告警
    assert all(e["window_expr"].startswith("0 11 ") for e in ents), \
        [e["window_expr"] for e in ents]  # 06:30+60min → 11:00 起跑（时点进 cron）
    assert all("已避让出备份窗" in e["notes_zh"] for e in ents)
    assert all("未落备份窗" not in e["notes_zh"] for e in ents)
    # 避让只动时刻档，不动排程结构（DOM/月列表原样）
    by = {e["task_id"]: e for e in ents}
    assert by["drill_recovery"]["window_expr"] == "0 11 15 2,5,8,11 *"


def test_drill_unnormalizable_frequency_degrades_to_manual(tmp_path):
    """态③降级：weekly/daily 与季频缺 months → manual + 逐条告警文案（不猜时间）。"""
    text = """
module_id: x
drills:
  weekly_probe:
    type: "周频探针"
    frequency: weekly
    day_of_month: 2
  daily_probe:
    type: "日频探针"
    frequency: daily
  quarterly_missing_months:
    type: "季频缺月"
    frequency: quarterly
    day_of_month: 15
  missing_frequency:
    type: "无频率"
"""
    ents, warns = gen.parse_drill_entities(_drill_file(tmp_path, text))
    by = {e["task_id"]: e for e in ents}
    assert len(ents) == 4
    assert all(e["window_type"] == "manual" for e in ents)
    assert all(e["window_expr"] is None for e in ents)  # manual 窗=无时间表达式
    # 降级实体仍在表（画像不丢），只是不占自动排产
    assert all(e["status"] == "planned" for e in ents)
    joined = "\n".join(warns)
    assert len(warns) == 4
    assert "drill_window_unnormalized weekly_probe" in joined
    assert "frequency='weekly'" in joined            # 说清是哪一频不认
    assert "drill_window_unnormalized daily_probe" in joined
    assert "frequency='daily'" in joined
    assert "drill_window_unnormalized quarterly_missing_months" in joined
    assert "quarterly 但未声明 months" in joined       # 季频无月列表=无法归一（不猜季度）
    assert "frequency='缺失'" in joined               # 缺 frequency 同样点名降级
    assert all("降级 manual" in w for w in warns)


def test_drill_non_dict_entry_skipped_with_warning(tmp_path):
    text = 'module_id: x\ndrills:\n  broken_entry: "不是字典"\n  ok_drill:\n    frequency: monthly\n    day_of_month: 1\n'
    ents, warns = gen.parse_drill_entities(_drill_file(tmp_path, text))
    assert [e["task_id"] for e in ents] == ["drill_ok"]
    assert any(w.startswith("drill_skipped broken_entry") for w in warns)


@pytest.mark.parametrize(
    "content,expected_prefix",
    [
        (None, "drill_source_missing"),        # 真源缺席
        ("drills: [oops\n", "drill_source_unreadable"),  # YAML 语法崩
        ("module_id: x\ndrills: {}\n", "drill_source_empty"),  # 结构变更/空表
    ],
)
def test_drill_source_absent_or_broken_degrades_loudly(tmp_path, content, expected_prefix):
    """第 4 真源源读不动 → 空实体 + 必发告警（本臂新加，绝不允许把三源再生搞崩）。"""
    p = tmp_path / "drill.yaml"
    if content is not None:
        p.write_text(content, encoding="utf-8")
    ents, warns = gen.parse_drill_entities(p)
    assert ents == []
    assert len(warns) == 1 and warns[0].startswith(expected_prefix)


def test_drill_production_source_parses_as_cron_or_manual_only():
    """生产真源可读性钉（结构判据，不钉内容）：每条演练都收进 cron/manual 二态之一。"""
    ents, warns = gen.parse_drill_entities()  # 默认真源路径=scripts/governance/meta/drill_schedule.yaml
    assert ents, "生产 drill 真源解析为空=第 4 真源源脱编（本函数默认路径即真源）"
    assert not any(w.startswith(("drill_source_missing", "drill_source_unreadable",
                                 "drill_source_empty")) for w in warns), warns
    for e in ents:
        assert e["schedule_truth_source"] == gen.DRILL_SCHEDULE_RELPATH
        assert e["window_type"] in {"cron", "manual"}
        if e["window_type"] == "cron":
            assert _CRON_SHAPE.match(str(e["window_expr"])), e["window_expr"]  # 无第四种日期法
            assert e["window_expr"].endswith(" *")  # dow 恒 *（演练按日不按星期）
        else:
            assert e["window_expr"] is None


# ---------------------------------------------------------------------------
# ⑥ C-11 声明↔代码反查臂：gated / gap / unresolved 三态台账 + 幂等标注
# 纪律：反查按 REPO_ROOT 定位源码，故整仓重定向 tmp（假仓），禁读写真仓执行体。
# ---------------------------------------------------------------------------
def _ent(task_id, truth_source="", **over):
    ent = {
        "task_id": task_id,
        "status": "active",
        "trading_sensitive": True,
        "schedule_truth_source": truth_source,
        "notes_zh": f"人写的正文 {task_id}",
    }
    ent.update(over)
    return ent


@pytest.fixture()
def fake_repo(tmp_path, monkeypatch):
    """假仓：py/ps1 执行体链 + -m 模块 + 数据槽宿主，全部落在 tmp（真仓零接触）。"""
    root = tmp_path / "repo"

    def w(rel, text):
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return rel

    # 已受闸执行体（三种被承认的调用形态各一种）
    w("scripts/fake/gated.py",
      "from scripts.backtest.compute_window_gate import check_gate\n\n"
      "def main():\n    return check_gate('fake_task', 'local_gpu')\n")
    w("scripts/fake/decision.py",
      "def main(e0):\n    return e0.gate_decision('fake_task', True, now, is_td)\n")
    w("scripts/fake/e0call.py",
      "def main():\n    return runtime_e0_decision('fake_task')\n")
    # 裸奔执行体：闸名只出现在注释/[DEPENDENCIES] 头和 import 里，**从不调用**
    w("scripts/fake/bare.py",
      "# [DEPENDENCIES] scripts.backtest.compute_window_gate\n"
      "# 本脚本自报已受 FAC-E0 管辖：check_gate 只是写在注释里的名字\n"
      "from scripts.backtest.compute_window_gate import check_gate\n\n"
      "def main():\n    return 0\n")
    # ps1 动作链：直取 .py / 变量前缀 / 盘符前缀 / 一跳子 ps1 / -m 模块 / 无脚本
    w("scripts/fake/gated_direct.ps1", 'python "scripts/fake/gated.py" --all\n')
    w("scripts/fake/gated_varroot.ps1",
      '$RepoRoot = "D:\\ZephyrAlpha"\n'
      '$a = "$RepoRoot\\scripts\\fake\\gated.py"\n')
    w("scripts/fake/gated_driver.ps1",
      'python "D:/ZephyrAlpha/scripts/fake/decision.py"\n')
    w("scripts/fake/hop.ps1", 'powershell -File "scripts/fake/inner.ps1"\n')
    w("scripts/fake/inner.ps1", 'python "scripts/fake/e0call.py"\n')
    w("scripts/fake/mod.ps1", "python -m fake.mod\n")
    w("src/fake/mod.py", "def main():\n    return check_gate('fake_mod')\n")
    w("scripts/fake/bare.ps1", 'python "scripts/fake/bare.py"\n')
    w("scripts/fake/quiet.ps1", 'Write-Host "只说话不拉脚本"\n')
    w("src/zephyr/data/scheduler.py", "def init_scheduler():\n    return None\n")
    monkeypatch.setattr(gen, "REPO_ROOT", root)
    return root


def test_c11_resolve_executor_source_calibers(fake_repo):
    """执行体定位四口径：直指 .py / ps1 链（含一跳与 -m）/ 槽位归宿主 / 不可达不猜。"""
    R = gen.resolve_executor_sources
    assert R(_ent("sch_a", "scripts/fake/gated.py")) == (["scripts/fake/gated.py"], "py_truth_source")
    assert R(_ent("sch_b", "scripts/fake/gated_direct.ps1")) == (["scripts/fake/gated.py"], "ps1_chain")
    # 变量前缀 `$RepoRoot\scripts\...` 与盘符前缀 `D:/.../scripts/...` 都归一到仓内相对路径
    assert R(_ent("sch_c", "scripts/fake/gated_varroot.ps1")) == (["scripts/fake/gated.py"], "ps1_chain")
    assert R(_ent("sch_d", "scripts/fake/gated_driver.ps1")) == (["scripts/fake/decision.py"], "ps1_chain")
    # .ps1 递归一跳（拉子脚本→子脚本再拉 .py；中间的 .ps1 不进执行体清单）
    assert R(_ent("sch_e", "scripts/fake/hop.ps1")) == (["scripts/fake/e0call.py"], "ps1_chain")
    # `-m 模块` → src 路径
    assert R(_ent("sch_f", "scripts/fake/mod.ps1")) == (["src/fake/mod.py"], "ps1_chain")
    # 槽位执行体=宿主进程（21 槽共用一个进程，逐槽找模块会找到天上）
    assert R(_ent("data_slot_x", "src/zephyr/data/config/schedule.yaml")) == \
        ([gen.EXECUTOR_SOURCE_RELPATH], "data_slot_host")
    # 源不可达：声明的 .py 不存在 / ps1 链无脚本 / 无真源——三状都返回空表 + 各自口径码
    assert R(_ent("sch_g", "scripts/fake/gone.py")) == ([], "py_unreadable")
    assert R(_ent("sch_h", "scripts/fake/quiet.ps1")) == ([], "ps1_chain_empty")
    assert R(_ent("sch_i", "")) == ([], "unresolved")
    assert R(_ent("sch_j", "docs/plan.md")) == ([], "unresolved")


def test_c11_ledger_separates_gated_gap_unresolved(fake_repo):
    """三态台账：查过没问题（gated）/ 声明缺口（gap）/ 查不动（unresolved）必须分开留痕。"""
    ents = [
        _ent("sch_gated_direct", "scripts/fake/gated.py"),
        _ent("sch_gated_chain", "scripts/fake/gated_direct.ps1"),
        _ent("sch_gap_chain", "scripts/fake/bare.ps1"),
        _ent("data_slot_host_probe", "src/zephyr/data/config/schedule.yaml"),
        _ent("sch_unreach_py", "scripts/fake/gone.py"),
        _ent("sch_unreach_chain", "scripts/fake/quiet.ps1"),
        _ent("sch_unreach_nosrc", ""),
        # 免查面：未排产 / 未申报受闸——不进台账（不制造噪声）
        _ent("sch_planned", "scripts/fake/bare.py", status="planned"),
        _ent("sch_not_sensitive", "scripts/fake/bare.py", trading_sensitive=False),
        _ent("sch_retired", "scripts/fake/bare.py", status="retired"),
    ]
    findings, ledger = gen.check_gate_declaration_gaps(ents)
    by = {l["task_id"]: l for l in ledger}
    assert set(by) == {"sch_gated_direct", "sch_gated_chain", "sch_gap_chain",
                       "data_slot_host_probe", "sch_unreach_py", "sch_unreach_chain",
                       "sch_unreach_nosrc"}
    assert by["sch_gated_direct"]["verdict"] == "gated"
    assert by["sch_gated_direct"]["sources"] == ["scripts/fake/gated.py"]
    assert by["sch_gated_chain"]["verdict"] == "gated" and by["sch_gated_chain"]["how"] == "ps1_chain"
    assert by["sch_gap_chain"]["verdict"] == "gap"
    assert by["data_slot_host_probe"] == {"task_id": "data_slot_host_probe", "verdict": "gap",
                                          "how": "data_slot_host",
                                          "sources": [gen.EXECUTOR_SOURCE_RELPATH]}
    assert {by[t]["verdict"] for t in ("sch_unreach_py", "sch_unreach_chain",
                                       "sch_unreach_nosrc")} == {"unresolved"}
    assert all(by[t]["sources"] == [] for t in ("sch_unreach_py", "sch_unreach_chain",
                                                "sch_unreach_nosrc"))
    # findings 只属于 gap（unresolved 是"查不动"，不是"违规"）
    assert sorted(tid for f in findings for tid in f["task_ids"]) == ["data_slot_host_probe",
                                                                      "sch_gap_chain"]
    assert all(f["reason_code"] == gen.GAP_REASON_CODE for f in findings)
    assert all(f["severity"] == "warn" for f in findings)  # 本臂先留痕后升格，不 block
    detail = findings[0]["detail"]
    assert "trading_sensitive=True" in detail and "纸面受管" in detail
    assert "解析口径=" in detail and "check_gate()" in detail  # 修法可执行
    # 非 dict 实体（脏表容错）不炸反查
    f2, l2 = gen.check_gate_declaration_gaps([None, "x", _ent("sch_gated_direct", "scripts/fake/gated.py")])
    assert l2[0]["task_id"] == "sch_gated_direct" and f2 == []


def test_c11_recognizes_gate_call_shape_not_symbol_name(fake_repo):
    """红蓝口径：注释/[DEPENDENCIES]/import 里写闸名洗不白，只认调用形态三种。"""
    assert gen._RE_GATE_CALL.search("check_gate(")
    assert gen._RE_GATE_CALL.search("e0.gate_decision(  ")
    assert gen._RE_GATE_CALL.search("runtime_e0_decision('p')")
    assert not gen._RE_GATE_CALL.search("# check_gate 已在注释里提到")
    assert not gen._RE_GATE_CALL.search("from x import check_gate\n")
    assert not gen._RE_GATE_CALL.search("compute_window_gate  # 裸符号名")
    # 端到端同判：bare.py 里闸名齐备但一次没调 → gap；三种调用形态各 → gated
    ents = [_ent("sch_bare", "scripts/fake/bare.py"),
            _ent("sch_check", "scripts/fake/gated.py"),
            _ent("sch_decision", "scripts/fake/decision.py"),
            _ent("sch_e0call", "scripts/fake/e0call.py")]
    findings, ledger = gen.check_gate_declaration_gaps(ents)
    verdicts = {l["task_id"]: l["verdict"] for l in ledger}
    assert verdicts == {"sch_bare": "gap", "sch_check": "gated",
                        "sch_decision": "gated", "sch_e0call": "gated"}
    assert [f["task_ids"][0] for f in findings] == ["sch_bare"]


def test_c11_annotation_is_idempotent_and_spares_human_text(fake_repo):
    """标注幂等：二次调用 notes_zh 零变化；人写正文一字不动；没标注的实体不被改写。"""
    ents = [
        _ent("sch_gap_chain", "scripts/fake/bare.ps1"),
        _ent("sch_gated_direct", "scripts/fake/gated.py"),
        _ent("sch_human_stale_note", "scripts/fake/gated.py",
             notes_zh="人写的正文 保留 " + gen.GAP_NOTE_MARK + " 上一轮的旧账尾注"),
        _ent("sch_unreach_py", "scripts/fake/gone.py"),
        {"task_id": "sch_no_notes_key", "status": "active", "trading_sensitive": True,
         "schedule_truth_source": "scripts/fake/gone.py"},
    ]
    findings, _ledger = gen.check_gate_declaration_gaps(ents)
    gen.annotate_gate_declaration_gaps(ents, findings)
    first_notes = [e.get("notes_zh") for e in ents]
    gap = next(e for e in ents if e["task_id"] == "sch_gap_chain")
    assert gen.GAP_NOTE_MARK in gap["notes_zh"]
    assert gap["notes_zh"].startswith("人写的正文 sch_gap_chain ")  # 正文原样在前
    # 幂等：连打三次，notes_zh 一字不变
    for _ in range(3):
        gen.annotate_gate_declaration_gaps(ents, findings)
    assert [e.get("notes_zh") for e in ents] == first_notes
    # 只标 gap：gated / unresolved（查不动）不沾哨兵
    by = {e["task_id"]: e for e in ents}
    assert gen.GAP_NOTE_MARK not in by["sch_gated_direct"]["notes_zh"]
    assert gen.GAP_NOTE_MARK not in by["sch_unreach_py"]["notes_zh"]
    # 旧哨兵随事实消失：闸补上后（本轮无 finding）上一轮尾注被剥，人写正文仍保留
    assert by["sch_human_stale_note"]["notes_zh"] == "人写的正文 保留"
    # 无 notes_zh 键的实体不被凭空造键（None 不得被写成空串）
    assert "notes_zh" not in by["sch_no_notes_key"] or by["sch_no_notes_key"]["notes_zh"] is None


def test_c11_report_is_stdout_trace_only_counting_gaps(fake_repo, capsys):
    """留痕臂：stdout 逐 gap 一行 + 三态计数行，返回值只数 gap（不可达≠缺口）。"""
    ents = [_ent("sch_gap_chain", "scripts/fake/bare.ps1"),
            _ent("sch_gated_direct", "scripts/fake/gated.py"),
            _ent("sch_unreach_py", "scripts/fake/gone.py")]
    assert gen.report_gate_declaration_gaps(ents) == 1
    out = capsys.readouterr().out
    gap_lines = [l for l in out.splitlines() if l.startswith("GAP[")]
    assert len(gap_lines) == 1 and "sch_gap_chain" in gap_lines[0]  # 只有 gap 逐条打
    assert "GAP[sched_gate_declaration_gap][warn]: sch_gated_direct" not in out
    audit = [line for line in out.splitlines() if line.startswith("GAP-AUDIT")][0]
    assert "代码实闸 1 / 声明缺口 1 / 反查不可达 1" in audit
    assert "不计退出码" in audit  # 未进闸/告警桥清单的自述（升格前不得影响退出码）


def test_c11_script_token_normalization(fake_repo):
    """路径碎片归一：变量前缀/盘符/反斜杠都归仓内相对路径，锚点前一律噪音，不存在则 None。"""
    assert gen._norm_script_token(r"$RepoRoot\scripts\fake\gated.py") == "scripts/fake/gated.py"
    assert gen._norm_script_token("D:/ZephyrAlpha/scripts/fake/bare.py") == "scripts/fake/bare.py"
    assert gen._norm_script_token("scripts\\fake\\hop.ps1") == "scripts/fake/hop.ps1"
    assert gen._norm_script_token("scripts/fake/never_written.py") is None  # 不在盘=不猜
    assert gen._norm_script_token("no_anchor/x.py") is None
    assert gen._norm_script_token("") is None
    # 链上只收 .py（.ps1 留在解析口径里递归，不进执行体清单的最终判据）
    assert [p for p in gen._ps1_chain_targets('python "scripts/fake/bare.py" "scripts/fake/hop.ps1"')
            if p.endswith(".ps1")] == ["scripts/fake/hop.ps1"]
