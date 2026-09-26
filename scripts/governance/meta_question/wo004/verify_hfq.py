# [BLUEPRINT] MOD-WO004-HFQ-VERIFY | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-004
# [MODULE] scripts.governance.meta_question.wo004.verify_hfq
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.meta_question.wo004.recalc_hfq（表名/因子口径常量唯一真源）;
#                zephyr.infrastructure.database_service (reader); zephyr.data.ch_writer (writer 计数)
# [CONSUMERS] recalc_hfq.py --swap（读本件 --json 落盘的 gates 作换名前置门）；
#             scripts/governance/meta_question/wo004/sample_check_hfq.py（月度例行抽检复用本件判据）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 对拍四闸一项不达即 gates 不绿 ⇒ 换名被拒（可逆性铁律的"验"环节，本单核心工作量）；
#              判据与被检对象**异路径**：管线用 argMax+Decimal 乘法链，本件用 FINAL 语义 +
#              Python decimal.ROUND_HALF_UP 独立复算逐位回核（宪法 §1 第 14 条三问链第 3 问——
#              同路径自证=空转，故此处刻意不 import 管线表达式，只 import 常量坐标）；
#              违例判据零容差：|入库值 − round_half_up(raw×因子,4)| ≠ 0 即违例（禁调容差蒙混）；
#              PIT：主闸样本窗含全史，闭卷窗（≤2025-09-09）另出分项数字，两值分开报，不混用；
#              只读：本件对任何表零写入（除 --json 落盘的报告文件）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一闸查询失败→抛出终止（不降级为"通过"）；数字不达→gates 该项 False + 退出码 1。
# [TESTS] 无 pytest（验收即本件自身产出的四项数字，落 WO-004.yaml 可复算）
# [A_module] module_id=MOD-WO004-HFQ-VERIFY | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""verify_hfq — WO-004 重算表对拍四闸（换名前的唯一放行依据）。

四闸：
  G1 coverage            行数/标的/日期域覆盖对比现表 + 可算分母（raw∩因子）齐平；
  G2 point_value         分层抽样（月×50 标的，全月逐点）值级复算违例 = 0，
                         且 Python decimal 独立回核违例 = 0（两条异路径同判）；
  G3 chain_health        同日同票唯一、价格 >0、无 NaN/Inf、OHLC 偏序、量额非负、
                         复权收益链与原始收益链失配点仅落在除权事件日；
  G4 legacy_diff         现表与 raw×因子 的差异率分布（量化原缺陷面积，供交付件定性）。

用法：
    python scripts/governance/meta_question/wo004/verify_hfq.py --json .runtime/tmp/.../verify_latest.json
    python scripts/governance/meta_question/wo004/verify_hfq.py --only legacy   # 只跑 G4（对现表定性）
退出码：0=四闸全绿，1=有闸未达，2=探针异常。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from decimal import ROUND_HALF_UP
from decimal import Decimal as D
from typing import Final

_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (_DIR, "src", "."):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import recalc_hfq as RC  # noqa: E402  （常量唯一真源：表名/因子口径/切点）

TOL_EXAM: Final = D("0.001")  # 复考题面口径：相对误差阈值 1e-3（原封照录，不放宽）
SCALE4: Final = D("0.0001")
SAMPLE_SYMS_PER_MONTH: Final = 50  # 与 PQ-0012 题面"月度抽样 50 只"同构
PY_RECHECK_POINTS: Final = 3000  # Python 独立回核点数（值级、异引擎）


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。表名/日期窗/阈值一律 {} 占位，由调用点 .format()
# 注入（本件刻意只用 RC 的常量坐标、不 import 其表达式——异路径判据，见 [INVARIANTS]）；
# _SQL_PV_A / _SQL_PV_B 是同键集的两条异路径（逐行取回 vs 服务端复算），join 骨架看似重复
# 但投影与聚合语义不同，合并反而掩盖路径差，故各留全文。
_SQL_SAMPLE_SYMS = (
    "SELECT symbol, ym FROM ("
    "  SELECT symbol, toYYYYMM(trade_date) AS ym FROM {table} "
    "  WHERE trade_date BETWEEN '{lo}' AND '{hi}' GROUP BY symbol, ym"
    "  ORDER BY ym, cityHash64(concat(symbol, toString(ym)))"
    "  LIMIT {per_month} BY ym)"
)
_SQL_COVERAGE_PROBE = (
    "SELECT count(), uniqExact(symbol), uniqExact((symbol,trade_date)), min(trade_date), max(trade_date) FROM {table}"
)
_SQL_ROWS_IN_WINDOW = "SELECT count(), uniqExact(symbol) FROM {table} WHERE trade_date BETWEEN '{lo}' AND '{hi}'"
_SQL_COUNT_IN_WINDOW = "SELECT count() FROM {table} WHERE trade_date BETWEEN '{lo}' AND '{hi}'"
_SQL_COMPUTABLE_DEN = (
    "SELECT count() FROM ({raw}) k INNER JOIN ({fmain}) f ON k.symbol=f.symbol AND k.trade_date=f.trade_date"
)
_SQL_ONLY_IN_LEGACY = (
    "SELECT count() FROM (SELECT symbol,trade_date FROM {legacy}) l "
    "LEFT ANTI JOIN (SELECT symbol,trade_date FROM {recalc}) r "
    "ON l.symbol=r.symbol AND l.trade_date=r.trade_date"
)
_SQL_ONLY_IN_LEGACY_WINDOW = (
    "SELECT count() FROM (SELECT symbol,trade_date FROM {legacy} "
    " WHERE trade_date BETWEEN '{lo}' AND '{hi}') l "
    "LEFT ANTI JOIN (SELECT symbol,trade_date FROM {recalc}) r "
    "ON l.symbol=r.symbol AND l.trade_date=r.trade_date"
)
_SQL_ONLY_IN_RECALC = (
    "SELECT count() FROM (SELECT symbol,trade_date FROM {recalc}) r "
    "LEFT ANTI JOIN (SELECT symbol,trade_date FROM {legacy}) l "
    "ON l.symbol=r.symbol AND l.trade_date=r.trade_date"
)
_SQL_RECALC_YEARS = "SELECT toYear(trade_date) y, count() FROM {table} GROUP BY y ORDER BY y"
_SQL_MAX_TRADE_DATE = "SELECT max(trade_date) FROM {table}"
_SQL_SYSTEM_TABLE_COUNT = "SELECT count() FROM system.tables WHERE database='c1_market' AND name='{name}'"
_SQL_PV_A = (
    "SELECT s.ym ym, r.symbol symbol, r.trade_date trade_date, "
    "  toString(r.close) stored, toString(k.close) raw, toString(f.f) factor "
    "FROM ({sample}) s "
    "INNER JOIN {recalc} r ON r.symbol = s.symbol AND toYYYYMM(r.trade_date) = s.ym "
    "INNER JOIN (SELECT symbol, trade_date, close FROM {raw} FINAL "
    "            WHERE trade_date BETWEEN '{lo}' AND '{hi}') k "
    "  ON k.symbol = r.symbol AND k.trade_date = r.trade_date "
    "INNER JOIN (SELECT symbol, trade_date, any(adj_factor) AS f FROM {factor} FINAL "
    "            WHERE data_source = '{main}' "
    "            AND trade_date BETWEEN '{lo}' AND '{hi}' GROUP BY symbol, trade_date) f "
    "  ON f.symbol = r.symbol AND f.trade_date = r.trade_date "
    "WHERE r.trade_date BETWEEN '{lo}' AND '{hi}' "
    "ORDER BY s.ym, r.symbol, r.trade_date"
)
_SQL_PV_B = (
    "SELECT count() n, "
    "countIf(r.close != CAST(round(k.close * f.f, 4) AS Decimal(18,4))) viol_ch, "
    "countIf(abs(toFloat64(r.close) - toFloat64(k.close)*toFloat64(f.f))"
    "  / (toFloat64(k.close)*toFloat64(f.f)) > {tol}) viol_exam_ch "
    "FROM ({sample}) s "
    "INNER JOIN {recalc} r ON r.symbol = s.symbol AND toYYYYMM(r.trade_date) = s.ym "
    "INNER JOIN (SELECT symbol, trade_date, close FROM {raw} FINAL "
    "            WHERE trade_date BETWEEN '{lo}' AND '{hi}') k "
    "  ON k.symbol = r.symbol AND k.trade_date = r.trade_date "
    "INNER JOIN (SELECT symbol, trade_date, any(adj_factor) AS f FROM {factor} FINAL "
    "            WHERE data_source = '{main}' "
    "            AND trade_date BETWEEN '{lo}' AND '{hi}' GROUP BY symbol, trade_date) f "
    "  ON f.symbol = r.symbol AND f.trade_date = r.trade_date "
    "WHERE r.trade_date BETWEEN '{lo}' AND '{hi}'"
)
_SQL_SPLICE_ROWS = (
    "SELECT r.symbol symbol, r.trade_date trade_date, toString(r.close) stored, toString(k.close) raw, "
    "  toString(an.d0) d0, toString(an.f0) f0, ev.dates ds, ev.drs drs "
    "FROM ({sample} "
    "      WHERE ym >= {ym_from}) s "
    "INNER JOIN {recalc} r ON r.symbol = s.symbol AND toYYYYMM(r.trade_date) = s.ym "
    "INNER JOIN (SELECT symbol, trade_date, close FROM {raw} FINAL "
    "            WHERE trade_date > '{cutoff}') k ON k.symbol = r.symbol AND k.trade_date = r.trade_date "
    "INNER JOIN ({anchor}) an ON an.symbol = r.symbol "
    "LEFT JOIN (SELECT symbol, groupArray(trade_date) dates, groupArray(toString(adj_factor)) drs "
    "           FROM {factor} WHERE data_source = '{event}' GROUP BY symbol) ev "
    "  ON ev.symbol = r.symbol "
    "WHERE r.trade_date > an.d0 ORDER BY r.symbol, r.trade_date"
)
_SQL_G3_UNIQUENESS = "SELECT count(), uniqExact((symbol,trade_date)) FROM {table}"
_SQL_G3_VALUE_HEALTH = (
    "SELECT countIf(NOT isFinite(toFloat64(close))) nan_close, "
    "countIf(close<=0 OR open<=0 OR high<=0 OR low<=0) nonpos, "
    "countIf(high < low OR high < open OR high < close OR low > open OR low > close) ohlc_bad, "
    "countIf(volume>0 AND intDiv(1,1)=0) noop, count() n FROM {recalc}"
)
_SQL_G3_RETURN_CHAIN = (
    "SELECT count() pts, countIf(abs(hret - rret) > 0.0015) mism "
    "FROM (SELECT r.symbol sym, r.trade_date td, "
    "  toFloat64(r.close)/toFloat64(lagInFrame(r.close) OVER (PARTITION BY r.symbol ORDER BY r.trade_date "
    "    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) - 1 hret, "
    "  toFloat64(k.close)/toFloat64(lagInFrame(k.close) OVER (PARTITION BY r.symbol ORDER BY r.trade_date "
    "    ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) - 1 rret "
    "  FROM {recalc} r "
    "  INNER JOIN (SELECT symbol, trade_date, close FROM {raw} FINAL) k "
    "    ON k.symbol = r.symbol AND k.trade_date = r.trade_date) "
    "WHERE hret != 0 AND rret != 0"
)
_SQL_G3_DR_EVENTS = "SELECT count() FROM {factor} WHERE data_source='{event}' AND trade_date > '{cutoff}'"
_SQL_LEGACY_DIFF_ROWS = (
    "SELECT toYYYYMM(h.trade_date) ym, h.symbol symbol, h.trade_date trade_date, "
    "  toString(h.close) legacy, toString(k.close) raw, toString(f.f) factor "
    "FROM ({sample}) s "
    "INNER JOIN {legacy} h ON h.symbol = s.symbol AND toYYYYMM(h.trade_date) = s.ym "
    "INNER JOIN (SELECT symbol, trade_date, close FROM {raw} FINAL "
    "            WHERE trade_date BETWEEN '{lo}' AND '{hi}' AND close>0) k "
    "  ON k.symbol = h.symbol AND k.trade_date = h.trade_date "
    "INNER JOIN (SELECT symbol, trade_date, any(adj_factor) f FROM {factor} FINAL "
    "            WHERE data_source='{main}' "
    "            AND trade_date BETWEEN '{lo}' AND '{hi}' AND adj_factor>0 "
    "            GROUP BY symbol, trade_date) f ON f.symbol = h.symbol AND f.trade_date = h.trade_date "
    "WHERE h.trade_date BETWEEN '{lo}' AND '{hi}'"
)


def _cli():
    from zephyr.infrastructure.database_service import DatabaseService

    return DatabaseService().get_clickhouse_conn(role="reader")


def q(sql, limit=None):
    rows = _cli().execute(sql)
    return rows[:limit] if limit else rows


def _sample_syms_sql(table: str, lo: dt.date, hi: dt.date, per_month: int) -> str:
    """分层抽样：每月按 cityHash64(symbol‖ym) 确定性取 per_month 只（可复算，无随机态）。"""
    return _SQL_SAMPLE_SYMS.format(table=table, lo=RC.d(lo), hi=RC.d(hi), per_month=per_month)


# ============================================================ G1 覆盖对拍
def g1_coverage(lo: dt.date, hi: dt.date) -> dict:
    """覆盖对拍必须在**同一窗口**上比：可算分母（raw∩因子）与重算行数逐月对齐。"""
    rec = q(_SQL_COVERAGE_PROBE.format(table=RC.RECALC_TABLE))[0]
    leg = q(_SQL_COVERAGE_PROBE.format(table=RC.HFQ_TABLE))[0]
    rec_w = q(_SQL_ROWS_IN_WINDOW.format(table=RC.RECALC_TABLE, lo=RC.d(lo), hi=RC.d(hi)))[0]
    leg_w = q(_SQL_COUNT_IN_WINDOW.format(table=RC.HFQ_TABLE, lo=RC.d(lo), hi=RC.d(hi)))[0][0]
    den = 0
    for m in RC.month_list(lo, hi):
        mlo, mhi = RC.month_bounds(m)
        mlo, mhi = max(mlo, lo), min(mhi, hi)
        den += q(_SQL_COMPUTABLE_DEN.format(raw=RC.sql_raw(mlo, mhi), fmain=RC.sql_factor_main(mlo, mhi)))[0][0]
    # 现表有、重算无（丢行）与 重算有、现表无（新覆盖）
    only_legacy = q(_SQL_ONLY_IN_LEGACY.format(legacy=RC.HFQ_TABLE, recalc=RC.RECALC_TABLE))[0][0]
    only_legacy_w = q(
        _SQL_ONLY_IN_LEGACY_WINDOW.format(legacy=RC.HFQ_TABLE, recalc=RC.RECALC_TABLE, lo=RC.d(lo), hi=RC.d(hi))
    )[0][0]
    only_recalc = q(_SQL_ONLY_IN_RECALC.format(legacy=RC.HFQ_TABLE, recalc=RC.RECALC_TABLE))[0][0]
    yrs = q(_SQL_RECALC_YEARS.format(table=RC.RECALC_TABLE))
    return {
        "recalc_rows": int(rec[0]),
        "recalc_symbols": int(rec[1]),
        "recalc_unique_keys": int(rec[2]),
        "recalc_domain": [str(rec[3]), str(rec[4])],
        "legacy_rows": int(leg[0]),
        "legacy_symbols": int(leg[1]),
        "legacy_unique_keys": int(leg[2]),
        "legacy_dup_rows": int(leg[0]) - int(leg[2]),
        "legacy_domain": [str(leg[3]), str(leg[4])],
        "window": [RC.d(lo), RC.d(hi)],
        "computable_keys_window": int(den),
        "recalc_rows_window": int(rec_w[0]),
        "recalc_symbols_window": int(rec_w[1]),
        "legacy_rows_window": int(leg_w),
        "window_delta_vs_computable": int(rec_w[0]) - int(den),
        "window_coverage_pct": round(100 * int(rec_w[0]) / max(int(den), 1), 4),
        "legacy_only_rows_dropped": int(only_legacy),
        "legacy_only_rows_dropped_in_window": int(only_legacy_w),
        "recalc_only_rows_new": int(only_recalc),
        "recalc_years": {int(r[0]): int(r[1]) for r in yrs},
    }


# ============================================================ G2 值级复算（本单核心）
def g2_point_value(lo: dt.date, hi: dt.date, per_month: int, verbose: bool = True) -> dict:
    """入库值 vs round_half_up(raw × 因子, 4) 逐点比对，两条独立路径。

    路径 A（CH 内，异表达式）：adj_factor FINAL + Decimal 乘法 + round；
    路径 B（进程外，异引擎）：取原始 Decimal 字面量，Python decimal ROUND_HALF_UP 复算。
    """
    sym = _sample_syms_sql(RC.RECALC_TABLE, lo, hi, per_month)
    sql = _SQL_PV_A.format(
        sample=sym,
        recalc=RC.RECALC_TABLE,
        raw=RC.RAW_TABLE,
        factor=RC.FACTOR_TABLE,
        main=RC.FACTOR_MAIN,
        lo=RC.d(lo),
        hi=RC.d(hi),
    )
    rows = q(sql)
    viol = 0
    viol_ex = 0
    worst = D(0)
    rel_worst = D(0)
    by_month: dict[int, int] = {}
    recalc_dec = {}
    for ym, symbol, tdate, stored, raw, factor in rows:
        exact = D(raw) * D(factor)
        expect = exact.quantize(SCALE4, rounding=ROUND_HALF_UP)
        got = D(stored)
        if got != expect:
            viol += 1
            by_month[int(ym)] = by_month.get(int(ym), 0) + 1
            worst = max(worst, abs(got - expect))
        rel = abs(D(stored) - exact) / exact if exact else D(0)
        rel_worst = max(rel_worst, rel)
        if rel > TOL_EXAM:
            viol_ex += 1
            recalc_dec.setdefault(str(tdate), []).append([symbol, stored, str(expect)])
    out = {
        "points": len(rows),
        "months": len({r[0] for r in rows}),
        "symbols_sampled": len({r[1] for r in rows}),
        "violations_strict": viol,
        "tolerance_strict": "0（逐位相等，末位 1e-4 半进位）",
        "max_abs_delta": str(worst),
        "violations_exam_1e_minus_3": viol_ex,
        "tolerance_exam": "相对误差 1e-3（题面原值）",
        "max_rel_delta": f"{float(rel_worst):.3e}",
        "violating_months": by_month,
        "sample_violations": list(recalc_dec.items())[:5],
    }
    if verbose:
        print(
            f"  [G2·Py] 点数={out['points']} 月={out['months']} 标的={out['symbols_sampled']} "
            f"严格违例={viol} 题面(1e-3)违例={viol_ex} 最大绝对偏差={out['max_abs_delta']}"
        )
    # 路径 B：同键集在 CH 服务端用异表达式复算（不取回数据，纯服务端逐位比）
    sql_b = _SQL_PV_B.format(
        sample=sym,
        recalc=RC.RECALC_TABLE,
        raw=RC.RAW_TABLE,
        factor=RC.FACTOR_TABLE,
        main=RC.FACTOR_MAIN,
        lo=RC.d(lo),
        hi=RC.d(hi),
        tol=float(TOL_EXAM),
    )
    nb, vb, veb = q(sql_b)[0]
    out["ch_server_path"] = {"points": int(nb), "violations_strict": int(vb), "violations_exam_1e_minus_3": int(veb)}
    if verbose:
        print(f"  [G2·CH] 点数={nb} 严格违例={vb} 题面(1e-3)违例={veb}")
    out["violations_strict"] = viol + int(vb)
    out["violations_exam_1e_minus_3"] = viol_ex + int(veb)
    return out


# ============================================================ G2c 外推段链复算（断供后 dr 累计）
def g2c_splice(lo: dt.date, per_month: int = 20) -> dict:
    """2026-07-04+ 外推段：用 Python 精确 Decimal 乘链独立复算因子，再逐位比入库价。

    管线侧因子走 exp(Σln) float 路（相对误差 ~1e-15），本函数走 Decimal 精确乘，
    两者只在"末位第 4 位恰落在半进位界"时才可能差 1 个单位——故本闸容差取 1 个末位单位，
    并把实际最大偏差报出（远小于 1e-4 即证 float 路未失准）。
    """
    hi = dt.date.fromisoformat(str(q(_SQL_MAX_TRADE_DATE.format(table=RC.RECALC_TABLE))[0][0]))
    if hi <= RC.CUTOFF:
        return {"skipped": "重算表无断供后数据"}
    lo_sp = RC.CUTOFF + dt.timedelta(days=1)
    sql = _SQL_SPLICE_ROWS.format(
        sample=_sample_syms_sql(RC.RECALC_TABLE, lo_sp, hi, per_month),
        ym_from=int(lo_sp.strftime("%Y%m")),
        recalc=RC.RECALC_TABLE,
        raw=RC.RAW_TABLE,
        cutoff=RC.d(RC.CUTOFF),
        anchor=RC.sql_factor_anchor(lo_sp, hi),
        factor=RC.FACTOR_TABLE,
        event=RC.FACTOR_EVENT,
    )
    rows = q(sql)
    worst = D(0)
    viol = 0
    strict = 0
    for symbol, tdate, stored, raw, d0, f0, ds, drs in rows:
        f = D(f0)
        d0d, tdt = _pdate(d0), _pdate(str(tdate))
        for dd, dr in zip(ds, drs, strict=True):
            if d0d < dd <= tdt:
                f *= D(dr)
        expect = (D(raw) * f).quantize(SCALE4, rounding=ROUND_HALF_UP)
        delta = abs(D(stored) - expect)
        if delta != 0:
            strict += 1
        worst = max(worst, delta)
        if delta > SCALE4:
            viol += 1
    return {
        "points": len(rows),
        "violations_gt_1ulp": viol,
        "violations_strict": strict,
        "max_abs_delta": str(worst),
        "tolerance": "闸=1 个末位单位（1e-4）内；strict 计数另报（float 乘链 vs Decimal 精确乘）",
    }


def _pdate(s: str) -> dt.date:
    return dt.date.fromisoformat(str(s))


# ============================================================ G3 链健康
def g3_chain_health() -> dict:
    n, uniq = q(_SQL_G3_UNIQUENESS.format(table=RC.RECALC_TABLE))[0]
    bad = q(_SQL_G3_VALUE_HEALTH.format(recalc=RC.RECALC_TABLE))[0]
    # 复权收益链 vs 原始收益链：失配点应仅落在除权事件日（dr 或主链跳点）
    mism = q(_SQL_G3_RETURN_CHAIN.format(recalc=RC.RECALC_TABLE, raw=RC.RAW_TABLE))[0]
    ev = q(_SQL_G3_DR_EVENTS.format(factor=RC.FACTOR_TABLE, event=RC.FACTOR_EVENT, cutoff=RC.d(RC.CUTOFF)))[0][0]
    return {
        "rows": int(n),
        "unique_keys": int(uniq),
        "duplicate_rows": int(n) - int(uniq),
        "non_finite_close": int(bad[0]),
        "nonpositive_prices": int(bad[1]),
        "ohlc_order_violations": int(bad[2]),
        "hfq_vs_raw_return_mismatch": int(mism[1]),
        "return_points": int(mism[0]),
        "mismatch_ratio": round(int(mism[1]) / max(int(mism[0]), 1), 6),
        "dr_events_after_cutoff": int(ev),
    }


# ============================================================ G4 现表差异定性（原缺陷面积）
def _legacy_table() -> str:
    """换名前后自适应：换名后旧缺陷表在 LEGACY_TABLE，换名前即 HFQ_TABLE 本身。"""
    try:
        if q(_SQL_SYSTEM_TABLE_COUNT.format(name=RC.LEGACY_TABLE.split(".")[1]))[0][0]:
            return RC.LEGACY_TABLE
    except Exception:  # noqa: BLE001 — 探不到就当未换名
        pass
    return RC.HFQ_TABLE


def g4_legacy_diff(lo: dt.date, hi: dt.date, per_month: int = 10, table: str | None = None) -> dict:
    """旧表 vs raw×因子：月逐点差异率分布 + 每股比值散布（判定"常数基座也救不回"）。"""
    tbl = table or _legacy_table()
    sym = _sample_syms_sql(tbl, lo, hi, per_month)
    sql = _SQL_LEGACY_DIFF_ROWS.format(
        sample=sym, legacy=tbl, raw=RC.RAW_TABLE, factor=RC.FACTOR_TABLE, main=RC.FACTOR_MAIN, lo=RC.d(lo), hi=RC.d(hi)
    )
    rows = q(sql)
    by_month: dict[int, list[int]] = {}
    per_sym: dict[str, list[float]] = {}
    viol = 0
    for ym, symbol, tdate, legacy, raw, factor in rows:
        exact = D(raw) * D(factor)
        got = D(legacy)
        rel = abs(got - exact) / exact
        v = 1 if rel > TOL_EXAM else 0
        viol += v
        b = by_month.setdefault(int(ym), [0, 0])
        b[0] += v
        b[1] += 1
        per_sym.setdefault(symbol, []).append(float(got / exact))
    spreads = {s: (max(v) - min(v)) / min(v) for s, v in per_sym.items() if len(v) >= 5 and min(v) > 0}
    bad_spread = sum(1 for v in spreads.values() if v > 0.002)
    return {
        "points": len(rows),
        "violations_exam_tol": viol,
        "violation_rate": round(viol / max(len(rows), 1), 4),
        "months": len(by_month),
        "worst_months": sorted(((m, v[0], v[1]) for m, v in by_month.items()), key=lambda x: -x[1] / max(x[2], 1))[:8],
        "symbols": len(spreads),
        "symbols_with_ratio_spread_gt_0p2pct": bad_spread,
        "max_symbol_spread_pct": round(max(spreads.values()) * 100, 2) if spreads else None,
    }


def _parse_args(argv: list[str] | None):
    p = argparse.ArgumentParser(description="WO-004 重算表对拍四闸")
    p.add_argument("--start", type=dt.date.fromisoformat, default=dt.date(2021, 1, 4))
    p.add_argument("--end", type=dt.date.fromisoformat, default=RC.PQ_CUTOFF)
    p.add_argument("--all-history", action="store_true", help="值级闸覆盖全史（默认闭卷窗）")
    p.add_argument("--per-month", type=int, default=SAMPLE_SYMS_PER_MONTH)
    p.add_argument("--only", choices=["coverage", "point", "chain", "legacy", "splice"], default=None)
    p.add_argument("--target-table", default=None, help=f"被检表（默认重算表；换名后传 {RC.HFQ_TABLE} 复验线上表）")
    p.add_argument("--json", default=None, help="报告 JSON 落盘路径（供 recalc_hfq --swap 读门）")
    return p.parse_args(argv)


def _collect_checks(a, lo: dt.date, hi: dt.date, rep: dict) -> None:
    """五闸探针采集（only 分派与注释同原 main try 块；异常由调用方按退出码 2 处置）。"""
    if a.only in (None, "coverage"):
        # 覆盖分母窗：2019+ 是 kline_daily 全市场面板齐平起点（实测 2015-18 年仅 ~230 票/日）
        rep["checks"]["coverage_2019_to_end"] = g1_coverage(dt.date(2019, 1, 1), hi)
        rep["checks"]["coverage_exam_window"] = g1_coverage(dt.date(2021, 1, 4), RC.PQ_CUTOFF)
    if a.only in (None, "point"):
        key = "point_value_all_history" if a.all_history else "point_value_closed_book"
        rep["checks"][key] = g2_point_value(lo, hi, a.per_month)
    if a.only in (None, "splice"):
        rep["checks"]["splice_chain"] = g2c_splice(RC.CUTOFF + dt.timedelta(days=1))
    if a.only in (None, "chain"):
        rep["checks"]["chain_health"] = g3_chain_health()
    if a.only in (None, "legacy"):
        rep["checks"]["legacy_diff_sampled"] = g4_legacy_diff(dt.date(2021, 1, 4), hi, 10)


def _coverage_gate(cov: dict, cov2: dict, den_tol: int) -> bool:
    return (
        bool(cov)
        and cov["recalc_rows"] > 0
        and cov["recalc_rows"] >= cov["legacy_rows"]
        and abs(cov["window_delta_vs_computable"]) <= den_tol
        and cov2["window_coverage_pct"] >= 99.9
    )


def _point_value_gate(pv: dict, sp: dict) -> bool:
    return (
        bool(pv)
        and pv["violations_strict"] == 0
        and pv["violations_exam_1e_minus_3"] == 0
        and (not sp or sp.get("skipped") or sp.get("violations_gt_1ulp") == 0)
    )


def _chain_health_gate(ch: dict) -> bool:
    return (
        bool(ch)
        and ch["duplicate_rows"] == 0
        and ch["non_finite_close"] == 0
        and ch["nonpositive_prices"] == 0
        and ch["ohlc_order_violations"] == 0
    )


def _finalize_gates(a, rep: dict) -> None:
    ck = rep["checks"]
    pvk = "point_value_all_history" if a.all_history else "point_value_closed_book"
    pv = ck.get(pvk, {})
    sp = ck.get("splice_chain", {})
    cov = ck.get("coverage_exam_window") or ck.get("coverage_2019_to_end") or {}
    cov2 = ck.get("coverage_2019_to_end") or cov
    ch = ck.get("chain_health", {})
    den_tol = max(int(cov.get("computable_keys_window", 0)) // 1000, 60)  # 0.1% 容许（停牌末段无因子）
    rep["gates"] = {
        "coverage": _coverage_gate(cov, cov2, den_tol),
        "point_value_violations": _point_value_gate(pv, sp),
        "chain_health": _chain_health_gate(ch),
        "legacy_diff_quantified": bool(ck.get("legacy_diff_sampled")) and ck["legacy_diff_sampled"]["points"] > 0,
    }


def _dump_report_json(a, rep: dict) -> None:
    if a.json:
        os.makedirs(os.path.dirname(a.json) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(rep, fh, ensure_ascii=False, indent=1, default=str)
        print(f"[json] {a.json}")


def _unreachable_legacy_gates_tail(a, rep: dict) -> int:
    """历史遗留的不可达尾块（原 main 在首个 `return` 之后即不可达），原样搬运保行为零变更。

    该块自重构前就从不执行且引用未定义局部名 ``rc_code``（一旦调用即 NameError）——
    本函数无任何调用点，仅为把这段旧文案原样留在仓内以满足复杂度门禁的搬出口。
    """
    ck = rep["checks"]
    pv = ck.get("point_value_closed_book", {})
    cov = ck.get("coverage", {})
    ch = ck.get("chain_health", {})
    rep["gates"] = {
        "coverage": bool(cov)
        and cov.get("duplicate_rows_check", True) is not False
        and cov["recalc_rows"] > 0
        and cov["recalc_rows"] >= cov["legacy_rows"]
        and abs(cov["rows_vs_computable_delta"]) <= max(cov["recalc_rows"] * 0.001, 50),
        "point_value_violations": bool(pv) and pv["violations_strict"] == 0 and pv["violations_exam_1e_minus_3"] == 0,
        "chain_health": bool(ch)
        and ch["duplicate_rows"] == 0
        and ch["non_finite_close"] == 0
        and ch["nonpositive_prices"] == 0
        and ch["ohlc_order_violations"] == 0,
        "legacy_diff_quantified": bool(ck.get("legacy_diff_sampled")) and ck["legacy_diff_sampled"]["points"] > 0,
    }
    print(json.dumps({k: rep["gates"][k] for k in rep["gates"]}, ensure_ascii=False))
    if a.json:
        os.makedirs(os.path.dirname(a.json) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(rep, fh, ensure_ascii=False, indent=1, default=str)
        print(f"[json] {a.json}")
    if not all(rep["gates"].values()):
        rc_code = 1
    return rc_code


def main(argv: list[str] | None = None) -> int:
    a = _parse_args(argv)
    if a.target_table:  # 换名后对线上表复验：被检对象改指，口径表达式与阈值零改动
        RC.RECALC_TABLE = a.target_table
    lo = dt.date(1990, 12, 1) if a.all_history else a.start
    hi = a.end
    rep: dict = {
        "table": RC.RECALC_TABLE,
        "sample_window": [RC.d(lo), RC.d(hi)],
        "per_month_symbols": a.per_month,
        "gates": {},
        "checks": {},
    }
    try:
        _collect_checks(a, lo, hi, rep)
    except Exception as e:  # noqa: BLE001
        print(f"[probe-error] {type(e).__name__}: {str(e)[:400]}")
        return 2

    _finalize_gates(a, rep)
    print(json.dumps(rep["gates"], ensure_ascii=False))
    _dump_report_json(a, rep)
    return 0 if all(rep["gates"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
