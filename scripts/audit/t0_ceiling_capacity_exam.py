# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/t0_matrix/t0_ceiling_prereg_card.md | §1 口径 + §2 判据（单向）
# [MODULE] t0_ceiling_capacity_exam（scripts 判据脚本；T0-CEILING 预注册卡 §0-§2 执行件）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] c1_market.kline_1min（价差上界，只读）；backtest_regime_state_anchored(逻辑品类)（T-1 波动/状态，只读）；docs/_working/t0_matrix/six_phase_history_v1.csv（T-1 六段，只读）
# [CONSUMERS] docs/_working/t0_matrix/T0_SCHEME_MATRIX.md（R1③ 优先级排序）；周五 GPU 矩阵做T 维度取舍；Owner 复查窗
# [STARTUP] manual（python scripts/audit/t0_ceiling_capacity_exam.py）
# [MATURITY] production（容量上界考试件，卡先行纪律：t0_ceiling_prereg_card.md frozen 先于本脚本取数）
# [INVARIANTS] **单向判读**：上界<成本 ⇒ 该组内先买后卖族整族判死；上界≥成本 ⇒ 不证明任何方法可用，禁写成 PASS/通过（卡 §0 是本卡唯一允许的推断方向）；判线 31.2/61.2bp 全继承 CST-T0-001 与 frozen 卡，本件零自定阈值；状态轴一律 PIT=T-1（禁同日，7 自然日容差），不可评日单独成组禁并入允许组；kline_1min 是 ReplacingMergeTree 且未 FINAL 时约 1.74× 重复 ⇒ bar 计数必用 uniqExact(trade_time) 禁 count()（否则把不可交易日误判为可交易）；不修正涨跌停可成交性（不修正使上界更大=偏向不杀=与单向判读一致）；查库只读零状态变更；产物只写 docs/_working/t0_matrix/（.yaml/.csv 禁 .json）
# [MODIFY-GUARD] 本脚本改动=容量考试判据变更，须先改卡并作废重开（卡 frozen 纪律）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 分钟腿不可达/零行=显式报错非静默空产物；六段真源缺失=显式报错（禁把情绪分组整组降级为"全部不可评"）；组内 symbol-day<30 记 INSUFFICIENT 不出判
# [TESTS] tests/audit/test_t0_ceiling_capacity_exam.py（判线继承性/单向判读禁 PASS 字样/uniqExact 计数/T-1 不同日）
# [TTL] task_bound
"""t0_ceiling_capacity_exam.py — 做T 日内价差**上界**容量考试（T0-CEILING 卡，frozen）

上帝视角可达价差 = 当日先出现最低价、后出现最高价时的 (high/low−1)。
这是任何"同日先买后卖"做T 策略的**数学上界**：上界不够成本 ⇒ 整族判死；够了 ⇒ 什么都不证明。
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cost_trio_exam as ct  # 成本常数唯一真源
import t0_conditional_e4_exam as v1  # 宏观门常数 + T-1 容差（零重写）
import t0_gpu_condition_pack as gp  # vol 三桶边界唯一真源（VOL_B3，引用不自定）

EMOTION_ALLOW = {"ignition", "expansion", "euphoria"}  # T0-CONDITIONAL 卡 §2.2 frozen 允许集（引用）

REPO = Path(__file__).resolve().parents[2]
SIX_TRUTH = REPO / "docs/_working/t0_matrix/six_phase_history_v1.csv"
CEILING_START = "2021-09-01"  # 分钟腿起点（卡 §1，禁扩）
CLOSED_BOOK_START = "2019-01-04"  # 与 GPU 包同闭卷窗，用于两包互验
CLOSED_BOOK_CUTOFF = "2025-09-09"
MIN_BARS = 200  # 卡 §1 可交易代理（真实 240 根，缺分钟容忍）
L1_BP = ct.RT_COST_BP  # 31.2：仅覆盖往返固定成本
L2_BP = ct.RT_COST_BP + ct.EDGE_PRECONDITION_BP  # 61.2：成本 + 开仓前置 30bp
DEAD_SHARE = 0.05  # 卡 §2 frozen 判死线
MARGINAL_SHARE = 0.20  # 卡 §2 frozen 边缘线
GROUP_MIN_SYMBOL_DAYS = ct.PAIR_GATE  # 30，承考试族样本门槛

_SQL_DAILY_CEILING = """
WITH rt AS (
    SELECT trade_date, symbol,
           min(low)  AS lo,
           max(high) AS hi,
           argMin(trade_time, low)  AS t_lo,
           argMax(trade_time, high) AS t_hi,
           uniqExact(trade_time)    AS bar_n
    FROM {table}
    WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end}')
    GROUP BY trade_date, symbol
), g AS (
    -- 除法全部收在这一层，且用 if() 兜住 lo=0：实测 kline_1min 存在 min(low)=0 的股票-日
    -- （零价分钟 bar），若在聚合外做 hi/lo 会触发 CH Code 153 Division by zero
    -- （本件首跑即被此拦下）。zero_lo_sd 列把这些坏行如实带出，不静默。
    SELECT trade_date, symbol, bar_n, t_lo, t_hi,
           if(lo > 0 AND hi > lo, (hi / lo - 1) * 10000, 0) AS gross_bp,
           if(lo = 0, 1, 0)                                 AS zero_lo,
           lo, hi
    FROM rt
)
SELECT trade_date,
       countIf(bar_n >= {min_bars})                                            AS universe_n,
       countIf(bar_n >= {min_bars} AND gross_bp > 0 AND t_lo < t_hi)           AS ok_n,
       countIf(bar_n >= {min_bars} AND t_lo < t_hi AND gross_bp >= {l1})       AS ge_l1_n,
       countIf(bar_n >= {min_bars} AND t_lo < t_hi AND gross_bp >= {l2})       AS ge_l2_n,
       countIf(zero_lo = 1)                                                    AS zero_lo_sd,
       round(quantileIf(0.5)(gross_bp, bar_n >= {min_bars} AND t_lo < t_hi AND gross_bp > 0), 2) AS p50_bp,
       round(quantileIf(0.9)(gross_bp, bar_n >= {min_bars} AND t_lo < t_hi AND gross_bp > 0), 2) AS p90_bp,
       round(maxIf(gross_bp, bar_n >= {min_bars} AND t_lo < t_hi), 2)          AS max_bp
FROM g
GROUP BY trade_date
ORDER BY trade_date
"""


def load_daily(start: str, end: str) -> list[dict]:
    from zephyr.data.table_registry import get_registry
    from zephyr.infrastructure.database_service import DatabaseService

    table = get_registry().table("market_kline_1min")
    conn = DatabaseService().get_clickhouse_conn()
    rows = conn.execute(
        _SQL_DAILY_CEILING.format(table=table, start=start, end=end, min_bars=MIN_BARS, l1=L1_BP, l2=L2_BP)
    )
    if not rows:
        raise SystemExit(f"FAIL: 分钟腿 {start}..{end} 零行——禁静默空产物")
    keys = ["trade_date", "universe_n", "ok_n", "ge_l1_n", "ge_l2_n", "zero_lo_sd", "p50_bp", "p90_bp", "max_bp"]
    out = []
    for r in rows:
        d = dict(zip(keys, r, strict=True))
        d["trade_date"] = str(d["trade_date"])
        out.append(d)
    return out


def load_six() -> dict[str, str]:
    if not SIX_TRUTH.exists():
        raise SystemExit(f"FAIL: 六段真源缺失 {SIX_TRUTH}——先跑 t0_six_phase_materialize.py")
    out: dict[str, str] = {}
    with SIX_TRUTH.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[r["trade_date"]] = r["six_phase"] if r["routed"] == "1" else ""
    return out


def t1(series: dict, day: str):
    """PIT=T-1 交易日 + 7 自然日容差（承考试族）。缺失/超容差=None=不可评，禁当禁做。"""
    cands = [k for k in series if k < day]
    if not cands:
        return None
    prev = max(cands)
    if (date.fromisoformat(day) - date.fromisoformat(prev)) > timedelta(days=v1.ASOF_TOLERANCE_DAYS):
        return None
    return series[prev]


def judge(n_sd: int, n_ge: int) -> str:
    """卡 §2 单向判读（**永不返回 PASS**）。"""
    if n_sd < GROUP_MIN_SYMBOL_DAYS:
        return "INSUFFICIENT"
    share = n_ge / n_sd
    if share < DEAD_SHARE:
        return "DEAD_BY_CEILING"
    if share < MARGINAL_SHARE:
        return "MARGINAL"
    return "CEILING_OK_NOT_A_PROOF"  # 字面含 NOT_A_PROOF：禁任何方法据此自称通过


def group_stats(rows: list[dict], key) -> dict:
    from collections import defaultdict

    acc: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])  # ok, ge_l1, ge_l2, days
    for r in rows:
        g = key(r)
        if g is None:
            continue
        acc[g][0] += int(r["ok_n"])
        acc[g][1] += int(r["ge_l1_n"])
        acc[g][2] += int(r["ge_l2_n"])
        acc[g][3] += 1
    out = {}
    for g, (ok, l1, l2, days) in acc.items():
        out[g] = {
            "days": days,
            "ok_symbol_days": ok,
            "ge_L1_symbol_days": l1,
            "ge_L2_symbol_days": l2,
            "share_ge_L1": round(l1 / ok, 4) if ok else None,
            "share_ge_L2": round(l2 / ok, 4) if ok else None,
            "verdict_L1": judge(ok, l1),  # 主判：只覆盖成本
            "verdict_L2": judge(ok, l2),  # 副判：成本+前置
        }
    return dict(sorted(out.items(), key=lambda kv: -(kv[1]["share_ge_L1"] or 0)))


def enrich_row(r, regime, six) -> dict:
    """给单日行贴两门的 T-1 态（None=不可评，禁把"不知道"编码成禁做）。"""
    d = r["trade_date"]
    dom, vol = t1(regime, d) or (None, None)
    sv = t1(six, d)
    r["t1_dominant"] = str(dom) if dom else ""
    r["t1_vol_pct"] = vol
    r["t1_six_phase"] = sv or ""
    r["t1_emotion_routed"] = bool(sv)
    r["t1_macro_allow"] = (
        bool((vol is not None and vol > v1.MACRO_VOL_H) or (str(dom) in v1.MACRO_TREND_STATES))
        if (dom or vol is not None)
        else None
    )
    r["t1_emotion_allow"] = (r["t1_six_phase"] in EMOTION_ALLOW) if sv else None
    return r


def _vol_key(r):
    v = r["t1_vol_pct"]
    if v is None:
        return "na"
    lo, hi = gp.VOL_B3  # 引用 t0_regime 卡 §3 frozen 边界（与 GPU 包同源，禁自定）
    return "L" if v <= lo else ("M" if v <= hi else "H")


def _dual_key(r):
    m, e = r["t1_macro_allow"], r["t1_emotion_allow"]
    if m and e:
        return "dual_allow"
    if m is not None and e is not None:
        return "dual_deny"
    return "unevaluable"


def build_groups(enriched) -> dict:
    return {
        "overall": group_stats(enriched, lambda r: "ALL"),
        "by_emotion_phase_T1": group_stats(enriched, lambda r: r["t1_six_phase"] or "unrouted"),
        "by_vol_bucket_T1": group_stats(enriched, _vol_key),
        "by_macro_state_T1": group_stats(enriched, lambda r: r["t1_dominant"] or None),
        "by_dual_gate_T1": group_stats(enriched, _dual_key),
    }


def closed_book_subset(enriched) -> dict:
    inwin = [r for r in enriched if CLOSED_BOOK_START <= r["trade_date"] <= CLOSED_BOOK_CUTOFF]
    return {
        "window": [CLOSED_BOOK_START, CLOSED_BOOK_CUTOFF],
        "days_in_window": len(inwin),
        "dual_allow_days_in_window": sum(1 for r in inwin if r["t1_macro_allow"] and r["t1_emotion_allow"]),
        "cross_check_target": "data/strategy_intake/grid_t0_conditional_v1/t0_condition_matrix_v1.meta.yaml"
        ":gpu_budget.closed_book.dual_gate_allow_days_in_window",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="做T 日内价差上界容量考试（T0-CEILING frozen）")
    ap.add_argument("--start", default=CEILING_START)
    ap.add_argument("--end", default="2026-09-23")
    ap.add_argument("--out-dir", default="docs/_working/t0_matrix")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_daily(args.start, args.end)
    six = load_six()
    # v1.load_regime_states 的键是 datetime.date，而本件的日期轴是 ISO 字符串
    # （分钟腿/六段真源均为字符串键）⇒ 混型比较会 TypeError 或静默错配，统一转字符串。
    regime = {str(k): v for k, v in v1.load_regime_states().items()}
    six_by_str = six

    # v1.load_regime_states 的键是 datetime.date，而本件日期轴是 ISO 字符串
    # （分钟腿/六段真源均字符串键）⇒ 混型比较会 TypeError 或静默错配，统一转字符串。
    regime = {str(k): v for k, v in v1.load_regime_states().items()}
    enriched = [enrich_row(r, regime, six) for r in rows]
    groups = build_groups(enriched)

    result = {
        "card": "docs/_working/t0_matrix/t0_ceiling_prereg_card.md (frozen)",
        "reading_rule": "单向：上界<成本 ⇒ 该组先买后卖族整族判死；上界≥成本 ⇒ 不证明任何方法可用（禁读成通过）",
        "cost_lines": {
            "L1_cover_cost_bp": L1_BP,
            "L2_cost_plus_precondition_bp": L2_BP,
            "provenance": "CST-T0-001（cost_trio_exam.RT_COST_BP / EDGE_PRECONDITION_BP，import 复用）",
        },
        "window": {"start": args.start, "end": args.end, "days": len(enriched)},
        "closed_book_subset": closed_book_subset(enriched),
        "groups": groups,
        "caveats": {
            "bar_count_uses_uniqExact": "kline_1min 为 ReplacingMergeTree 且未 FINAL 时同分钟多版（普查实测约 1.74×），"
            "count() 会虚增 bar_n 把不可交易日误判为可交易 ⇒ 必用 uniqExact(trade_time)",
            "no_limit_up_fix": "未修正涨跌停可成交性；该不修正使上界更大（更不易判死），与单向判读方向一致（卡 §4.2）",
            "dominant_is_vol_band": "regime_state_anchored.dominant 实为波动率风险四档非趋势标签（卡 §4.4），"
            "故 by_macro_state_T1 各组只能读成波动分层",
            "zero_price_minute_bars_exist": "实测 kline_1min 存在 min(low)=0 的股票-日（零价分钟 bar），"
            "本件把除法收进 if() 兜住并在 daily.csv 带出 zero_lo_sd 计数；"
            "任何用该表算振幅的消费方都须先挡这一路（本包首跑即被 Code 153 拦下）",
            "ceiling_not_strategy": "本件全部结论均为容量上界，不含任何策略可实现性主张",
            "cb_etf_out_of_scope": "转债/跨境 ETF 无分钟 bar，未入本卡；真 T+0 战场另立待料（见 T0_SCHEME_MATRIX §四）",
        },
    }
    (out_dir / "t0_ceiling_result.yaml").write_text(
        yaml.safe_dump(result, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    fields = [
        "trade_date",
        "universe_n",
        "ok_n",
        "ge_l1_n",
        "ge_l2_n",
        "p50_bp",
        "p90_bp",
        "max_bp",
        "zero_lo_sd",
        "t1_dominant",
        "t1_vol_pct",
        "t1_six_phase",
        "t1_macro_allow",
        "t1_emotion_allow",
    ]
    with (out_dir / "t0_ceiling_daily.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(enriched)
    print(yaml.safe_dump(result["groups"], allow_unicode=True, sort_keys=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
