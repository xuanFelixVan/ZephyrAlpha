# [BLUEPRINT] MOD-BT-090 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.sim_platform_journal
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.data.ch_config; zephyr.shared.alerts.alert_manager
# [CONSUMERS] c1_backtest.sim_platform_journal（平台日刊）；每日自动化（接线另批）；AI 检验接口消费方
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 一交易日一行平台汇总（幂等替换写）；健康检查三件=数据新鲜度/账本心跳/越界持仓；
#   异常经 AlertManager 告警（severity=warning，蓝图标降级）；只读体检+写日刊，不改钱包账
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(落库未确认/行情缺失)
# [TESTS] tests/backtest/test_sim_platform_journal.py
# [A_module] module_id=MOD-BT-090 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""模拟盘平台日刊生成器——每日全盘汇总+健康度三检+异常告警（平台蓝图批 2）。

每日收盘后跑一次：汇总所有钱包（sim_pocket_daily）权益与当日事件（sim_trade_log），
执行健康三检（行情新鲜度/账本心跳/越界持仓），异常写进日刊并经 AlertManager 告警。
用法：python scripts/backtest/sim_platform_journal.py [--date 2026-09-12]
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

logger = logging.getLogger(__name__)

QUOTA_WARNING = 1_100_000.0  # 钱包越界预警线（额度 100 万+10% 容差；额度分档见专题材料 §3）
CLOSE_CHECK_BJ = "15:05"  # 北京时刻收盘落库缓冲线（健检 1 时点感知判据，同保活循环收盘时点）


from schemas.categories.sim_pocket_daily import TABLE_NAME as _T_POCKET  # noqa: E402
from schemas.categories.sim_trade_log import TABLE_NAME as _T_TRADELOG  # noqa: E402

SQL_EVENTS_FOR_DAY = (
    f"SELECT count() FROM {_T_TRADELOG} FINAL"
    " WHERE trade_date = '{day}'"
)


def _q(sql: str):
    from zephyr.data.ch_writer import get_client_strict

    return get_client_strict().execute(sql)


def expected_fresh_date(day: str, now_bj: datetime | None = None) -> str:
    """健检 1 期望基准日（时点感知，R3 治本 2026-09-22 st-sim-launch）。

    事件链在交易日早间即跑日刊（08:42 北京实证），当日行情必未落——原口径
    "max >= 体检日" 在早间恒 false、degraded 恒 1（09-15..09-21 十行假阳性）。
    新口径：体检日为交易日且北京时刻未过 15:05（收盘落库缓冲）→ 期望=上一交易日
    （T-1 已落即新鲜）；收盘后/历史体检日/非交易日 → 期望=体检日本身（旧语义）。
    日历降级链同 zephyr.data.trading_calendar（XSHG→weekday），不可用时不放宽：
    回退期望=体检日本身（与旧口径一致，宁可假阳不可漏报）。
    """
    d = date.fromisoformat(day)
    now = now_bj or datetime.now(timezone(timedelta(hours=8)))
    after_close = now.date() > d or (now.date() == d and now.strftime("%H:%M") >= CLOSE_CHECK_BJ)
    if after_close:
        return day
    try:
        from zephyr.data.trading_calendar import is_trading_day, trading_days_in_range

        if not is_trading_day(d):
            return day
        prev = trading_days_in_range(d - timedelta(days=20), d - timedelta(days=1))
        return prev[-1].isoformat() if prev else day
    except Exception:  # noqa: BLE001 — 日历不可用=不放宽（fail-closed 回退旧口径）
        return day


def generate(day: str) -> dict:
    """体检+汇总指定交易日，返回日刊行（不落库）。"""
    sql_pockets = (
        "SELECT strategy_id, argMax(mode, ingest_ts), argMax(equity, ingest_ts),"
        " argMax(position_value, ingest_ts)"
        f" FROM {_T_POCKET} FINAL"
        f" WHERE trade_date = '{day}' GROUP BY strategy_id"
    )
    pockets = _q(sql_pockets)
    events = _q(SQL_EVENTS_FOR_DAY.format(day=day))
    kline_max = _q("SELECT max(trade_date) FROM c1_market.kline_index WHERE symbol = '000300'")[0][0]

    anomalies: list[str] = []
    # 在册外钱包隔离（R5 清偿 2026-09-22）：注册表 SSOT 卫兵止血了开户源头，
    # 存量孤儿钱包（STR-AUTO-001/STR-MULTIFACTOR-001 型）不再计入钱包数/总权益/
    # 越界检——否则平台汇总永远被幽灵 1M 污染；隔离是显式的（anomaly 注记留名），
    # 存量行零删除，处置归 Owner（lifecycle 终裁）。观察档 sim_observe 平面照常计入
    # （有翻译件重放的合法钱包）。
    registered_ids: set[str] | None
    try:
        import sim_paper_ledger as _ledger  # noqa: PLC0415

        registered_ids = {e["strategy_id"] for e in _ledger.registry_sim_entries()}
        registered_ids.add(_ledger.STRATEGY_ID)
    except Exception:  # noqa: BLE001 — 注册表不可读时不隔离（fail-open 保汇总不断）
        registered_ids = None
    counted: list = []
    quarantined: list[str] = []
    for r in pockets:
        is_observe = str(r[1]) == "sim_observe"
        row = (r[0], r[2], r[3])
        if registered_ids is not None and not is_observe and str(r[0]) not in registered_ids:
            quarantined.append(str(r[0]))
        else:
            counted.append(row)
    if quarantined:
        anomalies.append(f"在册外钱包已隔离（不计入汇总，存量处置呈 Owner）: {','.join(quarantined)}")
    pocket_count = len(counted)
    total_equity = round(sum(float(r[1] or 0) for r in counted), 2)
    summary = {r[0]: float(r[1] or 0) for r in counted}

    # 健检 1：行情数据新鲜度（收盘后须 >= 体检日；交易日早间 >= 上一交易日——时点感知）
    fresh_base = expected_fresh_date(day)
    fresh_ok = 1 if (kline_max and str(kline_max) >= fresh_base) else 0
    if not fresh_ok:
        anomalies.append(f"行情数据不新鲜: kline_index max={kline_max} < 期望基准 {fresh_base}（体检日 {day}）")

    # 健检 2：账本心跳（活跃钱包当日均有行；0 钱包=平台未跑，也记异常）
    if pocket_count == 0:
        heartbeat_ok, anomalies = 0, anomalies + [f"账本心跳缺失: {day} 无任何钱包行"]
    else:
        heartbeat_ok = 1

    # 健检 3：越界持仓（钱包持仓市值超额度预警线；在册外钱包已在上面隔离）
    for sid, equity, pos_val in counted:
        if float(pos_val or 0) > QUOTA_WARNING:
            anomalies.append(f"越界持仓: {sid} 持仓市值 {pos_val} 超预警线 {QUOTA_WARNING}")

    degraded = 1 if anomalies else 0
    return {
        "row": [
            day,
            pocket_count,
            total_equity,
            json.dumps(summary, ensure_ascii=False),
            int(events[0][0]),
            fresh_ok,
            heartbeat_ok,
            json.dumps(anomalies, ensure_ascii=False),
            degraded,
        ],
        "anomalies": anomalies,
        "degraded": degraded,
    }


def alert_if_degraded(day: str, anomalies: list[str]) -> None:
    if not anomalies:
        return
    from zephyr.shared.alerts.alert_manager import AlertManager, AlertSeverity

    mgr = AlertManager()
    mgr.raise_alert(
        title=f"模拟盘平台异常 {day}",
        severity=AlertSeverity.WARNING,
        source="sim_platform_journal",
        message="; ".join(anomalies)[:500],
    )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="模拟盘平台日刊生成器（批2）")
    ap.add_argument("--date", default=date.today().strftime("%Y-%m-%d"))
    ap.add_argument("--no-alert", action="store_true", help="只写日刊不触发告警")
    args = ap.parse_args()
    day = args.date
    res = generate(day)
    from zephyr.data import ch_writer

    def cell(v):
        if v is None:
            return chr(92) + "N"
        return str(v).replace(chr(9), " ").replace(chr(10), " ")

    cols = (
        "(trade_date, pocket_count, total_equity, pockets_summary, event_count,"
        " data_freshness_ok, heartbeat_ok, anomalies, degraded, run_id, note)"
    )
    row = res["row"] + [f"journal-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}", "平台日刊 批2"]
    tsv = "\t".join(cell(v) for v in row) + "\n"
    if not ch_writer.write_tsv("c1_backtest.sim_platform_journal", cols, tsv.encode("utf-8")):
        raise RuntimeError("日刊落库未确认——fail-closed")
    if res["anomalies"] and not args.no_alert:
        alert_if_degraded(day, res["anomalies"])
    print(
        json.dumps(
            {
                "date": day,
                "pockets": res["row"][1],
                "total_equity": res["row"][2],
                "anomalies": res["anomalies"],
                "degraded": res["row"][8],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
