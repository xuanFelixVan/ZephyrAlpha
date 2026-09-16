# [TEST] tests/scripts/test_build_consensus_daily_repaired.py
# [DOMAIN] D_DATA
# [TARGET] scripts/ch/build_consensus_daily_repaired.py::guard_pass / pick_slots / to_report_row + 适配后喂生产核的合成行为（纯函数，无 IO）
# [TTL] permanent
"""consensus_daily_repaired 证据适配层单元测试（C4 历史修复双轨重建，2026-09-16）。

覆盖：G1 量纲守卫边界（域内不可能值剔除）、G2 槽位选取规则 S1（前瞻优先/补上一年/截断至 3）、
槽位打包（不足三槽置 0 年+None EPS）、以及"适配层喂进生产核后 PIT 窗口与评级统计逐列不变"。
零 IO 零生产路径（不连 ClickHouse、不写 data/）。
"""

from __future__ import annotations

import importlib.util
import sys
from datetime import date
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "ch" / "build_consensus_daily_repaired.py"
_spec = importlib.util.spec_from_file_location("build_consensus_daily_repaired", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("build_consensus_daily_repaired", _mod)
_spec.loader.exec_module(_mod)


# ---------------------------------------------------------------------------
# G1 量纲守卫
# ---------------------------------------------------------------------------

def test_guard_pass_boundaries():
    """eps∈(0,50] 放行；0/负数/50 以上/None/NaN 拒绝（>50 段实证为营业收入行串列）。"""
    assert _mod.guard_pass(0.08) is True      # 苏宁云商 2017E=0.08 案：低值可为真值
    assert _mod.guard_pass(41.8) is True      # 茅台 2021 实际 EPS，域内上界内
    assert _mod.guard_pass(50.0) is True
    assert _mod.guard_pass(50.01) is False
    assert _mod.guard_pass(99.0) is False     # 跨标的重复哨兵值
    assert _mod.guard_pass(4696.2) is False   # 002563 案：营业收入(百万元)串成 EPS
    assert _mod.guard_pass(0.0) is False
    assert _mod.guard_pass(-1.5) is False
    assert _mod.guard_pass(None) is False
    assert _mod.guard_pass(float("nan")) is False


# ---------------------------------------------------------------------------
# G2 槽位选取规则 S1
# ---------------------------------------------------------------------------

def test_pick_slots_prefers_forward_years():
    """四个年度含发布年前一年时，取当年/次年/两年后，丢最远年（对齐 fy0/fy1/fy2 三槽）。"""
    picked = _mod.pick_slots([(2017, 0.28), (2018, 0.28), (2019, 0.49), (2020, 0.74)], 2018)
    assert picked == [(2018, 0.28), (2019, 0.49), (2020, 0.74)]


def test_pick_slots_keeps_prior_year_legitimate_forecast():
    """年初研报预测上一年度合法（抽核首批 #7 大族激光 2016E 案）——无当年预测时须保留。"""
    picked = _mod.pick_slots([(2016, 0.72), (2017, 0.95)], 2017)
    assert picked == [(2017, 0.95), (2016, 0.72)]


def test_pick_slots_backfill_order_is_nearest_first():
    """前瞻槽不足三位时，按"离发布年最近"降序补上一年，且整体截断到 SLOT_MAX。"""
    picked = _mod.pick_slots(
        [(2015, 1.0), (2016, 1.1), (2018, 1.3), (2019, 1.4)], 2017
    )
    assert picked == [(2018, 1.3), (2019, 1.4), (2016, 1.1)]
    assert len(_mod.pick_slots([(2018 + i, 1.0) for i in range(9)], 2018)) == _mod.SLOT_MAX


# ---------------------------------------------------------------------------
# 槽位打包
# ---------------------------------------------------------------------------

def test_to_report_row_packs_three_slots_and_nulls_pe():
    row = _mod.to_report_row("600519", "2019-04-25", "华泰", "买入",
                             [(2019, 32.8), (2020, 37.2), (2021, 41.8)])
    assert row["fy0_year"] == 2019 and row["eps_fy0"] == 32.8
    assert row["fy1_year"] == 2020 and row["eps_fy1"] == 37.2
    assert row["fy2_year"] == 2021 and row["eps_fy2"] == 41.8
    # C4 提取表 pe 列实测全空 → 三槽 PE 恒 None，repaired 的 pe_consensus 对 A 段恒 NULL
    assert row["pe_fy0"] is None and row["pe_fy1"] is None and row["pe_fy2"] is None


def test_to_report_row_missing_slots_become_zero_year():
    """只提取到一年预测时，其余槽位 year=0/eps=None（生产核按此丢弃，不产生幽灵年份行）。"""
    row = _mod.to_report_row("600519", "2019-04-25", "华泰", "买入", [(2019, 32.8)])
    assert row["fy0_year"] == 2019 and row["eps_fy0"] == 32.8
    assert row["fy1_year"] == 0 and row["eps_fy1"] is None
    assert row["fy2_year"] == 0 and row["eps_fy2"] is None


# ---------------------------------------------------------------------------
# 适配层 × 生产核：口径逐列不变的性质测试
# ---------------------------------------------------------------------------

def _dates():
    return [date(2019, 3, 1), date(2019, 3, 20), date(2019, 6, 30)]


def test_adapter_output_feeds_production_core_and_respects_pit():
    """PIT 铁律在适配后仍成立：3 月 1 日快照不得含 3 月 20 日发布的研报预测。"""
    rows = [
        _mod.to_report_row("600519", "2019-01-10", "东吴", "买入", [(2019, 30.0)]),
        _mod.to_report_row("600519", "2019-03-20", "华泰", "增持", [(2019, 33.0)]),
    ]
    out = _mod.build_consensus_rows(rows, _dates(), window_days=90)
    by_date = {(r[0], r[2]): r for r in out}
    # 2019-03-01 窗口=[2018-12-01, 2019-03-01] → 只有 1 月那份
    assert by_date[("2019-03-01", 2019)][3] == 30.0
    assert by_date[("2019-03-01", 2019)][9] == 1
    # 2019-06-30 窗口=[2019-03-31, 2019-06-30] → 两份都出窗（3-20 距今 >90 天），不成行
    assert ("2019-06-30", 2019) not in by_date


def test_rating_stats_use_all_reports_not_only_eps_bearers():
    """无 EPS 证据的研报仍贡献评级/机构统计（与 DS-229 同义，这是双轨可对照的前提）。"""
    rows = [
        _mod.to_report_row("600519", "2019-02-01", "东吴", "买入", [(2019, 30.0)]),
        _mod.to_report_row("600519", "2019-02-05", "国泰", "增持", []),  # 无 high 置信提取
        _mod.to_report_row("600519", "2019-02-09", "申万", "", []),      # 无评级
    ]
    out = _mod.build_consensus_rows(rows, [date(2019, 3, 1)], window_days=90)
    row = next(r for r in out if r[2] == 2019)
    assert row[9] == 1        # n_reports 只数有该年预测的（1 份）
    assert row[10] == 3       # n_orgs 数窗口内全部机构（3 家）
    assert row[16] == 1       # n_unrated 记无评级那份
    assert row[3] == 30.0


def test_provenance_columns_appended_without_breaking_column_count():
    """A 段行在 DS-229 二十列后追加 data_source/eps_source/build_batch 三值=22 列。"""
    rows = [_mod.to_report_row("600519", "2019-02-01", "东吴", "买入", [(2019, 30.0)])]
    base = _mod.build_consensus_rows(rows, [date(2019, 3, 1)], window_days=90)
    wrapped = [r[:19] + ("pdf_forecast_extracted", _mod.EPS_SOURCE_PDF_HIGH, _mod.BUILD_BATCH)
               for r in base]
    assert len(wrapped[0]) == 22
    assert wrapped[0][19] == "pdf_forecast_extracted"
    assert wrapped[0][21] == _mod.BUILD_BATCH
    # INSERT_COLUMNS 必须与行宽一致（否则写入静默错位）
    from schemas.categories.fundamental.consensus_daily_repaired import INSERT_COLUMNS
    assert len(INSERT_COLUMNS.strip("()").split(",")) == 22
