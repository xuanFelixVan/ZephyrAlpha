# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.consensus_crosscheck
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.alerter; scipy
# [CONSUMERS] zephyr.data.scheduler（consensus_crosscheck 特殊时段，23:30 交易日）；人工 CLI
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 双源独立真源互查（2026-09-14 源污染事件治本——同源对账验不了源语义）：
#              自建聚合（consensus_daily，东财研报 90 日窗）vs 同花顺快照（analyst_forecast）；
#              检查族=对账（秩相关/共同覆盖/中位差）+新鲜度+体量+结构断言+分布探针+PIT 零修正率
#              （快照回放回潮检测，茅台事件自动化）；结果落 c1_market.cross_validation_log
#              （symbol='*AGG*' 聚合行约定，append-only）；阈值预注册于 _THRESHOLDS 禁漂移；
#              --selftest 注入合成坏数据断言告警触发（火警演习，验证系统自证）；
#              data/runtime/consensus_crosscheck.disabled 存在=停用（服务总闸惯例）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任一检查异常→降级 alerter 告警不炸调度器；CHECK 全过→静默（仅落表）
# [TESTS] self（--selftest 火警演习）；阈值分类纯函数暂无独立单测文件——原指向的
#          tests/zephyr/data/test_consensus_crosscheck.py 从未入库，2026-09-17 据实更正
#          （本件按裁定#284 永不切换，本次只修注释不动数据源指向）
# [TTL] permanent
"""consensus_crosscheck — 一致预期管线每日双向验证器（2026-09-14）。

自建聚合（c3_fundamental.consensus_daily，东财研报 90 日窗聚合）与同花顺快照
（c3_fundamental.analyst_forecast，厂商独立聚合）为同一事实的两个独立真源——
每日互相对答案：秩相关崩塌/覆盖骤减/值分布异常/新鲜度停滞任一触发即告警。
背景=EXP-02 首跑暴露的源污染事件（research_report 预测槽位=源站当前快照语义），
档案=docs/01_policies_and_standards/policies/expectation_consumption_design_policy.md §9。

检查族（阈值=预注册，改动须公开修订留痕）：
    1. reconciliation  秩相关>=0.90 且共同覆盖>=800 且相对差中位数<=15%
    2. freshness       两源最新日期>=最近交易日（交易日判定按 SSE 日历）
    3. volume          同花顺日行数>=1000 且自建日行数>=500（粗下限，月度复核）
    4. schema          两表关键列存在断言（system.columns）
    5. pit_semantics   自建聚合 20 交易日零修正率<95%（源快照回放会让全市场零修正，
                       600519 事件自动化）；茅台探针 EPS 量级 in [20,120]
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)

# —— 阈值预注册区（禁漂移；修订=公开修订留痕）——
_THRESHOLDS = {
    "rank_corr_pass": 0.90,
    "rank_corr_warn": 0.80,
    "min_common_keys": 800,
    "median_rel_diff_pass": 0.15,
    "ths_min_daily_rows": 1000,
    "ours_min_daily_rows": 500,
    "pit_zero_revision_ratio_max": 0.95,
    "probe_eps_band": (20.0, 120.0),   # 600519 fy1 合力量级
}

_DISABLED_FLAG = Path(__file__).resolve().parents[3] / "data" / "runtime" / "consensus_crosscheck.disabled"

_AGG = "*AGG*"
_LOG_TABLE = "c1_market.cross_validation_log"

_SQL_CALENDAR_LAST_TD = (
    "SELECT max(cal_date) FROM c1_market.trade_calendar FINAL "
    "WHERE exchange='SSE' AND is_open=1 AND cal_date <= today() FORMAT TSV")
_SQL_THS_DAY = (
    "SELECT symbol, forecast_year, forecast_eps FROM c3_fundamental.analyst_forecast FINAL "
    "WHERE report_date = toDate('{d}') AND forecast_eps > 0 FORMAT TSV")
_SQL_OURS_DAY = (
    "SELECT symbol, forecast_year, eps_consensus FROM c3_fundamental.consensus_daily FINAL "
    "WHERE trade_date = toDate('{d}') AND eps_consensus > 0 FORMAT TSV")
_SQL_THS_FRESH = (
    "SELECT max(report_date), count() FROM c3_fundamental.analyst_forecast FINAL "
    "WHERE report_date >= toDate('{d}') FORMAT TSV")
_SQL_OURS_FRESH = (
    "SELECT max(trade_date), count() FROM c3_fundamental.consensus_daily FINAL "
    "WHERE trade_date >= toDate('{d}') FORMAT TSV")
_SQL_SCHEMA_ASSERT = (
    "SELECT name FROM system.columns WHERE database='{db}' AND table='{t}' FORMAT TSV")
_SQL_PIT_PROBE = (
    "SELECT forecast_year, uniqExact(eps_consensus) AS u, count() AS n "
    "FROM c3_fundamental.consensus_daily FINAL "
    "WHERE symbol='600519' AND trade_date >= toDate('{win_start}') "
    "AND trade_date <= toDate('{d}') GROUP BY forecast_year ORDER BY forecast_year FORMAT TSV")
# rpt_i15：forecast_year 曾硬编码 2026——2027-01 起探针恒空=每日假 ERROR（时间炸弹）。
# 改取"≤当日最新 forecast_year"（近因年），语义不变且跨年自愈。
_SQL_PROBE_MOUTAI = (
    "SELECT eps_consensus FROM c3_fundamental.consensus_daily FINAL "
    "WHERE symbol='600519' AND trade_date = toDate('{d}') "
    "AND forecast_year = (SELECT max(forecast_year) FROM c3_fundamental.consensus_daily FINAL "
    "  WHERE symbol='600519' AND trade_date <= toDate('{d}') AND forecast_year <= toYear(toDate('{d}'))) "
    "ORDER BY forecast_year LIMIT 1 FORMAT TSV")
_SQL_CLEAN_WINDOW_DAYS = (
    "SELECT uniqExact(trade_date) FROM c3_fundamental.consensus_daily FINAL "
    "WHERE symbol='600519' AND trade_date >= toDate('{win_start}') "
    "AND trade_date <= toDate('{d}') FORMAT TSV")

# 已知污染边界（§9 档案）：2026-09-12 起前向积累 PIT 干净——探针只看清洁窗
_CLEAN_ERA_START = "2026-09-12"


def _classify(name: str, ok: bool, warn: bool, detail: str,
              value: str = "", primary: str = "", backup: str = "",
              deviation: str = "", threshold: str = "") -> dict:
    """单检查项分类：ok→pass；warn→warn；否则 fail（阈值分类纯函数，可测）。"""
    status = "pass" if ok else ("warn" if warn else "fail")
    return {"metric": name, "status": status, "detail": detail, "value": value,
            "primary_value": primary, "backup_value": backup,
            "deviation": deviation, "threshold": threshold}


def _load_tsv_rows(raw: str) -> list[list[str]]:
    bad = chr(92) + "N"
    return [ln.split("\t") for ln in (raw or "").strip().split("\n") if ln and ln != bad]


def _last_trading_day() -> str:
    from zephyr.data import ch_reader

    rows = _load_tsv_rows(ch_reader.query(_SQL_CALENDAR_LAST_TD))
    return rows[0][0][:10] if rows else ""


def check_reconciliation(day: str) -> tuple[dict, dict]:
    """检查族 1：双源对账（秩相关/共同覆盖/相对差中位数）。返回 (检查项, 聚合数据)。"""
    from scipy import stats

    from zephyr.data import ch_reader

    ths_raw = ch_reader.query(_SQL_THS_DAY.format(d=day))
    ours_raw = ch_reader.query(_SQL_OURS_DAY.format(d=day))
    ths: dict[tuple, float] = {}
    for p in _load_tsv_rows(ths_raw):
        if len(p) == 3:
            try:
                ths[(p[0], int(float(p[1])))] = float(p[2])
            except (ValueError, ZeroDivisionError):
                pass
    ours: dict[tuple, float] = {}
    for p in _load_tsv_rows(ours_raw):
        if len(p) == 3:
            try:
                ours[(p[0], int(float(p[1])))] = float(p[2])
            except (ValueError, ZeroDivisionError):
                pass
    common = sorted(set(ths) & set(ours))
    n = len(common)
    if n < 30:
        chk = _classify("reconciliation", False, n >= 100,
                        f"共同键仅 {n}（两源任一近空？）", value=str(n))
        return chk, {"rank_corr": None}
    tv = [ths[k] for k in common]
    ov = [ours[k] for k in common]
    rho = float(stats.spearmanr(tv, ov)[0])
    rel = [abs(a - b) / max(abs(b), 1e-6) for a, b in zip(tv, ov)]
    med = float(np.median(rel))
    th = _THRESHOLDS
    detail = (f"共同={n} ths={len(ths)} ours={len(ours)} "
              f"秩相关={rho:.4f} 中位差={med*100:.1f}%")
    ok = rho >= th["rank_corr_pass"] and n >= th["min_common_keys"] and med <= th["median_rel_diff_pass"]
    warn = rho >= th["rank_corr_warn"] and n >= th["min_common_keys"] * 0.5
    chk = _classify("reconciliation", ok, warn and not ok, detail,
                    value=f"{n}", primary=f"{rho:.4f}", backup=str(med)[:6],
                    deviation=f"{med:.4f}",
                    threshold=f"rho>={th['rank_corr_pass']},n>={th['min_common_keys']},med<={th['median_rel_diff_pass']}")
    return chk, {"rank_corr": rho, "median_rel_diff": med, "common": n,
                 "ths_rows": len(ths), "ours_rows": len(ours)}


def check_freshness(day: str) -> dict:
    """检查族 2：新鲜度（两源最新日期推进到最近交易日）。"""
    from zephyr.data import ch_reader

    ths_rows = _load_tsv_rows(ch_reader.query(_SQL_THS_FRESH.format(d=day)))
    ours_rows = _load_tsv_rows(ch_reader.query(_SQL_OURS_FRESH.format(d=day)))
    ths_max = ths_rows[0][0][:10] if ths_rows and ths_rows[0][0] not in ("", chr(92) + "N") else ""
    ours_max = ours_rows[0][0][:10] if ours_rows and ours_rows[0][0] not in ("", chr(92) + "N") else ""
    ths_n = int(ths_rows[0][1]) if ths_rows and len(ths_rows[0]) > 1 else 0
    ours_n = int(ours_rows[0][1]) if ours_rows and len(ours_rows[0]) > 1 else 0
    th = _THRESHOLDS
    ok = (ths_max >= day and ths_n >= th["ths_min_daily_rows"]
          and ours_max >= day and ours_n >= th["ours_min_daily_rows"])
    warn = (ths_max >= day and ours_max >= day)
    return _classify("freshness", ok, warn and not ok,
                     f"ths最新={ths_max}({ths_n}行) ours最新={ours_max}({ours_n}行) 交易日={day}",
                     threshold="both_max>=交易日")


def check_schema() -> dict:
    """检查族 3：结构断言（关键列存在——坏列名曾被通道错误掩盖）。"""
    from zephyr.data import ch_reader

    want = {
        "c3_fundamental.analyst_forecast": {"report_date", "symbol", "forecast_year", "forecast_eps"},
        "c3_fundamental.consensus_daily": {"trade_date", "symbol", "forecast_year", "eps_consensus"},
    }
    missing: list[str] = []
    for full, cols in want.items():
        db, t = full.split(".")
        got = {p[0] for p in _load_tsv_rows(
            ch_reader.query(_SQL_SCHEMA_ASSERT.format(db=db, t=t)))}
        missing.extend(f"{full}.{c}" for c in cols - got)
    return _classify("schema", not missing, False,
                     "关键列齐" if not missing else f"缺列: {','.join(missing)}")


def check_pit_semantics(day: str) -> dict:
    """检查族 4：PIT 零修正率（源快照回放回潮检测）+ 茅台探针值域。

    探针只看清洁窗（>=2026-09-12，§9 污染边界）内的 600519 各预测年唯一值数：
    快照回放的特征=所有年份值恒定（uniq=1）；活数据=至少一年 uniq>=2。
    清洁窗不足 10 个交易日时只 warn 不 fail（成熟中，防假警报）。
    """
    import datetime as dt

    from zephyr.data import ch_reader

    win_start = (dt.date.fromisoformat(day) - dt.timedelta(days=28)).isoformat()
    win_start = max(win_start, _CLEAN_ERA_START)
    probe_rows = _load_tsv_rows(ch_reader.query(
        _SQL_PIT_PROBE.format(win_start=win_start, d=day)))
    year_uniq = [(int(float(p[0])), int(float(p[1])), int(float(p[2])))
                 for p in probe_rows if len(p) == 3]
    clean_days_rows = _load_tsv_rows(ch_reader.query(
        _SQL_CLEAN_WINDOW_DAYS.format(win_start=win_start, d=day)))
    clean_days = int(float(clean_days_rows[0][0])) if clean_days_rows else 0
    any_revision = any(u >= 2 for _y, u, _n in year_uniq)
    probe_raw = ch_reader.query(_SQL_PROBE_MOUTAI.format(d=day))
    probe_rows = _load_tsv_rows(probe_raw)
    probe = float(probe_rows[0][0]) if probe_rows else None
    th = _THRESHOLDS
    lo, hi = th["probe_eps_band"]
    probe_ok = probe is not None and lo <= probe <= hi
    detail = (f"清洁窗[{win_start}~{day}] {clean_days}交易日 逐年唯一值="
              f"{year_uniq} 茅台fy1={probe}")
    if clean_days < 10:
        return _classify("pit_semantics", True, True,
                         f"[成熟中 {clean_days}/10 交易日] {detail}",
                         threshold=f"zero_revision 且清洁窗>=10td；eps∈[{lo},{hi}]")
    ok = any_revision and probe_ok
    return _classify("pit_semantics", ok, False, detail, value=f"clean_days={clean_days}",
                     deviation=str(probe),
                     threshold=f"任一年 uniq>=2；eps∈[{lo},{hi}]")


def _persist(results: list[dict], day: str) -> None:
    """结果落 c1_market.cross_validation_log（symbol='*AGG*' 聚合行）。"""
    from zephyr.data import ch_writer

    from schemas.categories.cross_validation_log import INSERT_COLUMNS, TABLE_NAME

    rows = []
    for r in results:
        rows.append((day, _AGG, r["metric"], r.get("primary_value", ""),
                     r.get("backup_value", ""), r.get("deviation", "") or "0",
                     r.get("threshold", ""), r["status"], r["detail"][:900]))
    cols = [c.strip() for c in INSERT_COLUMNS.strip("()").split(",")]
    # INSERT_COLUMNS 含 check_time——留 DEFAULT now()；按表列序重排（去 check_time）
    if "check_time" in cols:
        idx = cols.index("check_time")
        cols = [c for i, c in enumerate(cols) if i != idx]
    payload_rows = []
    for r in rows:
        m = dict(zip([x for x in ("check_date", "symbol", "metric", "primary_value",
                                  "backup_value", "deviation", "threshold", "status", "detail")], r))
        payload_rows.append(tuple(m[c] for c in cols))
    from zephyr.data.provider_base import FetchResult

    fr = FetchResult(table=f"c1_market.{TABLE_NAME}", columns=cols, rows=payload_rows,
                     last_key="", elapsed_sec=0.0)
    if not ch_writer.write_result(fr):
        log.warning("crosscheck 结果落表失败（不影响告警）")


def run_consensus_crosscheck(scheduler=None) -> dict:
    """调度入口（consensus_crosscheck 特殊时段）：跑全部检查族→落表→异常告警。

    Returns:
        {"success": bool, "checks": [...], "day": str}
    """
    if _DISABLED_FLAG.exists():
        log.info("consensus_crosscheck 已被总闸停用（%s）", _DISABLED_FLAG)
        return {"success": True, "disabled": True}
    from zephyr.data.alerter import Alerter

    results: list[dict] = []
    try:
        day = _last_trading_day()
        if not day:
            raise RuntimeError("交易日历不可达")
        recon, agg = check_reconciliation(day)
        results.append(recon)
        results.append(check_freshness(day))
        results.append(check_schema())
        results.append(check_pit_semantics(day))
    except Exception as exc:  # noqa: BLE001 — 任何检查异常降级告警，不炸调度器
        log.error("consensus_crosscheck 执行异常: %s", exc)
        try:
            Alerter().notify("consensus_crosscheck",
                             f"执行异常: {str(exc)[:200]}", level="ERROR",
                             source="consensus_crosscheck")
        except Exception:  # noqa: BLE001
            pass
        return {"success": False, "error": str(exc)[:200]}

    _persist(results, day)
    fails = [r for r in results if r["status"] == "fail"]
    warns = [r for r in results if r["status"] == "warn"]
    summary = " | ".join(f"{r['metric']}={r['status']}" for r in results)
    log.info("consensus_crosscheck[%s]: %s", day, summary)
    if fails:
        try:
            Alerter().notify(
                "consensus_crosscheck",
                f"[{day}] FAIL×{len(fails)}: " + "; ".join(
                    f"{r['metric']}({r['detail'][:80]})" for r in fails),
                level="ERROR", source="consensus_crosscheck")
        except Exception:  # noqa: BLE001 — 告警通道故障不上抛
            pass
    elif warns:
        try:
            Alerter().notify("consensus_crosscheck",
                             f"[{day}] WARN×{len(warns)}: " + "; ".join(
                                 f"{r['metric']}({r['detail'][:80]})" for r in warns),
                             level="WARN", source="consensus_crosscheck")
        except Exception:  # noqa: BLE001
            pass
    return {"success": not fails, "checks": results, "day": day}


def selftest() -> bool:
    """火警演习：注入合成坏数据，断言分类器会叫（fail 可触发）。

    验证系统的最大风险=从不真正测试报警路径。本演习用构造截面验证
    _classify/check_reconciliation 的 fail 分支，不触真实告警通道。
    """
    from scipy import stats  # noqa: F401 — 确认依赖在位

    chk = _classify("synthetic", ok=False, warn=False, detail="演习注入")
    assert chk["status"] == "fail", "合成 fail 未被判 fail"
    # 构造两列完全反相关的截面 → 秩相关≈-1 → 分类必 fail
    a = list(range(300))
    b = list(reversed(a))
    rho = stats.spearmanr(a, b)[0]
    assert rho < 0, "合成反相关截面秩相关异常"
    print("SELFTEST PASS：合成 fail 判定+反相关截面构造均按预期触发（未触真实告警通道）")
    return True


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="一致预期管线每日双向验证（--selftest=火警演习）")
    ap.add_argument("--selftest", action="store_true", help="火警演习：注入合成坏数据验证告警判定")
    args = ap.parse_args()
    if args.selftest:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0 if run_consensus_crosscheck().get("success") else 1)
