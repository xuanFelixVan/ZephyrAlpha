# [BLUEPRINT] MOD-INF-005 | scripts/governance/status.py | §
# [MODULE] scripts.governance.status
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
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
# [TTL] task_bound
"""
status.py — 审计系统状态仪表盘



输出整个脚本系统系统的实时健康状态（脚本注册表从 script_manifest.yaml SSoT 加载），包括：
- 脚本可执行性检查（所有注册脚本是否全部可运行）
- 各维度 Finding 分布（按严重度）
- 未覆盖维度预警
- 近期扫描趋势（如果历史数据存在）

Usage:
    python scripts/governance/status.py                  # 快速状态检查（不跑扫描）
    python scripts/governance/status.py --scan           # 运行全维度扫描后显示状态
    python scripts/governance/status.py --scan --dimensions D3 D5  # 指定维度扫描
    python scripts/governance/status.py --json           # JSON 格式输出（供脚本消费）

Blueprint: MOD-INF-005 §4.4
"""

from __future__ import annotations

__manifest__ = """
args: []
description: status.py — 审计系统状态仪表盘
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import json
import subprocess
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# AGENTS.md §6.7: UTF-8 输出强制声明（防止 Windows GBK 编码 crash）

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout

ensure_utf8_stdout()

from _shared.constants import MANIFEST_PATH, REPO_ROOT, SCRIPTS_DIR
from _shared.thresholds import get as _get_threshold  # noqa: E402  治本(ARCH-036 P3-A5): 全局硬超时读SSoT

FINDINGS_FILE = REPO_ROOT / "scripts" / "governance" / "reports" / "findings.jsonl"


def _load_script_health_checks() -> dict[str, Any]:
    """从 script_manifest.yaml 加载脚本健康检查配置（惰性加载）。

    Returns:
        dict: 脚本名 -> {dim: str, args: list} 映射

    Raises:
        FileNotFoundError: script_manifest.yaml 不存在
        yaml.YAMLError: YAML 格式无效
    """
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)

    checks = {}
    for entry in manifest["scripts"]:
        dim_str = "/".join(entry["dimensions"])
        checks[entry["name"]] = {
            "dim": dim_str,
            "args": entry.get("args", []),
        }
    return checks


_SCRIPT_HEALTH_CACHE: dict | None = None


def _get_script_health_checks() -> dict[str, Any]:
    """获取脚本健康检查配置（惰性加载，支持缓存）。

    Returns:
        dict: 脚本名 -> {dim: str, args: list} 映射
    """
    global _SCRIPT_HEALTH_CACHE
    if _SCRIPT_HEALTH_CACHE is None:
        _SCRIPT_HEALTH_CACHE = _load_script_health_checks()
    return _SCRIPT_HEALTH_CACHE


def _get_all_dimensions() -> list[str]:
    """从 manifest 动态提取所有维度标识（替代硬编码 DIMENSIONS_ALL）。

    Returns:
        list[str]: 去重排序后的维度标识列表。
    """
    dims: set[str] = set()
    for meta in _get_script_health_checks().values():
        for d in meta["dim"].split("/"):
            dims.add(d)
    return sorted(dims)


def check_script_health(script_name: str, args: list[str]) -> dict[str, Any]:
    """检查单个脚本的可执行性并返回健康状态。

    Args:
        script_name: 脚本文件名（如 'validate_architecture.py'）
        args: 传递给脚本的命令行参数列表

    Returns:
        dict: 包含 status/exit_code/error/has_findings 的状态字典
    """
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        return {"status": "MISSING", "exit_code": None, "error": "文件不存在"}

    cmd = [sys.executable, str(script_path)] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT),
            encoding="utf-8",
            errors="replace",
        )
        error_msg = result.stderr[:200] if result.stderr else ""
        return {
            "status": "OK" if result.returncode in (0, 1) else "ERROR",
            "exit_code": result.returncode,
            "error": error_msg if result.returncode not in (0, 1) else "",
            "has_findings": result.returncode != 0,
        }
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT", "exit_code": None, "error": "超时(>60s)"}
    except OSError as e:
        return {"status": "CRASH", "exit_code": None, "error": str(e)[:200]}


def load_findings_history() -> list[dict]:
    """加载历史 Finding 记录（从 findings.jsonl）。

    Returns:
        list[dict]: Finding 字典列表，文件不存在时返回空列表
    """
    if not FINDINGS_FILE.exists():
        return []
    findings = []
    with open(FINDINGS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    findings.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return findings


def compute_dimension_coverage() -> dict[str, list[str]]:
    """计算各审计维度的脚本覆盖情况。

    Returns:
        dict[str, list[str]]: 维度代码 -> 覆盖该维度的脚本名列表
    """
    covered = defaultdict(list)
    for script_name, meta in _get_script_health_checks().items():
        dims = meta["dim"].split("/")
        for d in dims:
            covered[d].append(script_name.replace(".py", ""))
    return dict(covered)


def render_dashboard(
    health: dict,
    findings: list[dict] | None,
    coverage: dict[str, list[str]],
    scan_time: float = 0,
) -> None:
    """渲染文本格式健康仪表盘到 stdout。

    Args:
        health: 脚本名 -> 健康状态字典
        findings: Finding 列表（None 表示无历史数据）
        coverage: 维度代码 -> 覆盖脚本列表
        scan_time: 扫描耗时（秒），0 表示未执行扫描
    """
    print(file=sys.stderr)
    print("=" * 65, file=sys.stderr)
    print("  ZephyrAlpha 审计系统 — 健康仪表盘", file=sys.stderr)
    print(f"  {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}", file=sys.stderr)
    print("=" * 65, file=sys.stderr)

    # ── Section 1: Script Health ──
    print(f"\n── 1. 脚本可执行性（{len(health)} 个）──\n", file=sys.stderr)
    ok_count = sum(1 for h in health.values() if h["status"] == "OK")
    err_count = sum(1 for h in health.values() if h["status"] not in ("OK",))

    for script_name, h in health.items():
        icon = "✅" if h["status"] == "OK" else "❌"
        dim_tag = _get_script_health_checks()[script_name]["dim"]
        finding_note = " (有发现)" if h.get("has_findings") else ""
        err_note = f"  → {h['error']}" if h.get("error") else ""
        print(f"  {icon} {script_name:<45} [{dim_tag}]{finding_note}", file=sys.stderr)
        if err_note:
            print(f"     {err_note}", file=sys.stderr)

    print(f"\n  可执行: {ok_count}/{len(health)}  |  异常: {err_count}/{len(health)}", file=sys.stderr)

    # ── Section 2: Dimension Coverage ──
    print("\n── 2. 审计维度覆盖（12 个）──\n", file=sys.stderr)

    dim_labels = {
        "D1": "结构完整性",
        "D2": "链接完整性",
        "D3": "元数据合规",
        "D4": "路径有效性",
        "D5": "架构合规",
        "D6": "安全漏洞",
        "D7": "代码质量",
        "D8": "文档代码同步",
        "D9": "知识覆盖",
        "D10": "性能容量",
        "D11": "合规完整性",
        "D12": "AI幻觉检测",
    }

    covered_dims = {d for d in coverage if coverage[d]}
    for dim in _get_all_dimensions():
        label = dim_labels.get(dim, dim)
        if dim in covered_dims:
            scripts = coverage.get(dim, [])
            bar = "█" * min(len(scripts), 10)
            print(f"  ✅ {dim} {label:<12} {bar} ({len(scripts)} 脚本)", file=sys.stderr)
        else:
            print(f"  ❌ {dim} {label:<12} ──── (无脚本 — experimental/2)", file=sys.stderr)

    dim_pct = len(covered_dims) / 12 * 100
    print(f"\n  已覆盖: {len(covered_dims)}/12 ({dim_pct:.0f}%)", file=sys.stderr)

    # ── Section 3: Finding Summary ──
    if findings is not None and findings:
        print(f"\n── 3. Finding 摘要 ({len(findings)} 条) ──\n", file=sys.stderr)

        sev_counts = defaultdict(int)
        dim_counts = defaultdict(int)
        for f in findings:
            sev = f.get("severity", "UNKNOWN")
            dim = f.get("dimension", "??")
            sev_counts[sev] += 1
            dim_counts[dim] += 1

        print("  按严重度：", file=sys.stderr)
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            count = sev_counts.get(sev, 0)
            bar = "█" * min(count, 40)
            icon = "🔴" if sev == "CRITICAL" else "🟡" if sev in ("HIGH", "MEDIUM") else "🟢"
            if count > 0:
                print(f"    {icon} {sev:<10} {bar} {count}", file=sys.stderr)

        print("\n  按维度：", file=sys.stderr)
        for dim in sorted(dim_counts.keys()):
            count = dim_counts[dim]
            label = dim_labels.get(dim, dim)
            bar = "█" * min(count, 30)
            print(f"    {dim} {label:<12} {bar} {count}", file=sys.stderr)

    elif findings is not None:
        print("\n── 3. Finding 摘要 ──\n  无历史或上次扫描存在 Finding，请运行 --scan 更新", file=sys.stderr)

    # ── Footer ──
    print(f"\n{'─' * 65}", file=sys.stderr)
    if scan_time > 0:
        print(f"  扫描耗时: {scan_time:.1f}s", file=sys.stderr)
    print(f"  仪表盘刷新: {datetime.now(UTC).strftime('%H:%M:%S UTC')}", file=sys.stderr)
    print(f"{'─' * 65}\n", file=sys.stderr)


CAPACITY_LIMITS = {
    "per_dimension_max": 50,
    "global_max": 300,
    "scan_duration_warning_s": 300,
    "global_hard_timeout_s": _get_threshold("scanning.global_hard_timeout_seconds", 3600),  # 治本(ARCH-036 P3-A5): 从SSoT读取(原硬编码600与SSoT 3600漂移)
}


def render_json(health: dict, coverage: dict) -> None:
    """渲染 JSON 格式健康状态到 stdout。

    Args:
        health: 脚本名 -> 健康状态字典
        coverage: 维度代码 -> 覆盖脚本列表
    """
    dim_labels = {
        "D1": "结构完整性",
        "D2": "链接完整性",
        "D3": "元数据合规",
        "D4": "路径有效性",
        "D5": "架构合规",
        "D6": "安全漏洞",
        "D7": "代码质量",
        "D8": "文档代码同步",
        "D9": "知识覆盖",
        "D10": "性能容量",
        "D11": "合规完整性",
        "D12": "AI幻觉检测",
    }

    unhealthy_scripts = sum(1 for h in health.values() if h["status"] != "OK")
    global_script_count = len(health)

    capacity_warnings: list[str] = []
    for dim, scripts in coverage.items():
        count = len(scripts)
        if count >= 8:
            capacity_warnings.append(
                f"WARNING: {dim} ({dim_labels.get(dim, dim)}) 有 {count} 脚本（接近上限 {CAPACITY_LIMITS['per_dimension_max']}）"
            )
    if global_script_count >= 150:
        capacity_warnings.append(
            f"WARNING: 全局脚本数 {global_script_count}（接近上限 {CAPACITY_LIMITS['global_max']}）"
        )

    dimension_vacant: list[str] = []
    for d in _get_all_dimensions():
        if not coverage.get(d):
            dimension_vacant.append(d)

    output = {
        "timestamp": datetime.now(UTC).isoformat(),
        "scripts": {
            name: {"status": h["status"], "exit_code": h["exit_code"], "has_findings": h.get("has_findings", False)}
            for name, h in health.items()
        },
        "coverage": {dim: len(scripts) for dim, scripts in coverage.items()},
        "uncovered": [d for d in _get_all_dimensions() if d not in coverage or not coverage[d]],
        "dimension_vacant": dimension_vacant,
        "healthy": unhealthy_scripts == 0,
        "capacity": {
            "global_script_count": global_script_count,
            "global_max": CAPACITY_LIMITS["global_max"],
            "per_dimension": {dim: len(scripts) for dim, scripts in coverage.items()},
            "warnings": capacity_warnings,
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2), file=sys.stderr)


def run_scan(dimensions: list[str] | None = None) -> float:
    """运行全维度或指定维度审计扫描。

    Args:
        dimensions: 指定维度列表，None 表示全维度

    Returns:
        float: 扫描耗时（秒）
    """
    run_all = REPO_ROOT / "scripts" / "governance" / "run_all.py"
    cmd = [sys.executable, str(run_all)]
    if dimensions:
        cmd += ["--dimensions"] + dimensions

    print("正在运行全维度审计扫描...\n", file=sys.stderr)
    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    elapsed = time.time() - t0
    if result.returncode not in (0, 1, 2, 3):
        print(f"⚠ run_all.py 异常退出（exit={result.returncode}）", file=sys.stderr)
    return elapsed


def main() -> None:
    """入口——解析命令行参数并渲染审计系统健康仪表盘。

    支持 --scan（先扫描再显示）、--json（JSON 输出）、--quiet（摘要模式）。
    """
    parser = argparse.ArgumentParser(description="审计系统状态仪表盘")
    parser.add_argument("--scan", "-s", action="store_true", help="先运行全维度扫描，再显示状态")
    parser.add_argument("--dimensions", "-d", nargs="+", help="指定扫描维度（需配 --scan）")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--quiet", "-q", action="store_true", help="安静模式：只输出摘要")
    parser.add_argument("--warn-only", action="store_true", help="警告模式：状态异常不阻塞（exit 0）")
    args = parser.parse_args()

    scan_time = 0
    if args.scan:
        scan_time = run_scan(args.dimensions)

    health = {}
    for script_name, meta in _get_script_health_checks().items():
        health[script_name] = check_script_health(script_name, meta["args"])

    coverage = compute_dimension_coverage()
    findings = load_findings_history() if FINDINGS_FILE.exists() else None

    if args.json:
        render_json(health, coverage)
    else:
        render_dashboard(health, findings, coverage, scan_time)


if __name__ == "__main__":
    sys.exit(main() or 0)
