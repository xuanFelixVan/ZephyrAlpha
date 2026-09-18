#!/usr/bin/env python
# [BLUEPRINT] MOD-BT-218 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.exp_ic_evidence
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.eval_exp_expectations; zephyr.factor.expectations;
#                zephyr.data.ch_reader; zephyr.data.table_registry; scipy; pyyaml
# [CONSUMERS] docs/_working/kimi_audit/exp_evidence/exp_ic_evidence_ds271.yaml（WO-⑤-12 出证件）；
#             裁定#338④ DS-271 三口径预注册的执行端；factor_registry FCT-EXP 族证据引用
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 口径真源=eval_exp_expectations（现有 EXP 评估器）——本件零复制其判据/SQL/统计核，
#              全部 import 复用（_PROTOCOLS.exp_r36/build_ic_table/_seg/month_ends/SQL 常量）；
#              协议=exp_r36（裁定#338④ A 案：IS' 2019-01-01~2021-12 共 36 月窗缩，2022+ 缺证据
#              不复跑，全窗复跑待修复证据补齐）；聚合=high-only（exp_grade 即
#              pdf_forecast_extracted.confidence，high 入聚合，mid/low 只出诊断计数不入主统计；
#              DS-275 segment A 结构性只吃 high 行=repaired_compute :40/:212 守卫）；
#              IC=Spearman 截面秩相关（评估器口径）→ IC=秩IC 同值双标；
#              显著性=|t|>3.0（exp_r36 收紧门槛）；OOS'=结构不存在→显式 not_evaluable；
#              promotion_authority=none（永不产出晋级/否决结论）；
#              exp02/exp05 在修复源上结构性 not_evaluable（eps_std 恒 0，评估器 :50-52 已钉）；
#              零数据诚实件：探表失败/全空→出 verdict=NOT_EVALUABLE 零数据件，禁造数；
#              CH 读写走注入缝（_ch_query，测试注入 fake，生产走 ch_reader 正门，禁裸 duckdb）
# [MODIFY-GUARD] none
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 表不可达/探针失败->零数据证据件（不抛出证中断）；SQL 空->RuntimeError(加载失败)
# [TESTS] tests/backtest/test_exp_ic_evidence.py（零网：fake query 注入缝）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  一次性出证 CLI：按晋级批次/裁定批手动执行，无常驻循环
"""exp_ic_evidence.py — EXP 六因子 IC 出证（WO-⑤-12，裁定 #338④ 口径执行端）。

数据源=c3_fundamental.consensus_daily_repaired（DS-275 双轨修复表）+ pdf_forecast_extracted
（C4 PDF 发布时点提取，exp03 修正广度的研报级 EPS 直接源）。产出 YAML 证据件落
docs/_working/kimi_audit/exp_evidence/exp_ic_evidence_ds271.yaml，含：
  caliber 段（裁定 #338④ 逐字引用+窗缩显著标注+high/mid/low 三档计数）
  probe  段（表存在性/行数/置信档分布）
  factors段（exp01~exp06 各自 IS' 段 IC（=秩IC）/覆盖度/t 检验/判读）
  comparison 段（旧口径既有出证的对照说明，不改旧件）

与 eval_exp_expectations.py 的关系：那件是 SOP-B ④⑤⑥ 单因子评估器（判据真源）；
本件是裁定 #338④ 授权的六因子聚合出证编排（只编排不另立判据），统计核与 SQL 全量
import 复用，保证与既有 exp_r36 出证逐键可比。

用法::

    python scripts/backtest/exp_ic_evidence.py --out docs/_working/kimi_audit/exp_evidence/exp_ic_evidence_ds271.yaml
"""
from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.backtest import eval_exp_expectations as ev  # noqa: E402  口径真源，只 import 不复制

# IS' 月数分母（exp_r36：2019-01~2021-12=36；覆盖率口径=ev._seg 的 coverage_ratio）
_IS_MONTHS_TOTAL = 36
# exp03 修正广度：研报级 EPS 直接源（裁定 #338④ A 段证据链；confidence='high' 即
# exp_grade=='high' 入聚合——high-only 铁律在查询层显式生效，mid/low 物理不入）
# 首月月末 2019-01 的 63 自然日回看窗 + 缓冲 → 2018-01-01 起
_PDF_FROM = "2018-01-01"
# 一致预期月度分块加载窗（ev.load_consensus_fy1 同构分块；上界 2022-03 覆盖 IS' 末月
# 快照 + exp06 60td 回看全在 2018 起；修复源 B 段 2026-07+ 与本出证无关不拉）
_CONS_YM_LO = (2018, 1)
_CONS_YM_HI = (2022, 3)

# 出证件 verdict 常量（诚实三态：判读二值 + 结构不可判）
VERDICT_GREEN = "GREEN"
VERDICT_RED = "RED"
VERDICT_NOT_EVALUABLE = "NOT_EVALUABLE"

# 裁定 #338④ 逐字引用（真源=docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml，
# commit 08e09187a2；改此处不改登记=伪造，禁）
RULING_338_4_VERBATIM = (
    "④DS-271（DS-275 consensus_daily_repaired）EXP 复评三口径预注册：IS 窗=A 案"
    "（2019-2021 共 36 月窗缩先行出证+显著标注窗缩，2022+ 修复证据补齐后全窗复跑）；"
    "mid 不入聚合（守 high-only 铁律，mid/low 留档作诊断与反向核验）；切换规则="
    "switch_gate=Owner 不变，机器侧双轨并跑（DS-229 消费方零改动）累计不少于 4 周对数后"
    "提请 Owner 验收切换。本条解阻 WO-⑤-12 EXP 族出证。")
WINDOW_SHRINK_MARKER = "窗缩"  # 显著标注（裁定原文用词，禁替换为"截断/缩短"等近义词）

# 旧口径既有出证对照（只读引用，不改旧件；真源=logs/experiment_tracking_fallback/*.json
# 与 factor_registry FCT-EXP-002 evidence 字段）
LEGACY_COMPARISON = {
    "exp02": {
        "run": "EXP-FACTOR-EVAL-004（logs/experiment_tracking_fallback/exp02_eval_run1_r36_20260916.json）",
        "result": "not_evaluable（DS-275 eps_std 结构性不可得，分歧归一分母恒 0）",
    },
    "exp04": {
        "run": "exp04_eval_run1_r36_20260916.json",
        "result": "IS' n_months=33 ic_mean=0.0363 t_p=0.02505（未达 |t|>3.0）",
    },
    "exp06": {
        "run": "exp06_eval_run1_r36_20260916.json",
        "result": "IS' n_months=36 ic_mean=-0.0191 t_p=0.19403（未达 |t|>3.0）",
    },
    "note": "旧件一律不改；本件同协议（exp_r36@DS-275）重跑应与旧数在统计核路径上一致，"
            "差异只可能来自数据增量（修复表重建批次）或本件新增的 exp01/exp03 腿。",
}

QueryFn = Callable[..., str]


def _ch_query(sql: str, timeout: int = 60) -> str:
    """CH 读注入缝：生产走 ch_reader 正门（DatabaseService 体系），测试注入 fake。"""
    from zephyr.data import ch_reader  # 运行时导入保缝可注入

    return ch_reader.query(sql, timeout=timeout)


# —— SQL 常量区（NO-BARE-SQL；评估器已有口径的 SQL 从 ev import，本件只新增 pdf 查询）——
from zephyr.data.table_registry import get_registry  # noqa: E402

_TBL_REPAIRED = get_registry().table("fund_consensus_daily_repaired")
_TBL_PDF = get_registry().table("pdf_forecast_extracted")

_SQL_PDF_HIGH = (
    "SELECT symbol, publish_date, forecast_year, toFloat64(eps) AS eps "
    "FROM {table} FINAL "
    "WHERE confidence = 'high' AND eps IS NOT NULL "
    "AND publish_date >= toDate('{lo}') AND publish_date <= toDate('{hi}') "
    "FORMAT TSV")
_SQL_PDF_GRADES = (
    "SELECT confidence, count() FROM {table} FINAL "
    "GROUP BY confidence ORDER BY confidence FORMAT TSV")
_SQL_COUNT = "SELECT count() FROM {table} FINAL FORMAT TSV"
_SQL_SPAN = (
    "SELECT min(trade_date), max(trade_date), uniqExact(symbol) "
    "FROM {table} FINAL FORMAT TSV")


def _tsv_rows(tsv: str) -> list[list[str]]:
    """ch_reader TSV → 行数组（空串=零行；\\N 原样保留由调用方判）。"""
    if not tsv or not tsv.strip():
        return []
    return [ln.split("\t") for ln in tsv.strip().split("\n")]


def probe_tables(query: QueryFn = _ch_query) -> dict:
    """探表存在性与行数（工单 B 前置）；任何异常向上抛由 main 落零数据诚实件。"""
    repaired_rows = int(query(_SQL_COUNT.format(table=_TBL_REPAIRED)).strip())
    span = _tsv_rows(query(_SQL_SPAN.format(table=_TBL_REPAIRED)))
    grades = {r[0]: int(r[1]) for r in _tsv_rows(query(_SQL_PDF_GRADES.format(table=_TBL_PDF)))}
    pdf_rows = int(query(_SQL_COUNT.format(table=_TBL_PDF)).strip())
    return {
        "consensus_daily_repaired": {
            "table": _TBL_REPAIRED, "rows": repaired_rows,
            "span": [span[0][0], span[0][1]] if span else None,
            "symbols": int(span[0][2]) if span else None,
        },
        "pdf_forecast_extracted": {
            "table": _TBL_PDF, "rows": pdf_rows,
            "confidence_counts": {k: grades.get(k, 0) for k in ("high", "mid", "low")},
        },
    }


def load_consensus_fy1(query: QueryFn = _ch_query) -> pd.DataFrame:
    """DS-275 → fy1 快照长表（ev.load_consensus_fy1 同构，分块窗按 IS' 收窄零网减载）。

    列形状与评估器逐列一致：[symbol, td, fy, eps_consensus, eps_std, rating_mean, eps_mean]。
    """
    frames = []
    ym = _CONS_YM_LO
    while ym <= _CONS_YM_HI:
        y, m = ym
        last_day = [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28,
                    31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1]
        q = ev._SQL_CONSENSUS_MONTH.format(table=_TBL_REPAIRED, y=y, m=m, last_day=last_day)
        rows = _tsv_rows(query(q, timeout=300))
        if rows:
            frames.append(pd.DataFrame(rows, columns=["symbol", "td", "fy", "eps_consensus",
                                                      "eps_std", "rating_mean"]))
        ym = (y + 1, 1) if m == 12 else (y, m + 1)
    if not frames:
        raise RuntimeError(f"{_TBL_REPAIRED} fy1 快照为空")
    df = pd.concat(frames, ignore_index=True)
    df["td"] = pd.to_datetime(df["td"])
    df["fy"] = pd.to_numeric(df["fy"], errors="coerce")
    for c in ("eps_consensus", "eps_std", "rating_mean"):
        df[c] = pd.to_numeric(df[c].replace("\\N", np.nan), errors="coerce")
    df["eps_mean"] = df["eps_consensus"]  # 评估器口径（DS-229 同名派生）
    df = df[df["fy"] >= df["td"].dt.year].dropna(subset=["eps_consensus"])
    df = df.sort_values(["symbol", "td", "fy"]).drop_duplicates(["symbol", "td"], keep="first")
    return df.drop(columns=["fy"])


def load_calendar(query: QueryFn = _ch_query) -> list[str]:
    """交易日历（ev._SQL_CALENDAR 同款 SQL/口径）。"""
    return [ln.strip()[:10] for ln in query(ev._SQL_CALENDAR).strip().split("\n")]


def load_prices(needed_dates: list[str], query: QueryFn = _ch_query) -> pd.DataFrame:
    """需要日期全A收盘（ev._SQL_PRICES_DATES 同款，日期分块防 URL 超长）。"""
    frames = []
    for i in range(0, len(needed_dates), 50):
        chunk = needed_dates[i:i + 50]
        quoted = ",".join(f"'{d}'" for d in chunk)
        rows = _tsv_rows(query(ev._SQL_PRICES_DATES.format(quoted=quoted), timeout=300))
        if rows:
            frames.append(pd.DataFrame(rows, columns=["td", "symbol", "close"]))
    if not frames:
        raise RuntimeError("kline_daily 价格为空")
    px = pd.concat(frames, ignore_index=True)
    px["td"] = pd.to_datetime(px["td"])
    px["close"] = pd.to_numeric(px["close"], errors="coerce")
    return px


def load_report_coverage(mes: list[str], query: QueryFn = _ch_query) -> pd.DataFrame:
    """研报 90 自然日滚动覆盖计数（ev.load_report_coverage 同口径，注入缝版）。"""
    rows = _tsv_rows(query(ev._SQL_REPORTS, timeout=300))
    rep = pd.DataFrame(rows, columns=["symbol", "pub", "org"])
    rep["pub"] = pd.to_datetime(rep["pub"])
    rep = rep.sort_values(["symbol", "pub"])
    out = []
    for sym, g in rep.groupby("symbol", sort=False):
        pubs = g["pub"].values.astype("datetime64[D]")
        orgs = g["org"].to_numpy()
        for t in mes:
            ts = np.datetime64(pd.Timestamp(t), "D")
            lo = ts - np.timedelta64(89, "D")
            lf = int(np.searchsorted(pubs, lo, side="left"))
            rt = int(np.searchsorted(pubs, ts, side="right"))
            if rt <= lf:
                continue
            org_slice = orgs[lf:rt]
            n_orgs = pd.unique(org_slice[org_slice != ""]).size
            out.append({"td": pd.Timestamp(t), "symbol": sym,
                        "n_reports": rt - lf, "n_orgs": int(n_orgs)})
    if not out:
        return pd.DataFrame(columns=["td", "symbol", "n_reports", "n_orgs"])
    return pd.DataFrame(out)


def load_circ_mv_volume(needed_dates: list[str], query: QueryFn = _ch_query) -> tuple[pd.DataFrame, pd.DataFrame]:
    """circ_mv（stock_indicator）与 volume（kline_daily）长表（ev 同款 SQL）。"""
    mv_frames, vol_frames = [], []
    for i in range(0, len(needed_dates), 50):
        chunk = needed_dates[i:i + 50]
        quoted = ",".join(f"'{d}'" for d in chunk)
        rows = _tsv_rows(query(ev._SQL_MV_DATES.format(quoted=quoted), timeout=300))
        if rows:
            f = pd.DataFrame(rows, columns=["td", "symbol", "circ_mv"])
            f["td"] = pd.to_datetime(f["td"])
            f["circ_mv"] = pd.to_numeric(f["circ_mv"], errors="coerce")
            mv_frames.append(f)
        rows = _tsv_rows(query(ev._SQL_VOLUME_DATES.format(quoted=quoted), timeout=300))
        if rows:
            f = pd.DataFrame(rows, columns=["td", "symbol", "volume"])
            f["td"] = pd.to_datetime(f["td"])
            f["volume"] = pd.to_numeric(f["volume"], errors="coerce")
            vol_frames.append(f)
    if not mv_frames or not vol_frames:
        raise RuntimeError("stock_indicator/kline_daily 特征原料为空")
    return pd.concat(mv_frames, ignore_index=True), pd.concat(vol_frames, ignore_index=True)


def load_pdf_high_rows(query: QueryFn = _ch_query) -> pd.DataFrame:
    """pdf_forecast_extracted 置信档=high 的研报级 EPS（exp03 直接源；mid/low 不入聚合）。"""
    rows = _tsv_rows(query(_SQL_PDF_HIGH.format(table=_TBL_PDF, lo=_PDF_FROM,
                                                hi=ev._PROTOCOLS["exp_r36"]["is"][1])))
    if not rows:
        raise RuntimeError(f"{_TBL_PDF} high 置信行为空")
    df = pd.DataFrame(rows, columns=["symbol", "publish_date", "forecast_year", "eps"])
    df["publish_date"] = pd.to_datetime(df["publish_date"])
    df["forecast_year"] = pd.to_numeric(df["forecast_year"], errors="coerce")
    df["eps"] = pd.to_numeric(df["eps"], errors="coerce")
    return df.dropna(subset=["eps"])


def factor_panel_exp01(cons_fy1: pd.DataFrame, px_close: pd.DataFrame,
                       cal: list[str], mes: list[str]) -> pd.DataFrame:
    """EXP-01 一致预期 EP：fy1 eps_consensus / close（月末截面，exp01_consensus_ep 口径）。"""
    from zephyr.factor.expectations import exp01_consensus_ep

    eps_wide = cons_fy1.pivot(index="td", columns="symbol", values="eps_consensus").reindex(
        pd.to_datetime(cal)).sort_index()
    out = []
    for t in mes:
        ts = pd.Timestamp(t)
        if ts not in eps_wide.index or ts not in px_close.index:
            continue
        ep = exp01_consensus_ep(eps_wide.loc[ts], px_close.loc[ts])
        out.append(pd.DataFrame({"td": ts, "symbol": ep.index, "f": ep.values}))
    if not out:
        return pd.DataFrame(columns=["td", "symbol", "f"])
    return pd.concat(out, ignore_index=True).dropna()


def factor_panel_exp03(pdf_high: pd.DataFrame, cons_fy1: pd.DataFrame,
                       cal: list[str], mes: list[str]) -> pd.DataFrame:
    """EXP-03 修正广度：逐标的 exp03_revision_breadth（研报级 high EPS × 修复源 fy1 一致预期
    as-of 对齐），事件网格 → 月末"最后事件值≤t"快照（PIT：t 日只见发布日≤t 的研报）。

    窗口=函数缺省 63 自然日（Gleason-Lee 上调占比，因子定义真源=expectations.py，
    本件禁复制公式）。
    """
    from zephyr.factor.expectations import exp03_revision_breadth

    cal_idx = pd.to_datetime(cal)
    cons_by_sym = {s: g.set_index("td")["eps_consensus"].sort_index().rename_axis(None)
                   for s, g in cons_fy1.groupby("symbol")}
    out = []
    for sym, g in pdf_high.groupby("symbol"):
        cons = cons_by_sym.get(sym)
        if cons is None or cons.empty:
            continue
        breadth = exp03_revision_breadth(
            g[["publish_date", "forecast_year", "eps"]], cons, window_days=63)
        if breadth.empty:
            continue
        # 同标的同发布日多份研报 → 事件网格重复标签；rolling("63D") 对同日各行的
        # 窗口一致（窗=截至本行事件日），keep="last" 去重值不变（首跑零数据件教训：
        # 2026-09-18 reindex on duplicate labels 崩=出证中断）
        breadth = breadth[~breadth.index.duplicated(keep="last")]
        snap = breadth.reindex(cal_idx, method="ffill").reindex(pd.to_datetime(mes))
        out.append(pd.DataFrame({"td": snap.index, "symbol": sym, "f": snap.values}))
    if not out:
        return pd.DataFrame(columns=["td", "symbol", "f"])
    return pd.concat(out, ignore_index=True).dropna()


def seg_with_t(icdf: pd.DataFrame, is_end: str, total_months: int) -> dict:
    """IS' 段统计 = ev._seg（口径零漂移）+ t 统计量（|t|>3.0 门槛的判定数）。

    ev._seg 只出 t_p 不出 t_stat，exp_r36 显著性规则是 |t|>3.0（非 p 阈），
    故同一 ic 序列补算 scipy ttest_1samp 的 statistic（与评估器同一检验）。
    """
    d = icdf[icdf["td"] <= is_end]
    seg = ev._seg(d, total_months)
    seg["rank_ic_mean"] = seg.get("ic_mean")  # IC=Spearman 秩相关 → 同值双标（禁两口径）
    if seg.get("ic_mean") is not None and len(d) >= 2:
        tp = stats.ttest_1samp(d["ic"], 0.0)
        seg["t_stat"] = round(float(tp.statistic), 4)
        seg["sig_rule_met"] = bool(abs(tp.statistic) > 3.0)
    else:
        seg["t_stat"] = None
        seg["sig_rule_met"] = False
    return seg


def judge(seg: dict) -> tuple[str, list[str]]:
    """exp_r36 判读（预注册判据禁挪）：|IC|>=0.02 & |t|>3.0 & 月覆盖率>=0.60。"""
    proto = ev._PROTOCOLS["exp_r36"]
    if seg.get("ic_mean") is None:
        return VERDICT_NOT_EVALUABLE, ["IS' 段样本不足（n_months<12 或截面全空）"]
    reasons = []
    if abs(seg["ic_mean"]) < proto["ic_min"]:
        reasons.append(f"|IC|={abs(seg['ic_mean']):.4f} < {proto['ic_min']}（效应量地板不动）")
    if not seg.get("sig_rule_met"):
        reasons.append(f"|t|={abs(seg.get('t_stat') or 0):.4f} 未超 3.0"
                       "（Harvey-Liu-Zhu 收紧门槛）")
    cov = seg.get("coverage_ratio")
    if cov is None or cov < proto["coverage_min"]:
        reasons.append(f"月覆盖率={cov} < {proto['coverage_min']:.0%}（分母=IS' 36 月）")
    return (VERDICT_GREEN, []) if not reasons else (VERDICT_RED, reasons)


def not_evaluable_entry(factor: str, reason: str) -> dict:
    """exp02/exp05 结构性不可判出证（评估器 :50-52 判据引用，禁跑出假 IC）。"""
    proto = ev._PROTOCOLS["exp_r36"]
    return {"status": VERDICT_NOT_EVALUABLE, "reason": reason,
            "evidence_class": proto["evidence_class"],
            "promotion_authority": proto["promotion_authority"],
            "is_window": list(proto["is"]), "oos_window": None}


_NOT_EVALUABLE_REASONS = {
    "exp02": "DS-275 的 eps_std 结构性不可得（A 段=窗口聚合值不经原始离散度、B 段=源快照"
             "本身是聚合值），表内恒 0；exp02 分歧归一项分母为 0 ⇒ 因子退化（评估器"
             "eval_exp_expectations.py 已 fail-closed 钉死，0 不是零分歧）",
    "exp05": "同 exp02 根因：exp05_dispersion=eps_std/|eps_mean|，修复源 eps_std 恒 0 ⇒ "
             "因子全市场恒 0 零方差，截面 Spearman 无定义（跑出一个常数因子的 IC 是对"
             "不存在数据的断言）",
}


def build_evidence(query: QueryFn = _ch_query) -> tuple[dict, list[str], int]:
    """六因子聚合出证主流程（纯编排，判据全在 ev/预注册协议里）。"""
    proto = ev._PROTOCOLS["exp_r36"]
    is_lo, is_hi = proto["is"]

    cons = load_consensus_fy1(query)
    cal = load_calendar(query)
    mes = ev.month_ends(cal, is_lo, proto["panel_hi"])
    is_total = len(mes)  # exp_r36 覆盖率分母=IS' 月数（评估器同款口径）
    cal_pos = {d: i for i, d in enumerate(cal)}
    fwd_map = {d: (cal[cal_pos[d] + ev._FWD] if cal_pos[d] + ev._FWD < len(cal) else None)
               for d in mes}
    needed = set(mes) | {fwd_map[t] for t in mes if fwd_map[t]}
    for t in mes:
        j = cal_pos[t]
        # 换手 20 日窗（t-1..t-19）+ 63td 动量回看：评估器 main exp04 分支同款日期白名单；
        # t-20 = build_ic_table 动量对照列 mom_ic 的 k=20 回看。缺任何一段 → 特征全 NaN →
        # 残差全 NaN → 因子面板空（首跑 exp04 零行教训 2026-09-18）
        for off in list(range(1, 20)) + [20, 63]:
            jj = j - off
            if jj >= 0:
                needed.add(cal[jj])
    px = load_prices(sorted(needed), query)
    px_close = px.pivot(index="td", columns="symbol", values="close").reindex(
        pd.to_datetime(cal)).sort_index()

    # exp01：一致预期 EP
    fac1 = factor_panel_exp01(cons, px_close, cal, mes)
    ic1 = ev.build_ic_table(fac1.pivot(index="td", columns="symbol", values="f").sort_index(),
                            px_close, mes, fwd_map, k=20)
    seg1 = seg_with_t(ic1, is_hi, is_total)
    v, rs = judge(seg1)

    # exp03：修正广度（pdf high 研报级 EPS）
    pdf_high = load_pdf_high_rows(query)
    fac3 = factor_panel_exp03(pdf_high, cons, cal, mes)
    ic3 = ev.build_ic_table(fac3.pivot(index="td", columns="symbol", values="f").sort_index(),
                            px_close, mes, fwd_map, k=20)
    seg3 = seg_with_t(ic3, is_hi, is_total)
    v3, rs3 = judge(seg3)

    # exp04：异常覆盖（研报计数类，评估器纯核复用）
    cov = load_report_coverage(mes, query)
    mv, vol = load_circ_mv_volume(sorted(needed), query)
    mv_wide = mv.pivot(index="td", columns="symbol", values="circ_mv").reindex(
        pd.to_datetime(cal)).sort_index()
    vol_wide = vol.pivot(index="td", columns="symbol", values="volume").reindex(
        pd.to_datetime(cal)).sort_index()
    chars = ev.build_char_panel(mes, px_close, mv_wide, vol_wide)
    fac4 = ev.compute_factor_exp04(cov, chars)
    ic4 = ev.build_ic_table(fac4.pivot(index="td", columns="symbol", values="f").sort_index(),
                            px_close, mes, fwd_map, k=20)
    seg4 = seg_with_t(ic4, is_hi, is_total)
    v4, rs4 = judge(seg4)

    # exp06：评级动量（k=60 单配置，评估器同款）
    fac6 = ev.compute_factor_exp06(cons, k=60)
    ic6 = ev.build_ic_table(fac6.pivot(index="td", columns="symbol", values="f").sort_index(),
                            px_close, mes, fwd_map, k=20)
    seg6 = seg_with_t(ic6, is_hi, is_total)
    v6, rs6 = judge(seg6)

    factors = {
        "exp01_consensus_ep": {**seg1, "verdict": v, "red_reasons": rs,
                               "oos": {"status": "not_evaluable",
                                       "reason": "协议无 OOS 窗（exp_r36 结构性）"}},
        "exp02_revision_momentum": not_evaluable_entry("exp02", _NOT_EVALUABLE_REASONS["exp02"]),
        "exp03_revision_breadth": {**seg3, "verdict": v3, "red_reasons": rs3,
                                   "oos": {"status": "not_evaluable",
                                           "reason": "协议无 OOS 窗（exp_r36 结构性）"},
                                   "input_note": "pdf_forecast_extracted confidence='high' 研报级"
                                                 "EPS 直接源（mid/low 不入聚合）；月末快照=事件"
                                                 "网格最后事件值≤t"},
        "exp04_anomaly_coverage": {**seg4, "verdict": v4, "red_reasons": rs4,
                                   "oos": {"status": "not_evaluable",
                                           "reason": "协议无 OOS 窗（exp_r36 结构性）"}},
        "exp05_dispersion": not_evaluable_entry("exp05", _NOT_EVALUABLE_REASONS["exp05"]),
        "exp06_rating_momentum": {**seg6, "verdict": v6, "red_reasons": rs6,
                                  "oos": {"status": "not_evaluable",
                                          "reason": "协议无 OOS 窗（exp_r36 结构性）"}},
    }
    return factors, mes, is_total


def render_yaml(probe: dict, factors: dict, mes: list[str], is_total: int) -> str:
    """出证 YAML 组装（caliber 段逐字引用裁定 + 窗缩标注 + 三档计数）。"""
    run_ts = datetime.now(ZoneInfo("UTC")).isoformat(timespec="seconds")
    proto = ev._PROTOCOLS["exp_r36"]
    grades = probe["pdf_forecast_extracted"]["confidence_counts"]
    evaluable = {k: v for k, v in factors.items() if "verdict" in v}
    greens = [k for k, v in evaluable.items() if v["verdict"] == VERDICT_GREEN]
    lines = [
        "# WO-⑤-12 EXP 族 IC 出证（裁定 #338④ 口径执行端；统计核/SQL 全量复用",
        "# scripts/backtest/eval_exp_expectations.py——评估器=口径真源，本件零复制判据）",
        "evidence_id: exp_ic_evidence_ds271",
        f"run_ts: '{run_ts}'",
        "work_order: WO-⑤-12",
        "ruling: 裁定#338④（commit 08e09187a2）",
        "caliber:",
        "  ruling_338_4_verbatim: |",
        f"    {RULING_338_4_VERBATIM}",
        f"  window_shrink_marker: {WINDOW_SHRINK_MARKER}   # ← 显著标注（裁定原文用词）",
        f"  is_window: [{proto['is'][0]}, {proto['is'][1]}]",
        "  is_window_note: 窗缩——主协议 IS 2019-2023 共 60 月在修复源上仅 36 月真覆盖；"
        "2022+ 缺证据不复跑，全窗复跑待修复证据补齐（裁定 #338④ A 案）",
        f"  oos_window: null   # OOS' 结构不存在 → 全部因子显式 not_evaluable（禁写成 0）",
        f"  protocol: exp_r36",
        f"  significance_rule: \"{proto['sig_rule']}（t p<0.05 收紧；SE 放大 "
        f"{proto['se_inflation_vs_primary']} 倍=sqrt(60/36)）\"",
        f"  ic_min: {proto['ic_min']}   # 效应量地板不动",
        "  coverage_rule: '月覆盖率 coverage_ratio=n_months/36>=0.60（coverage_mean=月均截面"
        "股票数计数，禁与百分比门直比）'",
        "  ic_definition: Spearman 截面秩相关（评估器 build_ic_table 口径）→ IC=秩IC 同值"
        "（rank_ic_mean 双标零漂移）",
        "  aggregation: high-only（exp_grade 即 pdf_forecast_extracted.confidence；mid/low "
        "只出诊断计数不入主统计）",
        "  promotion_authority: none   # preliminary-coverage-limited，永不产出晋级/否决结论",
        "probe:",
        f"  consensus_daily_repaired: {{table: {probe['consensus_daily_repaired']['table']}, "
        f"rows: {probe['consensus_daily_repaired']['rows']}, "
        f"span: {probe['consensus_daily_repaired']['span']}, "
        f"symbols: {probe['consensus_daily_repaired']['symbols']}}}",
        f"  pdf_forecast_extracted: {{table: {probe['pdf_forecast_extracted']['table']}, "
        f"rows: {probe['pdf_forecast_extracted']['rows']}}}",
        "  exp_grade_counts:   # high/mid/low 三档计数（mid/low=诊断留档，不入主统计）",
        f"    high: {grades.get('high', 0)}   # ← 入聚合档",
        f"    mid: {grades.get('mid', 0)}    # ← 诊断计数",
        f"    low: {grades.get('low', 0)}     # ← 诊断计数（重建聚合铁律本就不入）",
        f"  is_months_total: {is_total}",
        f"  months_observed: {len(mes)}",
        "factors:",
    ]
    for k, v in factors.items():
        lines.append(f"  {k}:")
        if "verdict" in v:
            lines.append(f"    verdict: {v['verdict']}")
            lines.append(f"    n_months: {v.get('n_months')}")
            lines.append(f"    rank_ic_mean: {v.get('ic_mean')}   # =ic_mean（Spearman 秩相关）")
            lines.append(f"    t_stat: {v.get('t_stat')}")
            lines.append(f"    t_p: {v.get('t_p')}")
            lines.append(f"    coverage_mean: {v.get('coverage_mean')}   # 月均截面股票数（计数）")
            lines.append(f"    coverage_ratio: {v.get('coverage_ratio')}   # 月覆盖率（分母 36）")
            lines.append(f"    mom_ic_mean: {v.get('mom_ic_mean')}")
            if "oos" in v:
                lines.append(f"    oos: not_evaluable（exp_r36 协议无 OOS 窗，结构性）")
            if v.get("red_reasons"):
                lines.append("    red_reasons:")
                lines += [f"      - {r}" for r in v["red_reasons"]]
        else:
            lines.append(f"    status: {v['status']}")
            lines.append(f"    reason: {v['reason']}")
        lines.append(f"    promotion_authority: {v.get('promotion_authority', 'none')}")
    lines += [
        "comparison_with_legacy:   # 旧口径既有出证对照（只读引用，不改旧件）",
    ]
    for k, v in LEGACY_COMPARISON.items():
        if k == "note":
            lines.append(f"  note: {v}")
        else:
            lines.append(f"  {k}: {{run: {v['run']}, result: {v['result']}}}")
    lines += [
        "verdict_summary:",
        f"  evaluable_factors: {sorted(evaluable)}",
        f"  green: {greens if greens else '无'}",
        f"  not_evaluable: {sorted(k for k, v in factors.items() if 'verdict' not in v)}",
        "  overall: "
        + ("GREEN（预注册判据全过；仍无晋级权=evidence_class 限制）" if greens
           else "RED/NOT_EVALUABLE（初筛无达标信号或结构不可判；promotion_authority=none，"
                "本件不构成晋级/否决结论）"),
    ]
    return "\n".join(lines) + "\n"


def render_zero_data(reason: str) -> str:
    """零数据诚实件：表空/不可达时如实记录不可考，禁造数（结构完整可独立归档）。"""
    run_ts = datetime.now(ZoneInfo("UTC")).isoformat(timespec="seconds")
    proto = ev._PROTOCOLS["exp_r36"]
    return (
        "# WO-⑤-12 EXP 族 IC 出证——零数据诚实件（表空/不可达，禁造数）\n"
        "evidence_id: exp_ic_evidence_ds271\n"
        f"run_ts: '{run_ts}'\n"
        "work_order: WO-⑤-12\n"
        "ruling: 裁定#338④（commit 08e09187a2）\n"
        "status: NOT_EVALUABLE\n"
        "zero_data: true\n"
        f"reason: {reason}\n"
        "caliber:\n"
        "  ruling_338_4_verbatim: |\n"
        f"    {RULING_338_4_VERBATIM}\n"
        f"  window_shrink_marker: {WINDOW_SHRINK_MARKER}\n"
        f"  is_window: [{proto['is'][0]}, {proto['is'][1]}]\n"
        "  is_window_note: 窗缩（裁定 #338④ A 案）；本次因零数据未执行，零造数\n"
        "  promotion_authority: none\n"
        "factors: {}\n"
    )


def _fail_reason(prefix: str, exc: BaseException) -> str:
    """零数据件 reason：异常摘要 + 尾栈一帧（可自诊断，禁只写"失败"两字）。"""
    import traceback

    tb = traceback.extract_tb(exc.__traceback__)
    last = tb[-1] if tb else None
    loc = f"{Path(last.filename).name}:{last.lineno} {last.name}" if last else "?"
    return (f"{prefix}（{type(exc).__name__}: {str(exc)[:200]} @ {loc}）——"
            "数据不可考，零造数；修复后重跑本件即可")


def main() -> int:
    ap = argparse.ArgumentParser(description="EXP 六因子 IC 出证（WO-⑤-12，裁定 #338④ 口径）")
    ap.add_argument("--out", default=str(ROOT / "docs" / "_working" / "kimi_audit"
                                         / "exp_evidence" / "exp_ic_evidence_ds271.yaml"),
                    help="YAML 出证路径（缺省=工单指定真源路径）")
    args = ap.parse_args()

    try:
        probe = probe_tables()
    except Exception as exc:  # noqa: BLE001 — 探表失败→零数据诚实件（不造数）
        text = render_zero_data(_fail_reason("探表失败", exc))
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"WROTE {args.out} (zero-data)")
        return 0

    try:
        factors, mes, is_total = build_evidence()
    except Exception as exc:  # noqa: BLE001 — 加载失败→零数据诚实件（不造数）
        text = render_zero_data(_fail_reason("评估加载失败", exc))
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"WROTE {args.out} (zero-data)")
        return 0

    Path(args.out).write_text(render_yaml(probe, factors, mes, is_total), encoding="utf-8")
    print(f"WROTE {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
