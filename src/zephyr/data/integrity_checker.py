# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.integrity_checker
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.backfill_checker (_discover_backfill_tables); zephyr.data.ch_reader
# [CONSUMERS] zephyr.data.scheduler.run_schedule("integrity_check")
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 复用backfill_checker动态发现全表; 只检测不补下载; 告警通过alerter; 结果记录progress_store
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH查询失败->该表标记unhealthy; 无scheduler->只log不记录
# [TESTS] tests/zephyr/data/test_integrity_checker.py
# [A_module] module_id=MOD-GOV-integrity_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
数据完整性巡检器——每天盘后检测全表当日数据是否达标。

设计理念（数据韧性三层机制 §3）：
  - 复用 backfill_checker._discover_backfill_tables() 动态发现全表
  - 新增表只要在 tasks.yaml 注册任务，自动纳入巡检覆盖范围
  - 只检测不补下载（补下载由 weekend_backfill / 手动触发负责）
  - 阈值来自历史7天日均行数×0.5（与 backfill_checker 一致）
  - T+1 披露族（_T1_LAG_JUDGED_TABLES，现为 margin_trading）按"滞后≥2 开市日"判警
    （DU-03 案治本，先例=decision_chain_sentinel），行数下限降为次要参考列

调用方式：
  scheduler.run_schedule("integrity_check") → run_daily_check(scheduler)
  也可独立调用：python -c "from zephyr.data.integrity_checker import run_daily_check; run_daily_check()"

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/integrity_checker.yaml
"""

from __future__ import annotations

import datetime
import logging
import subprocess
import sys

from zephyr.data import ch_reader
from zephyr.data.backfill_checker import _discover_backfill_tables
from zephyr.shared.io.paths import REPO_ROOT

discover_backfill_tables = _discover_backfill_tables  # public alias（Stage 4 公共化）


log = logging.getLogger(__name__)

# SQL 模板（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_COUNT_TODAY = "SELECT count() FROM {table} WHERE {date_col}=toDate('{d_str}')"

# ---- T+1 披露族滞后判警（12 号文 DU-03 案，2026-09-25） ----
# 病根：margin_trading 的披露源是 T+1（D 日数据 D+1 日早间披露），当日行数对"今日"恒为 0，
# 按"当日行数 vs 7日均阈值"判警等于永久误报（data/failures 实证 42/42 全零 "0 < ~2052"，
# 每交易日一件；真断 4 交易日与常态不可分辨）。判警口径改为：max(date_col) 距参照日滞后
# >= _T1_LAG_ALERT_THRESHOLD 个开市日才告警（先例=scripts/governance/decision_chain_sentinel.py，
# 参照日=min(日历最近开市日<=今日, kline_index max(trade_date)) 取小）；行数下限降为次要参考列。
# 同族候选实测核对（"只动实测同病表"红线，逐表留档）：
#   c1_market.block_trade / block_trade_detail / dragon_tiger / dragon_tiger_seat——
#   failure 件仅 5/10 件且与真实抓取故障日（同日 *_incremental 失败件 09-02/09-16 等）完全聚簇，
#   常态当日行数达标 → 非永久病，判警行为零改动。
_T1_LAG_JUDGED_TABLES = frozenset({"c1_market.margin_trading"})
_T1_LAG_ALERT_THRESHOLD = 2  # 滞后 >=2 开市日才告警（同 decision_chain_sentinel 默认 N=2）
_CALENDAR_EXCHANGE = "SSE"  # 同 quality_sentinel/decision_chain_sentinel: 库内仅此一档
_CH_DATE_ZERO = "1970-01-01"  # CH 空集聚合 Date 零值（视为全史零行）

_SQL_T1_MAX_DATE = "SELECT max({date_col}) FROM {table}"
_SQL_CALENDAR_LAST_OPEN = (
    "SELECT max(cal_date) FROM {calendar} FINAL "
    "WHERE exchange = '{exchange}' AND is_open = 1 AND cal_date <= toDate('{ref_date}')"
)
_SQL_KLINE_MAX_DATE = "SELECT max(trade_date) FROM {table}"
_SQL_OPEN_DAYS_AFTER = (
    "SELECT count() FROM {calendar} FINAL "
    "WHERE exchange = '{exchange}' AND is_open = 1 "
    "AND cal_date > toDate('{start}') AND cal_date <= toDate('{end}')"
)

_T1_REF_TABLES: tuple[str, str] | None = None  # (trade_calendar, kline_index) 惰性缓存


def _t1_ref_tables() -> tuple[str, str]:
    """参照双腿表名（TableRegistry 品类真源，禁硬编码；惰性解析防 import 期新增失败面）。"""
    global _T1_REF_TABLES
    if _T1_REF_TABLES is None:
        from zephyr.data.table_registry import get_registry

        reg = get_registry()
        _T1_REF_TABLES = (reg.table("market_trade_calendar"), reg.table("market_index_kline"))
    return _T1_REF_TABLES


def _query_single_date(sql: str) -> datetime.date | None:
    """ch_reader 单值日期查询。空串(查询失败)/"\\N"/CH 空集零值日期 → None。"""
    out = (ch_reader.query(sql) or "").strip()
    if not out or out.startswith("\\N") or out.split("\t")[0].split("\n")[0][:10] == _CH_DATE_ZERO:
        return None
    try:
        return datetime.date.fromisoformat(out.split("\t")[0].split("\n")[0][:10])
    except ValueError:
        return None


def _resolve_reference_day(today: datetime.date) -> datetime.date | None:
    """参照日=min(日历最近开市日<=今日, kline_index max)（同 decision_chain_sentinel 取小口径：
    日历超前于数据面时不虚计滞后）。单腿失败降级另一腿，双腿全废返回 None（由调用方降级）。"""
    calendar_day: datetime.date | None = None
    kline_day: datetime.date | None = None
    try:
        calendar_tbl, kline_tbl = _t1_ref_tables()
    except Exception as e:  # noqa: BLE001 — 注册表不可用按双腿全废降级
        log.warning("T+1 参照表名解析失败（按参照日不可用降级）: %s", e)
        return None
    try:
        calendar_day = _query_single_date(
            _SQL_CALENDAR_LAST_OPEN.format(
                calendar=calendar_tbl, exchange=_CALENDAR_EXCHANGE, ref_date=today.isoformat()
            )
        )
    except Exception as e:  # noqa: BLE001 — 单腿降级（同先例）
        log.warning("T+1 参照日日历腿降级: %s", e)
    try:
        kline_day = _query_single_date(_SQL_KLINE_MAX_DATE.format(table=kline_tbl))
    except Exception as e:  # noqa: BLE001
        log.warning("T+1 参照日 kline 腿降级: %s", e)
    candidates = [d for d in (calendar_day, kline_day) if d is not None]
    return min(candidates) if candidates else None


def _compute_open_day_lag(last: datetime.date, ref: datetime.date) -> tuple[int, str]:
    """(last, ref] 内开市日数；日历查询失败降级为日历日差（保守偏大，同先例标注口径）。"""
    try:
        calendar_tbl, _ = _t1_ref_tables()
        out = ch_reader.query(
            _SQL_OPEN_DAYS_AFTER.format(
                calendar=calendar_tbl, exchange=_CALENDAR_EXCHANGE,
                start=last.isoformat(), end=ref.isoformat(),
            )
        )
        return int(out.strip()), "trading_days"
    except Exception as e:  # noqa: BLE001 — lag 腿降级（同先例）
        log.warning("T+1 滞后交易日口径降级为日历日差: %s", e)
        return (ref - last).days, "calendar_days"


def _judge_t1_lag(table: str, date_col: str, threshold: int, count: int, today: datetime.date) -> dict:
    """T+1 披露族判警：滞后开市日口径。行数下限保留为次要参考列（不参与判定）。"""
    result: dict = {
        "table": table,
        "date_col": date_col,
        "count": count,
        "threshold": threshold,
        "skipped": False,
    }
    last = _query_single_date(_SQL_T1_MAX_DATE.format(table=table, date_col=date_col))
    ref_day = _resolve_reference_day(today)

    if ref_day is None:
        # 参照日双腿全废：fail-soft 降级回行数口径（不硬抛断全表巡检；
        # calendar/kline_index 自身故障由其余表项巡检另行告警）
        healthy = count >= threshold
        result.update({
            "healthy": healthy,
            "last_date": last.isoformat() if last else None,
            "reference_day": None,
            "lag_trading_days": None,
            "lag_basis": "degraded_rowcount",
        })
        if not healthy:
            result["alert_message"] = (
                f"表 {table} T+1披露判警降级(参照日不可用): 当日行数 {count} < 阈值 {threshold}"
                f"（行数口径仅降级兜底，max({date_col})={last.isoformat() if last else '无'}）"
            )
        log.info("表 %s T+1判警降级行数口径: count=%d threshold=%d", table, count, threshold)
        return result

    result["reference_day"] = ref_day.isoformat()
    result["last_date"] = last.isoformat() if last else None
    if last is None:
        # 全史零行=断供（比滞后超限更重的形态，同 decision_chain_sentinel 口径）
        result.update({"healthy": False, "lag_trading_days": None, "lag_basis": None})
        result["alert_message"] = (
            f"表 {table} T+1披露断供: max({date_col}) 全史零行（{table} 无任何行）"
        )
        log.warning("表 %s T+1披露断供（全史零行）", table)
        return result

    lag, lag_basis = (0, "trading_days") if ref_day <= last else _compute_open_day_lag(last, ref_day)
    healthy = lag < _T1_LAG_ALERT_THRESHOLD
    result.update({"healthy": healthy, "lag_trading_days": lag, "lag_basis": lag_basis})
    if healthy:
        log.debug(
            "表 %s T+1披露达标: max(%s)=%s 参照日=%s 滞后=%d", table, date_col, last.isoformat(),
            ref_day.isoformat(), lag,
        )
    else:
        result["alert_message"] = (
            f"表 {table} T+1披露滞后: max({date_col})={last.isoformat()} 距参照日 {ref_day.isoformat()}"
            f" 缺勤 {lag} 个{'交易日' if lag_basis == 'trading_days' else '日历日(降级口径)'}"
            f" >= 阈值 {_T1_LAG_ALERT_THRESHOLD}（当日行数 {count} < {threshold}，行数仅参考）"
        )
        log.warning("%s", result["alert_message"])
    return result

#: P1-1 接线（2026-09-14 外部审查整改）：tick 真重复检查脚本正门路径。
#: 单一真源=脚本本体（RULE-DATA-OPS/TRAE-063 DATA-OPS-INV-002 配套），
#: 本模块经 subprocess 调用其 CLI，不在 src 侧复刻 14 字段真重复口径。
_TICK_DUP_SCRIPT = (
    REPO_ROOT / "scripts" / "governance" / "data_quality" / "check_tick_duplication.py"
)
_TICK_DUP_TIMEOUT_S = 300

# 周末/月初才跑的 schedule——工作日对账时不应期待它们当天运行
_NON_DAILY_SCHEDULES = frozenset(
    {
        "weekend_calibration",
        "monthly_static",
        "weekend_backfill",
    }
)

# SQL 模板（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_RUNS_SINCE = "SELECT task_id, status, started_at FROM task_runs WHERE started_at >= ? ORDER BY started_at DESC"


def _should_run_today(tasks: list[dict]) -> dict[str, str]:
    """筛出今日应跑任务（未禁用 + 每日类 schedule）。返回 {task_id: schedule}。"""
    should_run: dict[str, str] = {}
    for t in tasks:
        tid = t.get("task_id", "")
        if not tid:
            continue
        sched = t.get("schedule", "")
        disabled = bool(t.get("disabled")) or bool(t.get("extra", {}).get("disabled"))
        # rpt_tf15：schedule: disabled 是停用任务的表达方式（tasks.yaml 4 条），
        # 不识别则每个交易日进"应跑"名单 → 23:00 对账永久假红（告警疲劳）
        if disabled or sched in _NON_DAILY_SCHEDULES or sched == "disabled":
            continue
        should_run[tid] = sched
    return should_run


def _today_latest_status(store, today: datetime.date) -> dict[str, str]:
    """查今日 task_runs 每个任务最新一次状态。返回 {task_id: status}。失败返回 {}。"""
    # UTC 窗口：本地 today 00:00 = UTC today-1 16:00；task_runs.started_at 存 UTC ISO
    day_start_utc = (
        datetime.datetime.combine(today, datetime.time.min, tzinfo=datetime.timezone.utc) - datetime.timedelta(hours=8)
    ).isoformat()
    try:
        with store._lock:
            cur = store._conn.execute(_SQL_RUNS_SINCE, (day_start_utc,))
            runs = [dict(r) for r in cur.fetchall()]
            cur.close()
    except Exception as e:  # noqa: BLE001 — 对账失败不应中断主巡检
        log.error("任务级对账查询 task_runs 失败: %s", e)
        return {}

    latest: dict[str, str] = {}
    for r in runs:
        tid = r["task_id"]
        if tid not in latest:
            latest[tid] = r.get("status") or "UNKNOWN"
    return latest


def _reconcile_task_runs(scheduler, today: datetime.date) -> dict:
    """任务级对账：核对"今日应跑任务"在 task_runs 里是否有 SUCCESS 记录。

    病根（#ARCH-DATA-RECONCILE-001，2026-08-13）：原巡检只查每张表"今天有多少行"，
    用历史基线阈值判定。当某任务今天根本没跑（如调度器没拉起某批次），只要该表
    昨天有数据把历史基线拉高/或阈值被拉低，就会误报"达标"——37 个任务漏跑零告警。

    治本：除表级行数检查外，再做一层"声明 vs 实际"对账——
      应跑 = tasks.yaml 中未禁用、且 schedule 属于"每日类"（排除周末/月初时段）的任务
      实际 = task_runs 中今日（UTC 窗口）有 status='SUCCESS' 记录的任务
      缺口 = 应跑 - 实际 → 告警

    Args:
        scheduler: IntegratorScheduler 实例（取 _tasks / _progress_store）
        today: 检查日期（本地日）

    Returns:
        {"should_run": int, "succeeded": int, "missing": [...], "failed": [...]}
    """
    empty = {"should_run": 0, "succeeded": 0, "missing": [], "failed": []}
    if scheduler is None:
        return empty

    store = getattr(scheduler, "_progress_store", None)
    if store is None:
        return empty

    should_run = _should_run_today(getattr(scheduler, "_tasks", None) or [])
    latest = _today_latest_status(store, today)

    succeeded = {tid for tid in should_run if latest.get(tid) == "SUCCESS"}
    missing = sorted(tid for tid in should_run if tid not in latest)
    failed = sorted(tid for tid in should_run if tid in latest and latest[tid] != "SUCCESS")

    return {
        "should_run": len(should_run),
        "succeeded": len(succeeded),
        "missing": missing,
        "failed": failed,
    }


def _check_table_today(info: dict, today: datetime.date) -> dict | None:
    """检查单张表当天数据行数是否达标。

    Args:
        info: _discover_backfill_tables 返回的表信息（含 table/date_column/threshold）
        today: 检查日期

    Returns:
        检查结果 dict（含 table/date_col/count/threshold/healthy/skipped）。
        元数据表（无日期列或阈值为0）标记 skipped=True 并显式上报，不再静默跳过（Phase 3-B 治本修复）。
    """
    table = info.get("table", "")
    date_col = info.get("date_column", "")
    threshold = info.get("threshold", 0)

    # Phase 3-B 治本修复：元数据表（如 stock_list/etf_list 等无日频数据的表）显式标记为 skipped，
    # 不再静默跳过——静默跳过导致巡检覆盖率不透明，AI无法判断"未检查"vs"检查了但健康"。
    if not date_col or threshold <= 0:
        log.info("表 %s 跳过巡检（元数据表：无日期列或阈值为0，属正常白名单）", table)
        return {
            "table": table,
            "date_col": date_col,
            "count": 0,
            "threshold": threshold,
            "healthy": True,
            "skipped": True,
        }

    d_str = today.isoformat()
    cnt = ch_reader.query(_SQL_COUNT_TODAY.format(table=table, date_col=date_col, d_str=d_str))
    try:
        count = int(cnt.strip()) if cnt and cnt.strip() else 0
    except ValueError:
        count = 0

    # T+1 披露族改走滞后开市日口径（DU-03 案；其余表行为零改动）
    if table in _T1_LAG_JUDGED_TABLES:
        return _judge_t1_lag(table, date_col, threshold, count, today)

    healthy = count >= threshold
    if not healthy:
        log.warning("表 %s 当日数据不达标: %d < %d (阈值)", table, count, threshold)
    else:
        log.debug("表 %s 当日数据达标: %d >= %d", table, count, threshold)

    return {
        "table": table,
        "date_col": date_col,
        "count": count,
        "threshold": threshold,
        "healthy": healthy,
        "skipped": False,
    }


def run_tick_duplication_check(month: str | None = None, timeout_s: int = _TICK_DUP_TIMEOUT_S) -> dict:
    """月度 tick 真重复检查（P1-1 接线：RULE-DATA-OPS 工具入主巡检链路）。

    经 subprocess 调用正门脚本 check_tick_duplication.py（14 字段全同=真重复
    的唯一口径真源），只读检测、禁止删除。脚本退出码语义：
      0=无真重复（healthy）/ 1=发现真重复（duplicates，需排查数据源，
      禁止直接删）/ 2=检查失败（CH 不可达等，degraded 不阻断巡检）。

    Args:
        month: 检查月份（YYYYMM，默认当月）
        timeout_s: subprocess 超时秒数

    Returns:
        {"status": "healthy"|"duplicates"|"degraded", "exit_code": int,
         "month": str, "detail": str(截断)}
    """
    month = month or datetime.date.today().strftime("%Y%m")
    result: dict = {"status": "degraded", "exit_code": -1, "month": month, "detail": ""}
    if not _TICK_DUP_SCRIPT.exists():
        result["detail"] = f"脚本不存在: {_TICK_DUP_SCRIPT}"
        log.warning("tick 判重脚本缺失，巡检降级: %s", result["detail"])
        return result
    try:
        proc = subprocess.run(
            [sys.executable, str(_TICK_DUP_SCRIPT), "--month", month, "--json"],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=str(REPO_ROOT),
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        result["detail"] = f"subprocess 失败: {e}"
        log.warning("tick 判重检查执行失败（巡检降级不阻断）: %s", e)
        return result
    result["exit_code"] = proc.returncode
    detail = (proc.stdout or "").strip()
    if proc.returncode == 0:
        result["status"] = "healthy"
        result["detail"] = detail[-500:] if detail else "无真重复"
    elif proc.returncode == 1:
        result["status"] = "duplicates"
        result["detail"] = detail[-2000:] if detail else "发现真重复（详见脚本输出）"
        log.error("tick_data %s 发现真重复（禁止直接删除，须排查数据源）:\n%s", month, result["detail"])
    else:
        result["detail"] = ((proc.stderr or "") + detail)[-500:]
        log.warning("tick 判重检查失败 exit=%s（巡检降级不阻断）: %s", proc.returncode, result["detail"])
    return result


def run_daily_check(scheduler=None) -> dict:
    """每天盘后数据完整性巡检主入口。

    动态发现 tasks.yaml 中所有表，逐表检查当天数据行数是否达标。
    不达标的表通过 alerter 告警，结果记录到 progress_store。

    Args:
        scheduler: IntegratorScheduler 实例（可选，用于告警和记录进度）

    Returns:
        {"total": int, "healthy_count": int, "unhealthy_tables": list, "success": bool}
    """
    today = datetime.date.today()
    log.info("开始每日数据完整性巡检: date=%s", today.isoformat())

    # 动态发现所有表（使用公共别名，使测试 mock 可生效）
    tables_info = discover_backfill_tables()
    log.info("动态发现 %d 张表需要巡检", len(tables_info))

    results: list[dict] = []
    for info in tables_info:
        result = _check_table_today(info, today)
        if result is not None:
            results.append(result)

    total = len(results)
    unhealthy = [r for r in results if not r["healthy"]]
    healthy_count = total - len(unhealthy)

    # 任务级对账（#ARCH-DATA-RECONCILE-001）：核对"今日应跑 vs 实际 SUCCESS"
    # 补表级行数检查的盲区——任务没跑时表级可能因历史基线误报达标。
    recon = _reconcile_task_runs(scheduler, today)
    task_gaps = recon["missing"] + recon["failed"]

    # P1-1 tick 真重复检查（RULE-DATA-OPS 接线）：degraded 不阻断巡检，
    # 发现真重复走 ERROR 告警（只检测，禁止删除——判读权在人）。
    tick_dup = run_tick_duplication_check()

    # 告警
    if scheduler is not None:
        try:
            alerter = scheduler._alerter
            for r in unhealthy:
                # T+1 披露族自带滞后口径告警文案（alert_message）；其余表原文案零改动
                alerter.notify(
                    f"integrity_check_{r['table']}",
                    r.get("alert_message")
                    or f"表 {r['table']} 当日数据不达标: {r['count']} < {r['threshold']}",
                    level="ERROR",
                    source="integrity_check",
                )
            # 任务级缺口告警（漏跑/失败任务，聚合为一条避免刷屏）
            if task_gaps:
                alerter.notify(
                    "integrity_check_task_reconcile",
                    "任务级对账缺口: 应跑 %d, 成功 %d, 漏跑 %d, 失败 %d。漏跑=%s 失败=%s"
                    % (
                        recon["should_run"],
                        recon["succeeded"],
                        len(recon["missing"]),
                        len(recon["failed"]),
                        recon["missing"],
                        recon["failed"],
                    ),
                    level="ERROR",
                    source="integrity_check",
                )
            # P1-1 tick 真重复告警
            if tick_dup["status"] == "duplicates":
                alerter.notify(
                    "integrity_check_tick_duplication",
                    f"tick_data {tick_dup['month']} 发现真重复（只检测禁止删除，"
                    f"check_tick_duplication.py 详见输出）",
                    level="ERROR",
                    source="integrity_check",
                )
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.error("告警发送失败: %s", e)

    # 记录到 progress_store
    if scheduler is not None:
        try:
            scheduler._progress_store.save_progress(
                "integrity_check_daily",
                "integrity_check",
                today.isoformat(),
                "SUCCESS" if (not unhealthy and not task_gaps) else "PARTIAL",
                total,
            )
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            pass

    skipped_count = sum(1 for r in results if r.get("skipped"))
    summary = {
        "total": total,
        "healthy_count": healthy_count,
        "skipped_count": skipped_count,
        "unhealthy_tables": [
            # T+1 族附带滞后诊断列（last_date/reference_day/lag_*），其余表字段零改动
            {k: r[k] for k in ("table", "count", "threshold", "last_date", "reference_day",
                               "lag_trading_days", "lag_basis") if k in r}
            for r in unhealthy
        ],
        # 任务级对账结果（新增维度）
        "task_should_run": recon["should_run"],
        "task_succeeded": recon["succeeded"],
        "task_missing": recon["missing"],
        "task_failed": recon["failed"],
        # P1-1 tick 真重复检查结果（healthy/duplicates/degraded）
        "tick_duplication": tick_dup,
        "success": len(unhealthy) == 0 and not task_gaps,
    }

    log.info(
        "巡检完成: %d 张表, %d 达标, %d 跳过(元数据), %d 不达标 | 任务级: 应跑 %d, 成功 %d, 漏跑 %d, 失败 %d",
        total,
        healthy_count,
        skipped_count,
        len(unhealthy),
        recon["should_run"],
        recon["succeeded"],
        len(recon["missing"]),
        len(recon["failed"]),
    )
    if unhealthy:
        log.warning("不达标表: %s", [r["table"] for r in unhealthy])
    if recon["missing"]:
        log.warning("漏跑任务: %s", recon["missing"])
    if recon["failed"]:
        log.warning("失败任务: %s", recon["failed"])

    return summary
