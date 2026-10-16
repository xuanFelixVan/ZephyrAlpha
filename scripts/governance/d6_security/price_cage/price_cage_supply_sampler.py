# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/price_cage/price_cage_supply_sampler.py | §
# [MODULE] scripts.governance.d6_security.price_cage.price_cage_supply_sampler
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.data.implementations.qmt_bridge_provider（QmtBridgeIngestProvider.probe 供数探活真源）；
#   zephyr.data.trading_calendar（is_trading_day 真源）；zephyr.data.calendar.ashare（ASHareCalendar 连续竞价时段）；
#   zephyr.shared.io.audit_jsonl_writer（append_audit_jsonl 证据追加）；zephyr.shared.utils.time_utils（now_utc）
# [CONSUMERS] scripts.governance.d6_security.price_cage.price_cage_unknown_reject_judge（证据面唯一消费方）；裁定#535 观察窗（5 交易日）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 非交易日/非连续竞价时段零写零副作用直接退出；fresh 判据三重=probe.quote_file.fresh∧age_s≤10s
#   （笼子 is_fresh 同口径）∧quote.csv 尾行第 29 列 timetag 与 now 差≤60s；证据面只追加不删改
#   （append_audit_jsonl 轮转语义）；判定真源=自建证据面（写端每 tick 追加/策略重启截断，事后判定不可依赖写端）；
#   零 SQL/零 LLM/零真实交易动作（只读探活+文件尾读+审计追加）
# [MODIFY-GUARD] none（唯一写面=.runtime/audit/price_cage_supply.jsonl 自建证据面；禁触 flags.yaml/price_cage.py/生产 data）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单次采样任何环节失败→fresh=false+reason 留证不抛；审计落盘失败→exit 1
#   （证据面静默缺失=判官假绿风险，宁红不静默）；probe 基础设施异常→按不新鲜留证（fail-visible）
# [TESTS] tests/gov/governance/test_price_cage_judge.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  观察窗周期采样 CLI（[STARTUP] manual 既有语义），非常驻系统，__main__+argv 即其合法形态
"""裁定#535「unknown_reject 武装核证」供数新鲜度采样器（观察窗证据面采集端）。

职责（单一）：交易时段内对 QMT 文件桥 quote 供数做一次三重新鲜度判定，追加一行
证据到 ``.runtime/audit/price_cage_supply.jsonl``；非交易日/非交易时段直接退出零写。
判官（price_cage_unknown_reject_judge.py）消费本证据面做 5 交易日逐日逐窗核证。

三重 fresh 判据（裁定#535 口径，取最严链）：
  1. probe().quote_file.fresh（QmtBridgeIngestProvider 真源，_FRESH_SECONDS=60）；
  2. quote_file.age_s ≤ 10s（笼子 QmtFileBridgeQuoteProvider.is_fresh 同口径 stale_seconds=10）；
  3. quote.csv 尾行第 29 列 timetag（格式 ``20261012 11:29:45``，北京墙钟）与 now 差 ≤60s——
     mtime 可被无关重写污染，行内 timetag 才是"最后一条行情真的新鲜"的直接证据。

证据行 schema（规格 6 字段+取证 3 字段）::

    {"date": "2026-10-15", "window": "am|pm", "ts": "<ISO 采样时刻>",
     "fresh": true|false, "age_s": 1.2, "env": "sim|real",
     "timetag": "20261015 10:00:01", "timetag_age_s": 3.5, "reason": "..."}

节奏建议：每窗口（09:30-11:30 / 13:00-15:00）≥30 次采样，建议每 2 分钟触发一次
（2h 窗口≈60 条）；触发面（计划任务/会话）由裁定#535 观察窗运行方案另行落地。

用法::

    python scripts/governance/d6_security/price_cage/price_cage_supply_sampler.py \
        [--audit-dir DIR] [--quote-file PATH] [--env sim|real]

exit: 0=已采样或按规零写退出；1=采样完成但审计落盘失败
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

_REPO = Path(__file__).resolve().parents[4]
_SRC = str(_REPO / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from zephyr.data.calendar.ashare import ASHareCalendar  # noqa: E402
from zephyr.data.trading_calendar import is_trading_day  # noqa: E402
from zephyr.shared.io.audit_jsonl_writer import append_audit_jsonl  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

__manifest__ = """
args:
- --audit-dir
- --quote-file
- --env
description: 裁定#535 unknown_reject 武装核证——供数新鲜度采样器（交易时段三重判定，证据追加 price_cage_supply.jsonl）
dimensions:
- D6
priority: P2
timeout_seconds: 60
warn_only: false
"""

#: 笼子新鲜度阈值（秒）——QmtFileBridgeQuoteProvider stale_seconds=10 同口径
CAGE_STALE_SECONDS: float = 10.0
#: 尾行 timetag 与 now 允许最大差（秒）——judge/裁定#535 口径
TIMETAG_MAX_AGE_S: float = 60.0
#: quote.csv timetag 列（0 基第 28 列 = 第 29 列；列布局见 qmt_file_bridge_quote.py 头注 8+5+5+5+5+1=29）
QUOTE_TIMETAG_COL: int = 28
#: timetag 解析格式（QMT 北京墙钟）
_TIMETAG_FMT = "%Y%m%d %H:%M:%S"

_CN_TZ = ZoneInfo("Asia/Shanghai")
_EVIDENCE_FILENAME = "price_cage_supply.jsonl"
_WINDOWS = ("am", "pm")  # 连续竞价两窗（与 ASHareCalendar._SESSION_WINDOWS 一一对应）


def session_window_of(t: time) -> str | None:
    """北京墙钟 → 所属连续竞价窗口（am/pm）；非时段返回 None。

    时段真源=ASHareCalendar._SESSION_WINDOWS（09:30-11:30 / 13:00-15:00）。
    """
    for name, (start, end) in zip(_WINDOWS, ASHareCalendar._SESSION_WINDOWS, strict=True):
        if start <= t <= end:
            return name
    return None


def read_quote_tail_timetag(quote_path: Path) -> str:
    """读 quote.csv 尾非空行的 timetag 列；文件缺/空/列不足返回空串（调用方按不新鲜留证）。"""
    try:
        with open(quote_path, encoding="utf-8", errors="replace") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
    except OSError:
        return ""
    if not lines:
        return ""
    cols = lines[-1].split(",")
    if len(cols) <= QUOTE_TIMETAG_COL:
        return ""
    return cols[QUOTE_TIMETAG_COL].strip()


def parse_timetag(raw: str) -> datetime | None:
    """解析 QMT timetag（``20261012 11:29:45``）→ 北京时区 aware datetime；不合法返回 None。"""
    if not raw:
        return None
    try:
        return datetime.strptime(raw, _TIMETAG_FMT).replace(tzinfo=_CN_TZ)
    except ValueError:
        return None


def sample_once(
    *,
    now_cn: datetime,
    window: str,
    env: str,
    probe_result: dict,
    quote_path_override: Path | None = None,
) -> dict:
    """单次采样判定（纯逻辑；probe/文件面由调用方注入，测试零mock副作用）。

    Args:
        now_cn: 采样时刻（北京时区 aware）。
        window: 所属连续竞价窗口（am/pm，由 run_sampler 时段判定传入）。
        env: 环境标识（sim/real）。
        probe_result: QmtBridgeIngestProvider.probe() 返回 dict。
        quote_path_override: 尾行读取路径覆盖（缺省取 probe.quote_file.path）。

    Returns:
        证据行 dict（规格 6 字段 + timetag/timetag_age_s/reason 取证字段）。
    """
    quote = probe_result.get("quote_file") or {}
    path = quote_path_override or Path(str(quote.get("path", "")))
    age_s = quote.get("age_s")
    tail = read_quote_tail_timetag(path)
    tt = parse_timetag(tail)
    tt_age = (now_cn - tt).total_seconds() if tt is not None else None

    reason = ""
    if not quote.get("exists"):
        reason = "quote_file_missing"
    elif not quote.get("fresh"):
        reason = "probe_not_fresh"
    elif age_s is None or float(age_s) > CAGE_STALE_SECONDS:
        reason = f"age_s_gt_{CAGE_STALE_SECONDS:g}"
    elif tt is None:
        reason = "timetag_unparseable"
    elif tt_age is not None and abs(tt_age) > TIMETAG_MAX_AGE_S:
        reason = f"timetag_age_gt_{TIMETAG_MAX_AGE_S:g}"

    record: dict = {
        "date": now_cn.date().isoformat(),
        "window": window,
        "ts": now_utc().isoformat(timespec="milliseconds"),
        "fresh": reason == "",
        "age_s": age_s,
        "env": env,
        "timetag": tail,
        "timetag_age_s": round(tt_age, 1) if tt_age is not None else None,
    }
    if reason:
        record["reason"] = reason
    return record


def run_sampler(
    *,
    now_cn: datetime,
    audit_dir: Path,
    quote_file: Path | None = None,
    env: str,
    probe_fn,
    trading_day: bool,
) -> int:
    """采样主链（时段/交易日判定→probe→判定→证据落盘）；返回进程 exit code。

    非交易日/非连续竞价时段：零写零副作用直接退出（裁定#535 证据面只收时段内样本）。
    """
    if not trading_day:
        print(f"[sampler] 非交易日（{now_cn.date().isoformat()}），零写退出")
        return 0
    window = session_window_of(now_cn.time())
    if window is None:
        print(f"[sampler] 非连续竞价时段（{now_cn.time().isoformat(timespec='minutes')}），零写退出")
        return 0
    try:
        probe_result = probe_fn()
    except Exception as e:  # noqa: BLE001 — probe 基础设施故障按不新鲜留证（fail-visible 不中断采样链）
        probe_result = {"alive": False, "quote_file": {"exists": False, "fresh": False}, "probe_error": str(e)}
    record = sample_once(
        now_cn=now_cn, window=window, env=env, probe_result=probe_result, quote_path_override=quote_file
    )
    ok = append_audit_jsonl(audit_dir, _EVIDENCE_FILENAME, record)
    if not ok:
        print(f"[sampler] 证据落盘失败: {audit_dir / _EVIDENCE_FILENAME}")
        return 1
    print(
        f"[sampler] {record['date']} {window} fresh={record['fresh']} "
        f"age_s={record['age_s']} timetag={record['timetag']!r}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="裁定#535 供数新鲜度采样器（单次采样，证据追加 price_cage_supply.jsonl）"
    )
    parser.add_argument(
        "--audit-dir", default=str(_REPO / ".runtime" / "audit"), help="证据面目录（缺省 <repo>/.runtime/audit）"
    )
    parser.add_argument("--quote-file", default=None, help="quote.csv 路径覆盖（缺省随 probe 返回面）")
    parser.add_argument(
        "--env", default=None, choices=("sim", "real"), help="环境标识（缺省读 TICK_BRIDGE_ENV，再缺省 sim）"
    )
    args = parser.parse_args(argv)

    now_cn = now_utc().astimezone(_CN_TZ)
    return run_sampler(
        now_cn=now_cn,
        audit_dir=Path(args.audit_dir),
        quote_file=Path(args.quote_file) if args.quote_file else None,
        env=args.env or os.environ.get("TICK_BRIDGE_ENV", "sim"),
        probe_fn=_default_probe_fn,
        trading_day=is_trading_day(now_cn.date()),
    )


def _default_probe_fn() -> dict:
    """真实探活入口（延迟导入，测试注入面）。"""
    from zephyr.data.implementations.qmt_bridge_provider import QmtBridgeIngestProvider

    return QmtBridgeIngestProvider().probe()


if __name__ == "__main__":
    sys.exit(main())
