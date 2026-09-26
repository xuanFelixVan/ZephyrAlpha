# [BLUEPRINT] MOD-WO004-CASCADE-HFQ-VERIFY | docs/_working/meta_question_answers/casefiles/HFQ-CASCADE.yaml
# [MODULE] scripts.governance.meta_question.wo004_cascade.verify_hfq_cascade
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance/meta_question/wo004_cascade/recalc_hfq_cascade.py（表名/口径/聚合规则常量唯一真源）;
#                zephyr.infrastructure.database_service (reader)
# [CONSUMERS] recalc_hfq_cascade.py --swap（读本件 --json 落盘的 gates 作换名前置门）；
#             scripts/governance/meta_question/wo004_cascade/sample_check_hfq_cascade.py（月度抽检复用本件 q/抽样器）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 换名前必过 --derive（规则考古）：只有"旧日线 + 候选聚合规则"能把现周/月线逐位复现，
#              才证明本单动手的聚合规则是本项目实际口径（不是拍脑袋定的），再把它套到新日线上；
#              对拍四闸一项不达即 gates 不绿 ⇒ 换名被拒（可逆性铁律的"验"环节）；
#              判据与被检对象**异路径**：灌数侧按 (toISOYear,toISOWeek)/(toYear,toMonth) 元组分组聚合，
#              本件守恒闸按 toMonday(交易日)/toYYYYMM(交易日) 区间求和复算（同键集异表达式），
#              值级闸直接回到日线原子行逐字段比（宪法 §1 第 14 条三问链第 3 问——同路径自证=空转）；
#              违例判据零容差：任何不等即计数（禁调容差蒙混）；不达 0 时逐项归因（附样本键），
#              禁为归零而放宽判据或跳过标的；
#              只读：本件对任何表零写入（除 --json 落盘的报告文件）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一闸查询失败→抛出终止（不降级为"通过"）；数字不达→gates 该项 False + 退出码 1。
# [TESTS] 无 pytest（验收即本件自身产出的数字，落 HFQ-CASCADE.yaml 可复算）
# [A_module] module_id=MOD-WO004-CASCADE-HFQ-VERIFY | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""verify_hfq_cascade — 级联重算对拍：规则考古（--derive）+ 换名验收五闸（--gates）。

G0 derive   规则考古：旧日线 × 候选规则 → 现周/月线，逐字段复现率（含干扰候选，证 ISO 周口径）；
G1 close    周末收盘 == 该周日线末收盘（bar 级，全表；月线同闸）；
G2 ohlc     周↔日 OHLC 偏序不变量：low≤min(open,close)、max(open,close)≤high、价格>0、有限、键唯一；
G3 conserve 聚合守恒：bar.volume == 窗内日线 volume 之和（全表）、bar.amount 同理（异表达式路径）；
G4 coverage 覆盖不缩水：行数/标的/时间跨度 新表 ≥ 换名前现表，日线↔周线 687 只缺口闭合情况；
G5 lineage  血统单一：新表 data_source 全为级联标记（无第二套口径混写）。

用法：
    python scripts/governance/meta_question/wo004_cascade/verify_hfq_cascade.py --derive
    python scripts/governance/meta_question/wo004_cascade/verify_hfq_cascade.py \
        --json .runtime/tmp/st-metaq-gc-20260924/hfq_cascade/verify_latest.json
退出码：0=全绿，1=有闸未达，2=探针异常。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from typing import Final

_DIR = os.path.dirname(os.path.abspath(__file__))
for _p in (_DIR, "src", "."):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import recalc_hfq_cascade as CC  # noqa: E402  （常量唯一真源：表名/口径标记/聚合表达式）

SAMPLE_EXAMPLES: Final = 8  # 未达 0 时归因用样本键数（只报证据，不改判据）
MISSING_DETAIL_LIMIT: Final = 200  # 缺窗归因上限（实测个位数，取 200 留余量；超限即报红不静默截断）
SRC_PAD_DAYS: Final = 40  # 日线取数窗相对 bar 域左右外扩：首/末窗的成窗日线可能落在 bar 域外
# （不外扩会把 1990-12-19/20 这类窗前日期切掉 → 守恒复算假红）
SRC_PAD_DAYS: Final = 40  # 日线取数窗相对 bar 域左右外扩：首/末窗的成圆日线可能落在 bar 域外
# （不外扩会把 1990-12-19/20 这类窗前日期切掉，守恒复算假红）


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。表名/日期窗/年份一律 {} 占位，由调用点 .format() 注入。
# _SQL_WINSUM_* 刻意与灌数侧异表达式（toMonday / toYYYYMM 区间求和 vs ISO 元组分组），见 [INVARIANTS]。
_SQL_COVER_AGG = (
    "SELECT count(), uniqExact(symbol), min(trade_date), max(trade_date), "
    "countDistinct(toYYYYMM(trade_date)) FROM {table}"
)
_SQL_SYMBOLS_ONLY_OLD = (
    "SELECT count() FROM (SELECT DISTINCT symbol FROM {old} "
    "WHERE trade_date BETWEEN '{lo}' AND '{hi}') o "
    "LEFT ANTI JOIN (SELECT DISTINCT symbol FROM {new} "
    "WHERE trade_date BETWEEN '{lo}' AND '{hi}') n ON o.symbol = n.symbol"
)
_SQL_SYMBOL_GAP = (
    "SELECT count() FROM (SELECT DISTINCT symbol FROM {daily}) d "
    "LEFT ANTI JOIN (SELECT DISTINCT symbol FROM {bar}) b ON d.symbol = b.symbol"
)
_SQL_BAR_VS_DAILY = (
    "SELECT count() n, countIf(t.close != s.c) close_viol, "
    "  countIf(t.close != s.c AND t.trade_date >= toDate('{floor}')) close_viol_open, "
    "  countIf(t.trade_date >= toDate('{floor}')) bars_in_open_window "
    "FROM {bar} t INNER JOIN ({daily}) s ON t.symbol = s.symbol AND t.trade_date = s.trade_date"
)
_SQL_BARS_WITHOUT_DAILY = (
    "SELECT count() FROM (SELECT symbol, trade_date FROM {bar}) t "
    "LEFT ANTI JOIN ({daily}) s ON t.symbol = s.symbol AND t.trade_date = s.trade_date"
)
_SQL_BAR_EXAMPLES = (
    "SELECT t.symbol, toString(t.trade_date), toString(t.close), toString(s.c), toString(s.trade_date) "
    "FROM {bar} t INNER JOIN ({daily}) s ON t.symbol = s.symbol AND t.trade_date = s.trade_date "
    "WHERE t.close != s.c LIMIT {n}"
)
_SQL_ORDER_INVARIANT = (
    "SELECT count() n, countIf(high < low OR high < open OR high < close OR low > open "
    "  OR low > close) ohlc_bad, countIf(open <= 0 OR close <= 0 OR high <= 0 OR low <= 0) nonpos, "
    "  countIf(NOT isFinite(toFloat64(close))) nonfinite, "
    "  count() - uniqExact((symbol, trade_date)) dup, countIf(volume = 0) vol_zero "
    "FROM {bar}"
)
# 窗聚合复算（异表达式路径：toMonday/toYYYYMM 区间，灌数侧是 toISOYear+toISOWeek / toYear+toMonth 元组）
_SQL_WINAGG = (
    "SELECT b.symbol AS symbol, b.td AS td, sum(d.v) AS v, sum(d.a) AS a, "
    "  argMin(d.o, d.trade_date) AS o, argMax(d.c, d.trade_date) AS c, "
    "  max(d.h) AS h, min(d.l) AS l, count() AS nd, max(d.trade_date) AS last_day "
    "FROM (SELECT symbol, trade_date AS td, {mbf}(trade_date) AS mb FROM {bar}) b "
    "INNER JOIN (SELECT symbol, trade_date, {mbf}(trade_date) AS mb, o, c, h, l, v, a "
    "            FROM ({daily})) d "
    "ON b.symbol = d.symbol AND b.mb = d.mb GROUP BY b.symbol, b.td"
)
_SQL_CONSERVATION = (
    "SELECT count() n, countIf(t.volume != w.v) vol_viol, countIf(t.open != w.o) open_viol, "
    "  countIf(t.high != w.h) high_viol, countIf(t.low != w.l) low_viol, "
    "  countIf(t.close != w.c) close_viol, countIf(t.amount != w.a) amt_viol, "
    "  countIf(t.trade_date >= toDate('{floor}')) bars_open, "
    "  countIf((t.volume != w.v OR t.open != w.o OR t.high != w.h OR t.low != w.l) "
    "    AND t.trade_date >= toDate('{floor}')) neq_open, "
    "  countIf((t.volume != w.v OR t.open != w.o OR t.high != w.h OR t.low != w.l) "
    "    AND t.trade_date < toDate('{floor}')) neq_closed, "
    "  max(abs(toFloat64(t.amount) - toFloat64(w.a))) amt_maxabs "
    "FROM {bar} t INNER JOIN ({winagg}) w ON t.symbol = w.symbol AND t.trade_date = w.td"
)
_SQL_CONSERVATION_EXAMPLES = (
    "SELECT t.symbol, toString(t.trade_date), toString(w.last_day), t.volume, toString(w.v), "
    "  toString(t.close), toString(w.c), toString(w.nd) "
    "FROM {bar} t INNER JOIN ({winagg}) w ON t.symbol = w.symbol AND t.trade_date = w.td "
    "WHERE t.volume != w.v OR t.open != w.o OR t.high != w.h OR t.low != w.l OR t.close != w.c "
    "ORDER BY t.trade_date DESC LIMIT {n}"
)
_SQL_WINDOW_KEYS_AGG = (
    "SELECT count(), uniqExact((symbol, uy, uw)) FROM (SELECT symbol, {grp}(trade_date) AS uy, "
    "  {grp2}(trade_date) AS uw, trade_date FROM {table})"
)
_SQL_OLD_WINDOW_MISSING = (
    "SELECT count() FROM (SELECT symbol, {grp}(trade_date) AS uy, {grp2}(trade_date) AS uw "
    "  FROM {old} GROUP BY symbol, uy, uw) k "
    "LEFT ANTI JOIN (SELECT symbol, {grp}(trade_date) AS uy, {grp2}(trade_date) AS uw "
    "  FROM {new} GROUP BY symbol, uy, uw) n ON k.symbol = n.symbol AND k.uy = n.uy AND k.uw = n.uw"
)
# 缺窗逐条归因：旧表该窗 bar 是否"零量零额的停牌carry-over 幻影 bar"，且裁定基座（日线）该窗无行
_SQL_WIN_KEYS = (
    "SELECT symbol, {grp}(trade_date) AS uy, {grp2}(trade_date) AS uw, max(trade_date) AS bd, "
    "  argMax({vol}, trade_date) AS vol, argMax({amt}, trade_date) AS amt, count() AS n "
    "FROM {tbl} GROUP BY symbol, uy, uw"
)
_SQL_OLD_WINDOW_MISSING_DETAIL = (
    "SELECT k.symbol, toString(k.uy), toString(k.uw), toString(k.bd), toString(k.vol), "
    "  toString(k.amt), toUInt8(k.vol = 0 AND k.amt = 0) AS old_bar_empty "
    "FROM ({oldw}) k LEFT ANTI JOIN ({neww}) n "
    "ON k.symbol = n.symbol AND k.uy = n.uy AND k.uw = n.uw ORDER BY k.bd LIMIT {lim}"
)
_SQL_DAILY_ROWS_IN_WINDOW = (
    "SELECT count() FROM ({daily}) WHERE symbol = '{sym}' AND {grp}(trade_date) = {uy} AND {grp2}(trade_date) = {uw}"
)
_SQL_LINEAGE_DIST = "SELECT data_source, count() FROM {table} GROUP BY data_source ORDER BY 2 DESC"
_SQL_BARS_WITHOUT_WINDOW = (
    "SELECT count() FROM (SELECT symbol, trade_date, {mbf}(trade_date) AS mb FROM {bar}) b "
    "LEFT ANTI JOIN (SELECT symbol, {mbf}(trade_date) AS mb FROM ({daily})) d "
    "ON b.symbol = d.symbol AND b.mb = d.mb"
)
_SQL_TABLE_EXISTS = "SELECT count() FROM system.tables WHERE database='{db}' AND name='{tbl}'"
_SQL_COUNT_IN_WINDOW = "SELECT count() FROM {table} WHERE trade_date BETWEEN '{lo}' AND '{hi}'"
_SQL_MIN_TRADE_DATE = CC._SQL_MIN_TRADE_DATE
# ---- 规则考古（G0）：候选规则 = 窗定义 × trade_date 取法，逐字段复现现表
_SQL_DERIVE_LIVE = (
    "SELECT symbol, trade_date, open, close, high, low, volume, amount, "
    "  amplitude, pct_change, change, turnover, {grp} AS uy, {grp2} AS uw "
    "FROM {live} WHERE trade_date BETWEEN '{lo}' AND '{hi}'"
)
_SQL_DERIVE = (
    "SELECT count() n, countIf(x.trade_date = k.td) date_eq, countIf(x.close = k.c) close_eq, "
    "  countIf(x.open = k.o) open_eq, countIf(x.high = k.h) high_eq, countIf(x.low = k.l) low_eq, "
    "  countIf(x.volume = k.v) vol_eq, countIf(x.amount = k.a) amt_eq, "
    "  max(abs(toFloat64(x.amount) - toFloat64(k.a))) amt_maxabs, "
    "  countIf(x.amplitude != 0 OR x.pct_change != 0 OR x.change != 0 OR x.turnover != 0) derived_nonzero "
    "FROM ({livew}) x INNER JOIN ({bars}) k "
    "  ON x.symbol = k.symbol AND x.uy = k.uy AND x.uw = k.uw AND {date_pred}"
)
_SQL_DERIVE_UNMATCHED = (
    "SELECT count() FROM ({livew}) x LEFT ANTI JOIN ({bars}) k ON x.symbol = k.symbol AND x.uy = k.uy AND x.uw = k.uw"
)
_SQL_DERIVE_BARS = (
    "SELECT symbol, {grp} AS uy, {grp2} AS uw, max(trade_date) AS td, min(trade_date) AS fd, "
    "  argMin(o, trade_date) AS o, argMax(c, trade_date) AS c, max(h) AS h, min(l) AS l, "
    "  sum(v) AS v, sum(a) AS a "
    "FROM ({daily}) GROUP BY symbol, uy, uw"
)
# 现表"同窗多根 bar"的最早日：采集器改为逐日累计落盘的起点（考古对拍窗上限由此数据推出，非手填）
_SQL_TAIL_ONSET = (
    "SELECT min(md) FROM (SELECT symbol, {grp}(trade_date) AS uy, {grp2}(trade_date) AS uw, "
    "  min(trade_date) AS md FROM {live} GROUP BY symbol, uy, uw HAVING count() > 1)"
)
_SQL_DERIVE_YEAR_BREAKDOWN = (
    "SELECT toYear(x.trade_date) y, count() n, countIf(x.close != k.c OR x.open != k.o "
    "  OR x.high != k.h OR x.low != k.l OR x.volume != k.v) ohlcv_neq "
    "FROM ({livew}) x INNER JOIN ({bars}) k "
    "  ON x.symbol = k.symbol AND x.uy = k.uy AND x.uw = k.uw AND x.trade_date = k.td "
    "GROUP BY y ORDER BY y"
)
_SQL_LAST_BAR_CLOSE = (
    "SELECT symbol, max(trade_date) AS td, argMax(close, trade_date) AS c FROM {table} "
    "WHERE trade_date BETWEEN '{lo}' AND '{hi}' GROUP BY symbol"
)
_SQL_LAST_CLOSE_COMPARE = (
    "SELECT count() n, countIf(x.c != k.c) neq, countIf(x.td = k.td) same_date "
    "FROM ({last_x}) x INNER JOIN ({last_k}) k ON x.symbol = k.symbol"
)
_SQL_MAX_TRADE_DATE = "SELECT max(trade_date) FROM {table}"


def _cli():
    from zephyr.infrastructure.database_service import DatabaseService

    return DatabaseService().get_clickhouse_conn(role="reader")


def q(sql, limit=None):
    rows = _cli().execute(sql)
    return rows[:limit] if limit else rows


def _safe_sym(s: str) -> str:
    """symbol 只作探针值，剥掉一切引号（数据不当指令，宪法 §9.11）。"""
    return str(s).replace("'", "").replace("\\", "").strip()


def table_exists(name: str) -> bool:
    db, tbl = name.split(".")
    return bool(q(_SQL_TABLE_EXISTS.format(db=db, tbl=tbl))[0][0])


def resolve_pair(which: str, side: str = "auto") -> tuple[str, str, dict]:
    """返回 (被检新表, 换名前现表, 该表配置)。

    side=pre → 检 staging 重算表（换名前）；post → 检现表（换名后）；
    auto → 沿用"legacy 在=已换名"推断——**该推断在第二轮重建下会选错边**（实测：
    首轮换名留下 *_legacy_20260924，第二轮 staging 重建待验时它仍判"已换名"，
    于是把被污染的现表当成待验新表报红）。第二轮 MUST 显式 --check-side pre。
    """
    cfg = CC.TARGETS[which]
    if side == "pre":
        if not table_exists(cfg["recalc"]):
            raise FileNotFoundError(f"要求换名前对拍但重算表不存在：{cfg['recalc']}")
        return cfg["recalc"], cfg["live"], cfg
    if side == "post":
        return cfg["live"], cfg["legacy"], cfg
    if table_exists(cfg["legacy"]):
        return cfg["live"], cfg["legacy"], cfg
    return cfg["recalc"], cfg["live"], cfg


def daily_src(lo: dt.date, hi: dt.date, daily: str = CC.DAILY_HFQ) -> str:
    return CC.sql_daily_src(lo, hi, daily=daily)


# ============================================================ G0 规则考古（不许跳过的一步）
def _candidate(live: str, src: str, wlo: dt.date, whi: dt.date, grp: str, grp2: str, date_pred: str) -> dict:
    """src 必须是**完整**日线源（含比较窗两侧整窗），只把现表行限到 [wlo,whi]。

    日线源若被比较窗截断，窗首/窗末那几个不完整窗会造出假不一致（实测月线 2019 年
    假违例 3,334 条、amount 假差 8.4e9——全属切窗，非口径差）。
    """
    bars = _SQL_DERIVE_BARS.format(daily=src, grp=grp, grp2=grp2)
    livew = _SQL_DERIVE_LIVE.format(live=live, grp=grp, grp2=grp2, lo=CC.d(wlo), hi=CC.d(whi))
    row = q(_SQL_DERIVE.format(livew=livew, bars=bars, date_pred=date_pred))[0]
    unmatched = q(_SQL_DERIVE_UNMATCHED.format(livew=livew, bars=bars))[0][0]
    nrows = int(q(_SQL_COUNT_IN_WINDOW.format(table=live, lo=CC.d(wlo), hi=CC.d(whi)))[0][0])
    n = int(row[0]) or 1
    return {
        "joined": int(row[0]),
        "live_rows_in_window": nrows,
        "date_eq_pct": round(100 * int(row[1]) / n, 4),
        "close_eq_pct": round(100 * int(row[2]) / n, 4),
        "open_eq_pct": round(100 * int(row[3]) / n, 4),
        "high_eq_pct": round(100 * int(row[4]) / n, 4),
        "low_eq_pct": round(100 * int(row[5]) / n, 4),
        "volume_eq_pct": round(100 * int(row[6]) / n, 4),
        "amount_eq_pct": round(100 * int(row[7]) / n, 4),
        "amount_max_abs_delta": float(row[8] or 0),
        "derived_cols_nonzero_rows": int(row[9]),
        "unmatched_live_rows_by_window": int(unmatched),
    }


def derive(which: str, lo: dt.date, hi: dt.date) -> dict:
    """旧日线（被裁定为错的基座）+ 候选聚合规则 → 能否复现现周/月线。

    复现率即"本单所用聚合规则 = 项目实际口径"的证据；候选同跑以证伪替代解释：
      iso_last   = ISO 周（或自然月）窗，trade_date=窗内**末**交易日（本单采用）
      iso_first  = 同窗，trade_date=窗内首交易日（干扰候选：证末日假设才成立）
      shift_last = 窗边界平移（周日锚定周 / 月中锚定月，干扰候选：证 ISO 周边界）
    对拍窗上限取"现表首次出现同窗多根 bar"之日的前一日（tail_onset 数据推出）：该日之后
    采集器改为按"周内逐日累计"落盘，同一窗有数根 bar，本就不是一个干净的窗聚合样本。
    """
    cfg = CC.TARGETS[which]
    live = cfg["legacy"] if table_exists(cfg["legacy"]) else cfg["live"]
    daily = CC.DAILY_HFQ_LEGACY
    weekly = cfg["unit"] == "iso_week"
    iso, iso2 = ("toISOYear", "toISOWeek") if weekly else ("toYear", "toMonth")
    shift = (
        ("toStartOfWeek(trade_date, 4)", "toStartOfWeek(trade_date, 4)")
        if weekly
        else ("toYear(trade_date - 15)", "toMonth(trade_date - 15)")
    )
    onset_rows = q(_SQL_TAIL_ONSET.format(live=live, grp=iso, grp2=iso2))[0][0]
    onset = dt.date.fromisoformat(str(onset_rows)) if onset_rows else hi
    hi_closed = min(hi, onset - dt.timedelta(days=1))
    out: dict = {
        "table_under_test": live,
        "daily_basis": daily,
        "tail_onset_first_multi_bar_window": str(onset),
        "closed_window": [CC.d(lo), CC.d(hi_closed)],
        "full_window": [CC.d(lo), CC.d(hi)],
    }
    pad_days = max(cfg["buffer_days"], SRC_PAD_DAYS)
    src_full = daily_src(lo - dt.timedelta(days=pad_days), hi + dt.timedelta(days=pad_days), daily=daily)
    g, g2 = f"{iso}(trade_date)", f"{iso2}(trade_date)"
    for tag, wlo, whi in (("closed_window", lo, hi_closed), ("full_window", lo, hi)):
        out[f"{tag}_iso_last"] = _candidate(live, src_full, wlo, whi, g, g2, "x.trade_date = k.td")
        out[f"{tag}_iso_first"] = _candidate(live, src_full, wlo, whi, g, g2, "x.trade_date = k.fd")
        out[f"{tag}_shift_last"] = _candidate(live, src_full, wlo, whi, shift[0], shift[1], "x.trade_date = k.td")
    # 逐年 OHLCV 复现率（把"不一致只落在尾窗"这件事摆成数字，不靠叙述）
    bars = _SQL_DERIVE_BARS.format(daily=src_full, grp=g, grp2=g2)
    livew = _SQL_DERIVE_LIVE.format(live=live, grp=g, grp2=g2, lo=CC.d(lo), hi=CC.d(hi))
    out["ohlcv_mismatch_by_year"] = {
        int(r[0]): {"joined": int(r[1]), "neq": int(r[2])}
        for r in q(_SQL_DERIVE_YEAR_BREAKDOWN.format(livew=livew, bars=bars))
    }
    # 可比性：总包口径"周末收盘 vs 日线末收盘"标的级一致率（旧基座）。窗取闭合窗——
    # 尾窗日线与周线由不同采集器各自续写，末日期本就不齐，比较无意义（full 值另报以证竞态）。
    for tag, wlo, whi in (("closed_window", lo, hi_closed), ("full_window", lo, hi)):
        lastbar = _SQL_LAST_BAR_CLOSE.format(table=live, lo=CC.d(wlo), hi=CC.d(whi))
        lastdaily = _SQL_LAST_BAR_CLOSE.format(table=daily, lo=CC.d(wlo), hi=CC.d(whi))
        n, neq, same = q(_SQL_LAST_CLOSE_COMPARE.format(last_x=lastbar, last_k=lastdaily))[0]
        out[f"symbol_last_close_vs_old_daily_{tag}"] = {
            "symbols": int(n),
            "mismatch": int(neq),
            "consistency_pct": round(100 * (int(n) - int(neq)) / max(int(n), 1), 4),
            "mismatch_pct": round(100 * int(neq) / max(int(n), 1), 4),
            "same_last_date": int(same),
        }
    return out


# ============================================================ G1 收盘一致性（周↔日 / 月↔日）
def open_floor(which: str) -> dt.date:
    """未收盘窗（含日线源最新交易日的那个周/月）的起点——级联是快照，日线采集器在灌数后
    仍会往本窗续行，该窗 bar 与"当前日线"必然存在日历竞态尾差，必须与闭合窗分开计数。"""
    hi = dt.date.fromisoformat(str(q(_SQL_MAX_TRADE_DATE.format(table=CC.DAILY_HFQ))[0][0]))
    return (
        hi - dt.timedelta(days=hi.weekday())
        if CC.TARGETS[which]["unit"] == "iso_week"
        else dt.date(hi.year, hi.month, 1)
    )


def g1_close_consistency(which: str, bar: str, lo: dt.date, hi: dt.date) -> dict:
    """bar.close 必须逐位等于日线在 bar 日期（=窗内末交易日）那一行的 close。

    另出"标的级末收盘"口径（与总包 71.77% 那个数字可比），限定在闭合域内算——
    日线与周线由不同采集器各自续写，末日期不齐时该比较无意义，故分开报。
    """
    src = daily_src(lo - dt.timedelta(days=SRC_PAD_DAYS), hi + dt.timedelta(days=SRC_PAD_DAYS))
    floor = open_floor(which)
    n, cv, cvopen, barsopen = q(_SQL_BAR_VS_DAILY.format(bar=bar, daily=src, floor=CC.d(floor)))[0]
    orphan = q(_SQL_BARS_WITHOUT_DAILY.format(bar=bar, daily=src))[0][0]
    ex = q(_SQL_BAR_EXAMPLES.format(bar=bar, daily=src, n=SAMPLE_EXAMPLES))
    bound = floor - dt.timedelta(days=1)
    lastbar = _SQL_LAST_BAR_CLOSE.format(table=bar, lo=CC.d(lo), hi=CC.d(bound))
    lastdaily = _SQL_LAST_BAR_CLOSE.format(table=CC.DAILY_HFQ, lo=CC.d(lo), hi=CC.d(bound))
    sn, sneq, samesame = q(_SQL_LAST_CLOSE_COMPARE.format(last_x=lastbar, last_k=lastdaily))[0]
    return {
        "bar": bar,
        "bars_joined": int(n),
        "bars_without_daily_row": int(orphan),
        "close_violations": int(cv),
        "close_violation_rate": round(int(cv) / max(int(n), 1), 6),
        "close_violations_in_open_window": int(cvopen),
        "bars_in_open_window": int(barsopen),
        "close_violations_in_closed_windows": int(cv) - int(cvopen),
        "open_window_floor": CC.d(floor),
        "closed_domain_bound": CC.d(bound),
        "symbol_last_close_within_closed_domain": {
            "symbols": int(sn),
            "mismatch": int(sneq),
            "mismatch_pct": round(100 * int(sneq) / max(int(sn), 1), 4),
            "same_last_date": int(samesame),
        },
        "examples": [[str(x) for x in r] for r in ex],
    }


# ============================================================ G2 偏序不变量
def g2_order_invariants(bar: str) -> dict:
    n, bad, nonpos, nonfin, dup, vz = q(_SQL_ORDER_INVARIANT.format(bar=bar))[0]
    return {
        "bar": bar,
        "rows": int(n),
        "ohlc_order_violations": int(bad),
        "nonpositive_prices": int(nonpos),
        "non_finite_close": int(nonfin),
        "duplicate_keys": int(dup),
        "zero_volume_bars": int(vz),
    }


# ============================================================ G3 聚合守恒（异表达式路径）
def g3_conservation(which: str, bar: str, lo: dt.date, hi: dt.date) -> dict:
    """灌数侧按 ISO 元组分组聚合，本闸按 toMonday/toYYYYMM 区间复算——同键集异表达式。

    守恒口径覆盖 OHLCV+amount 全六项（open=窗首交易日、close=窗末、high=max、low=min、
    volume/amount=sum）。违例按闭合窗/未收盘窗分列：未收盘窗的差=日线在灌数后又续行
    （examples 里的 last_day > bar 日期即铁证），闭合窗的差不允许存在。
    """
    src = daily_src(lo - dt.timedelta(days=SRC_PAD_DAYS), hi + dt.timedelta(days=SRC_PAD_DAYS))
    weekly = CC.TARGETS[which]["unit"] == "iso_week"
    mbf = "toMonday" if weekly else "toYYYYMM"
    floor = open_floor(which)
    winagg = _SQL_WINAGG.format(bar=bar, daily=src, mbf=mbf)
    (n, vv, ov, hv, lv, cv, av, bars_open, neq_open, neq_closed, amax) = q(
        _SQL_CONSERVATION.format(bar=bar, winagg=winagg, floor=CC.d(floor))
    )[0]
    nowin = q(_SQL_BARS_WITHOUT_WINDOW.format(bar=bar, daily=src, mbf=mbf))[0][0]
    ex = q(_SQL_CONSERVATION_EXAMPLES.format(bar=bar, winagg=winagg, n=SAMPLE_EXAMPLES))
    return {
        "bar": bar,
        "bars": int(n),
        "volume_violations": int(vv),
        "open_violations": int(ov),
        "high_violations": int(hv),
        "low_violations": int(lv),
        "close_violations": int(cv),
        "amount_violations": int(av),
        "amount_max_abs_delta": float(amax or 0),
        "bars_in_open_window": int(bars_open),
        "violations_in_open_window": int(neq_open),
        "violations_in_closed_windows": int(neq_closed),
        "bars_without_window": int(nowin),
        "open_window_floor": CC.d(floor),
        "volume_violation_rate": round(int(vv) / max(int(n), 1), 6),
        "examples": [[str(x) for x in r] for r in ex],
    }


def _missing_window_detail(new: str, old: str, grp: str, grp2: str, lo: dt.date, hi: dt.date, total: int) -> dict:
    """旧表有、新表无的窗逐条取回并机检归因：

    可解释 = 旧表该窗 bar 量额皆 0（停牌期 carry-over 幻影 bar，采集器把上周收盘直抄）
             **且** 裁定基座（kline_daily_hfq）在该窗没有任何一行（即无原始交易可聚合）。
    其余一律计 unexplained（门红），禁"看着像停牌"就放过。
    """
    src = daily_src(lo - dt.timedelta(days=SRC_PAD_DAYS), hi + dt.timedelta(days=SRC_PAD_DAYS))
    oldw = _SQL_WIN_KEYS.format(tbl=old, grp=grp, grp2=grp2, vol="volume", amt="amount")
    neww = _SQL_WIN_KEYS.format(tbl=new, grp=grp, grp2=grp2, vol="volume", amt="amount")
    rows = q(_SQL_OLD_WINDOW_MISSING_DETAIL.format(oldw=oldw, neww=neww, lim=MISSING_DETAIL_LIMIT))
    explained = 0
    out = []
    for sym, uy, uw, bd, vol, amt, empty in rows:
        ndaily = int(
            q(_SQL_DAILY_ROWS_IN_WINDOW.format(daily=src, sym=_safe_sym(sym), grp=grp, grp2=grp2, uy=uy, uw=uw))[0][0]
        )
        ok = bool(int(empty)) and ndaily == 0
        explained += int(ok)
        out.append(
            {
                "symbol": sym,
                "window": f"{uy}-{uw}",
                "old_bar_date": bd,
                "old_volume": vol,
                "old_amount": amt,
                "ruled_daily_rows_in_window": ndaily,
                "explained_halt_phantom": ok,
            }
        )
    return {"explained": explained, "unexplained": max(total, len(rows)) - explained, "rows": out}


# ============================================================ G4 覆盖不缩水
def g4_coverage(which: str, new: str, old: str, lo: dt.date, hi: dt.date) -> dict:
    """覆盖判据按"窗"而非"行"：现表 2026-08 起采集器把同一窗改成逐日累计多根 bar，

    行数里含这些重复 bar（旧月表 519,728 行只对应 ~418,544 个 (标的,月) 窗）。
    真覆盖 = 标的数、时间跨度、以及"旧表每个窗的末交易日 bar 在新表必须存在"（缺=0）；
    行数只报数不作门（否则等于把重复 bar 当覆盖资产）。
    """
    weekly = CC.TARGETS[which]["unit"] == "iso_week"
    grp, grp2 = ("toISOYear", "toISOWeek") if weekly else ("toYear", "toMonth")
    a = q(_SQL_COVER_AGG.format(table=new))[0]
    b = q(_SQL_COVER_AGG.format(table=old))[0]
    old_keys_rows = q(_SQL_WINDOW_KEYS_AGG.format(table=old, grp=grp, grp2=grp2))[0]
    old_keys = int(old_keys_rows[1])
    new_keys = int(q(_SQL_WINDOW_KEYS_AGG.format(table=new, grp=grp, grp2=grp2))[0][1])
    missing = int(q(_SQL_OLD_WINDOW_MISSING.format(old=old, new=new, grp=grp, grp2=grp2))[0][0])
    detail = _missing_window_detail(new, old, grp, grp2, lo, hi, missing)
    only_old = q(_SQL_SYMBOLS_ONLY_OLD.format(old=old, new=new, lo=CC.d(lo), hi=CC.d(hi)))[0][0]
    gap_new = q(_SQL_SYMBOL_GAP.format(daily=CC.DAILY_HFQ, bar=new))[0][0]
    gap_old = q(_SQL_SYMBOL_GAP.format(daily=CC.DAILY_HFQ, bar=old))[0][0]
    return {
        "new": {
            "rows": int(a[0]),
            "symbols": int(a[1]),
            "domain": [str(a[2]), str(a[3])],
            "months": int(a[4]),
            "window_keys": new_keys,
        },
        "old": {
            "rows": int(b[0]),
            "symbols": int(b[1]),
            "domain": [str(b[2]), str(b[3])],
            "months": int(b[4]),
            "window_keys": old_keys,
            "unique_key_rows": int(old_keys_rows[0]),
        },
        "old_duplicate_window_bars": int(b[0]) - old_keys,
        "old_windows_missing_in_new": missing,
        "missing_windows_attributed_halt_phantom": detail["explained"],
        "missing_windows_unexplained": detail["unexplained"],
        "missing_windows_detail": detail["rows"],
        "symbols_lost": int(only_old),
        "daily_symbols_not_in_bar_new": int(gap_new),
        "daily_symbols_not_in_bar_old": int(gap_old),
    }


def _parse_cascade_args(argv: list[str] | None):
    p = argparse.ArgumentParser(description="WO-004 级联对拍：规则考古 + 换名验收五闸")
    p.add_argument("--derive", action="store_true", help="规则考古（旧日线复现现周/月线）")
    p.add_argument("--only", choices=["weekly", "monthly"], default=None)
    p.add_argument("--start", type=dt.date.fromisoformat, default=dt.date(1990, 1, 1))
    p.add_argument("--end", type=dt.date.fromisoformat, default=None, help="对拍窗上限（默认=日线源最新日）")
    p.add_argument("--derive-start", type=dt.date.fromisoformat, default=dt.date(2019, 1, 4))
    p.add_argument(
        "--check-side",
        choices=["auto", "pre", "post"],
        default="auto",
        help="被检表选边：pre=换名前重算表 / post=换名后现表 / auto=按 legacy 存在性推断"
        "（第二轮重建下 auto 会选错边，务必显式 pre）",
    )
    p.add_argument("--json", default=None, help="报告 JSON 落盘路径（供 --swap 读门）")
    return p.parse_args(argv)


def _collect_cascade_checks(a, which_list: list[str], rep: dict) -> None:
    """五闸探针采集（derive 分支只跑考古；异常由调用方按退出码 2 处置）。"""
    for which in which_list:
        new, old, cfg = resolve_pair(which, a.check_side)
        hi = a.end or dt.date.fromisoformat(str(q(_SQL_MAX_TRADE_DATE.format(table=CC.DAILY_HFQ))[0][0]))
        if a.derive:  # 考古只碰"现表×旧日线"，重算表尚不存在（或已换名后不该参与）
            rep["checks"][f"derive_{which}"] = derive(which, a.derive_start, hi)
            continue
        lo = max(a.start, dt.date.fromisoformat(str(q(_SQL_MIN_TRADE_DATE.format(table=new))[0][0])))
        rep.setdefault("tables", {})[which] = {
            "checked": new,
            "before_swap": old,
            "state": "swapped" if new == cfg["live"] else "pre-swap",
        }
        rep["checks"][f"close_{which}"] = g1_close_consistency(which, new, lo, hi)
        rep["checks"][f"order_{which}"] = g2_order_invariants(new)
        rep["checks"][f"conserve_{which}"] = g3_conservation(which, new, lo, hi)
        rep["checks"][f"coverage_{which}"] = g4_coverage(which, new, old, lo, hi)
        rep["checks"][f"lineage_{which}"] = {
            "distribution": {str(r[0]): int(r[1]) for r in q(_SQL_LINEAGE_DIST.format(table=new))}
        }


def _write_report_json(a, rep: dict) -> None:
    if a.json:
        os.makedirs(os.path.dirname(a.json) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(rep, fh, ensure_ascii=False, indent=1, default=str)
        print(f"[json] {a.json}")


def _finish_derive(a, rep: dict) -> int:
    """考古分支收尾：打印 checks 全量 + 落 JSON，退出码恒 0（同原 main derive 腿）。"""
    print(json.dumps({k: v for k, v in rep["checks"].items()}, ensure_ascii=False, indent=1, default=str))
    _write_report_json(a, rep)
    return 0


def _coverage_gate(cov: dict) -> bool:
    """G4 门：覆盖不缩水（标的数/窗数不降 + 时间域四向包络）。"""
    return (
        bool(cov)
        and cov["symbols_lost"] == 0
        and cov["missing_windows_unexplained"] == 0
        and cov["new"]["symbols"] >= cov["old"]["symbols"]
        and cov["new"]["window_keys"] >= cov["old"]["window_keys"]
        and cov["new"]["domain"][0] <= cov["old"]["domain"][0]
        and cov["new"]["domain"][1] >= cov["old"]["domain"][1]
    )


def _set_cascade_gates(ck: dict, rep: dict, which: str) -> None:
    """单表位五门判定与守恒指标落盘（键序与判据同原 main 门段）。"""
    cl, ordr, cons, cov = (
        ck.get(f"close_{which}"),
        ck.get(f"order_{which}"),
        ck.get(f"conserve_{which}"),
        ck.get(f"coverage_{which}"),
    )
    lin = ck.get(f"lineage_{which}", {}).get("distribution", {})
    mark = CC.TARGETS[which]["mark"]
    rep["gates"][f"close_{which}"] = bool(cl) and cl["bars_without_daily_row"] == 0 and cl["close_violations"] == 0
    rep["gates"][f"order_{which}"] = (
        bool(ordr)
        and ordr["ohlc_order_violations"] == 0
        and ordr["nonpositive_prices"] == 0
        and ordr["non_finite_close"] == 0
        and ordr["duplicate_keys"] == 0
    )
    rep["gates"][f"conserve_{which}"] = (
        bool(cons) and cons["bars_without_window"] == 0 and cons["violations_in_closed_windows"] == 0
    )
    rep["metrics"][f"volume_conservation_{which}"] = {
        "total_violations": cons["volume_violations"],
        "in_closed_windows": cons["violations_in_closed_windows"],
        "in_open_window": cons["violations_in_open_window"],
        "bars": cons["bars"],
    }
    rep["gates"][f"coverage_{which}"] = _coverage_gate(cov)
    rep["gates"][f"lineage_{which}"] = bool(lin) and set(lin) == {mark}


def main(argv: list[str] | None = None) -> int:
    a = _parse_cascade_args(argv)
    which_list = [a.only] if a.only else ["weekly", "monthly"]
    rep: dict = {
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "gates": {},
        "checks": {},
        "metrics": {},
    }
    try:
        _collect_cascade_checks(a, which_list, rep)
    except Exception as e:  # noqa: BLE001
        print(f"[probe-error] {type(e).__name__}: {str(e)[:400]}")
        return 2

    if a.derive:
        return _finish_derive(a, rep)

    ck = rep["checks"]
    for which in which_list:
        _set_cascade_gates(ck, rep, which)
    print(json.dumps(rep["gates"], ensure_ascii=False))
    print(json.dumps(rep["metrics"], ensure_ascii=False))
    for k, v in rep["gates"].items():
        if not v:
            print(f"[red] {k}: {json.dumps(ck.get(k, {}), ensure_ascii=False, default=str)[:900]}")
    _write_report_json(a, rep)
    return 0 if all(rep["gates"].values()) else 1


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  M11豁免: 表族一致性验尺是只读调尺 CLI（人工/提交前触发），非常驻服务
    raise SystemExit(main())
