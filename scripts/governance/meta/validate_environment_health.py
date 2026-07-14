# [BLUEPRINT] MOD-INF-005 | scripts/governance/meta/validate_environment_health.py | §
# [MODULE] scripts.governance.meta.validate_environment_health
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.meta.__init__
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
"""validate_environment_health.py — 脚本运行环境健康检查

对标 B21（脚本依赖隔离）+ Google SRE Environment Readiness Probe。
检查 Python 版本、关键包版本、各维度 requirements、磁盘空间、内存。
在 run_all.py 启动时和 CI 中运行。

Usage:
    python scripts/governance/meta/validate_environment_health.py
    python scripts/governance/meta/validate_environment_health.py --dimension D7
    python scripts/governance/meta/validate_environment_health.py --install D12
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  脚本运行环境健康检查——检查 Python 版本、关键包版本、各维度 requirements、磁盘空间、内存，
  在 run_all.py 启动时和 CI 中运行。
dimensions:
- D1
priority: P1
timeout_seconds: 30
warn_only: false
"""


import argparse
import importlib
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# 治本(2026-06-30): REPO_ROOT 真源来自 _shared.constants, 消除 parents[N] 硬编码
# 原 parents[2] 实为 scripts 目录而非 repo root, 变量名误导且路径计算有 bug
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import REPO_ROOT as _REPO_ROOT  # noqa: E402
_SCRIPTS_DIR = _REPO_ROOT / "scripts" / "governance"
_REQUIREMENTS_DIR = _SCRIPTS_DIR / "meta" / "requirements"

# 各维度按依赖重/轻分池
LIGHTWEIGHT_DIMS = {"D1", "D2", "D3", "D4"}
MEDIUM_DIMS = {"D5", "D6", "D7", "D8", "D11"}
HEAVYWEIGHT_DIMS = {"D9", "D10", "D12"}

DIMENSION_POOL = {
    "lightweight": LIGHTWEIGHT_DIMS,
    "medium": MEDIUM_DIMS,
    "heavyweight": HEAVYWEIGHT_DIMS,
}

DIM_PACKAGES: dict[str, list[str]] = {
    "D1": [],
    "D2": [],
    "D3": ["yaml"],
    "D4": [],
    "D5": ["yaml"],
    "D6": [],
    "D7": [],
    "D8": [],
    "D9": ["yaml"],
    "D10": [],
    "D11": ["yaml"],
    "D12": ["numpy"],
}

MIN_PYTHON = (3, 11)
MIN_DISK_MB = 100

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _check_python_version() -> dict:
    """_check_python_version implementation."""
    current = sys.version_info[:2]
    ok = current >= MIN_PYTHON
    return {
        "check": "python_version",
        "passed": ok,
        "required": f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]}+",
        "current": f"{current[0]}.{current[1]}",
    }


def _check_disk() -> dict:
    """_check_disk implementation."""
    try:
        usage = os.statvfs(str(_REPO_ROOT)) if hasattr(os, "statvfs") else None
        if usage:
            free_mb = (usage.f_frsize * usage.f_bavail) // (1024 * 1024)
        else:
            free_mb = 500
    except (OSError, AttributeError):
        free_mb = 500
    return {
        "check": "disk_space",
        "passed": free_mb >= MIN_DISK_MB,
        "free_mb": free_mb,
        "required_mb": MIN_DISK_MB,
    }


def _check_packages(dimension: str | None = None) -> dict:
    """_check_packages implementation."""
    missing: list[str] = []
    dims_to_check = [dimension] if dimension else list(DIM_PACKAGES.keys())

    checked: set[str] = set()
    for dim in dims_to_check:
        for pkg in DIM_PACKAGES.get(dim, []):
            if pkg in checked:
                continue
            checked.add(pkg)
            try:
                importlib.import_module(pkg)
            except ImportError:
                missing.append(f"{pkg} (required by {dim})")

    return {
        "check": "packages",
        "passed": len(missing) == 0,
        "missing": missing,
        "checked": len(checked),
    }


def _check_dimension_requirements(dimension: str) -> dict:
    """_check_dimension_requirements implementation."""
    req_file = _REQUIREMENTS_DIR / f"requirements-{dimension.lower()}.txt"
    if not req_file.exists():
        return {"check": f"dim_{dimension}_requirements", "passed": True, "note": "无专属 requirements"}

    with open(req_file, encoding="utf-8") as f:
        required = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    missing = []
    for spec in required:
        pkg_name = spec.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].strip()
        try:
            importlib.import_module(pkg_name.replace("-", "_"))
        except ImportError:
            missing.append(spec)

    return {
        "check": f"dim_{dimension}_requirements",
        "passed": len(missing) == 0,
        "required": len(required),
        "missing": missing,
    }


def _check_dim_pool(dimension: str) -> dict:
    """_check_dim_pool implementation."""
    if dimension in LIGHTWEIGHT_DIMS:
        pool = "lightweight"
    elif dimension in MEDIUM_DIMS:
        pool = "medium"
    else:
        pool = "heavyweight"
    return {"check": "dim_pool", "pool": pool, "dimension": dimension}


def install_dimension(dimension: str) -> dict:
    """install_dimension implementation."""
    req_file = _REQUIREMENTS_DIR / f"requirements-{dimension.lower()}.txt"
    if not req_file.exists():
        return {"installed": False, "error": f"requirements 文件不存在: {req_file}"}

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(_REPO_ROOT),
        encoding="utf-8",
        errors="replace",
    )
    return {
        "installed": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-500:] if result.stdout else "",
        "stderr_tail": result.stderr[-500:] if result.stderr else "",
    }


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="脚本运行环境健康检查")
    parser.add_argument("--dimension", "-d", type=str, help="指定维度")
    parser.add_argument("--install", type=str, help="安装指定维度的 requirements")
    parser.add_argument("--full", action="store_true", help="全维度检查（含各维度 requirements）")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    import json as json_mod

    if args.install:
        result = install_dimension(args.install)
        if args.json:
            print(json_mod.dumps(result, ensure_ascii=False))
        else:
            status = "✅" if result["installed"] else "❌"
            print(f"[ENV] {status} 安装 {args.install}: {result}", file=sys.stderr)
        return

    results: list[dict] = [
        _check_python_version(),
        _check_disk(),
        _check_packages(args.dimension),
    ]

    if args.dimension:
        results.append(_check_dim_pool(args.dimension))
        results.append(_check_dimension_requirements(args.dimension))
    elif args.full:
        for dim in sorted(DIM_PACKAGES.keys()):
            results.append(_check_dimension_requirements(dim))

    summary = {
        "timestamp": datetime.now(UTC).isoformat(),
        "all_passed": all(r["passed"] for r in results),
        "checks": results,
    }

    if args.json:
        print(json_mod.dumps(summary, ensure_ascii=False, indent=2))
    else:
        for r in results:
            icon = "✅" if r["passed"] else "❌"
            print(f"  {icon} {r['check']}: {r}", file=sys.stderr)

    sys.exit(0 if summary["all_passed"] else 1)


if __name__ == "__main__":
    main()
