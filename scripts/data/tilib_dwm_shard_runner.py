# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] scripts.data.tilib_dwm_shard_runner
# noqa: m11-perm-manual-legitimate  tilib_indicator_backfill_nightly 计划任务 02:30 经 backfill_night.ps1 自动触发（永久自动化正门），兼 Owner/施工会话手动续跑运维件，人工触发是设计意图非缺陷
# [DOMAIN] D_DATA
# [DEPENDENCIES] scripts.data.backfill_technical_indicator_dwm; zephyr.data.scheduler.acquire_single_instance_lock
# [CONSUMERS] tilib_indicator_backfill_nightly 计划任务（backfill_night.bat）；Owner/施工会话手动触发
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 单实例互斥（P3）：入口取一把 OS 级文件锁（锁文件与 state 同目录，句柄随进程生死），
#  已被活体持有即退出并打 TILIB_LOCK_HELD_BY_OTHER_INSTANCE 标记行——计划任务与手动续跑不再并行/接力；
#  每片独立子进程跑 backfill_technical_indicator_dwm.py --symbols-file <片清单>（进程级内存隔离），
#  片内再按自然年切窗（P4），每窗自带超时；窗跑完即增量写 state（崩了也看得见），
#  重跑跳过**当日**且 exit=0 片（2026-10-09 实测：该表引擎无版本列，未合并期同键多版并存且非 FINAL
#  读返回哪版由行序决定，所以"同键覆盖、重叠无害"不成立——重叠＝行数按趟数涨＋读数不确定；
#  故跳过判据加当日戳）；超时窗必须写 exit="timeout" 的 state 而非静默无 state（R3 治本：
#  2026-10-09 实测 shard_024 死于 7200s 超时且无 state ⇒ 该片每晚重头再来、结构性补不上）；
#  失败窗记录 error 后整片判失败并继续下一片。
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单片 exit!=0 不中断（隔毒片），全部跑完汇总 rc=1；窗超时 exit="timeout"（非零，当日必重算）；
#  取不到单实例锁 ⇒ 打印标记行后 rc=0 退出（让路是正确行为，不是故障，但必须留痕）
# [TESTS] 本 CLI 以 --help 自测；跳过判据与当日戳由 tests/data/data/data/test_tilib_dwm_shard_state_stamp.py 钉（8 例，含四条红证）；单实例锁/年切窗/超时留痕由 tests/data/data/data/test_ti_backfill_value_skip_and_shard_windows.py 钉
# [TTL] permanent
"""tilib 夜跑 dwm 指标回填分片编排器（2026-09-22 tracked 化，裁定#399）。

背景（Code 241 内存总闸阵亡治本，原 .runtime/tmp 临时版 st-data-fix-20260921）：
- 每片 = 独立子进程跑 backfill_technical_indicator_dwm.py --symbols-file <片清单>
  → 进程级内存隔离，单片阵亡不污染主进程，崩了续跑下一片。
- 每片完成写 data/runtime/dwm_shard_state/<period>_shard_<i>.json
  → 重跑跳过**当日**已完成片（shard_already_done）；隔到次日整片重算，同一晚重启零重插。
    旧写法"跳过任何 exit=0 片"配得上"每晚抹掉 state 目录"才不断更——那对组合正是
    全史每晚重灌的成因（2026-10-10 P2 治本，ps1 与判据同批改）。
- 失败片记录 error 后继续下一片（隔离毒片），全部跑完后汇总 exit 非零。

2026-10-10 P3/P4 追加（dexp 战役 §10 R2/R3 归因的处方，数据车道施工）：
- P3 单实例互斥：入口一把 OS 级文件锁，活体持有即让路。此前计划任务与手动续跑可以
  并行/接力（10-08 21:32 与 10-09 02:30 两趟叠加即为实证）。
- P4 片内按年切窗 + 超时必留态：7200s 对"100 标的 × 5.6 年"不够，而旧写法超时即抛、
  一支笔都不落 state ⇒ 该片每晚从头再来。切窗后每窗跑完就增量落盘，超时窗写
  exit="timeout"，续跑只补没跑完的窗。

用法：
    python scripts/data/tilib_dwm_shard_runner.py --periods daily            # 默认 100 标的/片
    python scripts/data/tilib_dwm_shard_runner.py --periods daily --only-shard 3   # 单片重跑
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STATE_DIR = REPO / "data" / "runtime" / "dwm_shard_state"
SHARD_SIZE = 100
# 超时异常类锚在模块导入期：测试替身只该换 subprocess.run，不该顺手把异常类一起换掉
# （写成 except subprocess.TimeoutExpired 时，替身没有该属性会炸成 AttributeError＝假阴）。
_TimeoutExpired = subprocess.TimeoutExpired
# 单个年窗超时（P4）：实测一片 100 标的跑 5.6 年需 1259.6s ⇒ 单年窗≈225s，给 8 倍余量。
# 旧值是"整片 7200s"一刀切，100 标的 × 5.6 年撑不住且超时即静默无 state（shard_024 实证）。
WINDOW_TIMEOUT_SEC = 1800
# 单实例锁文件名（P3），与片态同目录＝--state-dir 指哪就锁哪，测试天然不碰生产目录
INSTANCE_LOCK_NAME = "tilib_dwm_runner_instance.lock"
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


def shard_already_done(rec: dict, today: datetime.date | None = None) -> bool:
    """跳过判据：**当日**完成且 exit=0 才算已完成（2026-10-09 批复 P2）。

    旧判据只看 exit==0，于是入口脚本 `backfill_night.ps1` 每晚先删整个 state 目录
    来"让它重来"——那才是每晚全史重灌（实测单趟插入 11,227,985 行）的成因。
    加了当日戳之后：同一晚二次启动（手动续跑/看门狗重启）已完成片零重灌，
    跨到次日则整片重算，日频新鲜度不被牺牲。
    """
    if rec.get("exit") != 0:
        return False
    return str(rec.get("finished_at", ""))[:10] == (today or datetime.date.today()).isoformat()


def year_windows(start: str, end: str) -> list[tuple[str, str]]:
    """把 [start, end] 按自然年切成窗（P4：片内再分年）。

    单片 7200s 撑不住"100 标的 × 5.6 年"（2026-10-09 实测 shard_024 死于 TimeoutExpired），
    而旧写法一超时整个 run_shard 抛出、state 一支不落 ⇒ 该片每晚从头再来。切成自然年后
    每窗自带超时与增量留痕，续跑只补没跑完的窗。首尾窗截到 start/end，不越界。
    """
    first = datetime.date.fromisoformat(start)
    last = datetime.date.fromisoformat(end)
    if last < first:
        raise ValueError(f"end {end} 早于 start {start}")
    out: list[tuple[str, str]] = []
    for year in range(first.year, last.year + 1):
        w0 = max(first, datetime.date(year, 1, 1))
        w1 = min(last, datetime.date(year, 12, 31))
        if w0 <= w1:
            out.append((w0.isoformat(), w1.isoformat()))
    return out


def symbols_fingerprint(symbols: list[str]) -> str:
    """本片标的集合指纹——续跑只在"同一批标的"之间接续，换了清单不得复用旧窗进度。"""
    blob = "\n".join(sorted(symbols)).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def resumable_windows(
    rec: dict, fp: str, start: str, end: str, today: datetime.date | None = None
) -> list[tuple[str, str]]:
    """旧 state 里哪些窗可以接着用（当日 + 同标的指纹 + 同起止日，三样缺一即整片重算）。

    跨到次日一律作废＝P2 当日戳语义的延续（日频新鲜度优先于省算力）。
    """
    stamp = str(rec.get("finished_at", ""))[:10]
    if stamp != (today or datetime.date.today()).isoformat():
        return []
    if rec.get("symbols_sha256") != fp or rec.get("start_daily") != start or rec.get("end") != end:
        return []
    out: list[tuple[str, str]] = []
    for item in rec.get("done_windows") or []:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            out.append((str(item[0]), str(item[1])))
    return out


def parse_value_skip_marker(stdout_text: str) -> dict | None:
    """从子进程 stdout 里捞回填器打的值级跳过标记行（P1 可观测腿，进片态）。

    捞不到就返回 None——"这一趟到底跳没跳"必须是看得见的字段，不能靠推断。
    """
    marker = "TI_VALUE_SKIP "
    hits = [ln for ln in (stdout_text or "").splitlines() if marker in ln]
    if not hits:
        return None
    payload = hits[-1].split(marker, 1)[1].strip()
    try:
        return json.loads(payload)
    except ValueError:
        return {"unparsed": payload[:200]}


def _timeout_streams(exc: subprocess.TimeoutExpired) -> tuple[str, str]:
    """TimeoutExpired 携带的 stdout/stderr 可能是 bytes 也可能是 str（取决于 text=），统一成 str。"""
    out = b"" if exc.stdout is None else exc.stdout
    err = b"" if exc.stderr is None else exc.stderr
    if isinstance(out, bytes):
        out = out.decode("utf-8", "replace")
    if isinstance(err, bytes):
        err = err.decode("utf-8", "replace")
    return str(out), str(err)


def write_shard_state(period: str, i: int, rec: dict) -> None:
    shard_json(period, i).write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")


def run_shard(
    period: str,
    i: int,
    symbols: list[str],
    start: str,
    end: str | None = None,
    *,
    window_timeout: int = 1800,
    resume: list[tuple[str, str]] | None = None,
) -> dict:
    """跑一片＝按年窗逐个起子进程，每窗跑完就增量落 state；超时窗落 exit="timeout"。

    返回最后一次的片态 dict（含 exit/finished_at/done_windows/value_skip/timed_out_window）。
    exit=0 只在"全部窗都跑完且零退出码"时出现；任一窗非零（含 "timeout"）即整片判失败，
    下一片照跑（隔毒片语义与 P2 前一致）。
    """
    shard_file = STATE_DIR / f"{period}_symbols_shard_{i:03d}.txt"
    shard_file.write_text("\n".join(symbols) + "\n", encoding="utf-8")
    end = end or datetime.date.today().isoformat()
    windows = year_windows(start, end)
    done: set[tuple[str, str]] = set(resume or [])

    rec: dict = {
        "period": period,
        "shard": i,
        "symbols": len(symbols),
        "symbols_sha256": symbols_fingerprint(symbols),
        "start_daily": start,
        "end": end,
        "windows": [list(w) for w in windows],
        "done_windows": [list(w) for w in sorted(done)],
        "window_timeout_sec": window_timeout,
        "exit": "running",
        "elapsed_sec": 0.0,
        "finished_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "log_tail": "",
        "value_skip": None,
        "timed_out_window": None,
    }
    # 先落"在跑"态：片被强杀/断电也留得下痕迹，不再出现"跑过但查无此片"的第四态
    write_shard_state(period, i, rec)

    t_all = time.monotonic()
    for w0, w1 in windows:
        if (w0, w1) in done:
            print(f"[{period}] shard {i} 窗 {w0}~{w1} 当日已完成（续跑跳过）", flush=True)
            continue
        cmd = [
            PY,
            "-u",
            str(REPO / "scripts" / "data" / "backfill_technical_indicator_dwm.py"),
            "--periods",
            period,
            f"--start-{period}",
            w0,
            "--end",
            w1,
            "--symbols-file",
            str(shard_file),
        ]
        timed_out = False
        try:
            proc = subprocess.run(  # noqa: bare-subprocess  分片/分窗内存隔离是本件核心设计（Code 241 治本）：每窗独立子进程跑回填，父进程零大数据驻留；CLI 子进程场景 process_pool 不适用
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=window_timeout,
            )
            code: object = proc.returncode
            out, err = proc.stdout or "", proc.stderr or ""
        except _TimeoutExpired as exc:
            timed_out = True
            code = "timeout"
            out, err = _timeout_streams(exc)
        rec["exit"] = code
        rec["elapsed_sec"] = round(time.monotonic() - t_all, 1)
        rec["finished_at"] = datetime.datetime.now().isoformat(timespec="seconds")
        rec["log_tail"] = out[-200:] + err[-200:]
        marker = parse_value_skip_marker(out)
        if marker is not None:
            rec["value_skip"] = marker
        if timed_out:
            rec["timed_out_window"] = [w0, w1]
            write_shard_state(period, i, rec)
            return rec
        if code != 0:
            write_shard_state(period, i, rec)
            return rec
        done.add((w0, w1))
        rec["done_windows"] = [list(w) for w in sorted(done)]
        write_shard_state(period, i, rec)

    rec["exit"] = 0
    rec["elapsed_sec"] = round(time.monotonic() - t_all, 1)
    rec["finished_at"] = datetime.datetime.now().isoformat(timespec="seconds")
    write_shard_state(period, i, rec)
    return rec


def acquire_instance_lock():
    """P3 单实例互斥：取一把 OS 级文件锁，锁文件与片态同目录。

    复用 `zephyr.data.scheduler.acquire_single_instance_lock`（msvcrt.locking / fcntl.flock
    字节排他锁，句柄随进程生死 ⇒ 崩溃或被强杀都不留 stale 锁），不另造第二把判据。
    懒导入：`--help` 不必把调度器整条依赖链拖起来。

    Returns:
        持有锁的文件对象（调用方须让它在进程内活下去）；None＝已被别的活体持有。
    """
    from zephyr.data.scheduler import acquire_single_instance_lock

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    return acquire_single_instance_lock(STATE_DIR / INSTANCE_LOCK_NAME)


def main() -> int:
    global STATE_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default="daily")
    ap.add_argument("--start-daily", default="2021-01-01")
    ap.add_argument("--start-weekly", default="2019-01-01")
    ap.add_argument("--start-monthly", default="2019-01-01")
    ap.add_argument("--shard-size", type=int, default=SHARD_SIZE)
    ap.add_argument("--only-shard", type=int, default=-1)
    ap.add_argument("--end", default=None, help="回填右界（含日），缺省=今天；决定年窗切法")
    ap.add_argument(
        "--window-timeout",
        type=int,
        default=WINDOW_TIMEOUT_SEC,
        help=f"单个年窗超时秒（缺省 {WINDOW_TIMEOUT_SEC}）；超时窗写 exit=timeout 的 state",
    )
    ap.add_argument(
        "--state-dir", default=None, help="片完成态目录（测试可指 tmp_path，禁写生产 data/）；缺省=真源目录"
    )
    args = ap.parse_args()

    if args.state_dir:
        STATE_DIR = Path(args.state_dir)
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    lock_handle = acquire_instance_lock()
    if lock_handle is None:
        print(
            "TILIB_LOCK_HELD_BY_OTHER_INSTANCE 已有活体编排器持锁 ⇒ 本次让路退出"
            "（P3 单实例互斥：计划任务与手动续跑不再并行/接力）",
            flush=True,
        )
        return 0

    starts = {"daily": args.start_daily, "weekly": args.start_weekly, "monthly": args.start_monthly}
    end = args.end or datetime.date.today().isoformat()
    rc = 0
    for period in [p.strip() for p in args.periods.split(",") if p.strip()]:
        symbols = load_symbols(period, starts[period])
        n_shards = (len(symbols) + args.shard_size - 1) // args.shard_size
        print(f"[{period}] symbols={len(symbols)} shards={n_shards}", flush=True)
        for i in range(n_shards):
            if args.only_shard >= 0 and i != args.only_shard:
                continue
            chunk = symbols[i * args.shard_size : (i + 1) * args.shard_size]
            fp = symbols_fingerprint(chunk)
            sj = shard_json(period, i)
            resume: list[tuple[str, str]] = []
            if sj.exists():
                rec = json.loads(sj.read_text(encoding="utf-8"))
                if shard_already_done(rec) and args.only_shard < 0:
                    print(f"[{period}] shard {i} 当日已完成（跳过）", flush=True)
                    continue
                if args.only_shard < 0:
                    print(f"[{period}] shard {i} state 非当日或 exit!=0 ⇒ 重算", flush=True)
                resume = resumable_windows(rec, fp, starts[period], end)
                if resume:
                    print(
                        f"[{period}] shard {i} 续跑：复用当日已完成的 {len(resume)} 个年窗",
                        flush=True,
                    )
            print(
                f"[{period}] shard {i + 1}/{n_shards} 开始（{len(chunk)} 标的"
                f"，{len(year_windows(starts[period], end)) - len(resume)} 窗待跑）",
                flush=True,
            )
            rec = run_shard(
                period,
                i,
                chunk,
                starts[period],
                end,
                window_timeout=args.window_timeout,
                resume=resume,
            )
            print(f"[{period}] shard {i + 1}/{n_shards} exit={rec['exit']} {rec['elapsed_sec']}s", flush=True)
            if rec["exit"] != 0:
                rc = 1
                print(rec["log_tail"][-500:], flush=True)
    print("runner done rc=", rc, flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
