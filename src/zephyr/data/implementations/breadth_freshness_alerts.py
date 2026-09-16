# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.breadth_freshness_alerts
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed（唯一出口，本模块不另起炉灶）;
#   zephyr.data.ch_reader; zephyr.data.table_registry;
#   zephyr.data.implementations.index_breadth_compute（宇宙注册表复用，禁双真源）
# [CONSUMERS] zephyr.data.implementations.internal_compute_provider (capability=breadth_freshness_sentinel 路由);
#   frontend promotion 页（经 /api/ops-notifications 既有链路，零改动复用）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 断供必须可见：kline_index 宽度零值/缺行 → OpsAlertFeed 落板（promotion 页横幅），
#   禁静默零值；唯一出口纪律（飞书/SMTP 已裁撤，禁新建外部通道、不改 ops_alert_feed 本体）；
#   本哨兵不依赖广度进料任务（dependencies 空）——进料任务自身死亡时仍必须能告警；
#   告警线自身不得成为故障源（发布失败降级记日志不抛）；
#   扫描面与进料件共用 INDEX_UNIVERSE 注册表（单真源）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 扫描失败→发布 breadth_scan_failed critical 并返回摘要不抛；
#   缺口消失→按 key resolve（灰显解除，滞回语义照抄 ops_alert_feed）
# [TESTS] tests/data/implementations/test_breadth_freshness_alerts.py
# [A_module] module_id=MOD-DATA-BREADTHALERT | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""市场广度新鲜度哨兵——kline_index 涨跌家数断供 → promotion 页告警（车道 G 施工项3）。

背景（实证）：399106 等 10 只指数的 advance_count/decline_count 于 2026-07-03 起
静默归零，持续 53 个交易日无人知晓——下游 F4 恒 0 才在挖矿中被发现。根因不只是
进料口缺失，更是**断供不可见**：
  - 数据侧 Alerter 只写 failure 文件（任务本身是 SUCCESS 的，因为外部源确实在发
    OHLC，只是不带宽度列）；
  - scheduler 的 #ARCH-SILENT-SUCCESS 0 行 WARN 只在增量任务上生效；
  - 零值是 DEFAULT，不是 NULL，任何"缺列"检查都不会响。
故本哨兵按**语义**判据（宽度双零/整行缺失）扫真表，不依赖任何任务的成败。

告警出口裁定（Owner 2026-09-16：通知=前端 promotion 页，飞书/SMTP 通道已删除）：
只经 OpsAlertFeed.publish 落 `.runtime/ops_notifications/notifications.jsonl` →
`GET /api/ops-notifications` → promotion 页横幅/晨审。桥接方式与
MOD-RESCHED-ALERT（resource_schedule_alerts）一致：key 稳定去重 + 本轮未触发的
既有 key resolve + 板目录可注入（测试禁写生产 .runtime）。

判据（逐标的、按交易日历对齐）：
  ok      当日行存在且 (advance_count>0 OR decline_count>0)
  zero    当日行存在但宽度双零（进料未落地/覆盖度防御未写）
  missing 当日无行（指数 K 线本身断供）
尾部连续 bad（zero|missing）日数 ≥ _ALERT_TRAILING_DAYS 触发；≥ _CRITICAL_TRAILING_DAYS
升 critical（critical 在 promotion 页红标，且阻断依赖它的发布门）。阈值取 2 而非 1：
容忍盘后单日的任务晚到，避免每日 23:00 巡检的边界抖动刷板。

消息必须带"缺位天数"而非只报"已修复"——消费端 EQW_ALLA 补位（dd04d9d2）在补洞的
同时会遮蔽真源缺失，本告警是唯一的"补位不得永久遮蔽真源缺失"外显证据。

# [ALGO_FLOW] external: docs/03_modules/_domain_data/algo_flow/breadth_freshness_alerts.yaml
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Callable
from typing import Any, Final

from zephyr.data.implementations.index_breadth_compute import INDEX_UNIVERSE
from zephyr.data.table_registry import get_registry

logger = logging.getLogger(__name__)

__all__: Final = ["BreadthFreshnessAlerts", "run_check"]

_TBL_KLINE_INDEX: Final = get_registry().table("market_index_kline")
_TBL_TRADE_CALENDAR: Final = get_registry().table("market_trade_calendar")

# 扫描窗（日历天）——只需覆盖"近期是否还在断供"，历史修复由进料件负责
_SCAN_LOOKBACK_DAYS: Final = 60
# 尾部连续缺位 ≥2 交易日触发（容忍单日任务晚到）
_ALERT_TRAILING_DAYS: Final = 2
# 尾部连续缺位 ≥5 交易日升 critical
_CRITICAL_TRAILING_DAYS: Final = 5
# 同 key 静默窗口（照抄 resource_schedule_alerts 语义：30min 内只刷新不重复）
DEFAULT_SILENCE_WINDOW_S: Final = 1800.0

_MODULE_ID: Final = "breadth-freshness-sentinel"

# SQL 模板常量（NO-BARE-SQL gate：_SQL_* 前缀定义行）
_SQL_BREADTH_STATE: Final = (
    "SELECT symbol, trade_date, "
    "countIf(advance_count > 0 OR decline_count > 0) AS ok, count() AS n "
    f"FROM {_TBL_KLINE_INDEX} FINAL "
    "WHERE trade_date >= toDate('{start}') AND trade_date <= toDate('{end}') "
    "AND symbol IN ({symbols}) "
    "GROUP BY symbol, trade_date ORDER BY symbol, trade_date FORMAT TSV"
)

_SQL_TRADING_DAYS: Final = (
    "SELECT cal_date "
    f"FROM {_TBL_TRADE_CALENDAR} "
    "WHERE is_open = 1 AND cal_date >= toDate('{start}') AND cal_date <= toDate('{end}') "
    "ORDER BY cal_date FORMAT TSV"
)


def _default_reader(sql: str) -> str:
    from zephyr.data import ch_reader

    return ch_reader.query(sql)


class BreadthFreshnessAlerts:
    """宽度断供检测 → OpsAlertFeed 唯一通道桥（CH 读/板目录/时钟全注入，测试隔离）。"""

    def __init__(
        self,
        board_dir: str | None = None,
        reader: Callable[[str], str] | None = None,
        module_id: str = _MODULE_ID,
        silence_window_s: float = DEFAULT_SILENCE_WINDOW_S,
        alert_trailing_days: int = _ALERT_TRAILING_DAYS,
        critical_trailing_days: int = _CRITICAL_TRAILING_DAYS,
    ):
        self._board_dir = board_dir
        self._reader = reader or _default_reader
        self._module_id = module_id
        self._silence = float(silence_window_s)
        self._alert_days = int(alert_trailing_days)
        self._critical_days = int(critical_trailing_days)

    # ── 检测 ─────────────────────────────────────────────────────────────

    def scan(
        self, today: datetime.date | None = None, lookback_days: int = _SCAN_LOOKBACK_DAYS
    ) -> list[dict[str, Any]]:
        """扫描近窗宽度状态 → 触发项列表（每项含 symbol/name/trailing/gap_start/total_bad）。"""
        end = today or datetime.date.today()
        start = end - datetime.timedelta(days=int(lookback_days))
        trading_days = self._trading_days(start, end)
        if not trading_days:
            raise RuntimeError(f"{_TBL_TRADE_CALENDAR} 无 {start}~{end} 交易日——哨兵失去判据")
        state = self._breadth_state(list(INDEX_UNIVERSE), start, end)

        out: list[dict[str, Any]] = []
        for sym, uni in INDEX_UNIVERSE.items():
            per_day = state.get(sym, {})
            bad = [d for d in trading_days if per_day.get(d, "missing") != "ok"]
            if not bad:
                continue
            trailing = self._trailing_bad(trading_days, per_day)
            if trailing < self._alert_days:
                continue  # 尾部未达阈值=可能只是当日任务晚到，不刷板
            out.append(
                {
                    "symbol": sym,
                    "universe": uni,
                    "trailing_bad": trailing,
                    "total_bad": len(bad),
                    "gap_start": bad[0],
                    "gap_end": bad[-1],
                    "missing_rows": sum(1 for d in bad if per_day.get(d, "missing") == "missing"),
                }
            )
        return out

    @staticmethod
    def _trailing_bad(trading_days: list[str], per_day: dict[str, str]) -> int:
        """自窗尾向前数连续非 ok 天数（整行缺失与双零同判 bad）。"""
        n = 0
        for d in reversed(trading_days):
            if per_day.get(d, "missing") != "ok":
                n += 1
            else:
                break
        return n

    def _trading_days(self, start: datetime.date, end: datetime.date) -> list[str]:
        sql = _SQL_TRADING_DAYS.format(start=start.isoformat(), end=end.isoformat())
        return [ln.strip() for ln in (self._reader(sql) or "").splitlines() if ln.strip()]

    def _breadth_state(self, symbols: list[str], start: datetime.date, end: datetime.date) -> dict:
        """{(symbol): {trade_date: ok|zero}}（未出现的日期由调用方按 missing 判）。"""
        sql = _SQL_BREADTH_STATE.format(
            start=start.isoformat(), end=end.isoformat(), symbols=", ".join(f"'{s}'" for s in symbols)
        )
        state: dict[str, dict[str, str]] = {}
        for line in (self._reader(sql) or "").strip().splitlines():
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            sym, d, ok, _rows = parts[0], parts[1], parts[2], parts[3]
            try:
                state.setdefault(sym, {})[d] = "ok" if int(ok) > 0 else "zero"
            except ValueError:
                logger.warning("广度状态行解析失败: %s", line[:80])
        return state

    # ── 发布/解除 ────────────────────────────────────────────────────────

    def _feed(self):
        from zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed import OpsAlertFeed

        return OpsAlertFeed(board_dir=self._board_dir, module_id=self._module_id)

    def _safe_publish(self, feed, **kwargs) -> dict:
        """单条落板 fail-safe：异常记日志返回 failed 摘要（告警线自身不得成为故障源）。"""
        try:
            return feed.publish(**kwargs)
        except Exception as exc:  # noqa: BLE001 — INVARIANTS：发布失败降级不抛
            logger.warning("breadth sentinel publish failed key=%s: %s", kwargs.get("key"), exc)
            return {"op": "failed", "key": kwargs.get("key"), "reason": str(exc)[:120]}

    def publish(self, items: list[dict[str, Any]], scan_error: str | None = None) -> dict:
        """触发项落板 + 已消失 key resolve；扫描自身失败额外落 selfcheck critical。

        fail-safe：单条发布异常记日志继续（告警线自身不得成为故障源）。
        """
        feed = self._feed()
        ops: list[dict] = []
        active_keys: list[str] = []
        for it in items:
            key = f"breadth_gap:{it['symbol']}"
            active_keys.append(key)
            trailing = int(it.get("trailing_bad", 0))
            severity = "critical" if trailing >= self._critical_days else "warning"
            ops.append(
                self._safe_publish(
                    feed,
                    key=key,
                    severity=severity,
                    title=f"指数涨跌家数断供 {it['symbol']}（{it.get('universe', '?')} 口径）",
                    message=self._message(it),
                    source=self._module_id,
                    labels={
                        "symbol": it["symbol"],
                        "universe": it.get("universe", ""),
                        "trailing_bad": trailing,
                        "total_bad": int(it.get("total_bad", 0)),
                        "gap_start": str(it.get("gap_start", "")),
                        "feed_task": "kline_index_breadth_refresh",
                    },
                    silence_window_s=self._silence,
                )
            )
        if scan_error:
            key = "breadth_scan_failed"
            active_keys.append(key)
            ops.append(
                self._safe_publish(
                    feed,
                    key=key,
                    severity="critical",
                    title="广度新鲜度哨兵自检失败（断供不可见风险）",
                    message=(
                        f"哨兵扫描异常：{scan_error}\n"
                        "本轮无法判定 kline_index 涨跌家数新鲜度——视同断供未证，"
                        "须人工确认 c1_market.kline_index 与 trade_calendar 可达"
                    ),
                    source=self._module_id,
                    labels={"feed_task": "breadth_freshness_sentinel"},
                    silence_window_s=self._silence,
                )
            )
        else:
            try:
                feed.resolve("breadth_scan_failed")
            except Exception as exc:  # noqa: BLE001
                logger.warning("breadth sentinel resolve(selfcheck) failed: %s", exc)

        # 解除联动：本模块活动板里本轮未再触发的 key → resolve（缺口填平后灰显）
        try:
            board_keys = {
                e.get("key")
                for e in feed.list_active()
                if e.get("module_id") == self._module_id and not e.get("resolved_at")
            }
            for k in sorted(x for x in board_keys - set(active_keys) if x):
                n = feed.resolve(str(k))
                if n:
                    ops.append({"op": "resolved", "key": k, "count": n})
        except Exception as exc:  # noqa: BLE001 — 解除联动失败不抛
            logger.warning("breadth sentinel resolve failed: %s", exc)
        return {"ops": ops, "active_keys": active_keys, "triggered": len(items)}

    @staticmethod
    def _message(it: dict[str, Any]) -> str:
        """告警正文：缺位天数/起止/缺行数——补位遮蔽真源缺失的外显证据。"""
        return (
            f"{it['symbol']} 涨跌家数连续 {it['trailing_bad']} 个交易日无值"
            f"（扫描窗内共 {it['total_bad']} 日缺位，起 {it.get('gap_start')}，"
            f"止 {it.get('gap_end')}，其中整行缺失 {it.get('missing_rows', 0)} 日）。"
            "进料件=kline_index_breadth_refresh（内生宇宙聚合）；"
            "消费端 EQW_ALLA 补位会掩盖本缺口——须修真源而非依赖补位"
        )


def run_check(
    today: datetime.date | None = None,
    board_dir: str | None = None,
    reader: Callable[[str], str] | None = None,
    lookback_days: int = _SCAN_LOOKBACK_DAYS,
) -> dict:
    """便捷入口：扫描 + 落板，返回摘要（供 internal provider 路由与手动巡检共用）。"""
    alerts = BreadthFreshnessAlerts(board_dir=board_dir, reader=reader)
    scan_error: str | None = None
    items: list[dict[str, Any]] = []
    try:
        items = alerts.scan(today=today, lookback_days=lookback_days)
    except Exception as exc:  # noqa: BLE001 — 告警线自身不得成为故障源
        logger.error("广度新鲜度哨兵扫描异常: %s", exc)
        scan_error = str(exc)[:300]
    res = alerts.publish(items, scan_error=scan_error)
    res["items"] = items
    res["scan_error"] = scan_error
    return res
