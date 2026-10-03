# [BLUEPRINT] MOD-BT-151 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.compute_window_gate
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_config; zephyr.backtest.core.batch_window_preflight（点火面前置）
# [CONSUMERS] 策略生产全景图 FAC-E0 算力调度心跳；重算力任务开工闸（挖掘训练/批测/遗传优化
#   开工前必查）；FAC-E1 进货编排（下游消费方）；波12 统一跑批窗口点火面
#   （purpose ∈ batch_window_preflight.W12_WINDOW_PURPOSES 时先过五触发条件+批准卡，再判日历窗）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 纯拉式闸门（pull gate）——事件=任务到点开工前来问，本模块无常驻循环
#   无 cron/sleep-loop（宪法铁律：事件触发禁定时器）；日历缺失 fail-closed 拒重放行；
#   时间一律 Asia/Shanghai tz-aware（naive datetime 拒收）；交易时窗收盘缓冲 15:30
#   （给收盘结算留 30 分钟保守带）；波12 点火类 purpose 另加"触发条件+批准卡"前置且
#   预检不可读亦拒（本闸是重算力唯一问闸面，点火判据不另立第二道 gate）
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
  python scripts/backtest/compute_window_gate.py check --purpose wave12_t2_final --compute-class local_gpu
  python scripts/backtest/compute_window_gate.py window
  python scripts/backtest/compute_window_gate.py preflight   # 波12 五触发条件机读判决（不改判据）
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import date, datetime
from datetime import time as dtime
from zoneinfo import ZoneInfo

from zephyr.data.table_registry import TableRegistry

log = logging.getLogger(__name__)

_TZ = ZoneInfo("Asia/Shanghai")
CLOSE_BUFFER = dtime(15, 30)  # 收盘缓冲：15:30 后视为盘后
OPEN_BUFFER = dtime(9, 0)  # 开盘缓冲：09:00 前视为凌晨盘外（重算力黄金窗，
# 与收盘 30 分钟缓冲对称的开盘前 30 分钟保守带）

COMPUTE_LIGHT = "light"
COMPUTE_HEAVY = "heavy"
# 图9 节点 compute_class → 默认权重档（local/api 轻任务随时跑；GPU/混合=重算力受闸）
NODE_CLASS_WEIGHT = {"local": COMPUTE_LIGHT, "api": COMPUTE_LIGHT, "local_gpu": COMPUTE_HEAVY, "mixed": COMPUTE_HEAVY}

WINDOW_LIGHT_ONLY = "light_only"
WINDOW_HEAVY_OK = "heavy_ok"

REASON_ALLOW_LIGHT = "gate_allow_light_always"
REASON_ALLOW_OFFHOURS = "gate_allow_off_hours"
REASON_DENY_TRADING_HOURS = "gate_deny_trading_hours"
REASON_DENY_CALENDAR_UNKNOWN = "gate_deny_calendar_unknown"
# 波12 统一跑批窗口点火面（MOD-BT-226 预检器 + 本闸组合；判据真源在 W 册 §波12）
REASON_ALLOW_IGNITION_ARMED = "gate_allow_wave12_ignition_armed"
REASON_DENY_IGNITION_NOT_ARMED = "gate_deny_wave12_ignition_not_armed"
REASON_DENY_IGNITION_PREFLIGHT_FAILED = "gate_deny_wave12_preflight_unreadable"
#: 点火类 purpose 命名法——前缀即识别法，预检器导入失败也不漏判（fail-closed 不依赖集合读得到）
IGNITION_PURPOSE_PREFIX = "wave12_"

try:  # 预检器不可用时置空集：前缀判据仍生效，点火判决本身由 check_ignition 落拒
    from zephyr.backtest.core.batch_window_preflight import W12_WINDOW_PURPOSES as _W12_PURPOSES
except Exception:  # noqa: BLE001 - 缺依赖=点火面不可判，由 check_ignition 统一 fail-closed
    _W12_PURPOSES = frozenset()


def _require_aware(now: datetime) -> datetime:
    if now.tzinfo is None:
        raise ValueError("naive datetime 拒收（RULE-SCHEMA-TZ）：须带 Asia/Shanghai tzinfo")
    return now


def classify_window(now: datetime, is_trading_day: bool) -> str:
    """纯函数：当前时刻的算力窗档。

    交易日 09:00-15:30（开盘前缓冲到收盘后缓冲的保守带）=light_only；
    凌晨 00:00-09:00（盘外黄金窗）与 15:30 后、以及休市日=heavy_ok。
    （2026-09-16 治本：原实现把交易日 00:00-09:30 全段误判盘中，凌晨重算力
    被 gate_deny_trading_hours 拒——09-14 07:10/07:11 与 09-16 00:21 三次
    误拒实证；盘外时段恰是无人值守重算力的主窗口。）
    """
    _require_aware(now)
    local = now.astimezone(_TZ)
    if not is_trading_day:
        return WINDOW_HEAVY_OK
    t = local.time()
    if t >= CLOSE_BUFFER or t < OPEN_BUFFER:
        return WINDOW_HEAVY_OK
    return WINDOW_LIGHT_ONLY


def needs_heavy_window(node_compute_class: str) -> bool:
    """图9 compute_class → 是否重算力（缺省从重 fail-closed）。"""
    return NODE_CLASS_WEIGHT.get(node_compute_class, COMPUTE_HEAVY) == COMPUTE_HEAVY


def gate_decision(purpose: str, heavy: bool, now: datetime, is_trading_day: bool | None) -> dict:
    """纯函数：闸门判决（理由码代码生成；日历未知时对重任务 fail-closed）。"""
    _require_aware(now)
    if not heavy:
        return {"allowed": True, "reason_code": REASON_ALLOW_LIGHT, "window": None, "purpose": purpose}
    if is_trading_day is None:
        return {"allowed": False, "reason_code": REASON_DENY_CALENDAR_UNKNOWN, "window": None, "purpose": purpose}
    window = classify_window(now, is_trading_day)
    if window == WINDOW_HEAVY_OK:
        return {"allowed": True, "reason_code": REASON_ALLOW_OFFHOURS, "window": window, "purpose": purpose}
    return {"allowed": False, "reason_code": REASON_DENY_TRADING_HOURS, "window": window, "purpose": purpose}


# 日历表名走 TableRegistry 真源（#ARCH-CH-024；q-…-0008 死信处方）——运行时拼出的
# 全限定名与原字面量逐字相等（market_trade_calendar → c1_market.trade_calendar）
SQL_CAL_DAY = (
    "SELECT is_open FROM "
    + TableRegistry().table("market_trade_calendar")
    + " WHERE exchange = 'SSE' AND cal_date = %(d)s LIMIT 1"
)


def fetch_is_trading_day(d: date) -> bool | None:
    """CH 日历单日查询（SSE 口径；日历未覆盖/通道故障返回 None → 上层 fail-closed）。

    2026-10-04 治本（FactoryLaneC 10-02 20:00 rc=3 复盘，EXEC-3）：CH 瞬时不可达
    （备份窗/连接抖动）原与"日历真缺行"同判 None 且零留痕，重算力整夜被拒无重试。
    本修：①吞异常前 log 留痕；②通道异常立即有界重试（1 首查+2 补试，无 sleep——
    永久系统禁 Timer/sleep-loop 铁律，PERM-TRIGGER 门裁定；秒级抖动可吸收，长故
    障仍 fail-closed）。日历真缺行（rows 空）是确定性答案，不重试。
    """
    for attempt in range(3):
        try:
            from zephyr.data.ch_writer import get_client_strict

            cli = get_client_strict()
            rows = cli.execute(SQL_CAL_DAY, {"d": d})
            if not rows:
                return None
            return bool(rows[0][0])
        except Exception as exc:  # noqa: BLE001 — 留痕后重试；末次仍败 → None（fail-closed 由 gate_decision 落码）
            log.warning(
                "trade_calendar 查询失败（attempt=%d/3 date=%s）: %s: %s", attempt + 1, d, type(exc).__name__, exc
            )
    return None


def needs_ignition_check(purpose: str) -> bool:
    """本 purpose 是否属波12 统一跑批窗口（须先过五触发条件+批准卡）。"""
    return purpose.startswith(IGNITION_PURPOSE_PREFIX) or purpose in _W12_PURPOSES


def check_ignition(purpose: str, now: datetime | None = None) -> dict:
    """波12 点火前置问：五条触发条件全绿 **且** 批准卡生效才放行。

    fail-closed 三态全拒——①任一条件 RED ②任一条件 UNKNOWN（读不到≠干净）
    ③批准卡缺失/未 APPROVED/批文锚在裁定册查无/与现役 prereg 摘要不一致。
    预检器本身不可用同样拒（禁"预检崩了=没这个闸"）。
    """
    now = _require_aware(now or datetime.now(_TZ))
    try:
        from zephyr.backtest.core import batch_window_preflight as bwp

        verdict = bwp.run_preflight(bwp.build_context(now=now))
    except Exception as exc:  # noqa: BLE001 - 预检不可读=拒放行（与日历不可达同构）
        return {
            "allowed": False,
            "purpose": purpose,
            "window": None,
            "reason_code": REASON_DENY_IGNITION_PREFLIGHT_FAILED,
            "blocking": ["preflight_unreadable"],
            "detail": f"{type(exc).__name__}: {str(exc)[:200]}",
        }
    if verdict.allowed:
        return {
            "allowed": True,
            "purpose": purpose,
            "window": None,
            "reason_code": REASON_ALLOW_IGNITION_ARMED,
            "blocking": [],
            "detail": "五触发条件全绿且批准卡生效",
        }
    return {
        "allowed": False,
        "purpose": purpose,
        "window": None,
        "reason_code": REASON_DENY_IGNITION_NOT_ARMED,
        "blocking": list(verdict.blocking),
        "detail": bwp.blocking_detail(verdict),
    }


def check_gate(
    purpose: str, node_compute_class: str = "local_gpu", now: datetime | None = None, ignition: bool | None = None
) -> dict:
    """开工闸门（重算力任务开工事件的第一问）。

    波12 窗口类 purpose 先过点火闸（触发条件+批准卡），再走原日历窗判据——
    日历判据/阈值/轻活语义零改动（点火面只是**加**前置，不减不放）。
    """
    now = now or datetime.now(_TZ)
    _require_aware(now)
    want_ignition = needs_ignition_check(purpose) if ignition is None else bool(ignition)
    if want_ignition:
        armed = check_ignition(purpose, now)
        if not armed.get("allowed"):
            return armed
    heavy = needs_heavy_window(node_compute_class)
    is_td = fetch_is_trading_day(now.astimezone(_TZ).date()) if heavy else True
    decision = gate_decision(purpose, heavy, now, is_td)
    if want_ignition and decision.get("allowed"):
        decision = {**decision, "ignition": REASON_ALLOW_IGNITION_ARMED}
    return decision


def main() -> int:
    ap = argparse.ArgumentParser(description="FAC-E0 算力闸门（trade_calendar 当闸，事件触发）")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="重算力开工问闸（exit 0=放行 3=拒）")
    c.add_argument("--purpose", required=True, help="用途标识（如 c4_batch/gp_mine）")
    c.add_argument(
        "--compute-class", default="local_gpu", choices=sorted(NODE_CLASS_WEIGHT), help="图9 节点 compute_class"
    )
    c.add_argument(
        "--ignition", action="store_true", help="强制按波12 窗口类过点火闸（purpose 带 wave12_ 前缀时自动启用）"
    )
    sub.add_parser("window", help="看当前算力窗档")
    sub.add_parser("preflight", help="波12 五触发条件+批准卡机读判决（只读，不改判据）")
    args = ap.parse_args()
    now = datetime.now(_TZ)
    if args.cmd == "preflight":
        decision = check_ignition("wave12_preflight", now)
        print(json.dumps(decision, ensure_ascii=False, indent=2))
        return 0 if decision["allowed"] else 3
    if args.cmd == "window":
        is_td = fetch_is_trading_day(now.date())
        window = classify_window(now, is_td) if is_td is not None else None
        print(json.dumps({"now": now.isoformat(), "is_trading_day": is_td, "window": window}, ensure_ascii=False))
        return 0
    try:
        decision = check_gate(
            args.purpose, args.compute_class, now, ignition=True if getattr(args, "ignition", False) else None
        )
    except RuntimeError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(decision, ensure_ascii=False))
    return 0 if decision["allowed"] else 3


if __name__ == "__main__":
    sys.exit(main())
