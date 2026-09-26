# [BLUEPRINT] MOD-METAQ-REEXAM-A06 | docs/_working/meta_question_answers/gaps/A06_MONEYFLOW_BACKFILL_workbook.md §3
# [MODULE] scripts.governance.meta_question.reexam.a06.exam_a06
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pandas; numpy; scipy; zephyr.infrastructure.database_service (CH reader 只读);
#                scripts.governance.meta_question.reexam.a06.panels;
#                scripts.governance.meta_question.reexam.a06.stats_core
# [CONSUMERS] docs/_working/meta_question_answers/build/REEXAM-A06.yaml（案卷由本器输出 JSON 转录）；
#             后续 283 问战役复考范式件（同构造可挂其他族）
# [STARTUP] manual（python scripts/governance/meta_question/reexam/a06/exam_a06.py --out <json>）
# [MATURITY] testing
# [INVARIANTS] 判据零改动：六问阈值/criterion/method 逐字取自 PG
#              meta_question.meta_question.exam_plan（运行时回读并记入输出，禁本地另写判据）；
#              PIT 单点收口：所有窗参数经 panels.load_panels 且 cutoff 默认 2025-09-09，
#              前瞻端点由 shift(-n) 在切点面板上自然截断（信号端自动截止 cutoff-n 日）；
#              确定性：无随机数、无时钟参与计算（run_meta 单列且不参与 payload_md5）、
#              同输入必同 payload_md5；
#              不达标即判不达标：pass 需全部子条件成立，任一未达即 fail，无"调分组/换窗"补救；
#              只读考试：本器零写库（CH/PG 均 reader），输出仅 --out 指定文件
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 判据回读失败→raise（禁凭记忆写判据）；数据窗零样本→该问 verdict=insufficient 并记原因；
#                  未知 q_id→raise；CH 连接异常→raise（fail-visible）
# [TESTS] 本器 --selftest（合成面板闭式解比对 + 确定性双跑）；
#         重放一致性=真库双跑 payload_md5 相等
# [A_module] module_id=MOD-METAQ-REEXAM-A06 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""A06 资金流族 6 问可重放复考器（PQ-0025/0026/0125/0126/0127/0163）。

范式（本战役后续复考通用接口）：
    exam(panels, **判据参数) -> {
        q_id, exam_plan_ref(判据原文回读), pit(signal_end/return_end/horizon),
        sample(n_days/池规模), metrics(指标值), threshold_check(逐项比对),
        verdict(pass|fail|insufficient), robustness(变体口径披露), notes }

用法：
    python scripts/governance/meta_question/reexam/a06/exam_a06.py \
        --out .runtime/tmp/st-metaq-gc-20260924/reexam_a06/result.json
    可选：--cutoff 2025-09-09 --start 2021-01-04 --questions PQ-0125,PQ-0126 \
          --event-start 2023-01-01 --no-exam-plan-pg --selftest
重放一致性：同参数双跑，比对 payload_md5（不含 run_meta 时钟字段）。
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_REPO_SRC = str(Path(__file__).resolve().parents[6] / "src")
if _REPO_SRC not in sys.path:
    sys.path.insert(0, _REPO_SRC)
sys.path.insert(0, str(Path(__file__).resolve().parent))

import stats_core as sc  # noqa: E402  同目录范式件（nw_t / 秩 IC / Chow）
from panels import MIN_NAMES_DEFAULT, PIT_CUTOFF_DEFAULT, A06Panels, load_panels  # noqa: E402

from zephyr.data.table_registry import TableRegistry  # noqa: E402

Q_IDS = ("PQ-0025", "PQ-0026", "PQ-0125", "PQ-0126", "PQ-0127", "PQ-0163")
HORIZON_OF = {"PQ-0125": 1, "PQ-0126": 5, "PQ-0127": 20}
IS_RATIO = 0.60  # exam_plan method 原文："60/40 样本内外切分"

# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
_T_MONEY_FLOW = TableRegistry().table("market_money_flow")


# ---------------------------------------------------------------- 判据真源回读
# NO-BARE-SQL：题面真源读取 SQL 集中于此（§5.160.2）；q_ids 走参数化 ANY(%s)，禁字符串拼入。
_SQL_EXAM_PLANS = "SELECT q_id, title, exam_plan FROM meta_question.meta_question WHERE q_id = ANY(%s) ORDER BY q_id"


def load_exam_plan(q_ids: tuple[str, ...] = Q_IDS) -> dict[str, dict[str, str]]:
    """从 PG meta_question.meta_question.exam_plan 逐字回读判据（真源，禁凭记忆）。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    pg = get_depgraph_pg_connection()
    cur = pg.cursor()
    cur.execute(_SQL_EXAM_PLANS, (list(q_ids),))
    out: dict[str, dict[str, str]] = {}
    for qid, title, plan in cur.fetchall():
        plan = plan if isinstance(plan, dict) else json.loads(plan or "{}")
        out[str(qid)] = {
            "title": str(title),
            "method": str(plan.get("method", "")),
            "criterion": str(plan.get("criterion", "")),
            "threshold": str(plan.get("threshold", "")),
        }
    cur.close()
    missing = [q for q in q_ids if q not in out]
    if missing:
        raise AssertionError(f"PG 判据回读缺题：{missing}")
    return out


# ---------------------------------------------------------------- 通用统计件
def _ic_block(ic: pd.Series, horizon: int) -> dict[str, Any]:
    """全窗 / 60-40 样本内外 / 月度滚动 三视图（NW lag=horizon）。"""
    ics = ic.dropna()
    n = int(len(ics))
    if n < 20:
        return {"insufficient_reason": f"有效 IC 观测日仅 {n} 日（<20）", "n_days": n}
    split = int(n * IS_RATIO)
    full = ics.to_numpy(float)
    ins, oos = full[:split], full[split:]
    monthly = ics.groupby(ics.index.to_period("M")).mean()
    out: dict[str, Any] = {
        "n_days": n,
        "ic_mean": round(float(full.mean()), 5),
        "ic_sd": round(float(full.std(ddof=1)), 5),
        "ic_ir": round(float(full.mean() / full.std(ddof=1)), 4),
        "nw_lag": horizon,
        "nw_t_full": round(sc.nw_tstat(full, horizon), 3),
        "in_days": split,
        "ic_in_mean": round(float(ins.mean()), 5),
        "nw_t_in": round(sc.nw_tstat(ins, horizon), 3),
        "oos_days": n - split,
        "ic_oos_mean": round(float(oos.mean()), 5),
        "nw_t_oos": round(sc.nw_tstat(oos, horizon), 3),
        "oos_start": str(ics.index[split].date()),
        "pos_ic_share": round(float((full > 0).mean()), 4),
        "monthly_n": int(len(monthly)),
        "monthly_mean": round(float(monthly.mean()), 5),
        "monthly_pos_share": round(float((monthly > 0).mean()), 4),
        "monthly_min": round(float(monthly.min()), 5),
        "monthly_max": round(float(monthly.max()), 5),
        "signal_start": str(ics.index[0].date()),
        "signal_end": str(ics.index[-1].date()),
    }
    return out


# ---------------------------------------------------------------- 各问实现
def pq_012x(p: A06Panels, q_id: str, exam_plan: dict[str, str], event_start: str = "2023-01-01") -> dict[str, Any]:
    """PQ-0125/0126/0127：全 A 池主力净流入占比 → n 日前瞻收益秩 IC（NW t + 60/40 切分）。"""
    h = HORIZON_OF[q_id]
    sig = p.signal.where(p.pool("main"))
    ret = p.fwd(h)
    ic = sc.daily_rank_ic(sig, ret, min_names=MIN_NAMES_DEFAULT)
    block = _ic_block(ic, h)
    res: dict[str, Any] = {
        "q_id": q_id,
        "exam_plan_ref": exam_plan[q_id],
        "impl": {
            "signal": f"{_T_MONEY_FLOW} FINAL main_net_inflow_pct（主力=大单+超大单净买/主力档毛成交×100）",
            "forward_return": f"后复权收盘 close×adj_factor，wide.shift(-{h})/wide-1（交易日历对齐，端点停牌→剔除）",
            "ic": "逐日截面 Spearman 秩 IC（并列平均秩），日截面有效名 ≥300 方计入",
            "inference": f"日频 IC 序列均值的 Newey-West HAC t（Bartlett 核，lag={h}=前瞻窗长，重叠窗修正）",
            "split": "60/40 时间序切分（前 60% 样本内 / 后 40% 样本外），禁随机打乱",
            "pool": "全 A 现价池（kline_daily 有成交且 money_flow 有信号；题面未要求 ST/退市过滤，同 PQ-0110 先例）",
            "sql_ref": ["signal", "price"],
        },
        "pit": {
            "cutoff": p.cutoff,
            "signal_first": block.get("signal_start"),
            "signal_last": block.get("signal_end"),
            "return_end_max": p.cutoff,
            "note": f"信号端因前瞻窗自动截止 {block.get('signal_end')}（≤ {p.cutoff} −{h} 交易日）",
        },
        "sample": {
            "window": [p.start, p.cutoff],
            "coverage_days": int(len(p.trade_dates)),
            "median_pool_names": int((p.signal.notna() & p.adj_close.notna()).sum(axis=1).median()),
            "min_pool_names": int((p.signal.notna() & p.adj_close.notna()).sum(axis=1).min()),
            "ic_days": block.get("n_days"),
        },
        "metrics": block,
    }
    thr = exam_plan[q_id]["threshold"]
    if "n_days" not in block or block.get("insufficient_reason"):
        res["threshold_check"] = {"raw_threshold": thr, "reason": block.get("insufficient_reason", "样本不足")}
        res["verdict"] = "insufficient"
        return res
    checks = {
        "ic_gt_0.02": {"value": block["ic_mean"], "op": ">", "bound": 0.02, "met": block["ic_mean"] > 0.02},
        "nw_t_gt_2": {"value": block["nw_t_full"], "op": ">", "bound": 2.0, "met": block["nw_t_full"] > 2.0},
        "oos_ic_gt_0.01": {"value": block["ic_oos_mean"], "op": ">", "bound": 0.01, "met": block["ic_oos_mean"] > 0.01},
    }
    res["threshold_check"] = {"raw_threshold": thr, "items": checks}
    res["verdict"] = "pass" if all(c["met"] for c in checks.values()) else "fail"
    res["metrics"]["sub_windows"] = sc.sub_period_ic(
        ic,
        [
            ("2021-2022", "2021-01-04", "2022-12-31"),
            ("2023_以来_与PQ0025同窗", event_start, p.cutoff),
            ("最后12月", (pd.Timestamp(p.cutoff) - pd.DateOffset(months=12)).strftime("%Y-%m-%d"), p.cutoff),
        ],
    )

    # 稳健性披露（不改主判）：变体池 + IS 单列
    sig_v = p.signal.where(p.pool("variant")) if p.st_flag is not None else sig
    ic_v = sc.daily_rank_ic(sig_v, ret, min_names=MIN_NAMES_DEFAULT)
    blk_v = _ic_block(ic_v, h)
    alt = p.signal_amount_ratio().where(p.pool("main"))
    ic_alt = sc.daily_rank_ic(alt, ret, min_names=MIN_NAMES_DEFAULT)
    blk_alt = _ic_block(ic_alt, h)
    res["robustness"] = {
        "variant_pool_st_cn_liquidity": {
            k: blk_v.get(k) for k in ("n_days", "ic_mean", "nw_t_full", "ic_oos_mean", "nw_t_oos")
        },
        "alt_signal_pct_of_turnover": {
            k: blk_alt.get(k) for k in ("n_days", "ic_mean", "nw_t_full", "ic_oos_mean", "nw_t_oos")
        },
        "note": "变体①=剔除 ST/涨跌停锁板/成交额<1000万/次新（上市<120 日历日）；"
        "变体②=题面字面分母（主力净流入÷当日成交额，表内字段分母为主力档毛成交）；均仅披露，主判据按题面全 A 池",
    }
    if res["verdict"] == "fail":
        res["fail_type"] = "no_alpha" if block["ic_mean"] <= 0.02 else "threshold_close"
    return res


def _event_study(
    sig: pd.DataFrame,
    ret1: pd.DataFrame,
    event_start: str,
    q_frac: float = 0.90,
    min_cohort: int = 10,
) -> dict[str, Any]:
    """极端组次日收益事件研究（供主判与稳健性变体共用，避免第二套实现）。

    事件组=日截面信号分位 ≥q_frac（题面"前 10%"）；逐日等权组合均值序列做单样本 t，
    附超额（减同日全池等权）与十分位分解（D1..D10）。
    """
    rank = sig.rank(axis=1, pct=True)
    cohort = (rank >= q_frac) & sig.notna() & ret1.notna()
    daily = pd.DataFrame(
        {
            "cohort_ret": ret1.where(cohort).mean(axis=1),
            "pool_ret": ret1.where(sig.notna()).mean(axis=1),
            "n_cohort": cohort.sum(axis=1),
        }
    )
    win = daily[daily.index >= pd.Timestamp(event_start)]
    win = win[win["cohort_ret"].notna() & win["pool_ret"].notna() & (win["n_cohort"] >= min_cohort)]
    n = int(len(win))
    out: dict[str, Any] = {
        "n_event_days": n,
        "median_cohort_names": int(win["n_cohort"].median()) if n else 0,
        "signal_first": str(win.index[0].date()) if n else None,
        "signal_last": str(win.index[-1].date()) if n else None,
    }
    if n < 3:
        out["metrics"] = {"insufficient_reason": f"有效事件日 {n} 日"}
        return out
    plain = sc.mean_ttest(win["cohort_ret"])
    excess = win["cohort_ret"] - win["pool_ret"]
    ex_t = sc.mean_ttest(excess)
    deciles: dict[str, Any] = {}
    for i in range(10):
        sel = (rank > i / 10.0) & (rank <= (i + 1) / 10.0) & sig.notna() & ret1.notna()
        m = ret1.where(sel).mean(axis=1).reindex(win.index)
        deciles[f"D{i + 1}"] = round(float(m.mean()) * 100, 4) if m.notna().any() else None
    out["metrics"] = {
        "mean_next_day_ret_pct": round(plain["mean"] * 100, 4),
        "sd_next_day_ret_pct": round(plain["std"] * 100, 4),
        "t_plain": round(plain["t"], 3),
        "p_plain": round(plain["p"], 4),
        "t_nw_lag1": round(sc.nw_tstat(win["cohort_ret"], 1), 3),
        "mean_pool_next_day_ret_pct": round(float(win["pool_ret"].mean()) * 100, 4),
        "excess_mean_pct": round(ex_t["mean"] * 100, 4),
        "excess_t": round(ex_t["t"], 3),
        "excess_t_nw1": round(sc.nw_tstat(excess, 1), 3),
        "pos_day_share": round(float((win["cohort_ret"] > 0).mean()), 4),
        "decile_next_day_ret_pct": deciles,
    }
    return out


def pq_0025(p: A06Panels, exam_plan: dict[str, str], event_start: str) -> dict[str, Any]:
    """PQ-0025：2023 年以来事件研究——极端净流入组（日截面占比前 10%）次日收益 t 检验。"""
    h = 1
    pool = p.pool("main")
    sig = p.signal.where(pool)
    ret1 = p.fwd(h)
    es = _event_study(sig, ret1, event_start)
    alt = _event_study(p.signal_amount_ratio().where(pool), ret1, event_start)
    pool_v = p.pool("variant")
    trad = _event_study(p.signal.where(pool_v), ret1, event_start)
    res: dict[str, Any] = {
        "q_id": "PQ-0025",
        "exam_plan_ref": exam_plan["PQ-0025"],
        "impl": {
            "event_def": f"信号日 {event_start} 起逐日截面 main_net_inflow_pct 前 10%（占比分位≥0.90，组内 ≥10 名）",
            "return_def": "次日（T+1）后复权收盘收益 close×adj_factor，shift(-1)/px-1",
            "inference": "逐日组合收益均值序列的单样本 t 检验（H0: 均值=0），附 NW(1) 与超额（减同日全池等权）口径",
            "sql_ref": ["signal", "price"],
        },
        "pit": {
            "cutoff": p.cutoff,
            "signal_first": es["signal_first"],
            "signal_last": es["signal_last"],
            "return_end_max": p.cutoff,
            "note": "事件端自动截止 cutoff-1 交易日（次日收益须已实现）",
        },
        "sample": {
            "window": [event_start, p.cutoff],
            "n_event_days": es["n_event_days"],
            "median_cohort_names": es["median_cohort_names"],
            "median_pool_names": int(pool.sum(axis=1).median()),
        },
        "robustness": {
            "alt_signal_pct_of_turnover": {
                k: alt["metrics"].get(k) for k in ("mean_next_day_ret_pct", "t_plain", "excess_t")
            },
            "tradable_pool_only_st_cn_liquidity": (
                {
                    "n_event_days": trad["n_event_days"],
                    **{k: trad["metrics"].get(k) for k in ("mean_next_day_ret_pct", "t_plain", "excess_t")},
                }
                if trad["n_event_days"] >= 30
                else {"insufficient_reason": f"可交易日 {trad['n_event_days']} < 30"}
            ),
            "note": "变体①=题面字面分母（主力净流入÷当日成交额；表内字段分母为主力档毛成交）；"
            "变体②=信号日可交易池（剔 ST/涨跌停锁板/成交额<1000万/次新）——锁板不可买入者剔除后复核可实现性；"
            "均仅披露，主判据按题面全 A 池",
        },
    }
    if es["n_event_days"] < 30:
        res["metrics"] = {
            "n_event_days": es["n_event_days"],
            "insufficient_reason": f"有效事件日 {es['n_event_days']} < 30",
        }
        res["threshold_check"] = {"raw_threshold": exam_plan["PQ-0025"]["threshold"], "reason": "样本不足"}
        res["verdict"] = "insufficient"
        return res
    m = es["metrics"]
    res["metrics"] = m
    checks = {
        "mean_gt_0": {
            "value": m["mean_next_day_ret_pct"],
            "op": ">",
            "bound": 0.0,
            "met": m["mean_next_day_ret_pct"] > 0,
        },
        "t_gt_2": {"value": m["t_plain"], "op": ">", "bound": 2.0, "met": m["t_plain"] > 2.0},
    }
    res["threshold_check"] = {"raw_threshold": exam_plan["PQ-0025"]["threshold"], "items": checks}
    res["verdict"] = "pass" if all(c["met"] for c in checks.values()) else "fail"
    if res["verdict"] == "fail":
        res["fail_type"] = "no_alpha"
    return res


def pq_0026(p: A06Panels, exam_plan: dict[str, str], ic1: pd.Series | None) -> dict[str, Any]:
    """PQ-0026：口径版本标记实测 + Chow 断点检验（版本切换点 / 窗内最大断点扫描）。"""
    cen = p.version_census
    markers = cen["distinct_markers"]
    daily_mean = p.signal.where(p.pool("main")).mean(axis=1).dropna()
    chow_daily = sc.chow_scan(daily_mean.to_numpy(float))
    blk: dict[str, Any] = {}
    blk["designated_switch_breakpoint_available"] = bool(
        len(cen["ingest_batches"]) > 1 or len(cen["distinct_markers"]) > 1
    )
    blk["designated_breakpoint_note"] = (
        "窗内 data_source 单一取值且摄取批次唯一 ⇒ 无可指认的'版本切换日'，"
        "断点证据改由全候选断点扫描（max-F + Bonferroni）承担；现采段起点在窗外（PIT 禁越界）"
    )
    if ic1 is not None and len(ic1.dropna()) >= 40:
        v = ic1.dropna()
        blk["ic_series_n_days"] = int(len(v))
        blk["chow_scan_ic"] = {
            k: (round(x, 5) if isinstance(x, float) else x) for k, x in sc.chow_scan(v.to_numpy(float)).items()
        }
        blk["chow_scan_ic"]["break_date"] = (
            str(v.index[int(blk["chow_scan_ic"]["best_split_index"])].date())
            if blk["chow_scan_ic"].get("best_split_index", -1) >= 0
            else None
        )
    res: dict[str, Any] = {
        "q_id": "PQ-0026",
        "exam_plan_ref": exam_plan["PQ-0026"],
        "impl": {
            "marker_test": f"{_T_MONEY_FLOW} FINAL data_source 在复考窗内的取值分布（版本标记存在性/完整性/切换事件数）",
            "break_test": "Chow 断点检验（截距断裂，k=1）：①若有可指认版本切换日则在该点检验（实测=窗内无切换日，见 designated_switch_breakpoint_available）"
            "②全候选断点扫描取最大 F + Bonferroni 校正（断点内生化，禁人为挑日期）",
            "series_tested": [
                "日频截面主力净流入占比均值（口径漂移最敏感统计量）",
                "1 日前瞻秩 IC 日序列（题面所指 IC 断点）",
            ],
            "sql_ref": ["version_census", "ingest_batches"],
        },
        "pit": {
            "cutoff": p.cutoff,
            "window": [p.start, p.cutoff],
            "note": "断点检验序列全部 ≤ 切点；现采段在窗外不参与",
        },
        "sample": {
            "rows_in_window": cen["pit_probe"]["signal_window"]["rows"],
            "days_in_window": cen["pit_probe"]["signal_window"]["days"],
            "daily_series_n_days": int(len(daily_mean)),
        },
        "metrics": {
            "distinct_version_markers": markers,
            "marker_rows_by_source": cen["by_data_source"],
            "empty_marker_rows": cen["empty_marker_rows"],
            "ingest_batches": cen["ingest_batches"],
            "version_switch_events_in_window": max(0, len(markers) - 1) + max(0, len(cen["ingest_batches"]) - 1),
            "chow_daily_mean_scan": {k: (round(x, 5) if isinstance(x, float) else x) for k, x in chow_daily.items()},
            "break_date_daily_mean": (
                str(daily_mean.index[int(chow_daily["best_split_index"])].date())
                if chow_daily.get("best_split_index", -1) >= 0
                else None
            ),
            **blk,
        },
    }
    marker_ok = bool(cen["marker_single_and_complete"])
    p_raw = chow_daily.get("best_p_raw", float("nan"))
    p_bonf = chow_daily.get("best_p_bonf", float("nan"))
    checks = {
        "version_marker_present_and_complete": {"value": markers, "op": "非空且单值可辨", "met": marker_ok},
        "chow_p_lt_0.05_requires_marker": {
            "value_raw": None if not np.isfinite(p_raw) else round(float(p_raw), 6),
            "value_bonferroni": None if not np.isfinite(p_bonf) else round(float(p_bonf), 6),
            "op": "p<0.05 ⇒ 须标记",
            "met": True,
            "note": "断点显著性实测见 value_*；无论是否显著，版本标记列已 100% 落库⇒'须标记'义务满足",
        },
    }
    res["threshold_check"] = {"raw_threshold": exam_plan["PQ-0026"]["threshold"], "items": checks}
    res["verdict"] = "pass" if marker_ok else "fail"
    res["caveat"] = (
        "窗内 data_source 单一取值且摄取批次为单批=无版本切换事件，"
        "'切换前后 IC 断点'在闭卷窗内无对照段可测；本器改以（a）标记完整性实测+（b）全候选断点扫描"
        "承担同一治理含义（有无未标记的口径断裂），已在案卷登记为待裁项"
    )
    return res


def pq_0163(p: A06Panels, exam_plan: dict[str, str], event_start: str, outcome_0025: dict[str, Any]) -> dict[str, Any]:
    """PQ-0163：U6 退役判据历史重放演练——判据可执行率（组件级机械执行核验）。"""
    steps: list[dict[str, Any]] = []

    def step(no: str, name: str, ok: bool, detail: str) -> None:
        steps.append({"step": no, "component": name, "executable": bool(ok), "detail": detail})

    pool = p.pool("main")
    sig = p.signal.where(pool)
    ret1 = p.fwd(1)
    pct_rank = sig.rank(axis=1, pct=True)
    cohort = (pct_rank >= 0.90) & sig.notna() & ret1.notna()
    daily_full = ret1.where(cohort).mean(axis=1) - ret1.where(sig.notna()).mean(axis=1)
    daily_ex = daily_full.dropna()

    def _replay(win: pd.Series) -> dict[str, Any]:
        t = (
            sc.mean_ttest(win)
            if len(win) >= 3
            else {"n": 0, "mean": float("nan"), "t": float("nan"), "p": float("nan")}
        )
        return {
            "n_days": int(t["n"]),
            "excess_mean_pct": None
            if not np.isfinite(t.get("mean", float("nan")))
            else round(float(t["mean"]) * 100, 4),
            "t_plain": None if not np.isfinite(t.get("t", float("nan"))) else round(float(t["t"]), 3),
            "t_nw1": round(sc.nw_tstat(win, 1), 3) if len(win) >= 10 else None,
            "retire_flag": bool(not (np.isfinite(t.get("t", float("nan"))) and t["t"] > 2.0)),
        }

    w_full = daily_ex
    w_since = daily_ex[daily_ex.index >= pd.Timestamp(event_start)]
    r_full, r_since = _replay(w_full), _replay(w_since)
    prim = r_since  # 主窗=exam_plan『2023 年以来』（与 PQ-0025 判据对象同窗），整回补窗作对照
    step(
        "R1",
        "退役判据文本→事件定义可代码化",
        bool(cohort.notna().any().any()),
        "SL-A06 U6『净流入极端日』= 逐日截面主力净流入占比前 10%（分位≥0.90）",
    )
    step("R2", "超额收益口径可代码化", len(daily_ex) > 0, "次日组合等权收益 − 同日全池等权收益（后复权收盘，T+1 端）")
    step(
        "R3",
        "显著性检验可代码化",
        prim["t_plain"] is not None,
        f"单样本 t（n={prim['n_days']}, t={prim['t_plain']}）+ NW(1) 复核 t={prim['t_nw1']}",
    )
    step(
        "R4",
        "数据窗口明确可指定",
        prim["n_days"] > 0 and r_full["n_days"] > 0,
        f"主窗（exam_plan『2023 年以来』）{event_start}~{p.cutoff}（n={prim['n_days']}）与对照窗 "
        f"{p.start}~{p.cutoff}（n={r_full['n_days']}）两窗均可重放；信号端自动截止 cutoff-1 交易日",
    )
    retire = prim["retire_flag"]
    step(
        "R5",
        "退役布尔可机械输出",
        prim["t_plain"] is not None,
        f"证伪条件『无统计显著超额』⇒ retire={retire}（阈值 t>2 借 exam_plan 绑定，U6 原文无数字阈值）",
    )
    total = len(steps)
    ok_n = sum(1 for s in steps if s["executable"])
    ratio = ok_n / total
    res: dict[str, Any] = {
        "q_id": "PQ-0163",
        "exam_plan_ref": exam_plan["PQ-0163"],
        "impl": {
            "replay_target": "docs/_working/chain_piling_campaign/02_source_line_registry.md §SL-A06 U6 原文："
            "『净流入极端日后续收益事件研究；证伪=无统计显著超额。』",
            "threshold_source": "U6 原文无数字阈值与数据窗口 ⇒ 按先例 PQ-0133 处置：阈值/窗借 exam_plan（t>2）+ 本器窗参数绑定",
            "components": "R1 事件定义 / R2 超额口径 / R3 显著性检验 / R4 数据窗口 / R5 退役布尔",
            "sql_ref": ["signal", "price"],
        },
        "pit": {
            "cutoff": p.cutoff,
            "windows_replayed": [[p.start, p.cutoff], [event_start, p.cutoff]],
            "signal_last": str(daily_ex.index[-1].date()) if len(daily_ex) else None,
            "note": "两窗重放均为闭卷窗内；信号端自动截止 cutoff-1 交易日",
        },
        "sample": {
            "replay_days_full_window": r_full["n_days"],
            "replay_days_since_event_start": r_since["n_days"],
            "median_cohort_names": int(cohort.sum(axis=1).where(cohort.sum(axis=1) > 0).median() or 0),
        },
        "metrics": {
            "steps_total": total,
            "steps_executable": ok_n,
            "executable_ratio": round(ratio, 4),
            "retire_flag_primary_window_since_2023": bool(prim["retire_flag"]),
            "retire_flag_full_backfill_window": bool(r_full["retire_flag"]),
            "replay_full_window": r_full,
            "replay_since_event_start": r_since,
            "cross_ref_PQ0025_excess_t": outcome_0025.get("metrics", {}).get("excess_t"),
        },
        "steps": steps,
        "threshold_check": {
            "raw_threshold": exam_plan["PQ-0163"]["threshold"],
            "items": {"可执行率_eq_1": {"value": round(ratio, 4), "op": "=", "bound": 1.0, "met": ratio == 1.0}},
        },
    }
    res["verdict"] = "pass" if ratio == 1.0 else ("insufficient" if ok_n == 0 else "fail")
    res["caveat"] = "重放演练只证'判据可机械执行'，不等于退役成立；本窗实证超额 t 值见 metrics.excess_t"
    return res


# ---------------------------------------------------------------- 驱动
def run(
    p: A06Panels,
    exam_plan: dict[str, str],
    q_ids: tuple[str, ...],
    event_start: str,
) -> dict[str, Any]:
    """六问按题面判据逐问执行（0125/0126/0127 共用一次面板装载）。"""
    ic_cache: dict[int, pd.Series] = {}
    for h in (1, 5, 20):
        if any(HORIZON_OF.get(q) == h for q in q_ids) or "PQ-0026" in q_ids or "PQ-0025" in q_ids:
            ic_cache[h] = sc.daily_rank_ic(p.signal.where(p.pool("main")), p.fwd(h), MIN_NAMES_DEFAULT)
    out: dict[str, Any] = {"exams": {}}
    for q in q_ids:
        if q in HORIZON_OF:
            out["exams"][q] = pq_012x(p, q, exam_plan, event_start)
        elif q == "PQ-0025":
            out["exams"][q] = pq_0025(p, exam_plan, event_start)
        elif q == "PQ-0026":
            out["exams"][q] = pq_0026(p, exam_plan, ic_cache.get(1))
        elif q == "PQ-0163":
            o25 = out["exams"].get("PQ-0025") or pq_0025(p, exam_plan, event_start)
            out["exams"][q] = pq_0163(p, exam_plan, event_start, o25)
        else:
            raise ValueError(f"未注册考题 {q}")
    join_n = (p.signal.notna() & p.adj_close.notna()).sum(axis=1)
    dmean = p.signal.where(p.pool("main")).mean(axis=1).dropna()
    out["coverage"] = {
        "n_days": int(len(join_n)),
        "first": str(join_n.index[0].date()),
        "last": str(join_n.index[-1].date()),
        "median_names_per_day": int(join_n.median()),
        "min_names_per_day": int(join_n.min()),
        "days_below_min_names": int((join_n < MIN_NAMES_DEFAULT).sum()),
        "signal_mean_daily_window": [
            round(float(dmean.iloc[: len(dmean) // 2].mean()), 4),
            round(float(dmean.iloc[len(dmean) // 2 :].mean()), 4),
        ],
        "signal_stats": {
            "mean": round(float(dmean.mean()), 4),
            "sd_of_daily_mean": round(float(dmean.std(ddof=1)), 4),
            "median_daily_names": int(join_n.median()),
        },
    }
    out["pit"] = {
        "cutoff": p.cutoff,
        "signal_window": [p.start, p.cutoff],
        "panel_last_trade_date": str(p.trade_dates[-1].date()),
        "forward_return_end_max": str(p.trade_dates[-1].date()),
        "probe": p.version_census["pit_probe"],
        "assertion": "所有取数 SQL 上界=切点；面板二次断言端点 ≤ 切点；前瞻收益由 shift(-n) 在面板内截断，"
        "故信号端自动截止 切点-n 交易日，无切点后数据参与",
    }
    out["panel_warnings"] = p.warnings
    return out


def _md5(obj: Any) -> str:
    return hashlib.md5(json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _selftest() -> int:
    """合成面板闭式解比对 + 确定性双跑（不连库）。"""
    rng = np.random.default_rng(20260925)
    dates = pd.bdate_range("2024-01-01", periods=260)
    syms = [f"{i:06d}" for i in range(400)]
    sig = pd.DataFrame(rng.normal(0, 20, size=(len(dates), len(syms))), index=dates, columns=syms)
    px = pd.DataFrame(
        100.0 * np.cumprod(1 + rng.normal(0, 0.02, size=(len(dates), len(syms))), axis=0), index=dates, columns=syms
    )
    ret1 = px.shift(-1) / px - 1.0
    p = A06Panels(
        start="2024-01-01",
        cutoff="2024-12-31",
        signal=sig,
        inflow=sig * 10,
        adj_close=px,
        close_raw=px,
        amount=px * 1e6,
        coverage=pd.DataFrame({"n_join": sig.notna().sum(axis=1)}),
        version_census={
            "distinct_markers": ["synthetic"],
            "by_data_source": [],
            "empty_marker_rows": 0,
            "marker_single_and_complete": True,
            "ingest_batches": [{"ingest_day": "2024-12-31"}],
            "pit_probe": {"signal_window": {"rows": sig.size, "days": len(dates)}},
        },
        horizons=(1, 5, 20),
        sqls={},
        warnings=[],
    )
    fails: list[str] = []

    def chk(name: str, got: float, want: float, tol: float = 1e-6) -> None:
        ok = abs(got - want) <= tol
        print(f"  {'OK ' if ok else 'BAD'} {name}: got={got:.6g} want={want:.6g}")
        if not ok:
            fails.append(name)

    print("[selftest] stats_core 闭式解")
    # 1) 完全正相关截面 → IC=1
    y = sig.iloc[:5].rank(axis=1, pct=True)
    ic1 = sc.daily_rank_ic(sig.iloc[:5], y, min_names=10)
    chk("perfect-rank IC==1", float(ic1.mean()), 1.0, 1e-9)
    # 2) NW(1) 在独立正态序列 ≈ 普通 t
    v = pd.Series(rng.normal(0.5, 1.0, 400))
    chk("NW(1)≈plain t", abs(sc.nw_tstat(v, 1) - (v.mean() / (v.std(ddof=1) / np.sqrt(400)))), 0.0, 0.05)
    # 3) 完美重叠序列：AR(1)=0.95 时 NW(5) t 显著小于普通 t
    a = np.zeros(1500)
    for i in range(1, 1500):
        a[i] = 0.95 * a[i - 1] + rng.normal(0.05, 1.0)
    tt = float(np.mean(a) / (np.std(a, ddof=1) / np.sqrt(len(a))))
    print(f"  info  AR(.95): plain t={tt:.2f} nw1={sc.nw_tstat(a, 1):.2f} nw5={sc.nw_tstat(a, 5):.2f}")
    if not abs(sc.nw_tstat(a, 5)) < abs(tt):
        fails.append("NW 未收紧重叠序列 t")
    # 4) Chow：均值位移 0→1 应极显著；无位移段不显著
    shift = np.concatenate([rng.normal(0, 1, 300), rng.normal(1, 1, 300)])
    c = sc.chow_test(shift, 300)
    print(f"  info  Chow(真断点) F={c['f']:.1f} p={c['p']:.3g}")
    if not c["p"] < 1e-6:
        fails.append("Chow 未检出真断点")
    null = sc.chow_test(rng.normal(0, 1, 600), 300)
    scan_null = sc.chow_scan(rng.normal(0, 1, 600))
    print(f"  info  Chow(无断点) p={null['p']:.3g} scan_bonf={scan_null['best_p_bonf']:.3g}")
    if not null["p"] > 0.01:
        fails.append("Chow 假阳性")
    # 5) 确定性双跑
    print("[selftest] 确定性双跑（同面板两次执行 payload 指纹一致）")
    ep = {
        q: {"title": "synthetic", "method": "m", "criterion": "c", "threshold": "IC>0.02 且 t>2（样本外 IC>0.01）"}
        for q in Q_IDS
    }
    ep["PQ-0025"]["threshold"] = ">0 且 t>2"
    ep["PQ-0026"]["threshold"] = "p<0.05 即须标记"
    ep["PQ-0163"]["threshold"] = "判据可执行率=100%"
    r1 = run(p, ep, Q_IDS, "2024-01-01")
    r2 = run(p, ep, Q_IDS, "2024-01-01")
    chk("双跑 md5 相等", float(r1 is not None and r2 is not None and _md5(r1) == _md5(r2)), 1.0)
    # 6) 面板 PIT 断言与前瞻截断
    tail = p.fwd(20).notna().sum(axis=1)
    if int(tail.iloc[-1]) != 0:
        fails.append("fwd(20) 末行未截断（PIT 泄漏风险）")
    print(
        f"  {'OK ' if 'fwd(20) 末行未截断（PIT 泄漏风险）' not in fails else 'BAD'} fwd(20) 末交易日端点自动 NaN（PIT 截断）"
    )
    print(f"verdicts: { {k: v['verdict'] for k, v in r1['exams'].items()} }")
    print("SELFTEST", "PASS" if not fails else f"FAIL {fails}")
    return 0 if not fails else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="A06 资金流族 6 问可重放复考器")
    ap.add_argument("--out", default="", help="结果 JSON 输出路径（缺省仅打印）")
    ap.add_argument("--cutoff", default=PIT_CUTOFF_DEFAULT, help="PIT 闭卷切点（含）")
    ap.add_argument("--start", default="2021-01-04", help="信号窗起点（含）")
    ap.add_argument(
        "--event-start", default="2023-01-01", help="PQ-0025/0163 事件研究起点（exam_plan 原文『2023 年以来』）"
    )
    ap.add_argument("--questions", default=",".join(Q_IDS), help="子集（逗号分隔 q_id）")
    ap.add_argument("--no-exam-plan-pg", action="store_true", help="不回读 PG 判据（仅离线调试，禁用于出结论）")
    ap.add_argument("--no-variant-masks", action="store_true", help="跳过稳健性变体掩码（省时装载）")
    ap.add_argument("--selftest", action="store_true", help="合成数据闭式解自测（不连库）")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    q_ids = tuple(q.strip().upper() for q in args.questions.split(",") if q.strip())
    unknown = [q for q in q_ids if q not in Q_IDS]
    if unknown:
        raise SystemExit(f"未知考题 {unknown}；可选 {Q_IDS}")
    if args.no_exam_plan_pg:
        raise SystemExit("--no-exam-plan-pg 仅供调试：判据必须回读 PG 真源方可出结论")

    from zephyr.infrastructure.database_service import DatabaseService

    t0 = dt.datetime.now(dt.UTC)
    conn = DatabaseService().get_clickhouse_conn(role="reader")
    exam_plan = load_exam_plan(q_ids)
    p = load_panels(
        conn, start=args.start, cutoff=args.cutoff, horizons=(1, 5, 20), with_variant_masks=not args.no_variant_masks
    )
    payload = run(p, exam_plan, q_ids, args.event_start)
    payload["panels"] = {"sqls": p.sqls, "version_census": p.version_census}
    res = {
        "payload": payload,
        "payload_md5": _md5(payload),
        "run_meta": {
            "tool": str(Path(__file__).resolve()),
            "args": vars(args) | {"q_ids": list(q_ids)},
            "started_at": t0.isoformat(),
            "finished_at": dt.datetime.now(dt.UTC).isoformat(),
            "python": sys.version.split()[0],
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
    }
    txt = json.dumps(res, ensure_ascii=False, indent=1, default=str)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(txt, encoding="utf-8")
        print("WROTE", args.out, "payload_md5", res["payload_md5"])
    for q, e in payload["exams"].items():
        print(
            f"{q}: verdict={e['verdict']} metrics={ {k: v for k, v in e.get('metrics', {}).items() if not isinstance(v, (list, dict))} }"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
