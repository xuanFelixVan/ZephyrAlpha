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
# [A_module] module_id=MOD-L00-004-integrity_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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

log = logging.getLogger(__name__)

# SQL 模板（NO-BARE-SQL gate 豁免：_SQL_* 前缀）
_SQL_COUNT_TODAY = (
    "SELECT count() FROM {table} WHERE {date_col}=toDate('{d_str}')"
)


def _check_table_today(info: dict, today: datetime.date) -> dict | None:
    """检查单张表当天数据行数是否达标。

    Args:
        info: _discover_backfill_tables 返回的表信息（含 table/date_column/threshold）
        today: 检查日期

    Returns:
        检查结果 dict（含 table/date_col/count/threshold/healthy），跳过时返回 None。
    """
    table = info.get("table", "")
    date_col = info.get("date_column", "")
    threshold = info.get("threshold", 0)

    if not date_col or threshold <= 0:
        log.debug("表 %s 跳过巡检（无日期列或阈值为0）", table)
        return None

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

    # 动态发现所有表
    tables_info = _discover_backfill_tables()
    log.info("动态发现 %d 张表需要巡检", len(tables_info))

    results: list[dict] = []
    for info in tables_info:
        result = _check_table_today(info, today)
        if result is not None:
            results.append(result)

    total = len(results)
    unhealthy = [r for r in results if not r["healthy"]]
    healthy_count = total - len(unhealthy)

    # 告警
    if scheduler is not None and unhealthy:
        try:
            alerter = scheduler._alerter
            for r in unhealthy:
                alerter.notify(
                    f"integrity_check_{r['table']}",
                    f"表 {r['table']} 当日数据不达标: {r['count']} < {r['threshold']}",
                    level="ERROR",
                    source="integrity_check",
                )
        except Exception as e:
            log.error("告警发送失败: %s", e)

    # 记录到 progress_store
    if scheduler is not None:
        try:
            scheduler._progress_store.save_progress(
                "integrity_check_daily",
                "integrity_check",
                today.isoformat(),
                "SUCCESS" if not unhealthy else "PARTIAL",
                total,
            )
        except Exception:
            pass

    summary = {
        "total": total,
        "healthy_count": healthy_count,
        "unhealthy_tables": [
            {"table": r["table"], "count": r["count"], "threshold": r["threshold"]}
            for r in unhealthy
        ],
        "success": len(unhealthy) == 0,
    }

    log.info(
        "巡检完成: %d 张表, %d 达标, %d 不达标",
        total, healthy_count, len(unhealthy),
    )
    if unhealthy:
        log.warning("不达标表: %s", [r["table"] for r in unhealthy])

    return summary
