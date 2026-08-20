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
"""数据完整性巡检器——每天盘后检测全表当日数据是否达标。

设计理念（数据韧性三层机制 §3）：
  - 复用 backfill_checker._discover_backfill_tables() 动态发现全表
  - 新增表只要在 tasks.yaml 注册任务，自动纳入巡检覆盖范围
  - 只检测不补下载（补下载由 weekend_backfill / 手动触发负责）
  - 阈值来自历史7天日均行数×0.5（与 backfill_checker 一致）

调用方式：
  scheduler.run_schedule("integrity_check") → run_daily_check(scheduler)
  也可独立调用：python -c "from zephyr.data.integrity_checker import run_daily_check; run_daily_check()"
"""

from __future__ import annotations

import datetime
import logging

from zephyr.data import ch_reader
from zephyr.data.backfill_checker import _discover_backfill_tables

discover_backfill_tables = _discover_backfill_tables  # public alias（Stage 4 公共化）


log = logging.getLogger(__name__)

# SQL 模板（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_COUNT_TODAY = "SELECT count() FROM {table} WHERE {date_col}=toDate('{d_str}')"

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
        if disabled or sched in _NON_DAILY_SCHEDULES:
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

    # 告警
    if scheduler is not None:
        try:
            alerter = scheduler._alerter
            for r in unhealthy:
                alerter.notify(
                    f"integrity_check_{r['table']}",
                    f"表 {r['table']} 当日数据不达标: {r['count']} < {r['threshold']}",
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
            {"table": r["table"], "count": r["count"], "threshold": r["threshold"]} for r in unhealthy
        ],
        # 任务级对账结果（新增维度）
        "task_should_run": recon["should_run"],
        "task_succeeded": recon["succeeded"],
        "task_missing": recon["missing"],
        "task_failed": recon["failed"],
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
