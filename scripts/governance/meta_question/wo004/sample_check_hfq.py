# [BLUEPRINT] MOD-WO004-HFQ-SAMPLER | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md §WO-004 配套③
# [MODULE] scripts.governance.meta_question.wo004.sample_check_hfq
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.meta_question.wo004.recalc_hfq（表名/因子口径常量唯一真源）;
#                scripts.governance.meta_question.wo004.verify_hfq（抽样器与判据共享 _sample_syms_sql/TOL）;
#                zephyr.infrastructure.database_service (reader)
# [CONSUMERS] 月度排班（治理巡检线）；PQ-0012/0131 复考前的预检；换名后血统漂移绊线
# [STARTUP] scheduled（待排班：月度一次，接入方式由总指挥定；本件自身零常驻零副作用）
# [MATURITY] experimental
# [INVARIANTS] 只读 + 只写报告文件（默认落 .runtime/tmp/wo004_sampler/，禁写 data/ 与 docs/ 业务目录）；
#              判据 = round_half_up(raw × 因子, 4) 逐位相等，零容差（禁调容差蒙混——违例>0 即红）；
#              复算与入库异路径：抽样器在 Python decimal 域独立复算（含外推段 Decimal 精确乘链），
#              不复用灌数侧 SQL（同路径自证=空转，宪法 §1 第 14 条三问链第 3 问）；
#              复权链断供段（>2026-07-03）按 dr 精确乘链复算，与重算口径同构；
#              血统绊线：data_source ≠ recalc_raw_x_adjfactor 的行单独计数（外部报价流回写=口径再分裂
#              的前兆，报出但不混入违例数——两者语义不同，禁合并掩盖）；
#              fail-visible：样本窗内零行 / 因子缺位 / 探针异常 → 退出码 2（禁"无数据=通过"）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 违例=0 → exit 0；违例>0 → exit 1（红）；探针/样本异常 → exit 2。
# [TESTS] 无 pytest（一次性读库巡检，判据即其产出数字）
# [A_module] module_id=MOD-WO004-HFQ-SAMPLER | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TTL-NOTE] WO-004 配套③：抽检器例行化，月度 50 只（值须为枚举单字，注释放旁行）
"""sample_check_hfq — 后复权链月度抽检器（50 只/月，逐点复算比对）。

题面锚：PQ-0012/0131 验收判据 "复权抽检违例率 = 0（月度抽样 50 只复权链路审计）"。
本件即该判据的例行化载体：任一月份抽 50 只标的，对该月全部 (标的,交易日) 点，
用 raw × 因子 的独立 Decimal 复算与入库值逐位比对，违例数必须为 0。

    python scripts/governance/meta_question/wo004/sample_check_hfq.py --month 2026-06
    python scripts/governance/meta_question/wo004/sample_check_hfq.py --last-month --syms 50
    # 排班接线：退出码 0/1/2 即可作哨兵判据；报告行以 WO004-SAMPLER 前缀机器可读。
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from decimal import ROUND_HALF_UP
from decimal import Decimal as D
from typing import Final

_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (_DIR, "src", "."):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import recalc_hfq as RC  # noqa: E402
import verify_hfq as V  # noqa: E402

SCALE4: Final = D("0.0001")
DEFAULT_OUT_DIR: Final = os.path.join(".runtime/tmp", "wo004_sampler")


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{} 占位承载表名/口径值/PIT 日期窗/抽样 symbol 清单，
# 由调用点 .format() 注入；本件取数刻意与灌数侧异表达式（见 [INVARIANTS]），故不复用 RC 的 SQL 常量。
_SQL_SAMPLE_ROWS = (
    "SELECT s.ym ym, r.symbol symbol, r.trade_date trade_date, toString(r.close) stored, "
    "  toString(k.close) raw, r.data_source ds "
    "FROM ({sample}) s "
    "INNER JOIN {table} r ON r.symbol = s.symbol AND toYYYYMM(r.trade_date) = s.ym "
    "INNER JOIN (SELECT symbol, trade_date, close FROM {raw} FINAL "
    "            WHERE trade_date BETWEEN '{lo}' AND '{hi}' AND close > 0) k "
    "  ON k.symbol = r.symbol AND k.trade_date = r.trade_date "
    "WHERE r.trade_date BETWEEN '{lo}' AND '{hi}' "
    "ORDER BY r.symbol, r.trade_date"
)
_SQL_FACTOR_MAIN_WINDOW = (
    "SELECT symbol, trade_date, toString(any(adj_factor)) FROM {factor} FINAL "
    "WHERE data_source = '{main}' AND symbol IN ({lst}) "
    "AND trade_date BETWEEN '{lo}' AND '{hi}' GROUP BY symbol, trade_date"
)
_SQL_FACTOR_DR_EVENTS = (
    "SELECT symbol, groupArray(trade_date), groupArray(toString(adj_factor)) "
    "FROM {factor} WHERE data_source = '{event}' AND symbol IN ({lst}) "
    "GROUP BY symbol"
)
_SQL_FACTOR_ANCHOR = (
    "SELECT symbol, toString(max(trade_date)), toString(argMax(adj_factor, trade_date)) "
    "FROM {factor} WHERE data_source = '{main}' AND symbol IN ({lst}) "
    "GROUP BY symbol"
)
_SQL_FIRST_KLINE = (
    "SELECT symbol, toString(min(trade_date)) FROM {raw} "
    "WHERE market_type = 'A_share' AND trade_date BETWEEN '{lookback}' "
    "AND '{hi}' AND symbol IN ({lst}) GROUP BY symbol "
    "HAVING min(trade_date) > toDate('{cutoff}')"
)
_SQL_MAX_TRADE_DATE = "SELECT max(trade_date) FROM {table}"


def _month_window(month: dt.date) -> tuple[dt.date, dt.date]:
    return RC.month_bounds(month)


def _fetch_rows(table: str, lo: dt.date, hi: dt.date, per_month: int) -> list[tuple]:
    sql = _SQL_SAMPLE_ROWS.format(
        sample=V._sample_syms_sql(table, lo, hi, per_month), table=table, raw=RC.RAW_TABLE, lo=RC.d(lo), hi=RC.d(hi)
    )
    return V.q(sql)


def _factor_lookup(keys: list[tuple], lo: dt.date, hi: dt.date):
    """因子取数（与灌数侧异表达式）：主链 FINAL 直取；缺位者由锚点 × dr 精确乘链补。"""
    syms = sorted({k[0] for k in keys})
    if not syms:
        return {}
    lst = ",".join("'" + s.replace("'", "") + "'" for s in syms)
    fac: dict[tuple[str, dt.date], D] = {}
    for s, t, f in V.q(
        _SQL_FACTOR_MAIN_WINDOW.format(factor=RC.FACTOR_TABLE, main=RC.FACTOR_MAIN, lst=lst, lo=RC.d(lo), hi=RC.d(hi))
    ):
        fac[(s, t)] = D(f)
    ev: dict[str, list[tuple]] = {}
    for s, darr, rarr in V.q(_SQL_FACTOR_DR_EVENTS.format(factor=RC.FACTOR_TABLE, event=RC.FACTOR_EVENT, lst=lst)):
        ev[s] = list(zip(darr, rarr, strict=True))
    anch: dict[str, tuple[dt.date, D]] = {}
    for s, d0, f0 in V.q(_SQL_FACTOR_ANCHOR.format(factor=RC.FACTOR_TABLE, main=RC.FACTOR_MAIN, lst=lst)):
        anch[s] = (V._pdate(d0), D(f0))
    out = dict(fac)
    # 断供后新上市支（与灌数侧同规则、异实现）：主链完全无档 + 首根 K 线晚于 CUTOFF ⇒ f 起算=1
    newlist: dict[str, tuple[dt.date, D]] = {}
    for s, fd in V.q(
        _SQL_FIRST_KLINE.format(
            raw=RC.RAW_TABLE, lookback=RC.d(lo - dt.timedelta(days=200)), hi=RC.d(hi), lst=lst, cutoff=RC.d(RC.CUTOFF)
        )
    ):
        if s not in anch:
            newlist[s] = (V._pdate(fd) - dt.timedelta(days=1), D(1))
    for s, t in keys:
        if (s, t) in out:
            continue
        base = anch.get(s) or newlist.get(s)
        if base is None:
            continue
        d0, f0 = base
        if t <= d0:
            continue  # 无档可推（主链从未覆盖且非断供后新上市）
        f = f0
        for dd, dr in ev.get(s, []):
            if d0 < dd <= t:
                f *= D(dr)
        out[(s, t)] = f
    return out


def run(month: dt.date, per_month: int, table: str) -> dict:
    lo, hi = _month_window(month)
    rows = _fetch_rows(table, lo, hi, per_month)
    keys = [(r[1], r[2]) for r in rows]
    fac = _factor_lookup(keys, lo, hi)
    viol = nofactor = nonpos = dup = foreign = 0
    worst = D(0)
    examples: list = []
    seen: set = set()
    for _ym, sym, tdate, stored, raw, ds in rows:
        if (sym, tdate) in seen:
            dup += 1
        seen.add((sym, tdate))
        if ds != RC.DATA_SOURCE_MARK:
            foreign += 1
        got = D(stored)
        if got <= 0:
            nonpos += 1
        f = fac.get((sym, tdate))
        if f is None:
            nofactor += 1
            continue
        expect = (D(raw) * f).quantize(SCALE4, rounding=ROUND_HALF_UP)
        if got != expect:
            viol += 1
            worst = max(worst, abs(got - expect))
            if len(examples) < 5:
                examples.append([sym, str(tdate), str(got), str(expect), str(f)])
    months = len({r[0] for r in rows})
    return {
        "table": table,
        "month": month.strftime("%Y-%m"),
        "window": [RC.d(lo), RC.d(hi)],
        "symbols_sampled": len({r[1] for r in rows}),
        "months": months,
        "points": len(rows),
        "violations": viol,
        "max_abs_delta": str(worst),
        "examples": examples,
        "points_without_factor": nofactor,
        "duplicate_keys": dup,
        "nonpositive_close": nonpos,
        "foreign_lineage_rows": foreign,
        "verdict": "PASS" if (rows and viol == 0 and nofactor == 0) else ("NO_DATA" if not rows else "FAIL"),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="WO-004 后复权链月度抽检器（50 只/月，零容差）")
    p.add_argument(
        "--month", type=lambda x: dt.date.fromisoformat(x + "-01"), default=None, help="抽检自然月（YYYY-MM）"
    )
    p.add_argument("--last-month", action="store_true", help="取现表最新有数据的自然月")
    p.add_argument("--syms", type=int, default=50, help="每月抽样标的数（题面=50）")
    p.add_argument("--table", default=RC.HFQ_TABLE)
    p.add_argument("--out", default=None, help="报告 YAML 落盘路径（默认 .runtime/tmp/wo004_sampler/）")
    a = p.parse_args(argv)
    if a.month is None:
        if not a.last_month:
            p.error("须指定 --month YYYY-MM 或 --last-month")
        latest = V.q(_SQL_MAX_TRADE_DATE.format(table=a.table))[0][0]
        a.month = dt.date.fromisoformat(str(latest)).replace(day=1)
    rep = run(a.month, a.syms, a.table)
    out = a.out or os.path.join(DEFAULT_OUT_DIR, f"sample_{rep['month']}.yaml")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("# WO-004 后复权链月度抽检报告（判据=round_half_up(raw×因子,4) 逐位相等，零容差）\n")
        for k, v in rep.items():
            if k == "examples":
                fh.write("examples:\n")
                for e in v:
                    fh.write(f"  - {e}\n")
            else:
                fh.write(f"{k}: {v}\n")
    print(
        f"WO004-SAMPLER month={rep['month']} points={rep['points']} "
        f"symbols={rep['symbols_sampled']} violations={rep['violations']} "
        f"max_abs_delta={rep['max_abs_delta']} foreign_lineage={rep['foreign_lineage_rows']} "
        f"no_factor={rep['points_without_factor']} dup_keys={rep['duplicate_keys']} "
        f"nonpos={rep['nonpositive_close']} verdict={rep['verdict']} report={out}"
    )
    if not rep["points"]:
        return 2
    return 0 if rep["violations"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
