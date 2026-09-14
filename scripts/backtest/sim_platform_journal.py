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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

QUOTA_WARNING = 1_100_000.0  # 钱包越界预警线（额度 100 万+10% 容差；额度分档见专题材料 §3）


def _q(sql: str):
    from zephyr.data.ch_writer import get_client_strict

    return get_client_strict().execute(sql)



def generate(day: str) -> dict:
    """体检+汇总指定交易日，返回日刊行（不落库）。"""
    pockets = _q(
        "SELECT strategy_id, argMax(equity, ingest_ts), argMax(position_value, ingest_ts)"
        " FROM c1_backtest.sim_pocket_daily FINAL"
        f" WHERE trade_date = '{day}' GROUP BY strategy_id")
    events = _q(
        "SELECT count() FROM c1_backtest.sim_trade_log FINAL"
        f" WHERE trade_date = '{day}'")
    kline_max = _q("SELECT max(trade_date) FROM c1_market.kline_index WHERE symbol = '000300'")[0][0]

    anomalies: list[str] = []
    pocket_count = len(pockets)
    total_equity = round(sum(float(r[1] or 0) for r in pockets), 2)
    summary = {r[0]: float(r[1] or 0) for r in pockets}

    # 健检 1：行情数据新鲜度（行情表最新日期须 >= 体检日）
    fresh_ok = 1 if (kline_max and str(kline_max) >= day) else 0
    if not fresh_ok:
        anomalies.append(f"行情数据不新鲜: kline_index max={kline_max} < 体检日 {day}")

    # 健检 2：账本心跳（活跃钱包当日均有行；0 钱包=平台未跑，也记异常）
    if pocket_count == 0:
        heartbeat_ok, anomalies = 0, anomalies + [f"账本心跳缺失: {day} 无任何钱包行"]
    else:
        heartbeat_ok = 1

    # 健检 3：越界持仓（钱包持仓市值超额度预警线）
    for sid, equity, pos_val in pockets:
        if float(pos_val or 0) > QUOTA_WARNING:
            anomalies.append(f"越界持仓: {sid} 持仓市值 {pos_val} 超预警线 {QUOTA_WARNING}")

    degraded = 1 if anomalies else 0
    return {
        "row": [day, pocket_count, total_equity, json.dumps(summary, ensure_ascii=False),
                int(events[0][0]), fresh_ok, heartbeat_ok,
                json.dumps(anomalies, ensure_ascii=False), degraded],
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

    cols = ("(trade_date, pocket_count, total_equity, pockets_summary, event_count,"
            " data_freshness_ok, heartbeat_ok, anomalies, degraded, run_id, note)")
    row = res["row"] + [f"journal-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                        "平台日刊 批2"]
    tsv = "\t".join(cell(v) for v in row) + "\n"
    if not ch_writer.write_tsv("c1_backtest.sim_platform_journal", cols, tsv.encode("utf-8")):
        raise RuntimeError("日刊落库未确认——fail-closed")
    if res["anomalies"] and not args.no_alert:
        alert_if_degraded(day, res["anomalies"])
    print(json.dumps({"date": day, "pockets": res["row"][1], "total_equity": res["row"][2],
                      "anomalies": res["anomalies"], "degraded": res["row"][8]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
