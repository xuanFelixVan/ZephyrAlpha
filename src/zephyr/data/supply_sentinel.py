# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.supply_sentinel
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.alerter; zephyr.shared.io.paths
# [CONSUMERS] zephyr.data.scheduler (_run_special_schedule: data_supply_sentinel 槽位); CLI 独立运行
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 阈值配置唯一真源=src/zephyr/data/config/data_supply_sentinel.yaml（fail-visible 缺失即报错）;
#   只检测不修复（补跑由 catchup_guard/backfill 负责）; 查询失败按违规上报（宁报不漏）;
#   告警经 Alerter（失败落 failures/ 留痕）; calendar 表只对 past 窗口判停更（未来行不稀释新鲜度）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 配置缺失/畸形->SupplySentinelError 上抛（fail-visible）; 单表查询异常->计为违规+继续; 全程不抛
# [TESTS] tests/zephyr/data/test_supply_sentinel.py（暂缺；夜班施工件，随 D8 收口补）
# [A_module] module_id=MOD-L00-004-SS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""数据断供哨兵——表级 max(date) 停更检测（SOP §10.2 运维常态）。

诞生背景（altdata_line 09 清单 D1/D2 波1，2026-09-18 夜班 st-datapack-20260918）：
    股东户数表 2026-07 断供两月才被发现（shareholder_incremental 任务在、miniqmt 清退后
    管线死——「任务存在≠管线活着」SOP 反例）。L11 integrity_check 的日频口径对
    业务事件日期列表（解禁日/公告日/决议日）天然误报而被强制跳过（#ARCH-DATA-017
    _BUSINESS_EVENT_DATE_COLS），事件日历族由此成为停更检测盲区。本件补上该层：
    按表配置 max_lag_days，对 max(date_col) 落后天数判停更。

与相邻检测面的分工（查重声明）：
    - integrity_checker（L11）= 当日行数达标检测（高频日频表），事件日历表被跳过；
    - backfill_checker（L10/L10.5）= 缺口发现+补下载；
    - catchup_guard（L10.7）= 任务档期对账补跑（调度侧视角）；
    - 本件（data_supply_sentinel）= 表侧 max(date) 停更检测，覆盖慢频/事件日历族。

用法：
    scheduler.run_schedule("data_supply_sentinel")   # 调度槽位（schedule.yaml 06:50 日批，
                                                     # APScheduler 常驻调度=自动触发正门）
    python -c "from zephyr.data.supply_sentinel import run_supply_sentinel; run_supply_sentinel()"
                                                     # 运维一次性巡检（无 argparse 入口：
                                                     # MANUAL-ONLY-PERMANENT 门禁禁 permanent 模块
                                                     # 带 manual 触发模式）
"""

from __future__ import annotations

import datetime
import logging
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.data import ch_reader
from zephyr.data.alerter import LEVEL_ERROR, LEVEL_WARN, Alerter
from zephyr.shared.io.paths import REPO_ROOT

log = logging.getLogger(__name__)

__all__: Final = ["SupplySentinelError", "run_supply_sentinel", "check_tables"]

#: 阈值配置唯一真源（规则数据=YAML，trae_062 SSoT）
_SENTINEL_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "data_supply_sentinel.yaml"

# SQL 模板（NO-BARE-SQL gate 豁免：_SQL_* 前缀常量约定）
_SQL_MAX_DATE = "SELECT max({date_col}) FROM {table}{where_clause}"
_SQL_ROW_COUNT = "SELECT count() FROM {table}"


class SupplySentinelError(Exception):
    """哨兵配置非法（缺失/畸形）——fail-visible，禁码内第二真源兜底。"""


def _load_config(config_path: Path | None = None) -> list[dict[str, Any]]:
    """加载哨兵表清单（fail-visible：文件缺失/畸形/空清单即抛）。

    MSG-EXPOSURE 合规（5.99.20）：敏感定位信息（路径/条目序号）走 exc.details
    结构化字段，消息文本只留人类可读摘要（同 onboard_source.py 先例）。
    """
    path = config_path or _SENTINEL_CONFIG_PATH
    if not path.exists():
        e = SupplySentinelError("断供哨兵配置缺失")
        e.details = {"path": str(path)}  # type: ignore[attr-defined]
        raise e
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as ex:
        e = SupplySentinelError("断供哨兵配置 YAML 畸形")
        e.details = {"path": str(path), "yaml_error": str(ex)[:200]}  # type: ignore[attr-defined]
        raise e from ex
    tables = data.get("tables")
    if not isinstance(tables, list) or not tables:
        e = SupplySentinelError("断供哨兵配置 tables 清单为空")
        e.details = {"path": str(path)}  # type: ignore[attr-defined]
        raise e
    for i, entry in enumerate(tables):
        for field in ("table", "date_col", "max_lag_days"):
            if field not in entry:
                e = SupplySentinelError("断供哨兵配置条目缺必备字段")
                e.details = {"path": str(path), "entry_index": i, "missing_field": field}  # type: ignore[attr-defined]
                raise e
    return tables


def check_tables(config_path: Path | None = None) -> dict[str, Any]:
    """逐表检测 max(date_col) 停更，返回汇总。

    Returns:
        {ok, checked, breached, results: [{table, max_date, lag_days, max_lag_days, breached, detail}]}
    """
    today = datetime.date.today()
    entries = _load_config(config_path)
    results: list[dict[str, Any]] = []
    for entry in entries:
        table = entry["table"]
        date_col = entry["date_col"]
        max_lag = int(entry["max_lag_days"])
        # past_only=True：只对 <= today 的行取 max（预约/前瞻类未来行不稀释新鲜度判定）
        where = f" WHERE {date_col} <= toDate('{today.isoformat()}')" if entry.get("past_only") else ""
        sql = _SQL_MAX_DATE.format(date_col=date_col, table=table, where_clause=where)
        try:
            raw = ch_reader.query(sql)
            max_date_raw = (raw or "").strip().split("\n")[0].strip() if raw else ""
            if not max_date_raw or max_date_raw in ("\\N", "NULL", ""):
                # 空表/全 NULL：若配置 allow_empty 则跳过，否则计为违规
                if entry.get("allow_empty"):
                    results.append({"table": table, "max_date": None, "lag_days": None,
                                    "max_lag_days": max_lag, "breached": False, "detail": "empty(allowed)"})
                    continue
                results.append({"table": table, "max_date": None, "lag_days": None,
                                "max_lag_days": max_lag, "breached": True, "detail": "empty table"})
                continue
            max_date = datetime.date.fromisoformat(max_date_raw.split(" ")[0])
            lag_days = (today - max_date).days
            breached = lag_days > max_lag
            results.append({"table": table, "max_date": max_date.isoformat(), "lag_days": lag_days,
                            "max_lag_days": max_lag, "breached": breached,
                            "detail": f"lag={lag_days}d > {max_lag}d" if breached else "ok"})
        except Exception as e:  # noqa: BLE001 — 单表查询异常按违规计（宁报不漏），不阻断其余表
            results.append({"table": table, "max_date": None, "lag_days": None,
                            "max_lag_days": max_lag, "breached": True,
                            "detail": f"query error: {str(e)[:120]}"})

    breached = [r for r in results if r["breached"]]
    return {"ok": not breached, "checked": len(results), "breached": len(breached), "results": results}


def run_supply_sentinel(alerter: Alerter | None = None) -> dict[str, Any]:
    """哨兵入口（调度槽位/CLI 共用）：检测 + 告警留痕。全程不抛（告警路径自吞异常）。"""
    alerter = alerter or Alerter()
    try:
        summary = check_tables()
    except SupplySentinelError as e:
        log.error("断供哨兵配置错误: %s", e)
        alerter.notify("data_supply_sentinel", f"哨兵配置错误（检测未执行）: {e}", level=LEVEL_ERROR,
                       source="supply_sentinel")
        return {"ok": False, "config_error": str(e)}
    for r in summary["results"]:
        if not r["breached"]:
            log.info("断供哨兵 ok: %s max=%s lag=%sd", r["table"], r["max_date"], r["lag_days"])
            continue
        level = LEVEL_ERROR
        try:
            alerter.notify(
                "data_supply_sentinel",
                f"断供嫌疑: {r['table']} max({r.get('max_date')}) 停更 [{r['detail']}]",
                level=level,
                source="supply_sentinel",
            )
        except Exception:  # noqa: BLE001 — 告警通道故障不阻断巡检
            log.exception("断供哨兵告警写入失败: %s", r["table"])
    log.info("断供哨兵巡检完成: checked=%d breached=%d ok=%s", summary["checked"], summary["breached"], summary["ok"])
    return summary


