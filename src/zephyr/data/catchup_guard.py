# [BLUEPRINT] MOD-L00-021 | docs/03_modules/_domain_data/catchup_guard/blueprint.md
# [MODULE] zephyr.data.catchup_guard
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.backfill_checker(_load_tasks_yaml); zephyr.data.progress_store; zephyr.data.calendar; zephyr.data.alerter; zephyr.data.ch_reader
# [CONSUMERS] zephyr.data.scheduler(_run_special_schedule catchup_guard 分支); 前端缺口对账卡片(二期)
# [STARTUP] imported（由 data scheduler 03:30 cron 经 _run_special_schedule 调度；不进 TRADING_DAY_GUARDED_SCHEDULES）
# [MATURITY] testing
# [INVARIANTS] 只做"档期 vs 打卡"对账不做行数检测(L10/L10.5职责); 单实例锁防重入; 单批补跑≤15顺延收敛; trading_day_only任务非交易日顺延不判缺; RUNNING任务跳过防撞车; 补跑经 scheduler.run_task 幂等(ReplacingMergeTree)
# [MODIFY-GUARD] docs/03_modules/_domain_data/catchup_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单任务对账/补跑异常隔离不中断整体; CH 不可达时空表兜底跳过不误判; 锁获取失败直接退出
# [TESTS] tests/zephyr/data/test_catchup_guard.py
# [TTL] permanent
"""调度对账补跑器（Catch-up Guard）——任务档期 vs 打卡记录对账 + 自动补跑。

治本背景（2026-09-01 事故）：调度器宕机错过 monthly_static（月初 09:00 cron），
8 张静态表空缺 32 小时无人发现；backfill_checker 7 天行数扫描对"静态表跳过/
月度档期/空表形态/自身被宕机跳过"四类盲区结构性失明（blueprint §0 对照表）。

对账口径（档期 → overdue 判定，详见蓝图 §2）：
- monthly_static：本月无 SUCCESS 记录
- weekend_calibration/weekend_backfill：最近 7 天无 SUCCESS
- daily_*：last SUCCESS < 最近一个已收盘交易日
- intraday_*/pre_market/auction_highfreq：last SUCCESS < 最近已收盘交易日
- event_driven/news_slow（7×24）：last SUCCESS < 昨日
- 空表兜底：monthly_static/weekend_calibration 任务对应表 count()=0 无条件 overdue
- trading_day_only 且今日非交易日 → 顺延（deferred）；RUNNING → 跳过（防撞车）
"""

from __future__ import annotations

import datetime
import logging
import os

from zephyr.data.alerter import LEVEL_ERROR, LEVEL_INFO, LEVEL_WARN

log = logging.getLogger(__name__)

# 档期分桶（schedule 名 → 应跑频率；蓝图 §2 对账表）
_MONTHLY_SCHEDULES = frozenset({"monthly_static"})
_WEEKLY_SCHEDULES = frozenset({"weekend_calibration", "weekend_backfill"})
_DAILY_SCHEDULES = frozenset(
    {"daily_kline", "daily_capital", "daily_event", "nightly_financial", "daily_backfill"}
)
_INTRADAY_SCHEDULES = frozenset(
    {"pre_market", "intraday_realtime", "intraday_minute", "intraday_sector", "auction_highfreq"}
)
_ALWAYS_ON_SCHEDULES = frozenset({"event_driven", "news_slow"})  # 7×24 任务
_SKIP_SCHEDULES = frozenset({"integrity_check", "catchup_guard"})  # 系统/自身，不对账

# 档期优先级（补跑排序：越"高档"的错过越先补）
_CADENCE_PRIORITY = {  # schedule 名 → (bucket 序, bucket 名)
    **{s: (0, "monthly") for s in _MONTHLY_SCHEDULES},
    **{s: (1, "weekly") for s in _WEEKLY_SCHEDULES},
    **{s: (2, "daily") for s in _DAILY_SCHEDULES},
    **{s: (3, "intraday") for s in _INTRADAY_SCHEDULES},
    **{s: (3, "always_on") for s in _ALWAYS_ON_SCHEDULES},
}

# 空表兜底适用档期（打过卡但数据丢了形态，如 8/10 schema 重建清空 sector_list）
_EMPTY_TABLE_SCHEDULES = frozenset({"monthly_static", "weekend_calibration"})

MAX_RERUN_PER_RUN = 15  # 单批补跑上限，超出顺延次日（每日 03:30 必跑，天然收敛）
_LOCK_STALE_MINUTES = 30
_LOCK_PATH = os.path.join("tmp", "catchup_guard.lock")


def _read_lock_pid(path: str) -> int | None:
    """读锁文件 PID；不存在/非数字返回 None。"""
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read().strip()
        return int(content) if content.isdigit() else None
    except OSError:
        return None


def _pid_alive(pid: int) -> bool:
    """跨平台 PID 探活（psutil；Windows 禁用 os.kill(pid,0)——其语义是 TerminateProcess）。"""
    try:
        import psutil

        return psutil.pid_exists(pid)
    except Exception:  # noqa: BLE001 — psutil 不可用时退化为视为死亡（宁可重跑不空等）
        return False


def _acquire_lock(path: str = _LOCK_PATH) -> bool:
    """单实例锁（PID 活性检测 + 陈旧锁清理）。获取失败返回 False（已有实例在跑）。"""
    lock_dir = os.path.dirname(path)
    if lock_dir:
        os.makedirs(lock_dir, exist_ok=True)
    pid = _read_lock_pid(path)
    if pid is not None:
        if pid == os.getpid():
            return True
        alive = _pid_alive(pid)  # Windows 禁 os.kill(pid,0)——语义是 TerminateProcess
        if alive:
            try:
                age_min = (
                    datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(path))
                ).total_seconds() / 60
            except OSError:
                age_min = 0
            if age_min < _LOCK_STALE_MINUTES:
                log.warning("catchup_guard 已有实例在跑（PID=%d），本次退出", pid)
                return False
        log.warning("清理陈旧锁（PID=%d 死亡或超 %d 分钟）", pid, _LOCK_STALE_MINUTES)
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    return True


def _release_lock(path: str = _LOCK_PATH) -> None:
    """释放本实例持有的锁（PID 不匹配不动，防误删他人锁）。"""
    if _read_lock_pid(path) == os.getpid():
        try:
            os.remove(path)
        except OSError:
            pass


def _parse_last_success(st: dict | None) -> datetime.datetime | None:
    """从打卡记录解析最近一次 SUCCESS 时间（UTC ISO 字符串）；无 SUCCESS 返回 None。"""
    if not st or st.get("last_status") != "SUCCESS":
        return None
    raw = st.get("last_run_at")
    if not raw:
        return None
    try:
        return datetime.datetime.fromisoformat(str(raw))
    except ValueError:
        return None


def _cadence_of(schedule: str) -> tuple[int, str] | None:
    """schedule 名 → (优先级, 桶名)；不对账档期返回 None。"""
    return _CADENCE_PRIORITY.get(schedule)


def _is_overdue(
    bucket: str,
    last_success: datetime.datetime | None,
    *,
    today: datetime.date,
    last_completed_trading_day: datetime.date | None,
) -> bool:
    """按档期桶判定 overdue（last_success=None 一律 overdue）。"""
    if last_success is None:
        return True
    d = last_success.date()
    if bucket == "monthly":
        return d < today.replace(day=1)
    if bucket == "weekly":
        return d < today - datetime.timedelta(days=7)
    if bucket == "daily":
        return last_completed_trading_day is not None and d < last_completed_trading_day
    if bucket == "intraday":
        return last_completed_trading_day is not None and d < last_completed_trading_day
    if bucket == "always_on":  # 7×24 任务：昨日必须至少跑过一次
        return d < today - datetime.timedelta(days=1)
    return False


def run_catchup_guard(scheduler, *, lock_path: str = _LOCK_PATH) -> dict:
    """对账主入口：档期对账 → 空表兜底 → 补跑（带上限） → 告警留痕。

    Args:
        scheduler: IntegratorScheduler 实例（run_task/_alerter/_progress_store 注入）。
        lock_path: 单实例锁路径（测试注入用）。

    Returns:
        {"success", "overdue", "rerun", "deferred", "skipped_running", "cap_deferred", "empty_table"}
    """
    from zephyr.data.backfill_checker import _load_tasks_yaml
    from zephyr.data.calendar import get_market_calendar

    result: dict = {
        "success": False,
        "overdue": [],
        "rerun": {},
        "deferred": [],
        "skipped_running": [],
        "cap_deferred": [],
        "empty_table": [],
    }
    if not _acquire_lock(lock_path):
        return result
    try:
        cal = get_market_calendar("ashare")
        today = datetime.date.today()
        window_start = today - datetime.timedelta(days=10)
        trade_days = cal.trading_days_in_range(window_start, today)
        last_completed = max((d for d in trade_days if d < today), default=None)

        tasks = [t for t in _load_tasks_yaml() if not (t.get("extra") or {}).get("disabled")]
        is_trading_today = cal.is_trading_day(today)

        due: list[tuple[int, str, str, str]] = []  # (优先级, bucket, task_id, 原因)
        for t in tasks:
            schedule = t.get("schedule", "")
            task_id = t.get("task_id", "")
            bucket = _cadence_of(schedule)
            if task_id == "catchup_guard":
                continue
            extra = t.get("extra") or {}
            if bucket is None:
                if schedule not in _SKIP_SCHEDULES:
                    log.debug("任务 %s 档期 %s 不在对账范围，跳过", task_id, schedule)
                continue
            if extra.get("trading_day_only") and not is_trading_today:
                result["deferred"].append(task_id)
                continue
            st = scheduler._progress_store.get_task_status(task_id)
            if st and st.get("last_status") == "RUNNING":
                result["skipped_running"].append(task_id)
                continue
            last_success = _parse_last_success(st)
            reason = ""
            if _is_overdue(
                bucket[1], last_success, today=today, last_completed_trading_day=last_completed
            ):
                reason = f"{bucket[1]}_cadence_overdue(last_success={last_success})"
            elif schedule in _EMPTY_TABLE_SCHEDULES:
                table = t.get("table", "")
                if table and _table_is_empty(table):
                    reason = "empty_table_fallback"
                    result["empty_table"].append(table)
            if reason:
                due.append((bucket[0], bucket[1], task_id, reason))

        due.sort(key=lambda x: (x[0], x[2]))
        result["overdue"] = [f"{tid}({reason})" for _, _, tid, reason in due]

        for _, _, task_id, _reason in due[:MAX_RERUN_PER_RUN]:
            try:
                result["rerun"][task_id] = bool(scheduler.run_task(task_id))
            except Exception as e:  # noqa: BLE001 — 单任务异常隔离，不中断整体
                log.error("补跑任务 %s 异常: %s", task_id, e)
                result["rerun"][task_id] = False
        result["cap_deferred"] = [tid for _, _, tid, _ in due[MAX_RERUN_PER_RUN:]]

        failed = [tid for tid, ok in result["rerun"].items() if not ok]
        level = LEVEL_ERROR if failed else (LEVEL_WARN if result["overdue"] else LEVEL_INFO)
        summary = (
            f"对账完成: overdue={len(result['overdue'])} 补跑={len(result['rerun'])}"
            f" 失败={len(failed)} 顺延(交易日晚点)={len(result['deferred'])}"
            f" 上限截断={len(result['cap_deferred'])} 空表={result['empty_table']}"
        )
        if scheduler._alerter is not None:
            scheduler._alerter.notify("catchup_guard", summary, level=level, source="catchup")
        _save_summary(scheduler, result, failed)
        result["success"] = True
        log.info("catchup_guard %s", summary)
        return result
    finally:
        _release_lock(lock_path)


def _table_is_empty(table: str) -> bool:
    """空表兜底检测：count()=0 返回 True；CH 异常按"未知"处理返回 False（不误判）。"""
    from zephyr.data import ch_reader

    try:
        raw = ch_reader.query(f"SELECT count() FROM {table}")
        return int(raw.strip() or 0) == 0
    except Exception as e:  # noqa: BLE001 — CH 不可达时跳过兜底，不误判 overdue
        log.warning("空表兜底查询失败（跳过）: %s: %s", table, e)
        return False


def _save_summary(scheduler, result: dict, failed: list[str]) -> None:
    """对账结果写 progress_store（task_id=catchup_guard），供 CLI status/看板消费。"""
    try:
        scheduler._progress_store.save_progress(
            "catchup_guard",
            "internal",
            datetime.date.today().isoformat(),
            "SUCCESS" if not failed else "PARTIAL",
            len(result["rerun"]),
            ";".join(failed) if failed else None,
        )
    except Exception as e:  # noqa: BLE001 — 留痕失败不影响补跑成果
        log.warning("对账结果写 progress_store 失败: %s", e)
