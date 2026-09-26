# [BLUEPRINT] MOD-METAQ-REEXAM-DSRHYTHM | docs/_working/meta_question_answers/gaps/PQ-0172_workbook.md §六向台账 + PQ-0196_workbook.md §六向台账
# [MODULE] scripts.governance.meta_question.reexam.dsrhythm.exam_dsrhythm
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pyyaml; subprocess(只读 git show); zephyr.governance.depgraph_schema (PG reader);
#                zephyr.infrastructure.database_service (CH reader 只读)
# [CONSUMERS] docs/_working/meta_question_answers/casefiles/REEXAM-DSRHYTHM.yaml（案卷由本器输出 JSON 转录）；
#             scripts/governance/meta_question/reexam/dsrhythm/writeback_dsrhythm.py（PG 回写读案卷）
# [STARTUP] manual（python scripts/governance/meta_question/reexam/dsrhythm/exam_dsrhythm.py --out <json>）
# [MATURITY] testing
# [INVARIANTS] 判据零改动：method/criterion/threshold 运行时回读 PG meta_question.exam_plan，禁本地另写；
#              两面对账：登记面取 HEAD（git show，已落地治理记录）为主、工作区并披，实测面取 CH FINAL；
#              ReplacingMergeTree 一律 FINAL（未加 FINAL 的行数含未合并重复，禁用作判定基）；
#              断档判据固定：相邻落库日间隔 > HOLE_TOLERANCE_DAYS(=12 日历天) 记为断档项，
#              12 = 已观测最长节假日型断档(11 天) + 1，不随结果调参；
#              不达标即判不达标：threshold「不一致项=0」按逐项计数判定，任一项非零即 fail，无换口径补救；
#              确定性：无随机数、时钟仅入 run_meta（不参与 payload_md5），同输入必同 payload_md5；
#              只读考试：CH/PG 全 reader，本器零写库，输出仅 --out 指定文件
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exam_plan 回读缺项→raise（禁凭记忆写判据）；未知 q_id→raise；
#                  CH/PG 连接异常→raise（fail-visible）；登记面真源文件缺失→raise
# [TESTS] 本器双跑 payload_md5 相等（重放一致性）；数字以 CH reader 复核为准
# [A_module] module_id=MOD-METAQ-REEXAM-DSRHYTHM | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""DS 节奏族复考器（PQ-0172 SL-A08 航运运价线 / PQ-0196 SL-A12 天气线）。

判据（回读 PG，不复制）：method=健康检查日志与登记节奏对账，
criterion=更新频率与延迟与 DS 册健康检查口径一致，threshold=不一致项=0。

用法：
    python scripts/governance/meta_question/reexam/dsrhythm/exam_dsrhythm.py \
        --out .runtime/tmp/st-metaq-gc-20260924/reexam_dsrhythm/exam.json
可选：--cutoff 2025-09-09 --repo D:/ZephyrAlpha
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from itertools import pairwise
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "src"))

import yaml  # noqa: E402

from zephyr.data.table_registry import TableRegistry  # noqa: E402
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402
from zephyr.shared.utils.time_utils import now_iso  # noqa: E402  （时间戳唯一真源，禁裸本机时钟）

QIDS: tuple[str, ...] = ("PQ-0172", "PQ-0196")
ACTOR = "st-metaq-gc-20260924"
HOLE_TOLERANCE_DAYS = 12  # 已观测最长节假日型断档=11 天，+1 留余量（常量，不因结果调参）
CUTOFF_DEFAULT = dt.date(2025, 9, 9)
MEASURE_BASE = "2026-09-24"

DS_BOOK = "architecture_model/data/data_sources_registry.yaml"
LINE_BOOK = "docs/_working/chain_piling_campaign/02_source_line_registry.md"
GAPS_BOOK = "src/zephyr/data/config/known_data_gaps.yaml"
TASKS_BOOK = "src/zephyr/data/config/tasks.yaml"
ALT_BOOT = "src/zephyr/alt_data/alt_source_bootstrap.py"
HEALTH_LOG_GLOB = "logs/source_health_*.log"

# ── NO-BARE-SQL：全部 SQL 集中为模块级常量 ─────────────────────────────────
# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
_T_ALT_SHIPPING_INDEX = TableRegistry().table("market_alt_shipping_index")
_T_WEATHER_DATA = TableRegistry().table("market_weather_data")
_T_TRADE_CALENDAR = TableRegistry().table("market_trade_calendar")
_SQL_EXAM_PLAN = (
    "select q_id, title, layer, line_ref, frequency, data_sources, exam_plan, status "
    "from meta_question.meta_question where q_id in ('PQ-0172','PQ-0196') order by q_id"
)
_SQL_TRISTATE = (
    "select conclusion->>'outcome', count(*) from ("
    "  select distinct on (q_id) conclusion from meta_question.meta_question_exam_result"
    "  order by q_id, created_at desc) t group by 1 order by 2 desc"
)
_SQL_SHIP_SERIES = (
    "select index_code, index_name, min(trade_date), max(trade_date), count(), uniqExact(trade_date) "
    f"from {_T_ALT_SHIPPING_INDEX} FINAL group by index_code, index_name order by index_name"
)
_SQL_SHIP_DATES = (
    "select index_name, groupArray(trade_date) from ("
    f"  select distinct index_name, trade_date from {_T_ALT_SHIPPING_INDEX} FINAL order by trade_date"
    ") group by index_name order by index_name"
)
_SQL_SHIP_INGEST = (
    f"select index_name, max(ingest_ts), count() from {_T_ALT_SHIPPING_INDEX} FINAL "
    "group by index_name order by index_name"
)
_SQL_SHIP_INGEST_DAYS = (
    f"select toDate(ingest_ts) as d, count(), uniqExact(index_name) from {_T_ALT_SHIPPING_INDEX} FINAL "
    "group by d order by d desc limit 15"
)
_SQL_WEATHER_OVERVIEW = (
    "select min(record_date), max(record_date), uniqExact(record_date), uniqExact(location_id), count() "
    f"from {_T_WEATHER_DATA} FINAL"
)
_SQL_WEATHER_DAYS = (
    "select toDate(ingest_ts, 'Asia/Shanghai') as d, count(), "
    "uniqExact(toHour(ingest_ts, 'Asia/Shanghai')), countIf(forecast_type = 'now'), "
    "countIf(forecast_type = 'forecast'), uniqExact(location_id) "
    f"from {_T_WEATHER_DATA} FINAL group by d order by d"
)
_SQL_WEATHER_UTC_DAYS = f"select uniqExact(toDate(ingest_ts)) from {_T_WEATHER_DATA} FINAL"
_SQL_OPEN_DAYS = (
    f"select cal_date from {_T_TRADE_CALENDAR} FINAL where exchange = 'SSE' and is_open = 1 order by cal_date"
)
_SQL_SHIP_TOTALS_NO_FINAL = f"select count() from {_T_ALT_SHIPPING_INDEX}"  # noqa: ch-final  ch-final豁免: 该尺被测对象就是"未合并原始行数"，用于披露 FINAL 与 raw 的计数差；加 FINAL 会抹掉被测物


def _git_show_head(repo: Path, rel: str) -> str:
    """Read a tracked file as committed in HEAD (read-only git)."""
    proc = subprocess.run(  # noqa: S603
        ["git", "show", f"HEAD:{rel}"],  # noqa: S607
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git show HEAD:{rel} 失败: {proc.stderr[:200]}")
    return proc.stdout


def _ds_entry(text: str, ds_id: str) -> dict[str, Any]:
    """Pull one data_sources entry out of the DS book YAML text."""
    doc = yaml.safe_load(text)
    for src in doc.get("data_sources", []):
        if src.get("id") == ds_id:
            extra = (src.get("policy") or {}).get("extra") or {}
            return {
                "id": ds_id,
                "status": src.get("status"),
                "rate_limit": src.get("rate_limit"),
                "coverage": src.get("coverage"),
                "coverage_reason": src.get("coverage_reason"),
                "policy_note": extra.get("note"),
                "version_declared": (doc.get("description", "")[:0] or None),
            }
    raise RuntimeError(f"DS 册无 {ds_id} 条目")


def _line_u3(text: str, line_id: str) -> str:
    """Extract the U3 bullet of a SL-* section from the 02 source-line book."""
    sec = re.split(r"\n### ", text)
    for chunk in sec:
        if chunk.startswith(line_id):
            for ln in chunk.splitlines():
                if ln.startswith("- U3"):
                    return ln[2:].strip()
    raise RuntimeError(f"02 册无 {line_id} U3")


def _gap_entries(text: str, table: str) -> list[dict[str, Any]]:
    doc = yaml.safe_load(text)
    out = []
    for g in doc.get("gaps", []) or []:
        if g.get("table") == table:
            out.append(
                {
                    "id": g.get("id"),
                    "gap_type": g.get("gap_type"),
                    "status": g.get("status"),
                    "start_date": str(g.get("start_date")),
                    "end_date": str(g.get("end_date")),
                    "date_column": g.get("date_column"),
                    "detection_threshold": g.get("detection_threshold"),
                    "root_cause": " ".join(str(g.get("root_cause", "")).split())[:260],
                }
            )
    return out


def _task_schedules(text: str, table: str) -> list[dict[str, Any]]:
    doc = yaml.safe_load(text)
    out = []
    for t in doc.get("tasks", []) or []:
        if t.get("table") == table:
            out.append(
                {"task_id": t.get("task_id"), "schedule": t.get("schedule"), "incremental": t.get("incremental")}
            )
    return out


def _alt_catalog_freq(text: str, source_id: str) -> str | None:
    m = re.search(r'source_id="' + re.escape(source_id) + r'",.*?update_frequency="([^"]+)"', text, re.S)
    return m.group(1) if m else None


def _health_log_probe(repo: Path, needles: tuple[str, ...]) -> dict[str, Any]:
    files = sorted(repo.glob(HEALTH_LOG_GLOB))
    hit: list[str] = []
    sample_sources: list[str] = []
    for f in files:
        body = f.read_text(encoding="utf-8", errors="ignore").lower()
        if any(n.lower() in body for n in needles):
            hit.append(f.name)
    if files:
        last = files[-1].read_text(encoding="utf-8", errors="ignore")
        sample_sources = sorted(
            {m.group(1) for m in re.finditer(r"[✓✗]\s+([a-z_0-9]+)\s+(?:healthy|connect_fail|stale)", last)}
        )
    return {
        "n_log_files": len(files),
        "files_mentioning_source": hit,
        "latest_log_probed_sources": sample_sources,
        "logs_first": files[0].name if files else None,
        "logs_last": files[-1].name if files else None,
    }


def _gap_profile(dates: list[dt.date]) -> dict[str, Any]:
    diffs = [(b - a).days for a, b in pairwise(dates)]
    holes = [(a, b, (b - a).days) for a, b in pairwise(dates) if (b - a).days > HOLE_TOLERANCE_DAYS]
    s = sorted(diffs)
    return {
        "n_dates": len(dates),
        "first": str(dates[0]),
        "last": str(dates[-1]),
        "adjacent_gap_median": s[len(s) // 2] if s else None,
        "adjacent_gap_max": s[-1] if s else None,
        "n_holes_gt_tol": len(holes),
        "holes_gt_tol": [[str(a), str(b), d] for a, b, d in sorted(holes, key=lambda x: -x[2])[:6]],
    }


def measure_shipping(conn: Any, open_days: list[dt.date], cutoff: dt.date) -> dict[str, Any]:
    """Per-series trade-date rhythm of c1_market.alt_shipping_index (FINAL)."""
    series: dict[str, list[dt.date]] = {}
    for name, dates in conn.execute(_SQL_SHIP_DATES):
        series[name] = sorted(dates)
    out: dict[str, Any] = {"series": {}, "totals_no_final": ch_total_raw(conn)}
    open_set = set(open_days)
    for code, name, mn, mx, rows, uq in conn.execute(_SQL_SHIP_SERIES):
        ds = series[name]
        pre = [d for d in ds if d <= cutoff]
        weekdays = [
            mn + dt.timedelta(days=i) for i in range((mx - mn).days + 1) if (mn + dt.timedelta(days=i)).weekday() < 5
        ]
        exp_open = [d for d in open_set if mn <= d <= mx]
        prof = _gap_profile(ds)
        prof_pre = _gap_profile(pre) if len(pre) > 1 else {"n_holes_gt_tol": 0}
        out["series"][name] = {
            "index_code": code,
            "rows_final": rows,
            "distinct_dates": uq,
            "min": str(mn),
            "max": str(mx),
            "rows_pre_cutoff": len(pre),
            "weekday_span": len(weekdays),
            "weekday_missing": len(set(weekdays) - set(ds)),
            "sse_open_days": len(exp_open),
            "sse_open_missing": len(set(exp_open) - set(ds)),
            "hole_profile_full": prof,
            "hole_profile_pre_cutoff": prof_pre,
            "stale_days_at_measure_base": (dt.date.fromisoformat(MEASURE_BASE) - mx).days,
        }
    out["ingest_last_by_series"] = {n: [str(t), c] for n, t, c in conn.execute(_SQL_SHIP_INGEST)}
    out["ingest_recent_days"] = [[str(d), n, u] for d, n, u in conn.execute(_SQL_SHIP_INGEST_DAYS)]
    return out


def measure_weather(conn: Any, open_days: list[dt.date], cutoff: dt.date) -> dict[str, Any]:
    """Daily-batch rhythm of c1_market.weather_data (FINAL, Asia/Shanghai day cut)."""
    mn, mx, rec_days, locs, rows = conn.execute(_SQL_WEATHER_OVERVIEW)[0]
    days = conn.execute(_SQL_WEATHER_DAYS)
    present = [r[0] for r in days]
    span = (mx - mn).days + 1
    pset = set(present)
    missing = [str(mn + dt.timedelta(days=i)) for i in range(span) if (mn + dt.timedelta(days=i)) not in pset]
    open_set = set(open_days)
    multi_hour = [str(d) for d, _n, _h, _w, _f, _l in days if _h > 1]
    incomplete = [[str(d), n, w, f] for d, n, _h, w, f, _l in days if n < 320]
    return {
        "record_date_min": str(mn),
        "record_date_max": str(mx),
        "record_days": rec_days,
        "distinct_locations": locs,
        "rows_final": rows,
        "ingest_days_tz_shanghai": len(present),
        "ingest_days_tz_utc": conn.execute(_SQL_WEATHER_UTC_DAYS)[0][0],
        "calendar_span_days": span,
        "missing_calendar_days": len(missing),
        "missing_calendar_day_list": missing,
        "missing_sse_open_days": sorted(str(d) for d in open_set if mn <= d <= mx and d not in pset),
        "days_with_more_than_one_batch_hour": multi_hour,
        "incomplete_batch_days": incomplete,
        "rows_per_day": {
            "min": min(r[1] for r in days),
            "max": max(r[1] for r in days),
            "avg": round(sum(r[1] for r in days) / len(days), 2),
        },
        "stale_days_at_measure_base": (dt.date.fromisoformat(MEASURE_BASE) - max(present)).days,
        "rows_pre_cutoff": 0 if mn > cutoff else None,
        "pre_cutoff_note": f"表首记录日 {mn} 晚于闭卷切点 {cutoff}，闭卷窗内零行",
    }


def ch_total_raw(conn: Any) -> int:
    """Raw (non-FINAL) row count — disclosed only, to show the FINAL-vs-raw delta."""
    return int(conn.execute(_SQL_SHIP_TOTALS_NO_FINAL)[0][0])


def reconcile_shipping(reg: dict[str, Any], msr: dict[str, Any], health: dict[str, Any]) -> list[dict[str, Any]]:
    """Enumerate 登记断言×实测违背 items for PQ-0172 (each unexplained break = 1 item)."""
    items: list[dict[str, Any]] = []
    five = [
        "波罗的海综合运价指数",
        "波罗的海好望角型船运价指数",
        "波罗的海超级大灵便型船指数",
        "原油运价指数",
        "成品油运价指数",
    ]
    for name in five:
        s = msr["series"][name]
        if s["hole_profile_full"]["n_holes_gt_tol"] > 0:
            items.append(
                {
                    "item": f"{name}({s['index_code']}) 交易日内断档 > {HOLE_TOLERANCE_DAYS} 天 共 "
                    f"{s['hole_profile_full']['n_holes_gt_tol']} 处，最大 "
                    f"{s['hole_profile_full']['holes_gt_tol'][0][2]} 天",
                    "assertion": reg["u3_02_head"],
                    "assertion_source": "02 册 SL-A08 U3（HEAD）日更（交易日）五序列",
                    "measured": f"断档清单 {s['hole_profile_full']['holes_gt_tol'][:3]}",
                    "attribution": "实测断供（登记面无对应 known_data_gaps 条目）",
                }
            )
    if not reg["ds_coverage_head_has_discontinued_note"]:
        items.append(
            {
                "item": "DS 册（HEAD）coverage 仍作「BDI 1988起+六指数约2006起」，"
                "未标注 国际集装箱租船指数(HRCI 2011-08-23 止更 211 行)/灵便型船综合运价指数"
                "(BHMI 全史 1 行) 断供——WO-010 补注仅存工作区未落 HEAD",
                "assertion_source": DS_BOOK,
                "measured": f"工作区已注记={reg['ds_coverage_worktree_has_discontinued_note']}；"
                f"HEAD 未注记；known_data_gaps(HEAD) accepted 条目数="
                f"{len([g for g in reg['gaps_head'] if 'shipping' in str(g['id'])])}",
                "attribution": "登记面缺项（保护路径待审批，非采集故障）",
            }
        )
    if not health["files_mentioning_source"]:
        items.append(
            {
                "item": f"method 要求的「健康检查日志」面对本源零覆盖：{health['n_log_files']} 份 "
                f"source_health_*.log（{health['logs_first']}~{health['logs_last']}）无 akshare_alt/"
                "alt_shipping_index 任何记录，alt_source_health_manager 调度层未接线",
                "assertion_source": "src/zephyr/alt_data/alt_source_bootstrap.py（健康探针调度层「属后续批」）",
                "measured": f"最新日志探测源集={health['latest_log_probed_sources']}",
                "attribution": "登记/监控面缺项（对账缺日志侧，节奏仅能由 CH 实测代证）",
            }
        )
    return items


def reconcile_weather(
    reg: dict[str, Any], msr: dict[str, Any], health: dict[str, Any], pg_freq: str | None
) -> list[dict[str, Any]]:
    """Enumerate items for PQ-0196."""
    items: list[dict[str, Any]] = []
    if msr["missing_calendar_days"] > 0:
        items.append(
            {
                "item": f"「每日积累/日批」与实测不符：{msr['record_date_min']}..{msr['record_date_max']} "
                f"共 {msr['calendar_span_days']} 日历日仅 {msr['ingest_days_tz_shanghai']} 日有批次，"
                f"漏采 {msr['missing_calendar_days']} 日（其中 SSE 交易日 "
                f"{len(msr['missing_sse_open_days'])} 日）",
                "assertion": reg["ds_note_head"] + " / " + reg["u3_02_head"],
                "assertion_source": DS_BOOK + " + 02 册 SL-A12 U3（HEAD）",
                "measured": f"漏采日清单 {msr['missing_calendar_day_list'][:6]}…（全量见 evidence）",
                "attribution": "实测断供（known_data_gaps weather_data_sparse_31_days 登记的是"
                "「记录日深度 31 日」而非逐日漏采清单，2026-09-19 登记后仍新增漏采日）",
            }
        )
    if msr["incomplete_batch_days"]:
        items.append(
            {
                "item": f"{len(msr['incomplete_batch_days'])} 个批次日内容不完整（应 40 城×(1 实况+7 预报)=320 行）："
                f"{msr['incomplete_batch_days']}",
                "assertion": reg["ds_coverage_head"],
                "assertion_source": DS_BOOK + " coverage「40 城实时天气 + 7 天预报」",
                "measured": "forecast_type='forecast' 行数 0（三日）/ 273（一日）",
                "attribution": "实测断供（预报支路偶发零行，登记面无对应缺口条目）",
            }
        )
    if pg_freq and pg_freq.strip().lower() != "daily":
        items.append(
            {
                "item": f"PG meta_question.frequency='{pg_freq}' 与 DS 册「每日积累」/实测「每日单批」矛盾"
                "（题面 U3 亦仍表述为实时/小时级）",
                "assertion": f"meta_question.frequency={pg_freq}",
                "assertion_source": "meta_question.meta_question（不可 UPDATE，纯追加体制下待后续登记收敛）",
                "measured": f"每日单批（>1 批/日的日数={len(msr['days_with_more_than_one_batch_hour'])}）",
                "attribution": "口径表述差异（登记面内部矛盾）",
            }
        )
    if not health["files_mentioning_source"]:
        items.append(
            {
                "item": f"健康检查日志面对 qweather 零覆盖：{health['n_log_files']} 份 source_health_*.log "
                "无 qweather/weather_data 任何记录",
                "assertion_source": "logs/source_health_*.log",
                "measured": f"最新日志探测源集={health['latest_log_probed_sources']}",
                "attribution": "登记/监控面缺项",
            }
        )
    return items


def load_exam_plan() -> dict[str, Any]:
    conn = get_depgraph_pg_connection()
    cur = conn.cursor()
    cur.execute(_SQL_EXAM_PLAN)
    cols = [d.name for d in cur.description]
    plan = {r[0]: dict(zip(cols, r, strict=True)) for r in cur.fetchall()}
    cur.execute(_SQL_TRISTATE)
    tri = {str(k): v for k, v in cur.fetchall()}
    cur.close()
    conn.close()
    for q in QIDS:
        ep = (plan.get(q) or {}).get("exam_plan") or {}
        if not all(ep.get(k) for k in ("method", "criterion", "threshold")):
            raise RuntimeError(f"{q} exam_plan 判据不齐，禁凭记忆补写")
    return {"plan": plan, "tristate": tri, "tristate_sum": sum(tri.values())}


def load_registered(repo: Path) -> dict[str, Any]:
    """Both HEAD (landed) and worktree readings of the registered rhythm."""
    head_ds = _git_show_head(repo, DS_BOOK)
    wt_ds = (repo / DS_BOOK).read_text(encoding="utf-8")
    head_line = _git_show_head(repo, LINE_BOOK)
    wt_line = (repo / LINE_BOOK).read_text(encoding="utf-8")
    head_gaps = _git_show_head(repo, GAPS_BOOK)
    head_tasks = _git_show_head(repo, TASKS_BOOK)
    head_alt = _git_show_head(repo, ALT_BOOT)
    ship_h = _ds_entry(head_ds, "DS-AKSHARE-ALT")
    ship_w = _ds_entry(wt_ds, "DS-AKSHARE-ALT")
    wx_h = _ds_entry(head_ds, "DS-QWEATHER")
    reg = {
        "shipping_ds_head": ship_h,
        "shipping_ds_worktree": ship_w,
        "ds_coverage_head_has_discontinued_note": "charter_discontinued" in (ship_h["coverage"] or ""),
        "ds_coverage_worktree_has_discontinued_note": "charter_discontinued" in (ship_w["coverage"] or ""),
        "u3_02_head": _line_u3(head_line, "SL-A08"),
        "u3_02_worktree": _line_u3(wt_line, "SL-A08"),
        "wx_u3_02_head": _line_u3(head_line, "SL-A12"),
        "weather_ds_head": wx_h,
        "ds_note_head": wx_h["policy_note"] or "",
        "ds_coverage_head": wx_h["coverage"] or "",
        "gaps_head": _gap_entries(head_gaps, _T_ALT_SHIPPING_INDEX),
        "gaps_head_weather": _gap_entries(head_gaps, _T_WEATHER_DATA),
        "tasks_head_shipping": _task_schedules(head_tasks, _T_ALT_SHIPPING_INDEX),
        "tasks_head_weather": _task_schedules(head_tasks, _T_WEATHER_DATA),
        "alt_catalog_freq_shipping": _alt_catalog_freq(head_alt, "alt_shipping_index"),
        "alt_catalog_freq_weather": _alt_catalog_freq(head_alt, "heat_weather"),
        "head_sha": subprocess.run(  # noqa: S603, S607
            ["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True, check=True
        ).stdout.strip(),
    }
    return reg


def exam(cutoff: dt.date = CUTOFF_DEFAULT, repo: str | Path = "D:/ZephyrAlpha") -> dict[str, Any]:
    repo_p = Path(repo)
    pg = load_exam_plan()
    reg = load_registered(repo_p)
    ch = DatabaseService().get_clickhouse_conn(role="reader")
    open_days = [r[0] for r in ch.execute(_SQL_OPEN_DAYS)]
    ship = measure_shipping(ch, open_days, cutoff)
    wx = measure_weather(ch, open_days, cutoff)
    h_ship = _health_log_probe(repo_p, ("akshare_alt", "alt_shipping", "shipping"))
    h_wx = _health_log_probe(repo_p, ("qweather", "weather"))

    items_ship = reconcile_shipping(reg, ship, h_ship)
    items_wx = reconcile_weather(reg, wx, h_wx, pg["plan"]["PQ-0196"].get("frequency"))

    def _verdict(items: list[dict[str, Any]]) -> str:
        return "pass" if len(items) == 0 else "fail"

    payload: dict[str, Any] = {
        "actor": ACTOR,
        "engine": "scripts/governance/meta_question/reexam/dsrhythm/exam_dsrhythm.py",
        "cutoff": str(cutoff),
        "measure_base": MEASURE_BASE,
        "hole_tolerance_days": HOLE_TOLERANCE_DAYS,
        "head_sha": reg["head_sha"],
        "pg_baseline": {k: pg[k] for k in ("tristate", "tristate_sum")},
        "registered": reg,
        "measured": {"shipping": ship, "weather": wx},
        "health_log": {"shipping": h_ship, "weather": h_wx},
        "exams": {
            "PQ-0172": {
                "exam_plan_ref": pg["plan"]["PQ-0172"]["exam_plan"],
                "title": pg["plan"]["PQ-0172"]["title"],
                "inconsistency_items": items_ship,
                "n_items": len(items_ship),
                "outcome": _verdict(items_ship),
                "fail_type": None if not items_ship else "infra",
                "pre_cutoff_holds": all(
                    s["hole_profile_pre_cutoff"].get("n_holes_gt_tol", 0) > 0
                    for n, s in ship["series"].items()
                    if n in ("原油运价指数", "成品油运价指数", "波罗的海超级大灵便型船指数")
                ),
            },
            "PQ-0196": {
                "exam_plan_ref": pg["plan"]["PQ-0196"]["exam_plan"],
                "title": pg["plan"]["PQ-0196"]["title"],
                "inconsistency_items": items_wx,
                "n_items": len(items_wx),
                "outcome": _verdict(items_wx),
                "fail_type": None if not items_wx else "infra",
                "pre_cutoff_holds": False,
            },
        },
    }
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    payload["payload_md5"] = hashlib.md5(blob.encode("utf-8")).hexdigest()
    payload["run_meta"] = {"at": now_iso(), "cutoff_param": str(cutoff)}
    return payload


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cutoff", default=str(CUTOFF_DEFAULT))
    ap.add_argument("--repo", default="D:/ZephyrAlpha")
    args = ap.parse_args()
    res = exam(cutoff=dt.date.fromisoformat(args.cutoff), repo=args.repo)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    for q, ex in sorted(res["exams"].items()):
        print(f"{q}: 不一致项={ex['n_items']} -> {ex['outcome']} (fail_type={ex['fail_type']})")
        for it in ex["inconsistency_items"]:
            print("   -", it["item"][:150])
    print("payload_md5:", res["payload_md5"], "| PG tri-state:", res["pg_baseline"])
    print("written:", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
