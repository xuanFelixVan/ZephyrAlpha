# [BLUEPRINT] MOD-INF-005 | scripts/governance/d10_performance/collect_system_threads.py | §
# [MODULE] scripts.governance.d10_performance.collect_system_threads
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d10_performance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
collect_system_threads.py — 全系统线程数快照采集器


独立于 ResourceOptimizationEngine.snapshot() 的轻量级线程指标采集脚本。
线程采集通过 process_iter 遍历全系统进程，在 Windows 上耗时 1~3 秒，
因此从引擎热路径中剥离，改为按需独立执行。

Usage:
    python scripts/governance/d10_performance/collect_system_threads.py
    python scripts/governance/d10_performance/collect_system_threads.py --top 10
    python scripts/governance/d10_performance/collect_system_threads.py --json --output threads.json
    python scripts/governance/run_all.py --dimensions D10 --tags Resource

Output:
    JSON 格式：{total_threads, per_process: [{pid, name, num_threads}, ...]}
    按 num_threads 降序排列，方便定位线程泄漏进程。
"""

from __future__ import annotations

__manifest__ = """
args:
- flag: --top
  type: int
  description: 仅输出线程数最高的前 N 个进程
- flag: --json
  type: bool
  description: JSON 输出格式
- flag: --output
  type: str
  description: 输出文件路径（默认 stdout）
description: >
  全系统线程数快照采集——遍历所有进程统计线程数，
  输出总量 + 按进程降序排列的 Top-N 线程占用。
dimensions:
- D10
priority: P2
timeout_seconds: 30
warn_only: true
tags:
- Resource
- Periodic
"""

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()


EXIT_PASS = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2


@dataclass
class ThreadSnapshot:
    timestamp: float = field(default_factory=time.time)
    total_threads: int = 0
    total_processes: int = 0
    per_process: list[dict] = field(default_factory=list)


def collect_threads(top: int | None = None) -> ThreadSnapshot:
    """collect_threads implementation."""
    try:
        import psutil
    except ImportError:
        print("ERROR: psutil not installed — thread collection unavailable", file=sys.stderr)
        return ThreadSnapshot()

    processes = []
    total = 0
    try:
        for p in psutil.process_iter(["pid", "name", "num_threads"]):
            try:
                info = p.info
                nt = info.get("num_threads") or 0
                total += nt
                processes.append(
                    {
                        "pid": info.get("pid", 0),
                        "name": info.get("name", "?"),
                        "num_threads": nt,
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass

    processes.sort(key=lambda x: x["num_threads"], reverse=True)
    if top is not None and top > 0:
        processes = processes[:top]

    return ThreadSnapshot(
        timestamp=time.time(),
        total_threads=total,
        total_processes=len(processes),
        per_process=processes,
    )


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="全系统线程数快照采集器（D10 性能维度）")
    parser.add_argument("--top", type=int, default=None, help="仅输出 Top-N 线程占用进程")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--output", type=str, default=None, help="输出文件路径")
    args = parser.parse_args()

    snap = collect_threads(top=args.top)

    output: dict = {
        "timestamp": snap.timestamp,
        "total_threads": snap.total_threads,
        "total_processes": snap.total_processes,
        "per_process": snap.per_process,
    }

    if args.json:
        text = json.dumps(output, indent=2, ensure_ascii=False)
    else:
        lines = [
            f"total_threads={snap.total_threads}",
            f"total_processes={snap.total_processes}",
            f"timestamp={snap.timestamp}",
            "--- per_process (top threads) ---",
        ]
        for entry in snap.per_process:
            lines.append(f"  pid={entry['pid']:>6d}  threads={entry['num_threads']:>4d}  name={entry['name']}")
        text = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"output written to {args.output}")
    else:
        print(text)

    return EXIT_PASS


if __name__ == "__main__":
    sys.exit(main())
