# [BLUEPRINT] MOD-WO004-CASCADE-HFQ-SAMPLER | docs/_working/meta_question_answers/casefiles/HFQ-CASCADE.yaml §配套③
# [MODULE] scripts.governance.meta_question.wo004_cascade.sample_check_hfq_cascade
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance/meta_question/wo004_cascade/recalc_hfq_cascade.py（表名/血统标记/窗定义唯一真源）; scripts.governance/meta_question/wo004_cascade/verify_hfq_cascade.py（同一 reader 通道与 q 探针复用）; zephyr.infrastructure.database_service (reader)
# [CONSUMERS] 月度排班（治理巡检线，与 wo004/sample_check_hfq.py 同日同族）； 换名后"周↔日是否又分叉"的长期绊线；任何一次级联表重灌后的复检
# [STARTUP] scheduled（待排班：月度一次；本件自身零常驻零副作用）
# [MATURITY] experimental
# [INVARIANTS] 只读 + 只写报告文件（默认落 .runtime/tmp/wo004_cascade_sampler/，禁写 data/ 与 docs/ 业务目录）； 复算与入库**异路径**（宪法 §1 第 14 条三问链第 3 问：同路径自证=空转）—— 灌数侧在 CH 内按 (toISOYear,toISOWeek)/(toYear,toMonth) 元组分组聚合， 本件把日线原子行取回 Python，用 datetime.isocalendar() + Decimal/int 精确加独立重聚合再逐位比； 判据零容差：OHLCV+amount 六项任一不等即违例（禁调容差蒙混；amount 走 Decimal 精确加， 旧表 float 累计位差（实测最大 0.09 元）在新表已不存在，故不容纳任何位差）； 窗口口径与灌数侧同源：周=ISO 周（周一~周日）、月=自然月，bar 日期=窗内末交易日； 日线去重与灌数侧同规则（血统优先 recalc_raw_x_adjfactor、次取 ingest_ts 最新）—— 裁定口径的唯一实现，本件不自定义第二套； 重聚合器无遍历序依赖：日线行先按日期升序，open 取窗首行、close 逐行覆盖至窗末； 血统绊线：data_source != 级联标记 的行单独计数（采集器回灌=级联再分裂的前兆）， 报出但不混入违例数（两者语义不同，禁合并掩盖）； 负控自证（这把尺必须有牙）：--negative-control 对 *_legacy_20260924（旧基座级联表）跑同一判据， 必须报红；报绿即尺空转，本件以非零退出码自曝； fail-visible：样本窗内零行 / 日线缺窗 / 探针异常 → 退出码 2（禁"无数据=通过"）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 违例=0 → exit 0；违例>0 → exit 1（红）；样本/探针异常 → exit 2； --negative-control：旧表报红 → exit 0（尺有牙），旧表报绿 → exit 1（尺空转）。
# [TESTS] 无 pytest（读库巡检，判据即其产出数字；--negative-control 本身即本件的自检用例）
# [A_module] module_id=MOD-WO004-CASCADE-HFQ-SAMPLER | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TTL-NOTE] WO-004 级联配套③：周↔日一致性月度抽检 50 只（值须为枚举单字，注释放旁行）

"""sample_check_hfq_cascade — 后复权周/月线 ↔ 日线级联一致性月度抽检器（零容差，带负控）。

题面锚：WO-004 改正日线后，级联表（周/月）必须与日线同基座。本件是"级联是否又分叉"的长期绊线：
任一月份抽 N 只标的，把日线原子行取回本地用 Python 独立重聚合出该月每根周/月 bar，
与入库 bar 逐位比 OHLCV+amount，违例数必须为 0。

    python scripts/governance/meta_question/wo004_cascade/sample_check_hfq_cascade.py --month 2026-06
    python scripts/governance/meta_question/wo004_cascade/sample_check_hfq_cascade.py --last-month --which monthly
    python scripts/governance/meta_question/wo004_cascade/sample_check_hfq_cascade.py \
        --month 2026-06 --negative-control
    # 排班接线：退出码 0/1/2 即可作哨兵判据；报告行以 WO004-CASCADE-SAMPLER 前缀机器可读。
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from decimal import Decimal as D
from typing import Final

_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (_DIR, "src", "."):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import recalc_hfq_cascade as CC  # noqa: E402
import verify_hfq_cascade as V  # noqa: E402  （同一 reader 通道；本件刻意不用其 CH 聚合表达式）

DEFAULT_OUT_DIR: Final = os.path.join(".runtime", "tmp", "wo004_cascade_sampler")
SAMPLE_SYMS: Final = 50  # 题面口径：与 wo004 抽检器同构的"月度抽样 50 只"
PAD_DAYS: Final = 40  # 日线取数相对样本月左右外扩（覆盖整窗，含月线整月窗）
FIELDS: Final = ("open", "close", "high", "low", "volume", "amount")


# NO-BARE-SQL：SQL 集中于此（§5.160.2），{} 占位由调用点 .format() 注入。
# 本件刻意与灌数侧异表达式（取原子行回本地聚合），故只引用 CC 的表名/标记常量，不引用其聚合 SQL。
_SQL_SAMPLE_SYMS = (
    "SELECT symbol FROM (SELECT symbol FROM {table} "
    "  WHERE trade_date BETWEEN '{lo}' AND '{hi}' GROUP BY symbol "
    "  ORDER BY cityHash64(concat(symbol, '{seed}')) LIMIT {syms}) ORDER BY symbol"
)
_SQL_BARS = (
    "SELECT symbol, toString(trade_date), toString(open), toString(close), toString(high), "
    "  toString(low), toString(volume), toString(amount), toString(data_source) "
    "FROM {table} WHERE trade_date BETWEEN '{lo}' AND '{hi}' AND symbol IN ({lst}) "
    "ORDER BY symbol, trade_date"
)
_SQL_DAILY_ROWS = (
    "SELECT symbol, toString(trade_date), toString(o), toString(c), toString(h), toString(l), "
    "  toString(v), toString(a) FROM ("
    "  SELECT symbol, trade_date, "
    "    argMax(open, ordk) AS o, argMax(close, ordk) AS c, argMax(high, ordk) AS h, "
    "    argMax(low, ordk) AS l, argMax(volume, ordk) AS v, argMax(amount, ordk) AS a "
    "  FROM (SELECT symbol, trade_date, open, close, high, low, volume, amount, "
    "          (if(data_source = '{mark}', 1, 0), ingest_ts) AS ordk "
    "        FROM {daily} WHERE trade_date BETWEEN '{lo}' AND '{hi}' AND symbol IN ({lst})) "
    "  GROUP BY symbol, trade_date) ORDER BY symbol, trade_date"
)
_SQL_MAX_TRADE_DATE = "SELECT max(trade_date) FROM {table}"


def month_bounds(month: dt.date) -> tuple[dt.date, dt.date]:
    nxt = dt.date(month.year + 1, 1, 1) if month.month == 12 else dt.date(month.year, month.month + 1, 1)
    return dt.date(month.year, month.month, 1), nxt - dt.timedelta(days=1)


def _sym_list_sql(syms: list[str]) -> str:
    return ",".join("'" + s.replace("'", "") + "'" for s in sorted(syms))


def _win_key(d0: dt.date, unit: str):
    """ISO 周（周一~周日）/ 自然月 —— 本地实现，与 CH 的 toISOYear+toISOWeek 同义但异路径。"""
    return d0.isocalendar()[:2] if unit == "iso_week" else (d0.year, d0.month)


def reaggregate(daily_rows: list[tuple], unit: str) -> dict:
    """日线原子行 → 窗聚合：open=窗首交易日、close=窗末交易日、high=max、low=min、量额=sum。

    行已按 (symbol, trade_date) 唯一且入参按日期升序；先按标的分桶再排序，杜绝遍历序依赖。
    价格一进函数即转 Decimal（toString 回来的字符串比大小是字典序，会把 "101.07" 判给
    "97.53" 之下——本件首版踩过这个坑，修在入口而非比较处，杜绝第二套数值口径）；
    量用 int、额用 Decimal 精确加——不复用任何 CH 侧表达式（同路径自证=空转）。
    """
    by_sym: dict[str, list] = {}
    for row in daily_rows:
        by_sym.setdefault(row[0], []).append(row)
    out: dict = {}
    for sym, rows in by_sym.items():
        rows.sort(key=lambda r: r[1])
        win: dict = {}
        for _s, ds, o, c, h, l, v, a in rows:
            d0 = dt.date.fromisoformat(ds)
            key = _win_key(d0, unit)
            o, c, h, l = D(o), D(c), D(h), D(l)
            b = win.get(key)
            if b is None:
                b = {"open": o, "close": c, "high": h, "low": l, "volume": 0, "amount": D(0), "days": 0}
                win[key] = b
            else:
                b["close"] = c  # 升序遍历 ⇒ 最后一次覆盖即窗末交易日
                b["high"] = max(b["high"], h)
                b["low"] = min(b["low"], l)
            b["volume"] += int(v)
            b["amount"] += D(a)
            b["days"] += 1
        for key, b in win.items():
            out[(sym, key)] = b
    return out


def run(month: dt.date, syms_per_month: int, which: str, table: str) -> dict:
    cfg = CC.TARGETS[which]
    lo, hi = month_bounds(month)
    seed = f"{which}{month:%Y%m}"
    syms = [
        r[0]
        for r in V.q(_SQL_SAMPLE_SYMS.format(table=table, lo=CC.d(lo), hi=CC.d(hi), syms=syms_per_month, seed=seed))
    ]
    if not syms:
        return {
            "table": table,
            "which": which,
            "month": f"{month:%Y-%m}",
            "window": [CC.d(lo), CC.d(hi)],
            "symbols_sampled": 0,
            "bars": 0,
            "violations": 0,
            "examples": [],
            "verdict": "NO_DATA",
        }
    lst = _sym_list_sql(syms)
    bars = V.q(_SQL_BARS.format(table=table, lo=CC.d(lo), hi=CC.d(hi), lst=lst))
    drows = V.q(
        _SQL_DAILY_ROWS.format(
            mark=CC.LINEAGE_MARK,
            daily=CC.DAILY_HFQ,
            lo=CC.d(lo - dt.timedelta(days=PAD_DAYS)),
            hi=CC.d(hi + dt.timedelta(days=PAD_DAYS)),
            lst=lst,
        )
    )
    win = reaggregate(drows, cfg["unit"])
    viol = missing = foreign = dup = 0
    worst = D(0)
    examples: list = []
    seen: set = set()
    for sym, ds, o, c, h, l, v, a, src in bars:
        d0 = dt.date.fromisoformat(ds)
        if (sym, ds) in seen:
            dup += 1
        seen.add((sym, ds))
        if src != cfg["mark"]:
            foreign += 1
        b = win.get((sym, _win_key(d0, cfg["unit"])))
        if b is None:
            missing += 1
            if len(examples) < 5:
                examples.append([sym, ds, ["no_daily_window"], {}])
            continue
        got = {"open": D(o), "close": D(c), "high": D(h), "low": D(l), "volume": int(v), "amount": D(a)}
        exp = {
            "open": D(b["open"]),
            "close": D(b["close"]),
            "high": D(b["high"]),
            "low": D(b["low"]),
            "volume": b["volume"],
            "amount": b["amount"],
        }
        bad = [f for f in FIELDS if exp[f] != got[f]]
        if bad:
            viol += 1
            for f in bad:
                delta = D(str(exp[f])) - D(str(got[f]))
                worst = max(worst, abs(delta))
            if len(examples) < 5:
                examples.append([sym, ds, bad, {f: [str(got[f]), str(exp[f])] for f in bad}])
    return {
        "table": table,
        "which": which,
        "month": f"{month:%Y-%m}",
        "window": [CC.d(lo), CC.d(hi)],
        "symbols_sampled": len(syms),
        "bars": len(bars),
        "daily_rows": len(drows),
        "windows_recomputed": len(win),
        "violations": viol,
        "max_abs_delta": str(worst),
        "examples": examples,
        "bars_without_daily_window": missing,
        "duplicate_keys": dup,
        "foreign_lineage_bars": foreign,
        "verdict": "PASS" if (bars and viol == 0 and missing == 0) else ("NO_DATA" if not bars else "FAIL"),
    }


def negative_control(month: dt.date, syms: int) -> dict:
    """对旧基座级联表（*_legacy_20260924）跑同一把尺：必须报红，否则尺空转（本件自曝）。"""
    out = {}
    for which in ("weekly", "monthly"):
        legacy = CC.TARGETS[which]["legacy"]
        if not V.table_exists(legacy):
            out[which] = {"table": legacy, "status": "LEGACY_TABLE_ABSENT", "red": False}
            continue
        r = run(month, syms, which, legacy)
        out[which] = {
            "table": legacy,
            "bars": r["bars"],
            "violations": r["violations"],
            "max_abs_delta": r["max_abs_delta"],
            "red": r["violations"] > 0,
            "verdict": r["verdict"],
        }
    return out


def _write(rep: dict, out: str) -> None:
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("# WO-004 级联 周/月↔日 一致性月度抽检报告（判据=本地 Python 独立重聚合窗，六项逐位相等，零容差）\n")
        for k, v in rep.items():
            if k == "examples":
                fh.write("examples:\n")
                for e in v:
                    fh.write(f"  - {e}\n")
            else:
                fh.write(f"{k}: {v}\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="WO-004 级联 周↔日 一致性月度抽检器（零容差，带负控）")
    p.add_argument(
        "--month", type=lambda x: dt.date.fromisoformat(x + "-01"), default=None, help="抽检自然月（YYYY-MM）"
    )
    p.add_argument("--last-month", action="store_true", help="取被检表最新有数据的自然月")
    p.add_argument("--syms", type=int, default=SAMPLE_SYMS, help="每月抽样标的数（题面=50）")
    p.add_argument("--which", choices=["weekly", "monthly"], default="weekly")
    p.add_argument("--table", default=None, help="被检表（默认该级联表现名；负控用 *_legacy_20260924）")
    p.add_argument(
        "--negative-control", action="store_true", help="对 *_legacy_20260924 跑同一判据，必须报红（证明尺有牙）"
    )
    p.add_argument("--out", default=None, help="报告 YAML 落盘路径")
    a = p.parse_args(argv)
    cfg = CC.TARGETS[a.which]
    table = a.table or cfg["live"]
    if a.month is None:
        if not a.last_month:
            p.error("须指定 --month YYYY-MM 或 --last-month")
            return 2
        latest = V.q(_SQL_MAX_TRADE_DATE.format(table=table))[0][0]
        a.month = dt.date.fromisoformat(str(latest)).replace(day=1)
    if a.negative_control:
        nc = negative_control(a.month, a.syms)
        red_all = bool(nc) and all(v.get("red") for v in nc.values())
        print(
            f"WO004-CASCADE-NEGCRTL month={a.month:%Y-%m} {nc} verdict={'RED_OK' if red_all else 'GREEN_BAD(尺空转)'}"
        )
        _write(
            {
                "mode": "negative_control",
                "month": f"{a.month:%Y-%m}",
                "result": nc,
                "verdict": "RED_OK" if red_all else "GREEN_BAD",
            },
            a.out or os.path.join(DEFAULT_OUT_DIR, f"negctrl_{a.month:%Y-%m}.yaml"),
        )
        return 0 if red_all else 1
    rep = run(a.month, a.syms, a.which, table)
    out = a.out or os.path.join(DEFAULT_OUT_DIR, f"cascade_{a.which}_{rep['month']}.yaml")
    _write(rep, out)
    print(
        f"WO004-CASCADE-SAMPLER which={rep['which']} month={rep['month']} "
        f"symbols={rep['symbols_sampled']} bars={rep['bars']} violations={rep['violations']} "
        f"max_abs_delta={rep['max_abs_delta']} no_window={rep['bars_without_daily_window']} "
        f"foreign_lineage={rep['foreign_lineage_bars']} dup_keys={rep['duplicate_keys']} "
        f"verdict={rep['verdict']} report={out}"
    )
    if not rep["bars"]:
        return 2
    return 0 if rep["violations"] == 0 else 1


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 抽样对拍尺是只读人工核验入口，无自动触发语义（自动触发无意义——不落任何状态）
    raise SystemExit(main())
