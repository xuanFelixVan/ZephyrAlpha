# [A_test] module_id: MOD-RESCHED-PROFILE-TEST_MEM_CEILING_INVARIANT | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.infra.infrastructure.test_resource_schedule_mem_ceiling_invariant
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.gov_enforcement.commit_gates.resource_schedule_gate（判据数学单源，禁克隆）
# [CONSUMERS] 统筹裁定⑦（排班调档）复跑尺；总统统筹班/属主班落地前自证
# [STARTUP] manual (pytest)
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] tests/infra/infrastructure/test_resource_schedule_mem_ceiling_invariant.py
# [TTL] task_bound
"""排班内存天花板机判断言：sum(同刻并发申报量) <= mem_ceiling_gb（统筹裁定⑦）。

大白话：这张排班册自称"同一时刻所有班次的申报内存加起来不许超过 10GB"。本件把
这条不等式钉成一个能跑的测试——先在**未调的旧值**上证明它会红（判通过须先证明能红），
再在**调后新值**上证明它会绿，两端都跑在同一把尺（闸自己的 `_budget_rows`+
`_concurrency_sweep`+`check_mem_ceiling`）上，不另立第二套数学。

三条纪律：
1. **生产文件零写**：红/绿两臂都在 `deepcopy` 出的内存沙箱上跑，`config/resource_profile_registry.yaml`
   与两枚 `register_*.ps1` 真源逐字节不动（裁定 R-A：改排班只能走时间真源 +
   `scripts/governance/apply_resource_plan.py` 单口，表是 [GENERATED] 禁手改）。
2. **禁动上限**：`test_ceiling_constant_pinned_at_10gb` 把 10.0 在三个真源
   （表头 / 生成器常量 / reaper `_DANGEROUS_MEM_GB`）钉成同一枚数——谁放宽上限谁吃红。
3. **旧值内容寻址**：旧窗档 `35 9 * * *|5 13 * * *` / `40 9 * * *` 取自基线 commit
   `e869fd1e0d812fde1a53bab7e0055c9f8919fd50` 的表内现值（`git show <sha>:<path>`），
   不落 `.orig` 副本（docs/_working 目录契约 + 根宪法 §4 禁重复件）。

读数（2026-10-11 实测，本机 `PYTHONNOUSERSITE=1 PYTHONPATH=src python -m pytest` 本件）：
    09:35 同刻和 = 10.5GB（红）｜09:40 同刻和 = 11.0GB（红）
    同池口径   = default 6.5/7.0、realtime 4.0（绿）
    除去那两条档的盘前带基线 = 10.0GB（= 上限本身，零余量）
"""

from __future__ import annotations

import copy
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
import yaml

from zephyr.gov_enforcement.commit_gates import resource_schedule_gate as G

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = REPO_ROOT / "config" / "resource_profile_registry.yaml"
BASELINE_SHA = "e869fd1e0d812fde1a53bab7e0055c9f8919fd50"

TZ = ZoneInfo("Asia/Shanghai")
# 裁定⑦ 所指"明早"= 2026-10-12（周一，交易日）；now 取当日 00:00，窗档由闸展开
HORIZON_NOW = dt.datetime(2026, 10, 12, 0, 0, 0, tzinfo=TZ)
BAND_START = dt.datetime(2026, 10, 12, 9, 30, tzinfo=TZ)
BAND_END = dt.datetime(2026, 10, 12, 10, 0, tzinfo=TZ)

SIM_BRIDGE = "sch_sim_bridge_execute"
SENTINEL = "sch_decision_chain_sentinel"
# 基线旧值（内容寻址，见 docstring）
OLD_SIM_BRIDGE_EXPR = "35 9 * * *|5 13 * * *"
OLD_SENTINEL_EXPR = "40 9 * * *"
# 最小必要错峰量（实算扫出来的最小位移：09:30-09:45 带基线恒 10.0，09:45 起降到 8.0）
NEW_SIM_BRIDGE_EXPR = "45 9 * * *|5 13 * * *"
NEW_SENTINEL_EXPR = "50 9 * * *"

CEILING_GB = 10.0


def _entities() -> list[dict]:
    ents, _header = G.load_registry_entities(REGISTRY)
    return ents


def _header() -> dict:
    _ents, header = G.load_registry_entities(REGISTRY)
    return header


def _patch_windows(ents: list[dict], mapping: dict[str, str]) -> list[dict]:
    """内存沙箱改窗档（生产字节零动）；task_id 不存在即炸，防静默改错实体。"""
    sandbox = copy.deepcopy(ents)
    seen: set[str] = set()
    for e in sandbox:
        tid = str(e.get("task_id"))
        if tid in mapping:
            e["window_expr"] = mapping[tid]
            seen.add(tid)
    missing = set(mapping) - seen
    assert not missing, f"沙箱 patch 未命中实体：{missing}"
    return sandbox


def _band_sums(ents: list[dict]) -> dict[dt.datetime, float]:
    """带内每个事件时刻的**同刻并发申报和最大值**（闸自己的扫描线数学，不另立第二套）。

    同一分钟可有多次事件（intraday 槽 dur=2 每 5 分钟一起一落），逐时刻取最大才是
    "该刻的账"；取末态会把峰读成谷（2026-10-11 自纠：先写末态，09:35 读成 7.0）。
    """
    rows = G._budget_rows(ents, HORIZON_NOW, G.HORIZON_DAYS)
    snaps, mem = G._concurrency_sweep(rows)
    out: dict[dt.datetime, float] = {}
    for t, active in snaps:
        if BAND_START <= t <= BAND_END:
            out[t] = max(out.get(t, 0.0), round(sum(mem.get(x, 0.0) for x in active), 6))
    return out


def _band_active_ids(ents: list[dict]) -> set[str]:
    rows = G._budget_rows(ents, HORIZON_NOW, G.HORIZON_DAYS)
    snaps, _mem = G._concurrency_sweep(rows)
    ids: set[str] = set()
    for t, active in snaps:
        if BAND_START <= t <= BAND_END:
            ids |= set(active)
    return ids


def _band_blocks(ents: list[dict]) -> list[G.Finding]:
    return [
        f
        for f in G.check_mem_ceiling(ents, HORIZON_NOW, G.HORIZON_DAYS, ceiling_gb=CEILING_GB)
        if f.severity == "block" and f.at is not None and BAND_START <= dt.datetime.fromisoformat(f.at) <= BAND_END
    ]


# ---------------------------------------------------------------------------
# ① 上限常数三面一致（禁动 10GB 上限本身——放宽即红）
# ---------------------------------------------------------------------------
def test_ceiling_constant_pinned_at_10gb_across_three_truth_sources():
    assert G._mem_ceiling_gb(_header()) == CEILING_GB, "表头 mem_ceiling_gb 被改＝放松在册门禁"
    gen = (REPO_ROOT / "scripts/governance/generators/generate_resource_profile_registry.py").read_text(
        encoding="utf-8"
    )
    assert "MEM_CEILING_GB = 10.0" in gen, "生成器常量与表头分叉（双上限=第二捕不在岗）"
    reaper = (REPO_ROOT / "src/zephyr/trading/process_reaper.py").read_text(encoding="utf-8")
    assert "_DANGEROUS_MEM_GB = 10.0" in reaper, "reaper 红线被改＝收编在册引用（裁定 R-A 禁）"


# ---------------------------------------------------------------------------
# ② 红臂：未调的旧值上，不等式必须为红（判通过须先证明能红）
# ---------------------------------------------------------------------------
def test_inequality_is_red_on_untouched_old_values():
    old = _patch_windows(_entities(), {SIM_BRIDGE: OLD_SIM_BRIDGE_EXPR, SENTINEL: OLD_SENTINEL_EXPR})
    sums = _band_sums(old)
    assert sums[dt.datetime(2026, 10, 12, 9, 35, tzinfo=TZ)] == 10.5, "09:35 同刻和读数漂移"
    assert sums[dt.datetime(2026, 10, 12, 9, 40, tzinfo=TZ)] == 11.0, "09:40 同刻和读数漂移"
    blocks = _band_blocks(old)
    assert len(blocks) == 2, f"旧值应恰有 09:35/09:40 两条 block，实得 {len(blocks)}"
    assert {f.at[11:16] for f in blocks} == {"09:35", "09:40"}
    # 尺不假红：每条 block 的 `at` 时刻，独立求和确实 > 上限
    for f in blocks:
        assert sums[dt.datetime.fromisoformat(f.at)] > CEILING_GB, f"block 无对应超线读数：{f.at}"
    assert min(sums.values()) < CEILING_GB, "带内处处超线＝尺的视野坏了（应只在两刻红）"


def test_production_registry_now_carries_the_staggered_values():
    """现场读数留证（2026-10-11 维护三班落地后重写；原名
    ``test_production_registry_currently_carries_the_old_values``＝维护二班"本班未代落调档"
    的自证桩，其本体写明"本测试须随属主落地同步改写"）。

    现字节＝总统统筹裁定 T7 经 `apply_resource_plan.py` 单口写回后的值：
    09:35 腿→09:45、09:40 腿→09:50，13:05 腿不动；带内 block 归零。
    """
    ents = _entities()
    live = {str(e["task_id"]): e.get("window_expr") for e in ents}
    assert live[SIM_BRIDGE] == NEW_SIM_BRIDGE_EXPR, f"表内 sim_bridge 窗档非落后面：{live[SIM_BRIDGE]!r}"
    assert live[SENTINEL] == NEW_SENTINEL_EXPR, f"表内 sentinel 窗档非落后面：{live[SENTINEL]!r}"
    assert _band_blocks(ents) == [], "错峰后 09:30-10:00 带内仍报 block"
    # 尺不假绿：同一把尺把两腿拍回旧值必须立刻重新报出那两条红
    assert (
        len(_band_blocks(_patch_windows(ents, {SIM_BRIDGE: OLD_SIM_BRIDGE_EXPR, SENTINEL: OLD_SENTINEL_EXPR}))) == 2
    ), "旧值臂不再红＝尺没牙，本桩的绿不可信"


# ---------------------------------------------------------------------------
# ③ 绿臂：最小必要错峰后的新值上，不等式为绿（同一把尺，生产字节零动）
# ---------------------------------------------------------------------------
def test_inequality_turns_green_after_minimum_offset():
    new = _patch_windows(_entities(), {SIM_BRIDGE: NEW_SIM_BRIDGE_EXPR, SENTINEL: NEW_SENTINEL_EXPR})
    sums = _band_sums(new)
    assert sums, "带内无事件＝尺失效"
    assert max(sums.values()) == CEILING_GB, f"调后带内最大和读数漂移（实得 {max(sums.values())}）"
    assert max(sums.values()) <= CEILING_GB, f"调后仍超上限：{max(sums.values())}"
    assert _band_blocks(new) == [], "调后带内仍有 block"
    # 调档不新增别的冲突（互斥组交叠 / E0 交易保守带 / C-8 同池跨组堆积 三面对拍）
    ents = _entities()
    for checker in (G.check_overlap_group, G.check_e0_trading):
        assert len(checker(new, HORIZON_NOW)) == len(checker(ents, HORIZON_NOW)), "调档引入新冲突"
    new_c8 = [
        f
        for f in G.check_pool_concurrency(new, HORIZON_NOW, G.HORIZON_DAYS, ceiling_gb=CEILING_GB)
        if f.severity == "block"
    ]
    old_c8 = [
        f
        for f in G.check_pool_concurrency(ents, HORIZON_NOW, G.HORIZON_DAYS, ceiling_gb=CEILING_GB)
        if f.severity == "block"
    ]
    assert len(new_c8) == len(old_c8), "调档引入新的同池跨组堆积 block"


# ---------------------------------------------------------------------------
# ④ 裁字面不可满足：只下调那两条档的内存申报值清不了账（不是"少降点"，是降到底也不行）
# ---------------------------------------------------------------------------
def test_lowering_only_those_two_declarations_cannot_clear_the_band():
    """带内除去这两档的基线已 == 上限本身（10.0，零余量），故任何**正值**申报都红。

    凭据：`peak_mem_gb` 是实体真实占用的申报，降它=改申报口径而非改排班；把它压到
    0.0 才是唯一"绿"取值，而 0.0 GB 的进程不存在＝编造申报（册内自规"禁编造"，
    且 P5 实测校准器会把它回写）。⇒ 裁定⑦ 的"调"在机器层面只能= 改时间窗（错峰）。
    """
    fixture = [
        {
            "task_id": "data_slot_intraday_minute",
            "pool": "realtime",
            "peak_mem_gb": 1.0,
            "est_duration_min": 2,
            "window_expr": "*/5 9-15 * * 1-5",
            "exclusive_group": [],
            "status": "active",
        },
        {
            "task_id": "data_slot_intraday_realtime",
            "pool": "realtime",
            "peak_mem_gb": 1.0,
            "est_duration_min": 2,
            "window_expr": "*/5 9-15 * * 1-5",
            "exclusive_group": [],
            "status": "active",
        },
        {
            "task_id": "data_slot_intraday_sector",
            "pool": "realtime",
            "peak_mem_gb": 1.0,
            "est_duration_min": 2,
            "window_expr": "*/5 9-15 * * 1-5",
            "exclusive_group": [],
            "status": "active",
        },
        {
            "task_id": "data_slot_news_slow",
            "pool": "default",
            "peak_mem_gb": 2.0,
            "est_duration_min": 180,
            "window_expr": "17,47 * * * *",
            "exclusive_group": [],
            "status": "active",
        },
        {
            "task_id": "data_slot_post_auction",
            "pool": "default",
            "peak_mem_gb": 2.0,
            "est_duration_min": 30,
            "window_expr": "30 9 * * 1-5",
            "exclusive_group": [],
            "status": "active",
        },
        {
            "task_id": "data_slot_sector_pre_open",
            "pool": "default",
            "peak_mem_gb": 2.0,
            "est_duration_min": 30,
            "window_expr": "15 9 * * 1-5",
            "exclusive_group": [],
            "status": "active",
        },
        {
            "task_id": "sch_paper_session",
            "pool": "realtime",
            "peak_mem_gb": 1.0,
            "est_duration_min": 30,
            "window_expr": "25 9 * * *",
            "exclusive_group": [],
            "status": "active",
        },
    ]
    base = sum(float(e["peak_mem_gb"]) for e in fixture)
    assert base == CEILING_GB, f"带内基线读数漂移（实得 {base}），本断言的前提已不成立"

    two = [
        {
            "task_id": SIM_BRIDGE,
            "pool": "default",
            "peak_mem_gb": 0.5,
            "est_duration_min": 30,
            "window_expr": OLD_SIM_BRIDGE_EXPR,
            "exclusive_group": [],
            "status": "active",
        },
        {
            "task_id": SENTINEL,
            "pool": "default",
            "peak_mem_gb": 0.5,
            "est_duration_min": 15,
            "window_expr": OLD_SENTINEL_EXPR,
            "exclusive_group": [],
            "status": "active",
        },
    ]
    for declared in (0.5, 0.4, 0.3, 0.2, 0.1):
        ents = copy.deepcopy(fixture) + [
            {**two[0], "peak_mem_gb": declared},
            {**two[1], "peak_mem_gb": declared},
        ]
        assert max(_band_sums(ents).values()) > CEILING_GB, (
            f"申报降到 {declared} 仍应红——若此断言翻转，说明带内基线变了，须重读现场"
        )


# ---------------------------------------------------------------------------
# ⑤ 口径伪影排查：跨池和 6 枚 data_slot 同属一个宿主进程（册内自证），同池口径本就绿
# ---------------------------------------------------------------------------
def test_band_data_slots_share_one_host_process_and_are_not_independent_rams():
    ents = _entities()
    band_ids = _band_active_ids(ents)
    slots = [e for e in ents if str(e["task_id"]) in band_ids and str(e["task_id"]).startswith("data_slot_")]
    assert len(slots) == 6, f"带内 data_slot 数读数漂移（实得 {len(slots)}）"
    for e in slots:
        assert e["schedule_truth_source"] == "src/zephyr/data/config/schedule.yaml"
        reason = str((e.get("measured") or {}).get("no_sample_reason_zh") or "")
        assert "N 倍重复计数宿主" in reason, (
            f"{e['task_id']} 的 measured 口径注记已变，跨池求和是否仍在按宿主重复计数须重判"
        )


def test_same_pool_caliber_is_already_green_in_the_band():
    """分池口径（C-8 那本账）带内每池都远低于上限——红的只有"不分池一股脑求和"那一口径。"""
    ents = _entities()
    byid = {str(e["task_id"]): e for e in ents}
    rows = G._budget_rows(ents, HORIZON_NOW, G.HORIZON_DAYS)
    snaps, mem = G._concurrency_sweep(rows)
    worst: dict[str, float] = {}
    for t, active in snaps:
        if not (BAND_START <= t <= BAND_END):
            continue
        per: dict[str, float] = {}
        for tid in active:
            per[str(byid[tid].get("pool"))] = per.get(str(byid[tid].get("pool")), 0.0) + mem.get(tid, 0.0)
        for pool, s in per.items():
            worst[pool] = max(worst.get(pool, 0.0), s)
    assert worst, "带内无池读数"
    assert max(worst.values()) <= CEILING_GB, f"同池口径本应绿，实得 {worst}"
    # 2026-10-11 维护三班 T7 落地后重钉：default 7.0→6.0。来历＝错峰本身——
    # 旧 09:40 刻 default 池=sector_pre_open 2.0+post_auction 2.0+news_slow 2.0+sim 0.5+sentinel 0.5=7.0；
    # 两腿挪到 09:45/09:50 时 pre_open（09:15+30min）已结束，default 峰落在 09:35/09:40 的 6.0（纯基线）。
    # realtime 4.0 未动（三枚 intraday 槽与两腿不同池）。读数实测见
    # docs/_working/maint3_campaign/00_ledger.md §二·读数表。
    assert worst["default"] == pytest.approx(6.0) and worst["realtime"] == pytest.approx(4.0)


# ---------------------------------------------------------------------------
# ⑥ 裁定⑨ 现场读数：GPU 班互斥组未被这张册拦死（也未被它排产）
# ---------------------------------------------------------------------------
def test_gpu_default_group_is_inert_in_the_schedule_book_not_locked_out():
    ents = _entities()
    gpu = [e for e in ents if "gpu_default" in (e.get("exclusive_group") or [])]
    assert len(gpu) == 5, f"gpu_default 组成员数读数漂移（实得 {len(gpu)}）"
    assert all(e.get("window_expr") is None for e in gpu), "组内出现窗档＝互斥账开始生效，须重判"
    assert sum(1 for e in gpu if e.get("est_duration_min") in (0, None)) >= 1
    # 全horizon 互斥组交叠检查：零 block ⇒ 这张册没有把 GPU 班锁死
    assert G.check_overlap_group(ents, HORIZON_NOW, G.HORIZON_DAYS) == []


def test_resident_gpu_holder_is_excluded_from_the_sum_while_over_ceiling():
    """在册申报 8.0≤10 过单实体查；实测 11.5975GB 的常驻体因 window_expr=None 不进任何求和。

    只报现场不代改：这条是"10.5/11.0 读数不是物理读数"的反方向证据——同一本账
    既按槽位重复计一个 126MB 宿主，又漏计一个实测 11.6GB 的常驻显存/内存持有者。
    """
    ents = _entities()
    ollama = next(e for e in ents if e["task_id"] == "sch_ollama_serve")
    assert ollama["exclusive_group"] == ["gpu_default"]
    assert float(ollama["peak_mem_gb"]) == 8.0 <= CEILING_GB
    assert float(ollama["measured"]["peak_mem_gb"]) == pytest.approx(11.5975)
    assert ollama["window_expr"] is None and ollama["est_duration_min"] == 0
    sums = _band_sums(ents)
    assert max(sums.values()) < float(ollama["measured"]["peak_mem_gb"]) * 2, "常驻体被计入带内和＝口径已变"
    # 常驻体在预算表里存在，但窗档为空表 → 扫描线里永不进任何时刻的和
    rows = G._budget_rows(ents, HORIZON_NOW, G.HORIZON_DAYS)
    mine = [wins for (e, _m, wins) in rows if str(e.get("task_id")) == "sch_ollama_serve"]
    assert mine and all(wins == [] for wins in mine), "常驻体开始占窗档账＝口径已变，须重读现场"


def test_t7_landed_bytes_pinned_in_table_and_truth_sources():
    """T7 落地面钉桩。原名 `test_registry_yaml_bytes_untouched_by_this_shift`＝维护二班
    "本班零改动"守卫；总统统筹裁定 T7 授权写回后该前提被**有意**取代，故改写为"落后面钉桩"，
    禁动的上限常数继续钉（谁放宽 10.0 谁吃红）。

    三面同钉：表头上限行 / 表内两枚窗档 / 真源两枚 ps1 触发行，外加"同任务另一枚触发器
    （13:05 腿）未被牵连"——多腿写回最怕顺手挪走别人的班。
    """
    text = REGISTRY.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[15] == "mem_ceiling_gb: 10.0", "表头第 16 行＝上限常数，禁动"
    block = "\n".join(lines)
    assert "window_expr: " + NEW_SIM_BRIDGE_EXPR in block
    assert "window_expr: " + NEW_SENTINEL_EXPR in block
    assert "window_expr: " + OLD_SIM_BRIDGE_EXPR not in block, "表内旧窗档残留=双值第二真源"
    sim = (REPO_ROOT / "scripts/tasks/register/register_sim_bridge_execute_task.ps1").read_text(encoding="utf-8")
    sen = (REPO_ROOT / "scripts/tasks/register/register_decision_chain_sentinel_task.ps1").read_text(encoding="utf-8")
    assert '-Daily -At "09:45"' in sim and '-Daily -At "09:35"' not in sim
    assert '-Daily -At "13:05"' in sim, "同任务另一枚触发器被牵连＝多腿写回越界"
    assert '-Daily -At "09:50"' in sen and '-Daily -At "09:40"' not in sen
    assert sim.isascii() and sen.isascii(), "ps1 含非 ASCII=PS 5.1 GBK 假语法错误（根宪法 §9.7）"


def test_notice_artifact_exists_and_is_greppable():
    """知会件在场（append-only 新件，非生产判据面）——属主与后续班次据此回滚。"""
    notice = REPO_ROOT / "docs/_working/maint2_campaign/16_slot_notice_20261011.md"
    assert notice.exists(), "裁定⑦ 知会件缺席"
    body = notice.read_text(encoding="utf-8")
    assert "SCHED-NOTICE-20261011-R7" in body
    assert "撤销" in body and OLD_SIM_BRIDGE_EXPR in body
    assert yaml  # 件面禁 .json（docs/_working 在册死因），本件为 .md
