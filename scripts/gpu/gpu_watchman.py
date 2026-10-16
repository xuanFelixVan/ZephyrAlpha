# [BLUEPRINT] MOD-GPU-WATCHMAN | docs/03_modules/_domain_infrastructure_runtime/index.md
# [MODULE] scripts.gpu.gpu_watchman
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] stdlib(argparse;contextlib;csv;datetime;json;os;re;shlex;shutil;subprocess;sys;time;pathlib); zephyr.shared.infra.process_pool(run_subprocess_hidden 统一无窗口入口); zephyr.shared.io.paths(REPO_ROOT SSoT)
# [CONSUMERS] GPU 三档制（独占窗/机会档/禁入）调用方：训练/回测等批任务经 subprocess CLI
#   acquire/release/status 让路；调用方约定=退出码 7 即未获准，禁强占。
# [STARTUP] manual
# [MATURITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [INVARIANTS] 登记册 only-append JSONL 事件行 {ts,task,mode,event}（活跃集=每 task 最后事件为
#   acquire 的派生视图，禁就地改写/删除历史行）；detect() 不可知（nvidia-smi 缺失/超时/解析败）
#   =保守拒绝独占、放行机会档，禁把不可知当空闲独占；批准门柱=free_gb>=min_free_gb 且
#   util_pct<=max_util（缺省 8GB/10%）；任何阻塞→轮询等待至 wait_timeout，超时=退出码 7；
#   GPU_WATCHMAN_NVIDIA_SMI 指向假命令仅为测试/演练注入位，生产禁设。
# [MODIFY-GUARD] tests/gpu/test_gpu_watchman.py
# [STABILITY] experimental
# [ERROR_CONTRACT] 判读失败不抛：detect() 返回 None；acquire 超时=False（CLI 映射退出码 7）；
#   登记册坏行跳过不致命；登记册锁忙超时抛 TimeoutError（提示重试，不静默强写）。
# [TESTS] tests/gpu/test_gpu_watchman.py
# [A_module] module_id=MOD-GPU-WATCHMAN | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本件为按需运维 CLI 的让路等待轮询（acquire 阻塞等待与 wait 超时轮询），非常驻 cron/守护，事件订阅不适用（裁定#538 抢救入库时按 m10 逐件声明通道补登）
# noqa: m11-perm-manual-legitimate  M11豁免: 本件=人工/席位按需调用的 acquire/release/status 运维 CLI（GPU 三档制让路），非自动常驻服务（裁定#538 抢救入库时按 m11 逐件声明通道补登）
# [not-trading: GPU 调度让路基建（读数/登记/互斥），不在实盘交易决策路径上]
# create-guard-not-dup: 本模块=GPU 硬件让路看门人（nvidia-smi 读数+独占/机会档登记册 JSONL），命中词 'registry path'/'registry lock' 是 GPU 调度登记册与进程间文件锁的字面义，非 capability_lookup/架构生成器/密钥册一致性的第二实现。
"""GPU 机会档看门人——GPU 三档制（独占窗/机会档/禁入）的登记让路基建，替代裸占与一刀切独占。

读数：detect() 经 nvidia-smi 取 {free_gb, util_pct}；缺失/超时/解析败→None（不可知）。
登记：.runtime/gpu_registry/registry.jsonl 只追加事件行 {ts,task,mode,event}；
  活跃集=每 task 最后事件为 acquire 的派生视图，release 即追加 release 行抹除标记。
准入：exclusive 需登记册全空且 GPU 判读空闲（不可知=保守拒绝）；opportunistic 需登记册全空
  且 GPU 空闲或不可知（不可知=放行机会档）。阻塞→轮询等待至 wait_timeout，超时退出码 7。

CLI（供其他脚本 subprocess 调用）：
  python scripts/gpu/gpu_watchman.py acquire --task T [--exclusive]
      [--min-free-gb 8] [--max-util 10] [--wait-timeout 300]
  python scripts/gpu/gpu_watchman.py release --task T
  python scripts/gpu/gpu_watchman.py status
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden

_PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)  # bootstrap: scripts/gpu/ -> root（独立脚本零仓包假设时先自举 sys.path）
for _bootstrap_p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "src")):
    if _bootstrap_p not in sys.path:
        sys.path.insert(0, _bootstrap_p)

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSoT 唯一真源（禁本地重复定义，SSOT-REDEFINITION 处方）

DEFAULT_REGISTRY_PATH = REPO_ROOT / ".runtime" / "gpu_registry" / "registry.jsonl"
DEFAULT_MIN_FREE_GB = 8.0
DEFAULT_MAX_UTIL = 10.0
DEFAULT_WAIT_TIMEOUT = 300.0
POLL_INTERVAL = 5.0
SMI_TIMEOUT = 10.0
EXIT_TIMEOUT = 7
SMI_ARGS = ("--query-gpu=memory.used,memory.total,utilization.gpu", "--format=csv,noheader")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _smi_command() -> str | None:
    """解析 nvidia-smi 命令：环境变量注入位优先（测试/演练），缺省查 PATH。"""
    override = os.environ.get("GPU_WATCHMAN_NVIDIA_SMI", "").strip()
    if override:
        return override
    return shutil.which("nvidia-smi")


def _to_float(raw: str) -> float:
    """nvidia-smi 单元格→float；容忍单位后缀（'1234 MiB'/'39 %'），[N/A]/[Not Supported] 等不可判读值抛 ValueError。

    真机输出默认带单位（--format=csv,noheader 不加 nounits），旧实现 float('3348 MiB')
    恒 ValueError → detect() 恒 None → status 恒 unknown（st-ibtclose-20261015 件4 回归修复）。
    """
    match = re.match(r"^\[?\s*([+-]?\d+(?:\.\d+)?)", raw.strip())
    if match is None:
        raise ValueError(f"nvidia-smi cell unreadable: {raw!r}")
    return float(match.group(1))


def parse_smi_output(text: str) -> dict:
    """解析 `nvidia-smi --format=csv,noheader` 输出→{free_gb, util_pct}（取首卡）。

    行格式：`used_mib, total_mib, util_pct`；坏行/不可判读→ValueError（调用方转 None）。
    """
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 3:
            raise ValueError(f"unexpected nvidia-smi row: {line!r}")
        used_mib = _to_float(parts[0])
        total_mib = _to_float(parts[1])
        util_pct = _to_float(parts[2])
        return {
            "free_gb": round((total_mib - used_mib) / 1024.0, 3),
            "util_pct": round(util_pct, 3),
        }
    raise ValueError("empty nvidia-smi output")


def detect() -> dict | None:
    """GPU 读数→{free_gb, util_pct}；nvidia-smi 缺失/超时/非零退出/解析败→None（不可知）。"""
    command = _smi_command()
    if not command:
        return None
    try:
        proc = run_subprocess_hidden(
            [command, *SMI_ARGS],
            capture_output=True,
            text=True,
            timeout=SMI_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        return parse_smi_output(proc.stdout)
    except ValueError:
        return None


def _registry_path(registry_path: str | Path | None = None) -> Path:
    if registry_path is not None:
        return Path(registry_path)
    env = os.environ.get("GPU_WATCHMAN_REGISTRY", "").strip()
    if env:
        return Path(env)
    return DEFAULT_REGISTRY_PATH


@contextlib.contextmanager
def _registry_lock(lock_path: Path, timeout: float = 10.0, stale_age: float = 60.0):
    """登记册临界区互斥（O_EXCL 锁文件；陈旧锁抢占），防并发双批准。"""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout
    fd = None
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                if time.time() - lock_path.stat().st_mtime > stale_age:
                    lock_path.unlink()
                    continue
            except FileNotFoundError:
                pass
            if time.monotonic() >= deadline:
                raise TimeoutError(f"gpu registry lock busy: {lock_path}") from None
            time.sleep(0.05)
    try:
        yield
    finally:
        if fd is not None:
            os.close(fd)
        with contextlib.suppress(FileNotFoundError):
            lock_path.unlink()


def _append_event_unlocked(path: Path, task: str, mode: str, event: str) -> None:
    """写事件行（调用方须已持 _registry_lock，禁嵌套取锁）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(
        {"ts": _utc_now_iso(), "task": task, "mode": mode, "event": event},
        ensure_ascii=False,
    )
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def append_event(task: str, mode: str, event: str, registry_path: str | Path | None = None) -> None:
    """追加事件行 {ts,task,mode,event}（only-append，禁改写历史行）。"""
    path = _registry_path(registry_path)
    with _registry_lock(path.with_suffix(".lock")):
        _append_event_unlocked(path, task, mode, event)


def read_active(registry_path: str | Path | None = None) -> dict[str, dict]:
    """活跃集=每 task 最后事件为 acquire 的派生视图；坏行跳过。"""
    path = _registry_path(registry_path)
    active: dict[str, dict] = {}
    if not path.exists():
        return active
    with path.open("r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            task = str(row.get("task", ""))
            if not task:
                continue
            if row.get("event") == "acquire":
                active[task] = {"mode": str(row.get("mode", "")), "ts": str(row.get("ts", ""))}
            else:
                active.pop(task, None)
    return active


def acquire(
    task: str,
    exclusive: bool = False,
    min_free_gb: float = DEFAULT_MIN_FREE_GB,
    max_util: float = DEFAULT_MAX_UTIL,
    wait_timeout: float = DEFAULT_WAIT_TIMEOUT,
    registry_path: str | Path | None = None,
    poll_interval: float | None = None,
    detect_fn=None,
) -> bool:
    """申请 GPU：批准=True（登记 acquire 事件）；等待超时=False（调用方退出码 7）。

    - exclusive：登记册全空且 GPU 判读空闲才批准；不可知=保守拒绝。
    - opportunistic：登记册全空且 GPU 空闲或不可知即批准（不可知=放行机会档）。
    - detect_fn/registry_path/poll_interval 为注入位（测试零真 GPU）。
    """
    path = _registry_path(registry_path)
    probe = detect_fn if detect_fn is not None else detect
    poll = POLL_INTERVAL if poll_interval is None else poll_interval
    deadline = time.monotonic() + max(wait_timeout, 0.0)
    mode = "exclusive" if exclusive else "opportunistic"
    while True:
        active = read_active(path)
        if task in active:
            return True  # 幂等：已持
        reading = probe()
        if active:
            blocked = True  # 登记册有任何活跃任务→让路（独占与机会档同规）
        elif exclusive:
            blocked = (
                reading is None or reading["free_gb"] < min_free_gb or reading["util_pct"] > max_util
            )  # 不可知=保守拒绝独占
        else:
            blocked = reading is not None and (
                reading["free_gb"] < min_free_gb or reading["util_pct"] > max_util
            )  # 不可知=放行机会档
        if not blocked:
            with _registry_lock(path.with_suffix(".lock")):
                if task in read_active(path):  # 锁内复核，防并发双批准
                    return True
                _append_event_unlocked(path, task, mode, "acquire")
            return True
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        time.sleep(min(poll, remaining))


def release(task: str, registry_path: str | Path | None = None) -> None:
    """释放活跃标记（追加 release 事件；未持有时幂等无副作用）。"""
    active = read_active(registry_path)
    mode = active.get(task, {}).get("mode", "")
    append_event(task, mode, "release", registry_path)


def status(registry_path: str | Path | None = None) -> str:
    """当前活跃任务 + GPU 读数（不可知显式标 unknown，禁冒充空闲）。"""
    active = read_active(registry_path)
    lines = [
        f"active: task={task} mode={info['mode']} since={info['ts']}" for task, info in sorted(active.items())
    ] or ["active: (none)"]
    reading = detect()
    if reading is None:
        lines.append("gpu: unknown (nvidia-smi unavailable or unreadable)")
    else:
        lines.append(f"gpu: free_gb={reading['free_gb']} util_pct={reading['util_pct']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gpu_watchman",
        description="GPU 机会档看门人（独占窗/机会档登记让路；未获准=退出码 7）",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_acquire = subparsers.add_parser("acquire", help="申请 GPU（超时退出码 7）")
    p_acquire.add_argument("--task", required=True, help="任务标识（登记册主键）")
    p_acquire.add_argument("--exclusive", action="store_true", help="独占窗（默认机会档）")
    p_acquire.add_argument("--min-free-gb", type=float, default=DEFAULT_MIN_FREE_GB)
    p_acquire.add_argument("--max-util", type=float, default=DEFAULT_MAX_UTIL)
    p_acquire.add_argument("--wait-timeout", type=float, default=DEFAULT_WAIT_TIMEOUT)

    p_release = subparsers.add_parser("release", help="释放任务活跃标记")
    p_release.add_argument("--task", required=True)

    subparsers.add_parser("status", help="打印当前活跃任务与 GPU 读数")

    args = parser.parse_args(argv)
    if args.command == "acquire":
        approved = acquire(
            args.task,
            exclusive=args.exclusive,
            min_free_gb=args.min_free_gb,
            max_util=args.max_util,
            wait_timeout=args.wait_timeout,
        )
        if not approved:
            print(
                f"[gpu-watchman] acquire timeout: task={args.task} "
                f"mode={'exclusive' if args.exclusive else 'opportunistic'}",
                file=sys.stderr,
            )
            return EXIT_TIMEOUT
        print(f"[gpu-watchman] acquired: task={args.task} mode={'exclusive' if args.exclusive else 'opportunistic'}")
        return 0
    if args.command == "release":
        release(args.task)
        print(f"[gpu-watchman] released: task={args.task}")
        return 0
    print(status())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
