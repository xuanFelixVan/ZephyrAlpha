# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.data.tilib_dwm_shard_runner
# noqa: m11-perm-manual-legitimate  tilib_indicator_backfill_nightly 计划任务 02:30 经 backfill_night.ps1 自动触发（永久自动化正门），兼 Owner/施工会话手动续跑运维件，人工触发是设计意图非缺陷
# [DOMAIN] D_DATA
# [DEPENDENCIES] scripts.data.backfill_technical_indicator_dwm
# [CONSUMERS] tilib_indicator_backfill_nightly 计划任务（backfill_night.bat）；Owner/施工会话手动触发
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 单进程串行分片（并发=内存总闸 Code 241 复发）；每片独立子进程跑
#  backfill_technical_indicator_dwm.py --symbols-file <片清单>（进程级内存隔离）；
#  每片完成写 data/runtime/dwm_shard_state/<period>_shard_<i>.json，重跑跳过 exit=0 片
#  （幂等：ReplacingMergeTree 同键覆盖，重叠无害）；失败片记录 error 后继续下一片。
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单片 exit!=0 不中断（隔毒片），全部跑完汇总 rc=1
# [TESTS] 本 CLI 以 --help 自测；破坏面=指标表同键覆盖（幂等）
# [TTL] permanent
"""tilib 夜跑 dwm 指标回填分片编排器（2026-09-22 tracked 化，裁定#399）。

背景（Code 241 内存总闸阵亡治本，原 .runtime/tmp 临时版 st-data-fix-20260921）：
- 每片 = 独立子进程跑 backfill_technical_indicator_dwm.py --symbols-file <片清单>
  → 进程级内存隔离，单片阵亡不污染主进程，崩了续跑下一片。
- 每片完成写 data/runtime/dwm_shard_state/<period>_shard_<i>.json
  → 重跑本脚本自动跳过已完成片（幂等：ReplacingMergeTree 同键覆盖，重叠无害）。
- 失败片记录 error 后继续下一片（隔离毒片），全部跑完后汇总 exit 非零。

用法：
    python scripts/data/tilib_dwm_shard_runner.py --periods daily            # 默认 100 标的/片
    python scripts/data/tilib_dwm_shard_runner.py --periods daily --only-shard 3   # 单片重跑
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE_DIR = REPO / "data" / "runtime" / "dwm_shard_state"
SHARD_SIZE = 100
PY = sys.executable

sys.path.insert(0, str(REPO))
# src 前插：editable install 把 zephyr 钉在主区 src，worktree 运行必须显式抢优先级
_REPO_SRC = REPO / "src"
if str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))


def load_symbols(period: str, start: str) -> list[str]:
    from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider
    from zephyr.data.provider_base import FetchPayload
    from zephyr.data.table_registry import get_registry

    payload = FetchPayload(
        table=get_registry().table("market_technical_indicator"),
        symbols=None,
        start=datetime.date.fromisoformat(start),
        end=datetime.date.today(),
        incremental=False,
        extra={"period": period, "capability": "technical_indicator"},
    )
    provider = InternalComputeProvider()
    return sorted(provider._get_symbols(payload, period))


def shard_json(period: str, i: int) -> Path:
    return STATE_DIR / f"{period}_shard_{i:03d}.json"


def run_shard(period: str, i: int, symbols: list[str], start: str) -> dict:
    shard_file = STATE_DIR / f"{period}_symbols_shard_{i:03d}.txt"
    shard_file.write_text("\n".join(symbols) + "\n", encoding="utf-8")
    cmd = [
        PY, "-u", str(REPO / "scripts" / "data" / "backfill_technical_indicator_dwm.py"),
        "--periods", period,
        f"--start-{period}", start,
        "--symbols-file", str(shard_file),
    ]
    t0 = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=7200)  # noqa: bare-subprocess  分片内存隔离是本件核心设计（Code 241 治本）：每片独立子进程跑回填，父进程零大数据驻留；CLI 子进程场景 process_pool 不适用
    rec = {
        "period": period, "shard": i, "symbols": len(symbols),
        "exit": proc.returncode, "elapsed_sec": round(time.monotonic() - t0, 1),
        "finished_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "log_tail": (proc.stdout[-400:] + proc.stderr[-400:]),
    }
    shard_json(period, i).write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default="daily")
    ap.add_argument("--start-daily", default="2021-01-01")
    ap.add_argument("--start-weekly", default="2019-01-01")
    ap.add_argument("--start-monthly", default="2019-01-01")
    ap.add_argument("--shard-size", type=int, default=SHARD_SIZE)
    ap.add_argument("--only-shard", type=int, default=-1)
    args = ap.parse_args()

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    starts = {"daily": args.start_daily, "weekly": args.start_weekly, "monthly": args.start_monthly}
    rc = 0
    for period in [p.strip() for p in args.periods.split(",") if p.strip()]:
        symbols = load_symbols(period, starts[period])
        n_shards = (len(symbols) + args.shard_size - 1) // args.shard_size
        print(f"[{period}] symbols={len(symbols)} shards={n_shards}", flush=True)
        for i in range(n_shards):
            if args.only_shard >= 0 and i != args.only_shard:
                continue
            sj = shard_json(period, i)
            if sj.exists() and args.only_shard < 0:
                rec = json.loads(sj.read_text(encoding="utf-8"))
                if rec.get("exit") == 0:
                    print(f"[{period}] shard {i} 已完成（跳过）", flush=True)
                    continue
            chunk = symbols[i * args.shard_size:(i + 1) * args.shard_size]
            print(f"[{period}] shard {i + 1}/{n_shards} 开始（{len(chunk)} 标的）", flush=True)
            rec = run_shard(period, i, chunk, starts[period])
            print(f"[{period}] shard {i + 1}/{n_shards} exit={rec['exit']} {rec['elapsed_sec']}s", flush=True)
            if rec["exit"] != 0:
                rc = 1
                print(rec["log_tail"][-500:], flush=True)
    print("runner done rc=", rc, flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
