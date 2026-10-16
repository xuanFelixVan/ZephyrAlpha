#!/usr/bin/env python3
# [BLUEPRINT] MOD-SECTOR_LINE | docs/04_research_records/data/sector_line/sector_layer_skeleton_v0.md | §1 基线冻结
# [MODULE] scripts.sector_line.freeze_baseline
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.infrastructure.database_service (CH reader)
# [CONSUMERS] scripts.sector_line.build_gpu_input_pack（链 hash 单一真源）；状态回放深窗对拍（replay_report.md 两轮）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读（DatabaseService role='reader'，服务端 readonly=1）；零写库；禁用 ch_writer.query（实测其出错返回 ''，与真零行 '0不可辨→深度幻觉）；日期字面量必加引号（裸 2015-01-01 被 CH 解析成算术式）；tz-aware now（RULE-SCHEMA-TZ 禁 datetime.now()/utcnow()/time.time()）
# [MODIFY-GUARD] hash 格式化口径（fmt/_chain/snapshot）=唯一真源，禁改——改=全仓基线作废重冻
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 基线漂移→exit 2；连接失败→exit 3；正常→exit 0。永不静默吞异常。
# [TESTS] 手工红证 --selftest-red（微扰一收盘价链 hash 必变）+ --manifest 对拍两轮（replay_report.md 在案）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的 permanent CLI runner（880 链基线冻结/自验工具，exit 契约 0/2/3），非 cron 非 daemon 非常驻服务，会话显式触发
"""freeze_baseline.py — 状态层回放·活值与 880 板块日K 基线冻结器（可重跑断言零漂移）。"""

from __future__ import annotations

import argparse
import decimal
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from zephyr.data.table_registry import get_registry
from zephyr.infrastructure.database_service import DatabaseService

KLINE_HASH_SEED = "kline_sector_880/1d"
STATE_COLS = (
    "momentum_pct",
    "rrg_quadrant",
    "strength",
    "net_inflow_pct",
    "capital_score",
    "watch_score",
    "version",
    "ts",
)

# 表名唯一真源=TableRegistry（#ARCH-CH-024 Phase 5），禁硬编码字符串
_T_K880 = get_registry().table("market_sector_kline_880")
_T_SSTATE = get_registry().table("market_sector_state")
SQL_K880_1D = (
    "SELECT trade_date, sector_code, close, amount FROM " + _T_K880 + " FINAL "
    "WHERE period = '1d' ORDER BY trade_date, sector_code"
)
SQL_STATE_LIVE = (
    "SELECT trade_date, stage, sector_code, "
    + ", ".join(STATE_COLS)
    + " FROM "
    + _T_SSTATE
    + " ORDER BY trade_date, stage, sector_code"
)


def fmt(v: object) -> str:
    if v is None:
        return "\x00NULL"
    if isinstance(v, decimal.Decimal):
        return f"{v:.8f}"
    if isinstance(v, float):
        return f"{v:.12g}"
    if isinstance(v, (date, datetime)):
        return v.isoformat()[:10]
    return str(v)


def _chain(per_day: dict[str, str]) -> str:
    return hashlib.sha256("".join(f"{d}:{per_day[d]}\n" for d in sorted(per_day)).encode()).hexdigest()


def snapshot(conn: object, *, perturb: bool = False) -> dict[str, object]:
    krows = conn.execute(SQL_K880_1D)  # type: ignore[attr-defined]  # FINAL=裁定 #ARCH-CH-007：ReplacingMergeTree 读侧强制去重，冻结基线须确定性单版本
    days: dict[str, list[str]] = {}
    target = min(r[1] for r in krows) if perturb else None
    for td, sc, cl, am in krows:
        if target is not None and sc == target:
            cl = cl + decimal.Decimal("0.0001")  # selftest-only nudge
        days.setdefault(td.isoformat()[:10], []).append(f"{sc}|{fmt(cl)}|{fmt(am)}")
    kper = {d: hashlib.sha256("\n".join(v).encode()).hexdigest() for d, v in days.items()}

    srows = conn.execute(SQL_STATE_LIVE)  # type: ignore[attr-defined]
    sp: dict[str, list[str]] = {}
    for r in srows:
        sp.setdefault(r[0].isoformat()[:10], []).append(f"{r[1]}|{r[2]}|" + "|".join(fmt(x) for x in r[3:]))
    sper = {d: hashlib.sha256("\n".join(sorted(v)).encode()).hexdigest() for d, v in sp.items()}

    return {
        "kline_sector_880_1d": {
            "rows": len(krows),
            "days": len(kper),
            "first": min(kper),
            "last": max(kper),
            "chain_sha256": _chain(kper),
            "per_day_sha256": kper,
        },
        "sector_state_live": {
            "rows": len(srows),
            "days": len(sper),
            "first": min(sper),
            "last": max(sper),
            "chain_sha256": _chain(sper),
            "cols": list(STATE_COLS),
            "per_day_sha256": sper,
            "null_counts": {c: sum(1 for r in srows if r[3 + i] is None) for i, c in enumerate(STATE_COLS)},
        },
        "taken_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="freeze_baseline.py")
    ap.add_argument("--manifest", help="既有基线 json；给出则断言零漂移")
    ap.add_argument("--write", help="把本次基线写到此路径")
    ap.add_argument(
        "--selftest-red", action="store_true", help="红证：微扰一个收盘价，断言链 hash 必变（脚本能红=判定可信）"
    )
    a = ap.parse_args(argv)

    conn = DatabaseService().get_clickhouse_conn("reader")
    try:
        cur = snapshot(conn)
    except Exception as e:  # noqa: BLE001  fail-visible：本件绝不做 ch_writer 式静默空返回；ERROR_CONTRACT 契约出口=打印类型+exit 3，非静默吞
        print(f"ERROR: baseline snapshot failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 3

    if a.selftest_red:
        base, pert = (
            cur["kline_sector_880_1d"]["chain_sha256"],
            snapshot(conn, perturb=True)["kline_sector_880_1d"]["chain_sha256"],
        )
        ok = base != pert
        print(f"[RED-PROOF] perturbed hash differs: {ok}  ({base[:12]} -> {pert[:12]})")
        return 0 if ok else 2

    print(
        f"880 1d   rows={cur['kline_sector_880_1d']['rows']:>7} days={cur['kline_sector_880_1d']['days']}"
        f" chain={cur['kline_sector_880_1d']['chain_sha256']}"
    )
    print(
        f"state    rows={cur['sector_state_live']['rows']:>7} days={cur['sector_state_live']['days']}"
        f" chain={cur['sector_state_live']['chain_sha256']}"
    )
    print(f"nulls    { {k: v for k, v in cur['sector_state_live']['null_counts'].items() if v} }")

    if a.write:
        p = Path(a.write)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"wrote {p}")
    if a.manifest:
        prev = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
        drift = [
            t for t in ("kline_sector_880_1d", "sector_state_live") if prev[t]["chain_sha256"] != cur[t]["chain_sha256"]
        ]
        if drift:
            print(f"DRIFT in {drift}: 上游回补使基线作废，对拍必须重做", file=sys.stderr)
            return 2
        print("MATCH: 零漂移，对拍基线仍有效")
    return 0


if __name__ == "__main__":
    sys.exit(main())
