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


# ---------------------------------------------------------------------------
# 评估协议（exp_primary 判据禁挪 / exp_r36 另行预注册降权协议）
# DS-275 覆盖边界：A 段 2017-01~2021-12、B 段 2026-07-22 起，中间为源覆盖空洞 ⇒
# 主协议 IS 窗（2019-2023，60 月）在修复源上只有 36 月可得。处置=另立协议，禁挪主闸门。
# ---------------------------------------------------------------------------

_EVAL = Path(__file__).resolve().parents[2] / "scripts" / "backtest" / "eval_exp_expectations.py"
_espec = importlib.util.spec_from_file_location("eval_exp_expectations", _EVAL)
_ev = importlib.util.module_from_spec(_espec)
sys.modules.setdefault("eval_exp_expectations", _ev)
_espec.loader.exec_module(_ev)


def test_primary_protocol_judgement_criteria_are_frozen():
    """主协议窗与判据逐字冻结：任何"顺手调一下"都必须先撞红本钉（预注册禁挪）。"""
    p = _ev._PROTOCOLS["exp_primary"]
    assert p["is"] == ("2019-01-01", "2023-12-31")
    assert p["oos"] == ("2024-01-01", "2026-09-11")
    assert (p["ic_min"], p["sig_rule"], p["coverage_min"]) == (0.02, "t_p<0.05", 0.60)
    assert p["promotion_authority"] == "authoritative"
    assert _ev._IS == p["is"] and _ev._OOS == p["oos"] and _ev._PANEL_HI == p["oos"][1]


def test_r36_protocol_tightens_not_loosens():
    """降权协议只能更严：SE 按 1/sqrt(T) 放大 sqrt(60/36)=1.291 ⇒ 显著性门槛提高、
    效应量地板不动、无 OOS 即无晋级权。放宽任何一项都等于用事后信息改闸门。"""
    r = _ev._PROTOCOLS["exp_r36"]
    assert r["is"] == ("2019-01-01", "2021-12-31"), "IS'=修复源真覆盖区（36 个月）"
    assert r["oos"] == _ev._PROTOCOL_OOS_NA and r["panel_hi"] == "2021-12-31"
    assert r["sig_rule"] == "|t|>3.0", "收紧到 Harvey-Liu-Zhu 新因子门槛（不得回退 p<0.05）"
    assert r["ic_min"] == 0.02, "效应量地板与主协议同值（放大它=变相放宽）"
    assert r["se_inflation_vs_primary"] == 1.291
    assert r["promotion_authority"] == "none" and r["evidence_class"] == "preliminary-coverage-limited"


def test_no_oos_window_reports_not_evaluable_not_zero(monkeypatch):
    """协议无 OOS 窗 → 显式 not_evaluable；禁让空段落成 n_months=0（与"跑了但样本不足"同形）。"""
    import pandas as pd

    empty = pd.DataFrame(columns=["td", "ic", "n", "mom_ic"])
    monkeypatch.setattr(_ev, "_OOS", _ev._PROTOCOL_OOS_NA)
    seg = _ev._seg_oos(empty)
    assert seg["status"] == "not_evaluable" and "源覆盖空洞" in seg["reason"]
    monkeypatch.setattr(_ev, "_OOS", ("2024-01-01", "2026-09-11"))
    assert "status" not in _ev._seg_oos(empty), "有 OOS 窗时走既有 _seg 口径（零漂移）"


def test_cli_r36_on_polluted_source_is_fail_closed(monkeypatch):
    """exp_r36 只成立在修复源上：污染源跑降权协议=给假历史发一张看起来合法的证 → 退出 2。"""
    monkeypatch.setattr(sys, "argv", ["eval", "--protocol", "exp_r36", "--source", "polluted"])
    try:
        _ev.main()
        raise AssertionError("必须 fail-closed 退出（argparse error=2）")
    except SystemExit as exc:
        assert exc.code == 2


def test_cli_exp02_on_repaired_source_is_not_evaluable(monkeypatch, capsys):
    """exp02 在修复源上必须出 not_evaluable：eps_std 结构性恒 0，分歧归一分母为 0 ⇒
    跑出来的 IC 是对不存在数据的断言（χ²(n-1) 在 n=1 时自由度 0=无定义）。"""
    import json as _json

    monkeypatch.setattr(sys, "argv", ["eval", "--factor", "exp02", "--source", "repaired"])
    _ev.main()
    rep = _json.loads(capsys.readouterr().out)
    assert rep["status"] == "not_evaluable" and rep["promotion_authority"] == "none"
    assert "eps_std" in rep["reason"] and rep["oos_window"] is None


# ---------------------------------------------------------------------------
# 滑点腿必须走标定真源（35cf0eb36a 把 MatchingConfig.slippage_bps 默认从 Decimal("1")
# 改成 None=逐笔解析后，_narrow 仍拿它做除法 → 基准档 TypeError，EXP 族三因子的
# narrow_top50 腿全部出不了证，且零测试覆盖 ⇒ 本段是该缺陷的复发钉）
# ---------------------------------------------------------------------------

def _synth_panel(n_syms: int, n_months: int):
    """合成面板（n_months 个月末 × n_syms 只票），够驱动 _narrow 全流程，不连任何 IO。

    月末与 t+20 前向日错开一天，避免 fac/px 索引重叠造成的假对齐。
    """
    import numpy as np
    import pandas as pd

    mes = [f"2019-{m:02d}-28" for m in range(1, n_months + 1)]
    fwd = [f"2019-{m:02d}-20" for m in range(2, n_months + 2)]
    syms = [f"{i:06d}.SZ" for i in range(1, n_syms + 1)]
    idx = pd.to_datetime(sorted(set(mes) | set(fwd)))
    rng = np.random.default_rng(20260916)
    px = pd.DataFrame(
        100.0 * np.cumprod(1.0 + rng.normal(0.0005, 0.02, (len(idx), len(syms))), axis=0),
        index=idx, columns=syms)
    fac = pd.DataFrame(rng.normal(0, 1, (len(mes), len(syms))),
                       index=pd.to_datetime(mes), columns=syms)
    bench = pd.Series(3000.0 * np.cumprod(1.0 + rng.normal(0, 0.01, len(idx))), index=idx)
    return fac, px, bench, mes, {m: f for m, f in zip(mes, fwd)}


def test_narrow_degenerate_panel_degrades_to_none_not_typeerror():
    """广度不足（截面 < _MIN_NAMES）→ 四档全 None，禁抛 TypeError。

    病根：rets 为空时 pd.Series({}) 落默认 RangeIndex(int64)，与 _IS/_OOS 的日期串比较
    抛 "Invalid comparison between dtype=int64 and str"——整轮评估死于一个难懂的 pandas
    报错，而"该窗广度不足"本该是一张能读懂的 None 出证。
    """
    fac, px, bench, mes, fwd_map = _synth_panel(n_syms=4, n_months=4)
    assert 4 < _ev._MIN_NAMES, "面板必须真的够不着广度闸门，否则本测试测不到退化路径"
    out = _ev._narrow(fac, px, bench, mes, fwd_map)
    assert set(out) == {"slip_cfgbp", "slip_20bp", "slip_40bp", "slip_80bp"}
    for leg, vals in out.items():
        assert vals == {"excess_sharpe_is": None, "excess_sharpe_oos": None,
                        "oos_over_is": None}, f"{leg} 广度不足须降级 None，不得崩也不得伪造数值"


def test_narrow_base_slip_leg_consumes_calibrated_cost():
    """基准档（slip=None）必须消费标定真源的正滑点：既不是崩溃，也不是 0bp 的假乐观。

    None 在生产语义里是"按当日成交额走 ADV 分层标定"，不是"没有滑点"也不是旧 1bp 一口价。
    四档成本单调性是本条的判据：cfg 档滑点(标定值) < 20bp ⇒ 超额 Sharpe 严格更高，
    且四档随滑点递增单调下降——若 cfg 档被读成 0 或被读成 20bp，单调关系当场破。
    """
    from zephyr.backtest.core import cost_model_calibration as cost_cal

    per_trade = _ev._AUM / _ev._TOP_N
    base_bps = float(cost_cal.resolve_slippage_bps(per_trade, pinned_flat_bps=None))
    assert 0 < base_bps < 20.0, (
        f"基准档标定滑点须为正且低于最低压力档（实得 {base_bps}bp）；"
        "0=假乐观，>=20=压力网格失去意义，1.0=回退到无出处的 legacy 一口价"
    )
    assert base_bps != float(cost_cal.LEGACY_FLAT_SLIPPAGE_BPS), (
        "result_repository 同口径：consumed 滑点取标定档，不取 legacy 1bp"
    )

    fac, px, bench, mes, fwd_map = _synth_panel(n_syms=120, n_months=8)
    out = _ev._narrow(fac, px, bench, mes, fwd_map)   # 修复前此处 TypeError
    sharpes = [out[k]["excess_sharpe_is"] for k in
               ("slip_cfgbp", "slip_20bp", "slip_40bp", "slip_80bp")]
    assert all(v is not None for v in sharpes), f"够广面板须出数，实得 {sharpes}"
    assert sharpes[0] > sharpes[1] > sharpes[2] > sharpes[3], (
        f"四档超额 Sharpe 须随滑点严格递减（cfg={base_bps}bp < 20 < 40 < 80），实得 {sharpes}"
    )


def test_narrow_pinned_slip_legs_are_returned_verbatim():
    """钉住档 20/40/80 必须原样返回钉住值——压力腿的历史可比性靠这条（零漂移）。"""
    from decimal import Decimal

    from zephyr.backtest.core import cost_model_calibration as cost_cal

    per_trade = _ev._AUM / _ev._TOP_N
    for pinned in (20.0, 40.0, 80.0):
        got = cost_cal.resolve_slippage_bps(per_trade, pinned_flat_bps=Decimal(str(pinned)))
        assert float(got) == pinned, f"钉住档 {pinned}bp 被分层改写=压力腿失去可比性"
    assert _ev._SLIP_STRESS == (None, 20.0, 40.0, 80.0), "压力网格是预注册档，禁顺手改档位"


# ── T5 口径治本钉（2026-09-17）：coverage 门可比数=月覆盖率，coverage_mean=计数 ──

def _synth_ic_df(n_months=33, n_val=920.0):
    import pandas as pd
    import numpy as np
    return pd.DataFrame({
        "td": [f"20{19 + i // 12}-{(i % 12) * 3 + 1:02d}-28" for i in range(n_months)],
        "n": np.full(n_months, n_val),
        "ic": np.linspace(0.01, 0.05, n_months),
        "mom_ic": np.full(n_months, np.nan),
    })


def test_seg_coverage_ratio_is_month_fraction():
    """coverage_ratio=n_months/IS 月数（百分比门可比数），33/36=0.9167。"""
    seg = _ev._seg(_synth_ic_df(33), 36)
    assert seg["coverage_ratio"] == round(33 / 36, 4)
    assert seg["n_months"] == 33


def test_seg_coverage_mean_stays_breadth_count():
    """coverage_mean 原样保留为月均截面广度计数（920.0）——历史出证逐键可比。"""
    seg = _ev._seg(_synth_ic_df(33), 36)
    assert seg["coverage_mean"] == 920.0


def test_seg_without_total_months_has_no_ratio_key():
    """OOS/legacy 路径不传分母 → coverage_ratio 键不出现，既有键集零漂移。"""
    seg = _ev._seg(_synth_ic_df(33))
    assert "coverage_ratio" not in seg
    assert set(seg) == {"n_months", "ic_mean", "t_p", "coverage_mean", "mom_ic_mean"}


def test_is_total_months_denominator_follows_protocol(monkeypatch):
    """分母随协议窗：exp_r36 IS' 2019-2021=36 个月末（非主协议 60）。"""
    cal = [f"2019-{m:02d}-28" for m in range(1, 13)] + \
          [f"20{y}-{m:02d}-28" for y in (20, 21) for m in range(1, 13)] + \
          [f"20{y}-{m:02d}-28" for y in (22, 23) for m in range(1, 13)]
    monkeypatch.setattr(_ev, "_IS", ("2019-01-01", "2021-12-31"))
    assert _ev._is_total_months(cal) == 36
    monkeypatch.setattr(_ev, "_IS", ("2019-01-01", "2023-12-31"))
    assert _ev._is_total_months(cal) == 60
