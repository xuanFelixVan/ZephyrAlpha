# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md
# [MODULE] scripts.run_boot_sla_probe
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib; zephyr.shared.infra.process_pool (run_subprocess_hidden)
# [CONSUMERS] 18号 SLA 验收（2.8 boot watchdog 冷启动 P99<10s 实测留痕）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 纯只读探针：不修改任何文件（除 .runtime/ 下报告文件），无副作用；boot 次数可配置
# [MODIFY-GUARD] 18_gp0_construction_order.md §6 波 3-04
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 探针自身异常 -> exit 1；boot 超时单次记录不中断整体
# [TESTS] 无（一次性探针脚本）
# [A_module] module_id=MOD-INF-005 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
# run_boot_sla_probe.py - Boot SLA 连跑实测探针（GAP-010 / D-INF035-09 P99<10s）
#
# Purpose: 循环执行 N 次 `python start_brain.py --once`，收集每次 boot 耗时，
#          计算 P50/P95/P99 百分位数，判定是否达标（P99 < 10s），产出 JSONL 留痕报告。
#
# Data flow:
#   1. subprocess 执行 start_brain.py --once（每次收集 stdout/stderr + 总耗时）
#   2. 从 stdout grep "[BOOT_SLA]" 行提取 boot_ms
#   3. 统计 P50/P95/P99
#   4. 判定 P99 < 10000ms 是否达标
#   5. 报告落盘 .runtime/boot_sla_probe_report.jsonl
#
# Safety: 只读操作，不修改任何文件（除 .runtime/ 下报告文件），无副作用。

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final

from zephyr.shared.infra.process_pool import run_subprocess_hidden

from zephyr.shared.io.paths import REPO_ROOT as _ZEPHYR_REPO_ROOT
from zephyr.shared.io.paths import REPO_ROOT

RUNTIME_DIR: Final[Path] = _ZEPHYR_REPO_ROOT / ".runtime"
REPORT_PATH: Final[Path] = RUNTIME_DIR / "boot_sla_probe_report.jsonl"

BOOT_SLA_PATTERN: Final[re.Pattern[str]] = re.compile(r"\[BOOT_SLA\]\s+boot_ms=(\d+)\s+sla_ms=(\d+)\s+status=(\w+)")
SLA_TARGET_MS: Final[float] = 10_000.0
DEFAULT_ITERATIONS: Final[int] = 20


@dataclass(frozen=True)
class BootRunResult:
    """单次 boot 执行结果。"""

    iteration: int
    boot_ms: float
    sla_ms: float
    status: str
    exit_code: int
    stdout_tail: str
    stderr_tail: str
    total_elapsed_ms: float
    timestamp: str


@dataclass(frozen=True)
class BootSLAProbeReport:
    """SLA 连跑报告。"""

    total_runs: int
    successful_runs: int
    failed_runs: int
    boot_ms_list: list[float]
    p50_ms: float
    p95_ms: float
    p99_ms: float
    mean_ms: float
    min_ms: float
    max_ms: float
    sla_target_ms: float
    sla_met: bool
    report_ts: str
    runs: list[BootRunResult]


def _percentile(sorted_list: list[float], p: float) -> float:
    """计算百分位数（线性插值法）。

    Args:
        sorted_list: 已排序的数值列表
        p: 百分位 (0.0 ~ 1.0)

    Returns:
        百分位数值
    """
    if not sorted_list:
        return 0.0
    if len(sorted_list) == 1:
        return sorted_list[0]

    k = (len(sorted_list) - 1) * p
    f = int(k)
    c = k - f

    if f + 1 < len(sorted_list):
        return sorted_list[f] + c * (sorted_list[f + 1] - sorted_list[f])
    return sorted_list[f]


def _run_single_boot(iteration: int) -> BootRunResult:
    """执行单次 boot 并收集结果。

    Args:
        iteration: 迭代序号（从 1 开始）

    Returns:
        BootRunResult 实例
    """
    start_brain = REPO_ROOT / "scripts" / "construction" / "start_brain.py"
    cmd = [sys.executable, str(start_brain), "--once"]

    ts = datetime.now().isoformat()
    start = time.perf_counter()

    try:
        proc = run_subprocess_hidden(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=REPO_ROOT,
            timeout=60,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        exit_code = proc.returncode

        # 提取 [BOOT_SLA] 行
        boot_ms = 0.0
        sla_ms = SLA_TARGET_MS
        status = "UNKNOWN"

        for line in stdout.splitlines():
            match = BOOT_SLA_PATTERN.search(line)
            if match:
                boot_ms = float(match.group(1))
                sla_ms = float(match.group(2))
                status = match.group(3)
                break

        # 截取尾部用于留痕（最后 200 字符）
        stdout_tail = stdout[-200:] if stdout else ""
        stderr_tail = stderr[-200:] if stderr else ""

        return BootRunResult(
            iteration=iteration,
            boot_ms=boot_ms,
            sla_ms=sla_ms,
            status=status,
            exit_code=exit_code,
            stdout_tail=stdout_tail,
            stderr_tail=stderr_tail,
            total_elapsed_ms=round(elapsed_ms, 2),
            timestamp=ts,
        )

    except subprocess.TimeoutExpired:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return BootRunResult(
            iteration=iteration,
            boot_ms=0.0,
            sla_ms=SLA_TARGET_MS,
            status="TIMEOUT",
            exit_code=-1,
            stdout_tail="",
            stderr_tail="subprocess timeout after 60s",
            total_elapsed_ms=round(elapsed_ms, 2),
            timestamp=ts,
        )
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return BootRunResult(
            iteration=iteration,
            boot_ms=0.0,
            sla_ms=SLA_TARGET_MS,
            status="ERROR",
            exit_code=-2,
            stdout_tail="",
            stderr_tail=f"exception: {exc}",
            total_elapsed_ms=round(elapsed_ms, 2),
            timestamp=ts,
        )


def _run_probe(iterations: int) -> BootSLAProbeReport:
    """执行 N 次 boot 连跑并统计。

    Args:
        iterations: 执行次数

    Returns:
        BootSLAProbeReport 实例
    """
    runs: list[BootRunResult] = []
    boot_ms_list: list[float] = []

    print(f"[PROBE] 开始 {iterations} 次 boot 连跑...")
    print(f"[PROBE] SLA 目标: P99 < {SLA_TARGET_MS:.0f}ms ({SLA_TARGET_MS / 1000:.0f}s)")
    print()

    for i in range(1, iterations + 1):
        print(f"[PROBE] 第 {i}/{iterations} 次...", end=" ", flush=True)
        result = _run_single_boot(i)
        runs.append(result)

        if result.exit_code == 0 and result.boot_ms > 0:
            boot_ms_list.append(result.boot_ms)
            print(f"boot={result.boot_ms:.0f}ms status={result.status}")
        else:
            print(f"FAIL exit={result.exit_code} err={result.stderr_tail[:50]}")

    successful = sum(1 for r in runs if r.exit_code == 0 and r.boot_ms > 0)
    failed = iterations - successful

    sorted_ms = sorted(boot_ms_list)
    p50 = _percentile(sorted_ms, 0.50)
    p95 = _percentile(sorted_ms, 0.95)
    p99 = _percentile(sorted_ms, 0.99)
    mean = sum(sorted_ms) / len(sorted_ms) if sorted_ms else 0.0
    min_ms = min(sorted_ms) if sorted_ms else 0.0
    max_ms = max(sorted_ms) if sorted_ms else 0.0

    sla_met = p99 < SLA_TARGET_MS

    report = BootSLAProbeReport(
        total_runs=iterations,
        successful_runs=successful,
        failed_runs=failed,
        boot_ms_list=sorted_ms,
        p50_ms=round(p50, 2),
        p95_ms=round(p95, 2),
        p99_ms=round(p99, 2),
        mean_ms=round(mean, 2),
        min_ms=round(min_ms, 2),
        max_ms=round(max_ms, 2),
        sla_target_ms=SLA_TARGET_MS,
        sla_met=sla_met,
        report_ts=datetime.now().isoformat(),
        runs=runs,
    )

    return report


def _save_report_jsonl(report: BootSLAProbeReport, path: Path) -> None:
    """将报告以 JSONL 格式追加写入。

    Args:
        report: BootSLAProbeReport 实例
        path: 输出路径
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # 单条 JSON（整个报告作为一行）
    blob = {
        "report_ts": report.report_ts,
        "total_runs": report.total_runs,
        "successful_runs": report.successful_runs,
        "failed_runs": report.failed_runs,
        "p50_ms": report.p50_ms,
        "p95_ms": report.p95_ms,
        "p99_ms": report.p99_ms,
        "mean_ms": report.mean_ms,
        "min_ms": report.min_ms,
        "max_ms": report.max_ms,
        "sla_target_ms": report.sla_target_ms,
        "sla_met": report.sla_met,
        "boot_ms_list": report.boot_ms_list,
        "runs": [
            {
                "iteration": r.iteration,
                "boot_ms": r.boot_ms,
                "sla_ms": r.sla_ms,
                "status": r.status,
                "exit_code": r.exit_code,
                "total_elapsed_ms": r.total_elapsed_ms,
                "timestamp": r.timestamp,
            }
            for r in report.runs
        ],
    }

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(blob, ensure_ascii=False) + "\n")


def _print_summary(report: BootSLAProbeReport) -> None:
    """打印报告摘要。"""
    print()
    print("=" * 60)
    print("  Boot SLA 连跑报告")
    print("=" * 60)
    print(f"总运行次数:   {report.total_runs}")
    print(f"成功次数:     {report.successful_runs}")
    print(f"失败次数:     {report.failed_runs}")
    print()
    print(f"P50:          {report.p50_ms:.0f}ms ({report.p50_ms / 1000:.2f}s)")
    print(f"P95:          {report.p95_ms:.0f}ms ({report.p95_ms / 1000:.2f}s)")
    print(f"P99:          {report.p99_ms:.0f}ms ({report.p99_ms / 1000:.2f}s)")
    print(f"Mean:         {report.mean_ms:.0f}ms ({report.mean_ms / 1000:.2f}s)")
    print(f"Min:          {report.min_ms:.0f}ms ({report.min_ms / 1000:.2f}s)")
    print(f"Max:          {report.max_ms:.0f}ms ({report.max_ms / 1000:.2f}s)")
    print()
    print(f"SLA 目标:     P99 < {report.sla_target_ms:.0f}ms ({report.sla_target_ms / 1000:.0f}s)")
    status = "PASS" if report.sla_met else "FAIL"
    print(f"SLA 判定:     {status}")
    print("=" * 60)


def main() -> int:
    """主入口。

    Returns:
        exit code: 0 = SLA 达标，1 = SLA 未达标，2 = 执行异常
    """
    import argparse

    parser = argparse.ArgumentParser(description="Boot SLA 连跑实测探针")
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"连跑次数（默认 {DEFAULT_ITERATIONS}）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(REPORT_PATH),
        help=f"报告输出路径（默认 {REPORT_PATH}）",
    )
    args = parser.parse_args()

    try:
        report = _run_probe(args.iterations)
    except Exception as exc:
        print(f"[ERROR] 连跑执行异常: {exc}", file=sys.stderr)
        return 2

    output_path = Path(args.output)
    try:
        _save_report_jsonl(report, output_path)
        print(f"[OK] 报告已写入: {output_path}")
    except Exception as exc:
        print(f"[ERROR] 报告写入失败: {exc}", file=sys.stderr)
        return 2

    _print_summary(report)

    return 0 if report.sla_met else 1


if __name__ == "__main__":
    sys.exit(main())
