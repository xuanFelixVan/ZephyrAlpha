# [BLUEPRINT] MOD-BT-151 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.compute_window_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config
# [CONSUMERS] 策略生产全景图 FAC-E0 算力调度心跳；重算力任务开工闸（挖掘训练/批测/遗传优化
#   开工前必查）；FAC-E1 进货编排（下游消费方）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 纯拉式闸门（pull gate）——事件=任务到点开工前来问，本模块无常驻循环
#   无 cron/sleep-loop（宪法铁律：事件触发禁定时器）；日历缺失 fail-closed 拒重放行；
#   时间一律 Asia/Shanghai tz-aware（naive datetime 拒收）；交易时窗收盘缓冲 15:30
#   （给收盘结算留 30 分钟保守带）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError(naive datetime); RuntimeError(日历通道不可达);
#   SystemExit(0)=放行 SystemExit(3)=拒 SystemExit(1)=基础设施失败(CLI)
# [TESTS] tests/backtest/test_compute_window_gate.py
# [A_module] module_id=MOD-BT-151 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  手动 CLI 闸门检查器非常驻服务：闸门本体为函数库由任务开工事件调用，CLI 仅为人工核查入口
"""FAC-E0 算力调度心跳——trade_calendar 闸门：交易日白天只许轻任务，重算力排收盘后/休市日。

原理（图9 FAC-E0 algo_note + 讨论稿 v4/v5）：回测量是算力成本大头，自研薄调度层
（不引 Airflow/Dagster）。设计=拉式闸门：重算力任务在被事件触发的开工时刻先调
check_gate() 问闸，交易日盘中（is_open=1 且 <15:30）拒重放轻；休市日/收盘后放行。
日历缺失 fail-closed（宁停不裸奔）。本模块不含任何调度循环——四要素中的"自动触发"
由各任务自身的既有事件链承担（automation/数据到达），闸门只在开工瞬间被问一次。

用法:
  python scripts/backtest/compute_window_gate.py check --purpose c4_batch --compute-class heavy
  python scripts/backtest/compute_window_gate.py window
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, time as dtime
from zoneinfo import ZoneInfo

_TZ = ZoneInfo("Asia/Shanghai")
CLOSE_BUFFER = dtime(15, 30)  # 收盘缓冲：15:30 后视为盘后

COMPUTE_LIGHT = "light"
COMPUTE_HEAVY = "heavy"
# 图9 节点 compute_class → 默认权重档（local/api 轻任务随时跑；GPU/混合=重算力受闸）
NODE_CLASS_WEIGHT = {"local": COMPUTE_LIGHT, "api": COMPUTE_LIGHT,
                     "local_gpu": COMPUTE_HEAVY, "mixed": COMPUTE_HEAVY}

WINDOW_LIGHT_ONLY = "light_only"
WINDOW_HEAVY_OK = "heavy_ok"

REASON_ALLOW_LIGHT = "gate_allow_light_always"
REASON_ALLOW_OFFHOURS = "gate_allow_off_hours"
REASON_DENY_TRADING_HOURS = "gate_deny_trading_hours"
REASON_DENY_CALENDAR_UNKNOWN = "gate_deny_calendar_unknown"


def _require_aware(now: datetime) -> datetime:
    if now.tzinfo is None:
        raise ValueError("naive datetime 拒收（RULE-SCHEMA-TZ）：须带 Asia/Shanghai tzinfo")
    return now


def classify_window(now: datetime, is_trading_day: bool) -> str:
    """纯函数：当前时刻的算力窗档（盘中=light_only，盘后/休市=heavy_ok）。"""
    _require_aware(now)
    local = now.astimezone(_TZ)
    if not is_trading_day:
        return WINDOW_HEAVY_OK
    if local.time() >= CLOSE_BUFFER:
        return WINDOW_HEAVY_OK
    return WINDOW_LIGHT_ONLY


def needs_heavy_window(node_compute_class: str) -> bool:
    """图9 compute_class → 是否重算力（缺省从重 fail-closed）。"""
    return NODE_CLASS_WEIGHT.get(node_compute_class, COMPUTE_HEAVY) == COMPUTE_HEAVY


def gate_decision(purpose: str, heavy: bool, now: datetime,
                  is_trading_day: bool | None) -> dict:
    """纯函数：闸门判决（理由码代码生成；日历未知时对重任务 fail-closed）。"""
    _require_aware(now)
    if not heavy:
        return {"allowed": True, "reason_code": REASON_ALLOW_LIGHT,
                "window": None, "purpose": purpose}
    if is_trading_day is None:
        return {"allowed": False, "reason_code": REASON_DENY_CALENDAR_UNKNOWN,
                "window": None, "purpose": purpose}
    window = classify_window(now, is_trading_day)
    if window == WINDOW_HEAVY_OK:
        return {"allowed": True, "reason_code": REASON_ALLOW_OFFHOURS,
                "window": window, "purpose": purpose}
    return {"allowed": False, "reason_code": REASON_DENY_TRADING_HOURS,
            "window": window, "purpose": purpose}


SQL_CAL_DAY = (
    "SELECT is_open FROM c1_market.trade_calendar "
    "WHERE exchange = 'SSE' AND cal_date = %(d)s LIMIT 1"
)


def fetch_is_trading_day(d: date) -> bool | None:
    """CH 日历单日查询（SSE 口径；日历未覆盖/通道故障返回 None → 上层 fail-closed）。"""
    try:
        from zephyr.data.ch_writer import get_client_strict

        cli = get_client_strict()
        rows = cli.execute(SQL_CAL_DAY, {"d": d})
        if not rows:
            return None
        return bool(rows[0][0])
    except Exception:  # noqa: BLE001 — 日历不可达 → None（fail-closed 由 gate_decision 落码）
        return None


def check_gate(purpose: str, node_compute_class: str = "local_gpu",
               now: datetime | None = None) -> dict:
    """开工闸门（重算力任务开工事件的第一问）。"""
    now = now or datetime.now(_TZ)
    _require_aware(now)
    heavy = needs_heavy_window(node_compute_class)
    is_td = fetch_is_trading_day(now.astimezone(_TZ).date()) if heavy else True
    return gate_decision(purpose, heavy, now, is_td)


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E0 算力闸门（trade_calendar 当闸，事件触发）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="重算力开工问闸（exit 0=放行 3=拒）")
    c.add_argument("--purpose", required=True, help="用途标识（如 c4_batch/gp_mine）")
    c.add_argument("--compute-class", default="local_gpu",
                   choices=sorted(NODE_CLASS_WEIGHT), help="图9 节点 compute_class")
    sub.add_parser("window", help="看当前算力窗档")
    args = ap.parse_args()
    now = datetime.now(_TZ)
    if args.cmd == "window":
        is_td = fetch_is_trading_day(now.date())
        window = classify_window(now, is_td) if is_td is not None else None
        print(json.dumps({"now": now.isoformat(), "is_trading_day": is_td,
                          "window": window}, ensure_ascii=False))
        return 0
    try:
        decision = check_gate(args.purpose, args.compute_class, now)
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(decision, ensure_ascii=False))
    return 0 if decision["allowed"] else 3


if __name__ == "__main__":
    sys.exit(main())
